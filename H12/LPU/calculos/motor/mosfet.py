"""MOSFET: comparador de candidatos, pérdidas y temperatura de unión."""
from .unidades import fmt

NECESARIOS = ["ref", "VDS", "VGSmax", "VGSrec_on", "VGSrec_off", "Vth_min", "ID", "IDM", "Rthjc", "R25", "R25max",
              "Rhot", "Thot", "VSD", "Qg", "Ciss", "Crss", "Rgint", "Eon", "Eoff", "Vtest", "Itest", "tdon", "tr",
              "tdoff", "tf"]


def selecciona(ctx):
    """Valida los candidatos y fija ctx.mos_sel con el elegido en MOSFET_sel."""
    cands = []
    for mo in ctx.ent.mosfets:
        faltan = [k for k in NECESARIOS if k not in mo["datos"]]
        if faltan:
            mo["incompleto"] = faltan
        else:
            cands.append(mo)
    ctx.candidatos = cands
    sel = ctx.x.MOSFET_sel
    for mo in cands:
        if mo["ref"] == sel:
            ctx.mos_sel = mo["datos"]
            return
    refs = ", ".join(m["ref"] for m in cands) or "ninguno"
    raise ValueError(f"MOSFET_sel = «{sel}» no coincide con ningún candidato completo de componentes.md ({refs})")


def perdidas(ctx):
    x = ctx.x
    s = ctx.seccion(2, "MOSFET: comparador de candidatos",
                    "Pérdidas de primer orden: Eon/Eoff escaladas linealmente con V e I desde las condiciones de ensayo, y RDS(on) interpolada "
                    "linealmente con Tj entre 25 °C y la temperatura alta de la hoja de datos, escalada con la relación máx./típ. "
                    "El caso A supone Ipk en régimen permanente (conservador frente a t_pk). "
                    f"El MOSFET más cargado conduce una fracción D_worst = {fmt(x.D_worst)} del periodo.")
    ctx.mos_calc = {}
    for mo in ctx.candidatos:
        d = mo["datos"]
        c = {}
        c["Rtyp_as"] = d["R25"] + (d["Rhot"] - d["R25"]) * (x.Tj_assumed - 25) / (d["Thot"] - 25)
        c["Rmax_as"] = c["Rtyp_as"] * d["R25max"] / d["R25"]
        c["FOM"] = d["R25"] * 1e3 * d["Qg"] * 1e9
        for caso, I in (("pk", x.Ipk), ("c", x.Irms_cont)):
            esw = (d["Eon"] + d["Eoff"]) * (x.Vbus_max / d["Vtest"]) * (I / d["Itest"])
            c[f"Esw_{caso}"] = esw
            c[f"Pc_{caso}"] = I ** 2 * c["Rmax_as"] * x.D_worst
            c[f"Psw_{caso}"] = x.fsw * esw
            c[f"Pdt_{caso}"] = 2 * x.t_dead * x.fsw * d["VSD"] * I
            c[f"Pdev_{caso}"] = c[f"Pc_{caso}"] + c[f"Psw_{caso}"] + c[f"Pdt_{caso}"]
            c[f"Pbr_{caso}"] = 2 * I ** 2 * c["Rmax_as"] + 2 * x.fsw * esw + 4 * x.t_dead * x.fsw * d["VSD"] * I
        ctx.mos_calc[mo["ref"]] = c
    sel = ctx.mos_calc[x.MOSFET_sel]
    ctx.define("P_br_pk", sel["Pbr_pk"])
    ctx.define("P_br_c", sel["Pbr_c"])
    ctx.sec_mosfet = s


def temperatura(ctx):
    """Tj y tabla comparativa (necesita Rth_c2w y T_cool_out del bloque térmico)."""
    x, s = ctx.x, ctx.sec_mosfet
    for mo in ctx.candidatos:
        d, c = mo["datos"], ctx.mos_calc[mo["ref"]]
        for caso in ("pk", "c"):
            c[f"Tj_{caso}"] = x.T_cool_out + c[f"Pdev_{caso}"] * (d["Rthjc"] + x.Rth_c2w)
    cands = ctx.candidatos
    etq = {k: (e, u) for k, e, u, _ in ctx.ent.mosfet_filas}
    cab = ["Parámetro", "Unidad"] + [f"{m['ref']}{' (sel.)' if m['ref'] == x.MOSFET_sel else ''}" for m in cands]
    filas, reg = [], {}

    def fila(etiqueta, unidad, valores, clave=None, esc=1.0, dec=2, textos=None):
        celdas = []
        for m, v in zip(cands, valores):
            t = textos[cands.index(m)] if textos else fmt(v / esc if isinstance(v, (int, float)) else v, dec)
            celdas.append(t)
            if clave:
                reg[f"mosfet.{m['ref']}.{clave}"] = (v, t, unidad, f"{m['ref']}: {etiqueta}")
        filas.append([etiqueta, unidad] + celdas)

    def res_estado(v, lim, op, blando=False):
        ok = v <= lim if op == "<=" else v >= lim
        return "CUMPLE" if ok else ("**REVISAR**" if blando else "**NO CUMPLE**")

    filas.append(["**Datos principales**", ""] + [""] * len(cands))
    for k in ("pkg", "VDS", "R25", "Rthjc", "Qg", "Eon", "Eoff"):
        e, u = etq.get(k, (k, ""))
        fila(e, u, [None] * len(cands), textos=[m["textos"].get(k, "—").replace(f" {u}", "") for m in cands])
    D = lambda k: [ctx.mos_calc[m["ref"]][k] for m in cands]
    fila("RDS(on) típica a Tj_assumed", "mΩ", D("Rtyp_as"), "Rtyp_as", 1e-3)
    fila("RDS(on) máxima a Tj_assumed", "mΩ", D("Rmax_as"), "Rmax_as", 1e-3)
    fila("Figura de mérito RDS(on)·Qg (25 °C)", "mΩ·nC", D("FOM"), "FOM", 1, 0)
    for caso, titulo in (("pk", "**Caso A: Ipk**"), ("c", "**Caso B: Irms_cont**")):
        filas.append([titulo, ""] + [""] * len(cands))
        fila("Energía de conmutación escalada", "µJ", D(f"Esw_{caso}"), f"Esw_{caso}", 1e-6, 0)
        fila("Conducción del MOSFET más cargado", "W", D(f"Pc_{caso}"), f"Pc_{caso}", 1, 2)
        fila("Conmutación (toda la de la rama en un MOSFET)", "W", D(f"Psw_{caso}"), f"Psw_{caso}", 1, 2)
        fila("Diodo en los tiempos muertos", "W", D(f"Pdt_{caso}"), f"Pdt_{caso}", 1, 3)
        fila("Pérdidas totales del MOSFET más cargado", "W", D(f"Pdev_{caso}"), f"Pdev_{caso}", 1, 1)
        fila("Temperatura de unión", "°C", D(f"Tj_{caso}"), f"Tj_{caso}", 1, 1)
        fila("Tj ≤ Tj_lim", "–", [None] * len(cands),
             textos=[res_estado(v, x.Tj_lim, "<=") for v in D(f"Tj_{caso}")])
        if caso == "pk":
            fila("Tj ≤ Tj_assumed (coherencia de la RDS(on))", "–", [None] * len(cands),
                 textos=[res_estado(v, x.Tj_assumed, "<=", True) for v in D("Tj_pk")])
        fila("Pérdidas del puente completo (4 MOSFET)", "W", D(f"Pbr_{caso}"), f"Pbr_{caso}", 1, 1)
    filas.append(["**Márgenes**", ""] + [""] * len(cands))
    M = lambda k: [m["datos"][k] for m in cands]
    fila("VDS / V_cont", "–", [v / x.V_cont for v in M("VDS")], "VDS_rel", 1, 2)
    fila("VDS ≥ tensión del caso de fallo", "–", [None] * len(cands),
         textos=[res_estado(v, x.V_fault_max, ">=") for v in M("VDS")])
    fila("Vgs_on ≤ VGS recomendada", "–", [None] * len(cands),
         textos=[res_estado(x.Vgs_on, v, "<=", True) for v in M("VGSrec_on")])
    fila("Vgs_on ≤ VGS máxima absoluta", "–", [None] * len(cands),
         textos=[res_estado(x.Vgs_on, v, "<=") for v in M("VGSmax")])
    fila("Vgs_off ≥ VGS recomendada en OFF", "–", [None] * len(cands),
         textos=[res_estado(x.Vgs_off, v, ">=", True) for v in M("VGSrec_off")])
    fila("ID continua ≥ Ipk", "–", [None] * len(cands), textos=[res_estado(v, x.Ipk, ">=") for v in M("ID")])
    s.tabla(cab, filas, intro="Comparación de los candidatos completos de `componentes.md`. "
                              "Las temperaturas usan la cadena térmica y el agua del apartado 3.", registro=reg)
    incompletos = [f"{m['ref']} (faltan: {', '.join(m['incompleto'])})" for m in ctx.ent.mosfets if m.get("incompleto")]
    if incompletos:
        s.nota("Candidatos ignorados por datos incompletos: " + "; ".join(incompletos) + ".")
    sel = ctx.mos_calc[x.MOSFET_sel]
    ctx.define("Tj_pk_sel", sel["Tj_pk"])
    ctx.define("Tj_c_sel", sel["Tj_c"])
