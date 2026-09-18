"""Pistas y vías de potencia (fórmula de IPC-2221)."""
import math

from .unidades import fmt

MIL = 0.0254e-3        # m
OZ_MIL = 1.378         # espesor de 1 oz en mil
OZ_M = 35e-6           # espesor de 1 oz en m
RHO_CU = 1.724e-8      # Ω·m a 20 °C
ALFA_CU = 0.00393      # 1/K


def calcula(ctx):
    x = ctx.x
    s = ctx.seccion(4, "Pistas y vías de potencia",
                    "IPC-2221: I = k·ΔT^0,44·A^0,725 (A en mil²; k = 0,048 externa y 0,024 interna). La fórmula se obtuvo para corrientes y "
                    "anchos moderados (≈ hasta 35 A y 400 mil): con decenas de amperios es una extrapolación. Úsela como primera estimación y "
                    "confirme con IPC-2152 o simulación. Redes de `diseno.md`, tabla 1.")
    filas, reg = [], {}
    for f in ctx.ent.tablas.get("pistas", []):
        o, cl = f["_origen"], f["Clave"]
        I = ctx.resuelve(f["Corriente"], 1.0, o)
        capa = f["Capa"]
        if capa not in ("Ext", "Int"):
            raise ValueError(f"{o}: Capa debe ser «Ext» o «Int»")
        n = ctx.resuelve(f["Capas en paralelo"], 1.0, o)
        w = ctx.resuelve(f["Ancho previsto"], 1.0, o)
        L = ctx.resuelve(f["Longitud"], 1.0, o)
        oz = x.oz_ext if capa == "Ext" else x.oz_int
        tmil = oz * OZ_MIL
        k = 0.048 if capa == "Ext" else 0.024
        dT = x.dT_trace
        a_req = ((I / n) / (k * dT ** 0.44)) ** (1 / 0.725)
        w_req = a_req / tmil * MIL
        dT_est = ((I / n) / (k * (w / MIL * tmil) ** 0.725)) ** (1 / 0.44) if I > 0 else 0.0
        R = RHO_CU * (1 + ALFA_CU * (x.T_amb + dT_est - 20)) * L / (w * oz * OZ_M) / n
        P = I ** 2 * R
        filas.append([f["Red"], fmt(I, 2), f"{capa} × {fmt(n, 0)}", fmt(oz, 1), fmt(w_req * 1e3, 2), fmt(w * 1e3, 2),
                      fmt(dT_est, 1), fmt(R * 1e3, 3), fmt(P, 2), fmt(I * R * 1e3, 1), f.get("Estado") or ""])
        reg[f"pista.{cl}.w_req"] = (w_req, fmt(w_req * 1e3, 2), "mm", f"Ancho necesario: {f['Red']}")
        reg[f"pista.{cl}.dT"] = (dT_est, fmt(dT_est, 1), "°C", f"ΔT estimado: {f['Red']}")
        reg[f"pista.{cl}.P"] = (P, fmt(P, 2), "W", f"Pérdidas: {f['Red']}")
        f["_calc"] = (w, w_req)
    s.tabla(["Red", "I (A)", "Capa × nº", "Cu (oz)", "Ancho necesario por capa (mm)", "Ancho previsto (mm)",
             "ΔT estimado (°C)", "R (mΩ)", "P (W)", "Caída (mV)", "Estado"], filas,
            intro=f"Incremento de temperatura admisible: dT_trace = {fmt(x.dT_trace, 0)} °C. "
                  "La resistencia se evalúa a T_amb + ΔT estimado.", registro=reg)
    for f in ctx.ent.tablas.get("pistas", []):
        w, w_req = f["_calc"]
        s.chk(f"PIS-{f['Clave']}", f"Ancho de pista: {f['Red']}", w, w_req, ">=", "mm", 1e-3, 1,
              req="DCB-03 · LOAD-03", deps="MEC-03, PT-01, ME-I-03", expr="ancho previsto ≥ ancho necesario")
    s.sub("4.1 Vías para corriente",
          "Misma fórmula (k externa) con la sección de cobre del barril; diámetro y metalizado de las vías térmicas.")
    a_mil2 = x.A_barrel / MIL ** 2
    s.res("I_via", "Corriente admisible por vía", 0.048 * x.dT_trace ** 0.44 * a_mil2 ** 0.725, "A", dec=2,
          expr="0,048·dT_trace^0,44·A_barril^0,725")
    s.res("N_via_Ipk", "Vías necesarias para Ipk (cambio de capa de la salida)", float(math.ceil(x.Ipk / x.I_via)), "–",
          dec=0, expr="⌈Ipk/I_via⌉")
    s.res("N_via_in", "Vías necesarias para la entrada de la primera placa", float(math.ceil(x.I_in_first / x.I_via)),
          "–", dec=0, expr="⌈I_in_first/I_via⌉")
