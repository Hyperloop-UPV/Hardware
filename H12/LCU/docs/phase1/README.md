# LCU_H12 — Phase 1: Component Picking, Datasheet Parsing and BOM Risk

**Status:** 27 BOM lines across 22 parts. 9 carry over unchanged, 6 change, 4 are new, 5 are
proposed pending sign-off, 2 await selection, 1 deferred. 6 of 7 decisions closed; 1 deferred. One
finding changes the Phase 0 analog description.

**Inputs:** the LCU_H11 Altium LiveBOM (89 line items, 54 with a manufacturer part number),
the LCU_H10 and LCU_H11 schematics, and the SICK airgap datasheet.

| File | Contents |
|---|---|
| `bom/lcu_h12.bom.json` | The BOM model: parts, lines, risk weights, decisions. Source of truth. |
| `bom/h11_baseline.json` | The LCU_H11 BOM extracted from the Altium archive. Committed so the analysis runs without Altium. |
| `bom/import_h11_bom.py` | Regenerates the baseline from `LCU_H11/LCU_H11.zip`. |
| `bom/build.py` | Validates, scores, parses datasheets, regenerates the documents below. |
| `docs/phase1/generated/bom.md` | The BOM, grouped by block. |
| `docs/phase1/generated/risk-register.md` | Lines ordered by risk and impact. |
| `docs/phase1/generated/datasheet-params.md` | Parameters extracted from local datasheets. |
| `docs/phase1/generated/coverage.md` | Carry-over accounting and open decisions. |
| `docs/phase1/generated/checks.md` | Automated checks. |

```sh
python bom/import_h11_bom.py     # only if the reference archive changes
python bom/build.py              # validate, score, regenerate
python bom/build.py --check      # validate only; exit 1 on failure
```

---

## 1. Method

### 1.1 Carrying over instead of re-picking

The LCU_H12 is an update of an existing, flying board, so the default for every line is
"inherit from LCU_H11". Re-picking parts that already work would discard bench time and
introduce risk for no benefit. A part is only touched for one of four reasons:

- it is at end of life (`SN74AHCT367`);
- the requirement changed (`CAN` on both MCUs, `0.1 %` sense resistor, ESD protection);
- the connector family changed (all Nano-Fit to Micro-Fit+);
- it does not exist in LCU_H11 because H11 replaced that function with something that never
  worked (`F-01`, the airgap front end).

Every line therefore carries a status: `carry`, `changed`, `new` or `select`. Nine lines
carry over untouched; six change; three are new; seven still need selection.

The carry-over claim is enforced, not assumed: `build.py` checks every `carry` line against
the extracted H11 baseline and fails if the part cannot be found there. That check is how
`F-01` surfaced.

### 1.2 Risk model

Two axes, deliberately not merged:

- **Risk** — likelihood of a supply or availability problem, an additive score over explicit
  flags (lifecycle end-of-life 8, NRND 5, vendor-recommended migration 4, unknown 3,
  single-source 2, no alternate 1, stock under 1000 or 100, unverified parameters 2, missing
  datasheet 1, new to the design 1). Bands: critical ≥ 9, high ≥ 6, medium ≥ 3, low
  otherwise.
- **Impact** — what happens if the line fails in service: `safety`, `functional`,
  `auxiliary`.

Keeping them apart matters, because "low risk, safety impact" is a real and common category
here: a Micro-Fit+ header is trivially available and its failure drops the pod. Collapsing
both into one number would either hide the availability problem or exaggerate it.

Result: **1 critical, 3 high, 8 medium, 13 low** on risk; **16 safety, 4 functional, 5
auxiliary** on impact.

### 1.3 Datasheet parsing

`build.py` runs `pdftotext` over `H12/LCU/datasheets/` and looks for the parameters declared
per part in `datasheet_index`. Adding a datasheet means dropping the PDF into that folder,
naming it by MPN, and filling in the filename.

Coverage is currently poor: **1 of 7 declared datasheets is present** (the SICK airgap
sensor). The manufacturer sites block scripted downloads — ST returns an HTTP/2 stream
reset and Microchip returns 403 — so the files have to be fetched by hand. Until they are,
the affected parameters are unverified, which the risk model counts as a flag rather than
silently ignoring.

The practical output today is the airgap sensor's key figures, which are the ones that feed
the analog design: 60–200 mm range, 4–20 mA output at 16-bit resolution, 7.5 kHz maximum
rate, ±140 µm linearity.

---

## 2. Findings

### F-01 — The airgap analog front end exists only in the LCU_H10 BOM

LCU_H11 does not contain the 4-20 mA front end at all. Its Airgap Sensors sheet carries
eight **DFSDM** clock/data pairs (`DFSDM_CKOUT_0..7`, `DFSDM1_HF_DATIN1`) plus a 5 V filter
block built on a `DLW43SH110XK2L` common-mode choke — a sigma-delta interface, not a
current-loop input. The modulator board is the `A-ADC` board in the H11 inventory.

That path was never brought up, and LCU_H11 firmware reads the airgaps on ADC1, so **H11
hardware and firmware disagree about how the airgap sensors are connected**. This explains
the reported behaviour and the instruction to keep the analog front end.

Consequence for H12: the front end is reinstated from **LCU_H10** — 160 Ω sense resistor,
5th-order Butterworth in the `4-20mA conditioning sub-block`, MCP6022 into ADC1 — and those
parts are **not** in the LCU_H11 BOM. They have to be specified from the H10 schematic.
Three BOM lines are affected: `L-AGP-AFE`, `L-AGP-RSENSE`, `L-AGP-FILTER`.

Scope correction for the filter: LCU_H10 does not build a discrete network. The Airgap
Sensors sheet uses **one switched-capacitor filter IC per channel** (`MAX7420`, 5 V,
5th-order Butterworth) with its corner set by the internal oscillator from a 220 pF
capacitor. So the missing block is eight ICs and a handful of passives, not the eighty
discrete parts originally assumed.

The 3.3 V analog rail then forces a part change: the family splits by supply
(`MAX7418`–`MAX7421` at 5 V, `MAX7422`–`MAX7425` at 3 V) and by response
(`MAX7419`/`MAX7423` Bessel, `MAX7420`/`MAX7424` Butterworth, the rest elliptic). The
3 V Butterworth is therefore the **`MAX7424`** — same response, same 8-pin package.

Phase 0 §4.2 describes the analog topology without saying which board it comes from. The
description is correct; it describes LCU_H10, not LCU_H11.

### F-02 — The SN74LVC541A in the H11 BOM is there for a different purpose

`Buffer_CK` on LCU_H11 is the DFSDM clock buffer: `SN74LVC541A` with 33 Ω series resistors
driving `DFSDM_CKOUT` to the eight modulator channels. The block disappears with the
sigma-delta path, but the part and the 33 Ω pattern stay: it is the candidate primary for
the LPU PWM buffers.

---

## 3. Component decisions

| ID | Topic | Status | Outcome |
|---|---|---|---|
| `D-01` | LPU output buffer bank | **decided** | `SN74AHCT541`, **five packages**. Three signals leave the LCU per LPU at 5 V — `PWM_1`, `PWM_2` and `RESET` — so the bank carries 30 signals. TTL-compatible inputs put VIH at 2.0 V, so the 3.3 V MCU drive needs no level shifter and the output is full 5 V CMOS. Two LPUs per package (four PWM + two RESET channels) keeps the LCU_H10 grouping: 30 of 40 channels used. Four packages would be the arithmetic minimum; the fifth costs about €0.40 and 30 mm² and avoids splitting an LPU pair across packages. |
| `D-02` | microSD socket | **decided** | `MOLEX-216571-2002`. Both candidates appear in VCU_H11, but only the Molex part has a verified footprint and an embedded 3D STEP model (`216571-2002-Footprint-1` / `216571-2002.stp`). The TE `1939115-1` has `Package=None` and is flagged `Availability=Unavailable` in the VCU vault. Carry the footprint across verbatim rather than re-creating it. |
| `D-03` | Protection on off-board lines | **proposed** | Three tiers, costed in the BOM. Tier 1: the 50 signals that leave the board on the LPU connectors (20 PWM, 10 RESET, 10 READY, 10 FAULT). Tier 2: the 20 analog inputs (8 airgap loops, 4 corner NTC). Tier 3, board-internal signals, not proposed. CAN gets `SM712-02HTG`, already in the BOM. Awaits sign-off on the tier. |
| `D-07` | Buffer bank part and package count | **decided** | Five `SN74AHCT541` packages. RESET is active-low, so releasing it needs an actively driven HIGH and the buffer is mandatory — that rules out the unbuffered-reset option. The 8-channel TSSOP-20 is the area optimum at 3.6 mm² per channel; 16-bit packages reduce part count, not area. See §3.2. |
| `D-06` | Reset buffering and the brake override | **decided** | RESET shares the buffer bank, so the Phase 0 open-drain wired-AND cannot work against a push-pull output. The override moves to the buffer's 3-state enable: active-low, pulled to disabled, forced disabled by `brake_fault` through one gate shared by all five packages. Each RESET line gets a pull resistor to its asserted level. `L-RST-DRV` drops from twelve open-drain channels to a single gate. |
| `D-04` | Status indication | **decided** | Two hardware LEDs per LPU, one per status line, each driven through a series resistor: lit on `READY` means levitating, lit on `FAULT` means no fault. No driver IC, no inverter, no diode-OR, no MCU pins, no firmware. See §3.6. |
| `D-05` | Airgap amplifier | deferred | Keep `MCP6022`. Sensor linearity limits the chain to about 10 bits, so a lower-offset amplifier changes nothing measurable until that is fixed. Revisit later. |

### 3.1 The output bank: 30 channels, 5 packages, one enable

Three signals leave the LCU per LPU — `PWM_1`, `PWM_2` and `RESET` — all at 5 V. Ten LPUs
therefore need **30 buffered channels**, not 20. LCU_H10 solved exactly this with a hex
buffer (`SN74AHCT367`, six channels) covering two LPUs; H12 uses the eight-channel
`SN74AHCT541` with the same 1:2 grouping, so each package carries four PWM channels and two
RESET channels and leaves two channels spare. Five packages, 30 of 40 channels used.

A 3.3 V buffer cannot do the job at all. The LPU needs a 5 V input, and an `SN74LVC541A`
running from 3.3 V never exceeds about 3.3 V, so it is rejected despite being cheaper and
already in the BOM. The opposite direction — a 5 V buffer driven by a 3.3 V MCU — is only
safe because AHCT inputs are TTL-threshold: `VIH = 2.0 V`, so a 3.3 V CMOS output drives them
with 1.3 V of margin. A plain HC part at 5 V would need `0.7 × VCC = 3.5 V` and would be
marginal.

Two consequences follow. The 5 V rail is now load-bearing for PWM *levels*, not just for
drive strength, so a brownout produces indeterminate outputs rather than silence. And because
RESET is a push-pull output in the same bank, a brake fault must act on the enable rather than
on the reset net (`D-06`).

### 3.2 Buffer bank: the package arithmetic

Channel count is fixed at 30 (2 PWM + RESET per LPU) unless RESET leaves the bank. Body areas
are from the package drawings; total is area × count.

| Option | Part | ch/pkg | Package | Body mm | mm²/pkg | Pkgs | Total mm² | mm²/ch |
|---|---|---|---|---|---|---|---|---|
| A | `SN74AHCT367` | 6 | TSSOP-16 | 5.0 × 4.4 | 22.0 | 5 | 110 | 3.7 |
| B | `SN74AHCT541` | 8 | TSSOP-20 | 6.5 × 4.4 | 28.6 | 4 | 114 | **3.6** |
| C | `SN74AHCT541` | 8 | TSSOP-20 | 6.5 × 4.4 | 28.6 | 5 | 143 | **3.6** |
| D | `SN74AHCT244` | 8 | TSSOP-20 | 6.5 × 4.4 | 28.6 | 5 | 143 | 3.6 |
| E | `SN74AHCT16244` | 16 | TSSOP-48 | 12.5 × 6.1 | 76.3 | 2 | 152 | 4.8 |
| F | `SN74AHCT16244` | 16 | TVSOP-48 | 9.7 × 4.4 | 42.7 | 2 | **85** | **2.7** |
| G | no reset buffer, 3 × `SN74AHCT541` | 8 | TSSOP-20 | 6.5 × 4.4 | 28.6 | 3 | 86 | 3.6 |

**Going bigger does not save space.** The 16-bit part is *worse* per channel in TSSOP-48
(4.8 mm² against 3.6) because the wider body and 0.5 mm pitch more than cancel the extra
channels. It only reduces the part count from five to two. The one genuine area win is the
same 16-bit part in **TVSOP-48, 40 % smaller at 85 mm² total**, and that is 0.4 mm pitch —
which is a real cost unless the board is reflowed.

So the octal TSSOP-20 is the area optimum, and the choice is really about part count:

- **C (current, 5 packages)** — keeps each LPU pair on one package and one enable, 10 of 40
  channels spare. Costs 29 mm² more than B, which is 0.08 % of the board.
- **B (4 packages)** — the minimum that still uses a TSSOP-20. Saves one component; splits an
  LPU pair across two packages.
- **F (2 packages)** — smallest and fewest parts, at 0.4 mm pitch.

**Option G is ruled out.** Not buffering RESET would drop the bank to 20 channels — 3 packages,
86 mm², and the simpler open-drain brake override of Phase 0 §6.3 — but it requires the LPU
RESET input to be active-high.

It is **active-low**: driving it HIGH releases the reset and lets the LPU work. Releasing is
therefore an actively driven state, which a pull resistor cannot produce, so a push-pull driver
is mandatory. A pull-down *can* hold the asserted state when the buffer lets go, which is
exactly the arrangement the design uses.

The resolution is option **C**: five `SN74AHCT541`, two LPUs per package, 30 of 40 channels used.
The five spare-part cost of the fifth package is 29 mm² and about €0.40, against keeping each
LPU pair on one package and one enable.

### 3.3 Parts selected in this phase

| Line | Part | Why |
|---|---|---|
| `L-LPU-BUF` | `SN74AHCT541` ×5 | Replaces the NRND `SN74AHCT367`. Accepts the 3.3 V MCU drive on TTL thresholds, outputs 5 V, and carries 30 channels (2 PWM + RESET per LPU). |
| `L-AGP-CONN`, `L-NTC-CONN`, `L-BRAKE-CONN`, `L-BOOT-CONN` | `MOLEX-206832-0401` | One part number for four functions: 8 airgap, 4 corner NTC, 2 brake chain, 2 bootloader. Simplifies both BOM and harness tooling. |
| `L-AGP-RSENSE` | `160R-0603-0.1pct` | Reinstated from H10. 0.1 % already matches the sensor's linearity limit; 0.01 % would buy nothing. |
| `L-IMU` | `ICM-42688-P` | Optional, unpopulated. Chosen for simple SPI timing; any part the control team already has drivers for would supersede it. |
| `L-SD-SOCKET` | `MOLEX-216571-2002` | Verified footprint and 3D model in VCU_H11; the TE alternative is flagged unavailable. |
| `L-SD-ESD` | `82306050029` | Würth WE-VE ULC, already qualified on VCU_H11 and already in the BOM. |
| `L-ESD-LPU`, `L-ESD-ANALOG` | per voltage class | 70 suppressors; see §3.5 for why one part number does not work. |
| `L-LED-LPU`, `L-LED-HEALTH` | `VLMTG1300-GS08` | 20 LEDs with series resistors, one per status line. All hardware, all optional. |
| `L-ESD-CAN` | `SM712-02HTG` | Designed for two-line differential buses; already in the BOM. |

### 3.4 Lines still awaiting selection

| Line | Function | Qty | Candidates |
|---|---|---|---|
| `L-RST-DRV` | `brake_fault` → buffer enable gate | 1 | `74AHC1G08`, `74AHC08`, or a discrete transistor pulling the enable high |
| `L-NTC-EXC` | Corner NTC excitation and filter | 4 | 10 kΩ 0.1 % pull-up to 3V3 + 220 Ω + 10 nF, mirroring LCU_H11 `Temp_conditioning` |

**Deferred (1):** `L-AGP-FILTER`, the airgap 5th-order Butterworth filter. A different
filter design may be adopted, so it is not being specified now. Two things to carry when it
is picked up: it is eight switched-capacitor filter ICs rather than a passive network, and
the 3.3 V analog rail makes the `MAX7424` the equivalent of the `MAX7420` that LCU_H10 uses.

---

### 3.5 Protection: what it is actually for

The question worth answering before buying 70 suppressors.

**Three distinct threats reach these pins.**

1. **ESD during handling and mating.** Every LPU connector is mated and unmated by hand, and
   the pod is assembled and disassembled repeatedly. A contact discharge into a connector pin
   goes straight down the harness to a buffer input or an MCU pin. The internal ESD structures
   on those parts are sized for a part sitting on a bench, not for a cable plugged in by someone
   wearing a fleece.
2. **Transients coupled from the switching power stages.** The LPUs switch tens of amps at
   20 kHz, and the LPU harness runs alongside the signal lines. The observed airgap glitch is
   exactly this mechanism on an analog channel — 69–89 % of the bad samples coincide with
   |I| > 5 A. On the digital lines it appears as fast over- and under-shoot.
3. **Hot-plug and ground offset.** Mating a connector while the system is powered can connect a
   signal pin before its ground return. Separately, the LPU end and the LCU end are at different
   points on a common ground with real inductance between them, so the same signal can be
   referenced quite differently at the two ends during a current step.

**What each threat does to the silicon.** In the buffer, repeated over- and under-shoot at the
output stage degrades it progressively — this is consistent with the reported field behaviour.
At an MCU pin, an over-voltage forward-biases the protection diode and injects current into
`VDDA`, which corrupts conversions on other channels; sustained enough, it latches the pin.

**The clamp is the second half of the fix, not the first.** What actually limits current into a
pin is the series resistor. With a clamp that conducts at 9 V driving into a 3.3 V pin, a 100 Ω
series resistor still pushes about 57 mA through the internal diode; 1 kΩ brings it to 5.7 mA.
So the priority is:

1. **series resistor on every off-board line** — limits the current and kills the ringing;
2. **clamp at the connector** — absorbs the bulk energy before it reaches the resistor;
3. **the clamp's standoff voltage above the signal's maximum level** — otherwise it leaks or
   clips in normal operation.

**This forces a correction to the earlier plan.** Standardising on one WE-VE ULC part for
everything was wrong: it is a 5 V-standoff part, which sits right at the rail of a 5 V logic
line and leaks, and is useless on the 24 V brake chain. Three voltage classes are needed:

| Class | Lines | Standoff |
|---|---|---|
| 6 V | 5 V LPU signals (PWM, RESET) | above 5 V, so it never conducts in normal operation |
| 5 V | 3.3 V status, presence and analog inputs | above 3.3 V |
| 30 V | `brake_fault` daisy chain | above the 24 V working level |
| 24 V asymmetric | CAN, `SM712-02HTG` | already correct, already in the BOM |

**What protection does not do.** It does not fix the airgap coupling — that is a grounding and
shielding problem, and the front-end supply change is what stops the ADC being damaged while it
is being debugged. It also does not replace the tri-state enable, the pull-downs or the presence
detection. Protection bounds energy; it does not define states.

**Cost and tiers.** Seventy suppressors plus series resistors, roughly 90 mm² of a 38 400 mm²
board and about €10 at prototype quantity (0.2 % of the board). Tier 1 is the 50 signals that
leave on the LPU connectors; tier 2 adds the 20 analog inputs, whose cables run alongside the
LPU power leads. Tier 1 alone still covers where the exposure actually is. Against that, LCU_H10
and LCU_H11 currently let every off-board digital and analogue signal reach silicon with no
clamp at all.

### 3.6 Status indication

Two LEDs per LPU, both driven directly from the status line with nothing but a series resistor:

| Line | Driven by | Lit means | Parts |
|---|---|---|---|
| `L-LED-LPU` | `READY` | that magnet is levitating | 10 LEDs + 10 resistors |
| `L-LED-HEALTH` | `FAULT` | that LPU reports no fault | 10 LEDs + 10 resistors |

Forty parts in total, all 0603, all optional, and the same topology repeated twenty times. No
driver IC, no inverter, no diode-OR, no MCU pins, no firmware.

The three states read as:

| `READY` LED | `FAULT` LED | Meaning |
|---|---|---|
| lit | lit | levitating |
| dark | lit | healthy but idle |
| dark | dark | faulted, or the connector is unseated |

**Why the fault LED is inverted in meaning rather than in hardware.** `FAULT` is active-low, so
the obvious version — a red LED that lights on a fault — has to *sink* current into the line.
While the LPU drives the line low that is harmless, but with the connector unseated there is no
driver and only the 10 kΩ pull-down, so the LED current returns through it and lifts the line to
about **0.9 V** against a VIL of about 1.0 V. The presence detector would go marginal in exactly
the state it exists to detect, and doing it per LPU properly would need a transistor on each
line.

Indicating the **absence** of a fault removes the problem entirely. The LED sits from `FAULT` to
ground exactly like the `READY` one, so it conducts only when the line is HIGH. Un-driven, the
pull-down holds the line at 0 V, the LED stays off and draws nothing, and the logic level is
untouched. Both signals now use one rule, which is worth more than the extra LED.

The trade-off is that a fault is signalled by an absence of light rather than a red lamp coming
on. For a bench diagnostic that is acceptable, and the board keeps the five firmware-driven LEDs
inherited from LCU_H11 for an at-a-glance alarm if one is wanted.

**Colour.** Green on both, because the forward drop is about 2.0 V and leaves 1.3 V across the
series resistor on a 3.3 V rail. Blue would be a poor choice here: its forward voltage is around
3.0 V, so on a 3.3 V rail the current would be tiny and very sensitive to part-to-part spread. If
the two indicators need to look different, use an amber 0603 for the health LED rather than a
blue one.

Rejected: a 16-channel constant-current sink (`TLC5926` and similar). It would give the same
information in fewer packages, but it needs two or three MCU pins, a serial protocol, firmware
support and a defined power-up state before it shows anything.

Everything is DNP-able: leaving the LEDs and their resistors unpopulated affects nothing else.

## 4. Risk summary

| Risk | Impact | Score | Line | Part | Drivers |
|---|---|---|---|---|---|
| high | safety | 7 | `L-ETH-PHY` | `KSZ8041TLI` | vendor migration, single-source, datasheet missing |
| high | safety | 7 | `L-LPU-CONN` | `TE-5499922-6` | lifecycle unknown, single-source, unverified |
| high | safety | 6 | `L-MCU` | `STM32H723ZGT6` | single-source, long lead, datasheet missing |

Everything else is medium or low, including all four remaining unselected lines, which score
only on `not_selected`. Closing `D-02` dropped the microSD socket out of the critical band: the
part is now chosen and its footprint is proven, so only the datasheet is missing.

Three observations behind those rows:

- **`SN74AHCT367` is formally NRND.** TI states it directly in the datasheet: *"NRND: Not
  recommended for new designs. Device is in production to support existing customers, but TI
  does not recommend using this part in a new design."* That is objective grounds for the
  replacement, independent of the degradation reported in the field.
- **The `KSZ8041` family is being steered elsewhere.** Microchip publishes AN4212, *"Migrating
  to KSZ8081/8091 Family PHY Transceivers"*, written for customers using KSZ8041 devices.
  The note names the NL/RNL/MLL variants rather than the TL, so this is a family signal, not
  an EOL notice for the exact part. A migration would be a pinout change, not a drop-in.
- **The MCU is a supply risk, not a lifecycle risk.** The STM32H723ZGT6 is active and in the
  long-term availability programme, but it is effectively sole-source and H7 parts have had
  multi-month lead times. Buying both MCUs early is the most effective single de-risking
  action available on this board.

Full detail, including the two-axis scoring arithmetic, is in `generated/risk-register.md`.

---

## 5. What this phase did not cover

- **Power budget.** The rails are inherited and nothing has been added up. The only new
  loads are the SD card, the corner NTC dividers and a second CAN transceiver. `LT1963A` at
  1.5 A has margin unless the SD card and a LED driver together exceed a few hundred mA.
  `L-AGP-FILTER` and `L-LED-DRIVER` must be selected before this can close.
- **Footprints.** No footprint has been chosen or checked against the mechanical envelope.
- **Passive re-verification.** The 49 passive lines in the H11 baseline are inherited
  wholesale. Their lifecycle data is a snapshot from when the Altium archive was produced;
  re-check at order time, not now.
- **The airgap filter topology.** Deferred by decision, not by omission. If a different
  filter is chosen, the eight switched-capacitor ICs and their surrounding passives change
  with it, and the `MAX7424` substitution stops being relevant.
- **Schematic capture.** Nothing has been drawn.

---

## 6. Next actions

1. Sign off the protection (`D-03`). Parts, quantities and voltage classes are now specified;
   what is missing is confirmation that tiers 1 and 2 are both wanted, and the actual part
   numbers per voltage class.
2. Specify `L-AGP-FILTER` once the filter topology is decided. It is no longer the bottleneck
   it appeared to be: eight filter ICs plus a few passives, not eighty discrete parts. The
   `MAX7424` is the drop-in answer if the LCU_H10 topology is kept.
3. Close `L-RST-DRV`, now a single gate rather than twelve channels, and close `L-LED-DRIVER`.
4. Fetch the six missing datasheets by hand into `datasheets/` and re-run `build.py` so those
   parameters stop being unverified.
5. Verify `TE-5499922-6` lifecycle directly with TE, and confirm its 44.5 mm body — the
   Phase 0 mechanical figure depends on it.
