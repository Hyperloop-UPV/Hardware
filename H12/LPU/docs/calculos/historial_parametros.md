# Historial de cambios de parámetros

## 19/09/2026 18:17 (hora de Madrid)

Versión: commit `65be21b`

| Parámetro | Antes | Ahora | Estado | Fuente |
|---|---|---|---|---|
| IMT65R010M2H: Ciss | (no existía) | 2500 pF |  |  |
| IMT65R010M2H: Coss | (no existía) | 180 pF |  |  |
| IMT65R010M2H: Crss | (no existía) | 18 pF |  |  |
| IMT65R010M2H: Energía de apagado | (no existía) | 600 µJ |  |  |
| IMT65R010M2H: Energía de encendido | (no existía) | 500 µJ |  |  |
| IMT65R010M2H: ID continua (Tc = 25 °C) | (no existía) | 80 A |  |  |
| IMT65R010M2H: ID pulsada | (no existía) | 300 A |  |  |
| IMT65R010M2H: Corriente de ensayo de Eon/Eoff | (no existía) | 40 A |  |  |
| IMT65R010M2H: Carga total de puerta | (no existía) | 95 nC |  |  |
| IMT65R010M2H: Carga de recuperación inversa | (no existía) | 200 nC |  |  |
| IMT65R010M2H: RDS(on) típica a 25 °C | (no existía) | 10 mΩ |  |  |
| IMT65R010M2H: RDS(on) máxima a 25 °C | (no existía) | 12 mΩ |  |  |
| IMT65R010M2H: Resistencia interna de puerta | (no existía) | 1,5 Ω |  |  |
| IMT65R010M2H: RG de ensayo de Eon/Eoff y de los tiempos | (no existía) | 15 Ω |  |  |
| IMT65R010M2H: RDS(on) típica a temperatura alta | (no existía) | 15 mΩ |  |  |
| IMT65R010M2H: Rth unión-cápsula | (no existía) | 0,35 K/W |  |  |
| IMT65R010M2H: Temperatura de la RDS(on) anterior | (no existía) | 175 °C |  |  |
| IMT65R010M2H: Tj máxima | (no existía) | 175 °C |  |  |
| IMT65R010M2H: VDS máxima | (no existía) | 650 V |  |  |
| IMT65R010M2H: VGS máxima absoluta (positiva) | (no existía) | 20 V |  |  |
| IMT65R010M2H: VGS máxima absoluta (negativa) | (no existía) | -20 V |  |  |
| IMT65R010M2H: VGS recomendada en OFF (mínima) | (no existía) | -5 V |  |  |
| IMT65R010M2H: VGS recomendada en ON (máxima) | (no existía) | 15 V |  |  |
| IMT65R010M2H: Tensión del diodo interno | (no existía) | 1,2 V |  |  |
| IMT65R010M2H: Tensión de ensayo de Eon/Eoff | (no existía) | 400 V |  |  |
| IMT65R010M2H: VGS(th) mínima | (no existía) | 3,0 V |  |  |
| IMT65R010M2H: Fabricante | (no existía) | Infineon |  |  |
| IMT65R010M2H: Encapsulado | (no existía) | PG‑HSOF‑8 |  |  |
| IMT65R010M2H: Referencia | (no existía) | IMT65R010M2H |  |  |
| IMT65R010M2H: td(off) | (no existía) | 55 ns |  |  |
| IMT65R010M2H: td(on) | (no existía) | 30 ns |  |  |
| IMT65R010M2H: tf | (no existía) | 20 ns |  |  |
| IMT65R010M2H: tr | (no existía) | 40 ns |  |  |
| Área del pad de drenador del MOSFET (`A_pad`) | 80 mm² | 70 mm² | TBD → AC | — → HD |
| Identificación de posición: «AutoIncr», «EEPROM» o «Selector» | (no existía) | AutoIncr | TBD | P |
| Distribución del bus: «Encadenado» o «Estrella» (`Bus_topo`) | Estrella | Estrella | TBD → AC | TFG → P |
| Condensador de blanking del DESAT (`C_blank`) | 47 pF | 47 pF | TBD → AC | — → P |
| Plataforma de control: «FPGA» o «MCU» | (no existía) | FPGA | TBD | P |
| Referencia del gate driver usado en el resto de cálculos (columna de componentes.md) | (no existía) | STGAP3S6S | AC | P |
| Implementación del esclavo EtherCAT: «IPcore», «ESCext» o «ESCint» | (no existía) | IPcore | TBD | P |
| ESR equivalente del DC-link a 2·fsw (`ESR_dc`) | 2 mΩ | 2 mΩ | TBD | — → P |
| Energía total a absorber en el caso de fallo común | (no existía) | 200 J | AC | C |
| Umbral de sobrecorriente por hardware (`I_OC`) | 90 A | 90 A | TBD → AC | — → P |
| Corriente de disparo máxima admisible del DESAT (criterio) | (no existía) | 300 A | AC | P |
| Tipo de aislamiento HV–BT: «Básico» o «Reforzado» (`Ins_type`) | Básico | Básico | TBD | — → P |
| Corriente de pico (primeros segundos de la levitación) (`Ipk`) | 55 A | 60 A | OK | U |
| Corriente eficaz en régimen permanente (dimensionado térmico) (`Irms_cont`) | 10 A | 5 A | TBD | TFG |
| Inductancia parásita objetivo del lazo de conmutación | (no existía) | 15 nH | TBD | P |
| Referencia del MOSFET usado en el resto de cálculos (una de las columnas de componentes.md) (`MOSFET_sel`) | SCT012H90G3AG | IMT65R010M2H | AC | P → U |
| Modulación: «Unipolar» o «Bipolar» (`Modulacion`) | Bipolar | Unipolar | TBD | TFG |
| Resolución del ADC (opción amplificador aislado + ADC) (`N_adc`) | 12 bit | 12 bit | TBD | — → P |
| Canales ΔΣ necesarios en el controlador | (no existía) | 1 | AC | P |
| Placas en serie en el circuito de agua (la última es la peor) (`N_cool_ser`) | 1 | 1 | TBD | — → P |
| Número de diodos en serie en el circuito DESAT (`N_d_desat`) | 1 | 1 | TBD → AC | — → P |
| Número de DC-link que absorben la energía en el caso de fallo (`N_dc_abs`) | 1 | 1 | AC → OK | P → C |
| Puertos EtherCAT montados por placa | (no existía) | 2 | OK | P |
| Número de módulos que pierden la rueda libre a la vez (caso dimensionante) | (no existía) | 10 | AC | C |
| PHY Ethernet externos por placa | (no existía) | 2 | AC | P |
| Orden del filtro sinc (`N_sinc`) | 3 | 3 | TBD → AC | P |
| Número de vías térmicas bajo cada MOSFET (`N_via`) | 10 | 36 | TBD → AC | — → P |
| Grado de contaminación en superficies sin coating (`PD_bare`) | 2 | 2 | TBD → AC | P |
| Consumo máximo permitido por placa (`P_BT_lim`) | 15 W | 15 W | TBD | — → P |
| Potencia nominal de cada resistencia del divisor (`P_res_rat`) | 0,25 W | 0,25 W | TBD → AC | — → P |
| Potencia nominal del shunt (`P_sh_rat`) | 3 W | 3 W | TBD → AC | — → P |
| Caudal de refrigerante (`Q_cool`) | 2 L/min | 2 L/min | TBD | — → P |
| Resistencia serie del circuito DESAT (`R_desat`) | 1 kΩ | 1 kΩ | TBD → AC | — → P |
| Resistencia inferior del divisor de Vbus (`R_div_bot`) | 1 kΩ | 1 kΩ | TBD → AC | — → P |
| Resistencia de polarización de la NTC (`R_ntc_pu`) | 10 kΩ | 10 kΩ | TBD → AC | — → P |
| Impedancia de entrada del sensor de Vbus (`R_sens_in`) | 22 kΩ | 22 kΩ | TBD → AC | — → HD |
| Resistencia de la bobina (`Rcoil`) | 1,1 Ω | 1,2 Ω | OK | U |
| Resistencia de puerta externa de apagado (`Rg_off`) | 8 Ω | 8 Ω | TBD → AC | — → P |
| Resistencia de puerta externa de encendido (`Rg_on`) | 8 Ω | 8 Ω | TBD → AC | — → P |
| Redundancia en anillo del bus: «Si» o «No» | (no existía) | No | TBD | P |
| Resistencia térmica cara inferior de la PCB → agua, por MOSFET (`Rth_wb`) | 0,3 K/W | 0,3 K/W | TBD | — → P |
| Cadena de sensado de corriente: «DeltaSigma» o «AmpAislado» | (no existía) | DeltaSigma | TBD | P |
| Temperatura ambiente máxima (`T_amb`) | 50 °C | 50 °C | TBD | — → P |
| Temperatura máxima de la bobina (umbral de protección) (`T_coil_max`) | 110 °C | 110 °C | TBD | — → P |
| Temperatura del refrigerante a la entrada (`T_cool`) | 50 °C | 50 °C | TBD | — → P |
| Tensión mínima de la batería de BT (`V_BT_min`) | 18 V | 18 V | TBD | — → P |
| Umbral de sobretensión de bus por hardware (`V_OV`) | 420 V | 450 V | TBD → AC | — → P |
| Rigidez dieléctrica del material de interfaz (tensión de ruptura) (`V_TIM_bd`) | 4000 V | 4000 V | TBD → AC | — → P |
| Tensión de actuación del clamp o chopper (`V_chop_on`) | 550 V | 500 V | TBD → AC | P |
| Tensión máxima admisible en el DC-link durante el caso de fallo | (no existía) | 520 V | AC | C |
| Tensión continua que deben soportar componentes y aislamiento (`V_cont`) | 650 V | 600 V | OK | U |
| Tensión nominal de los condensadores del DC-link (`V_film`) | 650 V | 630 V | AC | TFG → P |
| Fondo de escala deseado de la medida de Vbus (`V_meas_FS`) | 700 V | 700 V | TBD → AC | P |
| Tensión de referencia del divisor de la NTC (`V_ntc_ref`) | 5 V | 5 V | TBD → AC | — → P |
| Tensión máxima de trabajo de cada resistencia del divisor (`V_res_rat`) | 200 V | 200 V | TBD → AC | — → P |
| Entrada lineal del sensor aislado de Vbus (`V_sens_FS`) | 0,25 V | 0,25 V | TBD → AC | — → HD |
| Tensión máxima del bus de HV (`Vbus_max`) | 405 V | 400 V | OK | U |
| Tensión mínima del bus de HV (`Vbus_min`) | 350 V | 320 V | OK | U |
| Caída de tensión de cada diodo DESAT (`Vf_desat`) | 0,7 V | 0,7 V | TBD → AC | — → P |
| Tensión de puerta en OFF (`Vgs_off`) | -5 V | -3 V | AC | TFG → P |
| Tensión de puerta en ON (`Vgs_on`) | 20 V | 18 V | AC | TFG → HD |
| Tensión de puerta en ON alternativa (módulo de 15 V) | (no existía) | 15 V | TBD | P |
| Distancia entre planos de referencia de la stripline (`b_sl`) | 0,5 mm | 0,5 mm | TBD → AC | — → P |
| Rizado de corriente pico a pico máximo admisible (`dI_pp_max`) | 1,5 A | 1,5 A | TBD | — → P |
| Diferencia de longitud del reloj entre emisor y receptor (`dL_clk`) | 10 mm | 10 mm | TBD | — → P |
| Rizado máximo de tensión en el DC-link (fracción de Vbus_min) (`dVdc_pct`) | 1 % | 2 % | AC | TFG |
| Diámetro de taladro de las vías térmicas (`d_via`) | 0,3 mm | 0,3 mm | TBD → AC | — → P |
| Permitividad relativa del dieléctrico (`er_pcb`) | 4,5 | 4,5 | TBD → AC | — → P |
| Rendimiento de la etapa de entrada BT (`eta_BT`) | 85 % | 85 % | TBD | — → P |
| Rendimiento de la etapa de potencia (para la corriente media de bus) (`eta_pwr`) | 96 % | 97 % | TBD → AC | P → C |
| Frecuencia de reloj de los moduladores ΔΣ (`f_clk_ds`) | 20 MHz | 20 MHz | TBD → AC | P |
| Frecuencia de conmutación (`fsw`) | 30 kHz | 20 kHz | TBD | TFG |
| Dieléctrico entre capa externa y su plano de referencia (microstrip) (`h_ms`) | 0,2 mm | 0,2 mm | TBD → AC | — → P |
| Conductividad del material de interfaz térmica (`k_TIM`) | 3 W/(m·K) | 3 W/(m·K) | TBD → AC | — → P |
| Margen mínimo de V_chop_on sobre Vbus_max (criterio) (`k_chop_mrg`) | 1,1 | 1,1 | TBD → AC | P |
| Factor de utilización máximo del fusible (criterio) (`k_fuse`) | 0,75 | 0,75 | TBD → AC | P |
| Factor de utilización de potencia de las resistencias (criterio) (`k_res`) | 0,5 | 0,5 | TBD → AC | P |
| Conductividad de la soldadura (`k_solder`) | 50 W/(m·K) | 50 W/(m·K) | AC | — → HD |
| Factor de utilización máximo de VDS (criterio) | (no existía) | 0,8 | AC | HD |
| Factor de utilización máximo de VGS (criterio) | (no existía) | 0,8 | AC | HD |
| Desfase admisible dentro de un par diferencial (`skew_pair`) | 5 ps | 5 ps | TBD | — → P |
| Espesor del material de interfaz térmica (`t_TIM`) | 0,5 mm | 0,5 mm | TBD → AC | — → P |
| Tiempo muerto (`t_dead`) | 120 ns | 100 ns | AC | TFG |
| Margen adicional en el cálculo del tiempo muerto mínimo (`t_dead_mrg`) | 20 ns | 20 ns | TBD → AC | P |
| Tiempo de hold del receptor (`t_h`) | 2 ns | 2 ns | TBD | — → P |
| Jitter y otras incertidumbres del reloj (`t_jit`) | 0,5 ns | 0,5 ns | TBD | — → P |
| Latencia máxima admisible de la cadena de medida de corriente | (no existía) | 10 µs | TBD | P |
| Espesor total de la PCB (`t_pcb`) | 1,6 mm | 1,6 mm | TBD → AC | — → P |
| Duración del pico de corriente (`t_pk`) | 2 s | 2 s | TBD → OK | — → U |
| Espesor del metalizado de las vías (`t_plat`) | 25 µm | 25 µm | TBD → AC | — → P |
| Espesor de la soldadura bajo el pad (`t_solder`) | 0,1 mm | 0,1 mm | TBD → AC | — → P |
| Tiempo de setup del receptor (`t_su`) | 4 ns | 4 ns | TBD | — → P |
| Tiempo de reacción objetivo del disparo por hardware del controlador | (no existía) | 1 µs | AC | P |
| Retardo de salida máximo del emisor (clock-to-out) (`tco_max`) | 10 ns | 10 ns | TBD | — → P |
| Retardo de salida mínimo del emisor (`tco_min`) | 2 ns | 2 ns | TBD | — → P |

