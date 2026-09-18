"""Potencia y bus DC: rizado, di/dt, corrientes de bus, caso de fallo y fusible."""
import math

from .unidades import fmt


def calcula(ctx):
    x = ctx.x
    s = ctx.seccion(1, "Potencia y bus DC",
                    "Modelo de primer orden: L constante en cada punto de trabajo y conmutación ideal.")
    bip = x.Modulacion == "Bipolar"
    if x.Modulacion not in ("Unipolar", "Bipolar"):
        raise ValueError("Modulacion debe ser «Unipolar» o «Bipolar»")
    casos = [("EMS, L mínima", "L_EMS_min"), ("EMS, L máxima", "L_EMS_max"),
             ("HEMS, L mínima", "L_HEMS_min"), ("HEMS, L máxima", "L_HEMS_max")]

    # 1.1 Rizado
    s.sub("1.1 Rizado de corriente en la bobina",
          "Unipolar: la salida conmuta entre 0 y ±Vbus a 2·fsw, ΔI = Vbus·m·(1−m)/(2·L·fsw), máximo en m = 0,5: Vbus/(8·L·fsw). "
          "Bipolar: ΔI = Vbus·(1−m²)/(2·L·fsw), máximo en m = 0: Vbus/(2·L·fsw). Se desprecia R frente a L. "
          f"Modulación seleccionada: **{x.Modulacion}**; fsw = {fmt(x.fsw / 1e3, 1)} kHz; rizado admisible = {fmt(x.dI_pp_max, 2)} A.")
    filas, reg, sel = [], {}, []
    for et, n in casos:
        L = ctx.v[n]
        u_min = x.Vbus_min / (8 * L * x.fsw)
        u_max = x.Vbus_max / (8 * L * x.fsw)
        b_max = x.Vbus_max / (2 * L * x.fsw)
        e = b_max if bip else u_max
        sel.append(e)
        estado = "CUMPLE" if e <= x.dI_pp_max else "**NO CUMPLE**"
        filas.append([et, fmt(L * 1e3, 2), fmt(u_min), fmt(u_max), fmt(b_max), fmt(e), estado])
        for k, val in (("unip_Vmin", u_min), ("unip_Vmax", u_max), ("bip_Vmax", b_max)):
            reg[f"rizado.{n}.{k}"] = (val, fmt(val), "A", f"Rizado {et} ({k})")
    s.tabla(["Electroimán / punto", "L (mH)", "ΔI unip., Vbus_min (A)", "ΔI unip., Vbus_max (A)",
             "ΔI bip., Vbus_max (A)", "ΔI con la modulación elegida (A)", "Resultado"], filas, registro=reg)
    s.chk("POT-01", "Rizado en el peor caso (L mínima, Vbus_max)", max(sel), x.dI_pp_max, "<=", "A", dec=2,
          req="LOAD-07", deps="EM-C-03, FW-08", nota="Doc. v0.2 §6.1.3: 1,30 A (EMS) y 0,40 A (HEMS) a 400 V, unipolar",
          expr="max(ΔI) ≤ dI_pp_max")
    k = 2 if bip else 8
    s.res("fsw_min_rizado", "fsw mínima para cumplir el rizado con L mínima",
          x.Vbus_max / (k * min(x.L_EMS_min, x.L_HEMS_min) * x.dI_pp_max), "kHz", 1e3, 1,
          expr="Vbus_max/(k·L_min·dI_pp_max)", nota="k = 8 (unipolar) o 2 (bipolar)")

    # 1.2 Dinámica
    s.sub("1.2 Dinámica de la corriente",
          "di/dt = (Vbus − R·I)/L. Tiempo de 0 a Ipk con L constante: τ·ln(Vbus/(Vbus − R·Ipk)), τ = L/R. "
          "En rueda libre (SAF-05) la corriente cae al 1 % en 4,6·τ. Con L no lineal, los valores son orientativos.")
    filas, reg = [], {}
    for et, n in casos:
        L = ctx.v[n]
        d1 = x.Vbus_min / L / 1e3
        d2 = x.Vbus_max / L / 1e3
        d3 = (x.Vbus_min - x.Rcoil * x.Ipk) / L / 1e3
        t = (L / x.Rcoil * math.log(x.Vbus_min / (x.Vbus_min - x.Rcoil * x.Ipk)) * 1e3
             if x.Vbus_min > x.Rcoil * x.Ipk else None)
        tau = L / x.Rcoil * 1e3
        filas.append([et, fmt(L * 1e3, 2), fmt(d1, 1), fmt(d2, 1), fmt(d3, 1),
                      fmt(t, 2) if t is not None else "no alcanzable", fmt(tau, 1)])
        reg[f"didt.{n}.Vmin"] = (d1, fmt(d1, 1), "A/ms", f"di/dt {et}, Vbus_min")
        reg[f"didt.{n}.Vmax"] = (d2, fmt(d2, 1), "A/ms", f"di/dt {et}, Vbus_max")
        reg[f"t_subida.{n}"] = (t, fmt(t, 2), "ms", f"Tiempo de 0 a Ipk, {et}")
        reg[f"tau.{n}"] = (tau, fmt(tau, 1), "ms", f"L/R, {et}")
    s.tabla(["Electroimán / punto", "L (mH)", "di/dt, Vbus_min, I = 0 (A/ms)", "di/dt, Vbus_max, I = 0 (A/ms)",
             "di/dt, Vbus_min, I = Ipk (A/ms)", "t de 0 a Ipk, Vbus_min (ms)", "τ = L/R (ms)"], filas, registro=reg)
    s.res("V_coil_pk", "Tensión en la bobina a Ipk", x.Rcoil * x.Ipk, "V", dec=1, expr="Rcoil·Ipk")
    s.res("m_pk", "Índice de modulación a Ipk con Vbus_min", x.V_coil_pk / x.Vbus_min, "–", dec=3, expr="V_coil_pk/Vbus_min")
    s.chk("POT-02", "Corriente máxima alcanzable con Vbus_min (sin pérdidas)", x.Vbus_min / x.Rcoil, x.Ipk, ">=", "A",
          dec=1, req="LOAD-03", nota="Margen de tensión para el lazo de corriente", expr="Vbus_min/Rcoil ≥ Ipk")

    # 1.3 Corrientes
    s.sub("1.3 Corrientes de bus y de DC-link",
          "Corriente media de bus = P_bobina/(η·Vbus). La entrada del puente son pulsos de amplitud I y ciclo m: "
          "I_rms,puente = I·√m; I_rms,C = I·√(m·(1−m)), con máximo I/2 en m = 0,5. Rizado del DC-link suponiendo que el bus solo aporta la media: "
          "ΔV = I·m·(1−m)/(2·fsw·C) + I·ESR. Se ignoran la inductancia del bus y la interacción entre placas.")
    s.res("P_coil_pk", "Potencia en la bobina a Ipk", x.Rcoil * x.Ipk ** 2, "W", dec=0, expr="Rcoil·Ipk²")
    s.res("I_bus_pk", "Corriente media de bus a Ipk, Vbus_min", x.P_coil_pk / (x.eta_pwr * x.Vbus_min), "A", dec=2,
          expr="P_coil_pk/(eta_pwr·Vbus_min)", nota="Doc. v0.2 §6.2: 13,5 A sin pérdidas")
    s.res("I_bus_pk_Vmax", "Corriente media de bus a Ipk, Vbus_max", x.P_coil_pk / (x.eta_pwr * x.Vbus_max), "A", dec=2,
          expr="P_coil_pk/(eta_pwr·Vbus_max)", nota="Doc. v0.2 §6.2: 10,8 A sin pérdidas")
    s.res("I_bus_cont", "Corriente media de bus en continuo, Vbus_min", x.Rcoil * x.Irms_cont ** 2 / (x.eta_pwr * x.Vbus_min),
          "A", dec=3, expr="Rcoil·Irms_cont²/(eta_pwr·Vbus_min)")
    if x.Bus_topo not in ("Encadenado", "Estrella"):
        raise ValueError("Bus_topo debe ser «Encadenado» o «Estrella»")
    s.res("N_chain", "Placas cuya corriente atraviesa la entrada de la primera",
          float(x.N_MD if x.Bus_topo == "Encadenado" else 1), "–", dec=0, expr="N_MD si Bus_topo = Encadenado; si no, 1")
    s.res("I_in_first", "Corriente de entrada de la primera placa, todas a Ipk", x.N_chain * x.I_bus_pk, "A", dec=1,
          expr="N_chain·I_bus_pk", nota="Peor caso simultáneo")
    s.res("I_in_first_cont", "Corriente de entrada de la primera placa, en continuo", x.N_chain * x.I_bus_cont, "A", dec=2,
          expr="N_chain·I_bus_cont")
    s.res("I_bridge_rms", "Corriente eficaz de entrada al puente a Ipk", x.Ipk * math.sqrt(x.m_pk), "A", dec=1,
          expr="Ipk·√m_pk", nota="Para las pistas DC-link ↔ puente")
    s.res("I_cap_rms_pk", "Corriente eficaz en el DC-link en el punto Ipk, Vbus_min",
          x.Ipk * math.sqrt(x.m_pk * (1 - x.m_pk)), "A", dec=1, expr="Ipk·√(m_pk·(1−m_pk))")
    s.res("I_cap_rms_wc", "Corriente eficaz en el DC-link, peor caso (m = 0,5)", x.Ipk / 2, "A", dec=1, expr="Ipk/2",
          nota="Por ejemplo, durante la subida de corriente; para elegir condensadores")
    s.dato("Cdc", "Capacidad del DC-link", "µF", 1e-6, 1)
    s.res("dV_dc_pk", "Rizado de tensión en el DC-link en el punto Ipk",
          x.Ipk * x.m_pk * (1 - x.m_pk) / (2 * x.fsw * x.Cdc) + x.Ipk * x.ESR_dc, "V", dec=2,
          expr="Ipk·m(1−m)/(2·fsw·Cdc) + Ipk·ESR_dc")
    s.chk("POT-03", "Rizado de tensión en el DC-link, peor caso (m = 0,5)",
          x.Ipk / (8 * x.fsw * x.Cdc) + x.Ipk * x.ESR_dc, x.dVdc_pct * x.Vbus_min, "<=", "V", dec=2,
          req="DCB-07", deps="HW-02 (ESR)", nota="Límite: dVdc_pct·Vbus_min", expr="Ipk/(8·fsw·Cdc) + Ipk·ESR_dc")
    s.res("C_min_rizado", "Capacidad mínima para el rizado (sin ESR)", x.Ipk / (8 * x.fsw * x.dVdc_pct * x.Vbus_min),
          "µF", 1e-6, 1, expr="Ipk/(8·fsw·dVdc_pct·Vbus_min)")
    s.res("f_dc_link", "Frecuencia fundamental de la corriente en el DC-link", (1 if bip else 2) * x.fsw, "kHz", 1e3, 1,
          expr="2·fsw (unipolar) o fsw (bipolar)")

    # 1.4 Caso de fallo
    s.sub("1.4 Caso de fallo: sin rueda libre, la energía vuelve al DC-link (DCB-08, SAF-07)",
          "Balance de energía: ½·C·(Vf² − V0²) = E, luego Vf = √(V0² + 2E/C). Se desprecian las pérdidas durante la descarga (conservador). "
          "Los mapas llegan a 55 A; la extrapolación a Ipk es cuadrática y solo orientativa, porque el HEMS no es lineal.")
    s.res("E_map", "Energía peor caso según los mapas H11 (55 A)", max(x.E_EMS, x.E_HEMS), "J", dec=1, expr="max(E_EMS, E_HEMS)")
    s.res("E_ext", "Energía extrapolada a Ipk", x.E_map * (x.Ipk / x.I_map) ** 2, "J", dec=1, expr="E_map·(Ipk/I_map)²",
          nota="Orientativa (EM-D-03)")
    s.res("E_const", "Cota pesimista con L constante", 0.5 * x.L_EMS_0 * x.Ipk ** 2, "J", dec=1, expr="½·L_EMS_0·Ipk²",
          nota="Doc. v0.2 §6.3: 48 J")
    s.res("C_abs", "Capacidad que absorbe la energía", x.Cdc * x.N_dc_abs, "µF", 1e-6, 1, expr="Cdc·N_dc_abs")
    vf = lambda v0, e: math.sqrt(v0 ** 2 + 2 * e / x.C_abs)
    s.res("V_fault_min_map", "Tensión final desde Vbus_min (energía de los mapas)", vf(x.Vbus_min, x.E_map), "V", dec=0,
          expr="√(Vbus_min² + 2·E_map/C_abs)", nota="Doc. v0.2: ≈ 650 V")
    s.res("V_fault_map", "Tensión final desde Vbus_max (energía de los mapas)", vf(x.Vbus_max, x.E_map), "V", dec=0,
          expr="√(Vbus_max² + 2·E_map/C_abs)", nota="Doc. v0.2: ≈ 690 V")
    s.res("V_fault_max", "Tensión final desde Vbus_max (energía extrapolada a Ipk)", vf(x.Vbus_max, x.E_ext), "V", dec=0,
          expr="√(Vbus_max² + 2·E_ext/C_abs)")
    s.res("V_fault_const", "Tensión final desde Vbus_max (cota pesimista)", vf(x.Vbus_max, x.E_const), "V", dec=0,
          expr="√(Vbus_max² + 2·E_const/C_abs)", nota="Doc. v0.2: ≈ 1040 V")
    s.chk("POT-04", "Tensión de fallo (extrapolada) frente a la tensión continua admisible", x.V_fault_max, x.V_cont, "<=",
          "V", dec=0, req="DCB-08 · DCB-02", deps="HW-03, EM-D-03", nota="Sin clamp, chopper ni DC-link mayor",
          expr="V_fault_max ≤ V_cont")
    s.chk("POT-05", "Tensión de fallo frente a la tensión nominal del DC-link", x.V_fault_max, x.V_film, "<=", "V", dec=0,
          req="DCB-08", deps="HW-02, HW-03", expr="V_fault_max ≤ V_film")
    s.chk("POT-06", "Tensión de fallo frente a la VDS del MOSFET seleccionado", x.V_fault_max, ctx.mos_sel["VDS"], "<=",
          "V", dec=0, req="PWR-02", deps="HW-02", expr="V_fault_max ≤ VDS")
    s.chk("POT-07", "Capacidad instalada frente a la necesaria para no superar V_cont desde Vbus_max",
          x.C_abs, 2 * x.E_ext / (x.V_cont ** 2 - x.Vbus_max ** 2), ">=", "µF", 1e-6, 0,
          req="DCB-08", deps="HW-03, EM-D-03", nota="Doc. v0.2: ≥ 167 µF con 16,7 J",
          expr="C_abs ≥ 2·E_ext/(V_cont² − Vbus_max²)")
    s.res("C_need_map", "Capacidad necesaria con la energía de los mapas (sin extrapolar)",
          2 * x.E_map / (x.V_cont ** 2 - x.Vbus_max ** 2), "µF", 1e-6, 0, expr="2·E_map/(V_cont² − Vbus_max²)")
    s.sub("1.5 Opción clamp o chopper (HW-03)")
    s.res("R_chop_max", "Resistencia máxima del chopper", x.V_chop_on / x.Ipk, "Ω", dec=2, expr="V_chop_on/Ipk",
          nota="Para que conduzca Ipk sin superar V_chop_on")
    s.res("P_chop_pk", "Potencia de pico en la resistencia", x.V_chop_on * x.Ipk, "kW", 1e3, 1, expr="V_chop_on·Ipk")
    s.res("E_chop", "Energía por evento en la resistencia (cota)", x.E_ext, "J", dec=1, expr="E_ext")
    s.chk("POT-08", "Tensión de actuación del chopper por encima de Vbus_max con margen", x.V_chop_on,
          x.k_chop_mrg * x.Vbus_max, ">=", "V", dec=0, req="HW-03", deps="HW-03", blando=True,
          expr="V_chop_on ≥ k_chop_mrg·Vbus_max", nota="Para no actuar en servicio")
    s.chk("POT-09", "Tensión de actuación del chopper por debajo de V_cont", x.V_chop_on, x.V_cont, "<=", "V", dec=0,
          req="HW-03", deps="HW-03", expr="V_chop_on ≤ V_cont")

    # 1.6 Fusible
    s.sub("1.6 Fusible en placa (DCB-06)")
    s.chk("POT-10", "Corriente media de bus a Ipk frente al fusible con factor de utilización", x.I_bus_pk,
          x.k_fuse * x.I_fuse, "<=", "A", dec=2, req="DCB-06", deps="EM-C-01, ME-I-03", blando=True,
          expr="I_bus_pk ≤ k_fuse·I_fuse", nota="El pico dura t_pk: revisar con la curva tiempo-corriente del fusible")
    s.chk("POT-11", "Corriente de entrada de la primera placa frente al fusible (si está en el camino encadenado)",
          x.I_in_first, x.k_fuse * x.I_fuse, "<=", "A", dec=2, req="DCB-05 · DCB-06", deps="ME-I-03", blando=True,
          expr="I_in_first ≤ k_fuse·I_fuse")
    s.chk("POT-12", "Tensión nominal del fusible frente a V_cont", x.V_fuse, x.V_cont, ">=", "V", dec=0,
          req="DCB-02 · DCB-06", deps="HW-02", expr="V_fuse ≥ V_cont", nota="El 0ADKC9150-BE es de 500 VDC")
    s.chk("POT-13", "Tensión nominal del fusible frente a la tensión de fallo", x.V_fuse, x.V_fault_max, ">=", "V", dec=0,
          req="DCB-08", deps="HW-02, HW-03", expr="V_fuse ≥ V_fault_max")
