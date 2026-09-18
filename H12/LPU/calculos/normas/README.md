# Tablas de normas

Datos de normas usados por los cálculos, en CSV con punto decimal.

| Fichero | Contenido | Fuente y nivel de verificación |
|---|---|---|
| `ipc2221b_tabla6-1.csv` | IPC-2221B, tabla 6-1: separación mínima entre conductores (mm). B1 = capas internas; B2 = externas sin recubrir ≤ 3050 m; B3 = externas sin recubrir > 3050 m; B4 = externas con recubrimiento permanente de polímero; A5 = externas con conformal coating sobre el conjunto; A6 = terminales sin recubrir; A7 = terminales con conformal coating. La última fila es el incremento por voltio por encima de 500 V | Reproducción de ProtoExpress (Sierra Circuits); B1 por voltio = 0,0025 mm/V según el ejemplo de Siemens EDA (600 V → 0,50 mm). Fuente secundaria: contrastar con la norma (ya existe IPC-2221C, 2025) |
| `iec60664-1_fuga_pcb.csv` | IEC 60664-1: líneas de fuga en material de circuito impreso, aislamiento funcional/básico (mm) | Verificados en fuentes secundarias: 400 V/PD2 (TI SLUAAR5) y 1000 V (Vishay). El resto, a contrastar con la norma |
| `poe.csv` | Potencia disponible en el equipo alimentado por tipo de PoE | IEEE 802.3af/at/bt; valores no consultados en la norma durante la preparación |
