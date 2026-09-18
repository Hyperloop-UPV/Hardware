"""Gate driving: potencia de puerta, fuentes aisladas, dv/dt, Miller, tiempo muerto y DESAT."""


def calcula(ctx):
    x, m = ctx.x, ctx.mos_sel
    s = ctx.seccion(8, "Gate driving",
                    f"Driver ADuM4146 y fuente aislada MGJ2 (datos en `componentes.md`). MOSFET seleccionado: **{m['ref']}**.")
    s.sub("8.1 Tensiones de puerta frente al MOSFET")
    s.chk("GDR-01", "Vgs_on dentro del rango recomendado del MOSFET", x.Vgs_on, m["VGSrec_on"], "<=", "V", dec=0,
          req="GD-01", deps="HW-02", blando=True, expr="Vgs_on ≤ VGSrec_on",
          nota="El TFG usa +20 V")
    s.chk("GDR-02", "Vgs_on por debajo del máximo absoluto", x.Vgs_on, m["VGSmax"], "<=", "V", dec=0,
          req="GD-01", deps="HW-02", expr="Vgs_on ≤ VGSmax")
    s.chk("GDR-03", "Vgs_off dentro del rango recomendado", x.Vgs_off, m["VGSrec_off"], ">=", "V", dec=0,
          req="GD-01", deps="HW-02", blando=True, expr="Vgs_off ≥ VGSrec_off")

    s.sub("8.2 Potencia de puerta y fuentes aisladas (por MOSFET)")
    s.res("dVg", "Excursión de tensión de puerta", x.Vgs_on - x.Vgs_off, "V", dec=1, expr="Vgs_on − Vgs_off")
    s.res("P_gate", "Potencia de puerta", m["Qg"] * x.dVg * x.fsw, "W", dec=3, expr="Qg·dVg·fsw",
          nota="Qg medida con la excursión de la hoja de datos: aproximación")
    s.res("P_iso_out", "Potencia en la salida de la fuente aislada", x.P_gate + x.D_IDD2 * x.dVg, "W", dec=3,
          expr="P_gate + D_IDD2·dVg")
    s.chk("GDR-04", "Carga de la fuente aislada frente a su potencia nominal", x.P_iso_out, x.G_P, "<=", "W", dec=3,
          req="GD-01 · AUX-02", deps="HW-02", expr="P_iso_out ≤ G_P")
    i_med = m["Qg"] * x.fsw + x.D_IDD2
    s.chk("GDR-05", "Corriente media de la salida +20 V", i_med, x.G_Ipos, "<=", "mA", 1e-3, 1,
          req="GD-01", deps="HW-02", expr="Qg·fsw + D_IDD2 ≤ G_Ipos")
    s.chk("GDR-06", "Corriente media de la salida −5 V", i_med, x.G_Ineg, "<=", "mA", 1e-3, 1,
          req="GD-01", deps="HW-02", expr="Qg·fsw + D_IDD2 ≤ G_Ineg",
          nota="Supone que toda la corriente de VDD2 vuelve por −5 V (conservador)")
    s.res("P_iso_in", "Potencia de entrada de cada fuente aislada", x.P_iso_out / x.G_eta, "W", dec=3,
          expr="P_iso_out/G_eta")
    s.res("I_iso_in", "Corriente de entrada de cada fuente aislada", x.P_iso_in / x.G_Vin, "mA", 1e-3, 1,
          expr="P_iso_in/G_Vin", nota="Se usa en el consumo de BT")

    s.sub("8.3 Corrientes de pico, dv/dt y Miller")
    s.chk("GDR-07", "Corriente de pico de encendido", x.dVg / (x.Rg_on + m["Rgint"] + x.D_Rp), x.D_Isrc, "<=", "A", dec=2,
          req="GD-01", deps="HW-02", expr="dVg/(Rg_on + Rgint + D_Rp) ≤ D_Isrc",
          nota="Límite: corriente de cortocircuito del driver")
    s.chk("GDR-08", "Corriente de pico de apagado", x.dVg / (x.Rg_off + m["Rgint"] + x.D_Rn), x.D_Isnk, "<=", "A", dec=2,
          req="GD-01", deps="HW-02", expr="dVg/(Rg_off + Rgint + D_Rn) ≤ D_Isnk")
    s.res("tau_on", "Constante de tiempo de encendido", (x.Rg_on + m["Rgint"]) * m["Ciss"], "ns", 1e-9, 1,
          expr="(Rg_on + Rgint)·Ciss")
    s.res("dvdt", "dv/dt estimada", x.Vbus_max / m["tr"], "kV/µs", 1e9, 1, expr="Vbus_max/tr",
          nota="tr de la hoja de datos con su RG de ensayo: recalcular con la RG real")
    for cid, lim, nombre, req, deps in (("GDR-09", x.D_CMTI, "del driver", "GD-01", "HW-02"),
                                        ("GDR-10", x.S_CMTI, "de los sensores aislados", "SNS-01", "HW-02, FW-01"),
                                        ("GDR-11", x.G_CMTI, "de la fuente aislada", "AUX-02", "HW-02")):
        s.chk(cid, f"dv/dt frente a la CMTI {nombre}", x.dvdt, lim, "<=", "kV/µs", 1e9, 1, req=req, deps=deps,
              expr="dvdt ≤ CMTI")
    s.res("I_miller", "Corriente de Miller", m["Crss"] * x.dvdt, "A", dec=3, expr="Crss·dvdt",
          nota="Crss a 600 V; a VDS baja es mayor")
    s.chk("GDR-12", "Pico de VGS en OFF por efecto Miller", x.Vgs_off + x.I_miller * (x.D_Rclamp + m["Rgint"]),
          m["Vth_min"], "<=", "V", dec=2, req="GD-01", deps="HW-02",
          expr="Vgs_off + I_miller·(D_Rclamp + Rgint) ≤ Vth_min", nota="Con el Miller clamp activo")

    s.sub("8.4 Tiempo muerto")
    s.res("t_dead_min", "Tiempo muerto mínimo", (m["tdoff"] + m["tf"] - m["tdon"]) + x.D_skew + x.t_dead_mrg, "ns",
          1e-9, 0, expr="(tdoff + tf − tdon) + D_skew + t_dead_mrg", nota="Tiempos del MOSFET con su RG de ensayo")
    s.chk("GDR-13", "Tiempo muerto configurado frente al mínimo", x.t_dead, x.t_dead_min, ">=", "ns", 1e-9, 0,
          req="PWR-04", deps="FW-08, HW-02", blando=True, expr="t_dead ≥ t_dead_min")
    s.res("dV_dead", "Error de tensión media por el tiempo muerto", 2 * x.t_dead * x.fsw * x.Vbus_max, "V", dec=2,
          expr="2·t_dead·fsw·Vbus_max")
    s.res("dV_dead_rel", "Error relativo a la tensión de bobina a Ipk", x.dV_dead / x.V_coil_pk, "%", 0.01, 1,
          expr="dV_dead/V_coil_pk", nota="Lo compensa el lazo de corriente")

    s.sub("8.5 Protección DESAT",
          "Umbral en VDS ≈ V_DESAT − N·Vf − I_carga·R_serie. La corriente de disparo se estima con RDS(on) lineal: en la zona de saturación "
          "la VDS crece más deprisa y el disparo real llega antes. Con pocos mΩ, un umbral de 9,2 V equivale a cientos de amperios: "
          "valorar el grado A/C (3,5 V) o un divisor.")
    s.res("V_ds_trip", "VDS de disparo", x.D_desat - x.N_d_desat * x.Vf_desat - x.D_Idesat * x.R_desat, "V", dec=2,
          expr="D_desat − N_d_desat·Vf_desat − D_Idesat·R_desat")
    s.res("I_trip_hot", "Corriente de disparo en caliente", x.V_ds_trip / m["Rhot"], "A", dec=0, expr="V_ds_trip/Rhot")
    s.chk("GDR-14", "Corriente de disparo a 25 °C (peor caso) frente a la ID pulsada", x.V_ds_trip / m["R25"], m["IDM"],
          "<=", "A", dec=0, req="GD-01 · SAF-04", deps="HW-01, HW-02", blando=True, expr="V_ds_trip/R25 ≤ IDM",
          nota="En frío la RDS(on) es menor y el disparo llega más tarde")
    s.res("t_blank", "Tiempo de blanking externo", x.C_blank * x.D_desat / x.D_Idesat, "µs", 1e-6, 3,
          expr="C_blank·D_desat/D_Idesat")
    s.chk("GDR-15", "Tiempo de respuesta DESAT (enmascaramiento + blanking)", x.D_mask + x.t_blank, x.t_desat_max, "<=",
          "µs", 1e-6, 2, req="GD-01", deps="HW-01", blando=True, expr="D_mask + t_blank ≤ t_desat_max",
          nota="No incluye la propagación interna ni el soft shutdown")
    s.chk("GDR-16", "Tensión de VDD2 por encima del UVLO del driver", x.Vgs_on, x.D_UVLO, ">=", "V", dec=1,
          req="GD-02", deps="HW-02", expr="Vgs_on ≥ D_UVLO")
