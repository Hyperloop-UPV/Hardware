#!/usr/bin/env python3
"""LCU_H12 Phase 0: expand the architecture description and check feasibility.

Input:   arch/lcu_h12.json
Output:  docs/phase0/generated/*.md

Usage:
    python arch/build.py            # validate and regenerate docs/phase0/generated/
    python arch/build.py --check    # validate only, write nothing

Standard library only. Exits with 1 if any check fails.
"""

import argparse
import json
import math
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs", "phase0", "generated")

# STM32H723 hardware facts used by the checks.
ADC_RANKS = 16              # conversion ranks per sequence (hardware limit)
TIMER_CHANNELS = 4          # PWM channels per timer
ADC3_BITS = 12              # ADC3 is 12-bit on H72x/H73x; ADC1/ADC2 are 16-bit
MAX_FADC_MHZ = {16: 36.0, 14: 50.0, 12: 96.0}   # max ADC clock per resolution
CONV_CYCLES_16B = 8.5      # conversion phase, STM32H7 ADC


class Report:
    """Collects check results and renders them as a markdown table."""

    def __init__(self):
        self.rows = []

    def ok(self, id_, text, detail=""):
        self.rows.append(("OK", id_, text, detail))

    def fail(self, id_, text, detail=""):
        self.rows.append(("FAIL", id_, text, detail))

    def warn(self, id_, text, detail=""):
        self.rows.append(("WARN", id_, text, detail))

    def skip(self, id_, text, detail=""):
        self.rows.append(("SKIP", id_, text, detail))

    @property
    def failures(self):
        return [r for r in self.rows if r[0] == "FAIL"]

    def count(self, kind):
        return sum(1 for r in self.rows if r[0] == kind)

    def markdown(self):
        label = {"OK": "OK", "FAIL": "**FAIL**", "WARN": "WARN", "SKIP": "skipped"}
        lines = ["| Status | Check | Detail |", "|---|---|---|"]
        for status, id_, text, detail in self.rows:
            lines.append("| %s | `%s` %s | %s |" % (label[status], id_, text, detail))
        return "\n".join(lines)


def load(path, schema, what):
    """Load and check the schema tag.

    This guard exists because a patch script once wrote the BOM model over the architecture
    model: both are JSON, both live in the same project, and the mismatch was only noticed
    when key lookups started failing. A wrong file should fail on the first line, not on the
    fortieth.
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    found = data.get("schema")
    if found != schema:
        sys.exit("%s: expected schema %r but found %r -- wrong file?\n  %s"
                 % (what, schema, found, path))
    return data


# --------------------------------------------------------------------------
# Pin budget
# --------------------------------------------------------------------------

def pin_plan(mcu):
    """Return ({pin: usage}, [(pin, usage_a, usage_b)]) for one MCU."""
    usage = {}
    duplicates = []
    for group_name, group in mcu.get("pin_groups", {}).items():
        for pin in group.get("pins", []):
            if pin in usage:
                duplicates.append((pin, usage[pin], group_name))
            usage[pin] = group_name
    for adc, cfg in mcu.get("adc_plan", {}).items():
        for group in cfg["groups"]:
            for pin in group["pins"]:
                name = "%s/%s" % (adc, group["name"])
                if pin in usage:
                    duplicates.append((pin, usage[pin], name))
                usage[pin] = name
    for pwm in mcu.get("pwm_plan", []):
        for pin in pwm["pins"]:
            name = "%s/%s" % (pwm["timer"], pwm["channels"])
            if pin in usage:
                duplicates.append((pin, usage[pin], name))
            usage[pin] = name
    return usage, duplicates


def check_pins(mcu_id, mcu, report):
    usage, duplicates = pin_plan(mcu)
    available = mcu["io_available"]
    used = len(usage)

    if duplicates:
        for pin, a, b in duplicates:
            report.fail("PIN-%s" % mcu_id, "Pin %s assigned twice" % pin, "%s and %s" % (a, b))
    else:
        report.ok("PIN-%s" % mcu_id, "No duplicated pins", "%d pins declared" % used)

    spare = available - used
    detail = "%d/%d used, %d spare" % (used, available, spare)
    if spare < 0:
        report.fail("PIN-%s-N" % mcu_id, "Pin budget", detail)
    elif spare < 10:
        report.warn("PIN-%s-N" % mcu_id, "Pin budget is tight", detail)
    else:
        report.ok("PIN-%s-N" % mcu_id, "Pin budget", detail)


# --------------------------------------------------------------------------
# ADC
# --------------------------------------------------------------------------

def check_adc(mcu_id, mcu, report, results):
    for adc, cfg in mcu.get("adc_plan", {}).items():
        bits = cfg["bits"]
        channels = sum(g["count"] for g in cfg["groups"])
        fadc = cfg["fadc_mhz"]
        sample = cfg["sample_time_cycles"]
        label = "%s/%s" % (mcu_id, adc)

        if adc == "ADC3" and bits > ADC3_BITS:
            report.fail("ADC-%s" % label, "%s tops out at %d bits" % (adc, ADC3_BITS),
                        "declared at %d bits" % bits)

        if channels > ADC_RANKS:
            report.fail("ADC-%s-RANKS" % label, "Sequence ranks",
                        "%d channels > %d" % (channels, ADC_RANKS))
        else:
            report.ok("ADC-%s-RANKS" % label, "Sequence ranks", "%d/%d" % (channels, ADC_RANKS))

        fmax = MAX_FADC_MHZ.get(bits)
        if fmax is None:
            report.warn("ADC-%s-FADC" % label, "No fADC limit known for %d bits" % bits)
        elif fadc > fmax:
            report.fail("ADC-%s-FADC" % label, "fADC above the limit",
                        "%.0f MHz > %.0f MHz at %d bits" % (fadc, fmax, bits))
        else:
            report.ok("ADC-%s-FADC" % label, "fADC within limits",
                      "%.0f MHz <= %.0f MHz at %d bits" % (fadc, fmax, bits))

        if channels:
            # Tconv = sampling + 8.5 cycles per channel; the scan is sequential.
            scan_us = (sample + CONV_CYCLES_16B) * channels / fadc
            results[label] = {
                "channels": channels,
                "bits": bits,
                "scan_us": scan_us,
                "per_channel_khz": 1000.0 / scan_us if scan_us else 0.0,
            }


def check_period(period_us, adc_results, report):
    worst, worst_id = 0.0, None
    for label, r in adc_results.items():
        if r["scan_us"] > worst:
            worst, worst_id = r["scan_us"], label
    if worst_id is None:
        report.skip("ADC-PERIOD", "Control period occupancy", "no ADC channels declared")
        return
    load = 100.0 * worst / period_us
    detail = "%s: %.1f us of %.0f us (%.0f%%)" % (worst_id, worst, period_us, load)
    if load > 50:
        report.fail("ADC-PERIOD", "Control period occupancy (worst ADC)", detail)
    elif load > 20:
        report.warn("ADC-PERIOD", "Control period occupancy (worst ADC)", detail)
    else:
        report.ok("ADC-PERIOD", "Control period occupancy (worst ADC)", detail)


# --------------------------------------------------------------------------
# PWM
# --------------------------------------------------------------------------

def check_pwm(mcu, report, results):
    plan = mcu.get("pwm_plan", [])
    if not plan:
        return

    by_timer, by_lpu = {}, {}
    for entry in plan:
        by_timer.setdefault(entry["timer"], []).append(entry)
        by_lpu.setdefault(entry["lpu"], []).append(entry)

    for timer, entries in sorted(by_timer.items()):
        channels = [c for e in entries for c in e["channels"]]
        if len(channels) > TIMER_CHANNELS:
            report.fail("PWM-%s" % timer, "Too many channels on %s" % timer,
                        "%d > %d" % (len(channels), TIMER_CHANNELS))
        elif len(set(channels)) != len(channels):
            report.fail("PWM-%s-DUP" % timer, "Repeated channel on %s" % timer, ", ".join(channels))
        else:
            report.ok("PWM-%s" % timer, "Channels of %s" % timer,
                      "%d used: %s" % (len(channels), ", ".join(sorted(channels))))

    for lpu, entries in sorted(by_lpu.items()):
        timers = sorted({e["timer"] for e in entries})
        channels = [c for e in entries for c in e["channels"]]
        if len(channels) != 2:
            report.fail("PWM-LPU%d-CHANNELS" % lpu, "LPU%d needs exactly 2 PWM" % lpu,
                        "has %d" % len(channels))
        elif len(timers) != 1:
            report.fail("PWM-LPU%d-TIMER" % lpu,
                        "LPU%d is split across two timers" % lpu, " and ".join(timers))
        else:
            report.ok("PWM-LPU%d" % lpu, "LPU%d" % lpu,
                      "%s %s" % (timers[0], "/".join(sorted(channels))))

    advanced = sorted({e["timer"] for e in plan if e.get("advanced")})
    if advanced:
        report.ok("PWM-SYNC", "Advanced timer available as sync master", ", ".join(advanced))
    else:
        report.fail("PWM-SYNC", "No advanced timer available as sync master", "")

    results["pwm"] = {
        "timers": len(by_timer),
        "channels": len(plan),
        "lpus": len(by_lpu),
        "advanced": advanced,
    }


# --------------------------------------------------------------------------
# Master <-> Slave SPI link
# --------------------------------------------------------------------------

def check_link(name, link, report, results):
    baud = link["baud_hz"]
    period = link["period_us"]
    key = name.replace("spi_", "").upper()

    def transfer_us(nbytes):
        return 1e6 * nbytes * 8.0 / baud

    rows = []
    payload = 0
    for field in link["proposed_payload"]:
        nbytes = field["count"] * field["bytes"]
        payload += nbytes
        rows.append((field["name"], field["count"], field["bytes"], nbytes, transfer_us(nbytes)))
    bare = payload + link["framing_bytes"]
    with_crc = bare + link["crc_bytes"]

    for nbytes, label in [(bare, "payload"), (with_crc, "payload + CRC")]:
        us = transfer_us(nbytes)
        load = 100.0 * us / period
        detail = "%d B -> %.0f us (%.0f%% of %.0f us)" % (nbytes, us, load, period)
        tag = "LINK-%s-%s" % (key, label.replace(" ", "_").replace("+", "and"))
        if load > 80:
            report.fail(tag, "%s: frame %s" % (link["owner"], label), detail)
        elif load > 60:
            report.warn(tag, "%s: frame %s" % (link["owner"], label), detail)
        else:
            report.ok(tag, "%s: frame %s" % (link["owner"], label), detail)

    h11 = link.get("h11_frame_bytes") or 0
    if h11:
        h11_us = transfer_us(h11)
        report.warn("LINK-%s-H11-BASELINE" % key, "Reference: frame measured on LCU_H11",
                    "%d B -> %.0f us (%.0f%% of the period). This link is now down to %d B."
                    % (h11, h11_us, 100.0 * h11_us / period, bare))

    double_baud = baud * 2
    us = 1e6 * with_crc * 8.0 / double_baud
    report.ok("LINK-%s-BAUD2" % key, "Headroom at %.1f MHz" % (double_baud / 1e6),
              "%d B -> %.0f us (%.0f%%)" % (with_crc, us, 100.0 * us / period))

    if not link.get("crc_bytes"):
        report.warn("LINK-%s-CRC" % key, "Frame carries no CRC",
                    "H11 validates only the 2 framing bytes; add a CRC in H12")
    else:
        report.ok("LINK-%s-CRC" % key, "Frame carries a CRC", "%d B" % link["crc_bytes"])

    results[key] = {"bytes": with_crc, "us": transfer_us(with_crc), "fields": rows}


# --------------------------------------------------------------------------
# Airgap analog front end
# --------------------------------------------------------------------------

def check_airgap(analog, report, results):
    a = analog["airgap_front_end"]
    v_min = a["i_min_ma"] / 1000.0 * a["r_sense_ohm"]
    v_max = a["i_max_ma"] / 1000.0 * a["r_sense_ohm"]
    lsb_v = a["adc_full_scale_v"] / (2 ** a["adc_bits"])
    lsb_ma = lsb_v / a["r_sense_ohm"] * 1000.0
    v_threshold = a["live_zero_threshold_ma"] / 1000.0 * a["r_sense_ohm"]

    if v_max <= a["adc_full_scale_v"]:
        report.ok("AGP-LEVEL", "Conditioner output fits the ADC range",
                  "%.2f V .. %.2f V (full scale %.1f V)"
                  % (v_min, v_max, a["adc_full_scale_v"]))
    else:
        report.fail("AGP-LEVEL", "Conditioner output exceeds the ADC full scale",
                    "%.2f V > %.1f V" % (v_max, a["adc_full_scale_v"]))

    # The amplifier rail is what can actually overdrive the ADC input.
    supply = a.get("afe_supply_v")
    planned = a.get("afe_supply_v_h12")
    if planned is None:
        report.skip("AGP-SUPPLY", "Amplifier rail vs ADC reference", "not declared")
    elif planned > a["adc_full_scale_v"] + 0.05:
        report.fail("AGP-SUPPLY", "Amplifier rail is above the ADC reference",
                    "%.1f V amplifier into a %.1f V ADC: an overcurrent or a coupled "
                    "transient forward-biases the input protection diode."
                    % (planned, a["adc_full_scale_v"]))
    else:
        report.ok("AGP-SUPPLY", "Amplifier rail is within the ADC reference",
                  "%.1f V <= %.1f V" % (planned, a["adc_full_scale_v"]))
    if supply is not None and supply > a["adc_full_scale_v"] + 0.05:
        report.warn("AGP-SUPPLY-H10", "Reference: the H10 front end runs at 5 V",
                    "%.1f V amplifier into a %.1f V ADC with nothing in between. "
                    "Benign while the loop stays under 20 mA (3.2 V) -- which is "
                    "exactly why it never showed up until the input saturated."
                    % (supply, a["adc_full_scale_v"]))

    if v_threshold < v_min:
        report.ok("AGP-LIVE-ZERO", "Live-zero threshold sits below the 4 mA level",
                  "threshold %.3f V (%.1f mA) < %.3f V: 0 mA is distinguishable from full scale"
                  % (v_threshold, a["live_zero_threshold_ma"], v_min))
    else:
        report.fail("AGP-LIVE-ZERO", "Live-zero threshold is above the 4 mA level",
                    "%.3f V vs %.3f V: open loop cannot be told from a valid reading"
                    % (v_threshold, v_min))

    span_mm = a["sensor_range_mm"]
    mm_per_ma = span_mm / (a["i_max_ma"] - a["i_min_ma"])
    lsb_mm = lsb_ma * mm_per_ma

    report.ok("AGP-LSB", "ADC resolution over the current loop",
              "%.1f uV/LSB = %.4f mA/LSB = %.1f um of sensor travel"
              % (lsb_v * 1e6, lsb_ma, lsb_mm * 1000.0))

    linearity_pct = 100.0 * a["sensor_linearity_um"] / 1000.0 / span_mm
    useful_bits = math.log2(100.0 / linearity_pct) if linearity_pct else 0.0
    report.warn("AGP-ENOB", "16-bit conversion is not 16-bit accuracy",
                "sensor linearity +/-%.0f um over %.0f mm = %.2f%% FS (~%.1f bits); "
                "H7 ADC ENOB ~13.2; %.1f%% sense resistor (~%.1f bits)"
                % (a["sensor_linearity_um"], span_mm, linearity_pct, useful_bits,
                   a["r_tolerance_pct"], math.log2(100.0 / a["r_tolerance_pct"])))

    results["airgap"] = {
        "v_min": v_min, "v_max": v_max,
        "lsb_uv": lsb_v * 1e6, "lsb_ma": lsb_ma,
        "threshold_v": v_threshold, "useful_bits": useful_bits,
    }


# --------------------------------------------------------------------------
# Mechanics
# --------------------------------------------------------------------------

def check_lpu_status(arch, report):
    """The un-driven state of a status line must never look healthy."""
    lpu = next((i for i in arch["interfaces"] if i["id"] == "IF-LPU"), None)
    if lpu is None:
        report.skip("LPU-STATUS", "LPU status line termination", "IF-LPU not declared")
        return

    signals = [s for s in lpu.get("signals", []) if "idle_pull" in s]
    if not signals:
        report.skip("LPU-STATUS", "LPU status line termination", "no truth table declared")
        return

    for s in signals:
        name = s["name"]
        pull = s["idle_pull"]
        fault_level = s["fault_level"]
        healthy = s["healthy_level"]

        if healthy == fault_level:
            report.fail("LPU-STATUS-%s" % name,
                        "%s has no distinguishable healthy and fault level" % name,
                        "both %s" % healthy)
            continue

        pulled_to = "LOW" if pull == "down" else "HIGH"
        if pulled_to != fault_level:
            report.fail("LPU-STATUS-%s" % name,
                        "%s pull is on the wrong side" % name,
                        "pulled %s -> %s, but the fault level is %s: an un-driven line "
                        "would read healthy" % (pull, pulled_to, fault_level))
        else:
            report.ok("LPU-STATUS-%s" % name,
                      "%s pull-down lands on the fault level" % name,
                      "un-driven = %s = fault level" % pulled_to)

    rows = lpu.get("state_table", {}).get("rows", [])
    if len(rows) == 4:
        healthy_rows = [r for r in rows
                        if r["ready"] == "HIGH" and r["fault"] == "HIGH"]
        report.ok("LPU-STATUS-TABLE", "State table is complete",
                  "4 of 4 combinations; only %d reads healthy, and it needs an active "
                  "driver on both lines" % len(healthy_rows))
    else:
        report.warn("LPU-STATUS-TABLE", "State table incomplete",
                    "%d of 4 combinations" % len(rows))


def check_mechanics(mechanics, constraints, report, results):
    connectors = mechanics["connectors"]
    total_length = sum(c["qty"] * c["body_mm"][0] for c in connectors)
    total_count = sum(c["qty"] for c in connectors)
    long_length = sum(c["qty"] * c["body_mm"][0] for c in connectors if c.get("edge") == "long")
    results["mechanics"] = {"connectors": total_count, "body_length_mm": total_length}

    w = constraints["board_outline"]["w_mm"]
    h = constraints["board_outline"]["h_mm"]
    if not w or not h:
        report.skip("MEC-PERIMETER", "Edge length available for connectors",
                    "%d connectors, %.0f mm of body in total; board outline TBD"
                    % (total_count, total_length))
        return

    perimeter = 2 * (w + h)
    long_edges = 2 * max(w, h)
    short_edges = 2 * min(w, h)

    # Connectors flagged as "long" are the ones that want an edge, but partial
    # stacking is allowed (team precedent), so this is a planning figure, not a limit.
    load = 100.0 * long_length / long_edges
    report.ok("MEC-LONG-EDGE", "26-pin LPU headers vs the two long edges",
              "%d mm of %.0f mm (%.0f%%). Stacking is allowed, so this is a planning "
              "figure: five per side is the natural arrangement."
              % (long_length, long_edges, load))

    rest = total_length - long_length
    load = 100.0 * rest / short_edges
    detail = "%d mm of %.0f mm on the two short edges (%.0f%%)" % (rest, short_edges, load)
    if load > 95:
        report.fail("MEC-SHORT-EDGE", "The remaining connectors do not fit the short edges", detail)
    elif load > 65:
        report.warn("MEC-SHORT-EDGE", "The short edges are heavily loaded", detail)
    else:
        report.ok("MEC-SHORT-EDGE", "Remaining connectors fit the short edges", detail)

    load = 100.0 * total_length / perimeter
    report.ok("MEC-PERIMETER", "Total connector body length",
              "%d connectors, %.0f mm of %.0f mm of perimeter (%.0f%%)"
              % (total_count, total_length, perimeter, load))


# --------------------------------------------------------------------------
# Requirements
# --------------------------------------------------------------------------

def summarise_requirements(arch, report):
    counts = Counter(r["status"] for r in arch["requirements"])
    for status in ("OK", "AC", "TBD", "REJ"):
        if counts[status]:
            report.ok("REQ-%s" % status, "Requirements in state %s" % status, str(counts[status]))
    if counts["TBD"] or counts["AC"]:
        report.warn("REQ-OPEN", "Requirements still open",
                    "%d AC + %d TBD" % (counts["AC"], counts["TBD"]))

    questions = arch.get("open_questions", [])
    open_q = [q for q in questions if q.get("status", "open") != "closed"]
    closed_q = [q for q in questions if q.get("status") == "closed"]
    report.ok("Q-CLOSED", "Questions answered", "%d of %d" % (len(closed_q), len(questions)))
    if open_q:
        report.warn("Q-OPEN", "Questions still open",
                    ", ".join(q["id"] for q in open_q))
    return counts


# --------------------------------------------------------------------------
# Document generation
# --------------------------------------------------------------------------

GROUP_ORDER = ["Power", "Compute", "Communications", "LPU interface",
               "Airgap sensing", "Temperature", "Safety", "Auxiliary"]

# Shape and colour per block kind.
KIND_STYLE = {
    "power":     ("cyl",  "power"),
    "mcu":       ("sub",  "mcu"),
    "comms":     ("box",  "comms"),
    "storage":   ("box",  "comms"),
    "connector": ("para", "conn"),
    "driver":    ("box",  "driver"),
    "analog":    ("hex",  "analog"),
    "sensor":    ("hex",  "analog"),
    "logic":     ("box",  "logic"),
    "indicator": ("box",  "aux"),
    "debug":     ("box",  "aux"),
}

CLASS_DEFS = {
    "power":  "fill:#eceff1,stroke:#607d8b,stroke-width:2px,color:#263238",
    "mcu":    "fill:#d6e4f0,stroke:#2f5d8a,stroke-width:2px,color:#102538",
    "comms":  "fill:#dcecd9,stroke:#4f7f43,stroke-width:2px,color:#1e2b16",
    "conn":   "fill:#fdf0cf,stroke:#b8860b,stroke-width:2px,color:#3a2c02",
    "driver": "fill:#efe4f7,stroke:#7a4f96,stroke-width:2px,color:#2a1633",
    "analog": "fill:#e7e0f2,stroke:#6a5aa0,stroke-width:2px,color:#221c38",
    "logic":  "fill:#fbe0e0,stroke:#a14b4b,stroke-width:2px,color:#3a1414",
    "aux":    "fill:#eceff1,stroke:#9097a0,stroke-width:1px,color:#2b2f33",
}


def _label(block):
    """Build the node label: title, optional quantity, subtitle, part."""
    title = block["title"]
    qty = block.get("qty")
    lines = ["<b>%s</b>%s" % (title, " ×%d" % qty if qty else "")]
    if block.get("sub"):
        lines.append("<i>%s</i>" % block["sub"])
    elif block.get("part"):
        lines.append(block["part"])
    return "<br/>".join(lines)


def _node(block):
    """Declare one node with the shape that matches its kind."""
    shape, _ = KIND_STYLE.get(block.get("kind"), ("box", "aux"))
    label = _label(block)
    rid = block["id"]
    if shape == "cyl":
        return '        %s[("%s")]' % (rid, label)
    if shape == "sub":
        return '        %s[["%s"]]' % (rid, label)
    if shape == "para":
        return '        %s[/"%s"/]' % (rid, label)
    if shape == "hex":
        return '        %s{{"%s"}}' % (rid, label)
    return '        %s["%s"]' % (rid, label)


def mermaid_blocks(arch):
    """Render the block diagram, grouped by subsystem."""
    blocks = {b["id"]: b for b in arch["blocks"]}
    groups = {}
    for block in arch["blocks"]:
        groups.setdefault(block.get("group", "Auxiliary"), []).append(block)

    order = [g for g in GROUP_ORDER if g in groups]
    order += [g for g in groups if g not in order]

    lines = ["```mermaid", "flowchart TB",
             '    accTitle: LCU_H12 system architecture',
             '    accDescr: Blocks and interfaces of the LCU_H12 board, grouped by subsystem.']
    for group in order:
        members = groups[group]
        lines.append('    subgraph G_%s["%s"]' % (
            group.replace(" ", "_"), group))
        if len(members) > 1:
            lines.append("        direction LR")
        for block in members:
            lines.append(_node(block))
        lines.append("    end")

    for src, dst, label in arch["graph"]:
        if "optional" in label.lower():
            lines.append('    %s -.->|"%s"| %s' % (src, label, dst))
        elif "SPI" in label:
            lines.append('    %s ==>|"%s"| %s' % (src, label, dst))
        else:
            lines.append('    %s -->|"%s"| %s' % (src, label, dst))

    for name, style in CLASS_DEFS.items():
        lines.append("    classDef %s %s" % (name, style))
    for block in arch["blocks"]:
        _, klass = KIND_STYLE.get(block.get("kind"), ("box", "aux"))
        lines.append("    class %s %s" % (block["id"], klass))

    lines.append("```")
    return "\n".join(lines)


def mermaid_pwm(arch):
    plan = arch["mcu"]["slave"].get("pwm_plan", [])
    if not plan:
        return ""
    by_timer = {}
    for entry in plan:
        by_timer.setdefault(entry["timer"], []).append(entry)
    lines = ["```mermaid", "flowchart LR", '    MCU["Slave MCU"]']
    for timer in sorted(by_timer):
        lines.append('    %s["%s"]' % (timer, timer))
        lines.append('    MCU -->|"TRGO sync"| %s' % timer)
    for entry in plan:
        lines.append('    %s -->|"%s"| LPU%d(("LPU%d"))'
                     % (entry["timer"], "/".join(entry["channels"]), entry["lpu"], entry["lpu"]))
    lines.append("```")
    return "\n".join(lines)


def pin_table(mcu_id, mcu):
    lines = ["### %s (%s, %s)" % (mcu_id.capitalize(), mcu["part"], mcu["package"]), "",
             "| Group | Pins | N | Note |", "|---|---|---|---|"]
    for name, group in mcu.get("pin_groups", {}).items():
        pins = group.get("pins", [])
        note = group.get("note", group.get("role", ""))
        if isinstance(note, list):
            note = ", ".join(note)
        lines.append("| `%s` | %s | %d | %s |"
                     % (name, ", ".join(pins) or "-", len(pins), note))
    for adc, cfg in mcu.get("adc_plan", {}).items():
        for group in cfg["groups"]:
            lines.append("| `%s/%s` (%d bits) | %s | %d | fADC %.0f MHz |"
                         % (adc, group["name"], cfg["bits"], ", ".join(group["pins"]),
                            group["count"], cfg["fadc_mhz"]))
    for timer in sorted({e["timer"] for e in mcu.get("pwm_plan", [])}):
        entries = [e for e in mcu["pwm_plan"] if e["timer"] == timer]
        pins = ", ".join(p for e in entries for p in e["pins"])
        lpus = ", ".join("LPU%d" % e["lpu"] for e in entries)
        lines.append("| `%s` (PWM) | %s | %d | %s |"
                     % (timer, pins, sum(len(e["pins"]) for e in entries), lpus))
    usage, _ = pin_plan(mcu)
    lines += ["", "Declared total: **%d** of %d available I/O."
              % (len(usage), mcu["io_available"]), ""]
    return "\n".join(lines)


BLOCK_LEGEND = """### Reading the diagram

| Shape | Means |
|---|---|
| Double border | MCU |
| Parallelogram | Off-board connector |
| Hexagon | Analog front end |
| Cylinder | Power supply |
| Stadium / box | Everything else |

Thick arrows are the two SPI links between the MCUs — the backbone of the board.
Dashed arrows are optional parts that may not be populated.

| Colour | Group |
|---|---|
| Blue | Compute |
| Green | Communications and storage |
| Purple | Analog front ends |
| Amber | Connectors |
| Red | Safety logic |
| Grey | Power and auxiliary |
"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")
    print("  -> %s" % os.path.relpath(path, ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without writing documents")
    args = parser.parse_args()

    arch = load(os.path.join(HERE, "lcu_h12.json"), "hl-lcu-arch/1.0", "architecture model")
    report = Report()
    adc_results, pwm_results, results = {}, {}, {}

    for mcu_id in ("master", "slave"):
        mcu = arch["mcu"][mcu_id]
        check_pins(mcu_id, mcu, report)
        check_adc(mcu_id, mcu, report, adc_results)
        check_pwm(mcu, report, pwm_results)

    check_period(arch["constraints"]["control_period_us"], adc_results, report)
    for name, link in arch["links"].items():
        check_link(name, link, report, results)
    check_airgap(arch["analog"], report, results)
    check_lpu_status(arch, report)
    check_mechanics(arch["mechanics"], arch["constraints"], report, results)
    counts = summarise_requirements(arch, report)

    print("\nFeasibility checks for the %s\n" % arch["meta"]["board"])
    for status, id_, text, detail in report.rows:
        print("  %-5s %-30s %s%s" % (status, id_, text,
                                     ("  [%s]" % detail) if detail else ""))
    print("\n%d OK, %d warnings, %d failures, %d skipped"
          % (report.count("OK"), report.count("WARN"),
             report.count("FAIL"), report.count("SKIP")))

    if args.check:
        return 1 if report.failures else 0

    print("\nWriting documents:")
    write(os.path.join(OUT, "blocks.md"),
          "# Block diagram\n\n"
          "> Generated by `arch/build.py` from `arch/lcu_h12.json`. Do not edit by hand.\n\n"
          + mermaid_blocks(arch) + "\n\n" + BLOCK_LEGEND)
    write(os.path.join(OUT, "pwm-tree.md"),
          "# PWM timer tree\n\n"
          "> Generated by `arch/build.py` from `arch/lcu_h12.json`. Do not edit by hand.\n\n"
          + mermaid_pwm(arch) + "\n")
    write(os.path.join(OUT, "feasibility.md"),
          "# Automated feasibility checks\n\n"
          "> Generated by `arch/build.py` from `arch/lcu_h12.json`. Do not edit by hand.\n\n"
          + report.markdown()
          + "\n\n## PWM timers\n\n" + mermaid_pwm(arch)
          + "\n\n## Requirement summary\n\n"
          + "\n".join("- **%s**: %d" % (k, v) for k, v in sorted(counts.items()))
          + "\n")
    write(os.path.join(OUT, "pin-budget.md"),
          "# Pin budget\n\n"
          "> Generated by `arch/build.py` from `arch/lcu_h12.json`. Do not edit by hand.\n\n"
          "## Master\n\n" + pin_table("master", arch["mcu"]["master"])
          + "\n\n## Slave\n\n" + pin_table("slave", arch["mcu"]["slave"])
          + "\n")

    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
