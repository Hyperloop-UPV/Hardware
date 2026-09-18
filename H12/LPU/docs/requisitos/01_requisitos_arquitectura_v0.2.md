# Magnet Driver Abejorro
**Convertidor DC/DC en puente en H con control local en FPGA**
## Documento de requisitos y arquitectura: borrador v0.2

| Campo | Valor |
|---|---|
| Módulo | **Magnet Driver Abejorro**: primera generación con control local en FPGA. Sustituye a la LPU (ver sección 8). |
| Versión | 0.2 (borrador de trabajo) |
| Fecha | 17/09/2026 |
| Estado | Incompleto: contiene requisitos por confirmar y huecos (TBD) |

### Convenciones

- **Fuente de cada requisito:**
  - **[U]**: lo ha indicado el equipo (16 y 17/09/2026).
  - **[TFG]**: se hereda del TFG de L. Navarro (2025/26) y no está revalidado.
  - **[C]**: sale de un cálculo de la sección 6.
  - **[P]**: es una propuesta de este documento y está pendiente de aprobación.
- **Estado de cada requisito:**
  - **OK**: confirmado.
  - **AC**: a confirmar.
  - **TBD**: valor desconocido. Entre paréntesis se indica la cuestión pendiente de la sección 7 que lo resolverá.
- **Códigos de subsistema** (sección 7): EM-C (Electromagnetics-Control), EM-D (Electromagnetics-Design), ME-C (Mechanics-Cooling), ME-I (Mechanics-Electrical Integration), FW (Firmware), HW (Hardware) y PT (Partners).
- **Siglas de los electroimanes:** HEMS es el electroimán híbrido de levitación (4 unidades). EMS es el electroimán de guiado lateral (6 unidades).

---

## 1. Objeto y alcance

Este documento define los requisitos y la arquitectura de la PCB del Magnet Driver. El Magnet Driver es un convertidor DC/DC en puente en H que alimenta los electroimanes de levitación y guiado del prototipo Hyperloop y cierra localmente el lazo de corriente en una FPGA.

**Entra en el alcance** la PCB completa:

- etapa de potencia;
- gate driving;
- sensado;
- FPGA y circuitos auxiliares, incluidos los ADC externos;
- interfaz de comunicación con la VCU;
- alimentación auxiliar.

**Queda fuera del alcance:**

- el firmware de la FPGA, que es responsabilidad de Firmware;
- la lectura de los sensores de entrehierro y el lazo de entrehierro, que hace la VCU;
- la precarga del bus;
- el circuito de refrigeración aguas arriba del waterblock;
- el diseño de las bobinas.

## 2. Contexto del sistema

### 2.1 Arquitectura anterior

```
VCU ──► LCU (2 MCU "master/slave", Ethernet, CAN, entradas de sensores de entrehierro)
          │  10 × cable plano de 26 pines: PWM L/R, reset, ready/fault,
          │  analógicas diferenciales de Vbus, Ishunt y NTC
          ▼
       10 × LPU (etapa de potencia sin inteligencia, TFG L. Navarro)
```

### 2.2 Arquitectura nueva

```
VCU (maestro de comunicaciones + lazo de entrehierro)
  │  bus de campo (EtherCAT preferente): consigna de corriente ▼ / telemetría ▲
  │  lógica cableada de seguridad (redundante)
  ├──► Magnet Driver #1 ──► HEMS 1
  ├──► ...
  └──► Magnet Driver #10 ──► EMS 6
```

- La LCU desaparece del vehículo [U].
- La lectura de los sensores de entrehierro, que antes hacía la LCU, pasa a la VCU [U].
- Hay que confirmar si la LCU tenía otras funciones que reasignar (HW-06).

## 3. Documentos de referencia

| Ref. | Documento |
|---|---|
| R1 | L. Navarro Torrejón, *Diseño, modelado e implementación de un convertidor DC/DC en puente en H de 400 V y 55 A pico con MOSFETs de SiC…*, TFG GIEIA, UPV, 2025/26 |
| R2 | Lattice, *MachXO5-NX Family Data Sheet*, FPGA-DS-02102 |
| R3 | Beckhoff, *EtherCAT IP Core for Lattice FPGAs – Hardware Description* (ET1825/26/27) |
| R4 | Reglamento de la competición (TBD: documento y versión) |
| R5 | Dpto. de electromagnetismo, `Inductancia_EMS_H11_datos.mat`: EMS del prototipo H11 (matriz L, 23/06/2026) |
| R6 | Dpto. de electromagnetismo, `Impedancia_EMS_H11.mat` (matriz Z, 23/06/2026) |
| R7 | Dpto. de electromagnetismo, `HEMS_H11_Inductancia.xlsx`: HEMS del prototipo H11 (entrehierro de 6 a 18 mm × corriente de ±55 A) |

---

## 4. Requisitos

### 4.1 Sistema (SYS)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| SYS-01 | Una única variante de placa para los 10 electroimanes (4 HEMS + 6 EMS) | U | OK |
| SYS-02 | El Magnet Driver ejecuta el lazo de corriente de forma autónoma; la VCU solo envía la consigna de corriente | U | OK |
| SYS-03 | Una sola PCB integra la potencia, el gate driving, el sensado, la FPGA, la comunicación y la alimentación auxiliar | U | OK |
| SYS-04 | Las funciones de la LCU eliminada quedan asignadas a la VCU o al Magnet Driver. La lectura de entrehierro la hace la VCU | U | Entrehierro: OK · resto: TBD (HW-06) |
| SYS-05 | Número de unidades a fabricar (10 + repuestos) | — | TBD (HW-07) |

### 4.2 Carga: electroimanes (LOAD)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| LOAD-01 | Carga inductiva no lineal (prototipo H11, ver 6.1). L incremental: EMS de 1,92 a 117 mH; HEMS de 6,2 a 11,2 mH (con el flujo del imán de 0,84 a 1,05 Wb). **R = 1,2 Ω medida en la bobina construida**. Habrá un nuevo diseño de bobinas, así que el Magnet Driver debe admitir un rango de L y R | U, R5, R7 | R: OK · HEMS: OK (derivado) · EMS: AC (EM-D-01, EM-D-02) · nuevas bobinas: TBD (EM-D-04) |
| LOAD-02 | Corriente de salida bipolar | U | OK |
| LOAD-03 | Corriente de pico de 60 A durante los primeros segundos de la levitación (el TFG usaba 55 A) | U | OK · duración: TBD (EM-C-01) · mapas a 60 A: TBD (EM-D-03) |
| LOAD-04 | Corriente nominal idealmente 0 A en HEMS (el imán permanente sostiene el peso) | U, TFG | HEMS: OK · EMS: TBD (EM-C-01) |
| LOAD-05 | Corriente eficaz o perfil de misión para el dimensionado térmico (el TFG mencionaba 5 A en régimen permanente) | TFG | TBD (EM-C-01) |
| LOAD-06 | Ancho de banda o tiempo de respuesta del lazo de corriente | — | TBD (EM-C-03) |
| LOAD-07 | Rizado de corriente máximo admisible | — | TBD (EM-C-03) |
| LOAD-08 | Medida de temperatura de bobina mediante una NTC en el electroimán (TFG: GA10K4A1IA) | U, TFG | Función: OK · sensor: AC (HW-02) |

### 4.3 Bus DC (DCB)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| DCB-01 | Tensión de bus de 320 V mín. a 400 V máx. La batería se va a rehacer | U | OK · revisar con la nueva batería (ME-I-07) |
| DCB-02 | Los componentes y el aislamiento deben soportar **600 V DC en continuo**. No hace falta prever un bus de 650 V (el TFG dimensionó el divisor de Vbus para ese valor) | U | OK |
| DCB-03 | Bus compartido por los 10 Magnet Driver | U | OK |
| DCB-04 | Precarga realizada por otro módulo, externo al Magnet Driver | U | OK |
| DCB-05 | Distribución del bus: encadenado placa a placa con dos pares de terminales (TFG) o en estrella | TFG | TBD (ME-I-03) |
| DCB-06 | Fusible en placa (TFG: 15 A / 500 VDC, 0ADKC9150-BE; no cubre los 600 V de DCB-02) | TFG | AC (ME-I-03, HW-02) |
| DCB-07 | Rizado de tensión en el DC-link ≤ 2 % (8 V) | TFG | AC (HW-02) |
| DCB-08 | Si la rueda libre no es posible (drivers sin alimentación o apagados por un fallo), la corriente de la bobina vuelve al DC-link por los diodos. El DC-link o un circuito de protección debe absorber esa energía sin superar la tensión nominal de ningún componente (ver 6.3) | C, P | TBD (HW-03) |

### 4.4 Etapa de potencia (PWR)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| PWR-01 | Topología de puente en H completo | U | OK |
| PWR-02 | MOSFET de SiC de 900 V (TFG: SCT012H90G3AG, 12 mΩ). La placa del TFG no se llegó a ensayar y se estudiarán alternativas | TFG, U | Abierto (HW-02) |
| PWR-03 | Frecuencia de conmutación de 20 kHz y modulación unipolar (TFG). Con la FPGA ambos parámetros pasan a ser configurables | TFG, P | TBD (FW-08) |
| PWR-04 | Los tiempos muertos se generan en la FPGA y son configurables, en lugar de fijarse con la red RC de 100 ns del TFG | P | AC (FW-08) |
| PWR-05 | Refrigeración líquida mediante waterblock bajo la PCB; el agua se enfría en un acumulador térmico de PCM (fuera del alcance). En esta generación el waterblock puede tener otras dimensiones | U, TFG | OK |
| PWR-06 | Interfaz térmica y mecánica con el nuevo waterblock | U | TBD (ME-C-01) |

### 4.5 Gate driving (GD)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| GD-01 | Drivers aislados con alimentación bipolar de +20 V / −5 V, protección DESAT (respuesta < 2 µs) y Miller clamp. En el TFG son ADuM4146 con fuentes MGJ2D052005BSC | TFG | AC (HW-02) |
| GD-02 | Los fallos internos del driver (DESAT, UVLO) se detectan por lógica programada (FPGA) y por lógica cableada | U | OK |
| GD-03 | Protección cruzada por hardware que impida el shoot-through aunque falle la FPGA | P | AC (HW-01) |
| GD-04 | Estado por defecto sin PWM o ante un fallo: **low-side en ON y high-side en OFF**, de modo que la corriente circula en rueda libre (como en el TFG) | U, TFG | OK |

### 4.6 Sensado y adquisición (SNS)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| SNS-01 | Medida de corriente de bobina aislada. El rango debe cubrir ±60 A con margen; el TFG usaba un shunt de 500 µΩ con AMC1302 y fondo de escala de ±100 A | U, TFG | AC (HW-02) |
| SNS-02 | Medida de la tensión de bus aislada | U, TFG | OK |
| SNS-03 | Medida de la temperatura de bobina aislada: la NTC está en el dominio HV | U, TFG | OK |
| SNS-04 | No se requiere medir la temperatura de los MOSFET ni del waterblock | U | OK |
| SNS-05 | Conversión con ADC externos en la propia placa. Resolución, frecuencia de muestreo y latencia por definir | U | TBD (FW-01) |
| SNS-06 | Muestreo de corriente sincronizado con la PWM | P | AC (FW-01) |

### 4.7 Control y FPGA (CTL)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| CTL-01 | FPGA Lattice MachXO5-NX (probable, sin elección definitiva). Densidad y encapsulado por definir | U | AC (FW-02) |
| CTL-02 | La FPGA implementa el lazo de corriente, la PWM, los tiempos muertos, las protecciones programadas y la pila de comunicación (si se usa IP core) | U, P | AC (FW-02, FW-06) |
| CTL-03 | Memoria de configuración. La MachXO5-NX lleva flash interna; ¿hace falta una flash externa? | — | TBD (FW-03) |
| CTL-04 | Conector JTAG accesible y actualización en campo por el bus (p. ej. FoE en EtherCAT) | P | TBD (FW-04) |
| CTL-05 | Comportamiento ante pérdida de comunicación: timeout y rampa a 0 A, o mantener la consigna | — | TBD (FW-05) |
| CTL-06 | Identificación de la posición del módulo (HEMS 1–4 / EMS 1–6) con una placa idéntica para todos | P | TBD (ME-I-06) |
| CTL-07 | El lazo de corriente debe ser estable y cumplir sus prestaciones con una inductancia de 1,92 a 117 mH (en el EMS varía unas 60 veces; ver 6.1). Para ello puede recibir el entrehierro por el bus o estimar L en línea. La arquitectura de control está pendiente | C, P, U | TBD (EM-C-02) |

### 4.8 Comunicación con la VCU (COM)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| COM-01 | EtherCAT como bus preferente, aún sin decisión definitiva | U | AC (FW-06) |
| COM-02 | Esclavo EtherCAT implementado con un ESC dedicado o con el IP core de Beckhoff. El IP core (licencia ET1825/26/27) soporta MachXO5-NX y admite MII, RMII o RGMII | P, R3 | TBD (FW-06) |
| COM-03 | Topología en línea: 2 puertos por Magnet Driver (entrada y salida), cada uno con su PHY y sus magnéticos | P | AC (FW-06) |
| COM-04 | Maestro EtherCAT en la VCU (plataforma por definir) y tiempo de ciclo por definir | — | TBD (FW-06) |
| COM-05 | Datos intercambiados: consigna, habilitación, modo, límites y parámetros hacia el Magnet Driver; corriente, tensión, temperaturas y fallos hacia la VCU | P | TBD (FW-07) |
| COM-06 | EEPROM SII del esclavo, física o emulada | R3 | TBD (FW-06) |

### 4.9 Alimentación auxiliar (AUX)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| AUX-01 | Alimentación de baja tensión desde la batería de BT (**24 V máximo**), o por PoE o una solución similar | U | 24 V máx.: OK · método: TBD (ME-I-02) |
| AUX-02 | Raíles necesarios: núcleo e I/O de la FPGA, PHY, cuatro fuentes aisladas de +20 V / −5 V para los drivers y una fuente aislada para el sensado en HV | P | AC (HW-05) |
| AUX-03 | Tensión mínima de entrada BT y consumo máximo permitido | — | TBD (ME-I-02) |

### 4.10 Protecciones y seguridad (SAF)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| SAF-01 | Fallos detectados: fallos internos del gate driver, temperatura de bobina y tensión de bus | U | OK |
| SAF-02 | Cada fallo se detecta por lógica programada (FPGA) y por lógica cableada independiente | U | OK |
| SAF-03 | El Magnet Driver recibe órdenes de forma redundante: por EtherCAT (o el protocolo elegido) y por **señales cableadas de enable y fault** | U | OK · señales, niveles y conectores: TBD (ME-I-01) |
| SAF-04 | Varias protecciones analógicas o de lógica cableada en la propia placa, además de DESAT (por ejemplo, sobrecorriente de bobina) | U | OK · cuáles y umbrales: TBD (HW-01) |
| SAF-05 | Estado seguro: **rueda libre por los low-side**. La energía de la bobina se disipa en su propia resistencia (ver 6.3) | U | OK |
| SAF-06 | Tiempo de respuesta de cada protección | — | TBD (HW-01) |
| SAF-07 | La rueda libre debe mantenerse aunque se pierda la alimentación de BT o falle un driver; si no, hay que prever el camino alternativo de DCB-08 | C, P | TBD (HW-03) |
| SAF-08 | Las protecciones de hardware se pueden desactivar fácilmente (jumpers o similar) | U | OK · método: TBD (HW-01) |
| SAF-09 | La FPGA lee el estado de esos jumpers y lo reporta por el bus, para que no se opere con protecciones desactivadas sin saberlo | P | AC (HW-01) |

### 4.11 Aislamiento (ISO)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| ISO-01 | Aislamiento galvánico entre HV y LV | U | OK |
| ISO-02 | Separación ≥ 4 mm con coating entre HV y LV (regla de la competición, vigente) | U, TFG | OK |
| ISO-03 | ≥ 2 mm entre distintas redes de HV | TFG | AC (HW-04) |
| ISO-04 | ≥ 4 mm entre los taladros de fijación del waterblock y cualquier conductor | TFG | AC (ME-C-01) |
| ISO-05 | Tensión de aislamiento y tipo de aislamiento (básico o reforzado) | — | TBD (HW-04) |
| ISO-06 | Distancias de aislamiento dimensionadas para 600 V DC en continuo (DCB-02) | U, C | AC (HW-04) |

### 4.12 Mecánica, fabricación y entorno (MEC)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| MEC-01 | Tamaño de la placa por acordar: el waterblock puede cambiar de dimensiones en esta generación (el TFG estaba limitado a 190 × 100 mm) | U, TFG | TBD (ME-C-01) |
| MEC-02 | Altura máxima de componentes de 40 mm | TFG | AC (ME-C-01) |
| MEC-03 | PCB de 6 capas simétrica con cobre de 2 oz (el TFG usaba el stackup de NCAB); fabricante por definir | TFG, U | AC (PT-01) |
| MEC-04 | Herramienta EDA: **KiCad** (el TFG usaba Altium Designer) | U | OK |
| MEC-05 | Operación a **temperatura y presión atmosféricas**, no en vacío. A diferencia de lo que suponía el TFG, hay convección | U | OK |
| MEC-06 | Valores numéricos del rango de temperatura ambiente (el TFG asumía ≥ 25 °C por competir en verano) | TFG | TBD (ME-C-02) |
| MEC-07 | Conectores de potencia, de bus de campo, de lógica cableada, de NTC y de alimentación BT | — | TBD (ME-I-04) |
| MEC-08 | Nivel de vibraciones (depende en parte del propio convertidor) | U | TBD (ME-I-05) |
| MEC-09 | Fabricación y montaje: fabricante de PCB y capacidad de montaje de BGA | U | TBD (PT-01, PT-02) |

---

## 5. Arquitectura de la PCB

### 5.1 Diagrama de bloques (opción A, propuesta)

```
 HV+ / HV- (bus compartido, 320-400 V)      entrada y salida hacia otros Magnet Driver (TBD)
   │
 ┌─┴──────────────────────── DOMINIO HV ───────────────────────────────────────┐
 │ [Fusible]─►[DC-link film+cerámicos]─►[Puente H SiC x4]─►[Shunt]─► BOBINA     │
 │      │                                    ▲                │        │ NTC    │
 │ [Divisor Vbus]                 [Gate drivers aislados x4]   │        │        │
 │      │                         [Fuentes aisladas +20/-5 x4] │        │        │
 │ [Medida aislada Vbus]         [Medida aislada Ibob]  [Medida aislada Tbob]     │
 └══════╪══════════════════════ BARRERA DE AISLAMIENTO ══════╪═══════════╪═════════┘
 ┌──────┴────────────────────── DOMINIO LV ──────────────────┴───────────┴────────┐
 │  [ADC externos / filtros de decimación]                                        │
 │                │                                                               │
 │  [FPGA MachXO5-NX] lazo de corriente · PWM + tiempos muertos · protecciones     │
 │       │      │        programadas · ESC EtherCAT (IP core) o bus hacia un ESC   │
 │       │      └──►[Lógica cableada de protección]──► inhibición de los drivers   │
 │       │                 ▲ fallos de driver, Tbob, Vbus, señales de la VCU       │
 │  [PHY 1]─[Magnéticos]─► EtherCAT IN      [PHY 2]─[Magnéticos]─► EtherCAT OUT    │
 │  [EEPROM SII] [Oscilador] [JTAG] [LEDs] [ID de posición]                        │
 │  [Alimentación auxiliar: entrada BT/PoE ─► raíles LV + fuentes aisladas hacia HV]│
 └────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Posición de la barrera de aislamiento: decisión pendiente (HW-05, FW-01)

| | **Opción A: FPGA en el dominio LV** (propuesta) | **Opción B: FPGA en el dominio HV** |
|---|---|---|
| Qué cruza la barrera | Las 3 medidas analógicas, las 4 señales de puerta y la alimentación | El bus de campo, las señales cableadas de la VCU y la alimentación |
| Sensado | Moduladores ΔΣ aislados (p. ej. familia AMC13xx de TI; la FPGA hace el filtro sinc) o amplificador aislado + ADC | ADC sin aislamiento, cerca del shunt |
| Depuración | JTAG seguro con HV presente | JTAG referido a HV: hace falta un depurador aislado |
| Continuidad con el TFG | Alta: reutiliza su filosofía de aislamiento | Baja |
| Riesgos | Más fuentes aisladas y latencia de los ΔΣ | Aislamiento de EtherCAT y de la lógica de seguridad; riesgo en pruebas |

### 5.3 Bloques: qué se hereda del TFG y qué es nuevo

| Bloque | Base en el TFG | Cambio |
|---|---|---|
| Puente en H y DC-link | Sí, sin ensayar | Revisar para 60 A, 600 V y el caso de fallo de 6.3; estudiar alternativas (HW-02) |
| Gate drivers | Sí, sin ensayar | Los tiempos muertos y el reset pasan a la FPGA; el estado por defecto sigue siendo rueda libre por los low-side (SAF-05) |
| Sensado | Sí (salida analógica hacia la LCU) | Ahora se digitaliza en placa |
| Lógica ready/fault | Puertas AND con salida hacia la LCU | Se integra en la lógica cableada de protección, desactivable por jumpers (SAF-08) |
| FPGA y control | No | Nuevo |
| EtherCAT | No | Nuevo |
| Alimentación auxiliar | Parcial: recibía +3V3, +5V y VBAT por el conector | Nueva etapa de entrada BT/PoE |

---

## 6. Comprobaciones preliminares [C]

Salvo que se indique otra cosa, los cálculos usan R = 1,2 Ω (medida en la bobina construida) e I = 60 A.

### 6.1 Inductancia de los electroimanes del prototipo H11 (R5, R6, R7)

En los dos electroimanes, la inductancia es del orden de **mH** y R = 1,2 Ω (medida en la bobina construida [U]).

#### 6.1.1 EMS de guiado (ficheros MATLAB, sin vectores de ejes)

- **L:** matriz de 111 × 71, con valores entre **1,92 y 117 mH** (en henrios dentro del fichero).
- **Z:** matriz de 105 × 67. Es exactamente |R + j·2π·2000·L| sobre la submatriz interior de L, con R = 0,503 Ω. Es decir, es el módulo de la impedancia a 2 kHz calculado con la R del modelo, no con la de la bobina construida.
- **Ejes (hipótesis reforzada):**
  - **Filas = corriente de −55 a +55 A en pasos de 1 A.** Es el mismo eje de 111 puntos que tiene el Excel de los HEMS, y las filas son exactamente simétricas, como corresponde a un EMS sin imán.
  - **Columnas = entrehierro creciente.** A corriente cero, L cae como 1/g, y la corriente a la que empieza la saturación crece con el entrehierro.
  - Los ficheros MATLAB guardan los ejes al revés que el Excel.
- **Definición de L:** solo la lectura como inductancia **incremental** (dψ/di) da un flujo monótono. Esto no coincide con la definición del Excel de los HEMS (6.1.2), así que hay que confirmarlo.
- **Valor citado:** 26,7 mH corresponde a I = 0 entre las columnas 5 y 6.

#### 6.1.2 HEMS de levitación (Excel, con ejes)

- **Ejes:** filas = entrehierro de 6 a 18 mm en pasos de 1 mm; columnas = corriente de −55 a +55 A en pasos de 1 A [U].
- **El valor tabulado es ψ/|i| e incluye el flujo del imán permanente.**
  - Por eso vale unos 1000 mH cerca de 0 A y se comporta como 1/|i|.
  - El valor en 0 A es la media de sus dos vecinos.
  - **No debe usarse directamente como inductancia de circuito.**
- **Flujo reconstruido:** ψ = L·|i| es continuo y crece de forma monótona con la corriente. El flujo del imán a 0 A vale entre 0,84 Wb (18 mm) y 1,05 Wb (6 mm).
- **Inductancia incremental derivada:** dψ/di va de **6,2 a 11,2 mH** en todo el mapa. Es menor con corriente positiva, que refuerza al imán y satura antes.

#### 6.1.3 Consecuencias para el diseño

| Magnitud | EMS | HEMS | Diseño (peor caso) |
|---|---|---|---|
| L incremental | 1,92 a 117 mH (×61) | 6,2 a 11,2 mH (×1,8) | 1,92 a 117 mH |
| Rizado pico a pico a 20 kHz (unipolar, D = 0,5), a 320 V / 400 V | 1,04 A / 1,30 A | 0,32 A / 0,40 A | 1,30 A |
| di/dt a 320 V / 400 V | de 2,7 a 208 A/ms | de 29 a 65 A/ms | de 2,7 a 208 A/ms |
| Energía devuelta al desmagnetizar desde 55 A | ≈ 15,6 J | ≈ 16,7 J (desde −55 A, 6 mm); ≈ 11 J desde +55 A | ≈ 16,7 J |

- **El lazo de corriente es mucho más exigente en el EMS**, donde la planta varía unas 60 veces con la corriente y el entrehierro (ver CTL-07 y EM-C-02). En el HEMS apenas varía.
- **Como la placa es la misma para los dos electroimanes** (SYS-01), el control debe cubrir ambos casos: por parámetros según la posición (CTL-06) o con un control que se adapte.
- **Los datos cubren hasta ±55 A.** Para 60 A hay que extrapolar o pedir mapas ampliados.
- **La corriente nula en los HEMS** (LOAD-04) es coherente con el flujo del imán, que sostiene el peso.

### 6.2 Potencia a 60 A en régimen permanente

- La tensión en bornes de la bobina es 72 V y disipa 4,3 kW.
- La corriente media del bus es de 13,5 A a 320 V y de 10,8 A a 400 V por Magnet Driver, sin contar pérdidas. Ese valor está muy cerca del fusible de 15 A del TFG, por lo que hay que revisar el fusible con el perfil real (EM-C-01, ME-I-03).
- Con el bus encadenado, la primera placa conduciría la suma de las 10.

### 6.3 Desmagnetización y estado seguro

**Funcionamiento normal (estado seguro elegido, SAF-05).**

- Con los low-side en ON, la bobina queda cortocircuitada y su corriente decae sobre su propia resistencia (1,2 Ω más la de los MOSFET y el shunt, que es despreciable). No se devuelve energía al bus.
- **Constante de tiempo orientativa (L/R):**
  - HEMS: de 5 a 9 ms.
  - EMS: de 1,6 a 98 ms, según el punto de trabajo.
  - La corriente cae prácticamente a cero en unas pocas constantes de tiempo.
- **Observación:** con la bobina cortocircuitada, un cambio de entrehierro induce corriente, sobre todo en los HEMS por el flujo del imán. El efecto es un amortiguamiento (EM-C-04).

**Caso de fallo: la rueda libre no es posible (DCB-08, SAF-07).**

Si los drivers se quedan sin alimentación o se apagan por un fallo, los MOSFET de SiC quedan en OFF y la corriente vuelve al DC-link por los diodos.

- **Con el peor caso de H11 (≈ 16,7 J, HEMS a −55 A) y los 105 µF del TFG:** el DC-link llegaría a ≈ **650 V desde 320 V** y a ≈ **690 V desde 400 V**.
  - Queda por debajo de los 900 V de los MOSFET.
  - **Supera los 600 V continuos que deben soportar los componentes (DCB-02) y los 500 V de los condensadores de film del TFG.**
- **Para no pasar de 600 V partiendo de 400 V** harían falta ≥ 167 µF.
- **Estimación inicial** (26,7 mH constantes a 60 A, 48 J): ≈ 1040 V. Queda como cota pesimista.
- **Opciones (HW-03):**
  - mantener la alimentación de los drivers low-side el tiempo suficiente;
  - añadir un clamp o un chopper;
  - aumentar el DC-link.

---

## 7. Cuestiones pendientes

Cada cuestión se asigna al subsistema que debe resolverla. ★ marca las que bloquean la arquitectura.

| Código | Subsistema |
|---|---|
| EM-C | Electromagnetics – Control |
| EM-D | Electromagnetics – Design |
| ME-C | Mechanics – Cooling |
| ME-I | Mechanics – Electrical Integration |
| FW | Firmware |
| HW | Hardware (este equipo) |
| PT | Partners (fabricación) |

### 7.1 Electromagnetics – Control (EM-C)

| ID | Cuestión | Afecta a |
|---|---|---|
| EM-C-01 ★ | Perfil de corriente: duración y forma del pico de 60 A, corriente eficaz en crucero en HEMS y EMS, y corriente nominal del EMS | LOAD-03, LOAD-04, LOAD-05, DCB-06, térmica |
| EM-C-02 ★ | Arquitectura de control (pendiente). ¿El Magnet Driver recibe el entrehierro de la VCU para ajustar las ganancias, estima L en línea o usa un control robusto? | CTL-07, COM-05 |
| EM-C-03 | Ancho de banda del lazo de corriente y rizado máximo admisible | LOAD-06, LOAD-07, PWR-03, SNS-05 |
| EM-C-04 | En rueda libre, un cambio de entrehierro induce corriente en la bobina, sobre todo en los HEMS. ¿Es aceptable o incluso deseable como amortiguamiento? | SAF-05, 6.3 |

### 7.2 Electromagnetics – Design (EM-D)

| ID | Cuestión | Afecta a |
|---|---|---|
| EM-D-01 | Ficheros MATLAB del EMS: vectores de ejes (hipótesis: filas = corriente de ±55 A; columnas = entrehierro) y valor del entrehierro en cada columna | LOAD-01, 6.1.1 |
| EM-D-02 | Definición de L. En el EMS parece incremental; en el Excel de los HEMS es ψ/\|i\| e incluye el flujo del imán. ¿Se calcularon de forma distinta? | LOAD-01, CTL-07 |
| EM-D-03 | Mapas de inductancia ampliados a 60 A | LOAD-03, 6.1.3 |
| EM-D-04 | Rango esperado de L y R de las nuevas bobinas | LOAD-01 |

### 7.3 Mechanics – Cooling (ME-C)

| ID | Cuestión | Afecta a |
|---|---|---|
| ME-C-01 ★ | Dimensiones e interfaz del nuevo waterblock: superficie de contacto, fijaciones, material térmico y altura máxima de componentes. Estos datos fijan el tamaño de la placa | PWR-06, MEC-01, MEC-02, ISO-04 |
| ME-C-02 | Temperatura y caudal del refrigerante; valores del rango de temperatura ambiente | MEC-06, térmica |

### 7.4 Mechanics – Electrical Integration (ME-I)

| ID | Cuestión | Afecta a |
|---|---|---|
| ME-I-01 ★ | Señales cableadas con la VCU: cuáles (enable, fault, lazo de seguridad), con qué niveles y conectores, y si el Magnet Driver solo las recibe o también debe abrir el lazo | SAF-03 |
| ME-I-02 ★ | Alimentación de BT: tensión mínima de la batería de 24 V, consumo permitido por placa y método (mazo de 24 V, PoE o similar). PoE es un enlace punto a punto y no encaja directamente con EtherCAT en línea; EtherCAT P (Beckhoff) es una alternativa | AUX-01, AUX-03 |
| ME-I-03 | Distribución del bus de HV: encadenado placa a placa (TFG) o en estrella; ¿fusible en cada placa? | DCB-05, DCB-06, 6.2 |
| ME-I-04 | Conectores: potencia, bobina, NTC, bus de campo, señales cableadas y BT | MEC-07 |
| ME-I-05 | Especificación de vibraciones | MEC-08 |
| ME-I-06 | Identificación de la posición de cada placa (alias en EEPROM, selector físico o codificación en el mazo), junto con Firmware | CTL-06, sección 8 |
| ME-I-07 | Rango de tensión de la nueva batería de HV | DCB-01 |

### 7.5 Firmware (FW)

| ID | Cuestión | Afecta a |
|---|---|---|
| FW-01 ★ | Adquisición. ¿Se acepta la opción A (FPGA en BT) con moduladores ΔΣ aislados como ADC externos, o se prefieren ADC en paralelo o SPI? ¿Qué resolución, frecuencia de muestreo y latencia hacen falta? | 5.2, SNS-05, SNS-06 |
| FW-02 | Elección definitiva de la FPGA: densidad y encapsulado. Según Lattice, la MachXO5-NX se ofrece en encapsulados BGA | CTL-01, PT-02 |
| FW-03 | ¿Hace falta una flash de configuración externa? | CTL-03 |
| FW-04 | Programación y depuración: conector JTAG y actualización por el bus | CTL-04 |
| FW-05 | Comportamiento ante pérdida de comunicación, junto con EM-C | CTL-05 |
| FW-06 ★ | EtherCAT: confirmación del protocolo; ESC dedicado o IP core de Beckhoff (de pago); plataforma del maestro en la VCU; tiempo de ciclo; EEPROM SII | COM-01, COM-02, COM-03, COM-04, COM-06 |
| FW-07 | Datos intercambiados con la VCU (mapa de objetos) | COM-05 |
| FW-08 | Rango de frecuencia de conmutación y tipo de modulación que debe admitir el hardware | PWR-03 |

### 7.6 Hardware (HW)

| ID | Cuestión | Afecta a |
|---|---|---|
| HW-01 | Qué protecciones analógicas o de lógica cableada se incluyen, con qué umbrales y tiempos de respuesta, y cómo se desactivan (jumpers) y se reportan | SAF-04, SAF-06, SAF-08, SAF-09 |
| HW-02 | Alternativas a los componentes del TFG, que no se llegó a ensayar: MOSFET, drivers, sensado, fusible y condensadores del DC-link para 600 V | PWR-02, GD-01, SNS-01, DCB-02, DCB-06, DCB-07 |
| HW-03 ★ | Caso de fallo sin rueda libre: mantener alimentados los drivers low-side, añadir un clamp o un chopper, o aumentar el DC-link (≥ 167 µF para no pasar de 600 V desde 400 V) | DCB-08, SAF-07, 6.3 |
| HW-04 | Tensión y tipo de aislamiento, distancias para 600 V, y documento y versión del reglamento (R4) | ISO-05, ISO-06 |
| HW-05 ★ | Posición de la barrera de aislamiento (opción A o B), junto con Firmware | 5.2, AUX-02 |
| HW-06 | ¿Tenía la LCU otras funciones que haya que reasignar, además de la lectura de entrehierro? | SYS-04 |
| HW-07 | Número de unidades a fabricar | SYS-05 |

### 7.7 Partners (PT)

| ID | Cuestión | Afecta a |
|---|---|---|
| PT-01 | Fabricante de PCB: capacidades (6 capas, 2 oz, fresados), stackup y aplicación del coating | MEC-03, MEC-09, ISO-02 |
| PT-02 | Montaje en casa o externo, con capacidad para BGA | MEC-09, FW-02 |
| PT-03 | Patrocinio o disponibilidad de componentes (MOSFET de SiC, etc.) y, si se elige el IP core, la licencia de Beckhoff | HW-02, FW-06 |

### 7.8 Preguntas resueltas (numeración de la versión 0.1)

| Pregunta | Respuesta | Dónde se recoge |
|---|---|---|
| N1 (en parte) | H11 es la generación del prototipo; R = 1,2 Ω medida en la bobina construida; los ejes del Excel de los HEMS son conocidos | LOAD-01, 6.1 |
| N2 | La VCU lee los sensores de entrehierro | 2.2, SYS-04 |
| N3 | Estado seguro: rueda libre por los low-side | GD-04, SAF-05, 6.3 |
| N6 | El waterblock puede tener otras dimensiones en esta generación | PWR-05, MEC-01 |
| N7 | La batería de BT es de 24 V máximo | AUX-01 |
| N8 (en parte) | Redundancia: señales cableadas de enable y fault más órdenes por el bus | SAF-03 |
| N9 | Varias protecciones analógicas o cableadas en placa, fáciles de desactivar con jumpers | SAF-04, SAF-08 |
| N10 | La separación de 4 mm con coating sigue vigente | ISO-02 |
| N11 | No hace falta prever 650 V, pero sí soportar 600 V en continuo | DCB-02, ISO-06 |
| N15 | No se mide la temperatura de los MOSFET ni del waterblock | SNS-04 |
| N16 (en parte) | La placa del TFG no se ensayó; se discutirán alternativas | PWR-02, HW-02 |
| N17 | Nombre: Magnet Driver Abejorro | Sección 8 |
| N18 | El documento sigue en Markdown | — |
| N19 (en parte) | Herramienta EDA: KiCad; fabricante por definir | MEC-04, PT-01 |
| N20 (en parte) | Temperatura y presión atmosféricas; vibraciones por definir | MEC-05, ME-I-05 |
| N21 | La arquitectura de control sigue pendiente | EM-C-02 |

Las demás preguntas de la versión 0.1 siguen abiertas con su nuevo código:

- N4 → HW-05, FW-01
- N5 → EM-C-01
- N12 → ME-I-03
- N13 → FW-06
- N14 → ME-I-06

---

## 8. Nomenclatura y control de versiones

- **Esquema de nombres** [U]:
  - Cada generación de hardware se llama "Magnet Driver" seguido de un nombre de insecto.
  - Se descartan las siglas.
  - Los nombres no tienen que seguir ningún orden.
- **Primera generación con FPGA** [U]: **Magnet Driver Abejorro**.
- **Para qué sirve el nombre** [U]: identifica de un vistazo la compatibilidad de conectores y de firmware.
- **Regla propuesta** [P]:
  - Se asigna un **nuevo nombre** cuando se rompe la compatibilidad. Eso ocurre si cambia el tipo o el pinout de algún conector externo, o si cambia la interfaz con el firmware (pinout de la FPGA, periféricos o mapa de entradas y salidas).
  - Si se mantiene la compatibilidad, se conserva el nombre y se sube la revisión: "Abejorro, revisión 2".
- **Registro de compatibilidad** [P]:

| Nombre | Revisión | Conectores | Firmware compatible | Notas |
|---|---|---|---|---|
| Abejorro | 1 | TBD | TBD | Primera generación con FPGA |

- **Identificación de cada unidad** [P]: nombre más posición, por ejemplo "Abejorro HEMS-1" o "Abejorro EMS-6" (ver ME-I-06).
- **Nombres disponibles** para generaciones futuras: Esfinge, Grillo, Hormiga, Libélula, Mantis, Sírfido, Tijereta.
- **Nombres descartados:**
  - Escarabajo: es el nombre del Volkswagen Beetle en español.
  - Mariposa: se confunde con la válvula de mariposa.
  - Abeja: demasiado parecido a Abejorro.
  - Mariquita, Cigarra, Zángano, Chinche, Polilla, Cucaracha, Mosquito y Zapatero: por sus connotaciones.

---

## 9. Historial de versiones

| Versión | Fecha | Cambios |
|---|---|---|
| 0.1 | 16/09/2026 | Primer borrador: requisitos, arquitectura, análisis de inductancias y nombre del módulo |
| 0.2 | 17/09/2026 | Respuestas a N2, N3, N6 a N11 y N15 a N21; estado seguro en rueda libre; 600 V en continuo; KiCad; operación a presión atmosférica; cuestiones pendientes por subsistema |

