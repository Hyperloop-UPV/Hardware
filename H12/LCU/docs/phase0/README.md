# LCU_H12 — Phase 0: Architecture, Requirements Decomposition and Feasibility

**Status:** draft complete. 15 of 15 open questions answered; 49 requirements accepted,
6 to be confirmed, 1 pending a value. No schematic and no PCB have been produced.

**Baseline:** `LCU_H10` (system topology and LPU interface) + `LCU_H11` (differential LPU
link, buffer changes) + `VCU_H11` (PHY, Micro-Fit+, SD card).

| File | Contents |
|---|---|
| `arch/lcu_h12.json` | The architecture in machine-readable form. Single source of truth. |
| `arch/build.py` | Reads the JSON, validates it, computes feasibility and regenerates the documents below. |
| `docs/phase0/generated/blocks.md` | Block diagram, grouped by subsystem. |
| `docs/phase0/generated/pwm-tree.md` | PWM timer allocation. |
| `docs/phase0/generated/pin-budget.md` | Pin budget per MCU. |
| `docs/phase0/generated/feasibility.md` | All automated checks. |

The four documents under `generated/` are derived artefacts and must not be edited by hand.

```sh
python arch/build.py            # validate and regenerate
python arch/build.py --check    # validate only; exit code 1 on failure
```

Deriving the diagram, the pin budget and the feasibility report from a single source keeps
them consistent, and makes every figure in this document reproducible rather than asserted.

**Scope.** Phase 0 covers architecture, requirements decomposition and feasibility. It does
not include schematic capture, symbol or footprint selection, PCB placement or routing, or
any firmware change — although several requirements assume firmware work.

---

## 1. Changes with respect to LCU_H10

| Area | LCU_H10 | LCU_H12 | Rationale |
|---|---|---|---|
| Ethernet PHY | LAN8700IC-AEZ | **KSZ8041TLI** | The LAN8700 is end-of-life at Microchip. VCU_H11 carries the replacement with its full support circuit. |
| PHY support | — | 50 MHz oscillator, RJ45 `7499011222A` with integrated magnetics, PHYAD = 1 | Port of the VCU_H11 circuit. |
| MCU-side RMII | `PINSET_H10` (RXER on PG2) | `PINSET_H11` (no RXER) | Already supported by ST-LIB; requires no new firmware, and releases four pins on the Master. |
| LPU connector | 26-pin TE `5499922-6` | **unchanged**, contract frozen to LPU_H11 | All 26 contacts are assigned; nothing can be added. |
| Airgap connectors | Nano-Fit `105310-1204` | **Micro-Fit+ `206832-0401`** | All ten Nano-Fit connectors on the board are replaced; none other changes family. |
| Bootloader connectors | Nano-Fit `105310-1204` | **Micro-Fit+ `206832-0401`** | As above, one per MCU. |
| Master↔Slave link | one SPI, Master as master, single 899 B frame | **two SPIs**: control (Master master, 81 B) and **telemetry (Slave master, 210 B)** | Isolates bulk logging from the 500 µs control deadline. §5. |
| Storage | none | **microSD on SDMMC1**, same socket as VCU_H11 | Requested. Port of a proven path. |
| LPU temperature | 4 conditioning channels on `LCU_H11`, unused | **10 channels over the LPU connector** | One per LPU. Requires LPU_H11. |
| Corner NTC | none | **4 connectors direct to the NTCs at the pod corners** | Retains operation with LPU_H10, which has no temperature sensing. §7. |
| Airgap ADC | 12-bit (firmware default) on ADC1 | **16-bit**, ADC1 | Requested. Requires fADC to drop from 96 MHz to 36 MHz. |
| Airgap front end | 4-20 mA + MCP6022 + 5th-order Butterworth, amplifier on +5 V | **unchanged topology, amplifier moved to +3.3 V** | Removes the amplifier's ability to overdrive the ADC input. §4.2. |
| VBAT sensing | 10 channels on the Slave (ADC3) | **10 channels on the Master, 12-bit** | Resolution is not required; allocation follows pins. Uncrowds the Slave's ADC1. |
| PWM | 8 timers, LPU7 split across TIM16/TIM17, no dead-time | **6 timers, each LPU on a single timer, no dead-time** | LPU7 could not be edge-aligned. Dead-time belongs to the LPU. §3.2. |
| ADC triggering | free-running | **timer-triggered, one scan per control period** | Free-running sampling beats against the 20 kHz PWM and injects ripple into the current measurement. |
| Slave reset | 5 pulses on the fault line, decoded in software | **dedicated GPIO to Slave NRST** | Separates the fault line from the reset mechanism. |
| LPU reset | 5 GPIO for 10 LPUs, buffered | **10 GPIO, one per LPU**, through the 5 V buffer bank | RESET is 5 V, active-low, buffered like the PWM lines. Permits isolating one LPU without de-levitating the pod. §6.2. |
| LPU output buffer | 6-channel part, 2 LPUs per package | **8-channel part, 5 packages, 2 LPUs each** | 3 signals leave per LPU (2 PWM + RESET), so 30 channels are needed. |
| Buffer enable | 5 GPIO for 10 buffers | 1 GPIO, pulled to disabled | Same function, one pin, defined state on MCU failure. |
| LPU status lines | 20 lines into `Pull::None` pins, no termination | **pull-down plus series R and TVS** | Removes the floating CMOS input condition. §6.1. |
| brake_fault | none | **2× Micro-Fit+, daisy-chained**, straight passthrough with an optional normally-closed variant | Source: the VCU's 2-pin brake connector. §6.3. |
| CAN | TJA1051T/3 on one MCU, unused by firmware | **2 transceivers, both MCUs as CAN nodes** | FDCAN1 is in the H12 baseline. Master `PD0`/`PD1`, Slave `PB8`/`PB9`. |
| Board | — | 240 × 160 mm, unchanged | — |
| IMU | none | **optional, unpopulated** | Third position measurement to fuse against the airgaps. §8.3. |

The H12 avionics design stack applies unchanged: 6 layers, FR-4 Tg170, 1.6–1.8 mm, ENIG,
50 Ω single-ended / 100 Ω differential, board between 80×120 mm and 180×300 mm,
STM32H723ZGT6, ETH in RMII, SDMMC1 4-bit, FDCAN1, Micro-Fit+, JTAG. Recorded in
`constraints.design_stack`.

---

## 2. Feasibility summary

All figures are recomputed by `arch/build.py` from `arch/lcu_h12.json`.

| Item | Result |
|---|---|
| Master pin budget | 101 of 114 I/O, 13 spare |
| Slave pin budget | 61 of 114 I/O, 53 spare |
| Control link | 81 B including CRC → 38 µs, 8 % of the period |
| Telemetry link | 210 B including CRC → 98 µs, 20 % of the period |
| LCU_H11 reference frame | 899 B → 418 µs, 84 % of the period |
| Master ADC1 | 10 of 16 ranks, 12-bit (10 × VBAT) |
| Master ADC3 | 10 of 10 exposed channels, 12-bit (10 × LPU NTC) — full |
| Slave ADC1 | 16 of 16 ranks, 16-bit (8 airgap + 8 shunt) — full |
| Slave ADC2 | 2 ranks, 16-bit (2 shunt) |
| Slave ADC3 | 4 of 16 ranks, 12-bit (4 × corner NTC) |
| Worst ADC scan | 7.6 µs, 2 % of the 500 µs control period |
| Airgap front end | 0.64–3.2 V, 50.4 µV/LSB = 2.8 µm of sensor travel, live-zero threshold 0.576 V |
| Connectors | 31 total, 666 mm of body on an 800 mm perimeter |

### 2.1 Analog channel allocation

Only the airgap channels require 16 bits. VBAT and temperature accept any ADC at any
resolution, so their placement is driven by pin availability alone. Two consequences:

- The 16-bit, 36 MHz constraint binds on a single ADC — the Slave's ADC1, which carries
  the eight airgap channels. Everything else is 12-bit and could run at 96 MHz. Both MCUs
  will still run at 36 MHz, because `PLL3` is configured in ST-LIB's `Halconfig.cpp`,
  which both board builds share (`ARCH-09`).
- The Master's analog capacity is limited by pins, not resolution: 21 usable analog pins
  after Ethernet and `PHY_RST`, of which 10 VBAT + 10 NTC consume 20. The four corner NTC
  channels therefore sit on the Slave's otherwise empty ADC3. Multiplexing the VBAT group
  would free nine pins, at the cost of a mux for no functional benefit.

### 2.2 Mechanical

The outline is 240 × 160 mm, giving 800 mm of perimeter. The ten 26-pin LPU headers alone
account for 445 mm; arranged five per side along the two 240 mm edges they occupy ~222 mm
of 240 mm each. Connectors are not required to sit on the board edge — partial stacking is
accepted and has precedent — so that figure is a planning input rather than a constraint.
The two 160 mm edges carry the remaining 21 connectors at 69 % utilisation.

Two items to verify before the connector order is frozen:

- The 445 mm assumes `5499922-6` is a 2.54 mm amp-latch header with a 44.5 mm body. The
  1.27 mm variant would halve it.
- A stacked connector must remain accessible to hand and harness; the binding limit is
  mechanical access, not millimetres of edge. This is a Phase 2 placement exercise.

---

## 3. PWM generation

### 3.1 Output stage

The current stage is an `SN74AHCT367` — a 5 V hex tri-state buffer driven directly from a
3.3 V MCU pin, feeding the 26-pin LPU connector with 0.1 µF of decoupling and no series
resistor, clamp or TVS. Tri-state enables come from the Slave, five lines for ten buffers,
active low.

The failure mode is in the interface, not the part:

1. **No series termination.** A 5 V output switching in a few nanoseconds into 50–100 pF of
   harness produces ringing above 5 V and below 0 V. The absolute maximum for the output
   stage is ±50 mA of clamp current; several hundred mA of transient is normal here.
   Repeated stress of this kind degrades the output stage progressively.
2. **Negative undershoot at the connector.** The same ringing drives the pin below ground
   with no external clamp, so the current returns through the substrate diode — a second
   degradation and latch-up path.
3. **No protection at the connector.** Every mating cycle and every ESD event at the far
   end reaches the buffer directly.
4. **Contention on tri-state release.** The enable is shared by two buffers and is released
   with the LPU side still holding charge.
5. **Lifecycle.** `SN74AHCT367` is not recommended for new designs at TI.

Required changes (`PWM-07`):

- series resistor of 33–47 Ω at every buffer output, placed at the buffer;
- TVS/ESD diode on the connector side (VCU_H11 already uses `WE-VE ULC`);
- one buffer per LPU, with the tri-state enable pulled to the disabled state in hardware;
- if the LPU accepts 3.3 V levels, remove the level translation entirely;
- confirm the part lifecycle before ordering.

`LCU_H11` already applies this pattern on its `Buffer_CK` sheet (`SN74LVC541A` with 33 Ω);
the LPU PWM path was not updated. Because the LPU performs its own dead-time insertion,
the buffer only has to deliver clean 5 V edges into a cable. Component selection is a
Phase 1 decision.

### 3.2 Timer allocation and synchronisation

`LCU_H11` uses eight timers, and LPU7 is driven by `TIM17_CH1` and `TIM16_CH1` — two
different timers. Its two signals can never be edge-aligned, and top-level synchronisation
cannot correct it.

Moving VBAT off the Slave releases three resources simultaneously:

- `PB0`/`PB1` become `TIM3_CH3`/`TIM3_CH4` instead of ADC inputs;
- two airgap channels move to `PC2`/`PC3` (which require the SYSCFG analog switch; ST-LIB
  already handles this);
- `PC8`/`PC9` become `TIM8_CH3`/`TIM8_CH4` instead of `TIM3_CH3`/`TIM3_CH4`.

The result is TIM1, TIM3, TIM4 and TIM8 with four channels each, plus TIM12 and TIM15 with
two: twenty channels in six timers, with both signals of every LPU on the same timer
(`pwm-tree.md`).

Dead-time is not generated on the LCU. The LPUs contain dedicated hardware for it, which is
also why the existing design uses two independent channels rather than a complementary
pair.

Synchronisation uses TIM1 as master, with its TRGO driving the others in slave/trigger
mode. Exact ITR availability must be checked against RM0468 Table 168 during Phase 1
(`PWM-04`). A fallback that always works: identical PSC/ARR on all six timers plus a single
simultaneous `CEN` write, giving tens of nanoseconds of skew against a 50 µs period.

---

## 4. Airgap sensing

The sensor is the SICK **OD2000-1301T15**: laser triangulation, 60–200 mm range, 4–20 mA
analogue output with 16-bit resolution, 7.5 kHz maximum measurement rate, plus IO-Link V1.1
and two digital outputs with an alarm function.

### 4.1 Fault and disconnection detection

The current loop is itself the detector. 4 mA is the live zero and 20 mA is full scale:

- **below 3.6 mA** (0.576 V at the ADC) — open loop, disconnected harness or dead sensor;
- **above 20.5 mA** — shorted loop;
- a frozen value while the PWM changes — a sensor that has stopped measuring.

This is a firmware threshold, not additional hardware. The sensor's digital alarm outputs
and IO-Link are not used; either would cost connector pins, ADC channels and eight
additional wires (`AGP-03`).

The low-side threshold does not cover the opposite failure. Pod data from 2026-11-09 shows
`airgap_4` jumping to 83.3 mm for one sample to 150 ms. 83.3 mm is the value the current
calibration returns at 3.3 V, so that reading is the ADC pinned at its rail. An open loop
reads 57.9 mm. Both thresholds are therefore required (`AGP-06`).

The same dataset characterises the coupling: 69–89 % of the glitch samples occur with
|I| > 5 A, the fault moved between channels across sessions, and it cleared when the
connector and cable were reseated. The failure is therefore in the grounding and shielding
of the sensor chain, and it is the primary item for Phase 1 (`AGP-07`).

### 4.2 Analog front end

The 4-20 mA loop is read across 160 Ω into a 5th-order Butterworth at 5 kHz and buffered by
an `MCP6022`. The topology is retained: the sigma-delta `A-ADC` alternative was never
brought up and is not a candidate.

This is the **LCU_H10** circuit, not the LCU_H11 one — LCU_H11 replaced it with a DFSDM
sigma-delta interface to an external modulator board, which is the path that never worked
(Phase 1 finding `F-01`). H12 therefore reinstates the H10 front end, and those parts are not
in the LCU_H11 BOM.

One change is required. In `LCU_H10` the `MCP6022` runs from `+5V_LCU` and its output
drives a 3.3 V ADC pin with nothing in between. The amplifier can therefore drive close to
5 V into a pin whose supply is 3.3 V. In normal operation the loop stays below 20 mA
(3.2 V) and nothing occurs, which is why the condition has not surfaced; under an
overcurrent or a transient coupled into the loop, the ADC input protection diode
forward-biases and injects current into `VDDA`, corrupting conversions on the other
channels.

A clamp would bound the voltage but would not contribute to diagnosis — the firmware
thresholds above already distinguish an open loop from a saturated input. The appropriate
change is to power the front end from **+3.3 V**. The `MCP6022` is rail-to-rail and rated
2.5–5.5 V, and the required output span of 0.64–3.2 V leaves 50–75 mV of margin below the
rail at light load into an ADC input. This removes the overdrive path with no additional
components. If a 5 V rail is required later, the fallback is a series resistor and a
`BAT54S` per channel.

### 4.3 Resolution

The 16-bit requirement is satisfied, but it does not imply 16-bit accuracy. The sensor's
own linearity is ±140 µm over a 140 mm range — approximately 0.1 % of full scale, or 10
bits. The STM32H7 16-bit ADC is specified at about 13.2 ENOB, and the 0.1 % sense resistor
contributes a further 10-bit limit. Expected performance is 10–12 effective bits.

Sixteen bits still provides oversampling headroom, which benefits a levitation loop. If
absolute accuracy becomes a requirement, the sense resistor must move to 0.01 % / 5 ppm and
the channels must be calibrated individually (`AGP-04`).

---

## 5. Master–Slave communication

The LCU_H11 design places setpoints, all measurements and the diagnostic record in a single
frame. That is why the frame reaches 899 B and 84 % of the 500 µs period, and why the least
time-critical content is the largest term in it.

H12 uses two independent links:

| Link | SPI master | Contents | Frame | Load |
|---|---|---|---|---|
| Control | Master | setpoints down, heartbeat up | 81 B | 8 % of period |
| Telemetry | **Slave** | measurements, diagnostics, configuration, SD-bound traffic | 210 B | 20 % of period |

Both run at 17.2 MHz (PCLK/8, as measured on LCU_H11). PCLK/4 = 34.4 MHz is available on
either link and halves the times above.

Pin allocation:

- Slave, SPI1 as master: `PB3` (SCK), `PG9` (MISO), `PD7` (MOSI), `PD6` (credit).
- Master, SPI4 as slave: `PE12` (SCK), `PE13` (MISO), `PE14` (MOSI), `PE11` (credit).

The Slave pins become available once LPU7 no longer requires `PIN16`/`PIN17`. The
displaced Master status and LED pins move to `PD14`/`PD15`/`PC6` and
`PB14`/`PB15`/`PE15`.

Three constraints apply (`ARCH-05` to `ARCH-08`):

1. **Flow control is mandatory.** An SPI slave cannot stall an SPI master. A 100 ms SD
   write on the Master would overrun the bus. `TEL_CREDIT` signals buffer availability and
   the Slave starts a transfer only when it is asserted.
2. **Failure handling must be defined.** Telemetry link failure: continue levitating and
   raise a degraded-telemetry warning. Control link failure: fault.
3. **The control loop must never block on the telemetry link.** DMA and a ring buffer on
   both sides; no spin-waits inside the Slave's control ISR.

At 2 kHz and 210 B per frame the log rate is about 420 kB/s. SD write latency spikes into
the hundreds of milliseconds, so approximately 42 kB of buffer is required to absorb them.
This is small against 564 kB of RAM but must be designed in (`ARCH-08`).

---

## 6. LPU status and reset

### 6.1 Status line termination

The LPU drives both status lines 3.3 V push-pull:

| Signal | Healthy | Fault / not-ready | Polarity |
|---|---|---|---|
| `READY_n` | HIGH | LOW | Active-high; HIGH = all four drivers ready |
| `FAULT_n` | HIGH | LOW | Active-low; LOW = at least one driver faulted |

The full state space, with both lines pulled down:

| `READY` | `FAULT` | Interpretation | Action |
|---|---|---|---|
| HIGH | HIGH | Healthy and ready | — |
| LOW | HIGH | Healthy, not ready (startup, disabled) | — |
| LOW | LOW | Faulted **or absent/unpowered** | Exclude that LPU, then discriminate |
| HIGH | LOW | Not physically valid | Treat as fault; stuck or shorted line |

The fault/not-ready state is LOW on both lines, so **both lines receive a pull-down**
(`LPU-03`). A pull-up would cause an unplugged connector to read as a healthy, ready
magnet.

The resulting invariant is that HIGH+HIGH — the only healthy combination — requires an
active driver on both lines, that is, a connected and powered LPU. An absent connector
cannot produce it. The same pull resistors also remove the floating-input condition
described below.

Faulted and absent cannot be distinguished, because a powered LPU in fault also drives both
lines LOW. Both require the same action, and the connector has no spare contact to
discriminate further.

**Floating inputs.** In `LCU_H10` and `LCU_H11` the twenty status lines reach MCU pins
configured `Pull::None`, and where the signals feed an `SN74ALVC08` the gate inputs are
equally unterminated. ALVC has no internal resistors, so an un-driven node floats: both
input transistors conduct partially, the gate draws shoot-through current, the output can
oscillate, and the MCU may observe random edges. With no termination, a floating node could
also have drifted into HIGH+HIGH and reported a healthy magnet.

Implementation (`LPU-04`):

- baseline: STM32 internal pull-down (~40 kΩ) on all twenty lines, no additional components;
- external pull-down only if the harness proves too noisy for 40 kΩ — a 10 kΩ pull costs
  the LPU 0.33 mA while driving HIGH;
- series resistor and TVS at the connector in all cases.

This invariant is enforced automatically (`LPU-STATUS-*` in `build.py`): a pull direction or
polarity change that would let an un-driven line read healthy fails the build.

**No logic gates in the status path.** VCU_H11 combines sensor lines through `SN74ALVC08` /
`SN74ALVC32`. Applying the same approach to `READY`/`FAULT` would discard the only
information those twenty pins carry — which magnet is faulted — and would require
termination at every gate input. The lines remain point-to-point into the MCUs (`LPU-06`).

### 6.2 Reset granularity

Each LPU has an independent reset line (10 GPIO), not a shared one. A shared reset means a
single LPU failure de-levitates the pod; ten separate buffer channels allow one LPU to be
isolated and reset while the other nine continue levitating (`RST-02`).

RESET is one of the three signals that leave the LCU per LPU — `PWM_1`, `PWM_2` and
`RESET` — all at 5 V, all driven through the same buffer bank. That is why the bank carries
30 channels and not 20.

RESET is **active-low**: driving it HIGH releases it and lets the LPU work, LOW asserts it. The
release state therefore has to be actively driven, which is what forces the push-pull buffer;
the asserted state is held by a pull-down when the bank is released (`RST-05`).

### 6.3 brake_fault

Hardware assertion is required; asserting the fault only in firmware defeats the purpose.

Because RESET is a push-pull 5 V buffer output, the reset nets cannot be wired-ANDed with a
second driver — the buffer would fight it. The override therefore acts on the buffer's
3-state enable:

- the enable is active-low and pulled to disabled, so a dead MCU already releases the bank;
- the conditioned `brake_fault` signal forces the same state in hardware, through one gate
  shared by all five packages;
- each RESET line carries a pull resistor to its asserted level, so a released output means
  "reset asserted" rather than a floating pin.

This keeps ten independent resets in normal operation — every LPU has its own buffer
channel — while the brake override takes them all down at once (`RST-03`).

Two ordering rules follow from the enable being the override point. Firmware must drive the
RESET buffer inputs LOW *before* it asserts the enable, because an unconfigured input floats at
TTL threshold and an early enable would present indeterminate levels to the LPUs. And every
RESET line carries a pull-down, so a released buffer, an unpowered board or an unseated
connector all read as "reset asserted" (`RST-05`).

Two consequences to design for. A released bank also releases the PWM lines, which is the
intended behaviour (levitation off) but means the LPU PWM inputs need their own pull-downs
or they float at the far end. And the override is per package in hardware, not per LPU, so it
cannot be used to isolate a single magnet.

The source is the VCU's 2-pin brake connector, daisy-chained through the LCU, so the board
carries two of them.

The passthrough has two population options on the same footprint (`SAF-05`):

- **straight passthrough (default)** — an unplugged downstream segment carries nothing and
  the pod continues to levitate;
- **normally closed** — a missing board also asserts the fault. Safer for levitation, worse
  for availability.

Either way, asserting the fault disables levitation, which at speed drops the pod onto its
skis. The signal must be debounced, latched and reported, and cleared only by an explicit
command (`SAF-02`, `SAF-03`).

---

## 7. Temperature sensing

Two independent paths exist:

**LPU temperature (10 channels).** Arrives over the 26-pin LPU connector and is conditioned
on the LCU (series 220 Ω + 10 nF), read by the Master's ADC3. This is the same topology as
`LCU_H11`'s `Temp_conditioning`, extended from four channels to ten. It requires LPU_H11.

**Corner NTC (4 connectors).** These run directly from the LCU to the NTCs at the pod
corners and retain temperature measurement on a pod using LPU_H10, which has no sensing.
Unlike the LPU path — where the LPU performs the work — the LCU owns the entire chain
(`TMP-02`):

- **excitation**: pull-up to the 3V3 ADC reference, making the reading ratiometric and
  independent of rail drift, matched to the NTC's nominal value so the divider spans
  approximately half the reference;
- **filter**: RC at the ADC;
- **protection**: series resistor and TVS at the connector, since the cable runs alongside
  the LPU power leads.

`LCU_H11`'s `Temp_conditioning` provides only the 220 Ω and 10 nF, and assumes an external
pull-up. With a directly connected NTC the LCU must supply the top of the divider
(`TMP-03`).

The four corner channels use the Slave's ADC3 at 12 bits. The NTC part is the same as the
LPU_H11 device; its beta constants define the pull-up value and the calibration
(`TMP-04`).

---

## 8. Other interfaces

### 8.1 CAN

Both MCUs are CAN nodes on the same bus, with one TJA1051T/3 each: Master on `PD0`/`PD1`,
Slave on `PB8`/`PB9`. Multiple nodes on one bus is valid CAN and provides a redundant path;
only one should be the talker for any given message set. FDCAN1 at 1 Mbit/s is part of the
H12 avionics baseline (`AUX-04`).

Note that the LPU H10 inventory includes units without `vbat`/`ready`/`fault` outputs.
Before committing ten of each, confirm that all LPUs will drive those lines.

### 8.2 microSD

SDMMC1 4-bit on the Master, same socket as VCU_H11. The path is proven, so this is a port
rather than a bring-up item (`SD-04`).

The only substantive change is the pin allocation: SDMMC1 occupies `PC10`/`PC11`/`PC12`,
which is where the LCU_H11 Master has SPI3. The H12 Master moves SPI3 to
`PB3`/`PB4`/`PB5` (`SD-02`). The Slave retains its SPI3 pins — the two ends are separate
nets and need not use the same instance.

The upper storage layer should be documented, because the telemetry buffer sizing in §5
depends on how writes behave rather than on whether the card functions.

### 8.3 IMU

An optional, unpopulated SPI device providing a third position measurement to fuse against
the airgaps. It is kept off the pin plan and off the outline so population can be decided
once a fusion design exists (`AUX-03`).

---

## 9. Items pending confirmation

**To be confirmed during schematic capture (6):**

| ID | Item |
|---|---|
| `PWM-04` | ITR availability per timer for TRGO synchronisation (RM0468 Table 168) |
| `ARCH-08` | Telemetry buffer size, once the logged signal set is frozen |
| `ARCH-09` | Single 36 MHz ADC clock for both MCUs, given the shared ST-LIB configuration |
| `AUX-02` | Per-LPU status indication: constant-current LED driver versus GPIO |
| `AUX-03` | IMU population decision |
| `MEC-01` | Connector placement and stacking (Phase 2) |

**Pending a value (1):**

| ID | Item |
|---|---|
| `TMP-04` | NTC part number and beta constants (same device as LPU_H11) |

All 15 architectural questions are closed. Each is retained in `arch/lcu_h12.json` with its
answer, so the reasoning remains available without this document.
