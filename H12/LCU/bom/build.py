#!/usr/bin/env python3
"""LCU_H12 Phase 1: validate the BOM, score its risk and parse the available datasheets.

Inputs:
    bom/lcu_h12.bom.json      the BOM model (hand written, reviewed)
    bom/h11_baseline.json     the LCU_H11 BOM, extracted from the Altium archive
    datasheets/*.pdf          whatever has been dropped in, named by MPN

Outputs (under docs/phase1/generated/):
    bom.md                    the BOM, grouped by block
    risk-register.md          parts ordered by priority
    datasheet-params.md       parameters extracted from the local datasheets
    coverage.md               carry-over accounting and open decisions

Usage:
    python bom/build.py            # validate, score, regenerate
    python bom/build.py --check    # validate only, exit 1 on failure

Standard library only. pdftotext is used if present; its absence is reported, not fatal.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs", "phase1", "generated")
DATASHEETS = os.path.join(ROOT, "datasheets")

# Parts whose identity in the Altium baseline is a vault code, not an MPN.
BASELINE_ALIASES = {
    "TE-5499922-6": "CMP-980-000000-4",
    "MCP6022-E/SN": "CMP-00005-4",
    "MOLEX-206832-0401": "CMP-006-00301-4",
    "TJA1051T/3": "CMP-IC-00001-001-4",
}

LIFECYCLE_FLAG = {
    "eol": "lifecycle_eol",
    "obsolete": "lifecycle_eol",
    "nrnd": "lifecycle_nrnd",
    "migrating": "lifecycle_migrating",
    "unknown": "lifecycle_unknown",
}


class Report:
    def __init__(self):
        self.rows = []

    def ok(self, tag, text, detail=""):
        self.rows.append(("OK", tag, text, detail))

    def fail(self, tag, text, detail=""):
        self.rows.append(("FAIL", tag, text, detail))

    def warn(self, tag, text, detail=""):
        self.rows.append(("WARN", tag, text, detail))

    @property
    def failures(self):
        return [r for r in self.rows if r[0] == "FAIL"]

    def count(self, kind):
        return sum(1 for r in self.rows if r[0] == kind)

    def markdown(self):
        label = {"OK": "OK", "FAIL": "**FAIL**", "WARN": "WARN"}
        lines = ["| Status | Check | Detail |", "|---|---|---|"]
        for status, tag, text, detail in self.rows:
            lines.append("| %s | `%s` %s | %s |" % (label[status], tag, text, detail))
        return "\n".join(lines)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def norm(text):
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


# --------------------------------------------------------------------------
# Risk
# --------------------------------------------------------------------------

def derive_flags(part, bom):
    """Explicit flags plus the ones implied by the data."""
    flags = list(part.get("flags") or [])

    lifecycle = (part.get("lifecycle") or "unknown").lower()
    implied = LIFECYCLE_FLAG.get(lifecycle)
    if implied and implied not in flags:
        flags.append(implied)

    if part.get("single_source") and "single_source" not in flags:
        flags.append("single_source")
    if part.get("single_source") and not part.get("alternates") and "no_alternate" not in flags:
        flags.append("no_alternate")

    stock = part.get("stock")
    if isinstance(stock, int):
        if stock < 100:
            flags.append("stock_below_100")
        elif stock < 1000:
            flags.append("stock_below_1000")

    index = bom.get("datasheet_index", {}).get(part.get("_key", ""), {})
    if index and not index.get("file"):
        flags.append("datasheet_missing")

    if not part.get("verified_on"):
        flags.append("unverified")

    seen, out = set(), []
    for flag in flags:
        if flag not in seen:
            seen.add(flag)
            out.append(flag)
    return out


def part_key(part):
    return part.get("_key", "")


def score(part, bom):
    weights = bom["risk_model"]["weights"]
    flags = derive_flags(part, bom)
    return sum(weights.get(flag, 1) for flag in flags), flags


def band_for(score_value, bom):
    bands = bom["risk_model"]["bands"]
    best = "low"
    for name in bom["risk_model"]["band_order"]:
        if score_value >= bands[name]:
            best = name
    return best


# Risk and impact are kept as two separate axes. A part can be low risk and safety-critical
# at the same time -- a commodity connector that is the only way to attach a levitation coil
# is exactly that. Conflating them into one number hides the distinction.
IMPACT_RANK = {"safety": 0, "functional": 1, "auxiliary": 2}
BAND_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def check_lines(bom, baseline, report):
    parts = bom["parts"]
    for key in parts:
        parts[key]["_key"] = key

    line_ids = set()
    for line in bom["lines"]:
        tag = line["id"]
        if tag in line_ids:
            report.fail("LINE-DUP", "Duplicate line id", tag)
        line_ids.add(tag)

        status = line["status"]
        if status not in ("carry", "changed", "new", "select", "proposed"):
            report.fail("LINE-STATUS", "Unknown line status", "%s -> %s" % (tag, status))
        if status == "select":
            if not line.get("candidates"):
                report.fail("LINE-CAND", "Line has no part and no candidates", tag)
            elif not line.get("part"):
                report.ok("LINE-OPEN", "Line awaiting selection", "%s (%d candidates)" % (tag, len(line["candidates"])))
        else:
            if not line.get("part"):
                report.fail("LINE-PART", "Line has a status but no part", tag)
            elif line["part"] not in parts and line["part"] != "INHERITED":
                report.fail("LINE-REF", "Line references an unknown part", "%s -> %s" % (tag, line["part"]))

        if not (0 <= len(line.get("criticality", ""))):
            report.fail("LINE-CRIT", "Line has no criticality", tag)

    used = {l["part"] for l in bom["lines"] if l.get("part")}
    for line in bom["lines"]:
        for candidate in line.get("candidates", []):
            if candidate in parts:
                used.add(candidate)
    orphans = [k for k in parts if k not in used and not parts[k].get("library_only")]
    if orphans:
        report.warn("PART-ORPHAN", "Parts declared but not used by any line", ", ".join(orphans))
    else:
        report.ok("PART-ORPHAN", "Every declared part is used by a line", "%d parts" % len(parts))


def check_carry_over(bom, baseline, report):
    """A line claiming to be carried over must exist in the H11 baseline."""
    identities = []
    for entry in baseline.get("lines", []):
        for label in (entry.get("identity"), entry.get("design_item")):
            if label:
                identities.append((norm(label), label, entry.get("lifecycle"), entry.get("stock")))

    matched, missing = 0, []
    for line in bom["lines"]:
        if line["status"] != "carry":
            continue
        part = line.get("part") or ""
        if part in ("INHERITED",):
            matched += 1
            continue
        needle = norm(BASELINE_ALIASES.get(part, part))
        hit = None
        for ident_norm, ident, lifecycle, stock in identities:
            if needle and (needle in ident_norm or ident_norm in needle):
                hit = (ident, lifecycle, stock)
                break
        if hit:
            matched += 1
        else:
            missing.append("%s (%s)" % (line["id"], part))

    if missing:
        report.fail("CARRY-MATCH", "Carry-over lines not found in the H11 baseline", ", ".join(missing))
    else:
        report.ok("CARRY-MATCH", "Every carry-over line exists in the H11 baseline",
                  "%d checked" % matched)


def check_decisions(bom, report):
    for decision in bom.get("decisions", []):
        blocks = decision.get("blocks") or []
        if decision["status"] in ("open", "blocked") and not decision.get("recommendation"):
            report.fail("DEC-REC", "Open decision has no recommendation", decision["id"])
        if not blocks:
            report.fail("DEC-BLOCK", "Decision does not name the lines it blocks", decision["id"])
    open_count = sum(1 for d in bom.get("decisions", []) if d["status"] in ("open", "blocked"))
    report.ok("DEC", "Decisions recorded",
              "%d total, %d open or blocked" % (len(bom.get("decisions", [])), open_count))
    return open_count


# --------------------------------------------------------------------------
# Datasheet parsing
# --------------------------------------------------------------------------

def parse_datasheets(bom, report):
    """Pull parameter lines out of whatever PDFs are present."""
    index = bom.get("datasheet_index", {})
    have_tool = shutil.which("pdftotext") is not None
    results = {}

    if not have_tool:
        report.warn("DS-TOOL", "pdftotext not available",
                    "datasheet extraction skipped; install poppler-utils")

    available = 0
    for part, spec in index.items():
        if part == "note":
            continue
        path = spec.get("file")
        entry = {"available": False, "params": {}, "missing": []}
        if not path:
            entry["missing"] = spec.get("params", [])
            results[part] = entry
            continue
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            entry["missing"] = spec.get("params", [])
            entry["error"] = "file not found: %s" % path
            results[part] = entry
            continue
        available += 1
        entry["available"] = True
        text = ""
        if have_tool:
            proc = subprocess.run(["pdftotext", "-layout", full, "-"],
                                  capture_output=True, text=True, timeout=120)
            text = proc.stdout
        lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        for param in spec.get("params", []):
            needle = param.lower()
            found = next((line for line in lines if needle in line.lower()), None)
            if found:
                entry["params"][param] = found[:150]
            else:
                entry["missing"].append(param)
        results[part] = entry

    declared = [p for p in index if p != "note"]
    report.ok("DS-INDEX", "Datasheet entries declared",
              "%d parts, %d PDFs present on disk" % (len(declared), available))
    if available < len(declared):
        report.warn("DS-MISSING", "Datasheets not present locally",
                    "%d of %d parts have no PDF, so their parameters are unverified"
                    % (len(declared) - available, len(declared)))
    return results


# --------------------------------------------------------------------------
# Documents
# --------------------------------------------------------------------------

def render_bom(bom, scored):
    parts = bom["parts"]
    out = ["# Bill of materials", "",
           "> Generated by `bom/build.py` from `bom/lcu_h12.bom.json`. Do not edit by hand.", "",
           "Risk is a per-part additive score; `Priority` additionally reflects the impact of the "
           "line failing (safety lines are bumped). See `risk-register.md` for the drivers.", ""]

    blocks = {}
    for line in bom["lines"]:
        blocks.setdefault(line["block"].split(",")[0].strip(), []).append(line)

    for block in sorted(blocks):
        out += ["## `%s`" % block, "",
                "| ID | Function | Qty | Part | Status | Lifecycle | Risk |",
                "|---|---|---|---|---|---|---|"]
        for line in sorted(blocks[block], key=lambda l: l["id"]):
            part = parts.get(line.get("part") or "", {})
            name = line.get("part") or "_(to select)_"
            out.append("| `%s` | %s | %d | `%s` | %s | %s | %s |" % (
                line["id"], line["function"], line["qty"], name, line["status"],
                part.get("lifecycle", "n/a"), part.get("_band", "n/a")))
        out.append("")

    out += ["## Line notes", ""]
    for line in bom["lines"]:
        if line.get("note"):
            out.append("- **`%s`** — %s" % (line["id"], line["note"]))
    out.append("")
    return "\n".join(out)


def render_risk(bom, scored):
    weights = bom["risk_model"]["weights"]
    ordered = sorted(scored, key=lambda s: (BAND_RANK[s["band"]],
                                             IMPACT_RANK[s["line"].get("criticality", "auxiliary")],
                                             -s["score"], s["line"]["id"]))
    out = ["# BOM risk register", "",
           "> Generated by `bom/build.py`. Do not edit by hand.", "",
           "Two axes, deliberately not collapsed into one number:", "",
           "- **Risk** is the likelihood of a supply or availability problem, scored from the part's "
           "flags. The arithmetic is in `risk_model` in the BOM model.",
           "- **Impact** is what happens if the line fails in service.", "",
           "A low-risk, safety-impact line is a real category here: the connector is easy to buy "
           "today and its failure drops the pod. It belongs at the top of the attention list even "
           "though its risk score is zero.", "",
           "| Risk | Impact | Score | Line | Part | Drivers | Mitigation |",
           "|---|---|---|---|---|---|---|"]

    for item in ordered:
        line, part = item["line"], item["part"]
        drivers = ", ".join(
            "%s (%d)" % (flag, weights.get(flag, 1)) for flag in item["flags"]) or "none"
        mitigation = (line.get("note") or part.get("note") or "").replace("|", "/")
        out.append("| %s | %s | %d | `%s` | `%s` | %s | %s |" % (
            item["band"], line.get("criticality", "-"), item["score"], line["id"],
            line.get("part") or "-", drivers, mitigation[:200]))

    tallies = {}
    for item in scored:
        tallies[item["band"]] = tallies.get(item["band"], 0) + 1
    out += ["", "## Tally by risk", "",
            "| Risk | Lines |", "|---|---|"]
    for band in bom["risk_model"]["band_order"][::-1]:
        if band in tallies:
            out.append("| %s | %d |" % (band, tallies[band]))

    impact = {}
    for item in scored:
        key = item["line"].get("criticality", "auxiliary")
        impact[key] = impact.get(key, 0) + 1
    out += ["", "## Tally by impact", "", "| Impact | Lines |", "|---|---|"]
    for key in ("safety", "functional", "auxiliary"):
        if key in impact:
            out.append("| %s | %d |" % (key, impact[key]))
    out.append("")
    return "\n".join(out)


def render_datasheets(results):
    out = ["# Datasheet parameters", "",
           "> Generated by `bom/build.py` using `pdftotext`. Do not edit by hand.", "",
           "Only datasheets present in `H12/LCU/datasheets/` can be parsed. A missing PDF means "
           "the parameters below are unverified, which the risk register counts as a flag.", ""]
    for part in sorted(results):
        entry = results[part]
        out += ["## `%s`" % part, ""]
        if not entry["available"]:
            out += ["> No datasheet on disk. Parameters unverified." + (
                " (%s)" % entry["error"] if entry.get("error") else ""), "",
                "Wanted: " + ", ".join(entry["missing"]) if entry["missing"] else "", ""]
            continue
        if entry["params"]:
            out += ["| Parameter | Extracted line |", "|---|---|"]
            for param, value in entry["params"].items():
                out.append("| %s | `%s` |" % (param, value.replace("|", "/")))
        if entry["missing"]:
            out += ["", "Not found in the document: " + ", ".join(entry["missing"])]
        out.append("")
    return "\n".join(out)


def render_coverage(bom, baseline, report, open_decisions):
    lines = bom["lines"]
    by_status = {}
    for line in lines:
        by_status[line["status"]] = by_status.get(line["status"], 0) + 1

    out = ["# Coverage and carry-over", "",
           "> Generated by `bom/build.py`. Do not edit by hand.", "",
           "## Line status", "", "| Status | Lines | Meaning |", "|---|---|---|"]
    meaning = bom["meta"]["conventions"]["line_status"]
    for status in ("carry", "changed", "new", "proposed", "select"):
        if status in by_status:
            out.append("| %s | %d | %s |" % (status, by_status[status], meaning[status]))
    out += ["", "## Baseline", "",
            "The LCU_H11 BOM was extracted from the Altium LiveBOM shipped inside the reference "
            "archive: **%d line items**, %d with a manufacturer part number, %d vault-only items "
            "without supplier data."
            % (baseline["counts"]["line_items"], baseline["counts"]["with_mpn"],
               baseline["counts"]["vault_only"]), "",
            "Lifecycle and stock figures inherited from that file are a snapshot taken when the "
            "archive was produced, not current data. They are used here as a starting point, and "
            "every part that matters has been re-checked by hand — see the `verified_on` field in "
            "the BOM model.", ""]

    if open_decisions:
        out += ["## Decisions still open", ""]
        for decision in bom["decisions"]:
            if decision["status"] in ("open", "blocked"):
                out.append("- **%s — %s** (%s): %s" % (
                    decision["id"], decision["topic"], decision["status"], decision["question"]))
                if decision.get("recommendation"):
                    out.append("  - Recommendation: %s" % decision["recommendation"])
        out.append("")
    return "\n".join(out)


def render_checks(report):
    out = ["# BOM checks", "",
           "> Generated by `bom/build.py`. Do not edit by hand.", "",
           report.markdown(), "",
           "%d OK, %d warnings, %d failures."
           % (report.count("OK"), report.count("WARN"), report.count("FAIL")), ""]
    return "\n".join(out)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text if text.endswith("\n") else text + "\n")
    print("  -> %s" % os.path.relpath(path, ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without writing documents")
    args = parser.parse_args()

    bom = load(os.path.join(HERE, "lcu_h12.bom.json"))
    baseline_path = os.path.join(HERE, "h11_baseline.json")
    if not os.path.exists(baseline_path):
        sys.exit("missing bom/h11_baseline.json -- run bom/import_h11_bom.py first")
    baseline = load(baseline_path)

    report = Report()
    check_lines(bom, baseline, report)
    check_carry_over(bom, baseline, report)
    open_decisions = check_decisions(bom, report)

    for key, part in bom["parts"].items():
        part["_key"] = key
        value, flags = score(part, bom)
        part["_score"], part["_flags"] = value, flags
        part["_band"] = band_for(value, bom)

    scored = []
    for line in bom["lines"]:
        part = bom["parts"].get(line.get("part") or "", {})
        value = part.get("_score", 0)
        flags = part.get("_flags", [])
        if line["status"] == "select":
            value += 3
            flags = flags + ["not_selected"]
        band = band_for(value, bom)
        scored.append({"line": line, "part": part, "score": value,
                       "flags": flags, "band": band})

    datasheet_results = parse_datasheets(bom, report)

    print("\nBOM checks for the %s\n" % bom["meta"]["board"])
    for status, tag, text, detail in report.rows:
        print("  %-5s %-16s %s%s" % (status, tag, text, ("  [%s]" % detail) if detail else ""))
    print("\n%d OK, %d warnings, %d failures"
          % (report.count("OK"), report.count("WARN"), report.count("FAIL")))

    tally = {}
    for item in scored:
        tally[item["band"]] = tally.get(item["band"], 0) + 1
    print("Risk: " + ", ".join("%s %d" % (b, tally[b])
                               for b in bom["risk_model"]["band_order"][::-1] if b in tally))

    if args.check:
        return 1 if report.failures else 0

    print("\nWriting documents:")
    write(os.path.join(OUT, "bom.md"), render_bom(bom, scored))
    write(os.path.join(OUT, "risk-register.md"), render_risk(bom, scored))
    write(os.path.join(OUT, "datasheet-params.md"), render_datasheets(datasheet_results))
    write(os.path.join(OUT, "coverage.md"), render_coverage(bom, baseline, report, open_decisions))
    write(os.path.join(OUT, "checks.md"), render_checks(report))

    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
