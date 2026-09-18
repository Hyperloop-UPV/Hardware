"""Aislamiento: IPC-2221B, IEC 60664-1 y reglas del proyecto."""
from .unidades import fmt

CLAVES = {
    "HVLV_coat": "HV–BT, superficie con coating",
    "HVHV_coat": "HV–HV, superficie con coating",
    "HVHV_int": "HV–HV, capas internas",
    "HVHV_bare": "HV–HV, terminales sin recubrir",
    "WB": "Taladros del waterblock – conductores",
}


def ipc(ent, V, col):
    """Separación IPC-2221B (mm) para la tensión V."""
    if V <= 500:
        fila = [f for f in ent.ipc_filas if f["desde"] <= V][-1]
        return fila[col]
    base = [f for f in ent.ipc_filas if f["hasta"] == 500][0][col]
    return base + (V - 500) * ent.ipc_por_voltio[col]


def iec(ent, V, pd, superior=False):
    """Línea de fuga IEC 60664-1 en PCB (mm), interpolada o de la fila superior. None si V > tabla."""
    col = f"PD{int(pd)}"
    filas = ent.iec_filas
    if V > filas[-1]["V"]:
        return None
    if V <= filas[0]["V"]:
        return filas[0][col]
    for a, b in zip(filas, filas[1:]):
        if a["V"] <= V <= b["V"]:
            if V == a["V"]:
                return a[col]
            if superior:
                return b[col]
            return a[col] + (V - a["V"]) * (b[col] - a[col]) / (b["V"] - a["V"])
    return None


def calcula(ctx):
    x, ent = ctx.x, ctx.ent
    s = ctx.seccion(5, "Aislamiento",
                    "Reglas del proyecto (ISO-02 a ISO-04) frente a IPC-2221B (tabla 6-1) e IEC 60664-1 (líneas de fuga en circuito impreso). "
                    "Las tablas de las normas proceden de fuentes secundarias (`calculos/normas/README.md`) y deben contrastarse con el texto oficial.")
    if x.Ins_type not in ("Básico", "Reforzado"):
        raise ValueError("Ins_type debe ser «Básico» o «Reforzado»")
    if int(x.PD_coat) not in (1, 2) or int(x.PD_bare) not in (1, 2):
        raise ValueError("PD_coat y PD_bare deben ser 1 o 2 (la tabla incluida solo cubre PD1 y PD2)")
    tensiones = [("V_cont", x.V_cont), ("V_fault_max", x.V_fault_max)]
    filas, reg = [], {}
    for nom, V in tensiones:
        vals = [ipc(ent, V, c) for c in ent.ipc_cols]
        filas.append([f"{nom} = {fmt(V, 0)} V"] + [fmt(v, 2) for v in vals])
        for c, v in zip(ent.ipc_cols, vals):
            reg[f"ipc.{nom}.{c}"] = (v, fmt(v, 2), "mm", f"IPC-2221B {c} a {nom}")
    s.tabla(["Tensión"] + ent.ipc_cols, filas, registro=reg,
            intro="IPC-2221B, separación mínima entre conductores (mm). B1: internas · B2/B3: externas sin recubrir (≤/> 3050 m) · "
                  "B4: recubrimiento permanente · A5: conformal coating · A6/A7: terminales sin/con coating.")
    k_ins = 2.0 if x.Ins_type == "Reforzado" else 1.0
    filas, reg = [], {}
    for nom, V in tensiones:
        for pd in (1, 2):
            vi, vs = iec(ent, V, pd), iec(ent, V, pd, True)
            filas.append([f"{nom} = {fmt(V, 0)} V", f"PD{pd}", fmt(vi, 2) if vi is not None else "fuera de tabla",
                          fmt(vs, 2) if vs is not None else "fuera de tabla"])
            reg[f"iec.{nom}.PD{pd}"] = (vi, fmt(vi, 2), "mm", f"IEC 60664-1 PD{pd} a {nom}")
    s.tabla(["Tensión", "Grado de contaminación", "Interpolada (mm)", "Fila superior (mm)"], filas, registro=reg,
            intro=f"IEC 60664-1, aislamiento funcional/básico en circuito impreso. Tipo de aislamiento HV–BT: **{x.Ins_type}** "
                  f"(factor {fmt(k_ins, 0)}). PD1 aplica bajo un recubrimiento conforme a IEC 60664-3.")
    V = x.V_cont
    mm = lambda v: None if v is None else v * 1e-3
    iec_c, iec_b = iec(ent, V, x.PD_coat), iec(ent, V, x.PD_bare)
    req = {
        "HVLV_coat": (x.d_HV_LV, mm(ipc(ent, V, "A5")), mm(None if iec_c is None else k_ins * iec_c),
                      "IPC A5 · IEC PD_coat × factor de aislamiento", "ISO-02 · ISO-05"),
        "HVHV_coat": (x.d_HV_HV, mm(ipc(ent, V, "A5")), mm(iec_c), "IPC A5 · IEC PD_coat, básico", "ISO-03"),
        "HVHV_int": (x.d_HV_HV, mm(ipc(ent, V, "B1")), None, "IPC B1 (la línea de fuga no aplica en capas internas)", "ISO-03"),
        "HVHV_bare": (x.d_HV_HV, mm(ipc(ent, V, "A6")), mm(iec_b), "IPC A6 · IEC PD_bare, básico", "ISO-03"),
        "WB": (x.d_WB, None, None, "Regla del proyecto", "ISO-04"),
    }
    dist = {f["Clave"]: f for f in ent.tablas.get("distancias", [])}
    for clave in dist:
        if clave not in CLAVES:
            raise ValueError(f"{dist[clave]['_origen']}: clave «{clave}» no reconocida ({', '.join(CLAVES)})")
    filas, reg, pend = [], {}, []
    for clave, (regla, v_ipc, v_iec, crit, rq) in req.items():
        nec = max(v for v in (regla, v_ipc, v_iec) if v is not None)
        f = dist.get(clave)
        prev = ctx.resuelve(f["Previsto"], 1e-3, f["_origen"]) if f else None
        ft = lambda v: fmt(None if v is None else v * 1e3, 2)
        filas.append([CLAVES[clave], ft(regla), ft(v_ipc), ft(v_iec), ft(nec), crit])
        reg[f"aisl.{clave}.requerido"] = (nec, ft(nec), "mm", f"Distancia requerida: {CLAVES[clave]}")
        pend.append((clave, prev, nec, rq, (f.get("Estado") or "") if f else ""))
        if clave == "HVLV_coat":
            ctx.define("d_req_HVLV", nec)
    s.tabla(["Caso", "Regla del proyecto (mm)", "IPC-2221B (mm)", "IEC 60664-1 (mm)", "Requerido (mm)", "Criterio"],
            filas, registro=reg,
            intro=f"Distancias requeridas a V_cont = {fmt(V, 0)} V: el máximo entre la regla del proyecto y las normas aplicables.")
    for clave, prev, nec, rq, est in pend:
        s.chk(f"AIS-{clave}", f"Distancia prevista: {CLAVES[clave]}", prev, nec, ">=", "mm", 1e-3, 2, req=rq,
              deps="HW-04, PT-01 (layout pendiente)", nota=f"Valor previsto en `diseno.md` (estado {est})" if est else "")
    s.sub("5.1 Componentes que cruzan la barrera HV–BT",
          "La línea de fuga del encapsulado debe ser ≥ la requerida HV–BT; la tensión de trabajo de la barrera, ≥ V_cont.")
    for f in ent.tablas.get("barrera", []):
        o = f["_origen"]
        fuga = ctx.resuelve(f["Fuga"], 1e-3, o)
        vt = ctx.resuelve(f["Tensión de trabajo"], 1.0, o)
        s.chk(f"AIS-F-{f['Clave']}", f"Línea de fuga del encapsulado: {f['Componente']}", fuga, x.d_req_HVLV, ">=", "mm",
              1e-3, 1, req="ISO-01 · ISO-02", deps="HW-04, HW-05", blando=True, nota=f.get("Fuente / nota", ""))
        s.chk(f"AIS-V-{f['Clave']}", f"Tensión de trabajo de la barrera: {f['Componente']}", vt, x.V_cont, ">=", "V",
              dec=0, req="ISO-06")
