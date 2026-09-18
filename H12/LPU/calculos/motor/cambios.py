"""Informe de cambios entre dos ejecuciones (resultados.json)."""
from .informe import tabla_md, estado_md


def _ab(a, b):
    return b if a == b else f"{a} → {b}"


def _num(seccion):
    try:
        return int(seccion.split(".")[0])
    except ValueError:
        return 99


def _cambios_entradas(ant, act):
    ea, eb = ant.get("entradas", {}), act.get("entradas", {})
    filas = []
    for k in sorted(set(ea) | set(eb)):
        a, b = ea.get(k), eb.get(k)
        if a is None:
            filas.append([b["etiqueta"], "(no existía)", b["texto"], b.get("estado", ""), b.get("fuente", "")])
        elif b is None:
            filas.append([a["etiqueta"], a["texto"], "(eliminado)", "", ""])
        elif any(a.get(c) != b.get(c) for c in ("texto", "estado", "fuente")):
            dif = lambda c: (f"{a.get(c) or '—'} → {b.get(c) or '—'}" if a.get(c) != b.get(c) else (b.get(c) or ""))
            filas.append([f"{b['etiqueta']} (`{k.split('.', 1)[1]}`)", a["texto"], b["texto"], dif("estado"), dif("fuente")])
    return filas


def historial_parametros(ant, act, meta):
    """Devuelve una entrada del historial de parámetros y si contiene cambios."""
    if ant is None:
        filas = [[v["etiqueta"], "(no existía)", v["texto"], v.get("estado", ""), v.get("fuente", "")]
                 for _, v in sorted(act.get("entradas", {}).items())]
        titulo = f"## {meta['fecha_texto']} · Primera ejecución"
    else:
        filas = _cambios_entradas(ant, act)
        titulo = f"## {meta['fecha_texto']}"
    if not filas:
        return "", False
    return "\n".join([titulo, "", f"Versión: {meta['version_texto']}", "",
                       tabla_md(["Parámetro", "Antes", "Ahora", "Estado", "Fuente"], filas), ""]), True


def compara(ant, act, meta):
    """Devuelve (texto Markdown, hay_cambios)."""
    L = ["# Magnet Driver Abejorro · Informe de cambios en los cálculos", ""]
    if ant is None:
        L += [f"Primera ejecución ({meta['fecha_texto']}): no hay un estado anterior con el que comparar.", ""]
        return "\n".join(L), True
    L += [tabla_md(["Dato", "Estado anterior", "Estado actual"], [
        ["Fecha", ant.get("fecha_texto") or ant.get("generado", "—"), meta["fecha_texto"]],
        ["Versión de las entradas", f"commit `{(ant.get('commit') or '—')[:7]}`", meta["version_texto"]],
        ["Motor de cálculo", ant.get("version_motor", "—"), act.get("version_motor", "—")],
    ]), ""]
    hay = False

    # 1. Entradas
    filas = _cambios_entradas(ant, act)
    L += ["## 1. Entradas modificadas", ""]
    if filas:
        hay = True
        L += [tabla_md(["Entrada", "Antes", "Ahora", "Estado", "Fuente"], filas), ""]
    else:
        L += ["Ninguna.", ""]

    # 2. Comprobaciones
    ca, cb = ant.get("comprobaciones", {}), act.get("comprobaciones", {})
    cambio_estado, cambio_valor = [], []
    for k in list(cb) + [k for k in ca if k not in cb]:
        a, b = ca.get(k), cb.get(k)
        if a is None:
            cambio_estado.append([k, b["etiqueta"], "(nueva)", estado_md(b["estado"]), f"{b['valor']} {b['unidad']}".strip()])
        elif b is None:
            cambio_estado.append([k, a["etiqueta"], estado_md(a["estado"]), "(eliminada)", ""])
        elif a["estado"] != b["estado"]:
            cambio_estado.append([k, b["etiqueta"], estado_md(a["estado"]), estado_md(b["estado"]),
                                  f"{_ab(a['valor'], b['valor'])} {b['unidad']} (límite {_ab(a['limite'], b['limite'])})"])
        elif a["valor"] != b["valor"] or a["limite"] != b["limite"]:
            cambio_valor.append([k, b["etiqueta"], _ab(a["valor"], b["valor"]), _ab(a["limite"], b["limite"]),
                                 b["unidad"], estado_md(b["estado"])])
    L += ["## 2. Comprobaciones que cambian de resultado", ""]
    if cambio_estado:
        hay = True
        L += [tabla_md(["ID", "Comprobación", "Antes", "Ahora", "Valor"], cambio_estado), ""]
    else:
        L += ["Ninguna.", ""]
    L += ["## 3. Comprobaciones con el mismo resultado pero otros valores", ""]
    if cambio_valor:
        hay = True
        L += [tabla_md(["ID", "Comprobación", "Valor", "Límite", "Unidad", "Resultado"], cambio_valor), ""]
    else:
        L += ["Ninguna.", ""]

    # 4. Resultados
    ra, rb = ant.get("resultados", {}), act.get("resultados", {})
    filas = []
    for k in sorted(set(ra) | set(rb), key=lambda k: (_num((rb.get(k) or ra.get(k)).get("seccion", "")), k)):
        a, b = ra.get(k), rb.get(k)
        if a is None or b is None:
            r = b or a
            filas.append([r.get("seccion", ""), r["etiqueta"], "(no existía)" if a is None else a["texto"],
                          "(eliminado)" if b is None else b["texto"], r["unidad"], ""])
        elif a["texto"] != b["texto"]:
            var = ""
            if isinstance(a["valor"], (int, float)) and isinstance(b["valor"], (int, float)) and a["valor"]:
                var = f"{(b['valor'] - a['valor']) / abs(a['valor']) * 100:+.1f} %".replace(".", ",").replace("-", "−")
            filas.append([b.get("seccion", ""), b["etiqueta"], a["texto"], b["texto"], b["unidad"], var])
    L += ["## 4. Magnitudes calculadas que cambian", ""]
    if filas:
        hay = True
        L += [tabla_md(["Apartado", "Magnitud", "Antes", "Ahora", "Unidad", "Variación"], filas), ""]
    else:
        L += ["Ninguna.", ""]
    if not hay:
        L += ["**Sin cambios respecto al estado anterior.**", ""]
    return "\n".join(L), hay
