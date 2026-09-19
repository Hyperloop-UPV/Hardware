# Parámetros de diseño

Parámetros escalares de los cálculos del Magnet Driver Abejorro. **Este es el fichero que se edita normalmente.**

- Cambie solo las columnas «Valor», «Estado», «Fuente» y «Nota». La columna «Nombre» es la que usan las fórmulas: no la cambie.
- Decimales con coma o con punto (`1,92` o `1.92`), sin separador de miles. Signo menos con `-` o `−`.
- Unidades admitidas: ver `calculos/README.md`. Un valor en `%` se interpreta como fracción (2 % → 0,02).
- «Estado»: `OK` (confirmado), `AC` (a confirmar) o `TBD` (desconocido: el valor es **provisional** y solo sirve para calcular).
- «Fuente»: `U` (equipo), `TFG` (TFG de L. Navarro), `C` (cálculo del documento de requisitos), `P` (propuesta), `HD` (hoja de datos) o el documento o fabricante citado.
- No use el carácter `|` dentro de las celdas.

> **Revisión del 19/09/2026.** Se han sustituido los valores de prueba del motor de cálculos por los del documento de requisitos v0.3 y de las hojas de datos. Ahora **ningún valor contradice al documento de requisitos**: donde el requisito da un número, está ese número y el `Estado` refleja el del requisito; donde no lo da, el valor es una propuesta `[P]` justificada en la nota, con `AC` si se puede defender con un cálculo y `TBD` si sigue siendo un hueco real. Los valores que cambian respecto a la versión de prueba llevan **[v0.3]** en la nota.
>
> Quedan **dos huecos que ningún cálculo puede rellenar** y que están marcados TBD a propósito: el perfil térmico del refrigerante (ME-C-02) y el presupuesto de tiempos de la interfaz con el PHY (FW-06).

> **Revisión del 19/09/2026 (v0.4).** Se añade la **sección 11**, que recoge la plataforma de control y la implementación del bus, ahora que la FPGA deja de ser la hipótesis de partida (FW-09 del documento de requisitos). Los parámetros nuevos llevan **[v0.4]** en la nota y salen todos como `TBD` o `AC`: **ninguno es una decisión tomada**, solo el valor provisional que usa el motor de cálculos mientras FW-09 no se cierre. Se actualizan además las notas de `OSR`, `N_adc` y `f_bus_clk`, y la cabecera de la sección 10.
>
> Cuidado al leer la sección 10: **su presupuesto de tiempos solo aplica si la interfaz con el ESC es MII o RMII**. Si FW-09 lleva a un ESC externo tipo LAN9252, la interfaz pasa a SPI/SQI y ese apartado hay que rehacerlo entero.

## 1. Bus DC

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| Vbus_min | Tensión mínima del bus de HV | 320 | V | U | OK | DCB-01 | [v0.3] Antes 350 V (prueba). Valor de DCB-01 |
| Vbus_max | Tensión máxima del bus de HV | 400 | V | U | OK | DCB-01 | [v0.3] Antes 405 V (prueba). Valor de DCB-01. Confirmado el 19/09/2026 que la batería seguirá siendo de 400 V mucho tiempo |
| V_cont | Tensión continua que deben soportar componentes y aislamiento | 600 | V | U | OK | DCB-02 · ISO-06 · HW-08 | [v0.3] Antes 650 V (prueba). Valor de DCB-02. **Atención (HW-08):** el IMT65R010M2H es de 650 V, así que frente a este requisito trabaja al 92 % de su tensión de ruptura. Hay que decidir si el requisito de 600 V continuos aplica a los interruptores o solo al aislamiento y a los pasivos |
| N_MD | Número de Magnet Driver conectados al bus | 10 | – | U | OK | DCB-03 · SYS-01 | 4 HEMS + 6 EMS |
| Bus_topo | Distribución del bus: «Encadenado» o «Estrella» | Estrella | – | P | AC | DCB-05 · ME-I-03 · EM-C-05 | Si los 10 pican a la vez el bus entrega unos 108 A y el encadenado obligaría a la primera placa a conducirlos. Pendiente de que Electromagnetics confirme la simultaneidad |
| dVdc_pct | Rizado máximo de tensión en el DC-link (fracción de Vbus_min) | 2 | % | TFG | AC | DCB-07 · HW-02 | [v0.3] Antes 1 % (prueba). DCB-07 dice ≤ 2 %, que son 8 V sobre 400 V |
| eta_pwr | Rendimiento de la etapa de potencia (para la corriente media de bus) | 97 | % | C | AC | — | [v0.3] Antes 96 % (provisional). Calculado a 60 A: 4320 W a la bobina, 72 W de conducción y 23 a 47 W de conmutación según el reescalado de Eon/Eoff a `Rg_on` → 97,3 a 97,8 %. Se redondea a 97 % por debajo |

## 2. Carga: electroimanes (prototipo H11)

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| Rcoil | Resistencia de la bobina | 1,2 | Ω | U | OK | LOAD-01 | [v0.3] Antes 1,1 Ω (prueba). Valor de LOAD-01, medido en la bobina construida. Nuevas bobinas: EM-D-04 |
| Ipk | Corriente de pico (primeros segundos de la levitación) | 60 | A | U | OK | LOAD-03 | [v0.3] Antes 55 A (valor del TFG). Valor de LOAD-03. Los 55 A siguen siendo el límite de los mapas de inductancia (`I_map`) |
| t_pk | Duración del pico de corriente | 2 | s | U | OK | LOAD-03 · EM-C-01 | Confirmado el 19/09/2026: no será mucho mayor de 2 s. A 2 s el die está prácticamente en régimen permanente, así que el térmico se evalúa con `Rthjc` y no con la impedancia transitoria |
| Irms_cont | Corriente eficaz en régimen permanente (dimensionado térmico) | 5 | A | TFG | TBD | LOAD-05 · EM-C-01 | [v0.3] Antes 10 A (prueba). LOAD-05 recoge los 5 A que menciona el TFG, sin revalidar. Es el dato que falta de EM-C-01 |
| L_EMS_min | Inductancia incremental mínima del EMS | 1,92 | mH | R5 | AC | LOAD-01 · EM-D-01/02 | Sección 6.1.1 |
| L_EMS_max | Inductancia incremental máxima del EMS | 117 | mH | R5 | AC | LOAD-01 · EM-D-01/02 | Sección 6.1.1 |
| L_HEMS_min | Inductancia incremental mínima del HEMS (dψ/di derivada) | 6,2 | mH | C | OK | LOAD-01 | Sección 6.1.2 (derivado del Excel R7) |
| L_HEMS_max | Inductancia incremental máxima del HEMS (dψ/di derivada) | 11,2 | mH | C | OK | LOAD-01 | Sección 6.1.2 |
| L_EMS_0 | Inductancia del EMS a I = 0 (valor citado, columnas 5–6) | 26,7 | mH | R5 | AC | 6.1.1 | Solo para la cota pesimista de energía (L constante) |
| E_EMS | Energía devuelta al desmagnetizar el EMS desde 55 A (mapa H11) | 15,6 | J | C | AC | 6.1.3 · EM-D-03 | Mapa hasta ±55 A |
| E_HEMS | Energía devuelta al desmagnetizar el HEMS desde −55 A, 6 mm (mapa H11) | 16,7 | J | C | AC | 6.1.3 · EM-D-03 | Peor caso del H11. A 60 A escala por (60/55)² ≈ 1,19 → unos 20 J, que es lo que alimenta `E_fault_tot` |
| I_map | Corriente máxima cubierta por los mapas de inductancia | 55 | A | R7 | OK | EM-D-03 | Por debajo de `Ipk`: los 60 A hay que extrapolar hasta que llegue EM-D-03 |
| dI_pp_max | Rizado de corriente pico a pico máximo admisible | 1,5 | A | P | TBD | LOAD-07 · EM-C-03 | El rizado calculado en 6.1.3 para el peor caso (EMS, 20 kHz, unipolar, 400 V) es 1,30 A, así que el límite queda coherente con un 15 % de margen. Sigue pendiente el valor que imponga EM-C |
| T_coil_max | Temperatura máxima de la bobina (umbral de protección) | 110 | °C | P | TBD | SAF-01 · EM-D | Con la GA10K4A1IA (10 kΩ, β = 3598) a 110 °C la NTC vale 688 Ω y el divisor con `R_ntc_pu` y `V_ntc_ref` da 0,322 V: hay resolución de sobra. Falta que EM-D fije el umbral real de la bobina |

## 3. Conmutación y MOSFET

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| fsw | Frecuencia de conmutación | 20 | kHz | TFG | TBD | PWR-03 · FW-08 | [v0.3] Antes 30 kHz (prueba). Valor de PWR-03. Pasa a ser configurable en la FPGA: FW-08 debe dar el rango que el hardware tiene que admitir |
| Modulacion | Modulación: «Unipolar» o «Bipolar» | Unipolar | – | TFG | TBD | PWR-03 · FW-08 | [v0.3] Antes «Bipolar» (prueba). Valor de PWR-03. Afecta al rizado de 6.1.3 |
| t_dead | Tiempo muerto | 100 | ns | TFG | AC | PWR-04 · FW-08 | [v0.3] Antes 120 ns (prueba). PWR-04 cita la red RC de 100 ns del TFG como punto de partida. Con el diodo de cuerpo del IMT65R010M2H a 4,3 V, conviene el mínimo compatible con `D_skew` (10 ns) más `t_dead_mrg` y los tiempos de conmutación |
| MOSFET_sel | Referencia del MOSFET usado en el resto de cálculos (una de las columnas de componentes.md) | IMT65R010M2H | – | U | AC | PWR-02 · HW-02 · HW-03 | Elegido por disponibilidad (stock en el taller y en distribución) frente al SCT012H90G3AG, a 25 semanas de plazo. Condicionado a resolver HW-03 |
| D_worst | Fracción del periodo que conduce el MOSFET más cargado | 1 | – | P | OK | SAF-05 | 1 = rueda libre permanente por los low-side (conservador). Con PWM en régimen, el más cargado conduce (1 + m)/2 |
| Tj_assumed | Tj supuesta para evaluar RDS(on) | 125 | °C | P | AC | — | Debe ser ≥ Tj calculada (comprobación en el apartado MOSFET) |
| Tj_lim | Tj máxima de diseño (criterio) | 150 | °C | P | AC | — | Margen de 25 °C sobre los 175 °C del IMT65R010M2H y del SCT012H90G3AG |
| t_dead_mrg | Margen adicional en el cálculo del tiempo muerto mínimo | 20 | ns | P | AC | PWR-04 | Cubre el desfase entre drivers (`D_skew` = 10 ns en el STGAP3S6S) más la dispersión de los tiempos de apagado |
| k_vds | Factor de utilización máximo de VDS (criterio) | 0,8 | – | HD | AC | PWR-02 · HW-03 | Hoja de datos R8: «for optimum lifetime and reliability, Infineon recommends operating conditions that do not exceed 80% of the maximum ratings». 0,8 × 650 V = 520 V |

## 4. DC-link y protección del bus

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| Cdc | Capacidad del DC-link en placa | 105 | µF | TFG | AC | DCB-07 · HW-02 · HW-03 | Se mantiene para el rizado. Con 650 V, subirla no resuelve el caso de fallo: harían falta más de 3 mF (6.3) |
| V_film | Tensión nominal de los condensadores del DC-link | 630 | V | P | AC | DCB-02 · HW-02 | [v0.3] Antes 650 V (prueba); el TFG tenía 500 V, que no valen. Con el clamp actuando a `V_chop_on` la tensión máxima que ven es `V_clamp_lim` = 520 V, y 630 V es el escalón de catálogo que además cubre `V_cont` |
| ESR_dc | ESR equivalente del DC-link a 2·fsw | 2 | mΩ | P | TBD | HW-02 | Orden de magnitud de un banco de film con cerámicos en paralelo. Confirmar con las referencias que se elijan |
| N_dc_abs | Número de DC-link que absorben la energía en el caso de fallo | 1 | – | C | OK | DCB-08 · HW-03 | 1 por módulo. Aunque el bus es compartido y los 10 DC-link quedan en paralelo (1050 µF), el caso que dimensiona es el fallo común: los 10 módulos descargan a la vez, lo que equivale a 1 DC-link por módulo. El fallo de un módulo aislado sí reparte entre los 10 y llega solo a 438 V |
| N_fault_sim | Número de módulos que pierden la rueda libre a la vez (caso dimensionante) | 10 | – | C | AC | DCB-08 · HW-03 · EM-C-05 | Una pérdida de BT o una parada de emergencia afecta a los 10 módulos simultáneamente |
| E_fault_tot | Energía total a absorber en el caso de fallo común | 200 | J | C | AC | DCB-08 · DCB-09 | `N_fault_sim` × `E_HEMS` escalada a `Ipk` = 10 × 20 J. Revisar con EM-D-03 (mapas a 60 A) y EM-D-04 (bobinas nuevas) |
| V_clamp_lim | Tensión máxima admisible en el DC-link durante el caso de fallo | 520 | V | C | AC | HW-03 · DCB-09 | `k_vds` × VDS del MOSFET elegido. Con el SCT012H90G3AG serían 720 V |
| V_chop_on | Tensión de actuación del clamp o chopper | 500 | V | P | AC | HW-03 · DCB-09 | [v0.3] Antes 550 V (prueba), que está por encima de `V_clamp_lim`. Tiene que quedar entre `k_chop_mrg` × `Vbus_max` = 440 V y `V_clamp_lim` = 520 V. Se propone 500 V; la ventana es de 80 V |
| k_chop_mrg | Margen mínimo de V_chop_on sobre Vbus_max (criterio) | 1,1 | – | P | AC | HW-03 | 1,1 × 400 V = 440 V. Tiene que dejar pasar el rizado de `dVdc_pct` (8 V) y el umbral de `V_OV` |
| I_fuse | Corriente nominal del fusible en placa | 15 | A | TFG | AC | DCB-06 · HW-02 | 0ADKC9150-BE. La corriente media de bus por módulo durante el pico es 10,8 A a 400 V y 13,5 A a 320 V: el factor de utilización llega a 0,90 en el caso de 320 V, por encima de `k_fuse` |
| V_fuse | Tensión nominal DC del fusible | 500 | V | TFG | AC | DCB-06 · HW-02 | 0ADKC9150-BE. **No cubre `V_cont` (600 V) ni `V_chop_on` (500 V):** hay que sustituirlo en HW-02 por uno de ≥ 700 VDC |
| k_fuse | Factor de utilización máximo del fusible (criterio) | 0,75 | – | P | AC | DCB-06 | A 400 V el uso real es 0,72 y pasa; a 320 V es 0,90 y no pasa. Confirmar con la curva de derating del fabricante y con `Irms_cont` cuando llegue EM-C-01 |

## 5. Gate driving

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| DRIVER_sel | Referencia del gate driver usado en el resto de cálculos (columna de componentes.md) | STGAP3S6S | – | P | AC | GD-01 · GD-05 · HW-02 | Único candidato evaluado cuyo UVLO del raíl positivo está referido a la masa aislada. Verificar stock antes de comprometer |
| Vgs_on | Tensión de puerta en ON | 18 | V | HD | AC | GD-01 · HW-02 | [v0.3] Antes 20 V (TFG). Es la VGS a la que están especificadas RDS(on) y Qg en las hojas de datos de los dos MOSFET candidatos. 20 V es el 87 % de la VGS máxima del IMT65R010M2H, por encima de `k_vgs` |
| Vgs_off | Tensión de puerta en OFF | -3 | V | P | AC | GD-01 · HW-02 | [v0.3] Antes −5 V (TFG). El IMT65R010M2H limita la VGS estática a −7 V: −3 V es el 43 % y −5 V el 71 %. Con VGS(th) típica de 4,5 V y robustez declarada a 0 V, −3 V ya da la inmunidad necesaria. Si se prefiere −5 V, también cumple `k_vgs` |
| Vgs_on_alt | Tensión de puerta en ON alternativa (módulo de 15 V) | 15 | V | P | TBD | AUX-02 · HW-02 | Para evaluar la penalización de RDS(on) si no se consigue un raíl de 18 V. En el SCT012H90G3AG la penalización medida es del 12 % (13,4 frente a 12 mΩ) |
| k_vgs | Factor de utilización máximo de VGS (criterio) | 0,8 | – | HD | AC | GD-01 | Se aplica a VGSmax y a VGSmin del MOSFET elegido. Para el IMT65R010M2H: +18,4 V y −5,6 V |
| Rg_on | Resistencia de puerta externa de encendido | 8 | Ω | P | AC | HW-02 · PWR-07 | [v0.3] Sigue siendo 8 Ω pero ya está justificado: con `Rgint` = 1,7 Ω y ~1 Ω del driver, la corriente de pico de puerta es 1,96 A, muy por debajo de los 6 A del STGAP3S6S. El ensayo de R8 usa 3,3 Ω: hay que reescalar Eon/Eoff a este valor |
| Rg_off | Resistencia de puerta externa de apagado | 8 | Ω | P | AC | HW-02 · PWR-07 | Es la palanca principal sobre la sobreoscilación de PWR-07: subirla reduce el pico de VDS al apagar a costa de más Eoff. Ajustar tras medir en la primera placa |
| N_d_desat | Número de diodos en serie en el circuito DESAT | 1 | – | P | AC | HW-01 · GD-07 | Un solo diodo rápido de 1000 a 1200 V cubre `V_chop_on` con margen |
| Vf_desat | Caída de tensión de cada diodo DESAT | 0,7 | V | P | AC | HW-01 | Valor a la corriente de polarización del DESAT (unos 0,5 mA), no a corriente nominal. Se resta del umbral, así que baja la corriente de disparo |
| R_desat | Resistencia serie del circuito DESAT | 1 | kΩ | P | AC | HW-01 | Valor habitual para limitar la corriente al pin DESAT durante la conmutación |
| C_blank | Condensador de blanking del DESAT | 47 | pF | P | AC | HW-01 | Con el umbral de 3,5 V y los 527 µA del ADuM4146 da 312 ns de enmascaramiento, coherente con los 260 a 340 ns de la hoja de datos. **El STGAP3S6S fija el blanking por otro mecanismo:** revisar cuando se cierre `DRIVER_sel` |
| t_desat_max | Tiempo de respuesta máximo de la protección DESAT | 2 | µs | TFG | AC | GD-01 | El STGAP3S6S interviene en 150 ns y reporta por DIAG en 2,5 µs máx.: el requisito se cumple con holgura en la intervención |
| I_desat_max | Corriente de disparo máxima admisible del DESAT (criterio) | 300 | A | P | AC | GD-06 · HW-01 | 5 × `Ipk`. Con 10 mΩ y umbral de 6 V el DESAT dispara a 600 A (458 A en caliente), muy por encima: por eso la sobrecorriente de bobina la tiene que cubrir `I_OC` |

## 6. Sensado

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| R_shunt | Resistencia del shunt de corriente | 500 | µΩ | TFG | AC | SNS-01 · HW-02 | Con el AMC1302 (±50 mV lineales) da 100 A de fondo de escala y 128 A de recorte |
| P_sh_rat | Potencia nominal del shunt | 3 | W | P | AC | HW-02 | A `Ipk` disipa 1,8 W durante 2 s y a `Irms_cont` 12,5 mW: 3 W cubre el caso continuo con margen. Comprobar el pulso de 2 s contra la curva del fabricante |
| I_margin | Margen mínimo fondo de escala / Ipk (criterio) | 1,2 | – | P | AC | SNS-01 | El shunt de 500 µΩ con el AMC1302 da 100 A / 60 A = 1,67: cumple |
| I_OC | Umbral de sobrecorriente por hardware | 90 | A | P | AC | SAF-04 · HW-01 | 1,5 × `Ipk`, por debajo del recorte del AMC1302 (128 A). Es la protección que cubre la sobrecorriente de bobina, porque el DESAT dispara a cientos de amperios (`I_desat_max`). Necesita un comparador rápido sobre el shunt, no la cadena del AMC1302 (`Sa_td` = 3 µs) |
| f_clk_ds | Frecuencia de reloj de los moduladores ΔΣ | 20 | MHz | P | AC | SNS-05 · FW-01 | Por debajo de los 21 MHz máximos del AMC1306 a 5 V (`Sd_fmax`) |
| OSR | Relación de sobremuestreo del filtro sinc | 128 | – | P | TBD | SNS-05 · SNS-09 · FW-01 | A 20 MHz, sinc3 con OSR = 128 asienta en 19,2 µs y da 156 kHz de salida. **Con un periodo de PWM de 50 µs eso es mucha latencia para el lazo:** con OSR = 64 baja a 9,6 µs. Comparar con `t_meas_lat`; la elección depende del ancho de banda que pida EM-C-03. Solo aplica si `Sens_chain` = DeltaSigma |
| N_sinc | Orden del filtro sinc | 3 | – | P | AC | FW-01 | sinc3 es el habitual con moduladores de 2.º orden |
| N_adc | Resolución del ADC (opción amplificador aislado + ADC) | 12 | bit | P | TBD | SNS-05 · FW-01 | Solo aplica si `Sens_chain` = AmpAislado. Con 100 A de fondo de escala, 12 bits dan 24 mA de cuantificación. **[v0.4]** En esa vía el ADC puede ser el interno del controlador: lo que decide no es dónde está el ADC sino qué cruza la barrera (6.6.3 del documento de requisitos) |
| t_meas_lat | Latencia máxima admisible de la cadena de medida de corriente | 10 | µs | P | TBD | SNS-09 · EM-C-03 | **[v0.4]** PROVISIONAL. Un 20 % del periodo de PWM (50 µs a `fsw` = 20 kHz). Con sinc3 y `OSR` = 128 el asentamiento es 19,2 µs y **no cabe**; con `OSR` = 64 son 9,6 µs y sí. Por la vía del amplificador aislado son centenas de ns. El valor real lo fija EM-C-03 |
| V_meas_FS | Fondo de escala deseado de la medida de Vbus | 700 | V | P | AC | SNS-02 | Cubre `V_chop_on` (500 V) y `V_clamp_lim` (520 V) con margen, y el fallo de un módulo aislado (438 V) |
| V_sens_FS | Entrada lineal del sensor aislado de Vbus | 0,25 | V | HD | AC | SNS-02 · HW-02 | AMC1306x25: ±250 mV |
| R_sens_in | Impedancia de entrada del sensor de Vbus | 22 | kΩ | HD | AC | HW-02 | AMC1306x25: 22 kΩ diferencial |
| R_div_bot | Resistencia inferior del divisor de Vbus | 1 | kΩ | P | AC | SNS-02 | Con `V_meas_FS` / `V_sens_FS` = 2800:1 sale una rama superior de 2,799 MΩ. A 400 V el divisor consume 143 µA y 57 mW en total; 1 kΩ queda muy por debajo de los 22 kΩ de entrada del sensor, así que la carga es despreciable |
| V_res_rat | Tensión máxima de trabajo de cada resistencia del divisor | 200 | V | P | AC | HW-02 | Con 4 resistencias en serie en la rama superior, cada una ve 130 V en el peor caso de 520 V: cumple |
| P_res_rat | Potencia nominal de cada resistencia del divisor | 0,25 | W | P | AC | HW-02 | Cada una disipa 24 mW a 520 V, un 10 % de su nominal: cumple `k_res` con holgura |
| k_res | Factor de utilización de potencia de las resistencias (criterio) | 0,5 | – | P | AC | — | |
| V_OV | Umbral de sobretensión de bus por hardware | 450 | V | P | AC | SAF-01 · HW-01 | [v0.3] Antes 420 V (prueba), solo 20 V por encima de `Vbus_max` y expuesto a falsos disparos. 450 V deja 42 V sobre el bus más el rizado de 8 V, y queda por debajo de `V_chop_on` (500 V) |
| NTC_R25 | Resistencia de la NTC a 25 °C | 10 | kΩ | TFG | AC | LOAD-08 · HW-02 | GA10K4A1IA (TE) |
| NTC_beta | Constante β(25/85) de la NTC | 3598 | K | TE | AC | LOAD-08 | Página de producto TE; contrastar con la tabla R-T |
| R_ntc_pu | Resistencia de polarización de la NTC | 10 | kΩ | P | AC | SNS-03 | Igual a `NTC_R25`, que centra el divisor a 25 °C (2,5 V). En `T_coil_max` (110 °C) da 0,322 V: hay resolución suficiente en todo el rango útil |
| V_ntc_ref | Tensión de referencia del divisor de la NTC | 5 | V | P | AC | SNS-03 | Coherente con la alimentación de 5 V del lado HV del AMC1306 |

## 7. Refrigeración y entorno

Los cuatro primeros parámetros son el hueco de ME-C-02 y **no se pueden justificar con un cálculo**: siguen TBD.

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| T_amb | Temperatura ambiente máxima | 50 | °C | P | TBD | MEC-06 · ME-C-02 | PROVISIONAL. El TFG asumía ≥ 25 °C por competir en verano; 50 °C es una hipótesis conservadora |
| T_cool | Temperatura del refrigerante a la entrada | 50 | °C | P | TBD | ME-C-02 | PROVISIONAL. Depende del acumulador de PCM, que está fuera del alcance |
| Q_cool | Caudal de refrigerante | 2 | L/min | P | TBD | ME-C-02 | PROVISIONAL. |
| N_cool_ser | Placas en serie en el circuito de agua (la última es la peor) | 1 | – | P | TBD | ME-C-01 · ME-C-02 | PROVISIONAL. Con 10 placas en serie la última vería un salto de temperatura del agua muy distinto |
| Rth_wb | Resistencia térmica cara inferior de la PCB → agua, por MOSFET | 0,3 | K/W | P | TBD | PWR-06 · ME-C-01 | PROVISIONAL. Es el término dominante: con `Rthjc` = 0,22 K/W y 36 W por dispositivo durante el pico, la unión sube solo 8 K sobre la cápsula |
| t_TIM | Espesor del material de interfaz térmica | 0,5 | mm | P | AC | ME-C-01 | Espesor habitual de un gap pad que absorbe la tolerancia de planitud del waterblock |
| k_TIM | Conductividad del material de interfaz térmica | 3 | W/(m·K) | P | AC | ME-C-01 | Gama media de los gap pads comerciales |
| V_TIM_bd | Rigidez dieléctrica del material de interfaz (tensión de ruptura) | 4000 | V | P | AC | ISO-04 · ME-C-01 | El pad de drenador está en HV en los dos candidatos de MOSFET. 4000 V sobre 0,5 mm cubre `V_cont` con factor 6,7 |
| k_spread | Área efectiva bajo el TIM / área del pad (ensanchamiento) | 2 | – | P | TBD | — | PROVISIONAL. Depende del cobre de la cara inferior; confirmar con una simulación o una medida |
| A_pad | Área del pad de drenador del MOSFET | 70 | mm² | HD | AC | HW-02 | [v0.3] Antes 80 mm² referido al H²PAK-7. El PG-HSOF-8 (TOLL) tiene cuerpo de 9,9 × 11,68 mm y el pad de drenador ocupa del orden de 70 mm². Confirmar con el footprint del fabricante |
| d_via | Diámetro de taladro de las vías térmicas | 0,3 | mm | P | AC | PT-01 | Taladro estándar sin coste añadido en 6 capas |
| t_plat | Espesor del metalizado de las vías | 25 | µm | P | AC | PT-01 | Valor de clase 2 habitual; confirmar con PT-01 |
| N_via | Número de vías térmicas bajo cada MOSFET | 36 | – | P | AC | ME-C-01 | [v0.3] Antes 10. En 70 mm² caben unas 48 posiciones a paso de 1,2 mm; se dejan 36 (matriz 6 × 6) para reservar sitio al reparto de pasta y evitar el vaciado de soldadura |
| t_solder | Espesor de la soldadura bajo el pad | 0,1 | mm | P | AC | PT-02 | Espesor típico tras reflujo de un encapsulado sin patillas |
| k_solder | Conductividad de la soldadura | 50 | W/(m·K) | HD | AC | — | Orden de magnitud de aleaciones SAC |
| k_Cu | Conductividad del cobre | 385 | W/(m·K) | — | OK | — | Valor físico |
| k_FR4 | Conductividad del FR-4 en el eje z | 0,3 | W/(m·K) | — | AC | PT-01 | Orden de magnitud; confirmar con el laminado |

## 8. PCB: stackup, pistas y aislamiento

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| t_pcb | Espesor total de la PCB | 1,6 | mm | P | AC | MEC-03 · PT-01 | Espesor estándar compatible con 6 capas de 2 oz |
| oz_ext | Cobre en capas externas | 2 | oz | TFG | AC | MEC-03 · PT-01 | 1 oz ≈ 35 µm |
| oz_int | Cobre en capas internas | 2 | oz | TFG | AC | MEC-03 · PT-01 | MEC-03 indica 2 oz sin distinguir capas |
| dT_trace | Incremento de temperatura admisible en pistas (criterio) | 30 | °C | P | AC | — | |
| er_pcb | Permitividad relativa del dieléctrico | 4,5 | – | P | AC | PT-01 | FR-4 estándar a la frecuencia de la interfaz del PHY |
| h_ms | Dieléctrico entre capa externa y su plano de referencia (microstrip) | 0,2 | mm | P | AC | PT-01 | Coherente con un stackup simétrico de 6 capas y 1,6 mm |
| b_sl | Distancia entre planos de referencia de la stripline | 0,5 | mm | P | AC | PT-01 | Ídem |
| tol_Z | Tolerancia admisible de impedancia (criterio) | 10 | % | P | AC | PT-01 | Tolerancia habitual de fabricación; confirmar con el fabricante |
| Ins_type | Tipo de aislamiento HV–BT: «Básico» o «Reforzado» | Básico | – | P | TBD | ISO-05 · HW-04 | PROVISIONAL. Si se pide reforzado, comparar VIORM: STGAP3S 1,2 kV pico frente a ADuM4146 2,15 kV pico |
| PD_coat | Grado de contaminación bajo el coating (IEC 60664-3) | 1 | – | P | AC | ISO-02 · HW-04 |  |
| PD_bare | Grado de contaminación en superficies sin coating | 2 | – | P | AC | HW-04 | Grado habitual para un entorno cerrado no estanco |
| d_HV_LV | Separación mínima HV–BT con coating (regla de la competición) | 4 | mm | U | OK | ISO-02 |  |
| d_HV_HV | Separación mínima entre redes de HV | 2 | mm | TFG | AC | ISO-03 · HW-04 |  |
| d_WB | Separación mínima taladros del waterblock – conductores | 4 | mm | TFG | AC | ISO-04 · ME-C-01 |  |
| L_loop | Inductancia parásita objetivo del lazo de conmutación | 15 | nH | P | TBD | PWR-07 · HW-02 | Con 15 nH y 4 A/ns la sobreoscilación es de 60 V: 460 V de pico, el 71 % de los 650 V. Con 25 nH sube a 500 V, el 77 %. Es el parámetro que decide si hacen falta snubbers, y solo se sabrá al medir |

## 9. Alimentación auxiliar (BT)

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| V_BT_max | Tensión máxima de la batería de BT | 24 | V | U | OK | AUX-01 |  |
| V_BT_min | Tensión mínima de la batería de BT | 18 | V | P | TBD | AUX-03 · ME-I-02 | PROVISIONAL. Corresponde al final de descarga de un pack nominal de 24 V; lo tiene que confirmar ME-I-02 |
| P_BT_lim | Consumo máximo permitido por placa | 15 | W | P | TBD | AUX-03 · ME-I-02 | PROVISIONAL. Es un límite que impone ME-I-02, no el consumo estimado. Las cuatro fuentes de puerta solo piden 0,8 W en secundario, 1,1 W en primario con `G_eta` = 74 % |
| eta_BT | Rendimiento de la etapa de entrada BT | 85 | % | P | TBD | AUX-02 · HW-05 | PROVISIONAL. Depende de la topología que se elija en ME-I-02 |
| P_margin | Margen sobre el consumo total estimado (criterio) | 20 | % | P | AC | — |  |

## 10. Integridad de señal: presupuesto de tiempos (interfaz MII/RMII u otra síncrona)

**Todo este apartado depende de FW-06 y de FW-09** (protocolo, vía de implementación del esclavo, y PHY y controlador concretos). Los valores son provisionales de forma deliberada: solo sirven para comprobar que el motor de cálculos cierra el presupuesto, y hay que rehacerlos con las hojas de datos que se elijan.

> **[v0.4] Este apartado solo aplica si `ESC_impl` es `IPcore` o `ESCint`**, es decir, si el controlador habla MII o RMII con dos PHY externos. Si FW-09 lleva a `ESCext` con un LAN9252, los PHY van dentro del ESC, la interfaz con el controlador pasa a SPI/SQI y este presupuesto hay que sustituirlo por el del SPI.

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| f_bus_clk | Frecuencia de reloj de la interfaz controlador–PHY | 50 | MHz | P | TBD | COM-02 · FW-06 | RMII: 50 MHz; MII: 25 MHz. Se toma el caso más exigente. **[v0.4]** Los ESC integrados en microcontrolador usan MII, así que por esa vía serían 25 MHz |
| tco_max | Retardo de salida máximo del emisor (clock-to-out) | 10 | ns | P | TBD | FW-06 | PROVISIONAL. Hoja de datos del PHY / FPGA |
| tco_min | Retardo de salida mínimo del emisor | 2 | ns | P | TBD | FW-06 | PROVISIONAL. |
| t_su | Tiempo de setup del receptor | 4 | ns | P | TBD | FW-06 | PROVISIONAL. |
| t_h | Tiempo de hold del receptor | 2 | ns | P | TBD | FW-06 | PROVISIONAL. |
| t_jit | Jitter y otras incertidumbres del reloj | 0,5 | ns | P | TBD | FW-06 | PROVISIONAL. |
| dL_clk | Diferencia de longitud del reloj entre emisor y receptor | 10 | mm | P | TBD | — | PROVISIONAL |
| skew_pair | Desfase admisible dentro de un par diferencial | 5 | ps | P | TBD | COM-03 | PROVISIONAL. Criterio del fabricante del PHY o de los magnéticos |
| SI_if_datos | Interfaz de datos usada en el presupuesto de tiempos (clave de diseno.md) | datos_phy | – | P | TBD | COM-02 · FW-06 |  |
| SI_if_reloj | Interfaz de reloj usada en el presupuesto de tiempos (clave de diseno.md) | reloj_phy | – | P | TBD | COM-02 · FW-06 |  |
| SI_if_par | Par diferencial usado para la igualación de longitudes (clave de diseno.md) | mdi_in | – | P | TBD | COM-03 |  |

## 11. Plataforma de control y bus de campo (FW-09)

**[v0.4] Sección nueva.** Ninguno de estos parámetros es una decisión tomada: son los valores provisionales con los que trabaja el motor de cálculos mientras FW-09 no se cierre. Los criterios de aceptación están en 5.4 del documento de requisitos y el análisis de candidatos en 6.6.

| Nombre | Descripción | Valor | Unidad | Fuente | Estado | Requisito / pendiente | Nota |
|---|---|--:|---|---|---|---|---|
| Ctrl_plat | Plataforma de control: «FPGA» o «MCU» | FPGA | – | P | TBD | CTL-01 · FW-09 | PROVISIONAL. Hipótesis heredada de la v0.3, ya no es un dato de partida. Candidatos MCU con ESC integrado en 6.6.1: XMC4800/4300, RX72M, C2000 F28P65x y F2838x |
| ESC_impl | Implementación del esclavo EtherCAT: «IPcore», «ESCext» o «ESCint» | IPcore | – | P | TBD | COM-02 · FW-06 · FW-09 | PROVISIONAL. `ESCext` (LAN9252) y `ESCint` evitan la licencia del IP core de Beckhoff; las tres vías siguen necesitando el Slave Stack Code por vía ETG. Decide el valor de `N_phy_ext` y si aplica la sección 10 |
| N_ecat_port | Puertos EtherCAT montados por placa | 2 | – | P | OK | COM-03 · SYS-01 | El ESC trae 2 o 3 puertos dentro; lo que obliga a montar dos en las 10 placas es SYS-01, no el ESC. En la última de la línea la salida queda sin usar, salvo con `Ring_red` = Si |
| N_phy_ext | PHY Ethernet externos por placa | 2 | – | P | AC | COM-03 · COM-02 | 2 con `ESC_impl` = IPcore o ESCint; **0 con ESCext**, porque el LAN9252 los lleva dentro. Es el coste real de la topología, no los puertos |
| Ring_red | Redundancia en anillo del bus: «Si» o «No» | No | – | P | TBD | COM-07 · FW-06 | PROVISIONAL. Un esclavo sin BT abre la línea y deja fuera a los de aguas abajo. El anillo cuesta un cable de vuelta a un 2.º puerto de la VCU y hace el bus inmune a un corte en cualquier punto |
| Addr_mode | Identificación de posición: «AutoIncr», «EEPROM» o «Selector» | AutoIncr | – | P | TBD | COM-08 · CTL-06 · ME-I-06 | PROVISIONAL. El direccionamiento auto-incremental da la posición en la línea sin hardware adicional, si el orden del cableado es fijo y está documentado. Es la vía más barata con placa única |
| Sens_chain | Cadena de sensado de corriente: «DeltaSigma» o «AmpAislado» | DeltaSigma | – | P | TBD | SNS-05 · FW-01 · FW-09 | PROVISIONAL. Hipótesis de la opción A. La decisión no es ADC interno o externo, sino qué cruza la barrera (6.6.3). `DeltaSigma` exige un periférico SDFM/DFSDM en la plataforma y cuesta latencia (`t_meas_lat`); `AmpAislado` vale con cualquier ADC pero es más sensible al ruido de conmutación |
| N_ch_ds | Canales ΔΣ necesarios en el controlador | 1 | – | P | AC | SNS-07 · FW-01 | Solo la corriente necesita el camino rápido: `Vbus` y la NTC admiten amplificador aislado más ADC. Todos los candidatos de 6.6.1 tienen 4 o más canales, así que este parámetro no discrimina |
| t_trip_hw | Tiempo de reacción objetivo del disparo por hardware del controlador | 1 | µs | P | AC | CTL-08 · HW-01 | Criterio C3 de 5.4. No sustituye a la lógica cableada independiente de SAF-02: es la segunda capa, dentro del propio controlador |
