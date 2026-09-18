# Magnet Driver Abejorro (H12/LPU)

Convertidor DC/DC en puente en H con control local en FPGA para los electroimanes de levitación y guiado del prototipo H12. Primera generación con FPGA; sustituye a la LPU anterior.

Todo el proyecto vive en esta carpeta del repositorio de Hardware, salvo el fichero de la GitHub Action, que tiene que estar en la raíz del repositorio (`.github/workflows/calculos-lpu.yml`) porque GitHub solo ejecuta los workflows que están ahí.

## Estructura

| Carpeta | Contenido |
|---|---|
| `docs/requisitos/` | Documento de requisitos y arquitectura (borrador v0.2) |
| `docs/calculos/` | Informe de cálculos de diseño **generado automáticamente**, sus resultados en JSON y el historial de informes de cambios. No se edita a mano |
| `calculos/entradas/` | **Entradas de los cálculos en Markdown**: parámetros, datos de componentes y tablas de diseño |
| `calculos/normas/` | Tablas de normas (IPC-2221B, IEC 60664-1, PoE) en CSV |
| `calculos/motor/` | Motor de cálculo en Python (fórmulas) |
| `tests/` | Pruebas del motor con un juego de entradas fijo |
| `salida/` | Vista previa local de los informes (no se sube al repositorio) |

## Cálculos de diseño en dos líneas

1. Edita `calculos/entradas/parametros.md` (o los otros ficheros de entradas) y sube el cambio.
2. La Action recalcula, actualiza `docs/calculos/informe.md`, añade un informe de cambios en `docs/calculos/cambios/` y deja ambos como descarga de la ejecución.

Manual completo: [`calculos/README.md`](calculos/README.md). Último informe: [`docs/calculos/informe.md`](docs/calculos/informe.md).
