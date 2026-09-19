"""Lectura de las tablas Markdown y CSV de entrada."""
import csv
import os
import re

from .unidades import factor, normaliza_unidad, parse_numero, UNIDADES_TEXTO


class ErrorEntradas(Exception):
    def __init__(self, errores):
        self.errores = errores
        super().__init__("\n".join(errores))


class Param:
    def __init__(self, nombre, descripcion, texto, unidad, fuente, estado, req, nota, origen):
        self.nombre = nombre
        self.descripcion = descripcion
        self.texto = texto
        self.unidad = unidad
        self.fuente = fuente
        self.estado = estado
        self.req = req
        self.nota = nota
        self.origen = origen
        self.valor = None


def tablas_markdown(ruta):
    """Devuelve una lista de (seccion, linea, cabeceras, filas[(linea, celdas)])."""
    tablas = []
    seccion = ""
    with open(ruta, encoding="utf-8") as f:
        lineas = f.read().splitlines()
    i = 0
    while i < len(lineas):
        ln = lineas[i].strip()
        if ln.startswith("#"):
            seccion = ln.lstrip("#").strip()
        if ln.startswith("|") and i + 1 < len(lineas) and re.match(r"^\|\s*:?-{2,}", lineas[i + 1].strip()):
            cab = [c.strip() for c in ln.strip("|").split("|")]
            filas = []
            j = i + 2
            while j < len(lineas) and lineas[j].strip().startswith("|"):
                celdas = [c.strip() for c in lineas[j].strip().strip("|").split("|")]
                if len(celdas) < len(cab):
                    celdas += [""] * (len(cab) - len(celdas))
                filas.append((j + 1, celdas[: len(cab)] if len(celdas) >= len(cab) else celdas))
                if len(celdas) > len(cab):
                    filas[-1] = (j + 1, celdas)
                j += 1
            tablas.append((seccion, i + 1, cab, filas))
            i = j
            continue
        i += 1
    return tablas


def separa_unidad(cabecera):
    m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", cabecera)
    if m:
        return m.group(1).strip(), normaliza_unidad(m.group(2))
    return cabecera.strip(), None


class Entradas:
    def __init__(self, dir_entradas, dir_normas):
        self.dir_entradas = dir_entradas
        self.dir_normas = dir_normas
        self.params = {}
        self.mosfet_filas = []      # (clave, etiqueta, unidad, nota)
        self.mosfets = []           # dict: col, datos{clave: valor SI o texto}, textos{clave: texto con unidad}
        self.tablas = {}            # nombre -> lista de filas (dict)
        self.errores = []
        self.ficheros = []
        for nombre in ("parametros.md", "componentes.md", "diseno.md"):
            ruta = os.path.join(dir_entradas, nombre)
            if not os.path.exists(ruta):
                self.errores.append(f"No existe el fichero de entradas {ruta}")
                continue
            self.ficheros.append(ruta)
            self._lee_md(ruta, nombre)
        self._lee_normas()
        if self.errores:
            raise ErrorEntradas(self.errores)

    # ------------------------------------------------------------------ Markdown
    def _err(self, origen, msg):
        self.errores.append(f"{origen}: {msg}")

    def _lee_md(self, ruta, nombre):
        for seccion, linea, cab, filas in tablas_markdown(ruta):
            if cab[:4] == ["Nombre", "Descripción", "Valor", "Unidad"]:
                self._tabla_escalar(nombre, seccion, cab, filas)
            elif cab[:3] == ["Nombre", "Descripción", "Unidad"] and any(c.startswith("Candidato") for c in cab):
                self._tabla_candidatos(nombre, seccion, cab, filas)
            elif "Clave" in cab and "Parámetro" in cab and any(c.startswith("Candidato") for c in cab):
                self._tabla_mosfet(nombre, cab, filas)
            elif cab and cab[0] == "Clave":
                tipo = None
                for marca, t in (("Red", "pistas"), ("Interfaz", "interfaces"), ("Caso", "distancias"),
                                 ("Consumidor", "consumos"), ("Componente", "barrera")):
                    if marca in cab:
                        tipo = t
                if tipo is None:
                    self._err(f"{nombre}:{linea}", "tabla con columna «Clave» no reconocida")
                    continue
                self._tabla_generica(nombre, tipo, cab, filas)
            else:
                self._err(f"{nombre}:{linea}", "tabla no reconocida (revise las cabeceras)")

    def _tabla_escalar(self, fichero, seccion, cab, filas):
        idx = {c: i for i, c in enumerate(cab)}
        for ln, c in filas:
            origen = f"{fichero}:{ln}"
            if len(c) != len(cab):
                self._err(origen, f"la fila tiene {len(c)} columnas y la tabla {len(cab)} (¿hay un «|» dentro de una celda?)")
                continue
            g = lambda k: c[idx[k]] if k in idx else ""
            nombre = g("Nombre")
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", nombre):
                self._err(origen, f"nombre de parámetro no válido: «{nombre}»")
                continue
            if nombre in self.params:
                self._err(origen, f"el parámetro {nombre} está repetido (ya en {self.params[nombre].origen})")
                continue
            unidad = normaliza_unidad(g("Unidad"))
            p = Param(nombre, g("Descripción"), g("Valor"), unidad, g("Fuente"), g("Estado"),
                      g("Requisito / pendiente"), g("Nota"), origen)
            p.seccion = seccion
            if p.estado not in ("OK", "AC", "TBD"):
                self._err(origen, f"{nombre}: estado «{p.estado}» no válido (OK, AC o TBD)")
            num = parse_numero(p.texto)
            if num is None:
                if unidad in UNIDADES_TEXTO and p.texto:
                    p.valor = p.texto
                else:
                    self._err(origen, f"{nombre}: valor «{p.texto}» no es un número")
                    continue
            else:
                try:
                    p.valor = num * factor(unidad)
                except KeyError:
                    self._err(origen, f"{nombre}: unidad «{unidad}» no reconocida")
                    continue
            self.params[nombre] = p

    def _tabla_candidatos(self, fichero, seccion, cab, filas):
        idx = {c: i for i, c in enumerate(cab)}
        candidatos = [i for i, c in enumerate(cab) if c.startswith("Candidato")]
        for ln, c in filas:
            origen = f"{fichero}:{ln}"
            if len(c) != len(cab):
                self._err(origen, f"la fila tiene {len(c)} columnas y la tabla {len(cab)}")
                continue
            nombre = c[idx["Nombre"]]
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", nombre):
                self._err(origen, f"nombre de parámetro no válido: «{nombre}»")
                continue
            if nombre in self.params:
                self._err(origen, f"el parámetro {nombre} está repetido (ya en {self.params[nombre].origen})")
                continue
            valor = next((c[i] for i in candidatos if c[i]), "")
            unidad = normaliza_unidad(c[idx["Unidad"]])
            p = Param(nombre, c[idx["Descripción"]], valor, unidad,
                      c[idx["Fuente"]] if "Fuente" in idx else "",
                      c[idx["Estado"]] if "Estado" in idx else "",
                      c[idx["Requisito / pendiente"]] if "Requisito / pendiente" in idx else "",
                      c[idx["Nota"]] if "Nota" in idx else "", origen)
            p.seccion = seccion
            if p.estado not in ("OK", "AC", "TBD"):
                self._err(origen, f"{nombre}: estado «{p.estado}» no válido (OK, AC o TBD)")
            num = parse_numero(p.texto)
            if num is None:
                if unidad in UNIDADES_TEXTO and p.texto:
                    p.valor = p.texto
                else:
                    self._err(origen, f"{nombre}: valor «{p.texto}» no es un número")
                    continue
            else:
                try:
                    p.valor = num * factor(unidad)
                except KeyError:
                    self._err(origen, f"{nombre}: unidad «{unidad}» no reconocida")
                    continue
            self.params[nombre] = p

    def _tabla_mosfet(self, fichero, cab, filas):
        i_cl, i_par, i_un = cab.index("Clave"), cab.index("Parámetro"), cab.index("Unidad")
        cols = [i for i, c in enumerate(cab) if c.startswith("Candidato")]
        i_nota = len(cab) - 1 if not cab[-1].startswith("Candidato") else None
        datos = {i: {} for i in cols}
        textos = {i: {} for i in cols}
        for ln, c in filas:
            origen = f"{fichero}:{ln}"
            if len(c) != len(cab):
                self._err(origen, "número de columnas incorrecto en la tabla de MOSFET")
                continue
            clave, unidad = c[i_cl], normaliza_unidad(c[i_un])
            self.mosfet_filas.append((clave, c[i_par], unidad, c[i_nota] if i_nota is not None else ""))
            for i in cols:
                t = c[i]
                if t == "":
                    continue
                num = parse_numero(t)
                if num is None:
                    if unidad in UNIDADES_TEXTO:
                        datos[i][clave] = t
                    else:
                        self._err(origen, f"{cab[i]}, {clave}: «{t}» no es un número")
                        continue
                else:
                    try:
                        datos[i][clave] = num * factor(unidad)
                    except KeyError:
                        self._err(origen, f"{clave}: unidad «{unidad}» no reconocida")
                        continue
                textos[i][clave] = f"{t} {unidad}".strip() if unidad not in UNIDADES_TEXTO else t
        for i in cols:
            if not datos[i]:
                continue
            ref = datos[i].get("ref")
            if not ref:
                self._err(fichero, f"{cab[i]} tiene datos pero no tiene «Referencia»")
                continue
            if any(m["ref"] == ref for m in self.mosfets):
                self._err(fichero, f"la referencia {ref} está repetida en los candidatos")
            self.mosfets.append({"col": cab[i], "ref": ref, "datos": datos[i], "textos": textos[i]})

    def _tabla_generica(self, fichero, tipo, cab, filas):
        lista = self.tablas.setdefault(tipo, [])
        claves = {f["Clave"] for f in lista}
        for ln, c in filas:
            origen = f"{fichero}:{ln}"
            if len(c) != len(cab):
                self._err(origen, f"la fila tiene {len(c)} columnas y la tabla {len(cab)}")
                continue
            fila = {"_origen": origen, "_textos": {}}
            for h, t in zip(cab, c):
                nombre, unidad = separa_unidad(h)
                fila["_textos"][h] = t
                if unidad is None:
                    fila[nombre] = t
                    continue
                num = parse_numero(t)
                if num is None:
                    fila[nombre] = t if t else None  # puede ser el nombre de una magnitud
                else:
                    try:
                        fila[nombre] = num * factor(unidad)
                    except KeyError:
                        self._err(origen, f"unidad «{unidad}» no reconocida en la cabecera «{h}»")
            if not re.match(r"^[A-Za-z0-9_]+$", fila["Clave"] or ""):
                self._err(origen, f"clave no válida: «{fila['Clave']}» (solo letras, números y _)")
                continue
            if fila["Clave"] in claves:
                self._err(origen, f"la clave {fila['Clave']} está repetida")
                continue
            claves.add(fila["Clave"])
            lista.append(fila)

    # ------------------------------------------------------------------ CSV
    def _lee_normas(self):
        def lee(nombre):
            ruta = os.path.join(self.dir_normas, nombre)
            if not os.path.exists(ruta):
                self.errores.append(f"No existe {ruta}")
                return []
            with open(ruta, encoding="utf-8", newline="") as f:
                return list(csv.DictReader(f))
        ipc = lee("ipc2221b_tabla6-1.csv")
        self.ipc_cols = ["B1", "B2", "B3", "B4", "A5", "A6", "A7"]
        self.ipc_filas, self.ipc_por_voltio = [], None
        for f in ipc:
            if f["desde_V"] == "por_voltio":
                self.ipc_por_voltio = {k: float(f[k]) for k in self.ipc_cols}
            else:
                self.ipc_filas.append({"desde": float(f["desde_V"]), "hasta": float(f["hasta_V"]),
                                       **{k: float(f[k]) for k in self.ipc_cols}})
        self.iec_filas = [{"V": float(f["tension_V"]), "PD1": float(f["PD1_mm"]), "PD2": float(f["PD2_mm"]),
                           "verif": f["verificacion"]} for f in lee("iec60664-1_fuga_pcb.csv")]
        self.poe = [(f["norma"], float(f["potencia_PD_W"])) for f in lee("poe.csv")]

    # ------------------------------------------------------------------ instantánea
    def instantanea(self):
        """Texto de cada entrada, para detectar cambios."""
        s = {}
        for n, p in self.params.items():
            s[f"param.{n}"] = {"texto": f"{p.texto} {p.unidad}".strip() if p.unidad not in UNIDADES_TEXTO else p.texto,
                               "estado": p.estado, "fuente": p.fuente, "etiqueta": p.descripcion}
        etiquetas = {k: e for k, e, _, _ in self.mosfet_filas}
        for m in self.mosfets:
            for k, t in m["textos"].items():
                s[f"mosfet.{m['ref']}.{k}"] = {"texto": t, "estado": "", "etiqueta": f"{m['ref']}: {etiquetas.get(k, k)}"}
        for tipo, filas in self.tablas.items():
            for f in filas:
                for h, t in f["_textos"].items():
                    if h == "Clave":
                        continue
                    s[f"{tipo}.{f['Clave']}.{h}"] = {"texto": t, "estado": f.get("Estado", "") or "",
                                                     "etiqueta": f"{tipo} {f['Clave']}: {h}"}
        return s
