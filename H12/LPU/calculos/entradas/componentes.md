# Datos de componentes

Datos de hoja de datos de los componentes candidatos. Se editan al añadir o cambiar un candidato; las referencias están en «Fuentes» de `calculos/README.md`.

Las mismas reglas de formato que en `parametros.md`: decimales con coma o punto, sin `|` dentro de las celdas.

## 1. MOSFET: candidatos

Una columna por candidato (se pueden añadir columnas «Candidato N»; una columna vacía se ignora). La columna «Clave» la usan las fórmulas y no debe cambiarse. El candidato activo se elige con `MOSFET_sel` en `parametros.md`, por su referencia.

| Parámetro | Clave | Unidad | Candidato 1 | Candidato 2 | Candidato 3 | Fuente / nota |
|---|---|---|---|---|---|---|
| Fabricante | fab | – | STMicroelectronics |  |  | |
| Referencia | ref | – | SCT012H90G3AG |  |  | Candidato del TFG, sin ensayar (PWR-02) |
| Encapsulado | pkg | – | H²PAK-7 (SMD) |  |  | ST, hoja de datos SCT012H90G3AG |
| VDS máxima | VDS | V | 900 |  |  | ST, hoja de datos |
| VGS máxima absoluta (positiva) | VGSmax | V | 22 |  |  | ST, hoja de datos |
| VGS máxima absoluta (negativa) | VGSmin | V | -10 |  |  | ST, hoja de datos |
| VGS recomendada en ON (máxima) | VGSrec_on | V | 18 |  |  | ST: rango recomendado −5 a 18 V |
| VGS recomendada en OFF (mínima) | VGSrec_off | V | -5 |  |  | ST, hoja de datos |
| VGS(th) mínima | Vth_min | V | 1,8 |  |  | ST (típ. 3,1 V; máx. 4,2 V) |
| ID continua (Tc = 25 °C) | ID | A | 110 |  |  | ST (110 A también a Tc = 100 °C) |
| ID pulsada | IDM | A | 454 |  |  | ST, hoja de datos |
| Tj máxima | Tjmax | °C | 175 |  |  | ST, hoja de datos |
| Rth unión-cápsula | Rthjc | K/W | 0,24 |  |  | ST, hoja de datos |
| RDS(on) típica a 25 °C | R25 | mΩ | 12 |  |  | ST: VGS = 18 V, ID = 60 A |
| RDS(on) máxima a 25 °C | R25max | mΩ | 15,8 |  |  | ST: VGS = 18 V, ID = 60 A |
| RDS(on) típica a temperatura alta | Rhot | mΩ | 18,5 |  |  | ST: VGS = 18 V, ID = 60 A |
| Temperatura de la RDS(on) anterior | Thot | °C | 175 |  |  | ST, hoja de datos |
| Tensión del diodo interno | VSD | V | 2,8 |  |  | ST: ISD = 60 A, VGS = 0 V |
| Carga de recuperación inversa | Qrr | nC | 335 |  |  | ST: ISD = 60 A |
| Carga total de puerta | Qg | nC | 138 |  |  | ST: VDD = 600 V, ID = 60 A |
| Ciss | Ciss | pF | 3880 |  |  | ST: VDS = 600 V, f = 1 MHz |
| Coss | Coss | pF | 244 |  |  | ST: VDS = 600 V |
| Crss | Crss | pF | 20 |  |  | ST: VDS = 600 V (a VDS bajas es mayor) |
| Resistencia interna de puerta | Rgint | Ω | 1,8 |  |  | ST, hoja de datos |
| Energía de encendido | Eon | µJ | 708 |  |  | ST: condiciones de ensayo abajo |
| Energía de apagado | Eoff | µJ | 889 |  |  | ST, hoja de datos |
| Tensión de ensayo de Eon/Eoff | Vtest | V | 600 |  |  | ST, hoja de datos |
| Corriente de ensayo de Eon/Eoff | Itest | A | 60 |  |  | ST, hoja de datos |
| RG de ensayo de Eon/Eoff y de los tiempos | Rgtest | Ω | 15 |  |  | ST: VGS = −5 a 18 V |
| td(on) | tdon | ns | 37 |  |  | ST, hoja de datos |
| tr | tr | ns | 47 |  |  | ST, hoja de datos |
| td(off) | tdoff | ns | 82 |  |  | ST, hoja de datos |
| tf | tf | ns | 30 |  |  | ST, hoja de datos |

## 2. Gate driver: ADuM4146

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| D_Isrc | Corriente de cortocircuito de fuente | 11 | A | ADI | OK | GD-01 | |
| D_Isnk | Corriente de cortocircuito de sumidero | 9 | A | ADI | OK | GD-01 | |
| D_Rp | RDS(on) del PMOS de salida (máx.) | 0,975 | Ω | ADI | OK | GD-01 | |
| D_Rn | RDS(on) del NMOS de salida (máx.) | 0,807 | Ω | ADI | OK | GD-01 | |
| D_skew | Desfase de propagación entre dispositivos (máx.) | 25 | ns | ADI | OK | PWR-04 | |
| D_desat | Umbral DESAT (grado B) | 9,2 | V | ADI | OK | GD-01 | Grados A y C: 3,5 V sin fuente de corriente interna |
| D_Idesat | Corriente de carga DESAT (grado B, típ.) | 527 | µA | ADI | OK | GD-01 | |
| D_mask | Tiempo de enmascaramiento DESAT (máx.) | 340 | ns | ADI | OK | GD-01 | 260 a 340 ns |
| D_Rclamp | Resistencia del Miller clamp (máx.) | 2,75 | Ω | ADI | OK | GD-01 | |
| D_CMTI | CMTI | 100 | kV/µs | ADI | OK | GD-01 | |
| D_IDD2 | Corriente de VDD2 (máx.) | 6,5 | mA | ADI | OK | AUX-02 | |
| D_UVLO | UVLO de VDD2, umbral de subida (grados B/C) | 11,5 | V | ADI | AC | GD-02 | Grado A: 14,5 V. Grado del TFG por confirmar |

## 3. Fuente aislada de puerta: MGJ2D052005BSC

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| G_Vin | Tensión de entrada nominal | 5 | V | Murata | OK | AUX-02 | 4,5 a 5,5 V |
| G_P | Potencia nominal | 2 | W | Murata | OK | GD-01 | |
| G_eta | Rendimiento mínimo a plena carga | 74 | % | Murata | OK | AUX-02 | Típ. 78,5 % |
| G_Ipos | Corriente máxima de la salida +20 V | 80 | mA | Murata | OK | GD-01 | |
| G_Ineg | Corriente máxima de la salida −5 V | 40 | mA | Murata | OK | GD-01 | |
| G_CMTI | CMTI | 200 | kV/µs | Murata | OK | GD-01 | > 200 kV/µs |

## 4. Sensores aislados: AMC1302 y AMC1306

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| Sa_Vlin | AMC1302: entrada diferencial lineal | 50 | mV | TI | OK | SNS-01 | ±50 mV |
| Sa_Vclip | AMC1302: entrada de recorte | 64 | mV | TI | OK | SNS-01 | ±64 mV |
| Sa_G | AMC1302: ganancia fija | 41 | – | TI | OK | SNS-01 | |
| Sa_BW | AMC1302: ancho de banda (mínimo) | 220 | kHz | TI | OK | SNS-05 | 220 a 280 kHz |
| Sa_td | AMC1302: retardo de señal 50–90 % (máximo) | 3 | µs | TI | OK | SNS-05 | |
| Sd_Vlin | AMC1306x05: entrada diferencial lineal | 50 | mV | TI | OK | SNS-01 | x25: ±250 mV |
| Sd_fmin | AMC1306: frecuencia de reloj mínima | 5 | MHz | TI | OK | FW-01 | |
| Sd_fmax | AMC1306: frecuencia de reloj máxima | 21 | MHz | TI | OK | FW-01 | A 5 V |
| Sd_ENOB | AMC1306: ENOB con sinc3 y OSR = 256 | 14 | bit | TI | AC | FW-01 | ≈ 14 bits; con otro OSR es distinto |
| S_CMTI | CMTI mínimo de los sensores aislados | 100 | kV/µs | TI | OK | SNS-01 | AMC1302: 100 kV/µs mín.; AMC1306: 100 kV/µs típ. |

## 5. Componentes que cruzan la barrera HV–BT

Distancias de fuga y tensiones de trabajo del encapsulado. La «Clave» identifica la comprobación en el informe.

| Clave | Componente | Fuga (mm) | Tensión de trabajo (V) | Fuente / nota |
|---|---|--:|--:|---|
| ADUM4146 | ADuM4146 (gate driver) | 8,3 | 2150 | ADI: 8,3 mm mín.; VIORM 2150 V pico |
| AMC1302 | AMC1302 (amplificador aislado) | 8,5 | 2121 | TI: ≥ 8,5 mm; VIORM 2121 V pico |
| AMC1306 | AMC1306 (modulador ΔΣ aislado) | 8,5 | 2120 | TI: ≥ 8,5 mm; VIORM 2120 V pico |
| MGJ2 | MGJ2D052005BSC (fuente aislada de puerta) | 2 | 2400 | Murata: 2 mm en el apartado de la aprobación UL60950; 2400 V de tensión continua de barrera. Medir la distancia real entre pines en el footprint |

## 6. EtherCAT P

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| ECP_V | Tensión de alimentación de EtherCAT P | 24 | V | Beckhoff | OK | AUX-01 | |
| ECP_Imax | Corriente máxima por alimentación (US o UP) | 3 | A | Beckhoff | OK | AUX-01 | Solo aplica si se elige EtherCAT P (ME-I-02) |
