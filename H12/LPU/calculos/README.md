# Cálculos de diseño: manual de uso

Los cálculos del Magnet Driver Abejorro (potencia, térmico, pistas, aislamiento, integridad de señal, sensado, gate driving y alimentación de BT) se definen con ficheros Markdown y se recalculan automáticamente. Sustituyen a la hoja Excel v0.1, con las mismas fórmulas y las mismas 75 comprobaciones.

## 1. Cómo funciona

```
H12/LPU/calculos/entradas/*.md ──► motor (Python) ──► H12/LPU/docs/calculos/informe.md          (informe general)
H12/LPU/calculos/normas/*.csv  ──┘                 ──► H12/LPU/docs/calculos/cambios/<fecha>.md  (informe de cambios)
                                                   ──► H12/LPU/docs/calculos/resultados.json     (estado para comparar)
```

Todas las rutas de este manual son relativas a `H12/LPU`, salvo la de la Action: su fichero está en `.github/workflows/calculos-lpu.yml`, en la raíz del repositorio de Hardware, porque GitHub solo ejecuta los workflows que están ahí. La Action solo se dispara con cambios de esta carpeta.

1. Se edita un fichero de `calculos/entradas/` y se sube el cambio a la rama principal.
2. La GitHub Action **Cálculos LPU (Magnet Driver Abejorro)**:
   - ejecuta las pruebas del motor;
   - recalcula todo;
   - compara con el último estado publicado (`docs/calculos/resultados.json`);
   - guarda en el repositorio el informe general y, si ha cambiado algo, un informe de cambios con fecha y commit;
   - deja los dos informes como **descarga** de la ejecución.
3. Si una entrada está mal escrita, la Action falla e indica el fichero, la línea y el problema. GitHub avisa por correo.

## 2. Qué fichero editar

| Fichero | Contenido | Cuándo se edita |
|---|---|---|
| `entradas/parametros.md` | Parámetros escalares con fuente, estado y requisito | Normalmente, es el único que se toca |
| `entradas/componentes.md` | Hojas de datos: MOSFET candidatos, driver, fuente aislada, sensores, componentes que cruzan la barrera | Al añadir o cambiar un componente |
| `entradas/diseno.md` | Pistas de potencia, interfaces de señal, distancias de aislamiento previstas y consumos de BT | Al avanzar el layout |
| `normas/*.csv` | Tablas de IPC-2221B, IEC 60664-1 y PoE | Al verificar las normas con el texto oficial |

### Reglas de formato

- En las tablas de parámetros se cambian «Valor», «Estado», «Fuente» y «Nota». **La columna «Nombre» (o «Clave») la usan las fórmulas**: no la cambie.
- Decimales con coma o con punto (`1,92` o `1.92`), sin separador de miles. Signo menos: `-` o `−`.
- «Estado»: `OK`, `AC` o `TBD`. Los TBD llevan un valor provisional y el informe los lista en el anexo C.
- Las unidades se convierten solas. Un valor en `%` se interpreta como fracción. Unidades admitidas:
  `V mV kV · A mA µA · Ω mΩ µΩ kΩ MΩ · H mH µH nH · F mF µF nF pF · C µC nC · J mJ µJ · W mW kW · s ms µs ns ps · Hz kHz MHz · m mm µm mm² · °C K K/W W/(m·K) · L/min · oz · bit · kV/µs · % · –`.
  Se puede escribir `u` en lugar de `µ` (por ejemplo, `uF`).
- Los parámetros de texto (unidad `–`) solo admiten los valores indicados en su descripción: `Encadenado`/`Estrella`, `Unipolar`/`Bipolar`, `Básico`/`Reforzado`, y la referencia de un MOSFET de `componentes.md` en `MOSFET_sel`.
- No use el carácter `|` dentro de una celda.
- La extensión recomendada *Markdown All in One* alinea las tablas con **Alt + Mayús + F**.

## 3. Ver el resultado antes de subir el cambio

Desde la raíz del repositorio:

```bash
python H12/LPU/calculos/calcular.py        # en Windows: py H12\LPU\calculos\calcular.py
```

En VS Code hay dos tareas preparadas («Cálculos: vista previa», que es la tarea de compilación por defecto, y «Cálculos: pruebas del motor»). Están en `H12/LPU/.vscode/tasks.json`, así que aparecen si abres **la carpeta `H12/LPU`** como espacio de trabajo (Archivo > Abrir carpeta) y se lanzan con Ctrl + Mayús + B.

Si prefieres abrir el repositorio entero, puedes usar el comando de arriba en el terminal integrado o copiar las dos tareas de [`extras/tareas-para-la-raiz.json`](../extras/tareas-para-la-raiz.json) en el `.vscode/tasks.json` de la raíz (ya llevan las rutas con el prefijo `H12/LPU`).

Genera en `salida/` (carpeta no versionada):

- `informe_<fecha>.md`: informe general, con la fecha, el commit y la instantánea de todos los parámetros (anexo B). Es el que conviene descargar para saber «en qué parámetros me he quedado»;
- `cambios_<fecha>.md`: cambios respecto al último informe publicado en `docs/calculos/`;
- `resultados.json`.

Si hay cambios sin confirmar en `calculos/`, el informe lo indica en «Versión de las entradas». Para ver los informes con formato, abra el fichero y pulse **Ctrl + Mayús + V**.

Las pruebas se lanzan con `python -m pytest -q -p no:cacheprovider H12/LPU/tests` (el `-p no:cacheprovider` evita que pytest cree una carpeta de caché en la raíz del repositorio de Hardware).

Requisitos: Python 3.9 o posterior. Para las pruebas: `pip install -r H12/LPU/requirements.txt`. En Windows, `tzdata` hace falta para que la fecha salga en hora de Madrid.

## 4. Dónde están los informes

| Qué | Dónde |
|---|---|
| Último informe general | `docs/calculos/informe.md` (en GitHub se lee con formato) |
| Últimos informes completos de cambios | `docs/calculos/cambios/README.md` (se conservan 3) |
| Historial de cambios de parámetros | `docs/calculos/historial_parametros.md` |
| Informes de una ejecución concreta | GitHub > Actions > Cálculos LPU > la ejecución > «Artifacts» > `informes-lpu-<fecha>` (se conservan 90 días) |
| Informe a fecha de hoy sin cambiar nada | GitHub > Actions > Cálculos LPU > **Run workflow** |
| Estado de cualquier fecha pasada | Historial de git de `docs/calculos/informe.md` |

El informe general solo se reescribe en el repositorio cuando cambia algo más que la fecha; el informe de cambios solo se crea cuando cambia alguna entrada o algún resultado.

## 5. Tareas habituales

### Añadir un MOSFET candidato

Rellene la columna «Candidato 2» (o añada «Candidato 4», «Candidato 5»…) de `componentes.md`. Todas las filas son obligatorias salvo «Fabricante», «Encapsulado», «VGS máxima absoluta (negativa)», «Tj máxima», «Coss», «Qrr» y «RG de ensayo»; un candidato incompleto se ignora y el informe dice qué le falta. Para usarlo en el resto de cálculos, ponga su referencia en `MOSFET_sel`.

### Añadir una pista, una interfaz o un consumo

Añada una fila a la tabla correspondiente de `diseno.md` con una «Clave» nueva (letras, números y `_`). La comprobación aparecerá en el informe como `PIS-<clave>`, `SI-<clave>`, etc.

### Añadir un parámetro o cambiar una fórmula

Las fórmulas están en `motor/`, un fichero por apartado (`potencia.py`, `termico.py`, etc.). Cada magnitud se escribe como:

```python
s.res("I_bus_pk", "Corriente media de bus a Ipk, Vbus_min", x.P_coil_pk / (x.eta_pwr * x.Vbus_min), "A", dec=2,
      expr="P_coil_pk/(eta_pwr·Vbus_min)")
```

- `x.<nombre>` da el valor en SI de un parámetro o de una magnitud ya calculada.
- Los valores se guardan en SI. `esc` y `dec` solo afectan a cómo se muestran.
- Las comprobaciones se escriben con `s.chk(id, etiqueta, valor, límite, "<=" o ">=", ...)`. Con `blando=True`, un fallo aparece como REVISAR.

Si añade un parámetro, añada también su fila en `parametros.md` **y en `tests/datos_v0.2/entradas/parametros.md`**, porque las pruebas usan esa copia fija. Si cambia una fórmula a propósito, las pruebas fallarán hasta que regenere los resultados de referencia:

```bash
python H12/LPU/tests/regenera_esperado.py
```

## 6. Ajustes de la Action

El fichero `.github/workflows/calculos-lpu.yml` (raíz del repositorio) tiene tres cosas que puede hacer falta tocar:

| Qué | Dónde | Cuándo |
|---|---|---|
| Ruta del proyecto | `env: PROY: H12/LPU` y los filtros `paths:` | Si la carpeta cambia de sitio o de nombre |
| Rama principal | `on: push: branches: [main]` | Si la rama principal no se llama `main` |
| `env: PUBLICAR: "si"` | Ponga `"no"` | Si la rama principal está protegida y la Action no puede escribir en el repositorio: entonces solo genera las descargas, y los informes se suben a mano desde la vista previa local |

Si el paso «Guardar los informes en el repositorio» falla con un error de permisos, hay dos opciones: activar «Read and write permissions» en Settings > Actions > General (lo decide quien administre el repositorio) o poner `PUBLICAR: "no"`.

Con pull requests, la Action calcula y deja los informes descargables en el propio pull request; los guarda en el repositorio al fusionar en la rama principal.

## 7. Pruebas

`tests/` contiene una copia fija de las entradas de la versión v0.2 y los resultados de referencia. Esos resultados se verificaron frente a la hoja Excel v0.1: 75 comprobaciones con los mismos valores y resultados. Las pruebas no dependen de los parámetros del proyecto, así que cambiar `parametros.md` nunca las rompe; solo detectan cambios no intencionados en las fórmulas.

## 8. Limitaciones

- Son cálculos de primer orden: L constante en cada punto de trabajo, escalado lineal de las pérdidas de conmutación, modelo térmico unidimensional en régimen permanente, fórmula de IPC-2221 para las pistas, fórmulas de IPC-2141A y AN-905 para la impedancia.
- Las tablas de normas vienen de fuentes secundarias: ver [`normas/README.md`](normas/README.md).
- El caso A del MOSFET supone Ipk en régimen permanente. Con picos de pocos segundos es muy conservador; hace falta la duración del pico (EM-C-01) y un modelo térmico transitorio.

## 9. Fuentes

| Dato | Fuente |
|---|---|
| Requisitos y valores de la sección 6 | `H12/LPU/docs/requisitos/01_requisitos_arquitectura_v0.2.md` |
| SCT012H90G3AG | [ST, hoja de datos](https://www.st.com/resource/en/datasheet/sct012h90g3ag.pdf) |
| ADuM4146 | [Analog Devices, hoja de datos](https://www.analog.com/media/en/technical-documentation/data-sheets/adum4146.pdf) |
| MGJ2D052005BSC | [Murata, hoja de datos MGJ2](https://docs.rs-online.com/4d1d/A700000007023131.pdf) |
| AMC1302 | [TI, hoja de datos](https://www.ti.com/lit/ds/symlink/amc1302.pdf) |
| AMC1306 | [TI, hoja de datos](https://www.ti.com/lit/ds/symlink/amc1306m05.pdf) |
| GA10K4A1IA | [TE, página de producto](https://www.te.com/en/product-GA10K4A1IA.html) |
| IPC-2221B, tabla 6-1 | [ProtoExpress](https://www.protoexpress.com/blog/ipc-2221-circuit-board-design/) y [Siemens EDA](https://blogs.sw.siemens.com/electronic-systems-design/2025/04/29/pcb-high-voltage-spacing-what-every-engineer-should-know/) |
| IEC 60664-1 | [TI SLUAAR5](https://www.ti.com/lit/pdf/sluaar5) y [Vishay](https://www.vishay.com/docs/28962/clearandcreepconsidcostsandspacefilmres.pdf) (parcial) |
| EtherCAT P | [Beckhoff](https://infosys.beckhoff.com/content/1033/ek1300/2268718219.html) |
