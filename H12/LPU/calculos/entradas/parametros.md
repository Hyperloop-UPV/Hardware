# Parámetros de diseño

Parámetros escalares de los cálculos del Magnet Driver Abejorro. **Este es el fichero que se edita normalmente.**

- Cambie solo las columnas «Valor», «Estado», «Fuente» y «Nota». La columna «Nombre» es la que usan las fórmulas: no la cambie.
- Decimales con coma o con punto (`1,92` o `1.92`), sin separador de miles. Signo menos con `-` o `−`.
- Unidades admitidas: ver `calculos/README.md`. Un valor en `%` se interpreta como fracción (2 % → 0,02).
- «Estado»: `OK` (confirmado), `AC` (a confirmar) o `TBD` (desconocido: el valor es **provisional** y solo sirve para calcular).
- «Fuente»: `U` (equipo), `TFG` (TFG de L. Navarro), `C` (cálculo del documento de requisitos), `P` (propuesta) o el documento o fabricante citado.
- No use el carácter `|` dentro de las celdas.


## 1. Bus DC

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| Vbus_min | Tensión mínima del bus de HV | 335 | V | U | OK | DCB-01 | Revisar con la nueva batería (ME-I-07) |
| Vbus_max | Tensión máxima del bus de HV | 405 | V | U | OK | DCB-01 | Revisar con la nueva batería (ME-I-07) |
| V_cont | Tensión continua que deben soportar componentes y aislamiento | 600 | V | U | OK | DCB-02 · ISO-06 |  |
| N_MD | Número de Magnet Driver conectados al bus | 10 | – | U | OK | DCB-03 · SYS-01 | 4 HEMS + 6 EMS |
| Bus_topo | Distribución del bus: «Encadenado» o «Estrella» | Encadenado | – | TFG | TBD | DCB-05 · ME-I-03 | Encadenado: la primera placa conduce la corriente de todas |
| dVdc_pct | Rizado máximo de tensión en el DC-link (fracción de Vbus_min) | 2 | % | TFG | AC | DCB-07 · HW-02 | 2 % de 400 V = 8 V según el TFG |
| eta_pwr | Rendimiento de la etapa de potencia (para la corriente media de bus) | 97 | % | P | TBD | — | PROVISIONAL. Ajustar con las pérdidas del puente del informe cuando se elija componente |

## 2. Carga: electroimanes (prototipo H11)

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| Rcoil | Resistencia de la bobina | 1,1 | Ω | U | OK | LOAD-01 | Medida en la bobina construida. Nuevas bobinas: EM-D-04 |
| Ipk | Corriente de pico (primeros segundos de la levitación) | 55 | A | U | OK | LOAD-03 |  |
| t_pk | Duración del pico de corriente | 2 | s | — | TBD | LOAD-03 · EM-C-01 | PROVISIONAL. «Primeros segundos» |
| Irms_cont | Corriente eficaz en régimen permanente (dimensionado térmico) | 5 | A | TFG | TBD | LOAD-05 · EM-C-01 | Valor mencionado en el TFG, sin revalidar |
| L_EMS_min | Inductancia incremental mínima del EMS | 1,92 | mH | R5 | AC | LOAD-01 · EM-D-01/02 | Sección 6.1.1 |
| L_EMS_max | Inductancia incremental máxima del EMS | 117 | mH | R5 | AC | LOAD-01 · EM-D-01/02 | Sección 6.1.1 |
| L_HEMS_min | Inductancia incremental mínima del HEMS (dψ/di derivada) | 6,2 | mH | C | OK | LOAD-01 | Sección 6.1.2 (derivado del Excel R7) |
| L_HEMS_max | Inductancia incremental máxima del HEMS (dψ/di derivada) | 11,2 | mH | C | OK | LOAD-01 | Sección 6.1.2 |
| L_EMS_0 | Inductancia del EMS a I = 0 (valor citado, columnas 5–6) | 26,7 | mH | R5 | AC | 6.1.1 | Solo para la cota pesimista de energía (L constante) |
| E_EMS | Energía devuelta al desmagnetizar el EMS desde 55 A (mapa H11) | 15,6 | J | C | AC | 6.1.3 · EM-D-03 | Mapa hasta ±55 A |
| E_HEMS | Energía devuelta al desmagnetizar el HEMS desde −55 A, 6 mm (mapa H11) | 16,7 | J | C | AC | 6.1.3 · EM-D-03 | Peor caso del H11 |
| I_map | Corriente máxima cubierta por los mapas de inductancia | 55 | A | R7 | OK | EM-D-03 |  |
| dI_pp_max | Rizado de corriente pico a pico máximo admisible | 2 | A | — | TBD | LOAD-07 · EM-C-03 | PROVISIONAL. |
| T_coil_max | Temperatura máxima de la bobina (umbral de protección) | 120 | °C | — | TBD | SAF-01 · sin pendiente | PROVISIONAL. No hay cuestión abierta que lo resuelva: proponer a EM-D |

## 3. Conmutación y MOSFET

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| fsw | Frecuencia de conmutación | 30 | kHz | TFG | TBD | PWR-03 · FW-08 |  |
| Modulacion | Modulación: «Unipolar» o «Bipolar» | Bipolar | – | TFG | TBD | PWR-03 · FW-08 |  |
| t_dead | Tiempo muerto | 100 | ns | TFG | AC | PWR-04 · FW-08 | Red RC del TFG; pasa a ser configurable en la FPGA |
| MOSFET_sel | Referencia del MOSFET usado en el resto de cálculos (una de las columnas de componentes.md) | SCT012H90G3AG | – | P | AC | PWR-02 · HW-02 |  |
| D_worst | Fracción del periodo que conduce el MOSFET más cargado | 1 | – | P | OK | SAF-05 | 1 = rueda libre permanente por los low-side (conservador). Con PWM en régimen, el más cargado conduce (1 + m)/2 |
| Tj_assumed | Tj supuesta para evaluar RDS(on) | 125 | °C | P | AC | — | Debe ser ≥ Tj calculada (comprobación en el apartado MOSFET) |
| Tj_lim | Tj máxima de diseño (criterio) | 150 | °C | P | AC | — | Margen sobre los 175 °C del SCT012H90G3AG |
| t_dead_mrg | Margen adicional en el cálculo del tiempo muerto mínimo | 20 | ns | P | TBD | PWR-04 | PROVISIONAL. |

## 4. DC-link y protección del bus

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| Cdc | Capacidad del DC-link en placa | 105 | µF | TFG | AC | DCB-07 · HW-02 · HW-03 |  |
| V_film | Tensión nominal de los condensadores del DC-link | 650 | V | TFG | AC | DCB-02 · HW-02 | No cubre los 600 V de DCB-02 |
| ESR_dc | ESR equivalente del DC-link a 2·fsw | 2 | mΩ | — | TBD | HW-02 | PROVISIONAL. |
| N_dc_abs | Número de DC-link que absorben la energía en el caso de fallo | 1 | – | P | AC | DCB-08 · HW-03 | 1 = solo la propia placa (conservador) |
| V_chop_on | Tensión de actuación del clamp o chopper (si se usa) | 550 | V | P | TBD | HW-03 | PROVISIONAL. |
| k_chop_mrg | Margen mínimo de V_chop_on sobre Vbus_max (criterio) | 1,1 | – | P | TBD | HW-03 | PROVISIONAL |
| I_fuse | Corriente nominal del fusible en placa | 15 | A | TFG | AC | DCB-06 · HW-02 | 0ADKC9150-BE |
| V_fuse | Tensión nominal DC del fusible | 500 | V | TFG | AC | DCB-06 · HW-02 | 0ADKC9150-BE |
| k_fuse | Factor de utilización máximo del fusible (criterio) | 0,75 | – | P | TBD | DCB-06 | PROVISIONAL. Confirmar con la curva de derating del fabricante |

## 5. Gate driving

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| Vgs_on | Tensión de puerta en ON | 20 | V | TFG | AC | GD-01 · HW-02 |  |
| Vgs_off | Tensión de puerta en OFF | -5 | V | TFG | AC | GD-01 · HW-02 |  |
| Rg_on | Resistencia de puerta externa de encendido | 8 | Ω | — | TBD | HW-02 | PROVISIONAL. |
| Rg_off | Resistencia de puerta externa de apagado | 8 | Ω | — | TBD | HW-02 | PROVISIONAL. |
| N_d_desat | Número de diodos en serie en el circuito DESAT | 1 | – | — | TBD | HW-01 | PROVISIONAL. |
| Vf_desat | Caída de tensión de cada diodo DESAT | 0,7 | V | — | TBD | HW-01 | PROVISIONAL. |
| R_desat | Resistencia serie del circuito DESAT | 1 | kΩ | — | TBD | HW-01 | PROVISIONAL. |
| C_blank | Condensador de blanking del DESAT | 47 | pF | — | TBD | HW-01 | PROVISIONAL. |
| t_desat_max | Tiempo de respuesta máximo de la protección DESAT | 2 | µs | TFG | AC | GD-01 |  |

## 6. Sensado

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| R_shunt | Resistencia del shunt de corriente | 500 | µΩ | TFG | AC | SNS-01 · HW-02 |  |
| P_sh_rat | Potencia nominal del shunt | 3 | W | — | TBD | HW-02 | PROVISIONAL. Referencia del shunt del TFG no documentada aquí |
| I_margin | Margen mínimo fondo de escala / Ipk (criterio) | 1,2 | – | P | AC | SNS-01 |  |
| I_OC | Umbral de sobrecorriente por hardware | 90 | A | — | TBD | SAF-04 · HW-01 | PROVISIONAL. |
| f_clk_ds | Frecuencia de reloj de los moduladores ΔΣ | 20 | MHz | P | TBD | SNS-05 · FW-01 | PROVISIONAL. |
| OSR | Relación de sobremuestreo del filtro sinc | 128 | – | P | TBD | SNS-05 · FW-01 | PROVISIONAL. |
| N_sinc | Orden del filtro sinc | 3 | – | P | TBD | FW-01 | sinc3 es el habitual con moduladores de 2.º orden |
| N_adc | Resolución del ADC (opción amplificador aislado + ADC) | 12 | bit | — | TBD | SNS-05 · FW-01 | PROVISIONAL. |
| V_meas_FS | Fondo de escala deseado de la medida de Vbus | 700 | V | P | TBD | SNS-02 | PROVISIONAL. Debe cubrir la tensión del caso de fallo |
| V_sens_FS | Entrada lineal del sensor aislado de Vbus | 0,25 | V | — | TBD | SNS-02 · HW-02 | PROVISIONAL. Ejemplo: AMC1306x25 (±250 mV) |
| R_sens_in | Impedancia de entrada del sensor de Vbus | 22 | kΩ | — | TBD | HW-02 | AMC1306x25: 22 kΩ diferencial (hoja de datos) |
| R_div_bot | Resistencia inferior del divisor de Vbus | 1 | kΩ | — | TBD | SNS-02 | PROVISIONAL. |
| V_res_rat | Tensión máxima de trabajo de cada resistencia del divisor | 200 | V | — | TBD | HW-02 | PROVISIONAL. Depende del encapsulado elegido |
| P_res_rat | Potencia nominal de cada resistencia del divisor | 0,25 | W | — | TBD | HW-02 | PROVISIONAL. |
| k_res | Factor de utilización de potencia de las resistencias (criterio) | 0,5 | – | P | TBD | — | PROVISIONAL. |
| V_OV | Umbral de sobretensión de bus por hardware | 450 | V | — | TBD | SAF-01 · HW-01 | PROVISIONAL. |
| NTC_R25 | Resistencia de la NTC a 25 °C | 10 | kΩ | TFG | AC | LOAD-08 · HW-02 | GA10K4A1IA (TE) |
| NTC_beta | Constante β(25/85) de la NTC | 3694 | K | TE | AC | LOAD-08 | Página de producto TE; contrastar con la tabla R-T |
| R_ntc_pu | Resistencia de polarización de la NTC | 10 | kΩ | — | TBD | SNS-03 | PROVISIONAL. |
| V_ntc_ref | Tensión de referencia del divisor de la NTC | 5 | V | — | TBD | SNS-03 | PROVISIONAL. |

## 7. Refrigeración y entorno

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| T_amb | Temperatura ambiente máxima | 40 | °C | — | TBD | MEC-06 · ME-C-02 | PROVISIONAL. El TFG asumía ≥ 25 °C |
| T_cool | Temperatura del refrigerante a la entrada | 40 | °C | — | TBD | ME-C-02 | PROVISIONAL. |
| Q_cool | Caudal de refrigerante | 2 | L/min | — | TBD | ME-C-02 | PROVISIONAL. |
| N_cool_ser | Placas en serie en el circuito de agua (la última es la peor) | 1 | – | — | TBD | ME-C-01 · ME-C-02 | PROVISIONAL. |
| Rth_wb | Resistencia térmica cara inferior de la PCB → agua, por MOSFET | 0,3 | K/W | — | TBD | PWR-06 · ME-C-01 | PROVISIONAL. |
| t_TIM | Espesor del material de interfaz térmica | 0,5 | mm | — | TBD | ME-C-01 | PROVISIONAL. |
| k_TIM | Conductividad del material de interfaz térmica | 3 | W/(m·K) | — | TBD | ME-C-01 | PROVISIONAL. |
| V_TIM_bd | Rigidez dieléctrica del material de interfaz (tensión de ruptura) | 4000 | V | — | TBD | ISO-04 · ME-C-01 | PROVISIONAL. El pad de drenador está en HV |
| k_spread | Área efectiva bajo el TIM / área del pad (ensanchamiento) | 2 | – | P | TBD | — | PROVISIONAL. |
| A_pad | Área del pad de drenador del MOSFET | 80 | mm² | — | TBD | HW-02 | PROVISIONAL. Comprobar con el footprint H2PAK-7 |
| d_via | Diámetro de taladro de las vías térmicas | 0,3 | mm | — | TBD | PT-01 | PROVISIONAL. |
| t_plat | Espesor del metalizado de las vías | 25 | µm | — | TBD | PT-01 | PROVISIONAL. |
| N_via | Número de vías térmicas bajo cada MOSFET | 40 | – | — | TBD | — | PROVISIONAL. |
| t_solder | Espesor de la soldadura bajo el pad | 0,1 | mm | — | TBD | PT-02 | PROVISIONAL. |
| k_solder | Conductividad de la soldadura | 50 | W/(m·K) | — | AC | — | Orden de magnitud de aleaciones SAC |
| k_Cu | Conductividad del cobre | 385 | W/(m·K) | — | OK | — | Valor físico |
| k_FR4 | Conductividad del FR-4 en el eje z | 0,3 | W/(m·K) | — | AC | PT-01 | Orden de magnitud; confirmar con el laminado |

## 8. PCB: stackup, pistas y aislamiento

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| t_pcb | Espesor total de la PCB | 1,6 | mm | — | TBD | MEC-03 · PT-01 | PROVISIONAL. |
| oz_ext | Cobre en capas externas | 2 | oz | TFG | AC | MEC-03 · PT-01 | 1 oz ≈ 35 µm |
| oz_int | Cobre en capas internas | 2 | oz | TFG | AC | MEC-03 · PT-01 | El documento indica 2 oz sin distinguir capas |
| dT_trace | Incremento de temperatura admisible en pistas (criterio) | 20 | °C | P | AC | — |  |
| er_pcb | Permitividad relativa del dieléctrico | 4,3 | – | — | TBD | PT-01 | PROVISIONAL. |
| h_ms | Dieléctrico entre capa externa y su plano de referencia (microstrip) | 0,2 | mm | — | TBD | PT-01 | PROVISIONAL |
| b_sl | Distancia entre planos de referencia de la stripline | 0,5 | mm | — | TBD | PT-01 | PROVISIONAL |
| tol_Z | Tolerancia admisible de impedancia (criterio) | 10 | % | P | AC | PT-01 | Tolerancia habitual de fabricación; confirmar con el fabricante |
| Ins_type | Tipo de aislamiento HV–BT: «Básico» o «Reforzado» | Básico | – | — | TBD | ISO-05 · HW-04 | PROVISIONAL. |
| PD_coat | Grado de contaminación bajo el coating (IEC 60664-3) | 1 | – | P | AC | ISO-02 · HW-04 |  |
| PD_bare | Grado de contaminación en superficies sin coating | 2 | – | P | TBD | HW-04 | PROVISIONAL. |
| d_HV_LV | Separación mínima HV–BT con coating (regla de la competición) | 4 | mm | U | OK | ISO-02 |  |
| d_HV_HV | Separación mínima entre redes de HV | 2 | mm | TFG | AC | ISO-03 · HW-04 |  |
| d_WB | Separación mínima taladros del waterblock – conductores | 4 | mm | TFG | AC | ISO-04 · ME-C-01 |  |

## 9. Alimentación auxiliar (BT)

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| V_BT_max | Tensión máxima de la batería de BT | 24 | V | U | OK | AUX-01 |  |
| V_BT_min | Tensión mínima de la batería de BT | 18 | V | — | TBD | AUX-03 · ME-I-02 | PROVISIONAL. |
| P_BT_lim | Consumo máximo permitido por placa | 15 | W | — | TBD | AUX-03 · ME-I-02 | PROVISIONAL. |
| eta_BT | Rendimiento de la etapa de entrada BT | 85 | % | — | TBD | AUX-02 · HW-05 | PROVISIONAL. |
| P_margin | Margen sobre el consumo total estimado (criterio) | 20 | % | P | AC | — |  |

## 10. Integridad de señal: presupuesto de tiempos (interfaz MII/RMII u otra síncrona)

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| f_bus_clk | Frecuencia de reloj de la interfaz FPGA–PHY | 50 | MHz | P | TBD | COM-02 · FW-06 | PROVISIONAL. RMII: 50 MHz; MII: 25 MHz |
| tco_max | Retardo de salida máximo del emisor (clock-to-out) | 10 | ns | — | TBD | FW-06 | PROVISIONAL. Hoja de datos del PHY / FPGA |
| tco_min | Retardo de salida mínimo del emisor | 2 | ns | — | TBD | FW-06 | PROVISIONAL. |
| t_su | Tiempo de setup del receptor | 4 | ns | — | TBD | FW-06 | PROVISIONAL. |
| t_h | Tiempo de hold del receptor | 2 | ns | — | TBD | FW-06 | PROVISIONAL. |
| t_jit | Jitter y otras incertidumbres del reloj | 0,5 | ns | — | TBD | FW-06 | PROVISIONAL. |
| dL_clk | Diferencia de longitud del reloj entre emisor y receptor | 10 | mm | — | TBD | — | PROVISIONAL |
| skew_pair | Desfase admisible dentro de un par diferencial | 5 | ps | — | TBD | COM-03 | PROVISIONAL. Criterio del fabricante del PHY o de los magnéticos |
| SI_if_datos | Interfaz de datos usada en el presupuesto de tiempos (clave de diseno.md) | datos_phy | – | P | TBD | COM-02 · FW-06 |  |
| SI_if_reloj | Interfaz de reloj usada en el presupuesto de tiempos (clave de diseno.md) | reloj_phy | – | P | TBD | COM-02 · FW-06 |  |
| SI_if_par | Par diferencial usado para la igualación de longitudes (clave de diseno.md) | mdi_in | – | P | TBD | COM-03 |  |
