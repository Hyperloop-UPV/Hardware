"""Térmico: cadena de resistencias térmicas, shunt, balance de la placa y refrigerante."""
import math


def cadena(ctx):
    x = ctx.x
    s = ctx.seccion(3, "Térmico",
                    "Modelo unidimensional en régimen permanente; no sustituye a una simulación térmica.")
    s.sub("3.1 Resistencia térmica cápsula → agua (por MOSFET)",
          "Vías en paralelo con el FR-4: R_vía = t_pcb/(k_Cu·A_barril), A_barril = π/4·(d² − (d − 2·t_met)²). "
          "Vías sin rellenar (conservador) y sin contar los planos internos. El pad de drenador está a potencial de HV: "
          "el material de interfaz debe aislar (ISO-04).")
    s.dato("A_pad", "Área del pad de drenador", "mm²", 1e-6, 1)
    s.dato("N_via", "Número de vías térmicas", "–", 1, 0)
    s.res("A_barrel", "Sección de cobre de una vía", math.pi / 4 * (x.d_via ** 2 - (x.d_via - 2 * x.t_plat) ** 2),
          "mm²", 1e-6, 4, expr="π/4·(d_via² − (d_via − 2·t_plat)²)")
    s.res("R_via1", "Resistencia de una vía", x.t_pcb / (x.k_Cu * x.A_barrel), "K/W", dec=1, expr="t_pcb/(k_Cu·A_barrel)")
    s.res("R_vias", "Resistencia del conjunto de vías", x.R_via1 / x.N_via, "K/W", dec=3, expr="R_via1/N_via")
    a_fr4 = x.A_pad - x.N_via * math.pi / 4 * x.d_via ** 2
    s.chk("TER-01", "Área de FR-4 restante bajo el pad", a_fr4, 0.0, ">=", "mm²", 1e-6, 1, req="PWR-06",
          deps="HW-02, PT-01", expr="A_pad − N_via·π·d_via²/4 ≥ 0", nota="Si es negativa, las vías no caben en el pad")
    s.res("R_fr4", "Resistencia del FR-4 bajo el pad", x.t_pcb / (x.k_FR4 * a_fr4) if a_fr4 > 0 else 1e9, "K/W", dec=1,
          expr="t_pcb/(k_FR4·A_FR4)")
    s.res("R_pcb", "Resistencia de la PCB (vías ∥ FR-4)", 1 / (1 / x.R_vias + 1 / x.R_fr4), "K/W", dec=3,
          expr="1/(1/R_vias + 1/R_fr4)")
    s.res("R_solder", "Resistencia de la soldadura", x.t_solder / (x.k_solder * x.A_pad), "K/W", dec=3,
          expr="t_solder/(k_solder·A_pad)")
    s.res("R_TIM", "Resistencia del material de interfaz", x.t_TIM / (x.k_TIM * x.A_pad * x.k_spread), "K/W", dec=3,
          expr="t_TIM/(k_TIM·A_pad·k_spread)")
    s.dato("Rth_wb", "Resistencia cara inferior → agua", "K/W", 1, 3)
    s.res("Rth_c2w", "Rth cápsula → agua", x.R_solder + x.R_pcb + x.R_TIM + x.Rth_wb, "K/W", dec=3,
          expr="R_solder + R_pcb + R_TIM + Rth_wb")
    s.chk("TER-02", "Rigidez dieléctrica del material de interfaz", x.V_TIM_bd, x.V_cont, ">=", "V", dec=0,
          req="ISO-04 · ISO-06", deps="ME-C-01, HW-04", blando=True, expr="V_TIM_bd ≥ V_cont",
          nota="Margen exigido por definir con el tipo de aislamiento (HW-04)")

    s.sub("3.2 Shunt de corriente")
    s.res("P_sh_pk", "Potencia en el shunt a Ipk", x.Ipk ** 2 * x.R_shunt, "W", dec=2, expr="Ipk²·R_shunt")
    s.res("E_sh_pk", "Energía en el shunt durante el pico", x.P_sh_pk * x.t_pk, "J", dec=1, expr="P_sh_pk·t_pk",
          nota="Comparar con la capacidad de pulso del shunt")
    s.res("P_sh_c", "Potencia en el shunt en continuo", x.Irms_cont ** 2 * x.R_shunt, "W", dec=3, expr="Irms_cont²·R_shunt")
    s.chk("TER-03", "Potencia de pico en el shunt frente a su potencia nominal", x.P_sh_pk, x.P_sh_rat, "<=", "W", dec=2,
          req="SNS-01", deps="HW-02, EM-C-01", blando=True, expr="P_sh_pk ≤ P_sh_rat",
          nota="Si el pico es corto, usar la curva de sobrecarga del shunt")

    s.sub("3.3 Balance de pérdidas de la placa y refrigerante")
    s.res("P_br_pk_m", "Pérdidas del puente a Ipk (MOSFET seleccionado)", x.P_br_pk, "W", dec=0, expr="apartado 2")
    s.res("P_br_c_m", "Pérdidas del puente en continuo (MOSFET seleccionado)", x.P_br_c, "W", dec=1, expr="apartado 2")
    s.res("P_esr", "Pérdidas por ESR en el DC-link (peor caso)", x.I_cap_rms_wc ** 2 * x.ESR_dc, "W", dec=2,
          expr="I_cap_rms_wc²·ESR_dc")
    s.res("P_aux", "Consumo de la alimentación auxiliar (acaba en calor)", x.P_BT_total, "W", dec=1, expr="P_BT_total")
    s.res("P_board_pk", "Pérdidas totales de la placa a Ipk", x.P_br_pk + x.P_sh_pk + x.P_esr + x.P_BT_total, "W", dec=0,
          expr="P_br_pk + P_sh_pk + P_esr + P_BT_total")
    s.res("P_board_c", "Pérdidas totales de la placa en continuo",
          x.P_br_c + x.P_sh_c + x.P_esr * (x.Irms_cont / x.Ipk) ** 2 + x.P_BT_total, "W", dec=1,
          expr="P_br_c + P_sh_c + P_esr·(Irms_cont/Ipk)² + P_BT_total")
    s.res("m_dot", "Gasto másico de agua", x.Q_cool * 997, "kg/s", dec=4, expr="Q_cool·997 kg/m³")
    s.res("dT_cool", "Incremento de temperatura del agua por placa a Ipk", x.P_board_pk / (x.m_dot * 4180), "K", dec=2,
          expr="P_board_pk/(m_dot·4180)", nota="Toda la pérdida al agua (conservador)")
    s.res("T_cool_out", "Temperatura del agua en la última placa en serie", x.T_cool + x.N_cool_ser * x.dT_cool, "°C",
          dec=1, expr="T_cool + N_cool_ser·dT_cool")
    s.res("E_acc", "Energía de todas las placas al acumulador durante el pico", x.N_MD * x.P_board_pk * x.t_pk, "kJ",
          1e3, 1, expr="N_MD·P_board_pk·t_pk", nota="Dato para ME-C (sin el calor de las bobinas)")
    ctx.sec_termico = s


def union(ctx):
    x, s = ctx.x, ctx.sec_termico
    s.sub("3.4 Temperatura de unión del MOSFET seleccionado", f"MOSFET seleccionado: **{x.MOSFET_sel}**.")
    s.chk("TER-04", "Tj a Ipk (régimen permanente)", x.Tj_pk_sel, x.Tj_lim, "<=", "°C", dec=1, req="PWR-05",
          deps="EM-C-01, ME-C-01, ME-C-02, HW-02", expr="Tj_pk ≤ Tj_lim",
          nota="Conservador si t_pk es corto frente a las constantes térmicas")
    s.chk("TER-05", "Tj en continuo (Irms_cont)", x.Tj_c_sel, x.Tj_lim, "<=", "°C", dec=1, req="PWR-05",
          deps="EM-C-01, ME-C-01, ME-C-02", expr="Tj_c ≤ Tj_lim")
    s.chk("TER-06", "Coherencia: Tj a Ipk ≤ Tj_assumed usada para la RDS(on)", x.Tj_pk_sel, x.Tj_assumed, "<=", "°C",
          dec=1, req="—", blando=True, expr="Tj_pk ≤ Tj_assumed", nota="Si falla, suba Tj_assumed y recalcule")
