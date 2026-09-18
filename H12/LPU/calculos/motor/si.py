"""Integridad de señal: impedancia, retardo, longitud crítica y presupuesto de tiempos."""
import math

from .unidades import fmt

PS_MM = 3.336  # ps/mm en el vacío


def z0(capa, w, t, er, h, b):
    """Impedancia de una línea (IPC-2141A). Longitudes en mm."""
    if capa == "MS":
        return 87 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))
    return 60 / math.sqrt(er) * math.log(4 * b / (0.67 * math.pi * (0.8 * w + t)))


def tpd(capa, er):
    return PS_MM * math.sqrt(0.475 * er + 0.67) if capa == "MS" else PS_MM * math.sqrt(er)


def calcula(ctx):
    x = ctx.x
    er, h, b = x.er_pcb, x.h_ms * 1e3, x.b_sl * 1e3
    t_ext, t_int = x.oz_ext * 0.035, x.oz_int * 0.035
    s = ctx.seccion(6, "Integridad de señal",
                    "Impedancia con IPC-2141A (microstrip y stripline centrada) y National AN-905 (pares diferenciales); retardo de propagación y "
                    "longitud crítica con la regla tr/6. Aproximaciones de ±10 %: el valor final lo da el calculador del fabricante (PT-01).")
    s.sub("6.1 Stackup",
          f"εr = {fmt(er, 2)}; h (microstrip) = {fmt(h, 3)} mm; b (stripline) = {fmt(b, 3)} mm; "
          f"cobre externo {fmt(t_ext, 3)} mm; interno {fmt(t_int, 3)} mm.")
    s.res("w_50_ms", "Ancho para 50 Ω en microstrip", (5.98 * h / math.exp(50 * math.sqrt(er + 1.41) / 87) - t_ext) / 0.8 * 1e-3,
          "mm", 1e-3, 3, expr="IPC-2141A despejada")
    s.res("w_50_sl", "Ancho para 50 Ω en stripline",
          (4 * b / (0.67 * math.pi * math.exp(50 * math.sqrt(er) / 60)) - t_int) / 0.8 * 1e-3, "mm", 1e-3, 3,
          expr="IPC-2141A despejada", nota="Con 2 oz en capas internas el ancho queda muy fino: consultar al fabricante")
    filas, reg, calc = [], {}, {}
    for f in ctx.ent.tablas.get("interfaces", []):
        o, cl = f["_origen"], f["Clave"]
        tipo, capa = f["Tipo"], f["Capa"]
        if tipo not in ("SE", "Dif") or capa not in ("MS", "SL"):
            raise ValueError(f"{o}: Tipo debe ser SE o Dif y Capa MS o SL")
        zt = ctx.resuelve(f["Z objetivo"], 1.0, o)
        w = ctx.resuelve(f["Ancho"], 1.0, o) * 1e3
        tr = ctx.resuelve(f["tr"], 1.0, o)
        L = ctx.resuelve(f["Longitud"], 1.0, o) * 1e3
        t = t_ext if capa == "MS" else t_int
        z = z0(capa, w, t, er, h, b)
        zd = None
        if tipo == "Dif":
            sp = ctx.resuelve(f["Separación"], 1.0, o) * 1e3
            zd = (2 * z * (1 - 0.48 * math.exp(-0.96 * sp / h)) if capa == "MS"
                  else 2 * z * (1 - 0.347 * math.exp(-2.9 * sp / b)))
        zc = zd if tipo == "Dif" else z
        err = (zc - zt) / zt
        if capa == "MS":
            valida = 0.1 <= w / h <= 2
        else:
            valida = w / (b - t) < 0.35 and t / b < 0.25
        tp = tpd(capa, er)
        lc = tr * 1e12 / (6 * tp)
        linea = L > lc or tipo == "Dif"
        filas.append([f["Interfaz"], f"{tipo}/{capa}", fmt(zt, 0), fmt(w, 3), fmt(z, 1), fmt(zd, 1) if zd else "—",
                      fmt(err * 100, 1), "Sí" if valida else "No", fmt(tp, 2), fmt(lc, 0), fmt(L, 0),
                      "Sí" if linea else "No", f.get("Estado") or ""])
        reg[f"si.{cl}.Z"] = (zc, fmt(zc, 1), "Ω", f"Impedancia: {f['Interfaz']}")
        reg[f"si.{cl}.Lcrit"] = (lc, fmt(lc, 0), "mm", f"Longitud crítica: {f['Interfaz']}")
        calc[cl] = {"zc": zc, "zt": zt, "tpd": tp, "td": L * tp, "nombre": f["Interfaz"], "valida": valida}
    s.tabla(["Interfaz", "Tipo/capa", "Z obj. (Ω)", "w (mm)", "Z0 (Ω)", "Zdif (Ω)", "Desv. (%)", "Fórmula válida",
             "tpd (ps/mm)", "L crítica (mm)", "L prevista (mm)", "¿Línea de transmisión?", "Estado"], filas, registro=reg,
            intro="Interfaces de `diseno.md`, tabla 2. Validez: microstrip 0,1 ≤ w/h ≤ 2; stripline w/(b−t) < 0,35 y t/b < 0,25.")
    for cl, c in calc.items():
        s.chk(f"SI-{cl}", f"Impedancia: {c['nombre']}", c["zc"], c["zt"], "<=", "Ω", dec=1, req="COM-03",
              deps="PT-01, FW-06", expr="|Z − Z_obj| ≤ tol_Z·Z_obj",
              nota=f"Tolerancia ±{fmt(x.tol_Z * 100, 0)} %")
        # sustituye el resultado por la comparación con tolerancia
        chk = ctx.comprobaciones[-1]
        ok = abs(c["zc"] - c["zt"]) <= x.tol_Z * c["zt"]
        chk["estado"] = "CUMPLE" if ok else "NO CUMPLE"
        chk["texto_limite"] = f"{fmt(c['zt'], 0)} ± {fmt(x.tol_Z * 100, 0)} %"
    s.sub("6.2 Presupuesto de tiempos de la interfaz FPGA–PHY",
          "Interfaz síncrona con reloj común: holgura de setup = T − (tco_max + t_vuelo,datos + t_su + t_jit + t_desfase,reloj); "
          "holgura de hold = tco_min + t_vuelo,datos − (t_h + t_desfase,reloj).")
    for nom in ("SI_if_datos", "SI_if_reloj", "SI_if_par"):
        if ctx.v[nom] not in calc:
            raise ValueError(f"{nom} = «{ctx.v[nom]}» no es una clave de la tabla de interfaces")
    s.res("T_bus_clk", "Periodo de reloj", 1 / x.f_bus_clk, "ns", 1e-9, 2, expr="1/f_bus_clk")
    s.res("t_fl_data", "Tiempo de vuelo de los datos", calc[x.SI_if_datos]["td"] * 1e-12, "ns", 1e-9, 3,
          expr="L·tpd de SI_if_datos")
    s.res("t_skew_clk", "Desfase del reloj por diferencia de longitud", x.dL_clk * 1e3 * calc[x.SI_if_reloj]["tpd"] * 1e-12,
          "ns", 1e-9, 3, expr="dL_clk·tpd de SI_if_reloj")
    s.chk("SI-SETUP", "Holgura de setup", x.T_bus_clk - (x.tco_max + x.t_fl_data + x.t_su + x.t_jit + x.t_skew_clk), 0.0,
          ">=", "ns", 1e-9, 2, req="COM-02", deps="FW-06", expr="T − (tco_max + t_fl_data + t_su + t_jit + t_skew_clk) ≥ 0")
    s.chk("SI-HOLD", "Holgura de hold", x.tco_min + x.t_fl_data - (x.t_h + x.t_skew_clk), 0.0, ">=", "ns", 1e-9, 2,
          req="COM-02", deps="FW-06", expr="tco_min + t_fl_data − (t_h + t_skew_clk) ≥ 0")
    s.sub("6.3 Igualación de longitudes")
    s.res("dL_pair_max", "Diferencia de longitud máxima dentro del par", x.skew_pair * 1e12 / calc[x.SI_if_par]["tpd"] * 1e-3,
          "mm", 1e-3, 2, expr="skew_pair/tpd de SI_if_par")
