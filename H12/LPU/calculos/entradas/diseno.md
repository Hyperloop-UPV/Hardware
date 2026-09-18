# Tablas de diseño

Datos del layout y de las interfaces. Casi todos son **provisionales** hasta tener el diseño de la PCB. Se pueden añadir filas; la columna «Clave» identifica cada fila en el informe y debe ser única.

## 1. Pistas de potencia

«Corriente» admite un valor en amperios (`12,5`) o el nombre de una magnitud calculada: `I_in_first` (entrada de la primera placa a Ipk), `I_in_first_cont` (ídem en continuo), `I_bridge_rms` (DC-link ↔ puente), `Ipk`, `Irms_cont`. «Capa»: `Ext` o `Int`.

| Clave | Red | Corriente | Capa | Capas en paralelo | Ancho previsto (mm) | Longitud (mm) | Estado | Nota |
|---|---|---|---|--:|--:|--:|---|---|
| entrada_pk | Entrada HV (1.ª placa), Ipk | I_in_first | Ext | 2 | 35 | 60 | TBD | PROVISIONAL |
| entrada_cont | Entrada HV (1.ª placa), continuo | I_in_first_cont | Ext | 2 | 10 | 60 | TBD | PROVISIONAL |
| puente_rms | DC-link ↔ puente, eficaz a Ipk | I_bridge_rms | Ext | 2 | 15 | 20 | TBD | PROVISIONAL |
| bobina_pk | Puente → bobina, Ipk | Ipk | Ext | 2 | 15 | 80 | TBD | PROVISIONAL |
| bobina_cont | Puente → bobina, continuo | Irms_cont | Ext | 2 | 5 | 80 | TBD | PROVISIONAL |

## 2. Interfaces de señal

«Tipo»: `SE` (simple) o `Dif` (diferencial). «Capa»: `MS` (microstrip, capa externa) o `SL` (stripline, capa interna). La separación solo se usa en los pares diferenciales.

| Clave | Interfaz | Tipo | Capa | Z objetivo (Ω) | Ancho (mm) | Separación (mm) | tr (ns) | Longitud (mm) | Estado | Nota |
|---|---|---|---|--:|--:|--:|--:|--:|---|---|
| mdi_in | EtherCAT IN (MDI) | Dif | MS | 100 | 0,2 | 0,2 | 5 | 30 | TBD | 100 Ω diferencial en el MDI de Ethernet |
| mdi_out | EtherCAT OUT (MDI) | Dif | MS | 100 | 0,2 | 0,2 | 5 | 30 | TBD | |
| reloj_phy | Reloj FPGA–PHY | SE | SL | 50 | 0,12 |  | 5 | 60 | TBD | |
| datos_phy | Datos FPGA–PHY | SE | SL | 50 | 0,12 |  | 5 | 60 | TBD | |
| reloj_ds | Reloj de los moduladores ΔΣ | SE | SL | 50 | 0,12 |  | 5 | 80 | TBD | |
| datos_ds | Datos de los moduladores ΔΣ | SE | SL | 50 | 0,12 |  | 5 | 80 | TBD | |
| pwm | PWM a los drivers | SE | MS | 50 | 0,29 |  | 5 | 100 | TBD | |
| jtag_tck | JTAG TCK | SE | MS | 50 | 0,29 |  | 5 | 100 | TBD | |

## 3. Distancias de aislamiento previstas

Distancia mínima medida en el layout para cada caso. Las claves son fijas: `HVLV_coat`, `HVHV_coat`, `HVHV_int`, `HVHV_bare`, `WB`.

| Clave | Caso | Previsto (mm) | Estado | Nota |
|---|---|--:|---|---|
| HVLV_coat | HV–BT, superficie con coating | 5 | TBD | PROVISIONAL |
| HVHV_coat | HV–HV, superficie con coating | 2,5 | TBD | PROVISIONAL |
| HVHV_int | HV–HV, capas internas | 2,5 | TBD | PROVISIONAL |
| HVHV_bare | HV–HV, terminales sin recubrir (conectores, etc.) | 3,5 | TBD | PROVISIONAL |
| WB | Taladros del waterblock – cualquier conductor | 4 | TBD | PROVISIONAL |

## 4. Consumos de la alimentación auxiliar (BT)

«Corriente» admite un valor en mA o el nombre de una magnitud calculada (`I_iso_in`: entrada de cada fuente aislada de puerta). «Rendimiento» es el del convertidor que genera ese raíl.

| Clave | Consumidor | Raíl (V) | Corriente (mA) | Nº | Rendimiento (%) | Fuente | Estado | Nota |
|---|---|--:|---|--:|--:|---|---|---|
| fpga_core | FPGA MachXO5-NX: núcleo | 1 | 150 | 1 | 85 | — | TBD | PROVISIONAL (FW-02) |
| fpga_io | FPGA MachXO5-NX: bancos de E/S | 3,3 | 30 | 1 | 85 | — | TBD | PROVISIONAL (FW-02) |
| phy | PHY Ethernet | 3,3 | 60 | 2 | 85 | — | TBD | PROVISIONAL (FW-06); 2 puertos (COM-03) |
| osc | Oscilador | 3,3 | 10 | 1 | 85 | — | TBD | PROVISIONAL |
| eeprom | EEPROM SII | 3,3 | 1 | 1 | 85 | — | TBD | PROVISIONAL (COM-06) |
| ds_lv | Moduladores ΔΣ, lado BT (DVDD) | 3,3 | 6 | 3 | 85 | TI AMC1306 | AC | Máx. de la hoja de datos; rendimiento provisional |
| ds_hv | Moduladores ΔΣ, lado HV (AVDD) vía fuente aislada | 5 | 9,8 | 3 | 70 | TI AMC1306 | AC | Máx. de la hoja de datos; rendimiento de la fuente aislada PROVISIONAL |
| drv_lv | Gate drivers ADuM4146, lado BT (VDD1) | 5 | 2,17 | 4 | 85 | ADI ADuM4146 | AC | Máx. de la hoja de datos; rendimiento provisional |
| iso_gd | Fuentes aisladas de puerta (entrada a 5 V) | 5 | I_iso_in | 4 | 85 | Cálculo | AC | Corriente calculada en el apartado de gate driving |
| logica | Lógica cableada y comparadores | 3,3 | 10 | 1 | 85 | — | TBD | PROVISIONAL (HW-01) |
| leds | LEDs | 3,3 | 2 | 4 | 85 | — | TBD | PROVISIONAL |
