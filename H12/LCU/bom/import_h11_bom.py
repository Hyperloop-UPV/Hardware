#!/usr/bin/env python3
"""Extract the LCU_H11 bill of materials from the Altium LiveBOM in the reference archive.

The archive `LCU_H11/LCU_H11.zip` contains an Altium LiveBOM (`*.BomDoc`) which holds, for
every line item, the manufacturer part number, the manufacturer, the supplier, the
lifecycle status and the distributor stock. That data is the inherited baseline for the
LCU_H12 BOM: it tells us which parts we are carrying over and which of them are already at
risk.

Usage:
    python bom/import_h11_bom.py                  # write bom/h11_baseline.json
    python bom/import_h11_bom.py --print          # dump a table to stdout

The output is committed, so the risk analysis works without the Altium archive present.
"""

import argparse
import io
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_ZIP = os.path.join(ROOT, "LCU_H11", "LCU_H11.zip")
OUT = os.path.join(HERE, "h11_baseline.json")

# Vault design items carry no supplier data; map them by hand to a readable identity.
VAULT_ALIASES = {
    "CMP-020-00000-1": "STM32H723ZGT6 MCU",
    "CMP-006-00301-4": "Micro-Fit+ header, 4 ckt",
    "CMP-006-00297-1": "Nano-Fit header",
    "CMP-006-00310-3": "Modular jack RJE3A/3B",
    "CMP-980-000000-4": "A/L universal header 26P (LPU connector)",
    "CMP-004-000017-1": "Hex buffer, 3-state (SN74AHCT367 class)",
    "CMP-00005-4": "Dual op-amp, 2.5 mV Vos (MCP6022 class)",
    "CMP-IC-00001-001-4": "High-speed CAN transceiver",
    "CMP-006-00233-1": "TVS diode, 200 W, 24 V",
    "CMP-006-00200-1": "Power inductor WE-PD 12 uH",
    "CMP-004-000020-1": "Darlington array ULN200x",
    "CMP-00031-3": "IDC header 1.27 mm, 14 pos",
    "CMP-006-00250-2": "Test point 1.2 mm",
    "CMP-006-00230-1": "2-pin 0.1in header",
    "CMP-006-00230-2": "2-pin 0.1in header",
    "CMP-006-00232-4": "Ferrite chip array, 4 element",
    "CMP-1011-000000-2": "unidentified vault item",
}


def records(raw):
    return re.split(r"(?=RECORD=)", raw)


def fields(record):
    out = {}
    for chunk in record.split("|"):
        if "=" in chunk:
            key, value = chunk.split("=", 1)
            out[key.strip()] = value.strip()
    return out


def component_param(item, name):
    match = re.search(r'"%s=([^"]*)"' % re.escape(name), item.get("COMPONENTPARAMETERS", ""))
    return match.group(1) if match else ""


def extract(bomdoc_bytes):
    raw = bomdoc_bytes.decode("latin-1")
    items, current = [], None
    for record in records(raw):
        if record.startswith("RECORD=CatalogItem"):
            current = {"item": fields(record), "choices": []}
            items.append(current)
        elif record.startswith("RECORD=PartChoice") and current is not None:
            current["choices"].append(fields(record))

    rows = []
    for entry in items:
        item = entry["item"]
        choices = sorted(entry["choices"], key=lambda c: int(c.get("RANK") or 99))
        best = choices[0] if choices else {}
        design_item = item.get("DESIGNITEMID", "")
        mpn = best.get("MANUFACTURERPARTNO", "").strip()

        payload = json.dumps(choices)
        datasheet = ""
        match = re.search(r'"componentlink1url=([^",]+)', item.get("COMPONENTPARAMETERS", ""))
        if match:
            datasheet = match.group(1).strip()

        rows.append({
            "identity": mpn or VAULT_ALIASES.get(design_item, design_item),
            "design_item": design_item,
            "comment": component_param(item, "Comment"),
            "description": item.get("DESCRIPTION", ""),
            "panel_status": item.get("STATUS", ""),
            "mpn": mpn,
            "manufacturer": best.get("MANUFACTURER", "").strip(),
            "supplier": best.get("SUPPLIER", "").strip(),
            "supplier_part": best.get("SUPPLIERPARTNO", "").strip(),
            "lifecycle": best.get("LIFECYCLESTATUS", "").strip(),
            "stock": int(best.get("AVAILABLEQUANTITY") or 0),
            "choices": len(choices),
            "datasheet": datasheet,
            "unresolved": not bool(mpn),
            "_payload": payload,
        })
    for row in rows:
        row.pop("_payload", None)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", default=DEFAULT_ZIP)
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.zip):
        sys.exit("reference archive not found: %s" % args.zip)

    with zipfile.ZipFile(args.zip) as archive:
        name = next((n for n in archive.namelist() if n.lower().endswith(".bomdoc")), None)
        if name is None:
            sys.exit("no .BomDoc inside %s" % args.zip)
        rows = extract(archive.read(name))
        source = "%s :: %s" % (os.path.basename(args.zip), name)

    unresolved = [r for r in rows if r["unresolved"]]
    payload = {
        "schema": "hl-bom-baseline/1.0",
        "source": source,
        "extracted_by": "bom/import_h11_bom.py",
        "note": ("Lifecycle and stock figures are a snapshot shipped inside the Altium "
                 "archive. Treat them as a starting point to re-verify, not as current."),
        "counts": {
            "line_items": len(rows),
            "with_mpn": len(rows) - len(unresolved),
            "vault_only": len(unresolved),
        },
        "lines": rows,
    }

    if args.print:
        print("%-34s %-18s %-18s %9s %s" % ("MPN / identity", "MANUFACTURER", "LIFECYCLE", "STOCK", "COMMENT"))
        for row in sorted(rows, key=lambda r: (r["lifecycle"], r["identity"])):
            print("%-34s %-18s %-18s %9d %s" % (
                row["identity"][:34], row["manufacturer"][:18],
                row["lifecycle"][:18], row["stock"], row["comment"][:24]))
        print("\n%d line items, %d with an MPN, %d vault-only"
              % (len(rows), len(rows) - len(unresolved), len(unresolved)))

    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print("wrote %s" % os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
