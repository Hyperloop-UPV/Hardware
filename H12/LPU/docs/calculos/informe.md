# Magnet Driver Abejorro · Informe de cálculos de diseño

| Dato | Valor |
|---|---|
| Fecha | 19/09/2026 18:17 (hora de Madrid) |
| Versión de las entradas | commit `65be21b` |
| Motor de cálculo | 1.0 |
| Documento base | Requisitos y arquitectura, borrador v0.2 (`docs/requisitos`) |
| MOSFET seleccionado | IMT65R010M2H |
| Parámetros | 163 en total: 37 TBD, 82 a confirmar |

> **Aviso.** Cálculos de primer orden para orientar el diseño: no sustituyen a las calculadoras especializadas, a la simulación ni a las normas originales. Los parámetros en estado **TBD** tienen valores provisionales, y todo resultado que dependa de ellos es provisional.

## Índice

- [Resumen](#resumen)
- [1. Potencia y bus DC](#1-potencia-y-bus-dc)
- [2. MOSFET: comparador de candidatos](#2-mosfet-comparador-de-candidatos)
- [3. Térmico](#3-térmico)
- [4. Pistas y vías de potencia](#4-pistas-y-vías-de-potencia)
- [5. Aislamiento](#5-aislamiento)
- [6. Integridad de señal](#6-integridad-de-señal)
- [7. Sensado y adquisición](#7-sensado-y-adquisición)
- [8. Gate driving](#8-gate-driving)
- [9. Alimentación auxiliar (BT)](#9-alimentación-auxiliar-bt)
- [Anexo A. Todas las comprobaciones](#anexo-a-todas-las-comprobaciones)
- [Anexo B. Parámetros usados](#anexo-b-parámetros-usados)
- [Anexo C. Parámetros pendientes](#anexo-c-parámetros-pendientes)

## Resumen

El cálculo incluye 75 comprobaciones. «REVISAR» indica un criterio blando o un dato que requiere un análisis más detallado.

| Resultado | Número |
|---|---|
| CUMPLE | 61 |
| NO CUMPLE | 8 |
| REVISAR | 6 |

Comprobaciones que no cumplen o que hay que revisar:

| ID | Comprobación | Valor | Límite | Unidad | Resultado | Requisito | Depende de |
|---|---|---|---|---|---|---|---|
| POT-04 | Tensión de fallo (extrapolada) frente a la tensión continua admisible | 734 | 600 | V | **NO CUMPLE** | DCB-08 · DCB-02 | HW-03, EM-D-03 |
| POT-05 | Tensión de fallo frente a la tensión nominal del DC-link | 734 | 630 | V | **NO CUMPLE** | DCB-08 | HW-02, HW-03 |
| POT-06 | Tensión de fallo frente a la VDS del MOSFET seleccionado | 734 | 650 | V | **NO CUMPLE** | PWR-02 | HW-02 |
| POT-07 | Capacidad instalada frente a la necesaria para no superar V_cont desde Vbus_max | 105 | 199 | µF | **NO CUMPLE** | DCB-08 | HW-03, EM-D-03 |
| POT-10 | Corriente media de bus a Ipk frente al fusible con factor de utilización | 13,92 | 11,25 | A | **REVISAR** | DCB-06 | EM-C-01, ME-I-03 |
| POT-11 | Corriente de entrada de la primera placa frente al fusible (si está en el camino encadenado) | 13,92 | 11,25 | A | **REVISAR** | DCB-05 · DCB-06 | ME-I-03 |
| POT-12 | Tensión nominal del fusible frente a V_cont | 500 | 600 | V | **NO CUMPLE** | DCB-02 · DCB-06 | HW-02 |
| POT-13 | Tensión nominal del fusible frente a la tensión de fallo | 500 | 734 | V | **NO CUMPLE** | DCB-08 | HW-02, HW-03 |
| GDR-01 | Vgs_on dentro del rango recomendado del MOSFET | 18 | 15 | V | **REVISAR** | GD-01 | HW-02 |
| GDR-14 | Corriente de disparo a 25 °C (peor caso) frente a la ID pulsada | 797 | 300 | A | **REVISAR** | GD-01 · SAF-04 | HW-01, HW-02 |
| TER-04 | Tj a Ipk (régimen permanente) | 676,3 | 150,0 | °C | **NO CUMPLE** | PWR-05 | EM-C-01, ME-C-01, ME-C-02, HW-02 |
| TER-06 | Coherencia: Tj a Ipk ≤ Tj_assumed usada para la RDS(on) | 676,3 | 125,0 | °C | **REVISAR** | — |  |
| AIS-F-MGJ2 | Línea de fuga del encapsulado: MGJ2D052005BSC (fuente aislada de puerta) | 2,0 | 4,0 | mm | **REVISAR** | ISO-01 · ISO-02 | HW-04, HW-05 |
| SEN-08 | Fondo de escala de Vbus frente a la tensión de fallo | 700 | 734 | V | **NO CUMPLE** | SNS-02 · DCB-08 | HW-03 |

## 1. Potencia y bus DC

Modelo de primer orden: L constante en cada punto de trabajo y conmutación ideal.

### 1.1 Rizado de corriente en la bobina

Unipolar: la salida conmuta entre 0 y ±Vbus a 2·fsw, ΔI = Vbus·m·(1−m)/(2·L·fsw), máximo en m = 0,5: Vbus/(8·L·fsw). Bipolar: ΔI = Vbus·(1−m²)/(2·L·fsw), máximo en m = 0: Vbus/(2·L·fsw). Se desprecia R frente a L. Modulación seleccionada: **Unipolar**; fsw = 20,0 kHz; rizado admisible = 1,50 A.

| Electroimán / punto | L (mH) | ΔI unip., Vbus_min (A) | ΔI unip., Vbus_max (A) | ΔI bip., Vbus_max (A) | ΔI con la modulación elegida (A) | Resultado |
|---|---|---|---|---|---|---|
| EMS, L mínima | 1,92 | 1,04 | 1,30 | 5,21 | 1,30 | CUMPLE |
| EMS, L máxima | 117,00 | 0,02 | 0,02 | 0,09 | 0,02 | CUMPLE |
| HEMS, L mínima | 6,20 | 0,32 | 0,40 | 1,61 | 0,40 | CUMPLE |
| HEMS, L máxima | 11,20 | 0,18 | 0,22 | 0,89 | 0,22 | CUMPLE |

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Rizado en el peor caso (L mínima, Vbus_max) (POT-01) | 1,30 | A | 1,50 | CUMPLE | `max(ΔI) ≤ dI_pp_max` | Doc. v0.2 §6.1.3: 1,30 A (EMS) y 0,40 A (HEMS) a 400 V, unipolar |
| fsw mínima para cumplir el rizado con L mínima | 17,4 | kHz |  |  | `Vbus_max/(k·L_min·dI_pp_max)` | k = 8 (unipolar) o 2 (bipolar) |

### 1.2 Dinámica de la corriente

di/dt = (Vbus − R·I)/L. Tiempo de 0 a Ipk con L constante: τ·ln(Vbus/(Vbus − R·Ipk)), τ = L/R. En rueda libre (SAF-05) la corriente cae al 1 % en 4,6·τ. Con L no lineal, los valores son orientativos.

| Electroimán / punto | L (mH) | di/dt, Vbus_min, I = 0 (A/ms) | di/dt, Vbus_max, I = 0 (A/ms) | di/dt, Vbus_min, I = Ipk (A/ms) | t de 0 a Ipk, Vbus_min (ms) | τ = L/R (ms) |
|---|---|---|---|---|---|---|
| EMS, L mínima | 1,92 | 166,7 | 208,3 | 129,2 | 0,41 | 1,6 |
| EMS, L máxima | 117,00 | 2,7 | 3,4 | 2,1 | 24,85 | 97,5 |
| HEMS, L mínima | 6,20 | 51,6 | 64,5 | 40,0 | 1,32 | 5,2 |
| HEMS, L máxima | 11,20 | 28,6 | 35,7 | 22,1 | 2,38 | 9,3 |

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Tensión en la bobina a Ipk | 72,0 | V |  |  | `Rcoil·Ipk` |  |
| Índice de modulación a Ipk con Vbus_min | 0,225 | – |  |  | `V_coil_pk/Vbus_min` |  |
| Corriente máxima alcanzable con Vbus_min (sin pérdidas) (POT-02) | 266,7 | A | 60,0 | CUMPLE | `Vbus_min/Rcoil ≥ Ipk` | Margen de tensión para el lazo de corriente |

### 1.3 Corrientes de bus y de DC-link

Corriente media de bus = P_bobina/(η·Vbus). La entrada del puente son pulsos de amplitud I y ciclo m: I_rms,puente = I·√m; I_rms,C = I·√(m·(1−m)), con máximo I/2 en m = 0,5. Rizado del DC-link suponiendo que el bus solo aporta la media: ΔV = I·m·(1−m)/(2·fsw·C) + I·ESR. Se ignoran la inductancia del bus y la interacción entre placas.

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Potencia en la bobina a Ipk | 4320 | W |  |  | `Rcoil·Ipk²` |  |
| Corriente media de bus a Ipk, Vbus_min | 13,92 | A |  |  | `P_coil_pk/(eta_pwr·Vbus_min)` | Doc. v0.2 §6.2: 13,5 A sin pérdidas |
| Corriente media de bus a Ipk, Vbus_max | 11,13 | A |  |  | `P_coil_pk/(eta_pwr·Vbus_max)` | Doc. v0.2 §6.2: 10,8 A sin pérdidas |
| Corriente media de bus en continuo, Vbus_min | 0,097 | A |  |  | `Rcoil·Irms_cont²/(eta_pwr·Vbus_min)` |  |
| Placas cuya corriente atraviesa la entrada de la primera | 1 | – |  |  | `N_MD si Bus_topo = Encadenado; si no, 1` |  |
| Corriente de entrada de la primera placa, todas a Ipk | 13,9 | A |  |  | `N_chain·I_bus_pk` | Peor caso simultáneo |
| Corriente de entrada de la primera placa, en continuo | 0,10 | A |  |  | `N_chain·I_bus_cont` |  |
| Corriente eficaz de entrada al puente a Ipk | 28,5 | A |  |  | `Ipk·√m_pk` | Para las pistas DC-link ↔ puente |
| Corriente eficaz en el DC-link en el punto Ipk, Vbus_min | 25,1 | A |  |  | `Ipk·√(m_pk·(1−m_pk))` |  |
| Corriente eficaz en el DC-link, peor caso (m = 0,5) | 30,0 | A |  |  | `Ipk/2` | Por ejemplo, durante la subida de corriente; para elegir condensadores |
| Capacidad del DC-link | 105,0 | µF |  |  | `Cdc` | Entrada (AC) |
| Rizado de tensión en el DC-link en el punto Ipk | 2,61 | V |  |  | `Ipk·m(1−m)/(2·fsw·Cdc) + Ipk·ESR_dc` |  |
| Rizado de tensión en el DC-link, peor caso (m = 0,5) (POT-03) | 3,69 | V | 6,40 | CUMPLE | `Ipk/(8·fsw·Cdc) + Ipk·ESR_dc` | Límite: dVdc_pct·Vbus_min |
| Capacidad mínima para el rizado (sin ESR) | 58,6 | µF |  |  | `Ipk/(8·fsw·dVdc_pct·Vbus_min)` |  |
| Frecuencia fundamental de la corriente en el DC-link | 40,0 | kHz |  |  | `2·fsw (unipolar) o fsw (bipolar)` |  |

### 1.4 Caso de fallo: sin rueda libre, la energía vuelve al DC-link (DCB-08, SAF-07)

Balance de energía: ½·C·(Vf² − V0²) = E, luego Vf = √(V0² + 2E/C). Se desprecian las pérdidas durante la descarga (conservador). Los mapas llegan a 55 A; la extrapolación a Ipk es cuadrática y solo orientativa, porque el HEMS no es lineal.

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Energía peor caso según los mapas H11 (55 A) | 16,7 | J |  |  | `max(E_EMS, E_HEMS)` |  |
| Energía extrapolada a Ipk | 19,9 | J |  |  | `E_map·(Ipk/I_map)²` | Orientativa (EM-D-03) |
| Cota pesimista con L constante | 48,1 | J |  |  | `½·L_EMS_0·Ipk²` | Doc. v0.2 §6.3: 48 J |
| Capacidad que absorbe la energía | 105,0 | µF |  |  | `Cdc·N_dc_abs` |  |
| Tensión final desde Vbus_min (energía de los mapas) | 648 | V |  |  | `√(Vbus_min² + 2·E_map/C_abs)` | Doc. v0.2: ≈ 650 V |
| Tensión final desde Vbus_max (energía de los mapas) | 691 | V |  |  | `√(Vbus_max² + 2·E_map/C_abs)` | Doc. v0.2: ≈ 690 V |
| Tensión final desde Vbus_max (energía extrapolada a Ipk) | 734 | V |  |  | `√(Vbus_max² + 2·E_ext/C_abs)` |  |
| Tensión final desde Vbus_max (cota pesimista) | 1037 | V |  |  | `√(Vbus_max² + 2·E_const/C_abs)` | Doc. v0.2: ≈ 1040 V |
| Tensión de fallo (extrapolada) frente a la tensión continua admisible (POT-04) | 734 | V | 600 | **NO CUMPLE** | `V_fault_max ≤ V_cont` | Sin clamp, chopper ni DC-link mayor |
| Tensión de fallo frente a la tensión nominal del DC-link (POT-05) | 734 | V | 630 | **NO CUMPLE** | `V_fault_max ≤ V_film` |  |
| Tensión de fallo frente a la VDS del MOSFET seleccionado (POT-06) | 734 | V | 650 | **NO CUMPLE** | `V_fault_max ≤ VDS` |  |
| Capacidad instalada frente a la necesaria para no superar V_cont desde Vbus_max (POT-07) | 105 | µF | 199 | **NO CUMPLE** | `C_abs ≥ 2·E_ext/(V_cont² − Vbus_max²)` | Doc. v0.2: ≥ 167 µF con 16,7 J |
| Capacidad necesaria con la energía de los mapas (sin extrapolar) | 167 | µF |  |  | `2·E_map/(V_cont² − Vbus_max²)` |  |

### 1.5 Opción clamp o chopper (HW-03)

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Resistencia máxima del chopper | 8,33 | Ω |  |  | `V_chop_on/Ipk` | Para que conduzca Ipk sin superar V_chop_on |
| Potencia de pico en la resistencia | 30,0 | kW |  |  | `V_chop_on·Ipk` |  |
| Energía por evento en la resistencia (cota) | 19,9 | J |  |  | `E_ext` |  |
| Tensión de actuación del chopper por encima de Vbus_max con margen (POT-08) | 500 | V | 440 | CUMPLE | `V_chop_on ≥ k_chop_mrg·Vbus_max` | Para no actuar en servicio |
| Tensión de actuación del chopper por debajo de V_cont (POT-09) | 500 | V | 600 | CUMPLE | `V_chop_on ≤ V_cont` |  |

### 1.6 Fusible en placa (DCB-06)

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Corriente media de bus a Ipk frente al fusible con factor de utilización (POT-10) | 13,92 | A | 11,25 | **REVISAR** | `I_bus_pk ≤ k_fuse·I_fuse` | El pico dura t_pk: revisar con la curva tiempo-corriente del fusible |
| Corriente de entrada de la primera placa frente al fusible (si está en el camino encadenado) (POT-11) | 13,92 | A | 11,25 | **REVISAR** | `I_in_first ≤ k_fuse·I_fuse` |  |
| Tensión nominal del fusible frente a V_cont (POT-12) | 500 | V | 600 | **NO CUMPLE** | `V_fuse ≥ V_cont` | El 0ADKC9150-BE es de 500 VDC |
| Tensión nominal del fusible frente a la tensión de fallo (POT-13) | 500 | V | 734 | **NO CUMPLE** | `V_fuse ≥ V_fault_max` |  |


## 2. MOSFET: comparador de candidatos

Pérdidas de primer orden: Eon/Eoff escaladas linealmente con V e I desde las condiciones de ensayo, y RDS(on) interpolada linealmente con Tj entre 25 °C y la temperatura alta de la hoja de datos, escalada con la relación máx./típ. El caso A supone Ipk en régimen permanente (conservador frente a t_pk). El MOSFET más cargado conduce una fracción D_worst = 1,00 del periodo.

Comparación de los candidatos completos de `componentes.md`. Las temperaturas usan la cadena térmica y el agua del apartado 3.

| Parámetro | Unidad | IMT65R010M2H (sel.) | SCT012H90G3AG |
|---|---|---|---|
| **Datos principales** |  |  |  |
| Encapsulado | – | PG‑HSOF‑8 | H²PAK-7 (SMD) |
| VDS máxima | V | 650 | 900 |
| RDS(on) típica a 25 °C | mΩ | 10 | 12 |
| Rth unión-cápsula | K/W | 0,35 | 0,24 |
| Carga total de puerta | nC | 95 | 138 |
| Energía de encendido | µJ | 500 | 708 |
| Energía de apagado | µJ | 600 | 889 |
| RDS(on) típica a Tj_assumed | mΩ | 13,33 | 16,33 |
| RDS(on) máxima a Tj_assumed | mΩ | 16,00 | 21,51 |
| Figura de mérito RDS(on)·Qg (25 °C) | mΩ·nC | 950 | 1656 |
| **Caso A: Ipk** |  |  |  |
| Energía de conmutación escalada | µJ | 1650 | 1065 |
| Conducción del MOSFET más cargado | W | 57,60 | 77,42 |
| Conmutación (toda la de la rama en un MOSFET) | W | 33,00 | 21,29 |
| Diodo en los tiempos muertos | W | 0,288 | 0,672 |
| Pérdidas totales del MOSFET más cargado | W | 90,9 | 99,4 |
| Temperatura de unión | °C | 676,3 | 723,7 |
| Tj ≤ Tj_lim | – | **NO CUMPLE** | **NO CUMPLE** |
| Tj ≤ Tj_assumed (coherencia de la RDS(on)) | – | **REVISAR** | **REVISAR** |
| Pérdidas del puente completo (4 MOSFET) | W | 181,8 | 198,8 |
| **Caso B: Irms_cont** |  |  |  |
| Energía de conmutación escalada | µJ | 138 | 89 |
| Conducción del MOSFET más cargado | W | 0,40 | 0,54 |
| Conmutación (toda la de la rama en un MOSFET) | W | 2,75 | 1,77 |
| Diodo en los tiempos muertos | W | 0,024 | 0,056 |
| Pérdidas totales del MOSFET más cargado | W | 3,2 | 2,4 |
| Temperatura de unión | °C | 73,2 | 67,4 |
| Tj ≤ Tj_lim | – | CUMPLE | CUMPLE |
| Pérdidas del puente completo (4 MOSFET) | W | 6,3 | 4,7 |
| **Márgenes** |  |  |  |
| VDS / V_cont | – | 1,08 | 1,50 |
| VDS ≥ tensión del caso de fallo | – | **NO CUMPLE** | CUMPLE |
| Vgs_on ≤ VGS recomendada | – | **REVISAR** | CUMPLE |
| Vgs_on ≤ VGS máxima absoluta | – | CUMPLE | CUMPLE |
| Vgs_off ≥ VGS recomendada en OFF | – | CUMPLE | CUMPLE |
| ID continua ≥ Ipk | – | CUMPLE | CUMPLE |


## 3. Térmico

Modelo unidimensional en régimen permanente; no sustituye a una simulación térmica.

### 3.1 Resistencia térmica cápsula → agua (por MOSFET)

Vías en paralelo con el FR-4: R_vía = t_pcb/(k_Cu·A_barril), A_barril = π/4·(d² − (d − 2·t_met)²). Vías sin rellenar (conservador) y sin contar los planos internos. El pad de drenador está a potencial de HV: el material de interfaz debe aislar (ISO-04).

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Área del pad de drenador | 70,0 | mm² |  |  | `A_pad` | Entrada (AC) |
| Número de vías térmicas | 36 | – |  |  | `N_via` | Entrada (AC) |
| Sección de cobre de una vía | 0,0216 | mm² |  |  | `π/4·(d_via² − (d_via − 2·t_plat)²)` |  |
| Resistencia de una vía | 192,4 | K/W |  |  | `t_pcb/(k_Cu·A_barrel)` |  |
| Resistencia del conjunto de vías | 5,345 | K/W |  |  | `R_via1/N_via` |  |
| Área de FR-4 restante bajo el pad (TER-01) | 67,5 | mm² | 0,0 | CUMPLE | `A_pad − N_via·π·d_via²/4 ≥ 0` | Si es negativa, las vías no caben en el pad |
| Resistencia del FR-4 bajo el pad | 79,1 | K/W |  |  | `t_pcb/(k_FR4·A_FR4)` |  |
| Resistencia de la PCB (vías ∥ FR-4) | 5,006 | K/W |  |  | `1/(1/R_vias + 1/R_fr4)` |  |
| Resistencia de la soldadura | 0,029 | K/W |  |  | `t_solder/(k_solder·A_pad)` |  |
| Resistencia del material de interfaz | 1,190 | K/W |  |  | `t_TIM/(k_TIM·A_pad·k_spread)` |  |
| Resistencia cara inferior → agua | 0,300 | K/W |  |  | `Rth_wb` | Entrada (TBD) |
| Rth cápsula → agua | 6,525 | K/W |  |  | `R_solder + R_pcb + R_TIM + Rth_wb` |  |
| Rigidez dieléctrica del material de interfaz (TER-02) | 4000 | V | 600 | CUMPLE | `V_TIM_bd ≥ V_cont` | Margen exigido por definir con el tipo de aislamiento (HW-04) |

### 3.2 Shunt de corriente

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Potencia en el shunt a Ipk | 1,80 | W |  |  | `Ipk²·R_shunt` |  |
| Energía en el shunt durante el pico | 3,6 | J |  |  | `P_sh_pk·t_pk` | Comparar con la capacidad de pulso del shunt |
| Potencia en el shunt en continuo | 0,013 | W |  |  | `Irms_cont²·R_shunt` |  |
| Potencia de pico en el shunt frente a su potencia nominal (TER-03) | 1,80 | W | 3,00 | CUMPLE | `P_sh_pk ≤ P_sh_rat` | Si el pico es corto, usar la curva de sobrecarga del shunt |

### 3.3 Balance de pérdidas de la placa y refrigerante

| Magnitud | Valor | Unidad | Expresión | Nota |
|---|---|---|---|---|
| Pérdidas del puente a Ipk (MOSFET seleccionado) | 182 | W | `apartado 2` |  |
| Pérdidas del puente en continuo (MOSFET seleccionado) | 6,3 | W | `apartado 2` |  |
| Pérdidas por ESR en el DC-link (peor caso) | 1,80 | W | `I_cap_rms_wc²·ESR_dc` |  |
| Consumo de la alimentación auxiliar (acaba en calor) | 3,3 | W | `P_BT_total` |  |
| Pérdidas totales de la placa a Ipk | 189 | W | `P_br_pk + P_sh_pk + P_esr + P_BT_total` |  |
| Pérdidas totales de la placa en continuo | 9,7 | W | `P_br_c + P_sh_c + P_esr·(Irms_cont/Ipk)² + P_BT_total` |  |
| Gasto másico de agua | 0,0332 | kg/s | `Q_cool·997 kg/m³` |  |
| Incremento de temperatura del agua por placa a Ipk | 1,36 | K | `P_board_pk/(m_dot·4180)` | Toda la pérdida al agua (conservador) |
| Temperatura del agua en la última placa en serie | 51,4 | °C | `T_cool + N_cool_ser·dT_cool` |  |
| Energía de todas las placas al acumulador durante el pico | 3,8 | kJ | `N_MD·P_board_pk·t_pk` | Dato para ME-C (sin el calor de las bobinas) |

### 3.4 Temperatura de unión del MOSFET seleccionado

MOSFET seleccionado: **IMT65R010M2H**.

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Tj a Ipk (régimen permanente) (TER-04) | 676,3 | °C | 150,0 | **NO CUMPLE** | `Tj_pk ≤ Tj_lim` | Conservador si t_pk es corto frente a las constantes térmicas |
| Tj en continuo (Irms_cont) (TER-05) | 73,2 | °C | 150,0 | CUMPLE | `Tj_c ≤ Tj_lim` |  |
| Coherencia: Tj a Ipk ≤ Tj_assumed usada para la RDS(on) (TER-06) | 676,3 | °C | 125,0 | **REVISAR** | `Tj_pk ≤ Tj_assumed` | Si falla, suba Tj_assumed y recalcule |


## 4. Pistas y vías de potencia

IPC-2221: I = k·ΔT^0,44·A^0,725 (A en mil²; k = 0,048 externa y 0,024 interna). La fórmula se obtuvo para corrientes y anchos moderados (≈ hasta 35 A y 400 mil): con decenas de amperios es una extrapolación. Úsela como primera estimación y confirme con IPC-2152 o simulación. Redes de `diseno.md`, tabla 1.

Incremento de temperatura admisible: dT_trace = 30 °C. La resistencia se evalúa a T_amb + ΔT estimado.

| Red | I (A) | Capa × nº | Cu (oz) | Ancho necesario por capa (mm) | Ancho previsto (mm) | ΔT estimado (°C) | R (mΩ) | P (W) | Caída (mV) | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| Entrada HV (1.ª placa), Ipk | 13,92 | Ext × 2 | 2,0 | 1,12 | 35,00 | 0,1 | 0,236 | 0,05 | 3,3 | TBD |
| Entrada HV (1.ª placa), continuo | 0,10 | Ext × 2 | 2,0 | 0,00 | 10,00 | 0,0 | 0,826 | 0,00 | 0,1 | TBD |
| DC-link ↔ puente, eficaz a Ipk | 28,46 | Ext × 2 | 2,0 | 3,00 | 15,00 | 2,1 | 0,185 | 0,15 | 5,3 | TBD |
| Puente → bobina, Ipk | 60,00 | Ext × 2 | 2,0 | 8,40 | 15,00 | 11,5 | 0,764 | 2,75 | 45,8 | TBD |
| Puente → bobina, continuo | 5,00 | Ext × 2 | 2,0 | 0,27 | 5,00 | 0,2 | 2,205 | 0,06 | 11,0 | TBD |

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Ancho de pista: Entrada HV (1.ª placa), Ipk (PIS-entrada_pk) | 35,0 | mm | 1,1 | CUMPLE | `ancho previsto ≥ ancho necesario` |  |
| Ancho de pista: Entrada HV (1.ª placa), continuo (PIS-entrada_cont) | 10,0 | mm | 0,0 | CUMPLE | `ancho previsto ≥ ancho necesario` |  |
| Ancho de pista: DC-link ↔ puente, eficaz a Ipk (PIS-puente_rms) | 15,0 | mm | 3,0 | CUMPLE | `ancho previsto ≥ ancho necesario` |  |
| Ancho de pista: Puente → bobina, Ipk (PIS-bobina_pk) | 15,0 | mm | 8,4 | CUMPLE | `ancho previsto ≥ ancho necesario` |  |
| Ancho de pista: Puente → bobina, continuo (PIS-bobina_cont) | 5,0 | mm | 0,3 | CUMPLE | `ancho previsto ≥ ancho necesario` |  |

### 4.1 Vías para corriente

Misma fórmula (k externa) con la sección de cobre del barril; diámetro y metalizado de las vías térmicas.

| Magnitud | Valor | Unidad | Expresión | Nota |
|---|---|---|---|---|
| Corriente admisible por vía | 2,73 | A | `0,048·dT_trace^0,44·A_barril^0,725` |  |
| Vías necesarias para Ipk (cambio de capa de la salida) | 22 | – | `⌈Ipk/I_via⌉` |  |
| Vías necesarias para la entrada de la primera placa | 6 | – | `⌈I_in_first/I_via⌉` |  |


## 5. Aislamiento

Reglas del proyecto (ISO-02 a ISO-04) frente a IPC-2221B (tabla 6-1) e IEC 60664-1 (líneas de fuga en circuito impreso). Las tablas de las normas proceden de fuentes secundarias (`calculos/normas/README.md`) y deben contrastarse con el texto oficial.

IPC-2221B, separación mínima entre conductores (mm). B1: internas · B2/B3: externas sin recubrir (≤/> 3050 m) · B4: recubrimiento permanente · A5: conformal coating · A6/A7: terminales sin/con coating.

| Tensión | B1 | B2 | B3 | B4 | A5 | A6 | A7 |
|---|---|---|---|---|---|---|---|
| V_cont = 600 V | 0,50 | 3,00 | 15,00 | 1,10 | 1,10 | 1,80 | 1,10 |
| V_fault_max = 734 V | 0,83 | 3,67 | 18,35 | 1,51 | 1,51 | 2,21 | 1,51 |

IEC 60664-1, aislamiento funcional/básico en circuito impreso. Tipo de aislamiento HV–BT: **Básico** (factor 1). PD1 aplica bajo un recubrimiento conforme a IEC 60664-3.

| Tensión | Grado de contaminación | Interpolada (mm) | Fila superior (mm) |
|---|---|---|---|
| V_cont = 600 V | PD1 | 1,68 | 1,80 |
| V_cont = 600 V | PD2 | 3,04 | 3,20 |
| V_fault_max = 734 V | PD1 | 2,17 | 2,40 |
| V_fault_max = 734 V | PD2 | 3,69 | 4,00 |

Distancias requeridas a V_cont = 600 V: el máximo entre la regla del proyecto y las normas aplicables.

| Caso | Regla del proyecto (mm) | IPC-2221B (mm) | IEC 60664-1 (mm) | Requerido (mm) | Criterio |
|---|---|---|---|---|---|
| HV–BT, superficie con coating | 4,00 | 1,10 | 1,68 | 4,00 | IPC A5 · IEC PD_coat × factor de aislamiento |
| HV–HV, superficie con coating | 2,00 | 1,10 | 1,68 | 2,00 | IPC A5 · IEC PD_coat, básico |
| HV–HV, capas internas | 2,00 | 0,50 | — | 2,00 | IPC B1 (la línea de fuga no aplica en capas internas) |
| HV–HV, terminales sin recubrir | 2,00 | 1,80 | 3,04 | 3,04 | IPC A6 · IEC PD_bare, básico |
| Taladros del waterblock – conductores | 4,00 | — | — | 4,00 | Regla del proyecto |

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Distancia prevista: HV–BT, superficie con coating (AIS-HVLV_coat) | 5,00 | mm | 4,00 | CUMPLE |  | Valor previsto en `diseno.md` (estado TBD) |
| Distancia prevista: HV–HV, superficie con coating (AIS-HVHV_coat) | 2,50 | mm | 2,00 | CUMPLE |  | Valor previsto en `diseno.md` (estado TBD) |
| Distancia prevista: HV–HV, capas internas (AIS-HVHV_int) | 2,50 | mm | 2,00 | CUMPLE |  | Valor previsto en `diseno.md` (estado TBD) |
| Distancia prevista: HV–HV, terminales sin recubrir (AIS-HVHV_bare) | 3,50 | mm | 3,04 | CUMPLE |  | Valor previsto en `diseno.md` (estado TBD) |
| Distancia prevista: Taladros del waterblock – conductores (AIS-WB) | 4,00 | mm | 4,00 | CUMPLE |  | Valor previsto en `diseno.md` (estado TBD) |

### 5.1 Componentes que cruzan la barrera HV–BT

La línea de fuga del encapsulado debe ser ≥ la requerida HV–BT; la tensión de trabajo de la barrera, ≥ V_cont.

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Línea de fuga del encapsulado: ADuM4146 (gate driver) (AIS-F-ADUM4146) | 8,3 | mm | 4,0 | CUMPLE |  | ADI: 8,3 mm mín.; VIORM 2150 V pico |
| Tensión de trabajo de la barrera: ADuM4146 (gate driver) (AIS-V-ADUM4146) | 2150 | V | 600 | CUMPLE |  |  |
| Línea de fuga del encapsulado: AMC1302 (amplificador aislado) (AIS-F-AMC1302) | 8,5 | mm | 4,0 | CUMPLE |  | TI: ≥ 8,5 mm; VIORM 2121 V pico |
| Tensión de trabajo de la barrera: AMC1302 (amplificador aislado) (AIS-V-AMC1302) | 2121 | V | 600 | CUMPLE |  |  |
| Línea de fuga del encapsulado: AMC1306 (modulador ΔΣ aislado) (AIS-F-AMC1306) | 8,5 | mm | 4,0 | CUMPLE |  | TI: ≥ 8,5 mm; VIORM 2120 V pico |
| Tensión de trabajo de la barrera: AMC1306 (modulador ΔΣ aislado) (AIS-V-AMC1306) | 2120 | V | 600 | CUMPLE |  |  |
| Línea de fuga del encapsulado: MGJ2D052005BSC (fuente aislada de puerta) (AIS-F-MGJ2) | 2,0 | mm | 4,0 | **REVISAR** |  | Murata: 2 mm en el apartado de la aprobación UL60950; 2400 V de tensión continua de barrera. Medir la distancia real entre pines en el footprint |
| Tensión de trabajo de la barrera: MGJ2D052005BSC (fuente aislada de puerta) (AIS-V-MGJ2) | 2400 | V | 600 | CUMPLE |  |  |


## 6. Integridad de señal

Impedancia con IPC-2141A (microstrip y stripline centrada) y National AN-905 (pares diferenciales); retardo de propagación y longitud crítica con la regla tr/6. Aproximaciones de ±10 %: el valor final lo da el calculador del fabricante (PT-01).

### 6.1 Stackup

εr = 4,50; h (microstrip) = 0,200 mm; b (stripline) = 0,500 mm; cobre externo 0,070 mm; interno 0,070 mm.

| Magnitud | Valor | Unidad | Expresión | Nota |
|---|---|---|---|---|
| Ancho para 50 Ω en microstrip | 0,282 | mm | `IPC-2141A despejada` |  |
| Ancho para 50 Ω en stripline | 0,115 | mm | `IPC-2141A despejada` | Con 2 oz en capas internas el ancho queda muy fino: consultar al fabricante |

Interfaces de `diseno.md`, tabla 2. Validez: microstrip 0,1 ≤ w/h ≤ 2; stripline w/(b−t) < 0,35 y t/b < 0,25.

| Interfaz | Tipo/capa | Z obj. (Ω) | w (mm) | Z0 (Ω) | Zdif (Ω) | Desv. (%) | Fórmula válida | tpd (ps/mm) | L crítica (mm) | L prevista (mm) | ¿Línea de transmisión? | Estado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EtherCAT IN (MDI) | Dif/MS | 100 | 0,200 | 59,0 | 96,3 | −3,7 | Sí | 5,59 | 149 | 30 | Sí | TBD |
| EtherCAT OUT (MDI) | Dif/MS | 100 | 0,200 | 59,0 | 96,3 | −3,7 | Sí | 5,59 | 149 | 30 | Sí | TBD |
| Reloj FPGA–PHY | SE/SL | 50 | 0,120 | 49,3 | — | −1,3 | Sí | 7,08 | 118 | 60 | No | TBD |
| Datos FPGA–PHY | SE/SL | 50 | 0,120 | 49,3 | — | −1,3 | Sí | 7,08 | 118 | 60 | No | TBD |
| Reloj de los moduladores ΔΣ | SE/SL | 50 | 0,120 | 49,3 | — | −1,3 | Sí | 7,08 | 118 | 80 | No | TBD |
| Datos de los moduladores ΔΣ | SE/SL | 50 | 0,120 | 49,3 | — | −1,3 | Sí | 7,08 | 118 | 80 | No | TBD |
| PWM a los drivers | SE/MS | 50 | 0,290 | 49,3 | — | −1,5 | Sí | 5,59 | 149 | 100 | No | TBD |
| JTAG TCK | SE/MS | 50 | 0,290 | 49,3 | — | −1,5 | Sí | 5,59 | 149 | 100 | No | TBD |

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Impedancia: EtherCAT IN (MDI) (SI-mdi_in) | 96,3 | Ω | 100 ± 10 % | CUMPLE | `\|Z − Z_obj\| ≤ tol_Z·Z_obj` | Tolerancia ±10 % |
| Impedancia: EtherCAT OUT (MDI) (SI-mdi_out) | 96,3 | Ω | 100 ± 10 % | CUMPLE | `\|Z − Z_obj\| ≤ tol_Z·Z_obj` | Tolerancia ±10 % |
| Impedancia: Reloj FPGA–PHY (SI-reloj_phy) | 49,3 | Ω | 50 ± 10 % | CUMPLE | `\|Z − Z_obj\| ≤ tol_Z·Z_obj` | Tolerancia ±10 % |
| Impedancia: Datos FPGA–PHY (SI-datos_phy) | 49,3 | Ω | 50 ± 10 % | CUMPLE | `\|Z − Z_obj\| ≤ tol_Z·Z_obj` | Tolerancia ±10 % |
| Impedancia: Reloj de los moduladores ΔΣ (SI-reloj_ds) | 49,3 | Ω | 50 ± 10 % | CUMPLE | `\|Z − Z_obj\| ≤ tol_Z·Z_obj` | Tolerancia ±10 % |
| Impedancia: Datos de los moduladores ΔΣ (SI-datos_ds) | 49,3 | Ω | 50 ± 10 % | CUMPLE | `\|Z − Z_obj\| ≤ tol_Z·Z_obj` | Tolerancia ±10 % |
| Impedancia: PWM a los drivers (SI-pwm) | 49,3 | Ω | 50 ± 10 % | CUMPLE | `\|Z − Z_obj\| ≤ tol_Z·Z_obj` | Tolerancia ±10 % |
| Impedancia: JTAG TCK (SI-jtag_tck) | 49,3 | Ω | 50 ± 10 % | CUMPLE | `\|Z − Z_obj\| ≤ tol_Z·Z_obj` | Tolerancia ±10 % |

### 6.2 Presupuesto de tiempos de la interfaz FPGA–PHY

Interfaz síncrona con reloj común: holgura de setup = T − (tco_max + t_vuelo,datos + t_su + t_jit + t_desfase,reloj); holgura de hold = tco_min + t_vuelo,datos − (t_h + t_desfase,reloj).

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Periodo de reloj | 20,00 | ns |  |  | `1/f_bus_clk` |  |
| Tiempo de vuelo de los datos | 0,425 | ns |  |  | `L·tpd de SI_if_datos` |  |
| Desfase del reloj por diferencia de longitud | 0,071 | ns |  |  | `dL_clk·tpd de SI_if_reloj` |  |
| Holgura de setup (SI-SETUP) | 5,00 | ns | 0,00 | CUMPLE | `T − (tco_max + t_fl_data + t_su + t_jit + t_skew_clk) ≥ 0` |  |
| Holgura de hold (SI-HOLD) | 0,35 | ns | 0,00 | CUMPLE | `tco_min + t_fl_data − (t_h + t_skew_clk) ≥ 0` |  |

### 6.3 Igualación de longitudes

| Magnitud | Valor | Unidad | Expresión | Nota |
|---|---|---|---|---|
| Diferencia de longitud máxima dentro del par | 0,89 | mm | `skew_pair/tpd de SI_if_par` |  |


## 7. Sensado y adquisición

Opción A1: amplificador aislado (AMC1302) + ADC. Opción A2: modulador ΔΣ aislado (AMC1306) + filtro sinc en la FPGA. La opción está pendiente (FW-01, HW-05). Datos de los sensores en `componentes.md`.

### 7.1 Corriente de bobina (shunt)

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Resistencia del shunt | 500 | µΩ |  |  | `R_shunt` | Entrada (AC) |
| Fondo de escala de corriente | 100,0 | A |  |  | `Sd_Vlin/R_shunt` | Mismo rango lineal en AMC1302 y AMC1306x05 |
| Fondo de escala frente a Ipk con margen (SEN-01) | 100,0 | A | 72,0 | CUMPLE | `I_FS ≥ I_margin·Ipk` |  |
| Corriente de recorte (AMC1302) | 128,0 | A |  |  | `Sa_Vclip/R_shunt` |  |
| Tensión en el shunt a Ipk | 30,0 | mV |  |  | `Ipk·R_shunt` |  |
| Umbral de sobrecorriente por encima de Ipk (SEN-02) | 90 | A | 60 | CUMPLE | `I_OC ≥ Ipk` |  |
| Umbral de sobrecorriente dentro del rango lineal (SEN-03) | 90 | A | 100 | CUMPLE | `I_OC ≤ I_FS` |  |

### 7.2 Opción A1: amplificador aislado + ADC

| Magnitud | Valor | Unidad | Expresión | Nota |
|---|---|---|---|---|
| Tensión diferencial de salida a Ipk | 1,230 | V | `Ipk·R_shunt·Sa_G` |  |
| Resolución (LSB) con el ADC | 48,8 | mA | `2·I_FS/2^N_adc` |  |
| Retardo de la cadena / semiperiodo de PWM | 12,0 | % | `Sa_td·2·fsw` |  |

### 7.3 Opción A2: modulador ΔΣ + filtro sinc

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Frecuencia de reloj dentro del rango del modulador (SEN-04) | 20,0 | MHz | 5 a 21 | CUMPLE | `Sd_fmin ≤ f_clk_ds ≤ Sd_fmax` |  |
| Frecuencia de datos a la salida del filtro | 156,25 | kHz |  |  | `f_clk_ds/OSR` |  |
| Muestras por periodo de PWM | 7,81 | – |  |  | `f_clk_ds/(OSR·fsw)` |  |
| Longitud de palabra a la salida del sinc | 22,0 | bit |  |  | `N_sinc·log2(OSR) + 1` |  |
| Retardo de grupo del filtro | 9,53 | µs |  |  | `N_sinc·(OSR − 1)/(2·f_clk_ds)` |  |
| Tiempo de establecimiento del filtro frente al semiperiodo de PWM (SEN-05) | 19,2 | µs | 25,0 | CUMPLE | `N_sinc·OSR/f_clk_ds ≤ 1/(2·fsw)` | Una muestra independiente por semiperiodo (muestreo sincronizado) |
| Resolución efectiva (con el ENOB de la hoja de datos) | 12,2 | mA |  |  | `2·I_FS/2^Sd_ENOB` | ENOB dado con OSR = 256; recalcular con el OSR elegido |

### 7.4 Tensión de bus (divisor + sensor aislado)

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Resistencia inferior efectiva (con la entrada del sensor) | 956,5 | Ω |  |  | `R_div_bot ∥ R_sens_in` |  |
| Resistencia superior total | 2677,3 | kΩ |  |  | `R_bot_eff·(V_meas_FS/V_sens_FS − 1)` |  |
| Resistencias en serie necesarias en la rama superior | 4 | – |  |  | `⌈max(V_cont, V_fault_max)/V_res_rat⌉` |  |
| Valor de cada resistencia superior | 669,3 | kΩ |  |  | `R_top/N_res` |  |
| Corriente del divisor a V_cont | 224 | µA |  |  | `V_cont/(R_top + R_bot_eff)` |  |
| Potencia en cada resistencia superior a V_cont (SEN-06) | 33,6 | mW | 125,0 | CUMPLE | `I_div²·R_top/N_res ≤ k_res·P_res_rat` |  |
| Tensión en cada resistencia superior en el caso de fallo (SEN-07) | 183 | V | 200 | CUMPLE | `V_fault_max·R_top/(R_top + R_bot_eff)/N_res ≤ V_res_rat` |  |
| Fondo de escala de Vbus frente a la tensión de fallo (SEN-08) | 700 | V | 734 | **NO CUMPLE** | `V_meas_FS ≥ V_fault_max` |  |
| Tensión en el sensor a Vbus_max | 142,9 | mV |  |  | `Vbus_max·R_bot_eff/(R_top + R_bot_eff)` |  |
| Resolución efectiva de Vbus | 0,085 | V |  |  | `2·V_meas_FS/2^Sd_ENOB` | Rango bipolar del sensor con bus unipolar: se usa la mitad de los códigos |
| Umbral de sobretensión por encima de Vbus_max (SEN-09) | 450 | V | 400 | CUMPLE | `V_OV ≥ Vbus_max` |  |
| Umbral de sobretensión por debajo de V_cont (SEN-10) | 450 | V | 600 | CUMPLE | `V_OV ≤ V_cont` |  |
| Tensión en el sensor en el umbral de sobretensión | 160,7 | mV |  |  | `V_OV·R_bot_eff/(R_top + R_bot_eff)` |  |

### 7.5 NTC de bobina (modelo β)

R(T) = R25·exp(β·(1/T − 1/298,15)); divisor con la NTC abajo: V = Vref·R/(R + R_pol). El modelo β pierde exactitud lejos de 25–85 °C: para el umbral definitivo, use la tabla R-T del fabricante o Steinhart-Hart.

| Magnitud | Valor | Unidad | Expresión | Nota |
|---|---|---|---|---|
| R de la NTC a T_coil_max | 688 | Ω | `R25·exp(β(1/T − 1/T25))` |  |
| Tensión del divisor a T_coil_max (umbral del comparador) | 0,322 | V | `V_ntc_ref·R/(R + R_ntc_pu)` |  |
| Sensibilidad a T_coil_max | −7,38 | mV/°C | `dV/dT` |  |
| Autocalentamiento: potencia en la NTC a 25 °C | 0,62 | mW | `Vref²·R25/(R25 + R_pol)²` | Comparar con la constante de disipación de la NTC |

Curva de la NTC con la polarización elegida.

| T (°C) | R_NTC (kΩ) | V_NTC (V) | dV/dT (mV/°C) |
|---|---|---|---|
| -20 | 85,435 | 4,476 | −26,33 |
| -10 | 49,782 | 4,164 | −36,19 |
| 0 | 30,177 | 3,756 | −45,08 |
| 10 | 18,951 | 3,273 | −50,73 |
| 20 | 12,285 | 2,756 | −51,78 |
| 30 | 8,195 | 2,252 | −48,46 |
| 40 | 5,610 | 1,797 | −42,24 |
| 50 | 3,931 | 1,411 | −34,90 |
| 60 | 2,814 | 1,098 | −27,78 |
| 70 | 2,055 | 0,852 | −21,60 |
| 80 | 1,527 | 0,662 | −16,58 |
| 90 | 1,153 | 0,517 | −12,65 |
| 100 | 0,884 | 0,406 | −9,64 |
| 110 | 0,688 | 0,322 | −7,38 |
| 120 | 0,541 | 0,257 | −5,67 |
| 130 | 0,432 | 0,207 | −4,39 |
| 140 | 0,348 | 0,168 | −3,42 |
| 150 | 0,283 | 0,138 | −2,69 |


## 8. Gate driving

Driver ADuM4146 y fuente aislada MGJ2 (datos en `componentes.md`). MOSFET seleccionado: **IMT65R010M2H**.

### 8.1 Tensiones de puerta frente al MOSFET

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Vgs_on dentro del rango recomendado del MOSFET (GDR-01) | 18 | V | 15 | **REVISAR** | `Vgs_on ≤ VGSrec_on` | El TFG usa +20 V |
| Vgs_on por debajo del máximo absoluto (GDR-02) | 18 | V | 20 | CUMPLE | `Vgs_on ≤ VGSmax` |  |
| Vgs_off dentro del rango recomendado (GDR-03) | −3 | V | −5 | CUMPLE | `Vgs_off ≥ VGSrec_off` |  |

### 8.2 Potencia de puerta y fuentes aisladas (por MOSFET)

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Excursión de tensión de puerta | 21,0 | V |  |  | `Vgs_on − Vgs_off` |  |
| Potencia de puerta | 0,040 | W |  |  | `Qg·dVg·fsw` | Qg medida con la excursión de la hoja de datos: aproximación |
| Potencia en la salida de la fuente aislada | 0,176 | W |  |  | `P_gate + D_IDD2·dVg` |  |
| Carga de la fuente aislada frente a su potencia nominal (GDR-04) | 0,176 | W | 2,000 | CUMPLE | `P_iso_out ≤ G_P` |  |
| Corriente media de la salida +20 V (GDR-05) | 8,4 | mA | 80,0 | CUMPLE | `Qg·fsw + D_IDD2 ≤ G_Ipos` |  |
| Corriente media de la salida −5 V (GDR-06) | 8,4 | mA | 40,0 | CUMPLE | `Qg·fsw + D_IDD2 ≤ G_Ineg` | Supone que toda la corriente de VDD2 vuelve por −5 V (conservador) |
| Potencia de entrada de cada fuente aislada | 0,238 | W |  |  | `P_iso_out/G_eta` |  |
| Corriente de entrada de cada fuente aislada | 47,7 | mA |  |  | `P_iso_in/G_Vin` | Se usa en el consumo de BT |

### 8.3 Corrientes de pico, dv/dt y Miller

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Corriente de pico de encendido (GDR-07) | 2,00 | A | 11,00 | CUMPLE | `dVg/(Rg_on + Rgint + D_Rp) ≤ D_Isrc` | Límite: corriente de cortocircuito del driver |
| Corriente de pico de apagado (GDR-08) | 2,04 | A | 9,00 | CUMPLE | `dVg/(Rg_off + Rgint + D_Rn) ≤ D_Isnk` |  |
| Constante de tiempo de encendido | 23,8 | ns |  |  | `(Rg_on + Rgint)·Ciss` |  |
| dv/dt estimada | 10,0 | kV/µs |  |  | `Vbus_max/tr` | tr de la hoja de datos con su RG de ensayo: recalcular con la RG real |
| dv/dt frente a la CMTI del driver (GDR-09) | 10,0 | kV/µs | 100,0 | CUMPLE | `dvdt ≤ CMTI` |  |
| dv/dt frente a la CMTI de los sensores aislados (GDR-10) | 10,0 | kV/µs | 100,0 | CUMPLE | `dvdt ≤ CMTI` |  |
| dv/dt frente a la CMTI de la fuente aislada (GDR-11) | 10,0 | kV/µs | 200,0 | CUMPLE | `dvdt ≤ CMTI` |  |
| Corriente de Miller | 0,180 | A |  |  | `Crss·dvdt` | Crss a 600 V; a VDS baja es mayor |
| Pico de VGS en OFF por efecto Miller (GDR-12) | −2,23 | V | 3,00 | CUMPLE | `Vgs_off + I_miller·(D_Rclamp + Rgint) ≤ Vth_min` | Con el Miller clamp activo |

### 8.4 Tiempo muerto

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Tiempo muerto mínimo | 90 | ns |  |  | `(tdoff + tf − tdon) + D_skew + t_dead_mrg` | Tiempos del MOSFET con su RG de ensayo |
| Tiempo muerto configurado frente al mínimo (GDR-13) | 100 | ns | 90 | CUMPLE | `t_dead ≥ t_dead_min` |  |
| Error de tensión media por el tiempo muerto | 1,60 | V |  |  | `2·t_dead·fsw·Vbus_max` |  |
| Error relativo a la tensión de bobina a Ipk | 2,2 | % |  |  | `dV_dead/V_coil_pk` | Lo compensa el lazo de corriente |

### 8.5 Protección DESAT

Umbral en VDS ≈ V_DESAT − N·Vf − I_carga·R_serie. La corriente de disparo se estima con RDS(on) lineal: en la zona de saturación la VDS crece más deprisa y el disparo real llega antes. Con pocos mΩ, un umbral de 9,2 V equivale a cientos de amperios: valorar el grado A/C (3,5 V) o un divisor.

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| VDS de disparo | 7,97 | V |  |  | `D_desat − N_d_desat·Vf_desat − D_Idesat·R_desat` |  |
| Corriente de disparo en caliente | 532 | A |  |  | `V_ds_trip/Rhot` |  |
| Corriente de disparo a 25 °C (peor caso) frente a la ID pulsada (GDR-14) | 797 | A | 300 | **REVISAR** | `V_ds_trip/R25 ≤ IDM` | En frío la RDS(on) es menor y el disparo llega más tarde |
| Tiempo de blanking externo | 0,820 | µs |  |  | `C_blank·D_desat/D_Idesat` |  |
| Tiempo de respuesta DESAT (enmascaramiento + blanking) (GDR-15) | 1,16 | µs | 2,00 | CUMPLE | `D_mask + t_blank ≤ t_desat_max` | No incluye la propagación interna ni el soft shutdown |
| Tensión de VDD2 por encima del UVLO del driver (GDR-16) | 18,0 | V | 11,5 | CUMPLE | `Vgs_on ≥ D_UVLO` |  |


## 9. Alimentación auxiliar (BT)

Consumo por placa desde la batería de BT: P = V·I·N/(η_raíl·eta_BT). Consumos de `diseno.md`, tabla 4.

| Consumidor | Raíl (V) | I (mA) | Nº | P en carga (W) | η raíl (%) | P desde BT (W) | Estado |
|---|---|---|---|---|---|---|---|
| FPGA MachXO5-NX: núcleo | 1,0 | 150,00 | 1 | 0,150 | 85 | 0,208 | TBD |
| FPGA MachXO5-NX: bancos de E/S | 3,3 | 30,00 | 1 | 0,099 | 85 | 0,137 | TBD |
| PHY Ethernet | 3,3 | 60,00 | 2 | 0,396 | 85 | 0,548 | TBD |
| Oscilador | 3,3 | 10,00 | 1 | 0,033 | 85 | 0,046 | TBD |
| EEPROM SII | 3,3 | 1,00 | 1 | 0,003 | 85 | 0,005 | TBD |
| Moduladores ΔΣ, lado BT (DVDD) | 3,3 | 6,00 | 3 | 0,059 | 85 | 0,082 | AC |
| Moduladores ΔΣ, lado HV (AVDD) vía fuente aislada | 5,0 | 9,80 | 3 | 0,147 | 70 | 0,247 | AC |
| Gate drivers ADuM4146, lado BT (VDD1) | 5,0 | 2,17 | 4 | 0,043 | 85 | 0,060 | AC |
| Fuentes aisladas de puerta (entrada a 5 V) | 5,0 | 47,68 | 4 | 0,954 | 85 | 1,320 | AC |
| Lógica cableada y comparadores | 3,3 | 10,00 | 1 | 0,033 | 85 | 0,046 | TBD |
| LEDs | 3,3 | 2,00 | 4 | 0,026 | 85 | 0,037 | TBD |

| Magnitud | Valor | Unidad | Límite | Resultado | Expresión | Nota |
|---|---|---|---|---|---|---|
| Subtotal desde BT | 2,73 | W |  |  | `Σ P desde BT` |  |
| Total por placa con margen | 3,28 | W |  |  | `P_BT_sub·(1 + P_margin)` | Se suma a las pérdidas en el balance térmico |
| Corriente de entrada a V_BT_min | 0,182 | A |  |  | `P_BT_total/V_BT_min` |  |
| Corriente de entrada a V_BT_max | 0,137 | A |  |  | `P_BT_total/V_BT_max` |  |
| Consumo de las N_MD placas | 32,8 | W |  |  | `N_MD·P_BT_total` | Dato para ME-I-02 |
| Consumo por placa frente al permitido (BT-01) | 3,28 | W | 15,00 | CUMPLE | `P_BT_total ≤ P_BT_lim` |  |
| EtherCAT P: corriente de la línea completa (BT-02) | 1,37 | A | 3,00 | CUMPLE | `N_MD·P_BT_total/ECP_V ≤ ECP_Imax` | Solo si se elige EtherCAT P: la primera conexión alimenta a todas las placas |

PoE es un enlace punto a punto y no encaja directamente con EtherCAT en línea (ME-I-02).

| Tipo de PoE | Potencia en el equipo alimentado (W) | ¿Suficiente para una placa? |
|---|---|---|
| IEEE 802.3af (Tipo 1) | 12,95 | Sí |
| IEEE 802.3at (Tipo 2) | 25,50 | Sí |
| IEEE 802.3bt (Tipo 3) | 51,00 | Sí |
| IEEE 802.3bt (Tipo 4) | 71,30 | Sí |


## Anexo A. Todas las comprobaciones

| ID | Comprobación | Apartado | Valor | Límite | Unidad | Resultado | Requisito | Depende de | Nota |
|---|---|---|---|---|---|---|---|---|---|
| POT-01 | Rizado en el peor caso (L mínima, Vbus_max) | 1. Potencia y bus DC | 1,30 | 1,50 | A | CUMPLE | LOAD-07 | EM-C-03, FW-08 | Doc. v0.2 §6.1.3: 1,30 A (EMS) y 0,40 A (HEMS) a 400 V, unipolar |
| POT-02 | Corriente máxima alcanzable con Vbus_min (sin pérdidas) | 1. Potencia y bus DC | 266,7 | 60,0 | A | CUMPLE | LOAD-03 |  | Margen de tensión para el lazo de corriente |
| POT-03 | Rizado de tensión en el DC-link, peor caso (m = 0,5) | 1. Potencia y bus DC | 3,69 | 6,40 | V | CUMPLE | DCB-07 | HW-02 (ESR) | Límite: dVdc_pct·Vbus_min |
| POT-04 | Tensión de fallo (extrapolada) frente a la tensión continua admisible | 1. Potencia y bus DC | 734 | 600 | V | **NO CUMPLE** | DCB-08 · DCB-02 | HW-03, EM-D-03 | Sin clamp, chopper ni DC-link mayor |
| POT-05 | Tensión de fallo frente a la tensión nominal del DC-link | 1. Potencia y bus DC | 734 | 630 | V | **NO CUMPLE** | DCB-08 | HW-02, HW-03 |  |
| POT-06 | Tensión de fallo frente a la VDS del MOSFET seleccionado | 1. Potencia y bus DC | 734 | 650 | V | **NO CUMPLE** | PWR-02 | HW-02 |  |
| POT-07 | Capacidad instalada frente a la necesaria para no superar V_cont desde Vbus_max | 1. Potencia y bus DC | 105 | 199 | µF | **NO CUMPLE** | DCB-08 | HW-03, EM-D-03 | Doc. v0.2: ≥ 167 µF con 16,7 J |
| POT-08 | Tensión de actuación del chopper por encima de Vbus_max con margen | 1. Potencia y bus DC | 500 | 440 | V | CUMPLE | HW-03 | HW-03 | Para no actuar en servicio |
| POT-09 | Tensión de actuación del chopper por debajo de V_cont | 1. Potencia y bus DC | 500 | 600 | V | CUMPLE | HW-03 | HW-03 |  |
| POT-10 | Corriente media de bus a Ipk frente al fusible con factor de utilización | 1. Potencia y bus DC | 13,92 | 11,25 | A | **REVISAR** | DCB-06 | EM-C-01, ME-I-03 | El pico dura t_pk: revisar con la curva tiempo-corriente del fusible |
| POT-11 | Corriente de entrada de la primera placa frente al fusible (si está en el camino encadenado) | 1. Potencia y bus DC | 13,92 | 11,25 | A | **REVISAR** | DCB-05 · DCB-06 | ME-I-03 |  |
| POT-12 | Tensión nominal del fusible frente a V_cont | 1. Potencia y bus DC | 500 | 600 | V | **NO CUMPLE** | DCB-02 · DCB-06 | HW-02 | El 0ADKC9150-BE es de 500 VDC |
| POT-13 | Tensión nominal del fusible frente a la tensión de fallo | 1. Potencia y bus DC | 500 | 734 | V | **NO CUMPLE** | DCB-08 | HW-02, HW-03 |  |
| GDR-01 | Vgs_on dentro del rango recomendado del MOSFET | 8. Gate driving | 18 | 15 | V | **REVISAR** | GD-01 | HW-02 | El TFG usa +20 V |
| GDR-02 | Vgs_on por debajo del máximo absoluto | 8. Gate driving | 18 | 20 | V | CUMPLE | GD-01 | HW-02 |  |
| GDR-03 | Vgs_off dentro del rango recomendado | 8. Gate driving | −3 | −5 | V | CUMPLE | GD-01 | HW-02 |  |
| GDR-04 | Carga de la fuente aislada frente a su potencia nominal | 8. Gate driving | 0,176 | 2,000 | W | CUMPLE | GD-01 · AUX-02 | HW-02 |  |
| GDR-05 | Corriente media de la salida +20 V | 8. Gate driving | 8,4 | 80,0 | mA | CUMPLE | GD-01 | HW-02 |  |
| GDR-06 | Corriente media de la salida −5 V | 8. Gate driving | 8,4 | 40,0 | mA | CUMPLE | GD-01 | HW-02 | Supone que toda la corriente de VDD2 vuelve por −5 V (conservador) |
| GDR-07 | Corriente de pico de encendido | 8. Gate driving | 2,00 | 11,00 | A | CUMPLE | GD-01 | HW-02 | Límite: corriente de cortocircuito del driver |
| GDR-08 | Corriente de pico de apagado | 8. Gate driving | 2,04 | 9,00 | A | CUMPLE | GD-01 | HW-02 |  |
| GDR-09 | dv/dt frente a la CMTI del driver | 8. Gate driving | 10,0 | 100,0 | kV/µs | CUMPLE | GD-01 | HW-02 |  |
| GDR-10 | dv/dt frente a la CMTI de los sensores aislados | 8. Gate driving | 10,0 | 100,0 | kV/µs | CUMPLE | SNS-01 | HW-02, FW-01 |  |
| GDR-11 | dv/dt frente a la CMTI de la fuente aislada | 8. Gate driving | 10,0 | 200,0 | kV/µs | CUMPLE | AUX-02 | HW-02 |  |
| GDR-12 | Pico de VGS en OFF por efecto Miller | 8. Gate driving | −2,23 | 3,00 | V | CUMPLE | GD-01 | HW-02 | Con el Miller clamp activo |
| GDR-13 | Tiempo muerto configurado frente al mínimo | 8. Gate driving | 100 | 90 | ns | CUMPLE | PWR-04 | FW-08, HW-02 |  |
| GDR-14 | Corriente de disparo a 25 °C (peor caso) frente a la ID pulsada | 8. Gate driving | 797 | 300 | A | **REVISAR** | GD-01 · SAF-04 | HW-01, HW-02 | En frío la RDS(on) es menor y el disparo llega más tarde |
| GDR-15 | Tiempo de respuesta DESAT (enmascaramiento + blanking) | 8. Gate driving | 1,16 | 2,00 | µs | CUMPLE | GD-01 | HW-01 | No incluye la propagación interna ni el soft shutdown |
| GDR-16 | Tensión de VDD2 por encima del UVLO del driver | 8. Gate driving | 18,0 | 11,5 | V | CUMPLE | GD-02 | HW-02 |  |
| BT-01 | Consumo por placa frente al permitido | 9. Alimentación auxiliar (BT) | 3,28 | 15,00 | W | CUMPLE | AUX-03 | ME-I-02, HW-05 |  |
| BT-02 | EtherCAT P: corriente de la línea completa | 9. Alimentación auxiliar (BT) | 1,37 | 3,00 | A | CUMPLE | AUX-01 | ME-I-02 | Solo si se elige EtherCAT P: la primera conexión alimenta a todas las placas |
| TER-01 | Área de FR-4 restante bajo el pad | 3. Térmico | 67,5 | 0,0 | mm² | CUMPLE | PWR-06 | HW-02, PT-01 | Si es negativa, las vías no caben en el pad |
| TER-02 | Rigidez dieléctrica del material de interfaz | 3. Térmico | 4000 | 600 | V | CUMPLE | ISO-04 · ISO-06 | ME-C-01, HW-04 | Margen exigido por definir con el tipo de aislamiento (HW-04) |
| TER-03 | Potencia de pico en el shunt frente a su potencia nominal | 3. Térmico | 1,80 | 3,00 | W | CUMPLE | SNS-01 | HW-02, EM-C-01 | Si el pico es corto, usar la curva de sobrecarga del shunt |
| TER-04 | Tj a Ipk (régimen permanente) | 3. Térmico | 676,3 | 150,0 | °C | **NO CUMPLE** | PWR-05 | EM-C-01, ME-C-01, ME-C-02, HW-02 | Conservador si t_pk es corto frente a las constantes térmicas |
| TER-05 | Tj en continuo (Irms_cont) | 3. Térmico | 73,2 | 150,0 | °C | CUMPLE | PWR-05 | EM-C-01, ME-C-01, ME-C-02 |  |
| TER-06 | Coherencia: Tj a Ipk ≤ Tj_assumed usada para la RDS(on) | 3. Térmico | 676,3 | 125,0 | °C | **REVISAR** | — |  | Si falla, suba Tj_assumed y recalcule |
| PIS-entrada_pk | Ancho de pista: Entrada HV (1.ª placa), Ipk | 4. Pistas y vías de potencia | 35,0 | 1,1 | mm | CUMPLE | DCB-03 · LOAD-03 | MEC-03, PT-01, ME-I-03 |  |
| PIS-entrada_cont | Ancho de pista: Entrada HV (1.ª placa), continuo | 4. Pistas y vías de potencia | 10,0 | 0,0 | mm | CUMPLE | DCB-03 · LOAD-03 | MEC-03, PT-01, ME-I-03 |  |
| PIS-puente_rms | Ancho de pista: DC-link ↔ puente, eficaz a Ipk | 4. Pistas y vías de potencia | 15,0 | 3,0 | mm | CUMPLE | DCB-03 · LOAD-03 | MEC-03, PT-01, ME-I-03 |  |
| PIS-bobina_pk | Ancho de pista: Puente → bobina, Ipk | 4. Pistas y vías de potencia | 15,0 | 8,4 | mm | CUMPLE | DCB-03 · LOAD-03 | MEC-03, PT-01, ME-I-03 |  |
| PIS-bobina_cont | Ancho de pista: Puente → bobina, continuo | 4. Pistas y vías de potencia | 5,0 | 0,3 | mm | CUMPLE | DCB-03 · LOAD-03 | MEC-03, PT-01, ME-I-03 |  |
| AIS-HVLV_coat | Distancia prevista: HV–BT, superficie con coating | 5. Aislamiento | 5,00 | 4,00 | mm | CUMPLE | ISO-02 · ISO-05 | HW-04, PT-01 (layout pendiente) | Valor previsto en `diseno.md` (estado TBD) |
| AIS-HVHV_coat | Distancia prevista: HV–HV, superficie con coating | 5. Aislamiento | 2,50 | 2,00 | mm | CUMPLE | ISO-03 | HW-04, PT-01 (layout pendiente) | Valor previsto en `diseno.md` (estado TBD) |
| AIS-HVHV_int | Distancia prevista: HV–HV, capas internas | 5. Aislamiento | 2,50 | 2,00 | mm | CUMPLE | ISO-03 | HW-04, PT-01 (layout pendiente) | Valor previsto en `diseno.md` (estado TBD) |
| AIS-HVHV_bare | Distancia prevista: HV–HV, terminales sin recubrir | 5. Aislamiento | 3,50 | 3,04 | mm | CUMPLE | ISO-03 | HW-04, PT-01 (layout pendiente) | Valor previsto en `diseno.md` (estado TBD) |
| AIS-WB | Distancia prevista: Taladros del waterblock – conductores | 5. Aislamiento | 4,00 | 4,00 | mm | CUMPLE | ISO-04 | HW-04, PT-01 (layout pendiente) | Valor previsto en `diseno.md` (estado TBD) |
| AIS-F-ADUM4146 | Línea de fuga del encapsulado: ADuM4146 (gate driver) | 5. Aislamiento | 8,3 | 4,0 | mm | CUMPLE | ISO-01 · ISO-02 | HW-04, HW-05 | ADI: 8,3 mm mín.; VIORM 2150 V pico |
| AIS-V-ADUM4146 | Tensión de trabajo de la barrera: ADuM4146 (gate driver) | 5. Aislamiento | 2150 | 600 | V | CUMPLE | ISO-06 |  |  |
| AIS-F-AMC1302 | Línea de fuga del encapsulado: AMC1302 (amplificador aislado) | 5. Aislamiento | 8,5 | 4,0 | mm | CUMPLE | ISO-01 · ISO-02 | HW-04, HW-05 | TI: ≥ 8,5 mm; VIORM 2121 V pico |
| AIS-V-AMC1302 | Tensión de trabajo de la barrera: AMC1302 (amplificador aislado) | 5. Aislamiento | 2121 | 600 | V | CUMPLE | ISO-06 |  |  |
| AIS-F-AMC1306 | Línea de fuga del encapsulado: AMC1306 (modulador ΔΣ aislado) | 5. Aislamiento | 8,5 | 4,0 | mm | CUMPLE | ISO-01 · ISO-02 | HW-04, HW-05 | TI: ≥ 8,5 mm; VIORM 2120 V pico |
| AIS-V-AMC1306 | Tensión de trabajo de la barrera: AMC1306 (modulador ΔΣ aislado) | 5. Aislamiento | 2120 | 600 | V | CUMPLE | ISO-06 |  |  |
| AIS-F-MGJ2 | Línea de fuga del encapsulado: MGJ2D052005BSC (fuente aislada de puerta) | 5. Aislamiento | 2,0 | 4,0 | mm | **REVISAR** | ISO-01 · ISO-02 | HW-04, HW-05 | Murata: 2 mm en el apartado de la aprobación UL60950; 2400 V de tensión continua de barrera. Medir la distancia real entre pines en el footprint |
| AIS-V-MGJ2 | Tensión de trabajo de la barrera: MGJ2D052005BSC (fuente aislada de puerta) | 5. Aislamiento | 2400 | 600 | V | CUMPLE | ISO-06 |  |  |
| SI-mdi_in | Impedancia: EtherCAT IN (MDI) | 6. Integridad de señal | 96,3 | 100 ± 10 % | Ω | CUMPLE | COM-03 | PT-01, FW-06 | Tolerancia ±10 % |
| SI-mdi_out | Impedancia: EtherCAT OUT (MDI) | 6. Integridad de señal | 96,3 | 100 ± 10 % | Ω | CUMPLE | COM-03 | PT-01, FW-06 | Tolerancia ±10 % |
| SI-reloj_phy | Impedancia: Reloj FPGA–PHY | 6. Integridad de señal | 49,3 | 50 ± 10 % | Ω | CUMPLE | COM-03 | PT-01, FW-06 | Tolerancia ±10 % |
| SI-datos_phy | Impedancia: Datos FPGA–PHY | 6. Integridad de señal | 49,3 | 50 ± 10 % | Ω | CUMPLE | COM-03 | PT-01, FW-06 | Tolerancia ±10 % |
| SI-reloj_ds | Impedancia: Reloj de los moduladores ΔΣ | 6. Integridad de señal | 49,3 | 50 ± 10 % | Ω | CUMPLE | COM-03 | PT-01, FW-06 | Tolerancia ±10 % |
| SI-datos_ds | Impedancia: Datos de los moduladores ΔΣ | 6. Integridad de señal | 49,3 | 50 ± 10 % | Ω | CUMPLE | COM-03 | PT-01, FW-06 | Tolerancia ±10 % |
| SI-pwm | Impedancia: PWM a los drivers | 6. Integridad de señal | 49,3 | 50 ± 10 % | Ω | CUMPLE | COM-03 | PT-01, FW-06 | Tolerancia ±10 % |
| SI-jtag_tck | Impedancia: JTAG TCK | 6. Integridad de señal | 49,3 | 50 ± 10 % | Ω | CUMPLE | COM-03 | PT-01, FW-06 | Tolerancia ±10 % |
| SI-SETUP | Holgura de setup | 6. Integridad de señal | 5,00 | 0,00 | ns | CUMPLE | COM-02 | FW-06 |  |
| SI-HOLD | Holgura de hold | 6. Integridad de señal | 0,35 | 0,00 | ns | CUMPLE | COM-02 | FW-06 |  |
| SEN-01 | Fondo de escala frente a Ipk con margen | 7. Sensado y adquisición | 100,0 | 72,0 | A | CUMPLE | SNS-01 | HW-02 |  |
| SEN-02 | Umbral de sobrecorriente por encima de Ipk | 7. Sensado y adquisición | 90 | 60 | A | CUMPLE | SAF-04 | HW-01 |  |
| SEN-03 | Umbral de sobrecorriente dentro del rango lineal | 7. Sensado y adquisición | 90 | 100 | A | CUMPLE | SAF-04 | HW-01 |  |
| SEN-04 | Frecuencia de reloj dentro del rango del modulador | 7. Sensado y adquisición | 20,0 | 5 a 21 | MHz | CUMPLE | SNS-05 | FW-01 |  |
| SEN-05 | Tiempo de establecimiento del filtro frente al semiperiodo de PWM | 7. Sensado y adquisición | 19,2 | 25,0 | µs | CUMPLE | SNS-05 · SNS-06 | FW-01 | Una muestra independiente por semiperiodo (muestreo sincronizado) |
| SEN-06 | Potencia en cada resistencia superior a V_cont | 7. Sensado y adquisición | 33,6 | 125,0 | mW | CUMPLE | SNS-02 | HW-02 |  |
| SEN-07 | Tensión en cada resistencia superior en el caso de fallo | 7. Sensado y adquisición | 183 | 200 | V | CUMPLE | DCB-02 · SNS-02 | HW-02, HW-03 |  |
| SEN-08 | Fondo de escala de Vbus frente a la tensión de fallo | 7. Sensado y adquisición | 700 | 734 | V | **NO CUMPLE** | SNS-02 · DCB-08 | HW-03 |  |
| SEN-09 | Umbral de sobretensión por encima de Vbus_max | 7. Sensado y adquisición | 450 | 400 | V | CUMPLE | SAF-01 | HW-01 |  |
| SEN-10 | Umbral de sobretensión por debajo de V_cont | 7. Sensado y adquisición | 450 | 600 | V | CUMPLE | SAF-01 · DCB-02 | HW-01 |  |

## Anexo B. Parámetros usados

Instantánea de todos los parámetros escalares en el momento del cálculo (ficheros de `calculos/entradas`). Las tablas de MOSFET, pistas, interfaces, distancias y consumos se muestran en sus apartados.

**`parametros.md` · 1. Bus DC**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `Vbus_min` | Tensión mínima del bus de HV | 320 | V | U | OK | DCB-01 | [v0.3] Antes 350 V (prueba). Valor de DCB-01 |
| `Vbus_max` | Tensión máxima del bus de HV | 400 | V | U | OK | DCB-01 | [v0.3] Antes 405 V (prueba). Valor de DCB-01. Confirmado el 19/09/2026 que la batería seguirá siendo de 400 V mucho tiempo |
| `V_cont` | Tensión continua que deben soportar componentes y aislamiento | 600 | V | U | OK | DCB-02 · ISO-06 · HW-08 | [v0.3] Antes 650 V (prueba). Valor de DCB-02. **Atención (HW-08):** el IMT65R010M2H es de 650 V, así que frente a este requisito trabaja al 92 % de su tensión de ruptura. Hay que decidir si el requisito de 600 V continuos aplica a los interruptores o solo al aislamiento y a los pasivos |
| `N_MD` | Número de Magnet Driver conectados al bus | 10 |  | U | OK | DCB-03 · SYS-01 | 4 HEMS + 6 EMS |
| `Bus_topo` | Distribución del bus: «Encadenado» o «Estrella» | Estrella |  | P | AC | DCB-05 · ME-I-03 · EM-C-05 | Si los 10 pican a la vez el bus entrega unos 108 A y el encadenado obligaría a la primera placa a conducirlos. Pendiente de que Electromagnetics confirme la simultaneidad |
| `dVdc_pct` | Rizado máximo de tensión en el DC-link (fracción de Vbus_min) | 2 | % | TFG | AC | DCB-07 · HW-02 | [v0.3] Antes 1 % (prueba). DCB-07 dice ≤ 2 %, que son 8 V sobre 400 V |
| `eta_pwr` | Rendimiento de la etapa de potencia (para la corriente media de bus) | 97 | % | C | AC | — | [v0.3] Antes 96 % (provisional). Calculado a 60 A: 4320 W a la bobina, 72 W de conducción y 23 a 47 W de conmutación según el reescalado de Eon/Eoff a `Rg_on` → 97,3 a 97,8 %. Se redondea a 97 % por debajo |

**`parametros.md` · 2. Carga: electroimanes (prototipo H11)**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `Rcoil` | Resistencia de la bobina | 1,2 | Ω | U | OK | LOAD-01 | [v0.3] Antes 1,1 Ω (prueba). Valor de LOAD-01, medido en la bobina construida. Nuevas bobinas: EM-D-04 |
| `Ipk` | Corriente de pico (primeros segundos de la levitación) | 60 | A | U | OK | LOAD-03 | [v0.3] Antes 55 A (valor del TFG). Valor de LOAD-03. Los 55 A siguen siendo el límite de los mapas de inductancia (`I_map`) |
| `t_pk` | Duración del pico de corriente | 2 | s | U | OK | LOAD-03 · EM-C-01 | Confirmado el 19/09/2026: no será mucho mayor de 2 s. A 2 s el die está prácticamente en régimen permanente, así que el térmico se evalúa con `Rthjc` y no con la impedancia transitoria |
| `Irms_cont` | Corriente eficaz en régimen permanente (dimensionado térmico) | 5 | A | TFG | TBD | LOAD-05 · EM-C-01 | [v0.3] Antes 10 A (prueba). LOAD-05 recoge los 5 A que menciona el TFG, sin revalidar. Es el dato que falta de EM-C-01 |
| `L_EMS_min` | Inductancia incremental mínima del EMS | 1,92 | mH | R5 | AC | LOAD-01 · EM-D-01/02 | Sección 6.1.1 |
| `L_EMS_max` | Inductancia incremental máxima del EMS | 117 | mH | R5 | AC | LOAD-01 · EM-D-01/02 | Sección 6.1.1 |
| `L_HEMS_min` | Inductancia incremental mínima del HEMS (dψ/di derivada) | 6,2 | mH | C | OK | LOAD-01 | Sección 6.1.2 (derivado del Excel R7) |
| `L_HEMS_max` | Inductancia incremental máxima del HEMS (dψ/di derivada) | 11,2 | mH | C | OK | LOAD-01 | Sección 6.1.2 |
| `L_EMS_0` | Inductancia del EMS a I = 0 (valor citado, columnas 5–6) | 26,7 | mH | R5 | AC | 6.1.1 | Solo para la cota pesimista de energía (L constante) |
| `E_EMS` | Energía devuelta al desmagnetizar el EMS desde 55 A (mapa H11) | 15,6 | J | C | AC | 6.1.3 · EM-D-03 | Mapa hasta ±55 A |
| `E_HEMS` | Energía devuelta al desmagnetizar el HEMS desde −55 A, 6 mm (mapa H11) | 16,7 | J | C | AC | 6.1.3 · EM-D-03 | Peor caso del H11. A 60 A escala por (60/55)² ≈ 1,19 → unos 20 J, que es lo que alimenta `E_fault_tot` |
| `I_map` | Corriente máxima cubierta por los mapas de inductancia | 55 | A | R7 | OK | EM-D-03 | Por debajo de `Ipk`: los 60 A hay que extrapolar hasta que llegue EM-D-03 |
| `dI_pp_max` | Rizado de corriente pico a pico máximo admisible | 1,5 | A | P | TBD | LOAD-07 · EM-C-03 | El rizado calculado en 6.1.3 para el peor caso (EMS, 20 kHz, unipolar, 400 V) es 1,30 A, así que el límite queda coherente con un 15 % de margen. Sigue pendiente el valor que imponga EM-C |
| `T_coil_max` | Temperatura máxima de la bobina (umbral de protección) | 110 | °C | P | TBD | SAF-01 · EM-D | Con la GA10K4A1IA (10 kΩ, β = 3598) a 110 °C la NTC vale 688 Ω y el divisor con `R_ntc_pu` y `V_ntc_ref` da 0,322 V: hay resolución de sobra. Falta que EM-D fije el umbral real de la bobina |

**`parametros.md` · 3. Conmutación y MOSFET**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `fsw` | Frecuencia de conmutación | 20 | kHz | TFG | TBD | PWR-03 · FW-08 | [v0.3] Antes 30 kHz (prueba). Valor de PWR-03. Pasa a ser configurable en la FPGA: FW-08 debe dar el rango que el hardware tiene que admitir |
| `Modulacion` | Modulación: «Unipolar» o «Bipolar» | Unipolar |  | TFG | TBD | PWR-03 · FW-08 | [v0.3] Antes «Bipolar» (prueba). Valor de PWR-03. Afecta al rizado de 6.1.3 |
| `t_dead` | Tiempo muerto | 100 | ns | TFG | AC | PWR-04 · FW-08 | [v0.3] Antes 120 ns (prueba). PWR-04 cita la red RC de 100 ns del TFG como punto de partida. Con el diodo de cuerpo del IMT65R010M2H a 4,3 V, conviene el mínimo compatible con `D_skew` (10 ns) más `t_dead_mrg` y los tiempos de conmutación |
| `MOSFET_sel` | Referencia del MOSFET usado en el resto de cálculos (una de las columnas de componentes.md) | IMT65R010M2H |  | U | AC | PWR-02 · HW-02 · HW-03 | Elegido por disponibilidad (stock en el taller y en distribución) frente al SCT012H90G3AG, a 25 semanas de plazo. Condicionado a resolver HW-03 |
| `D_worst` | Fracción del periodo que conduce el MOSFET más cargado | 1 |  | P | OK | SAF-05 | 1 = rueda libre permanente por los low-side (conservador). Con PWM en régimen, el más cargado conduce (1 + m)/2 |
| `Tj_assumed` | Tj supuesta para evaluar RDS(on) | 125 | °C | P | AC | — | Debe ser ≥ Tj calculada (comprobación en el apartado MOSFET) |
| `Tj_lim` | Tj máxima de diseño (criterio) | 150 | °C | P | AC | — | Margen de 25 °C sobre los 175 °C del IMT65R010M2H y del SCT012H90G3AG |
| `t_dead_mrg` | Margen adicional en el cálculo del tiempo muerto mínimo | 20 | ns | P | AC | PWR-04 | Cubre el desfase entre drivers (`D_skew` = 10 ns en el STGAP3S6S) más la dispersión de los tiempos de apagado |
| `k_vds` | Factor de utilización máximo de VDS (criterio) | 0,8 |  | HD | AC | PWR-02 · HW-03 | Hoja de datos R8: «for optimum lifetime and reliability, Infineon recommends operating conditions that do not exceed 80% of the maximum ratings». 0,8 × 650 V = 520 V |

**`parametros.md` · 4. DC-link y protección del bus**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `Cdc` | Capacidad del DC-link en placa | 105 | µF | TFG | AC | DCB-07 · HW-02 · HW-03 | Se mantiene para el rizado. Con 650 V, subirla no resuelve el caso de fallo: harían falta más de 3 mF (6.3) |
| `V_film` | Tensión nominal de los condensadores del DC-link | 630 | V | P | AC | DCB-02 · HW-02 | [v0.3] Antes 650 V (prueba); el TFG tenía 500 V, que no valen. Con el clamp actuando a `V_chop_on` la tensión máxima que ven es `V_clamp_lim` = 520 V, y 630 V es el escalón de catálogo que además cubre `V_cont` |
| `ESR_dc` | ESR equivalente del DC-link a 2·fsw | 2 | mΩ | P | TBD | HW-02 | Orden de magnitud de un banco de film con cerámicos en paralelo. Confirmar con las referencias que se elijan |
| `N_dc_abs` | Número de DC-link que absorben la energía en el caso de fallo | 1 |  | C | OK | DCB-08 · HW-03 | 1 por módulo. Aunque el bus es compartido y los 10 DC-link quedan en paralelo (1050 µF), el caso que dimensiona es el fallo común: los 10 módulos descargan a la vez, lo que equivale a 1 DC-link por módulo. El fallo de un módulo aislado sí reparte entre los 10 y llega solo a 438 V |
| `N_fault_sim` | Número de módulos que pierden la rueda libre a la vez (caso dimensionante) | 10 |  | C | AC | DCB-08 · HW-03 · EM-C-05 | Una pérdida de BT o una parada de emergencia afecta a los 10 módulos simultáneamente |
| `E_fault_tot` | Energía total a absorber en el caso de fallo común | 200 | J | C | AC | DCB-08 · DCB-09 | `N_fault_sim` × `E_HEMS` escalada a `Ipk` = 10 × 20 J. Revisar con EM-D-03 (mapas a 60 A) y EM-D-04 (bobinas nuevas) |
| `V_clamp_lim` | Tensión máxima admisible en el DC-link durante el caso de fallo | 520 | V | C | AC | HW-03 · DCB-09 | `k_vds` × VDS del MOSFET elegido. Con el SCT012H90G3AG serían 720 V |
| `V_chop_on` | Tensión de actuación del clamp o chopper | 500 | V | P | AC | HW-03 · DCB-09 | [v0.3] Antes 550 V (prueba), que está por encima de `V_clamp_lim`. Tiene que quedar entre `k_chop_mrg` × `Vbus_max` = 440 V y `V_clamp_lim` = 520 V. Se propone 500 V; la ventana es de 80 V |
| `k_chop_mrg` | Margen mínimo de V_chop_on sobre Vbus_max (criterio) | 1,1 |  | P | AC | HW-03 | 1,1 × 400 V = 440 V. Tiene que dejar pasar el rizado de `dVdc_pct` (8 V) y el umbral de `V_OV` |
| `I_fuse` | Corriente nominal del fusible en placa | 15 | A | TFG | AC | DCB-06 · HW-02 | 0ADKC9150-BE. La corriente media de bus por módulo durante el pico es 10,8 A a 400 V y 13,5 A a 320 V: el factor de utilización llega a 0,90 en el caso de 320 V, por encima de `k_fuse` |
| `V_fuse` | Tensión nominal DC del fusible | 500 | V | TFG | AC | DCB-06 · HW-02 | 0ADKC9150-BE. **No cubre `V_cont` (600 V) ni `V_chop_on` (500 V):** hay que sustituirlo en HW-02 por uno de ≥ 700 VDC |
| `k_fuse` | Factor de utilización máximo del fusible (criterio) | 0,75 |  | P | AC | DCB-06 | A 400 V el uso real es 0,72 y pasa; a 320 V es 0,90 y no pasa. Confirmar con la curva de derating del fabricante y con `Irms_cont` cuando llegue EM-C-01 |

**`parametros.md` · 5. Gate driving**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `DRIVER_sel` | Referencia del gate driver usado en el resto de cálculos (columna de componentes.md) | STGAP3S6S |  | P | AC | GD-01 · GD-05 · HW-02 | Único candidato evaluado cuyo UVLO del raíl positivo está referido a la masa aislada. Verificar stock antes de comprometer |
| `Vgs_on` | Tensión de puerta en ON | 18 | V | HD | AC | GD-01 · HW-02 | [v0.3] Antes 20 V (TFG). Es la VGS a la que están especificadas RDS(on) y Qg en las hojas de datos de los dos MOSFET candidatos. 20 V es el 87 % de la VGS máxima del IMT65R010M2H, por encima de `k_vgs` |
| `Vgs_off` | Tensión de puerta en OFF | -3 | V | P | AC | GD-01 · HW-02 | [v0.3] Antes −5 V (TFG). El IMT65R010M2H limita la VGS estática a −7 V: −3 V es el 43 % y −5 V el 71 %. Con VGS(th) típica de 4,5 V y robustez declarada a 0 V, −3 V ya da la inmunidad necesaria. Si se prefiere −5 V, también cumple `k_vgs` |
| `Vgs_on_alt` | Tensión de puerta en ON alternativa (módulo de 15 V) | 15 | V | P | TBD | AUX-02 · HW-02 | Para evaluar la penalización de RDS(on) si no se consigue un raíl de 18 V. En el SCT012H90G3AG la penalización medida es del 12 % (13,4 frente a 12 mΩ) |
| `k_vgs` | Factor de utilización máximo de VGS (criterio) | 0,8 |  | HD | AC | GD-01 | Se aplica a VGSmax y a VGSmin del MOSFET elegido. Para el IMT65R010M2H: +18,4 V y −5,6 V |
| `Rg_on` | Resistencia de puerta externa de encendido | 8 | Ω | P | AC | HW-02 · PWR-07 | [v0.3] Sigue siendo 8 Ω pero ya está justificado: con `Rgint` = 1,7 Ω y ~1 Ω del driver, la corriente de pico de puerta es 1,96 A, muy por debajo de los 6 A del STGAP3S6S. El ensayo de R8 usa 3,3 Ω: hay que reescalar Eon/Eoff a este valor |
| `Rg_off` | Resistencia de puerta externa de apagado | 8 | Ω | P | AC | HW-02 · PWR-07 | Es la palanca principal sobre la sobreoscilación de PWR-07: subirla reduce el pico de VDS al apagar a costa de más Eoff. Ajustar tras medir en la primera placa |
| `N_d_desat` | Número de diodos en serie en el circuito DESAT | 1 |  | P | AC | HW-01 · GD-07 | Un solo diodo rápido de 1000 a 1200 V cubre `V_chop_on` con margen |
| `Vf_desat` | Caída de tensión de cada diodo DESAT | 0,7 | V | P | AC | HW-01 | Valor a la corriente de polarización del DESAT (unos 0,5 mA), no a corriente nominal. Se resta del umbral, así que baja la corriente de disparo |
| `R_desat` | Resistencia serie del circuito DESAT | 1 | kΩ | P | AC | HW-01 | Valor habitual para limitar la corriente al pin DESAT durante la conmutación |
| `C_blank` | Condensador de blanking del DESAT | 47 | pF | P | AC | HW-01 | Con el umbral de 3,5 V y los 527 µA del ADuM4146 da 312 ns de enmascaramiento, coherente con los 260 a 340 ns de la hoja de datos. **El STGAP3S6S fija el blanking por otro mecanismo:** revisar cuando se cierre `DRIVER_sel` |
| `t_desat_max` | Tiempo de respuesta máximo de la protección DESAT | 2 | µs | TFG | AC | GD-01 | El STGAP3S6S interviene en 150 ns y reporta por DIAG en 2,5 µs máx.: el requisito se cumple con holgura en la intervención |
| `I_desat_max` | Corriente de disparo máxima admisible del DESAT (criterio) | 300 | A | P | AC | GD-06 · HW-01 | 5 × `Ipk`. Con 10 mΩ y umbral de 6 V el DESAT dispara a 600 A (458 A en caliente), muy por encima: por eso la sobrecorriente de bobina la tiene que cubrir `I_OC` |

**`parametros.md` · 6. Sensado**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `R_shunt` | Resistencia del shunt de corriente | 500 | µΩ | TFG | AC | SNS-01 · HW-02 | Con el AMC1302 (±50 mV lineales) da 100 A de fondo de escala y 128 A de recorte |
| `P_sh_rat` | Potencia nominal del shunt | 3 | W | P | AC | HW-02 | A `Ipk` disipa 1,8 W durante 2 s y a `Irms_cont` 12,5 mW: 3 W cubre el caso continuo con margen. Comprobar el pulso de 2 s contra la curva del fabricante |
| `I_margin` | Margen mínimo fondo de escala / Ipk (criterio) | 1,2 |  | P | AC | SNS-01 | El shunt de 500 µΩ con el AMC1302 da 100 A / 60 A = 1,67: cumple |
| `I_OC` | Umbral de sobrecorriente por hardware | 90 | A | P | AC | SAF-04 · HW-01 | 1,5 × `Ipk`, por debajo del recorte del AMC1302 (128 A). Es la protección que cubre la sobrecorriente de bobina, porque el DESAT dispara a cientos de amperios (`I_desat_max`). Necesita un comparador rápido sobre el shunt, no la cadena del AMC1302 (`Sa_td` = 3 µs) |
| `f_clk_ds` | Frecuencia de reloj de los moduladores ΔΣ | 20 | MHz | P | AC | SNS-05 · FW-01 | Por debajo de los 21 MHz máximos del AMC1306 a 5 V (`Sd_fmax`) |
| `OSR` | Relación de sobremuestreo del filtro sinc | 128 |  | P | TBD | SNS-05 · SNS-09 · FW-01 | A 20 MHz, sinc3 con OSR = 128 asienta en 19,2 µs y da 156 kHz de salida. **Con un periodo de PWM de 50 µs eso es mucha latencia para el lazo:** con OSR = 64 baja a 9,6 µs. Comparar con `t_meas_lat`; la elección depende del ancho de banda que pida EM-C-03. Solo aplica si `Sens_chain` = DeltaSigma |
| `N_sinc` | Orden del filtro sinc | 3 |  | P | AC | FW-01 | sinc3 es el habitual con moduladores de 2.º orden |
| `N_adc` | Resolución del ADC (opción amplificador aislado + ADC) | 12 | bit | P | TBD | SNS-05 · FW-01 | Solo aplica si `Sens_chain` = AmpAislado. Con 100 A de fondo de escala, 12 bits dan 24 mA de cuantificación. **[v0.4]** En esa vía el ADC puede ser el interno del controlador: lo que decide no es dónde está el ADC sino qué cruza la barrera (6.6.3 del documento de requisitos) |
| `t_meas_lat` | Latencia máxima admisible de la cadena de medida de corriente | 10 | µs | P | TBD | SNS-09 · EM-C-03 | **[v0.4]** PROVISIONAL. Un 20 % del periodo de PWM (50 µs a `fsw` = 20 kHz). Con sinc3 y `OSR` = 128 el asentamiento es 19,2 µs y **no cabe**; con `OSR` = 64 son 9,6 µs y sí. Por la vía del amplificador aislado son centenas de ns. El valor real lo fija EM-C-03 |
| `V_meas_FS` | Fondo de escala deseado de la medida de Vbus | 700 | V | P | AC | SNS-02 | Cubre `V_chop_on` (500 V) y `V_clamp_lim` (520 V) con margen, y el fallo de un módulo aislado (438 V) |
| `V_sens_FS` | Entrada lineal del sensor aislado de Vbus | 0,25 | V | HD | AC | SNS-02 · HW-02 | AMC1306x25: ±250 mV |
| `R_sens_in` | Impedancia de entrada del sensor de Vbus | 22 | kΩ | HD | AC | HW-02 | AMC1306x25: 22 kΩ diferencial |
| `R_div_bot` | Resistencia inferior del divisor de Vbus | 1 | kΩ | P | AC | SNS-02 | Con `V_meas_FS` / `V_sens_FS` = 2800:1 sale una rama superior de 2,799 MΩ. A 400 V el divisor consume 143 µA y 57 mW en total; 1 kΩ queda muy por debajo de los 22 kΩ de entrada del sensor, así que la carga es despreciable |
| `V_res_rat` | Tensión máxima de trabajo de cada resistencia del divisor | 200 | V | P | AC | HW-02 | Con 4 resistencias en serie en la rama superior, cada una ve 130 V en el peor caso de 520 V: cumple |
| `P_res_rat` | Potencia nominal de cada resistencia del divisor | 0,25 | W | P | AC | HW-02 | Cada una disipa 24 mW a 520 V, un 10 % de su nominal: cumple `k_res` con holgura |
| `k_res` | Factor de utilización de potencia de las resistencias (criterio) | 0,5 |  | P | AC | — |  |
| `V_OV` | Umbral de sobretensión de bus por hardware | 450 | V | P | AC | SAF-01 · HW-01 | [v0.3] Antes 420 V (prueba), solo 20 V por encima de `Vbus_max` y expuesto a falsos disparos. 450 V deja 42 V sobre el bus más el rizado de 8 V, y queda por debajo de `V_chop_on` (500 V) |
| `NTC_R25` | Resistencia de la NTC a 25 °C | 10 | kΩ | TFG | AC | LOAD-08 · HW-02 | GA10K4A1IA (TE) |
| `NTC_beta` | Constante β(25/85) de la NTC | 3598 | K | TE | AC | LOAD-08 | Página de producto TE; contrastar con la tabla R-T |
| `R_ntc_pu` | Resistencia de polarización de la NTC | 10 | kΩ | P | AC | SNS-03 | Igual a `NTC_R25`, que centra el divisor a 25 °C (2,5 V). En `T_coil_max` (110 °C) da 0,322 V: hay resolución suficiente en todo el rango útil |
| `V_ntc_ref` | Tensión de referencia del divisor de la NTC | 5 | V | P | AC | SNS-03 | Coherente con la alimentación de 5 V del lado HV del AMC1306 |

**`parametros.md` · 7. Refrigeración y entorno**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `T_amb` | Temperatura ambiente máxima | 50 | °C | P | TBD | MEC-06 · ME-C-02 | PROVISIONAL. El TFG asumía ≥ 25 °C por competir en verano; 50 °C es una hipótesis conservadora |
| `T_cool` | Temperatura del refrigerante a la entrada | 50 | °C | P | TBD | ME-C-02 | PROVISIONAL. Depende del acumulador de PCM, que está fuera del alcance |
| `Q_cool` | Caudal de refrigerante | 2 | L/min | P | TBD | ME-C-02 | PROVISIONAL. |
| `N_cool_ser` | Placas en serie en el circuito de agua (la última es la peor) | 1 |  | P | TBD | ME-C-01 · ME-C-02 | PROVISIONAL. Con 10 placas en serie la última vería un salto de temperatura del agua muy distinto |
| `Rth_wb` | Resistencia térmica cara inferior de la PCB → agua, por MOSFET | 0,3 | K/W | P | TBD | PWR-06 · ME-C-01 | PROVISIONAL. Es el término dominante: con `Rthjc` = 0,22 K/W y 36 W por dispositivo durante el pico, la unión sube solo 8 K sobre la cápsula |
| `t_TIM` | Espesor del material de interfaz térmica | 0,5 | mm | P | AC | ME-C-01 | Espesor habitual de un gap pad que absorbe la tolerancia de planitud del waterblock |
| `k_TIM` | Conductividad del material de interfaz térmica | 3 | W/(m·K) | P | AC | ME-C-01 | Gama media de los gap pads comerciales |
| `V_TIM_bd` | Rigidez dieléctrica del material de interfaz (tensión de ruptura) | 4000 | V | P | AC | ISO-04 · ME-C-01 | El pad de drenador está en HV en los dos candidatos de MOSFET. 4000 V sobre 0,5 mm cubre `V_cont` con factor 6,7 |
| `k_spread` | Área efectiva bajo el TIM / área del pad (ensanchamiento) | 2 |  | P | TBD | — | PROVISIONAL. Depende del cobre de la cara inferior; confirmar con una simulación o una medida |
| `A_pad` | Área del pad de drenador del MOSFET | 70 | mm² | HD | AC | HW-02 | [v0.3] Antes 80 mm² referido al H²PAK-7. El PG-HSOF-8 (TOLL) tiene cuerpo de 9,9 × 11,68 mm y el pad de drenador ocupa del orden de 70 mm². Confirmar con el footprint del fabricante |
| `d_via` | Diámetro de taladro de las vías térmicas | 0,3 | mm | P | AC | PT-01 | Taladro estándar sin coste añadido en 6 capas |
| `t_plat` | Espesor del metalizado de las vías | 25 | µm | P | AC | PT-01 | Valor de clase 2 habitual; confirmar con PT-01 |
| `N_via` | Número de vías térmicas bajo cada MOSFET | 36 |  | P | AC | ME-C-01 | [v0.3] Antes 10. En 70 mm² caben unas 48 posiciones a paso de 1,2 mm; se dejan 36 (matriz 6 × 6) para reservar sitio al reparto de pasta y evitar el vaciado de soldadura |
| `t_solder` | Espesor de la soldadura bajo el pad | 0,1 | mm | P | AC | PT-02 | Espesor típico tras reflujo de un encapsulado sin patillas |
| `k_solder` | Conductividad de la soldadura | 50 | W/(m·K) | HD | AC | — | Orden de magnitud de aleaciones SAC |
| `k_Cu` | Conductividad del cobre | 385 | W/(m·K) | — | OK | — | Valor físico |
| `k_FR4` | Conductividad del FR-4 en el eje z | 0,3 | W/(m·K) | — | AC | PT-01 | Orden de magnitud; confirmar con el laminado |

**`parametros.md` · 8. PCB: stackup, pistas y aislamiento**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `t_pcb` | Espesor total de la PCB | 1,6 | mm | P | AC | MEC-03 · PT-01 | Espesor estándar compatible con 6 capas de 2 oz |
| `oz_ext` | Cobre en capas externas | 2 | oz | TFG | AC | MEC-03 · PT-01 | 1 oz ≈ 35 µm |
| `oz_int` | Cobre en capas internas | 2 | oz | TFG | AC | MEC-03 · PT-01 | MEC-03 indica 2 oz sin distinguir capas |
| `dT_trace` | Incremento de temperatura admisible en pistas (criterio) | 30 | °C | P | AC | — |  |
| `er_pcb` | Permitividad relativa del dieléctrico | 4,5 |  | P | AC | PT-01 | FR-4 estándar a la frecuencia de la interfaz del PHY |
| `h_ms` | Dieléctrico entre capa externa y su plano de referencia (microstrip) | 0,2 | mm | P | AC | PT-01 | Coherente con un stackup simétrico de 6 capas y 1,6 mm |
| `b_sl` | Distancia entre planos de referencia de la stripline | 0,5 | mm | P | AC | PT-01 | Ídem |
| `tol_Z` | Tolerancia admisible de impedancia (criterio) | 10 | % | P | AC | PT-01 | Tolerancia habitual de fabricación; confirmar con el fabricante |
| `Ins_type` | Tipo de aislamiento HV–BT: «Básico» o «Reforzado» | Básico |  | P | TBD | ISO-05 · HW-04 | PROVISIONAL. Si se pide reforzado, comparar VIORM: STGAP3S 1,2 kV pico frente a ADuM4146 2,15 kV pico |
| `PD_coat` | Grado de contaminación bajo el coating (IEC 60664-3) | 1 |  | P | AC | ISO-02 · HW-04 |  |
| `PD_bare` | Grado de contaminación en superficies sin coating | 2 |  | P | AC | HW-04 | Grado habitual para un entorno cerrado no estanco |
| `d_HV_LV` | Separación mínima HV–BT con coating (regla de la competición) | 4 | mm | U | OK | ISO-02 |  |
| `d_HV_HV` | Separación mínima entre redes de HV | 2 | mm | TFG | AC | ISO-03 · HW-04 |  |
| `d_WB` | Separación mínima taladros del waterblock – conductores | 4 | mm | TFG | AC | ISO-04 · ME-C-01 |  |
| `L_loop` | Inductancia parásita objetivo del lazo de conmutación | 15 | nH | P | TBD | PWR-07 · HW-02 | Con 15 nH y 4 A/ns la sobreoscilación es de 60 V: 460 V de pico, el 71 % de los 650 V. Con 25 nH sube a 500 V, el 77 %. Es el parámetro que decide si hacen falta snubbers, y solo se sabrá al medir |

**`parametros.md` · 9. Alimentación auxiliar (BT)**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `V_BT_max` | Tensión máxima de la batería de BT | 24 | V | U | OK | AUX-01 |  |
| `V_BT_min` | Tensión mínima de la batería de BT | 18 | V | P | TBD | AUX-03 · ME-I-02 | PROVISIONAL. Corresponde al final de descarga de un pack nominal de 24 V; lo tiene que confirmar ME-I-02 |
| `P_BT_lim` | Consumo máximo permitido por placa | 15 | W | P | TBD | AUX-03 · ME-I-02 | PROVISIONAL. Es un límite que impone ME-I-02, no el consumo estimado. Las cuatro fuentes de puerta solo piden 0,8 W en secundario, 1,1 W en primario con `G_eta` = 74 % |
| `eta_BT` | Rendimiento de la etapa de entrada BT | 85 | % | P | TBD | AUX-02 · HW-05 | PROVISIONAL. Depende de la topología que se elija en ME-I-02 |
| `P_margin` | Margen sobre el consumo total estimado (criterio) | 20 | % | P | AC | — |  |

**`parametros.md` · 10. Integridad de señal: presupuesto de tiempos (interfaz MII/RMII u otra síncrona)**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `f_bus_clk` | Frecuencia de reloj de la interfaz controlador–PHY | 50 | MHz | P | TBD | COM-02 · FW-06 | RMII: 50 MHz; MII: 25 MHz. Se toma el caso más exigente. **[v0.4]** Los ESC integrados en microcontrolador usan MII, así que por esa vía serían 25 MHz |
| `tco_max` | Retardo de salida máximo del emisor (clock-to-out) | 10 | ns | P | TBD | FW-06 | PROVISIONAL. Hoja de datos del PHY / FPGA |
| `tco_min` | Retardo de salida mínimo del emisor | 2 | ns | P | TBD | FW-06 | PROVISIONAL. |
| `t_su` | Tiempo de setup del receptor | 4 | ns | P | TBD | FW-06 | PROVISIONAL. |
| `t_h` | Tiempo de hold del receptor | 2 | ns | P | TBD | FW-06 | PROVISIONAL. |
| `t_jit` | Jitter y otras incertidumbres del reloj | 0,5 | ns | P | TBD | FW-06 | PROVISIONAL. |
| `dL_clk` | Diferencia de longitud del reloj entre emisor y receptor | 10 | mm | P | TBD | — | PROVISIONAL |
| `skew_pair` | Desfase admisible dentro de un par diferencial | 5 | ps | P | TBD | COM-03 | PROVISIONAL. Criterio del fabricante del PHY o de los magnéticos |
| `SI_if_datos` | Interfaz de datos usada en el presupuesto de tiempos (clave de diseno.md) | datos_phy |  | P | TBD | COM-02 · FW-06 |  |
| `SI_if_reloj` | Interfaz de reloj usada en el presupuesto de tiempos (clave de diseno.md) | reloj_phy |  | P | TBD | COM-02 · FW-06 |  |
| `SI_if_par` | Par diferencial usado para la igualación de longitudes (clave de diseno.md) | mdi_in |  | P | TBD | COM-03 |  |

**`parametros.md` · 11. Plataforma de control y bus de campo (FW-09)**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `Ctrl_plat` | Plataforma de control: «FPGA» o «MCU» | FPGA |  | P | TBD | CTL-01 · FW-09 | PROVISIONAL. Hipótesis heredada de la v0.3, ya no es un dato de partida. Candidatos MCU con ESC integrado en 6.6.1: XMC4800/4300, RX72M, C2000 F28P65x y F2838x |
| `ESC_impl` | Implementación del esclavo EtherCAT: «IPcore», «ESCext» o «ESCint» | IPcore |  | P | TBD | COM-02 · FW-06 · FW-09 | PROVISIONAL. `ESCext` (LAN9252) y `ESCint` evitan la licencia del IP core de Beckhoff; las tres vías siguen necesitando el Slave Stack Code por vía ETG. Decide el valor de `N_phy_ext` y si aplica la sección 10 |
| `N_ecat_port` | Puertos EtherCAT montados por placa | 2 |  | P | OK | COM-03 · SYS-01 | El ESC trae 2 o 3 puertos dentro; lo que obliga a montar dos en las 10 placas es SYS-01, no el ESC. En la última de la línea la salida queda sin usar, salvo con `Ring_red` = Si |
| `N_phy_ext` | PHY Ethernet externos por placa | 2 |  | P | AC | COM-03 · COM-02 | 2 con `ESC_impl` = IPcore o ESCint; **0 con ESCext**, porque el LAN9252 los lleva dentro. Es el coste real de la topología, no los puertos |
| `Ring_red` | Redundancia en anillo del bus: «Si» o «No» | No |  | P | TBD | COM-07 · FW-06 | PROVISIONAL. Un esclavo sin BT abre la línea y deja fuera a los de aguas abajo. El anillo cuesta un cable de vuelta a un 2.º puerto de la VCU y hace el bus inmune a un corte en cualquier punto |
| `Addr_mode` | Identificación de posición: «AutoIncr», «EEPROM» o «Selector» | AutoIncr |  | P | TBD | COM-08 · CTL-06 · ME-I-06 | PROVISIONAL. El direccionamiento auto-incremental da la posición en la línea sin hardware adicional, si el orden del cableado es fijo y está documentado. Es la vía más barata con placa única |
| `Sens_chain` | Cadena de sensado de corriente: «DeltaSigma» o «AmpAislado» | DeltaSigma |  | P | TBD | SNS-05 · FW-01 · FW-09 | PROVISIONAL. Hipótesis de la opción A. La decisión no es ADC interno o externo, sino qué cruza la barrera (6.6.3). `DeltaSigma` exige un periférico SDFM/DFSDM en la plataforma y cuesta latencia (`t_meas_lat`); `AmpAislado` vale con cualquier ADC pero es más sensible al ruido de conmutación |
| `N_ch_ds` | Canales ΔΣ necesarios en el controlador | 1 |  | P | AC | SNS-07 · FW-01 | Solo la corriente necesita el camino rápido: `Vbus` y la NTC admiten amplificador aislado más ADC. Todos los candidatos de 6.6.1 tienen 4 o más canales, así que este parámetro no discrimina |
| `t_trip_hw` | Tiempo de reacción objetivo del disparo por hardware del controlador | 1 | µs | P | AC | CTL-08 · HW-01 | Criterio C3 de 5.4. No sustituye a la lógica cableada independiente de SAF-02: es la segunda capa, dentro del propio controlador |

**`componentes.md` · 2. Gate driver: candidatos**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `D_Isrc` | Corriente de cortocircuito de fuente | 11 | A | ADI | OK | GD-01 |  |
| `D_Isnk` | Corriente de cortocircuito de sumidero | 9 | A | ADI | OK | GD-01 |  |
| `D_Rp` | RDS(on) del PMOS de salida (máx.) | 0,975 | Ω | ADI | OK | GD-01 |  |
| `D_Rn` | RDS(on) del NMOS de salida (máx.) | 0,807 | Ω | ADI | OK | GD-01 |  |
| `D_skew` | Desfase de propagación entre dispositivos (máx.) | 25 | ns | ADI | OK | PWR-04 |  |
| `D_desat` | Umbral DESAT (grado B) | 9,2 | V | ADI | OK | GD-01 | Grados A y C: 3,5 V sin fuente de corriente interna |
| `D_Idesat` | Corriente de carga DESAT (grado B, típ.) | 527 | µA | ADI | OK | GD-01 |  |
| `D_mask` | Tiempo de enmascaramiento DESAT (máx.) | 340 | ns | ADI | OK | GD-01 | 260 a 340 ns |
| `D_Rclamp` | Resistencia del Miller clamp (máx.) | 2,75 | Ω | ADI | OK | GD-01 |  |
| `D_CMTI` | CMTI | 100 | kV/µs | ADI | OK | GD-01 |  |
| `D_IDD2` | Corriente de VDD2 (máx.) | 6,5 | mA | ADI | OK | AUX-02 |  |
| `D_UVLO` | UVLO de VDD2, umbral de subida (grados B/C) | 11,5 | V | ADI | AC | GD-02 | Grado A: 14,5 V. Grado del TFG por confirmar |

**`componentes.md` · 3. Fuente aislada de puerta: candidatos**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `G_Vin` | Tensión de entrada nominal | 5 | V | Murata | OK | AUX-02 | 4,5 a 5,5 V |
| `G_P` | Potencia nominal | 2 | W | Murata | OK | GD-01 |  |
| `G_eta` | Rendimiento mínimo a plena carga | 74 | % | Murata | OK | AUX-02 | Típ. 78,5 % |
| `G_Ipos` | Corriente máxima de la salida +20 V | 80 | mA | Murata | OK | GD-01 |  |
| `G_Ineg` | Corriente máxima de la salida −5 V | 40 | mA | Murata | OK | GD-01 |  |
| `G_CMTI` | CMTI | 200 | kV/µs | Murata | OK | GD-01 | > 200 kV/µs |

**`componentes.md` · 4. Sensores aislados: candidatos**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `Sa_Vlin` | AMC1302: entrada diferencial lineal | 50 | mV | TI | OK | SNS-01 | ±50 mV |
| `Sa_Vclip` | AMC1302: entrada de recorte | 64 | mV | TI | OK | SNS-01 | ±64 mV |
| `Sa_G` | AMC1302: ganancia fija | 41 |  | TI | OK | SNS-01 |  |
| `Sa_BW` | AMC1302: ancho de banda (mínimo) | 220 | kHz | TI | OK | SNS-05 | 220 a 280 kHz |
| `Sa_td` | AMC1302: retardo de señal 50–90 % (máximo) | 3 | µs | TI | OK | SNS-05 |  |
| `Sd_Vlin` | AMC1306x05: entrada diferencial lineal | 50 | mV | TI | OK | SNS-01 | x25: ±250 mV |
| `Sd_fmin` | AMC1306: frecuencia de reloj mínima | 5 | MHz | TI | OK | FW-01 |  |
| `Sd_fmax` | AMC1306: frecuencia de reloj máxima | 21 | MHz | TI | OK | FW-01 | A 5 V |
| `Sd_ENOB` | AMC1306: ENOB con sinc3 y OSR = 256 | 14 | bit | TI | AC | FW-01 | ≈ 14 bits; con otro OSR es distinto |
| `S_CMTI` | CMTI mínimo de los sensores aislados | 100 | kV/µs | TI | OK | SNS-01 | AMC1302: 100 kV/µs mín.; AMC1306: 100 kV/µs típ. |

**`componentes.md` · 6. EtherCAT P: candidatos**

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---|---|---|---|---|
| `ECP_V` | Tensión de alimentación de EtherCAT P | 24 | V | Beckhoff | OK | AUX-01 |  |
| `ECP_Imax` | Corriente máxima por alimentación (US o UP) | 3 | A | Beckhoff | OK | AUX-01 | Solo aplica si se elige EtherCAT P (ME-I-02) |

## Anexo C. Parámetros pendientes

Parámetros en estado TBD (valor provisional) y AC (a confirmar), con la cuestión que los resolverá.

| Estado | Nombre | Descripción | Valor provisional | Requisito / pendiente |
|---|---|---|---|---|
| TBD | `Irms_cont` | Corriente eficaz en régimen permanente (dimensionado térmico) | 5 A | LOAD-05 · EM-C-01 |
| TBD | `dI_pp_max` | Rizado de corriente pico a pico máximo admisible | 1,5 A | LOAD-07 · EM-C-03 |
| TBD | `T_coil_max` | Temperatura máxima de la bobina (umbral de protección) | 110 °C | SAF-01 · EM-D |
| TBD | `fsw` | Frecuencia de conmutación | 20 kHz | PWR-03 · FW-08 |
| TBD | `Modulacion` | Modulación: «Unipolar» o «Bipolar» | Unipolar | PWR-03 · FW-08 |
| TBD | `ESR_dc` | ESR equivalente del DC-link a 2·fsw | 2 mΩ | HW-02 |
| TBD | `Vgs_on_alt` | Tensión de puerta en ON alternativa (módulo de 15 V) | 15 V | AUX-02 · HW-02 |
| TBD | `OSR` | Relación de sobremuestreo del filtro sinc | 128 | SNS-05 · SNS-09 · FW-01 |
| TBD | `N_adc` | Resolución del ADC (opción amplificador aislado + ADC) | 12 bit | SNS-05 · FW-01 |
| TBD | `t_meas_lat` | Latencia máxima admisible de la cadena de medida de corriente | 10 µs | SNS-09 · EM-C-03 |
| TBD | `T_amb` | Temperatura ambiente máxima | 50 °C | MEC-06 · ME-C-02 |
| TBD | `T_cool` | Temperatura del refrigerante a la entrada | 50 °C | ME-C-02 |
| TBD | `Q_cool` | Caudal de refrigerante | 2 L/min | ME-C-02 |
| TBD | `N_cool_ser` | Placas en serie en el circuito de agua (la última es la peor) | 1 | ME-C-01 · ME-C-02 |
| TBD | `Rth_wb` | Resistencia térmica cara inferior de la PCB → agua, por MOSFET | 0,3 K/W | PWR-06 · ME-C-01 |
| TBD | `k_spread` | Área efectiva bajo el TIM / área del pad (ensanchamiento) | 2 | — |
| TBD | `Ins_type` | Tipo de aislamiento HV–BT: «Básico» o «Reforzado» | Básico | ISO-05 · HW-04 |
| TBD | `L_loop` | Inductancia parásita objetivo del lazo de conmutación | 15 nH | PWR-07 · HW-02 |
| TBD | `V_BT_min` | Tensión mínima de la batería de BT | 18 V | AUX-03 · ME-I-02 |
| TBD | `P_BT_lim` | Consumo máximo permitido por placa | 15 W | AUX-03 · ME-I-02 |
| TBD | `eta_BT` | Rendimiento de la etapa de entrada BT | 85 % | AUX-02 · HW-05 |
| TBD | `f_bus_clk` | Frecuencia de reloj de la interfaz controlador–PHY | 50 MHz | COM-02 · FW-06 |
| TBD | `tco_max` | Retardo de salida máximo del emisor (clock-to-out) | 10 ns | FW-06 |
| TBD | `tco_min` | Retardo de salida mínimo del emisor | 2 ns | FW-06 |
| TBD | `t_su` | Tiempo de setup del receptor | 4 ns | FW-06 |
| TBD | `t_h` | Tiempo de hold del receptor | 2 ns | FW-06 |
| TBD | `t_jit` | Jitter y otras incertidumbres del reloj | 0,5 ns | FW-06 |
| TBD | `dL_clk` | Diferencia de longitud del reloj entre emisor y receptor | 10 mm | — |
| TBD | `skew_pair` | Desfase admisible dentro de un par diferencial | 5 ps | COM-03 |
| TBD | `SI_if_datos` | Interfaz de datos usada en el presupuesto de tiempos (clave de diseno.md) | datos_phy | COM-02 · FW-06 |
| TBD | `SI_if_reloj` | Interfaz de reloj usada en el presupuesto de tiempos (clave de diseno.md) | reloj_phy | COM-02 · FW-06 |
| TBD | `SI_if_par` | Par diferencial usado para la igualación de longitudes (clave de diseno.md) | mdi_in | COM-03 |
| TBD | `Ctrl_plat` | Plataforma de control: «FPGA» o «MCU» | FPGA | CTL-01 · FW-09 |
| TBD | `ESC_impl` | Implementación del esclavo EtherCAT: «IPcore», «ESCext» o «ESCint» | IPcore | COM-02 · FW-06 · FW-09 |
| TBD | `Ring_red` | Redundancia en anillo del bus: «Si» o «No» | No | COM-07 · FW-06 |
| TBD | `Addr_mode` | Identificación de posición: «AutoIncr», «EEPROM» o «Selector» | AutoIncr | COM-08 · CTL-06 · ME-I-06 |
| TBD | `Sens_chain` | Cadena de sensado de corriente: «DeltaSigma» o «AmpAislado» | DeltaSigma | SNS-05 · FW-01 · FW-09 |
| AC | `Bus_topo` | Distribución del bus: «Encadenado» o «Estrella» | Estrella | DCB-05 · ME-I-03 · EM-C-05 |
| AC | `dVdc_pct` | Rizado máximo de tensión en el DC-link (fracción de Vbus_min) | 2 % | DCB-07 · HW-02 |
| AC | `eta_pwr` | Rendimiento de la etapa de potencia (para la corriente media de bus) | 97 % | — |
| AC | `L_EMS_min` | Inductancia incremental mínima del EMS | 1,92 mH | LOAD-01 · EM-D-01/02 |
| AC | `L_EMS_max` | Inductancia incremental máxima del EMS | 117 mH | LOAD-01 · EM-D-01/02 |
| AC | `L_EMS_0` | Inductancia del EMS a I = 0 (valor citado, columnas 5–6) | 26,7 mH | 6.1.1 |
| AC | `E_EMS` | Energía devuelta al desmagnetizar el EMS desde 55 A (mapa H11) | 15,6 J | 6.1.3 · EM-D-03 |
| AC | `E_HEMS` | Energía devuelta al desmagnetizar el HEMS desde −55 A, 6 mm (mapa H11) | 16,7 J | 6.1.3 · EM-D-03 |
| AC | `t_dead` | Tiempo muerto | 100 ns | PWR-04 · FW-08 |
| AC | `MOSFET_sel` | Referencia del MOSFET usado en el resto de cálculos (una de las columnas de componentes.md) | IMT65R010M2H | PWR-02 · HW-02 · HW-03 |
| AC | `Tj_assumed` | Tj supuesta para evaluar RDS(on) | 125 °C | — |
| AC | `Tj_lim` | Tj máxima de diseño (criterio) | 150 °C | — |
| AC | `t_dead_mrg` | Margen adicional en el cálculo del tiempo muerto mínimo | 20 ns | PWR-04 |
| AC | `k_vds` | Factor de utilización máximo de VDS (criterio) | 0,8 | PWR-02 · HW-03 |
| AC | `Cdc` | Capacidad del DC-link en placa | 105 µF | DCB-07 · HW-02 · HW-03 |
| AC | `V_film` | Tensión nominal de los condensadores del DC-link | 630 V | DCB-02 · HW-02 |
| AC | `N_fault_sim` | Número de módulos que pierden la rueda libre a la vez (caso dimensionante) | 10 | DCB-08 · HW-03 · EM-C-05 |
| AC | `E_fault_tot` | Energía total a absorber en el caso de fallo común | 200 J | DCB-08 · DCB-09 |
| AC | `V_clamp_lim` | Tensión máxima admisible en el DC-link durante el caso de fallo | 520 V | HW-03 · DCB-09 |
| AC | `V_chop_on` | Tensión de actuación del clamp o chopper | 500 V | HW-03 · DCB-09 |
| AC | `k_chop_mrg` | Margen mínimo de V_chop_on sobre Vbus_max (criterio) | 1,1 | HW-03 |
| AC | `I_fuse` | Corriente nominal del fusible en placa | 15 A | DCB-06 · HW-02 |
| AC | `V_fuse` | Tensión nominal DC del fusible | 500 V | DCB-06 · HW-02 |
| AC | `k_fuse` | Factor de utilización máximo del fusible (criterio) | 0,75 | DCB-06 |
| AC | `DRIVER_sel` | Referencia del gate driver usado en el resto de cálculos (columna de componentes.md) | STGAP3S6S | GD-01 · GD-05 · HW-02 |
| AC | `Vgs_on` | Tensión de puerta en ON | 18 V | GD-01 · HW-02 |
| AC | `Vgs_off` | Tensión de puerta en OFF | -3 V | GD-01 · HW-02 |
| AC | `k_vgs` | Factor de utilización máximo de VGS (criterio) | 0,8 | GD-01 |
| AC | `Rg_on` | Resistencia de puerta externa de encendido | 8 Ω | HW-02 · PWR-07 |
| AC | `Rg_off` | Resistencia de puerta externa de apagado | 8 Ω | HW-02 · PWR-07 |
| AC | `N_d_desat` | Número de diodos en serie en el circuito DESAT | 1 | HW-01 · GD-07 |
| AC | `Vf_desat` | Caída de tensión de cada diodo DESAT | 0,7 V | HW-01 |
| AC | `R_desat` | Resistencia serie del circuito DESAT | 1 kΩ | HW-01 |
| AC | `C_blank` | Condensador de blanking del DESAT | 47 pF | HW-01 |
| AC | `t_desat_max` | Tiempo de respuesta máximo de la protección DESAT | 2 µs | GD-01 |
| AC | `I_desat_max` | Corriente de disparo máxima admisible del DESAT (criterio) | 300 A | GD-06 · HW-01 |
| AC | `R_shunt` | Resistencia del shunt de corriente | 500 µΩ | SNS-01 · HW-02 |
| AC | `P_sh_rat` | Potencia nominal del shunt | 3 W | HW-02 |
| AC | `I_margin` | Margen mínimo fondo de escala / Ipk (criterio) | 1,2 | SNS-01 |
| AC | `I_OC` | Umbral de sobrecorriente por hardware | 90 A | SAF-04 · HW-01 |
| AC | `f_clk_ds` | Frecuencia de reloj de los moduladores ΔΣ | 20 MHz | SNS-05 · FW-01 |
| AC | `N_sinc` | Orden del filtro sinc | 3 | FW-01 |
| AC | `V_meas_FS` | Fondo de escala deseado de la medida de Vbus | 700 V | SNS-02 |
| AC | `V_sens_FS` | Entrada lineal del sensor aislado de Vbus | 0,25 V | SNS-02 · HW-02 |
| AC | `R_sens_in` | Impedancia de entrada del sensor de Vbus | 22 kΩ | HW-02 |
| AC | `R_div_bot` | Resistencia inferior del divisor de Vbus | 1 kΩ | SNS-02 |
| AC | `V_res_rat` | Tensión máxima de trabajo de cada resistencia del divisor | 200 V | HW-02 |
| AC | `P_res_rat` | Potencia nominal de cada resistencia del divisor | 0,25 W | HW-02 |
| AC | `k_res` | Factor de utilización de potencia de las resistencias (criterio) | 0,5 | — |
| AC | `V_OV` | Umbral de sobretensión de bus por hardware | 450 V | SAF-01 · HW-01 |
| AC | `NTC_R25` | Resistencia de la NTC a 25 °C | 10 kΩ | LOAD-08 · HW-02 |
| AC | `NTC_beta` | Constante β(25/85) de la NTC | 3598 K | LOAD-08 |
| AC | `R_ntc_pu` | Resistencia de polarización de la NTC | 10 kΩ | SNS-03 |
| AC | `V_ntc_ref` | Tensión de referencia del divisor de la NTC | 5 V | SNS-03 |
| AC | `t_TIM` | Espesor del material de interfaz térmica | 0,5 mm | ME-C-01 |
| AC | `k_TIM` | Conductividad del material de interfaz térmica | 3 W/(m·K) | ME-C-01 |
| AC | `V_TIM_bd` | Rigidez dieléctrica del material de interfaz (tensión de ruptura) | 4000 V | ISO-04 · ME-C-01 |
| AC | `A_pad` | Área del pad de drenador del MOSFET | 70 mm² | HW-02 |
| AC | `d_via` | Diámetro de taladro de las vías térmicas | 0,3 mm | PT-01 |
| AC | `t_plat` | Espesor del metalizado de las vías | 25 µm | PT-01 |
| AC | `N_via` | Número de vías térmicas bajo cada MOSFET | 36 | ME-C-01 |
| AC | `t_solder` | Espesor de la soldadura bajo el pad | 0,1 mm | PT-02 |
| AC | `k_solder` | Conductividad de la soldadura | 50 W/(m·K) | — |
| AC | `k_FR4` | Conductividad del FR-4 en el eje z | 0,3 W/(m·K) | PT-01 |
| AC | `t_pcb` | Espesor total de la PCB | 1,6 mm | MEC-03 · PT-01 |
| AC | `oz_ext` | Cobre en capas externas | 2 oz | MEC-03 · PT-01 |
| AC | `oz_int` | Cobre en capas internas | 2 oz | MEC-03 · PT-01 |
| AC | `dT_trace` | Incremento de temperatura admisible en pistas (criterio) | 30 °C | — |
| AC | `er_pcb` | Permitividad relativa del dieléctrico | 4,5 | PT-01 |
| AC | `h_ms` | Dieléctrico entre capa externa y su plano de referencia (microstrip) | 0,2 mm | PT-01 |
| AC | `b_sl` | Distancia entre planos de referencia de la stripline | 0,5 mm | PT-01 |
| AC | `tol_Z` | Tolerancia admisible de impedancia (criterio) | 10 % | PT-01 |
| AC | `PD_coat` | Grado de contaminación bajo el coating (IEC 60664-3) | 1 | ISO-02 · HW-04 |
| AC | `PD_bare` | Grado de contaminación en superficies sin coating | 2 | HW-04 |
| AC | `d_HV_HV` | Separación mínima entre redes de HV | 2 mm | ISO-03 · HW-04 |
| AC | `d_WB` | Separación mínima taladros del waterblock – conductores | 4 mm | ISO-04 · ME-C-01 |
| AC | `P_margin` | Margen sobre el consumo total estimado (criterio) | 20 % | — |
| AC | `N_phy_ext` | PHY Ethernet externos por placa | 2 | COM-03 · COM-02 |
| AC | `N_ch_ds` | Canales ΔΣ necesarios en el controlador | 1 | SNS-07 · FW-01 |
| AC | `t_trip_hw` | Tiempo de reacción objetivo del disparo por hardware del controlador | 1 µs | CTL-08 · HW-01 |
| AC | `D_UVLO` | UVLO de VDD2, umbral de subida (grados B/C) | 11,5 V | GD-02 |
| AC | `Sd_ENOB` | AMC1306: ENOB con sinc3 y OSR = 256 | 14 bit | FW-01 |
