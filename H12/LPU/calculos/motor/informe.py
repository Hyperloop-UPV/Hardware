"""Informe general en Markdown y resultados en JSON."""
from . import VERSION_MOTOR
from .nucleo import CUMPLE, NO_CUMPLE, REVISAR
from .unidades import UNIDADES_TEXTO

AVISO = ("> **Aviso.** Cálculos de primer orden para orientar el diseño: no sustituyen a las calculadoras especializadas, "
         "a la simulación ni a las normas originales. Los parámetros en estado **TBD** tienen valores provisionales, y todo "
         "resultado que dependa de ellos es provisional.")


def celda(t):
    return str("" if t is None else t).replace("|", "\\|").replace("\n", " ")


def tabla_md(cab, filas):
    out = ["| " + " | ".join(celda(c) for c in cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    for f in filas:
        out.append("| " + " | ".join(celda(c) for c in f) + " |")
    return "\n".join(out)


def estado_md(e):
    return f"**{e}**" if e in (NO_CUMPLE, REVISAR) else e


def _grupo(items):
    con_chk = any(t == "chk" for t, _ in items)
    cab = ["Magnitud", "Valor", "Unidad"] + (["Límite", "Resultado"] if con_chk else []) + ["Expresión", "Nota"]
    filas = []
    for t, d in items:
        if t == "res":
            f = [d["etiqueta"], d["texto"], d["unidad"]] + (["", ""] if con_chk else [])
        else:
            f = [f"{d['etiqueta']} ({d['id']})", d["texto_valor"], d["unidad"], d["texto_limite"], estado_md(d["estado"])]
        f += [f"`{d['expr']}`" if d.get("expr") and not d["expr"].startswith("`") else d.get("expr", ""), d.get("nota", "")]
        filas.append(f)
    return tabla_md(cab, filas)


def seccion_md(s):
    out = [f"## {s.num}. {s.titulo}", ""]
    if s.intro:
        out += [s.intro, ""]
    grupo = []

    def vacia():
        if grupo:
            out.extend([_grupo(grupo), ""])
            grupo.clear()
    for it in s.items:
        if it[0] in ("res", "chk"):
            grupo.append(it)
            continue
        vacia()
        if it[0] == "sub":
            out += [f"### {it[1]}", ""]
            if it[2]:
                out += [it[2], ""]
        elif it[0] == "nota":
            out += [f"*{it[1]}*", ""]
        elif it[0] == "tabla":
            _, cab, filas, intro = it
            if intro:
                out += [intro, ""]
            out += [tabla_md(cab, filas), ""]
    vacia()
    return "\n".join(out)


def ancla(texto):
    import re
    t = texto.lower().strip()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def informe(ctx, meta):
    ent = ctx.ent
    rc = ctx.recuento()
    params = ent.params
    tbd = [p for p in params.values() if p.estado == "TBD"]
    ac = [p for p in params.values() if p.estado == "AC"]
    L = []
    L += ["# Magnet Driver Abejorro · Informe de cálculos de diseño", ""]
    L += [tabla_md(["Dato", "Valor"], [
        ["Fecha", meta["fecha_texto"]],
        ["Versión de las entradas", meta["version_texto"]],
        ["Motor de cálculo", VERSION_MOTOR],
        ["Documento base", "Requisitos y arquitectura, borrador v0.2 (`docs/requisitos`)"],
        ["MOSFET seleccionado", ctx.x.MOSFET_sel],
        ["Parámetros", f"{len(params)} en total: {len(tbd)} TBD, {len(ac)} a confirmar"],
    ]), ""]
    L += [AVISO, ""]
    L += ["## Índice", ""]
    L += ["- [Resumen](#resumen)"]
    for s in ctx.secciones:
        t = f"{s.num}. {s.titulo}"
        L.append(f"- [{t}](#{ancla(t)})")
    L += ["- [Anexo A. Todas las comprobaciones](#anexo-a-todas-las-comprobaciones)",
          "- [Anexo B. Parámetros usados](#anexo-b-parámetros-usados)",
          "- [Anexo C. Parámetros pendientes](#anexo-c-parámetros-pendientes)", ""]
    L += ["## Resumen", ""]
    L += [f"El cálculo incluye {len(ctx.comprobaciones)} comprobaciones. «REVISAR» indica un criterio blando o un dato que "
          "requiere un análisis más detallado.", ""]
    L += [tabla_md(["Resultado", "Número"], [[CUMPLE, rc.get(CUMPLE, 0)], [NO_CUMPLE, rc.get(NO_CUMPLE, 0)],
                                             [REVISAR, rc.get(REVISAR, 0)]]), ""]
    malas = [c for c in ctx.comprobaciones if c["estado"] in (NO_CUMPLE, REVISAR)]
    if malas:
        L += ["Comprobaciones que no cumplen o que hay que revisar:", ""]
        L += [tabla_md(["ID", "Comprobación", "Valor", "Límite", "Unidad", "Resultado", "Requisito", "Depende de"],
                       [[c["id"], c["etiqueta"], c["texto_valor"], c["texto_limite"], c["unidad"], estado_md(c["estado"]),
                         c["req"], c["deps"]] for c in malas]), ""]
    for s in ctx.secciones:
        L += [seccion_md(s), ""]
    L += ["## Anexo A. Todas las comprobaciones", ""]
    L += [tabla_md(["ID", "Comprobación", "Apartado", "Valor", "Límite", "Unidad", "Resultado", "Requisito", "Depende de", "Nota"],
                   [[c["id"], c["etiqueta"], c["seccion"], c["texto_valor"], c["texto_limite"], c["unidad"],
                     estado_md(c["estado"]), c["req"], c["deps"], c["nota"]] for c in ctx.comprobaciones]), ""]
    L += ["## Anexo B. Parámetros usados", "",
          "Instantánea de todos los parámetros escalares en el momento del cálculo (ficheros de `calculos/entradas`). "
          "Las tablas de MOSFET, pistas, interfaces, distancias y consumos se muestran en sus apartados.", ""]
    grupos = {}
    for p in params.values():
        grupos.setdefault((p.origen.split(":")[0], getattr(p, "seccion", "")), []).append(p)
    for (fich, sec), ps in grupos.items():
        L += [f"**`{fich}` · {sec}**", ""]
        L += [tabla_md(["Nombre", "Descripción", "Valor", "Unidad", "Fuente", "Estado", "Requisito / pendiente", "Nota"],
                       [[f"`{p.nombre}`", p.descripcion, p.texto, "" if p.unidad in UNIDADES_TEXTO else p.unidad,
                         p.fuente, estado_md(p.estado) if p.estado == "TBD" else p.estado, p.req, p.nota] for p in ps]), ""]
    L += ["## Anexo C. Parámetros pendientes", "",
          "Parámetros en estado TBD (valor provisional) y AC (a confirmar), con la cuestión que los resolverá.", ""]
    L += [tabla_md(["Estado", "Nombre", "Descripción", "Valor provisional", "Requisito / pendiente"],
                   [[p.estado, f"`{p.nombre}`", p.descripcion, f"{p.texto} {'' if p.unidad in UNIDADES_TEXTO else p.unidad}".strip(),
                     p.req] for p in tbd + ac]), ""]
    return "\n".join(L)


def resultados_json(ctx, meta):
    def limpio(v):
        return v if isinstance(v, (int, float, str)) or v is None else str(v)
    return {
        "generado": meta["fecha_iso"],
        "commit": meta.get("commit"),
        "version_motor": VERSION_MOTOR,
        "entradas": ctx.ent.instantanea(),
        "resultados": {k: {"valor": limpio(r["valor"]), "texto": r["texto"], "unidad": r["unidad"],
                           "etiqueta": r["etiqueta"], "seccion": r.get("seccion", "")}
                       for k, r in sorted(ctx.resultados.items())},
        "comprobaciones": {c["id"]: {"etiqueta": c["etiqueta"], "estado": c["estado"], "valor": c["texto_valor"],
                                     "limite": c["texto_limite"], "unidad": c["unidad"], "seccion": c["seccion"]}
                           for c in ctx.comprobaciones},
    }
