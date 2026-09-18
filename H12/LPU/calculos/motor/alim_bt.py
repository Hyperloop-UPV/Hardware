"""Alimentación auxiliar de BT: presupuesto de consumo, PoE y EtherCAT P."""
from .unidades import fmt


def calcula(ctx):
    x = ctx.x
    s = ctx.seccion(9, "Alimentación auxiliar (BT)",
                    "Consumo por placa desde la batería de BT: P = V·I·N/(η_raíl·eta_BT). Consumos de `diseno.md`, tabla 4.")
    filas, reg, total = [], {}, 0.0
    for f in ctx.ent.tablas.get("consumos", []):
        o = f["_origen"]
        V = ctx.resuelve(f["Raíl"], 1.0, o)
        I = ctx.resuelve(f["Corriente"], 1e-3, o)
        n = ctx.resuelve(f["Nº"], 1.0, o)
        eta = ctx.resuelve(f["Rendimiento"], 1.0, o)
        p_carga = V * I * n
        p_bt = p_carga / eta / x.eta_BT
        total += p_bt
        filas.append([f["Consumidor"], fmt(V, 1), fmt(I * 1e3, 2), fmt(n, 0), fmt(p_carga, 3), fmt(eta * 100, 0),
                      fmt(p_bt, 3), f.get("Estado") or ""])
        reg[f"bt.{f['Clave']}"] = (p_bt, fmt(p_bt, 3), "W", f"Consumo desde BT: {f['Consumidor']}")
    s.tabla(["Consumidor", "Raíl (V)", "I (mA)", "Nº", "P en carga (W)", "η raíl (%)", "P desde BT (W)", "Estado"],
            filas, registro=reg)
    s.res("P_BT_sub", "Subtotal desde BT", total, "W", dec=2, expr="Σ P desde BT")
    s.res("P_BT_total", "Total por placa con margen", x.P_BT_sub * (1 + x.P_margin), "W", dec=2,
          expr="P_BT_sub·(1 + P_margin)", nota="Se suma a las pérdidas en el balance térmico")
    s.res("I_BT_min", "Corriente de entrada a V_BT_min", x.P_BT_total / x.V_BT_min, "A", dec=3, expr="P_BT_total/V_BT_min")
    s.res("I_BT_max", "Corriente de entrada a V_BT_max", x.P_BT_total / x.V_BT_max, "A", dec=3, expr="P_BT_total/V_BT_max")
    s.res("P_BT_todas", "Consumo de las N_MD placas", x.N_MD * x.P_BT_total, "W", dec=1, expr="N_MD·P_BT_total",
          nota="Dato para ME-I-02")
    s.chk("BT-01", "Consumo por placa frente al permitido", x.P_BT_total, x.P_BT_lim, "<=", "W", dec=2,
          req="AUX-03", deps="ME-I-02, HW-05", expr="P_BT_total ≤ P_BT_lim")
    s.chk("BT-02", "EtherCAT P: corriente de la línea completa", x.N_MD * x.P_BT_total / x.ECP_V, x.ECP_Imax, "<=", "A",
          dec=2, req="AUX-01", deps="ME-I-02", blando=True, expr="N_MD·P_BT_total/ECP_V ≤ ECP_Imax",
          nota="Solo si se elige EtherCAT P: la primera conexión alimenta a todas las placas")
    filas = [[n, fmt(p, 2), "Sí" if p >= x.P_BT_total else "No"] for n, p in ctx.ent.poe]
    s.tabla(["Tipo de PoE", "Potencia en el equipo alimentado (W)", "¿Suficiente para una placa?"], filas,
            intro="PoE es un enlace punto a punto y no encaja directamente con EtherCAT en línea (ME-I-02).")
