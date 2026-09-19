# Magnet Driver Abejorro
**Convertidor DC/DC en puente en H con control local programable**
## Documento de requisitos y arquitectura: borrador v0.4

| Campo | Valor |
|---|---|
| Módulo | **Magnet Driver Abejorro**: primera generación con control local en la propia placa. Sustituye a la LPU (ver sección 8). |
| Versión | 0.4 (borrador de trabajo) |
| Fecha | 19/09/2026 |
| Estado | Incompleto: contiene requisitos por confirmar y huecos (TBD) |
| Alcance de esta revisión | **Plataforma de control:** deja de darse por supuesta la FPGA; se fijan criterios de aceptación (5.4), candidatos (6.6) y orden de decisión (FW-09). **Topología EtherCAT:** consecuencias de la línea, de los dos puertos, del esclavo sin alimentación y del direccionamiento por posición. **Cadena de sensado:** qué decide de verdad entre ΔΣ aislado y amplificador aislado. El resto del documento se mantiene como en la v0.3 |

### Convenciones

- **Fuente de cada requisito:**
  - **[U]**: lo ha indicado el equipo (16, 17 y 19/09/2026).
  - **[TFG]**: se hereda del TFG de L. Navarro (2025/26) y no está revalidado.
  - **[C]**: sale de un cálculo de la sección 6.
  - **[P]**: es una propuesta de este documento y está pendiente de aprobación.
  - **[HD]**: sale de una hoja de datos de fabricante (referencias R8 a R14 de la sección 3).
- **Estado de cada requisito:**
  - **OK**: confirmado.
  - **AC**: a confirmar.
  - **TBD**: valor desconocido. Entre paréntesis se indica la cuestión pendiente de la sección 7 que lo resolverá.
- **Códigos de subsistema** (sección 7): EM-C (Electromagnetics-Control), EM-D (Electromagnetics-Design), ME-C (Mechanics-Cooling), ME-I (Mechanics-Electrical Integration), FW (Firmware), HW (Hardware) y PT (Partners).
- **Siglas de los electroimanes:** HEMS es el electroimán híbrido de levitación (4 unidades). EMS es el electroimán de guiado lateral (6 unidades).

---

## 1. Objeto y alcance

Este documento define los requisitos y la arquitectura de la PCB del Magnet Driver. El Magnet Driver es un convertidor DC/DC en puente en H que alimenta los electroimanes de levitación y guiado del prototipo Hyperloop y **cierra localmente el lazo de corriente en un controlador programable alojado en la propia placa**.

**Nuevo en la v0.4:** la plataforma de ese controlador deja de darse por supuesta. La FPGA sigue siendo candidata, pero no la única: el alcance de CTL-02 lo cubren también varios microcontroladores de tiempo real con controlador de esclavo EtherCAT integrado. Los criterios de aceptación están en 5.4, los candidatos en 6.6 y la decisión es FW-09.

**Entra en el alcance** la PCB completa:

- etapa de potencia;
- gate driving;
- sensado;
- el controlador y sus circuitos auxiliares, incluida la cadena de adquisición;
- interfaz de comunicación con la VCU;
- alimentación auxiliar.

**Queda fuera del alcance:**

- el firmware del controlador, que es responsabilidad de Firmware;
- la lectura de los sensores de entrehierro y el lazo de entrehierro, que hace la VCU;
- la precarga del bus;
- **el clamp de bus de DCB-09**, que es un circuito de vehículo y se propone alojar en el módulo de precarga (nuevo en la v0.3);
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
  │  lógica cableada de seguridad (redundante) ──► a todos los Magnet Driver
  │
  │  bus de campo (EtherCAT preferente): TOPOLOGÍA EN LÍNEA, no en estrella
  └─► MD #1 ─► MD #2 ─► … ─► MD #10          (consigna ▼ / telemetría ▲)
       │        │              │
      HEMS 1   HEMS 2        EMS 6
                              ╎
                              ╎ opcional: vuelta a un 2.º puerto de la VCU
                              ╎ = redundancia en anillo (COM-07)
                              ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌►

Bus de HV compartido ──► [Módulo de precarga + CLAMP DE BUS (DCB-09)]
```

- La LCU desaparece del vehículo [U].
- La lectura de los sensores de entrehierro, que antes hacía la LCU, pasa a la VCU [U].
- Hay que confirmar si la LCU tenía otras funciones que reasignar (HW-06).
- **Nuevo en la v0.3:** el bus compartido necesita un clamp disipativo común a los 10 módulos (DCB-09, justificado en 6.3).
- **Nuevo en la v0.4:** el bus de campo se dibuja como lo que es, una línea. EtherCAT no admite la estrella que sugería el diagrama de la v0.3 (ver COM-03 y 6.6.4). Consecuencia: **un Magnet Driver sin alimentación de BT abre la cadena y deja fuera del bus a los que están aguas abajo** (COM-07).

## 3. Documentos de referencia

| Ref. | Documento |
|---|---|
| R1 | L. Navarro Torrejón, *Diseño, modelado e implementación de un convertidor DC/DC en puente en H de 400 V y 55 A pico con MOSFETs de SiC…*, TFG GIEIA, UPV, 2025/26 |
| R2 | Lattice, *MachXO5-NX Family Data Sheet*, FPGA-DS-02102 (solo aplica a la vía FPGA) |
| R3 | Beckhoff, *EtherCAT IP Core for Lattice FPGAs – Hardware Description* (ET1825/26/27) (solo aplica a la vía FPGA) |
| R4 | Reglamento de la competición (TBD: documento y versión) |
| R5 | Dpto. de electromagnetismo, `Inductancia_EMS_H11_datos.mat`: EMS del prototipo H11 (matriz L, 23/06/2026) |
| R6 | Dpto. de electromagnetismo, `Impedancia_EMS_H11.mat` (matriz Z, 23/06/2026) |
| R7 | Dpto. de electromagnetismo, `HEMS_H11_Inductancia.xlsx`: HEMS del prototipo H11 (entrehierro de 6 a 18 mm × corriente de ±55 A) |
| **R8** | Infineon, *IMT65R010M2H – CoolSiC MOSFET 650 V G2*, hoja de datos rev. 2.1 |
| **R9** | STMicroelectronics, *SCT012H90G3AG*, hoja de datos |
| **R10** | STMicroelectronics, *STGAP3S – Galvanically isolated single gate driver*, hoja de datos |
| **R11** | Analog Devices, *ADuM4146 – Single-/Dual-Supply, High Voltage, Isolated SiC Gate Driver with Miller Clamp*, hoja de datos |
| **R12** | Infineon, *EiceDRIVER 1ED31xxMU12H Compact*, hoja de datos rev. 2.1 |
| **R13** | Murata, *MGJ1 Series 5,7 kVDC Isolated 1W SM Gate Drive DC-DC Converters* |
| **R14** | Murata, *MGJ2 Series 5,2 kVDC Isolated 2W Gate Drive DC-DC Converters* |
| **R15** | Texas Instruments, *TMS320F28P65x Real-Time Microcontrollers*, hoja de datos (tabla de comparación de dispositivos y encapsulados; plano de encapsulado PTP0176H) |
| **R16** | Infineon, *XMC4800 / XMC4300 – XMC4000 family with integrated EtherCAT node*, página de producto y hoja de datos |
| **R17** | Renesas, *RX72M Group*, folleto y hoja de datos |
| **R18** | Microchip, *LAN9252 – 2/3-Port EtherCAT Slave Controller with integrated Ethernet PHYs*, hoja de datos |
| **R19** | Texas Instruments, *TMS320F28003x Real-Time Microcontrollers*, hoja de datos |
| **R20** | STMicroelectronics, *STM32H723/733*, hoja de datos |

---

## 4. Requisitos

### 4.1 Sistema (SYS)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| SYS-01 | Una única variante de placa para los 10 electroimanes (4 HEMS + 6 EMS). **Consecuencia (v0.4):** obliga a montar los dos conectores EtherCAT en las 10 placas aunque la última de la línea deje la salida sin usar (COM-03) | U | OK |
| SYS-02 | El Magnet Driver ejecuta el lazo de corriente de forma autónoma; la VCU solo envía la consigna de corriente | U | OK |
| SYS-03 | Una sola PCB integra la potencia, el gate driving, el sensado, la FPGA, la comunicación y la alimentación auxiliar | U | OK |
| SYS-04 | Las funciones de la LCU eliminada quedan asignadas a la VCU o al Magnet Driver. La lectura de entrehierro la hace la VCU | U | Entrehierro: OK · resto: TBD (HW-06) |
| SYS-05 | Número de unidades a fabricar (10 + repuestos) | — | TBD (HW-07) |

### 4.2 Carga: electroimanes (LOAD)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| LOAD-01 | Carga inductiva no lineal (prototipo H11, ver 6.1). L incremental: EMS de 1,92 a 117 mH; HEMS de 6,2 a 11,2 mH (con el flujo del imán de 0,84 a 1,05 Wb). **R = 1,2 Ω medida en la bobina construida**. Habrá un nuevo diseño de bobinas, así que el Magnet Driver debe admitir un rango de L y R | U, R5, R7 | R: OK · HEMS: OK (derivado) · EMS: AC (EM-D-01, EM-D-02) · nuevas bobinas: TBD (EM-D-04) |
| LOAD-02 | Corriente de salida bipolar | U | OK |
| LOAD-03 | Corriente de pico de 60 A durante **no mucho más de 2 s** al inicio de la levitación (el TFG usaba 55 A) | U | Valor: OK · **duración: OK (confirmada el 19/09/2026)** · mapas a 60 A: TBD (EM-D-03) |
| LOAD-04 | Corriente nominal idealmente 0 A en HEMS (el imán permanente sostiene el peso) | U, TFG | HEMS: OK · EMS: TBD (EM-C-01) |
| LOAD-05 | Corriente eficaz o perfil de misión para el dimensionado térmico (el TFG mencionaba 5 A en régimen permanente) | TFG | TBD (EM-C-01) |
| LOAD-06 | Ancho de banda o tiempo de respuesta del lazo de corriente | — | TBD (EM-C-03) |
| LOAD-07 | Rizado de corriente máximo admisible | — | TBD (EM-C-03) |
| LOAD-08 | Medida de temperatura de bobina mediante una NTC en el electroimán (TFG: GA10K4A1IA) | U, TFG | Función: OK · sensor: AC (HW-02) |

### 4.3 Bus DC (DCB)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| DCB-01 | Tensión de bus de 320 V mín. a 400 V máx. **La batería de HV seguirá siendo de 400 V durante mucho tiempo** (19/09/2026), así que ME-I-07 deja de bloquear la elección del MOSFET | U | OK |
| DCB-02 | Los componentes y el aislamiento deben soportar **600 V DC en continuo**. No hace falta prever un bus de 650 V | U | OK · **ver HW-08**: frente a este requisito, un MOSFET de 650 V trabaja al 92 % de su tensión de ruptura |
| DCB-03 | Bus compartido por los 10 Magnet Driver. **Los 10 DC-link quedan en paralelo (≈ 1050 µF), lo que reparte la energía de un fallo aislado pero no la de un fallo común (ver 6.3)** | U, C | OK |
| DCB-04 | Precarga realizada por otro módulo, externo al Magnet Driver | U | OK |
| DCB-05 | Distribución del bus: **en estrella**. El encadenado obligaría a la primera placa a conducir la suma de las 10 (unos 108 A si pican a la vez, ver 6.2) | TFG, C | AC (ME-I-03, EM-C-05) |
| DCB-06 | Fusible en placa (TFG: 15 A / 500 VDC, 0ADKC9150-BE). Con el pico de 2 s la corriente media de bus por módulo es de 10,8 A a 400 V (utilización 0,72) pero de **13,5 A a 320 V (utilización 0,90)**, por encima del criterio. Y su tensión nominal no cubre ni los 600 V de DCB-02 ni la actuación del clamp: **hay que sustituirlo por uno de ≥ 700 VDC** | TFG, C | AC (ME-I-03, HW-02) |
| DCB-07 | Rizado de tensión en el DC-link ≤ 2 % (8 V) | TFG | AC (HW-02) |
| DCB-08 | Si la rueda libre no es posible (drivers sin alimentación o apagados por un fallo), la corriente de la bobina vuelve al DC-link por los diodos de cuerpo. **Con el MOSFET de 650 V elegido, la capacidad del DC-link no puede absorber sola esa energía** (harían falta más de 3 mF): hace falta el clamp de DCB-09. Ver 6.3 | C, P | AC (HW-03) |
| **DCB-09** | **Clamp disipativo en el bus de HV, común a los 10 módulos**: ~200 J en pulso no repetitivo, actuación por debajo de 520 V y por encima de 446 V, y **autoalimentado desde el propio bus**, porque debe actuar con la BT muerta. Se propone alojarlo en el módulo de precarga (DCB-04), fuera del alcance de esta PCB | C, P | TBD (HW-03, ME-I-08) |

### 4.4 Etapa de potencia (PWR)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| PWR-01 | Topología de puente en H completo | U | OK |
| PWR-02 | **MOSFET de SiC Infineon IMT65R010M2H** (650 V, 10 mΩ, PG-HSOF-8, con pin de fuente Kelvin). Se elige por disponibilidad: hay stock en el taller y en distribución, mientras que el SCT012H90G3AG del TFG está a 25 semanas de plazo. **La elección queda condicionada a resolver HW-03**: con 650 V el caso de fallo de 6.3 no es sobrevivible sin el clamp de DCB-09. Alternativa técnica si HW-03 no se cierra: SCT012H90G3AG (900 V), que lo resuelve solo con la capacidad ya existente. Comparativa completa en 6.4 | U, HD, C | AC (HW-02, HW-03) |
| PWR-03 | Frecuencia de conmutación de 20 kHz y modulación unipolar (TFG). Con la FPGA ambos parámetros pasan a ser configurables | TFG, P | TBD (FW-08) |
| PWR-04 | Los tiempos muertos se generan en la FPGA y son configurables, en lugar de fijarse con la red RC de 100 ns del TFG. **El diodo de cuerpo del IMT65R010M2H cae 4,3 V a 92 A**, así que el tiempo muerto debe ser el mínimo compatible con el desfase del driver y los tiempos de conmutación | P, HD | AC (FW-08) |
| PWR-05 | Refrigeración líquida mediante waterblock bajo la PCB; el agua se enfría en un acumulador térmico de PCM (fuera del alcance). En esta generación el waterblock puede tener otras dimensiones | U, TFG | OK |
| PWR-06 | Interfaz térmica y mecánica con el nuevo waterblock. **El encapsulado pasa a PG-HSOF-8 (TOLL)**: refrigera por la cara inferior con el pad de drenador a potencial de HV, igual que el H²PAK-7, pero con otra huella y otra área de pad | U, HD | TBD (ME-C-01) |
| **PWR-07** | **Inductancia del lazo de conmutación objetivo ≤ 15 nH.** Con 650 V el margen de sobreoscilación es la mitad que con 900 V: a 4 A/ns, 15 nH dan 60 V de pico (460 V, el 71 % del límite) y 25 nH dan 100 V (500 V, el 77 %). Ver 6.4 | C, P | TBD (HW-02) |

### 4.5 Gate driving (GD)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| GD-01 | Drivers aislados con alimentación bipolar de **+18 V / −3 V**, protección DESAT y Miller clamp. Los +18 V son la tensión a la que están especificadas RDS(on) y Qg en las hojas de datos de los dos MOSFET candidatos; los +20 V del TFG son el 87 % de la VGS máxima del IMT65R010M2H. Los −3 V son el 43 % del límite estático de −7 V y bastan para la inmunidad frente a encendido parásito (VGS(th) típica de 4,5 V). Driver propuesto: **STGAP3S6S**; alternativa: ADuM4146 grado A. Ver 6.5 | U, HD, P | AC (HW-02) |
| GD-02 | Los fallos internos del driver (DESAT, UVLO, sobretemperatura) se detectan por lógica programada (FPGA) y por lógica cableada | U | OK |
| GD-03 | Protección cruzada por hardware que impida el shoot-through aunque falle la FPGA. **Nota: el shunt de bobina no ve la corriente de un shoot-through**, así que esta protección y el DESAT son los únicos que la cubren | P, C | AC (HW-01) |
| GD-04 | Estado por defecto sin PWM o ante un fallo: **low-side en ON y high-side en OFF**, de modo que la corriente circula en rueda libre (como en el TFG) | U, TFG | OK |
| **GD-05** | **El UVLO del raíl positivo del driver debe estar referido a la masa aislada (GNDISO), no al raíl negativo.** Si se refiere al raíl negativo, con −3 V y un umbral de 10,5 a 14,5 V el raíl positivo puede caer hasta 7,5–11,5 V sin que salte la protección, y un SiC conduciendo a media puerta se va térmicamente. De los candidatos evaluados solo el STGAP3S lo declara así (R10); el 1ED31xx dice literalmente lo contrario (R12) y el ADuM4146 no lo documenta (R11) | HD, C | AC (HW-02) |
| **GD-06** | **El umbral de DESAT debe dimensionarse contra la RDS(on) del MOSFET.** La corriente de disparo es el umbral dividido por RDS(on) menos la caída del diodo de bloqueo: con 10 mΩ y umbral de 6 V son 600 A (458 A en caliente). El DESAT es un detector de cortocircuito duro y de shoot-through, **no** una protección de sobrecorriente de bobina | HD, C | AC (HW-01) |
| **GD-07** | El diodo de bloqueo del DESAT debe soportar más que la tensión máxima del bus, incluida la tensión de actuación del clamp, y ser de recuperación rápida | HD | AC (HW-01) |

### 4.6 Sensado y adquisición (SNS)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| SNS-01 | Medida de corriente de bobina aislada. El rango debe cubrir ±60 A con margen; el TFG usaba un shunt de 500 µΩ con AMC1302 y fondo de escala de ±100 A. **Además del camino de medida hace falta un comparador rápido sobre el shunt para SAF-04**: el retardo del AMC1302 (3 µs) no sirve como protección | U, TFG, C | AC (HW-02) |
| SNS-02 | Medida de la tensión de bus aislada. El fondo de escala debe cubrir la tensión de actuación del clamp con margen | U, TFG | OK |
| SNS-03 | Medida de la temperatura de bobina aislada: la NTC está en el dominio HV | U, TFG | OK |
| SNS-04 | No se requiere medir la temperatura de los MOSFET ni del waterblock | U | OK |
| SNS-05 | Conversión en la propia placa. **Reformulado en la v0.4:** la decisión no es ADC interno o externo, sino qué cruza la barrera. Con la opción A hay dos cadenas: **(a)** amplificador aislado más ADC, que puede ser el ADC interno del controlador, o **(b)** modulador ΔΣ aislado más filtro de decimación, que exige un periférico SDFM/DFSDM en la plataforma. La (b) es más inmune al ruido de conmutación y la (a) tiene mucha menos latencia. Ver 6.6.3 | U, C | TBD (FW-01, FW-09) |
| SNS-06 | Muestreo de corriente sincronizado con la PWM | P | AC (FW-01) |
| **SNS-07** | **Solo la medida de corriente necesita el camino rápido.** La tensión de bus (SNS-02) y la NTC (SNS-03) admiten amplificador aislado más ADC sin penalización, así que la decisión de FW-01 puede limitarse a un único canal | P | AC (FW-01) |
| **SNS-08** | **Objetivo de diseño:** que la huella del sensor de corriente admita las dos cadenas de SNS-05 sin rehacer el rutado, de modo que FW-01 no bloquee el layout. El shunt, su valor y su conexión Kelvin son comunes a las dos; lo que cambia es la pieza inmediatamente posterior. Pendiente comprobar la compatibilidad de huellas y de señales entre el AMC1302 y el AMC1306 | P | AC (HW-02, FW-01) |
| **SNS-09** | La latencia total de la cadena de medida de corriente debe entrar en el presupuesto de retardo del lazo. Con un periodo de PWM de 50 µs, un sinc3 con OSR = 128 a 20 MHz asienta en 19,2 µs y un SAR tarda centenas de ns. El valor admisible lo fija EM-C-03 (parámetro `t_meas_lat`) | C, P | TBD (EM-C-03, FW-01) |

### 4.7 Control y plataforma (CTL)

**Reformulada en la v0.4:** la plataforma deja de ser un dato de partida y pasa a ser la cuestión FW-09. Los requisitos se escriben sin nombrar fabricante.

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| CTL-01 | **Plataforma de control por definir: FPGA o microcontrolador de tiempo real.** La MachXO5-NX deja de ser la hipótesis única (v0.4). Criterios de aceptación en 5.4, candidatos en 6.6 | U, P | TBD (FW-09) |
| CTL-02 | La plataforma implementa el lazo de corriente, la PWM, los tiempos muertos, las protecciones programadas y la pila de comunicación | U, P | AC (FW-09, FW-06) |
| CTL-03 | Memoria de configuración. **Solo aplica a la vía FPGA:** la MachXO5-NX lleva flash interna; ¿hace falta una flash externa? | — | TBD (FW-03, FW-09) |
| CTL-04 | Conector de programación y depuración accesible (JTAG o SWD según la plataforma) y actualización en campo por el bus (p. ej. FoE en EtherCAT) | P | TBD (FW-04) |
| CTL-05 | Comportamiento ante pérdida de comunicación: timeout y rampa a 0 A, o mantener la consigna | — | TBD (FW-05) |
| CTL-06 | Identificación de la posición del módulo (HEMS 1–4 / EMS 1–6) con una placa idéntica para todos. **Vía propuesta en la v0.4:** el direccionamiento auto-incremental de EtherCAT da a cada esclavo su posición en la línea, así que si el orden del cableado es fijo y está documentado no hace falta selector físico ni jumpers (COM-08) | P | TBD (ME-I-06) |
| CTL-07 | El lazo de corriente debe ser estable y cumplir sus prestaciones con una inductancia de 1,92 a 117 mH (en el EMS varía unas 60 veces; ver 6.1). Para ello puede recibir el entrehierro por el bus o estimar L en línea. La arquitectura de control está pendiente | C, P, U | TBD (EM-C-02) |
| **CTL-08** | **Disparo de PWM por hardware, sin intervención del núcleo ni de la lógica programada**, a partir de comparadores con umbral programable y de entradas de fallo externas (DESAT, sobrecorriente de SAF-04, enable cableado). Tiempo de reacción objetivo por debajo de 1 µs. Es un criterio de aceptación de la plataforma (C3 en 5.4) y no sustituye a la lógica cableada independiente de SAF-02 | P, C | AC (HW-01, FW-09) |
| **CTL-09** | La plataforma debe disponer de coma flotante o capacidad equivalente para el ajuste de ganancias o la estimación de L en línea que pida EM-C-02. Con el rango de L de CTL-07, resolverlo en HDL es sustancialmente más caro que en C | P, C | AC (EM-C-02, FW-09) |

### 4.8 Comunicación con la VCU (COM)

**Ampliada en la v0.4** con las consecuencias de la topología en línea (ver 6.6.4).

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| COM-01 | EtherCAT como bus preferente, aún sin decisión definitiva | U | AC (FW-06) |
| COM-02 | Esclavo EtherCAT implementado por una de estas tres vías: **(a) ESC dedicado externo** (p. ej. LAN9252, que integra los dos PHY y se conecta por SPI/SQI); **(b) ESC integrado en el microcontrolador** (F28P65x, F2838x, XMC4800, RX72M); **(c) IP core de Beckhoff en FPGA** (licencia ET1825/26/27, de pago, admite MII, RMII o RGMII). Las vías (a) y (b) evitan la licencia del IP core, aunque las tres siguen necesitando el Slave Stack Code de Beckhoff por vía ETG | P, R3, R15-R18 | TBD (FW-06, FW-09) |
| COM-03 | **Topología en línea, no en estrella.** EtherCAT es intrínsecamente una línea: la trama entra por un puerto, el esclavo la procesa al vuelo y la saca por el otro; para ramificar haría falta un esclavo de tres puertos o un módulo de unión, y cada rama seguiría siendo una línea. Se montan **2 puertos en las 10 placas**, cada uno con sus magnéticos. **Lo que obliga a los dos es SYS-01, no el ESC**, que ya trae dos o tres dentro: el último esclavo de la línea funcionaría con uno solo, porque un puerto cerrado devuelve la trama automáticamente. El coste real no son los puertos sino los PHY (ver COM-02 y 6.6.4) | P, C | OK · implementación: TBD (FW-06) |
| COM-04 | Maestro EtherCAT en la VCU (plataforma por definir) y tiempo de ciclo por definir | — | TBD (FW-06) |
| COM-05 | Datos intercambiados: consigna, habilitación, modo, límites y parámetros hacia el Magnet Driver; corriente, tensión, temperaturas y fallos hacia la VCU | P | TBD (FW-07) |
| COM-06 | EEPROM SII del esclavo, física o emulada | R3 | TBD (FW-06) |
| **COM-07** | **Un esclavo sin alimentación abre la línea.** Si un Magnet Driver pierde la BT, los que están aguas abajo desaparecen del bus. Mitigación propuesta: **redundancia en anillo**, cerrando la línea desde el último Magnet Driver a un segundo puerto de la VCU. Cuesta un cable y hace el bus inmune a un corte en cualquier punto; si se adopta, los dos puertos se usan en las 10 placas. Ata ME-I-02 con SAF-07 | C, P | TBD (FW-06, ME-I-02) |
| **COM-08** | **Direccionamiento por posición.** El direccionamiento auto-incremental del esclavo da su posición en la línea sin hardware adicional, siempre que el orden del cableado sea fijo y esté documentado. Es la vía más barata para CTL-06 y ME-I-06 con placa única | P | AC (ME-I-06, CTL-06) |

### 4.9 Alimentación auxiliar (AUX)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| AUX-01 | Alimentación de baja tensión desde la batería de BT (**24 V máximo**), o por PoE o una solución similar | U | 24 V máx.: OK · método: TBD (ME-I-02) |
| AUX-02 | Raíles necesarios: núcleo e I/O de la FPGA, PHY, **cuatro fuentes aisladas de +18 V / −3 V** para los drivers y una fuente aislada para el sensado en HV. **Cada canal consume unos 0,2 W** (113 nC × 21 V × 20 kHz de puerta más el reposo del driver), así que 1 W por módulo sobra y los 2 W del MGJ2 del TFG están 10 veces sobredimensionados. **Ningún módulo de catálogo da +18 V**: ver el aviso de la sección 3 de `componentes.md` (postregular 19 V, aceptar 15 V, o topología propia). Mantener la capacidad de barrera en el orden de 3 pF para no degradar el CMTI | P, C, HD | AC (HW-05, HW-02) |
| AUX-03 | Tensión mínima de entrada BT y consumo máximo permitido | — | TBD (ME-I-02) |

### 4.10 Protecciones y seguridad (SAF)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| SAF-01 | Fallos detectados: fallos internos del gate driver, temperatura de bobina y tensión de bus | U | OK |
| SAF-02 | Cada fallo se detecta por lógica programada (en el controlador) y por lógica cableada independiente. **Esta exigencia no depende de FW-09:** la lógica cableada es hardware aparte en todas las vías, y el disparo por hardware interno de CTL-08 no la sustituye | U | OK |
| SAF-03 | El Magnet Driver recibe órdenes de forma redundante: por EtherCAT (o el protocolo elegido) y por **señales cableadas de enable y fault** | U | OK · señales, niveles y conectores: TBD (ME-I-01) |
| SAF-04 | Varias protecciones analógicas o de lógica cableada en la propia placa, además de DESAT. **En particular un comparador rápido de sobrecorriente sobre el shunt de bobina**, que es el que de verdad cubre la sobrecorriente: el DESAT dispara a cientos de amperios (GD-06) | U, C | OK · cuáles y umbrales: TBD (HW-01) |
| SAF-05 | Estado seguro: **rueda libre por los low-side**. La energía de la bobina se disipa en su propia resistencia (ver 6.3) | U | OK |
| SAF-06 | Tiempo de respuesta de cada protección | — | TBD (HW-01) |
| SAF-07 | La rueda libre debe mantenerse aunque se pierda la alimentación de BT o falle un driver. **Nota de la v0.4: la pérdida de BT en un módulo también lo saca del bus y corta la línea aguas abajo (COM-07).** **Si no se garantiza, el camino alternativo es el clamp de bus de DCB-09.** Se descarta la retención local (mantener alimentados los drivers low-side) por dos razones: el peor EMS tiene L/R de 98 ms, lo que obliga a sostener el ON unos 500 ms y a 400–800 µF por módulo, y además haría falta un enclavamiento en el lado HV que fuerce el ON cuando desaparece la BT, porque la salida por defecto del driver es LOW. Ver 6.3 | C, P | AC (HW-03) |
| SAF-08 | Las protecciones de hardware se pueden desactivar fácilmente (jumpers o similar) | U | OK · método: TBD (HW-01) |
| SAF-09 | La FPGA lee el estado de esos jumpers y lo reporta por el bus, para que no se opere con protecciones desactivadas sin saberlo | P | AC (HW-01) |

### 4.11 Aislamiento (ISO)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| ISO-01 | Aislamiento galvánico entre HV y LV | U | OK |
| ISO-02 | Separación ≥ 4 mm con coating entre HV y LV (regla de la competición, vigente) | U, TFG | OK |
| ISO-03 | ≥ 2 mm entre distintas redes de HV | TFG | AC (HW-04) |
| ISO-04 | ≥ 4 mm entre los taladros de fijación del waterblock y cualquier conductor | TFG | AC (ME-C-01) |
| ISO-05 | Tensión de aislamiento y tipo de aislamiento (básico o reforzado). **Si se pide reforzado con margen, tener en cuenta que el STGAP3S declara VIORM de 1,2 kV pico frente a los 2,15 kV pico del ADuM4146**; los dos superan los 8 mm de fuga y cubren 600 V continuos | —, HD | TBD (HW-04) |
| ISO-06 | Distancias de aislamiento dimensionadas para la tensión continua de DCB-02 | U, C | AC (HW-04, HW-08) |

### 4.12 Mecánica, fabricación y entorno (MEC)

| ID | Requisito | Fuente | Estado |
|---|---|---|---|
| MEC-01 | Tamaño de la placa por acordar: el waterblock puede cambiar de dimensiones en esta generación (el TFG estaba limitado a 190 × 100 mm) | U, TFG | TBD (ME-C-01) |
| MEC-02 | Altura máxima de componentes de 40 mm. **Cambiar el MGJ2 (inserción) por un módulo SMD baja el perfil y elimina 4 componentes de inserción** | TFG, P | AC (ME-C-01) |
| MEC-03 | PCB de 6 capas simétrica con cobre de 2 oz (el TFG usaba el stackup de NCAB); fabricante por definir | TFG, U | AC (PT-01) |
| MEC-04 | Herramienta EDA: **KiCad** (el TFG usaba Altium Designer) | U | OK |
| MEC-05 | Operación a **temperatura y presión atmosféricas**, no en vacío. A diferencia de lo que suponía el TFG, hay convección | U | OK |
| MEC-06 | Valores numéricos del rango de temperatura ambiente (el TFG asumía ≥ 25 °C por competir en verano) | TFG | TBD (ME-C-02) |
| MEC-07 | Conectores de potencia, de bus de campo, de lógica cableada, de NTC y de alimentación BT | — | TBD (ME-I-04) |
| MEC-08 | Nivel de vibraciones (depende en parte del propio convertidor) | U | TBD (ME-I-05) |
| MEC-09 | Fabricación y montaje: fabricante de PCB y capacidad de montaje de BGA. **El PG-HSOF-8 es un encapsulado sin patillas (TOLL): requiere inspección de soldadura por rayos X o al menos un proceso de pasta controlado** | U, HD | TBD (PT-01, PT-02) |

---

## 5. Arquitectura de la PCB

### 5.1 Diagrama de bloques (opción A, propuesta)

```
 HV+ / HV- (bus compartido, 320-400 V)   ◄──► resto de Magnet Driver (estrella, DCB-05)
   │                                      ◄──► módulo de precarga + CLAMP DE BUS (DCB-09)
 ┌─┴──────────────────────── DOMINIO HV ───────────────────────────────────────┐
 │ [Fusible]─►[DC-link film+cerámicos]─►[Puente H SiC x4]─►[Shunt]─► BOBINA     │
 │      │                                    ▲                │        │ NTC    │
 │ [Divisor Vbus]                 [Gate drivers aislados x4]   │        │        │
 │      │                         [Fuentes aisladas +18/-3 x4] │        │        │
 │      │                          ▲ DESAT + Miller clamp      │        │        │
 │ [Medida aislada Vbus]         [Medida aislada Ibob]  [Medida aislada Tbob]     │
 │                               [Comparador rápido OC]  (SAF-04)                │
 └══════╪══════════════════════ BARRERA DE AISLAMIENTO ══════╪═══════════╪═════════┘
 ┌──────┴────────────────────── DOMINIO LV ──────────────────┴───────────┴────────┐
 │  [Adquisición: ΔΣ + filtro de decimación  ó  amplificador aislado + ADC]        │
 │                │                                    (SNS-05, decide FW-01)      │
 │  [CONTROLADOR: FPGA o MCU de tiempo real — FW-09]                               │
 │       │      │   lazo de corriente · PWM + tiempos muertos · disparo por         │
 │       │      │   hardware (CTL-08) · protecciones programadas · esclavo EtherCAT │
 │       │      └──►[Lógica cableada de protección]──► inhibición de los drivers   │
 │       │                 ▲ DIAG/RDY de los drivers, OC, Tbob, Vbus, VCU         │
 │  [ESC: integrado en el MCU, externo (LAN9252) o IP core en la FPGA] — COM-02     │
 │  [PHY 1]─[Magnéticos]─► EtherCAT IN      [PHY 2]─[Magnéticos]─► EtherCAT OUT    │
 │       (0 PHY externos si el ESC los integra, como el LAN9252)                    │
 │  [EEPROM SII] [Oscilador] [JTAG/SWD] [LEDs] [ID de posición → COM-08]            │
 │  [Alimentación auxiliar: entrada BT/PoE ─► raíles LV + fuentes aisladas hacia HV]│
 └────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Posición de la barrera de aislamiento: decisión pendiente (HW-05, FW-01)

**Nota de la v0.4: esta decisión no depende de FW-09.** Todos los candidatos de 6.6 admiten la opción A, así que HW-05 se puede cerrar antes que la plataforma, y cerrarla desbloquea AUX-02, las fuentes aisladas y buena parte del floorplan.

| | **Opción A: controlador en el dominio LV** (propuesta) | **Opción B: controlador en el dominio HV** |
|---|---|---|
| Qué cruza la barrera | Las 3 medidas analógicas, las 4 señales de puerta y la alimentación | El bus de campo, las señales cableadas de la VCU y la alimentación |
| Sensado | Moduladores ΔΣ aislados (familia AMC13xx; el controlador hace el filtro sinc, lo que exige SDFM/DFSDM) o amplificador aislado + ADC. Ver 6.6.3 | ADC interno sin aislamiento, cerca del shunt: la discusión del ΔΣ desaparece |
| Depuración | JTAG seguro con HV presente | JTAG referido a HV: hace falta un depurador aislado |
| Continuidad con el TFG | Alta: reutiliza su filosofía de aislamiento | Baja |
| Riesgos | Más fuentes aisladas y latencia de los ΔΣ (SNS-09) | Aislamiento de EtherCAT y de la lógica de seguridad; riesgo en pruebas |

### 5.3 Bloques: qué se hereda del TFG y qué es nuevo

| Bloque | Base en el TFG | Cambio |
|---|---|---|
| Puente en H | Sí, sin ensayar | **MOSFET nuevo: IMT65R010M2H, 650 V, PG-HSOF-8** (PWR-02). Cambia huella, área de pad y diseño térmico. Objetivo de inductancia de lazo ≤ 15 nH (PWR-07) |
| DC-link | Sí, sin ensayar | Los 105 µF se mantienen para el rizado; el caso de fallo lo resuelve el clamp de bus, no la capacidad (6.3). Los condensadores de film pasan de 500 V a 630 V |
| Gate drivers | Sí, sin ensayar | **Driver nuevo propuesto: STGAP3S6S** (GD-01, 6.5). Raíles a +18/−3 V. Los tiempos muertos y el reset pasan a la FPGA; el estado por defecto sigue siendo rueda libre por los low-side (SAF-05). El Miller clamp pasa a MOSFET externo (poblable o no) |
| Fuentes aisladas de puerta | MGJ2, 2 W, inserción | Sobredimensionadas 10 veces: se puede bajar a 1 W y a SMD. Pendiente resolver el raíl de 18 V (AUX-02) |
| Sensado | Sí (salida analógica hacia la LCU) | Ahora se digitaliza en placa, **más un comparador rápido de sobrecorriente** (SAF-04) |
| Lógica ready/fault | Puertas AND con salida hacia la LCU | Se integra en la lógica cableada de protección, desactivable por jumpers (SAF-08). Ahora incluye DIAG, RDY y sobretemperatura del driver |
| Protección del caso de fallo | No existía | **Nuevo: clamp de bus de ~200 J fuera de la placa** (DCB-09) |
| Controlador y control | No | Nuevo. Plataforma por decidir en FW-09 (5.4 y 6.6) |
| EtherCAT | No | Nuevo. Línea de 2 puertos, no estrella (COM-03). El ESC puede ir integrado en el controlador, externo o como IP core (COM-02) |
| Alimentación auxiliar | Parcial: recibía +3V3, +5V y VBAT por el conector | Nueva etapa de entrada BT/PoE |

### 5.4 Plataforma de control: criterios de aceptación y orden de decisión

**Nuevo en la v0.4.** La elección de plataforma **no la decide dónde estén los puertos EtherCAT**, porque todos los candidatos viables los tienen. Se acuerda este orden de decisión:

1. **Hardware acota:** fija los criterios de aceptación de la tabla siguiente, sin nombrar fabricante. No dependen de quién programe.
2. **Se comprueba qué candidatos los cumplen** (sección 6.6). No es una lista de uno.
3. **Firmware elige dentro de ese conjunto**, y con peso real: es quien va a mantener el código a lo largo de los relevos del equipo, y un toolchain que nadie domina es un riesgo de calendario tan serio como un periférico que falta.

El orden inverso —Firmware elige y Hardware comprueba si se puede— es el que llevó a la hipótesis de la MachXO5-NX sin un análisis previo de lo que el lazo necesita. Invertirlo evita que la comprobación llegue cuando ya hay compromiso con una plataforma.

| # | Criterio de aceptación | Requisitos |
|---|---|---|
| C1 | Dos puertos EtherCAT disponibles en un encapsulado montable según PT-02 | COM-03, PT-02 |
| C2 | Cadena de sensado aislada resuelta: periférico SDFM/DFSDM si se elige ΔΣ, o ADC interno suficiente si se elige amplificador aislado | SNS-05, FW-01 |
| C3 | Disparo de PWM por hardware sin intervención del núcleo, con umbral programable y reacción por debajo de 1 µs | CTL-08, SAF-04, HW-01 |
| C4 | Tiempos muertos configurables por hardware, con resolución compatible con el desfase entre drivers (10 ns en el STGAP3S6S) | PWR-04, FW-08 |
| C5 | Coma flotante o capacidad equivalente para el ajuste de ganancias o la estimación de L en línea | CTL-09, CTL-07, EM-C-02 |
| C6 | **Margen deliberado en cómputo y en pines.** EM-C-01 y EM-C-03 siguen abiertas: ajustar la plataforma contra requisitos que no están cerrados es la forma habitual de acabar cambiando de micro a mitad del layout | EM-C-01, EM-C-03 |

---

## 6. Comprobaciones preliminares [C]

Salvo que se indique otra cosa, los cálculos usan R = 1,2 Ω (medida en la bobina construida) e I = 60 A.

### 6.1 Inductancia de los electroimanes del prototipo H11 (R5, R6, R7)

Sin cambios respecto a la v0.2.

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
- **Los datos cubren hasta ±55 A.** Para 60 A hay que extrapolar o pedir mapas ampliados. Escalando por (60/55)² la energía del peor caso pasa de 16,7 J a unos **20 J por módulo**.
- **La corriente nula en los HEMS** (LOAD-04) es coherente con el flujo del imán, que sostiene el peso.

### 6.2 Potencia durante el pico de 2 s

Con la duración del pico confirmada en 2 s [U]:

- La tensión en bornes de la bobina es 72 V y disipa 4,3 kW, es decir **8,6 kJ en los 2 s**. Es el dato que condiciona el térmico de la bobina y el umbral de `T_coil_max`, no el de la PCB.
- La corriente media del bus es de 13,5 A a 320 V y de 10,8 A a 400 V por Magnet Driver, sin contar pérdidas. El fusible de 15 A del TFG aguanta 10,8 A durante 2 s, pero el factor de utilización queda en 0,72, justo en el criterio `k_fuse`.
- **Si los 10 electroimanes pican a la vez, el bus entrega unos 108 A.** Con el bus encadenado, la primera placa de la cadena tendría que conducirlos: **el encadenado deja de ser viable y la distribución pasa a estrella** (DCB-05). Falta que Electromagnetics confirme si el pico es simultáneo o escalonado (EM-C-05).
- Pérdidas de conducción en el puente durante el pico, con dos dispositivos en serie en el camino de corriente:

| MOSFET | A 25 °C | A 175 °C (típ.) | Por dispositivo a 25 °C |
|---|---|---|---|
| IMT65R010M2H (10 mΩ) | 72 W | 115 W | 36 W |
| SCT012H90G3AG (12 mΩ) | 86 W | 133 W | 43 W |

- **A 2 s el die está prácticamente en régimen permanente**, así que el salto de temperatura se evalúa con `Rthjc`, no con la impedancia térmica transitoria: 36 W × 0,22 K/W = **8 K** de unión a cápsula. El término dominante es el camino cápsula → PCB → waterblock (`Rth_wb`), que sigue siendo TBD (ME-C-01).

### 6.3 Desmagnetización, estado seguro y caso de fallo

**Funcionamiento normal (estado seguro elegido, SAF-05).**

- Con los low-side en ON, la bobina queda cortocircuitada y su corriente decae sobre su propia resistencia (1,2 Ω más la de los MOSFET y el shunt, que es despreciable). No se devuelve energía al bus.
- **Constante de tiempo orientativa (L/R):**
  - HEMS: de 5 a 9 ms.
  - EMS: de 1,6 a 98 ms, según el punto de trabajo.
  - La corriente cae prácticamente a cero en unas pocas constantes de tiempo.
- **Observación:** con la bobina cortocircuitada, un cambio de entrehierro induce corriente, sobre todo en los HEMS por el flujo del imán. El efecto es un amortiguamiento (EM-C-04).

**Caso de fallo: la rueda libre no es posible (DCB-08, DCB-09, SAF-07).**

Si los drivers se quedan sin alimentación o se apagan por un fallo, los MOSFET de SiC quedan en OFF y la corriente vuelve al DC-link por los diodos de cuerpo.

**Novedad de la v0.3: hay que distinguir dos escenarios, porque el bus es compartido (DCB-03) y los 10 DC-link están en paralelo (≈ 1050 µF).**

| Escenario | Energía | Pico desde 400 V | % de 650 V | % de 900 V |
|---|---|---|---|---|
| Falla **un solo** módulo (los otros 9 DC-link absorben) | 17 J | **438 V** | 67 % | 49 % |
| Fallan **los 10** (pérdida de BT o parada de emergencia), a 55 A | 167 J | **691 V** | 106 % | 77 % |
| Fallan **los 10**, escalado a 60 A | 200 J | **735 V** | 113 % | 82 % |

- **El fallo de un módulo aislado es inofensivo.** El caso que dimensiona es el **fallo común**, que es además el probable: una pérdida de BT o una parada de emergencia afecta a los 10 módulos a la vez, y si además abre los contactores, la batería ya no puede absorber la energía.
- **Con un MOSFET de 650 V la capacidad sola no lo resuelve.** Para no pasar de 520 V (el 80 % de 650 V, criterio `k_vds` de la propia hoja de datos R8) harían falta **más de 3 mF** de film. No caben en el vehículo.
- **Con un MOSFET de 900 V sí bastaría la capacidad:** para no pasar de 720 V harían falta 930 µF (167 J) o 1120 µF (200 J), es decir aproximadamente los 1050 µF que ya hay en el bus, cambiando los condensadores de film de 500 V a 800 V.
- **Conclusión:** elegido el IMT65R010M2H, **el clamp de DCB-09 es obligatorio**. Especificación de partida:
  - energía: **~200 J** en pulso no repetitivo (dos resistencias de potencia lo absorben);
  - actuación: por debajo de **520 V** (`V_clamp_lim`) y por encima de **446 V** (`k_chop_mrg` × `Vbus_max`); se propone 500 V;
  - **autoalimentado desde el propio bus**, con disparo por referencia Zener o comparador alimentado del bus, porque tiene que actuar con la BT muerta;
  - **uno para todo el vehículo, no uno por placa**: se propone alojarlo en el módulo de precarga (DCB-04), lo que libera área en las 10 placas (ME-I-08).
- **Opción descartada: retención local.** Mantener el ON de los low-side durante 5 constantes de tiempo del peor EMS (98 ms → unos 500 ms) pide 400–800 µF en el raíl del driver, lo que es viable, pero además haría falta un enclavamiento en el lado HV que fuerce el ON al desaparecer la BT, porque la salida por defecto del driver es LOW. Es circuitería nueva en diez placas frente a un circuito en una.
- **Cota pesimista que se mantiene** (26,7 mH constantes a 60 A, 48 J por módulo): queda como techo superior mientras EM-D no dé los mapas a 60 A (EM-D-03) ni el rango de las bobinas nuevas (EM-D-04).

### 6.4 Elección del MOSFET (PWR-02)

Los dos candidatos están disponibles por patrocinio, así que la comparación es técnica; la disponibilidad entra solo como cantidad y plazo de reposición.

| | **IMT65R010M2H** (Infineon) | **SCT012H90G3AG** (ST) |
|---|---|---|
| VDS | 650 V | 900 V |
| Utilización a 400 V | 62 % | 44 % |
| Pico de conmutación estimado (15 nH, 4 A/ns) | 460 V = 71 % | 460 V = 51 % |
| RDS(on) típ. 25 °C / 175 °C | 10 / 16 mΩ | 12 / 18,5 mΩ |
| Pérdida de conducción a 60 A (2 en serie) | 72 W | 86 W |
| RthJC | 0,22 K/W | 0,24 K/W |
| ΔT unión-cápsula en el pico de 2 s | 8 K | 10 K |
| ID continua (Tc = 25 °C) | 168 A | 110 A |
| VGS estática máx. | −7 a +23 V | −10 a +22 V |
| VGS transitoria | −10 a +25 V (≤ 500 ns, ≤ 1 %) | no especificada |
| VGS recomendada | +18 / 0 V | +18 / −5 V |
| VGS(th) típ. | 4,5 V | — |
| Margen con apagado a −3 V | 43 % del límite | 30 % del límite |
| Margen con apagado a −5 V | 71 % del límite | 50 % del límite |
| Diodo de cuerpo | 4,3 V a 92 A | 2,8 V a 60 A |
| Encapsulado | PG-HSOF-8 (TOLL) | H²PAK-7 |
| **Caso de fallo de 6.3** | **exige clamp (DCB-09)** | se resuelve con la capacidad ya existente |
| Plazo de reposición (19/09/2026) | con stock | 25 semanas |

**Lectura.** En operación normal los dos valen: incluso con un layout mediocre (25 nH, 4 A/ns) el pico de conmutación se queda en el 77 % de los 650 V. Térmicamente tampoco discriminan, porque a 2 s manda el camino hacia el agua. Las diferencias reales son dos:

1. **El caso de fallo.** Es la única diferencia cualitativa: con 900 V se cierra con condensadores, con 650 V hace falta un circuito nuevo.
2. **El margen de puerta con apagado negativo.** El ST admite −10 V estáticos y el Infineon −7 V. Con −3 V los dos quedan cómodos; con −5 V el Infineon queda al 71 %, que cumple su propio criterio del 80 % pero es menos holgado.

**Se elige el IMT65R010M2H** por cantidad y plazo, **con el clamp de DCB-09 como condición**. Si HW-03 no se cierra, la vía de repliegue es el SCT012H90G3AG.

**Nota importante sobre los datos.** La columna del IMT65R010M2H en `componentes.md` tenía diecisiete parámetros que no correspondían a R8; se ha rehecho completa el 19/09/2026. El más grave era VGS mínima, que figuraba como −20 V frente a los −7 V reales. Además, Eon/Eoff de los dos candidatos están medidos con RG y condiciones distintas (3,3 Ω / 400 V / 92,1 A frente a 15 Ω / 600 V / 60 A) y **no se pueden comparar sin reescalar**.

### 6.5 Elección del gate driver (GD-01, GD-05)

Con alimentación bipolar, el criterio que separa a los candidatos no es la corriente de salida ni el CMTI, sino **dónde está referido el UVLO del raíl positivo** (GD-05).

| | **ADuM4146** (TFG) | **STGAP3S6S** (propuesto) | **1ED3124MU12H** (descartado) |
|---|---|---|---|
| Corriente de salida | 4 A a 2 Ω (11 A cc) | 6 A / 10 A | 14 A |
| CMTI | 100 kV/µs | 200 kV/µs | 200 kV/µs |
| Retardo / desfase entre piezas | 75 ns / 25 ns | 75 ns / 10 ns | 90 ns / 5 ns |
| DESAT | < 2 µs, máscara 300 ns, umbral 9,2 V (grado B) o 3,5 V (A y C) | 150 ns, umbral 6 V, soft-off ajustable | **no tiene** |
| Miller clamp | integrado | pre-driver con MOSFET externo | integrado solo en el 1ED3122 |
| **UVLO del raíl positivo** | 11,5 V (B/C) o 14,5 V (A), **referencia sin declarar** | **13,6 V referido a GNDISO** | 10,5 V, **referido a VEE2** |
| Sobretemperatura | no | 164 °C | no |
| Aislamiento / fuga / VIORM | 5 kVrms / 8,3 mm / 2150 Vpk | 5,7 kVrms / 8 mm / 1200 Vpk | 5,7 kVrms / > 8 mm / — |
| Encapsulado | SOIC-16W | SO-16W | PG-DSO-8 |
| Precio 1 ud. (19/09/2026) | 7,99 $ | 3,40 € | — |

**Se propone el STGAP3S6S** porque es el único de los tres que garantiza la referencia del UVLO a la masa aislada, además de intervenir el DESAT en 150 ns, llevar apagado suave ajustable y protección por sobretemperatura, y mantener la huella SO-16W. Contrapartidas a asumir:

- el Miller clamp necesita un MOSFET pequeño por canal (4 en total); con −3 V y VGS(th) mínima de 3,5 V conviene poblarlo, aunque el margen es razonable;
- su VIORM es la mitad que la del ADuM4146: revisar en ISO-05 si se quiere aislamiento reforzado con más margen;
- **el stock era escaso en distribución el 19/09/2026 (2 unidades en RS España)**: hay que verificarlo antes de comprometer el diseño;
- su umbral de DESAT (6 V) dispara a 600 A con 10 mΩ (458 A en caliente), peor que los 3,5 V de los grados A y C del ADuM4146, que disparan a 350 A (267 A en caliente). En los dos casos el DESAT es un detector de cortocircuito duro, no de sobrecorriente de bobina (GD-06).

**Alternativa si el STGAP3S no se consigue:** ADuM4146 **grado A** (UVLO 14,5 V, umbral de DESAT 3,5 V), con la condición de confirmar con ADI a qué referencia mide el UVLO con alimentación bipolar.

**Sin verificar:** la familia EiceDRIVER X3 Enhanced (1ED34xx analógica, 1ED38xx configurable por I²C) tiene DESAT y Miller clamp integrados y sería el emparejamiento de un solo fabricante con el MOSFET, pero su hoja de datos no es accesible sin registro (HW-09).

### 6.6 Plataforma de control: candidatos (FW-09)

**Nuevo en la v0.4.** Análisis de partida para la decisión de FW-09, con los criterios C1 a C6 de 5.4.

#### 6.6.1 Tres vías de solución

**Vía 1: microcontrolador de tiempo real con ESC integrado.** No hace falta ASIC de comunicación ni licencia de IP core.

| Familia | Núcleo | Interfaz ΔΣ nativa | Encapsulado más pequeño **con EtherCAT** | Nota |
|---|---|---|---|---|
| **Infineon XMC4800 / XMC4300** (R16) | Cortex-M4, 144 MHz, FPU y DSP | 4 demoduladores ΔΣ | **LQFP100, 14 × 14 mm** | El único que mete el ESC en un QFP de 100 pines. Paquete de seguridad funcional para SIL-2/3; disponibilidad declarada hasta 2031 o más; compatible en pines y código con el resto de la familia XMC4000. **Verificar cuántos puertos saca el LQFP100** |
| **Renesas RX72M** (R17) | RXv3, 240 MHz, FPU de doble precisión | interfaz de modulador Δ-Σ | LFQFP de 100, 144 y 176 pines; BGA de 176 y 224 | El más potente del grupo; acelerador trigonométrico orientado a control de motores. **Verificar en qué encapsulados sale el ESC de 2 canales** |
| **TI C2000 F28P65x** (R15) | 2 × C28x, 200 MHz | 16 canales SDFM | 176 QFP (24 × 24 mm) o BGA de 256 bolas (13 × 13 mm, paso 0,8 mm) | La tabla de comparación de R15 es explícita: **el ESC no está ni en el QFP de 100 pines ni en el BGA de 169 bolas**. Lockstep y Functional Safety-Compliant |
| **TI C2000 F2838x** | 2 × C28x + Cortex-M4 | 8 canales SDFM | 176 QFP | El M4 puede llevar las comunicaciones de forma separada del control |
| TI Sitara AM243x | Cortex-R5F + PRU-ICSSG | vía PRU | solo BGA | Queda fuera por PT-02 salvo que se acepte BGA |

**Vía 2: controlador pequeño más ESC externo.** El **LAN9252** (R18) integra **los dos PHY dentro**, en QFN64 o TQFP-EP64, y se conecta por SPI/SQI con unos 6 pines. Desaparecen los dos PHY externos, sus cristales y sus straps; quedan magnéticos y RJ45. Coste: la latencia del PDI por SPI, irrelevante para un lazo local a 20 kHz con ciclo de bus de 1 kHz. Las salidas SYNC0/SYNC1 del reloj distribuido siguen disponibles para sincronizar la PWM.

Candidatos de controlador con interfaz ΔΣ nativa: **TI F28003x / F28004x** (R19: LQFP de 64, 80 y 100 pines, 8 canales SDFM, 4 CMPSS con DAC de referencia de 12 bits, 16 canales ePWM con dead-band y trip zones, CLA, FPU y TMU a 120 MHz), **STM32H7 con DFSDM** (R20: LQFP100 de 14 × 14 y LQFP144 de 20 × 20; el H723 no llega a 176 pines) y **XMC4400 / XMC4500**. El STM32G4 **no** tiene interfaz ΔΣ: obligaría a amplificador aislado más SAR, que es una cadena válida pero es otra decisión de HW-02.

**Vía 3: FPGA con IP core de Beckhoff.** Es la hipótesis de la v0.3 y sigue en la mesa. Su coste diferencial es la licencia (PT-03) y el HDL del filtro sinc y del ajuste de ganancias de CTL-07.

#### 6.6.2 El tamaño del encapsulado no es el criterio

| Encapsulado | Cuerpo | Con patillas | Paso |
|---|---|---|---|
| TI PTP176 (HLQFP, R15) | 24 × 24 mm | 26 × 26 mm | 0,5 mm |
| STM32H723 LQFP144 (R20) | 20 × 20 mm | 22 × 22 mm | 0,5 mm |
| STM32H723 LQFP100 · XMC4800 LQFP100 | 14 × 14 mm | 16 × 16 mm | 0,5 mm |
| TI ZEJ256 (nFBGA, R15) | 13 × 13 mm | — | 0,8 mm |

- Entre el mayor y el menor hay un factor de 2,9 en área, pero sobre una placa del orden de 190 × 100 mm la diferencia es **del orden del 1 % del área total**: no es el criterio que debe decidir.
- **Lo que sí pesa del PTP176 es el PowerPAD:** no es un LQFP normal, lleva pad térmico expuesto que hay que soldar a una isla de cobre con su campo de vías, y el plano del encapsulado avisa de que su tamaño puede variar por requisitos de línea de fuga. En una placa con barrera de aislamiento y waterblock debajo esa isla molesta más que los 4 mm de lado.
- **El BGA de 0,8 mm no es el BGA de PT-02.** El ZEJ256 de 13 × 13 mm se rutea en 6 capas con vías normales; es otra liga que un paso de 0,5 mm.
- **La comparación justa incluye el ESC.** Sumando el QFN64 del LAN9252 (unos 9 × 9 mm) a un LQFP144, el área total queda cerca de la del PTP176 solo. La diferencia de tamaño casi se cancela.

#### 6.6.3 ¿Importa la interfaz ΔΣ si el controlador ya tiene ADC internos?

La pregunta no es si el controlador tiene ADC, **sino dónde está la barrera** (HW-05). Con la opción A el shunt está en HV y el controlador en BT, así que algo tiene que cruzar el aislamiento:

| | **Amplificador aislado** (AMC1302, TFG) | **Modulador ΔΣ aislado** (AMC1306 / AMC1336) |
|---|---|---|
| Qué cruza y recorre la placa | señal analógica diferencial de pocos cientos de mV | flujo de bits a 10–20 MHz |
| Periférico necesario | ADC, que puede ser el interno del controlador | SDFM / DFSDM |
| Inmunidad en un convertidor de 400 V a 20 kHz | menor: la analógica recoge ruido justo entre la barrera y el ADC | mayor: un bitstream digital no lo recoge |
| Latencia | centenas de ns (SAR) | 5 a 10 µs según el sobremuestreo (sinc3, OSR 128 a 20 MHz: 19,2 µs; OSR 64: 9,6 µs) |
| Disparo rápido por hardware | comparador analógico del controlador (CMPSS o equivalente) | filtro comparador del SDFM, que reacciona sin pasar por el núcleo |

- Con un periodo de PWM de 50 µs la latencia del sinc **cabe**, pero tiene que entrar en el presupuesto de retardo cuando EM-C-03 fije el ancho de banda (SNS-09, parámetro `t_meas_lat`).
- **Solo la corriente necesita el camino rápido** (SNS-07): Vbus y la NTC pueden ir por amplificador aislado y ADC. Puede que solo haga falta un canal ΔΣ.
- **Las dos vías dan la protección cableada de HW-01**, una por el filtro comparador del SDFM y la otra por el comparador analógico.
- **Con la opción B la discusión desaparece:** el ADC interno lee el shunt directamente. El ΔΣ es el precio de tener el controlador en el lado seguro.

#### 6.6.4 Los dos puertos EtherCAT

- **EtherCAT es intrínsecamente una línea.** La trama entra por un puerto, el esclavo la procesa al vuelo y la saca por el otro. La estrella habitual de Ethernet no existe: para ramificar hace falta un esclavo de tres puertos o un módulo de unión, y cada rama sigue siendo una línea. Un cable de la VCU al primer Magnet Driver y luego 1→2, 2→3… ahorra la mitad del mazo frente a una estrella.
- **El ESC ya trae dos o tres puertos dentro.** No se «añade» un segundo puerto: se decide cuántos se sacan a la placa. El último esclavo de la línea funciona con uno solo, porque un puerto cerrado o sin conectar devuelve la trama automáticamente.
- **Lo que obliga a montar dos en las diez placas es SYS-01.** Coste real: un conector y un PHY sin usar en una de cada diez placas, mucho más barato que mantener dos variantes de PCB.
- **El coste no es «dos puertos», es «dos PHY».** El ESC integrado ahorra el ASIC pero no los PHY; el LAN9252 ahorra los PHY pero no el ASIC. Por eso la comparación de área de 6.6.2 acaba casi empatada.
- **Con redundancia en anillo** (COM-07) los dos puertos se usan en las diez placas, y el maestro sobrevive a un corte en cualquier punto.
- **EBUS**, la variante LVDS de EtherCAT que va sin PHY ni magnéticos, es la única vía para bajar de dos PHY, pero solo lo implementan los ESC de Beckhoff (ET1100, ET1200), no los integrados en micro, y tiene alcance corto entre nodos. Se deja constancia en FW-06; **no se propone**.

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
| EM-C-01 | Perfil de corriente: **falta la corriente eficaz en crucero** en HEMS y EMS y la corriente nominal del EMS. La duración del pico ya está cerrada en 2 s | LOAD-04, LOAD-05, DCB-06, térmica |
| EM-C-02 ★ | Arquitectura de control (pendiente). ¿El Magnet Driver recibe el entrehierro de la VCU para ajustar las ganancias, estima L en línea o usa un control robusto? | CTL-07, COM-05 |
| EM-C-03 | Ancho de banda del lazo de corriente y rizado máximo admisible | LOAD-06, LOAD-07, PWR-03, SNS-05 |
| EM-C-04 | En rueda libre, un cambio de entrehierro induce corriente en la bobina, sobre todo en los HEMS. ¿Es aceptable o incluso deseable como amortiguamiento? | SAF-05, 6.3 |
| **EM-C-05 ★** | **¿Pican los 10 electroimanes a la vez o de forma escalonada?** Decide los 108 A del bus (topología en estrella, DCB-05) y si el clamp de DCB-09 se dimensiona para 200 J o para 20 J | DCB-05, DCB-09, 6.2, 6.3 |

### 7.2 Electromagnetics – Design (EM-D)

| ID | Cuestión | Afecta a |
|---|---|---|
| EM-D-01 | Ficheros MATLAB del EMS: vectores de ejes (hipótesis: filas = corriente de ±55 A; columnas = entrehierro) y valor del entrehierro en cada columna | LOAD-01, 6.1.1 |
| EM-D-02 | Definición de L. En el EMS parece incremental; en el Excel de los HEMS es ψ/\|i\| e incluye el flujo del imán. ¿Se calcularon de forma distinta? | LOAD-01, CTL-07 |
| EM-D-03 | Mapas de inductancia ampliados a 60 A | LOAD-03, 6.1.3, DCB-09 |
| EM-D-04 ★ | Rango esperado de L y R de las nuevas bobinas. **Sube de prioridad:** la energía del caso de fallo escala con L·I² y es lo que dimensiona el clamp de DCB-09 | LOAD-01, DCB-09, 6.3 |

### 7.3 Mechanics – Cooling (ME-C)

| ID | Cuestión | Afecta a |
|---|---|---|
| ME-C-01 ★ | Dimensiones e interfaz del nuevo waterblock: superficie de contacto, fijaciones, material térmico y altura máxima de componentes. Estos datos fijan el tamaño de la placa. **Además hay que rehacer el camino térmico para el pad del PG-HSOF-8**, que sustituye al H²PAK-7 | PWR-06, MEC-01, MEC-02, ISO-04 |
| ME-C-02 | Temperatura y caudal del refrigerante; valores del rango de temperatura ambiente | MEC-06, térmica |

### 7.4 Mechanics – Electrical Integration (ME-I)

| ID | Cuestión | Afecta a |
|---|---|---|
| ME-I-01 ★ | Señales cableadas con la VCU: cuáles (enable, fault, lazo de seguridad), con qué niveles y conectores, y si el Magnet Driver solo las recibe o también debe abrir el lazo | SAF-03 |
| ME-I-02 ★ | Alimentación de BT: tensión mínima de la batería de 24 V, consumo permitido por placa y método (mazo de 24 V, PoE o similar). PoE es un enlace punto a punto y no encaja directamente con EtherCAT en línea; EtherCAT P (Beckhoff) es una alternativa. **Sube de prioridad (v0.4): un Magnet Driver sin BT abre la línea EtherCAT y deja fuera del bus a los que están aguas abajo** (COM-07). La alimentación de BT deja de ser solo una cuestión de consumo y pasa a condicionar la disponibilidad del bus | AUX-01, AUX-03, COM-07 |
| ME-I-03 | Distribución del bus de HV: **la propuesta pasa a estrella** por los 108 A de 6.2; ¿fusible en cada placa? | DCB-05, DCB-06, 6.2 |
| ME-I-04 | Conectores: potencia, bobina, NTC, bus de campo, señales cableadas y BT | MEC-07 |
| ME-I-05 | Especificación de vibraciones | MEC-08 |
| ME-I-06 | Identificación de la posición de cada placa (alias en EEPROM, selector físico o codificación en el mazo), junto con Firmware. **Vía más barata (v0.4):** el direccionamiento auto-incremental de EtherCAT (COM-08), si el orden del cableado es fijo y está documentado. Elimina el selector físico de la placa única | CTL-06, COM-08, sección 8 |
| ME-I-07 | Rango de tensión de la nueva batería de HV. **Deja de bloquear:** se confirma que seguirá siendo de 400 V mucho tiempo | DCB-01 |
| **ME-I-08 ★** | **¿Quién se hace cargo del clamp de bus de DCB-09 y acepta alojarlo en el módulo de precarga?** Si no cabe allí, hay que decidir dónde va antes de cerrar el área de las 10 placas | DCB-09, SAF-07, HW-03 |

### 7.5 Firmware (FW)

**Ampliada en la v0.4** con FW-09, que reabre la plataforma de control.

| ID | Cuestión | Afecta a |
|---|---|---|
| FW-01 ★ | Adquisición. **Reformulada (v0.4):** la elección no es entre ADC interno y externo, sino entre **amplificador aislado** (vale cualquier ADC, incluido el interno del controlador) y **modulador ΔΣ aislado** (exige SDFM/DFSDM en la plataforma). Ver 6.6.3. ¿Qué resolución, frecuencia de muestreo y latencia hacen falta? ¿Basta con un solo canal ΔΣ (SNS-07)? | 5.2, 6.6.3, SNS-05, SNS-06, SNS-07, SNS-09, FW-09 |
| FW-02 | Elección definitiva **dentro de la vía FPGA**, si FW-09 concluye que la plataforma es una FPGA: densidad y encapsulado. Según Lattice, la MachXO5-NX se ofrece en encapsulados BGA | CTL-01, PT-02, FW-09 |
| FW-03 | ¿Hace falta una flash de configuración externa? | CTL-03 |
| FW-04 | Programación y depuración: conector JTAG y actualización por el bus | CTL-04 |
| FW-05 | Comportamiento ante pérdida de comunicación, junto con EM-C | CTL-05 |
| FW-06 ★ | EtherCAT: confirmación del protocolo; implementación del esclavo entre las **tres vías** de COM-02 (ESC externo tipo LAN9252, ESC integrado en el micro, o IP core en FPGA); plataforma del maestro en la VCU; tiempo de ciclo; EEPROM SII. **Nuevo (v0.4):** ¿se adopta la **redundancia en anillo** de COM-07? ¿Se acepta el **direccionamiento auto-incremental** de COM-08 como identificación de posición? EBUS queda documentado en 6.6.4 y descartado | COM-01 a COM-04, COM-06, COM-07, COM-08, FW-09 |
| FW-07 | Datos intercambiados con la VCU (mapa de objetos) | COM-05 |
| FW-08 | Rango de frecuencia de conmutación y tipo de modulación que debe admitir el hardware | PWR-03 |
| **FW-09 ★** | **Elección de la plataforma de control: FPGA o microcontrolador de tiempo real.** Criterios de aceptación C1 a C6 en 5.4; candidatos y análisis en 6.6. Orden de decisión acordado: Hardware acota el conjunto, Firmware elige dentro de él. Sustituye a la hipótesis de partida de la MachXO5-NX | CTL-01, CTL-02, CTL-03, CTL-08, CTL-09, COM-02, SNS-05, PT-02, PT-03 |

### 7.6 Hardware (HW)

| ID | Cuestión | Afecta a |
|---|---|---|
| HW-01 | Qué protecciones analógicas o de lógica cableada se incluyen, con qué umbrales y tiempos de respuesta, y cómo se desactivan (jumpers) y se reportan. **Incluye ahora el comparador rápido sobre el shunt** (SAF-04) y el dimensionado del circuito de DESAT (GD-06, GD-07). **Nuevo (v0.4):** decidir qué parte la cubre el disparo por hardware interno del controlador (CTL-08) y qué parte la lógica cableada independiente de SAF-02 | SAF-04, SAF-06, SAF-08, SAF-09, GD-06, GD-07, CTL-08 |
| HW-02 | Alternativas a los componentes del TFG. **Resuelto en parte:** MOSFET (PWR-02) y driver (GD-01) propuestos. **Sigue abierto:** módulo de la fuente aislada de puerta con raíl de 18 V (AUX-02), sensado, fusible para la tensión de DCB-02 y condensadores del DC-link, más la confirmación de stock del STGAP3S6S | GD-01, SNS-01, DCB-02, DCB-06, DCB-07, AUX-02 |
| HW-03 ★ | **Reformulada.** Con el MOSFET de 650 V, el caso de fallo sin rueda libre solo se resuelve con un clamp disipativo de ~200 J en el bus (DCB-09): la capacidad necesitaría más de 3 mF y la retención local exige circuitería nueva en las 10 placas. Hay que especificar el clamp (umbral, energía, autoalimentación, diagnóstico) y decidir dónde va (ME-I-08) | DCB-08, DCB-09, SAF-07, PWR-02, 6.3 |
| HW-04 | Tensión y tipo de aislamiento, distancias, y documento y versión del reglamento (R4) | ISO-05, ISO-06 |
| HW-05 ★ | Posición de la barrera de aislamiento (opción A o B), junto con Firmware. **No depende de FW-09:** todos los candidatos de 6.6 admiten la opción A, así que se puede cerrar antes, y cerrarla desbloquea AUX-02 y el floorplan | 5.2, 6.6.3, AUX-02 |
| HW-06 | ¿Tenía la LCU otras funciones que haya que reasignar, además de la lectura de entrehierro? | SYS-04 |
| HW-07 | Número de unidades a fabricar. **Además: ¿cuántos IMT65R010M2H hay en el taller?** Hacen falta 4 por placa más repuestos | SYS-05, PWR-02 |
| **HW-08 ★** | **¿El requisito de 600 V continuos de DCB-02 aplica también a los interruptores, o solo al aislamiento y a los pasivos?** Un MOSFET de 650 V queda al 92 % de su tensión de ruptura frente a ese requisito, y el criterio del 80 % de su propio fabricante daría 520 V. En operación el bus nunca pasa de 400 V y el clamp limita el fallo a 520 V, así que la lectura razonable es que los 600 V son una regla de aislamiento y de pasivos: hay que confirmarlo | DCB-02, ISO-06, PWR-02 |
| **HW-09** | Pedir al FAE de Infineon la hoja de datos de la familia EiceDRIVER X3 Enhanced (1ED34xx / 1ED38xx) y comprobar **a qué referencia mide su UVLO** y su umbral de DESAT. Sería el emparejamiento de un solo fabricante con el MOSFET | GD-01, GD-05, 6.5 |

### 7.7 Partners (PT)

| ID | Cuestión | Afecta a |
|---|---|---|
| PT-01 | Fabricante de PCB: capacidades (6 capas, 2 oz, fresados), stackup y aplicación del coating | MEC-03, MEC-09, ISO-02 |
| PT-02 | Montaje en casa o externo, con capacidad para el PG-HSOF-8 (TOLL), que es un encapsulado sin patillas e inspeccionable solo por rayos X, y para el encapsulado del controlador. **Matiz (v0.4):** «BGA» no es una sola categoría. Un paso de 0,8 mm (BGA de 256 bolas, 13 × 13 mm) se rutea en 6 capas con vías normales; un paso de 0,5 mm es otra cosa. Conviene declarar la capacidad por paso, no por tipo de encapsulado | MEC-09, FW-02, FW-09, MEC-03 |
| PT-03 | Patrocinio o disponibilidad de componentes y, **solo si FW-09 lleva a la vía del IP core**, la licencia de Beckhoff. Las vías de ESC externo o integrado la evitan, aunque las tres siguen necesitando el Slave Stack Code de Beckhoff por vía ETG. **Los dos MOSFET candidatos están cubiertos por patrocinio; el gate driver no** | HW-02, FW-06, FW-09, PWR-02 |

### 7.8 Preguntas resueltas

**Aclaradas en la v0.4 (19/09/2026).** Ninguna cierra una decisión, pero todas eliminan una vía muerta:

| Cuestión | Respuesta | Dónde se recoge |
|---|---|---|
| ¿Puede un microcontrolador hacer el trabajo de la FPGA? (parte de FW-02) | Sí. El alcance de CTL-02 lo cubren varias familias con ESC integrado, y en CTL-07 y CTL-09 el micro tiene ventaja | 6.6.1, FW-09 |
| ¿Se puede cablear la red en estrella desde la VCU? (parte de COM-03) | No. EtherCAT es intrínsecamente una línea | COM-03, 6.6.4 |
| ¿Hacen falta dos puertos EtherCAT en todas las placas? (parte de COM-03) | Sí, pero por SYS-01, no por el ESC, que ya los trae. Y en todas si se adopta el anillo | COM-03, COM-07, 6.6.4 |
| ¿Importa la interfaz ΔΣ si el controlador tiene ADC internos? (parte de FW-01) | Lo que decide es dónde está la barrera, no el ADC | 6.6.3, SNS-05, SNS-07 |
| ¿Decide la plataforma el tamaño del encapsulado? (parte de FW-02) | No: la diferencia es del orden del 1 % del área de la placa. Deciden el PowerPAD, el rutado y el toolchain | 6.6.2 |
| Orden de decisión de la plataforma | Hardware acota con C1 a C6; Firmware elige dentro de ese conjunto | 5.4, FW-09 |

**Resueltas en la v0.3 (19/09/2026):**

| Cuestión | Respuesta | Dónde se recoge |
|---|---|---|
| Duración del pico de corriente (parte de EM-C-01) | No mucho más de 2 s | LOAD-03, 6.2 |
| Rango de la batería de HV (ME-I-07) | Seguirá siendo de 400 V mucho tiempo | DCB-01 |
| Tensión de puerta (parte de GD-01) | +18 / −3 V, en lugar de +20 / −5 V | GD-01, 6.4 |
| Elección del MOSFET (parte de PWR-02 y HW-02) | IMT65R010M2H, condicionado a HW-03 | PWR-02, 6.4 |
| Elección del gate driver (parte de GD-01 y HW-02) | STGAP3S6S propuesto; ADuM4146 grado A como alternativa | GD-01, 6.5 |
| Disponibilidad de los dos MOSFET (parte de PT-03) | Los dos por patrocinio; más stock del Infineon | PWR-02, PT-03 |
| Topología del bus (parte de ME-I-03) | Propuesta en estrella por los 108 A del pico simultáneo | DCB-05, 6.2 |

**Resueltas en la v0.2 (numeración de la v0.1):**

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
| N11 | No hace falta prever 650 V, pero sí soportar 600 V en continuo | DCB-02, ISO-06, **revisar en HW-08** |
| N15 | No se mide la temperatura de los MOSFET ni del waterblock | SNS-04 |
| N16 (en parte) | La placa del TFG no se ensayó; se discutirán alternativas | PWR-02, HW-02 |
| N17 | Nombre: Magnet Driver Abejorro | Sección 8 |
| N18 | El documento sigue en Markdown | — |
| N19 (en parte) | Herramienta EDA: KiCad; fabricante por definir | MEC-04, PT-01 |
| N20 (en parte) | Temperatura y presión atmosféricas; vibraciones por definir | MEC-05, ME-I-05 |
| N21 | La arquitectura de control sigue pendiente | EM-C-02 |

Las demás preguntas de la versión 0.1 siguen abiertas con su nuevo código:

- N4 → HW-05, FW-01
- N5 → EM-C-01 (parcialmente resuelta: la duración del pico ya está)
- N12 → ME-I-03
- N13 → FW-06
- N14 → ME-I-06

---

## 8. Nomenclatura y control de versiones

Sin cambios respecto a la v0.2.

- **Esquema de nombres** [U]:
  - Cada generación de hardware se llama "Magnet Driver" seguido de un nombre de insecto.
  - Se descartan las siglas.
  - Los nombres no tienen que seguir ningún orden.
- **Primera generación con control local en placa** [U]: **Magnet Driver Abejorro**. (En la v0.3 este renglón decía «con FPGA»; se generaliza porque la plataforma es ahora FW-09 y el rasgo que define la generación es el control local, no el silicio que lo ejecuta.)
- **Para qué sirve el nombre** [U]: identifica de un vistazo la compatibilidad de conectores y de firmware.
- **Regla propuesta** [P]:
  - Se asigna un **nuevo nombre** cuando se rompe la compatibilidad. Eso ocurre si cambia el tipo o el pinout de algún conector externo, o si cambia la interfaz con el firmware (pinout del controlador, periféricos o mapa de entradas y salidas).
  - Si se mantiene la compatibilidad, se conserva el nombre y se sube la revisión: "Abejorro, revisión 2".
- **Registro de compatibilidad** [P]:

| Nombre | Revisión | Conectores | Firmware compatible | Notas |
|---|---|---|---|---|
| Abejorro | 1 | TBD | TBD | Primera generación con control local en placa |

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
| 0.4 | 19/09/2026 | **Se reabre la plataforma de control (FW-09):** la FPGA pasa de hipótesis de partida a una de tres vías, con criterios de aceptación C1 a C6 en la nueva sección 5.4 y análisis de candidatos en la nueva sección 6.6 (XMC4800/4300, RX72M, C2000 F28P65x y F2838x, la vía de MCU pequeño más LAN9252, y la FPGA con IP core). Se documenta que el tamaño del encapsulado no es un criterio discriminante y que sí lo son el PowerPAD y el paso de bolas (PT-02). **Topología EtherCAT:** el diagrama de 2.2 se corrige a línea; COM-03 reescrito; nuevos COM-07 (un esclavo sin BT abre la línea, con el anillo como mitigación) y COM-08 (direccionamiento auto-incremental como identificación de posición), que descargan a ME-I-06 y CTL-06. **Cadena de sensado:** SNS-05 reformulado (la decisión es dónde está la barrera, no ADC interno o externo) y nuevos SNS-07 a SNS-09. Nuevos CTL-08 (disparo por hardware) y CTL-09 (coma flotante). Actualizados FW-01, FW-02, FW-06, HW-01, HW-05, ME-I-02, ME-I-06, PT-02 y PT-03. Título y sección 8 generalizados de «con FPGA» a «con control local». `parametros.md` ampliado con la sección 11 |
| 0.3 | 19/09/2026 | **Elección de MOSFET (IMT65R010M2H) y de gate driver (STGAP3S6S) con su justificación en 6.4 y 6.5.** Tensiones de puerta a +18 / −3 V. Nuevos requisitos DCB-09 (clamp de bus), PWR-07 (inductancia del lazo), GD-05 a GD-07. Caso de fallo de 6.3 rehecho con el bus compartido: se distingue el fallo aislado del fallo común y se concluye que con 650 V el clamp es obligatorio. Duración del pico (2 s) y batería de 400 V confirmadas. Distribución del bus propuesta en estrella. Nuevas cuestiones EM-C-05, ME-I-08, HW-08 y HW-09. Corrección de 17 parámetros del IMT65R010M2H en `componentes.md`. **`parametros.md` reconciliado con este documento:** se sustituyen los valores de prueba del motor de cálculos (Vbus 350/405, V_cont 650, Rcoil 1,1, Irms 10 A, 30 kHz, bipolar, rizado 1 %) por los de los requisitos, y se justifican con un cálculo los que antes eran provisionales (eta_pwr, V_film, V_OV, A_pad, N_via, Rg, C_blank, divisor de Vbus, NTC) |
