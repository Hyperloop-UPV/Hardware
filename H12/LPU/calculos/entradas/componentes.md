# Datos de componentes

Datos de hoja de datos de los componentes candidatos. Se editan al añadir o cambiar un candidato; las referencias están en «Fuentes» de `calculos/README.md`.

Las mismas reglas de formato que en `parametros.md`: decimales con coma o punto, sin `|` dentro de las celdas.

## 1. MOSFET: candidatos

Una columna por candidato (se pueden añadir columnas «Candidato N»; una columna vacía se ignora). La columna «Clave» la usan las fórmulas y no debe cambiarse. El candidato activo se elige con `MOSFET_sel` en `parametros.md`, por su referencia.

| Parámetro | Clave | Unidad | Candidato 1 | Candidato 2 | Candidato 3 | Fuente / nota |
|---|---|---|---|---|---|---|
| Fabricante | fab | – | Infineon | STMicroelectronics |  | |
| Referencia | ref | – | IMT65R010M2H | SCT012H90G3AG |  | Candidato del TFG, sin ensayar (PWR-02) |
| Encapsulado | pkg | – | PG‑HSOF‑8 | H²PAK-7 (SMD) |  | Infineon, hoja de datos IMT65R010M2H |
| VDS máxima | VDS | V | 650 | 900 |  | Infineon, hoja de datos |
| VGS máxima absoluta (positiva) | VGSmax | V | 20 | 22 |  | Infineon, hoja de datos |
| VGS máxima absoluta (negativa) | VGSmin | V | -20 | -10 |  | Infineon, hoja de datos |
| VGS recomendada en ON (máxima) | VGSrec_on | V | 15 | 18 |  | Infineon, hoja de datos |
| VGS recomendada en OFF (mínima) | VGSrec_off | V | -5 | -5 |  | Infineon, hoja de datos |
| VGS(th) mínima | Vth_min | V | 3,0 | 1,8 |  | Infineon, hoja de datos |
| ID continua (Tc = 25 °C) | ID | A | 80 | 110 |  | Infineon, hoja de datos |
| ID pulsada | IDM | A | 300 | 454 |  | Infineon, hoja de datos |
| Tj máxima | Tjmax | °C | 175 | 175 |  | Infineon, hoja de datos |
| Rth unión-cápsula | Rthjc | K/W | 0,35 | 0,24 |  | Infineon, hoja de datos |
| RDS(on) típica a 25 °C | R25 | mΩ | 10 | 12 |  | Infineon, hoja de datos |
| RDS(on) máxima a 25 °C | R25max | mΩ | 12 | 15,8 |  | Infineon, hoja de datos |
| RDS(on) típica a temperatura alta | Rhot | mΩ | 15 | 18,5 |  | Infineon, hoja de datos |
| Temperatura de la RDS(on) anterior | Thot | °C | 175 | 175 |  | Infineon, hoja de datos |
| Tensión del diodo interno | VSD | V | 1,2 | 2,8 |  | Infineon, hoja de datos |
| Carga de recuperación inversa | Qrr | nC | 200 | 335 |  | Infineon, hoja de datos |
| Carga total de puerta | Qg | nC | 95 | 138 |  | Infineon, hoja de datos |
| Ciss | Ciss | pF | 2500 | 3880 |  | Infineon, hoja de datos |
| Coss | Coss | pF | 180 | 244 |  | Infineon, hoja de datos |
| Crss | Crss | pF | 18 | 20 |  | Infineon, hoja de datos |
| Resistencia interna de puerta | Rgint | Ω | 1,5 | 1,8 |  | Infineon, hoja de datos |
| Energía de encendido | Eon | µJ | 500 | 708 |  | Infineon, hoja de datos |
| Energía de apagado | Eoff | µJ | 600 | 889 |  | Infineon, hoja de datos |
| Tensión de ensayo de Eon/Eoff | Vtest | V | 400 | 600 |  | Infineon, hoja de datos |
| Corriente de ensayo de Eon/Eoff | Itest | A | 40 | 60 |  | Infineon, hoja de datos |
| RG de ensayo de Eon/Eoff y de los tiempos | Rgtest | Ω | 15 | 15 |  | Infineon, hoja de datos |
| td(on) | tdon | ns | 30 | 37 |  | Infineon, hoja de datos |
| tr | tr | ns | 40 | 47 |  | Infineon, hoja de datos |
| td(off) | tdoff | ns | 55 | 82 |  | Infineon, hoja de datos |
| tf | tf | ns | 20 | 30 |  | Infineon, hoja de datos |

## 2. Gate driver: candidatos

En esta tabla, el primer candidato es el actual y el segundo queda reservado para una alternativa posible.

| Nombre | Descripción | Unidad | Candidato 1 | Candidato 2 | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---:|---:|---|---|---|---|
| D_Isrc | Corriente de cortocircuito de fuente | A | 11 |  | ADI | OK | GD-01 | |
| D_Isnk | Corriente de cortocircuito de sumidero | A | 9 |  | ADI | OK | GD-01 | |
| D_Rp | RDS(on) del PMOS de salida (máx.) | Ω | 0,975 |  | ADI | OK | GD-01 | |
| D_Rn | RDS(on) del NMOS de salida (máx.) | Ω | 0,807 |  | ADI | OK | GD-01 | |
| D_skew | Desfase de propagación entre dispositivos (máx.) | ns | 25 |  | ADI | OK | PWR-04 | |
| D_desat | Umbral DESAT (grado B) | V | 9,2 |  | ADI | OK | GD-01 | Grados A y C: 3,5 V sin fuente de corriente interna |
| D_Idesat | Corriente de carga DESAT (grado B, típ.) | µA | 527 |  | ADI | OK | GD-01 | |
| D_mask | Tiempo de enmascaramiento DESAT (máx.) | ns | 340 |  | ADI | OK | GD-01 | 260 a 340 ns |
| D_Rclamp | Resistencia del Miller clamp (máx.) | Ω | 2,75 |  | ADI | OK | GD-01 | |
| D_CMTI | CMTI | kV/µs | 100 |  | ADI | OK | GD-01 | |
| D_IDD2 | Corriente de VDD2 (máx.) | mA | 6,5 |  | ADI | OK | AUX-02 | |
| D_UVLO | UVLO de VDD2, umbral de subida (grados B/C) | V | 11,5 |  | ADI | AC | GD-02 | Grado A: 14,5 V. Grado del TFG por confirmar |

## 3. Fuente aislada de puerta: candidatos

| Nombre | Descripción | Unidad | Candidato 1 | Candidato 2 | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---:|---:|---|---|---|---|
| G_Vin | Tensión de entrada nominal | V | 5 |  | Murata | OK | AUX-02 | 4,5 a 5,5 V |
| G_P | Potencia nominal | W | 2 |  | Murata | OK | GD-01 | |
| G_eta | Rendimiento mínimo a plena carga | % | 74 |  | Murata | OK | AUX-02 | Típ. 78,5 % |
| G_Ipos | Corriente máxima de la salida +20 V | mA | 80 |  | Murata | OK | GD-01 | |
| G_Ineg | Corriente máxima de la salida −5 V | mA | 40 |  | Murata | OK | GD-01 | |
| G_CMTI | CMTI | kV/µs | 200 |  | Murata | OK | GD-01 | > 200 kV/µs |

## 4. Sensores aislados: candidatos

| Nombre | Descripción | Unidad | Candidato 1 | Candidato 2 | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---:|---:|---|---|---|---|
| Sa_Vlin | AMC1302: entrada diferencial lineal | mV | 50 |  | TI | OK | SNS-01 | ±50 mV |
| Sa_Vclip | AMC1302: entrada de recorte | mV | 64 |  | TI | OK | SNS-01 | ±64 mV |
| Sa_G | AMC1302: ganancia fija | – | 41 |  | TI | OK | SNS-01 | |
| Sa_BW | AMC1302: ancho de banda (mínimo) | kHz | 220 |  | TI | OK | SNS-05 | 220 a 280 kHz |
| Sa_td | AMC1302: retardo de señal 50–90 % (máximo) | µs | 3 |  | TI | OK | SNS-05 | |
| Sd_Vlin | AMC1306x05: entrada diferencial lineal | mV | 50 |  | TI | OK | SNS-01 | x25: ±250 mV |
| Sd_fmin | AMC1306: frecuencia de reloj mínima | MHz | 5 |  | TI | OK | FW-01 | |
| Sd_fmax | AMC1306: frecuencia de reloj máxima | MHz | 21 |  | TI | OK | FW-01 | A 5 V |
| Sd_ENOB | AMC1306: ENOB con sinc3 y OSR = 256 | bit | 14 |  | TI | AC | FW-01 | ≈ 14 bits; con otro OSR es distinto |
| S_CMTI | CMTI mínimo de los sensores aislados | kV/µs | 100 |  | TI | OK | SNS-01 | AMC1302: 100 kV/µs mín.; AMC1306: 100 kV/µs típ. |

## 5. Componentes que cruzan la barrera HV–BT

Distancias de fuga y tensiones de trabajo del encapsulado. La «Clave» identifica la comprobación en el informe.

| Clave | Componente | Fuga (mm) | Tensión de trabajo (V) | Fuente / nota |
|---|---|--:|--:|---|
| ADUM4146 | ADuM4146 (gate driver) | 8,3 | 2150 | ADI: 8,3 mm mín.; VIORM 2150 V pico |
| AMC1302 | AMC1302 (amplificador aislado) | 8,5 | 2121 | TI: ≥ 8,5 mm; VIORM 2121 V pico |
| AMC1306 | AMC1306 (modulador ΔΣ aislado) | 8,5 | 2120 | TI: ≥ 8,5 mm; VIORM 2120 V pico |
| MGJ2 | MGJ2D052005BSC (fuente aislada de puerta) | 2 | 2400 | Murata: 2 mm en el apartado de la aprobación UL60950; 2400 V de tensión continua de barrera. Medir la distancia real entre pines en el footprint |

## 6. EtherCAT P: candidatos

| Nombre | Descripción | Unidad | Candidato 1 | Candidato 2 | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|---|---:|---:|---|---|---|---|
| ECP_V | Tensión de alimentación de EtherCAT P | V | 24 |  | Beckhoff | OK | AUX-01 | |
| ECP_Imax | Corriente máxima por alimentación (US o UP) | A | 3 |  | Beckhoff | OK | AUX-01 | Solo aplica si se elige EtherCAT P (ME-I-02) |
