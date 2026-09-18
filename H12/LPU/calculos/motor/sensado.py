"""Sensado: shunt con amplificador aislado o modulador ΔΣ, divisor de Vbus y NTC."""
import math

from .unidades import fmt


def calcula(ctx):
    x = ctx.x
    s = ctx.seccion(7, "Sensado y adquisición",
                    "Opción A1: amplificador aislado (AMC1302) + ADC. Opción A2: modulador ΔΣ aislado (AMC1306) + filtro sinc en la FPGA. "
                    "La opción está pendiente (FW-01, HW-05). Datos de los sensores en `componentes.md`.")
    s.sub("7.1 Corriente de bobina (shunt)")
    s.dato("R_shunt", "Resistencia del shunt", "µΩ", 1e-6, 0)
    s.res("I_FS", "Fondo de escala de corriente", x.Sd_Vlin / x.R_shunt, "A", dec=1, expr="Sd_Vlin/R_shunt",
          nota="Mismo rango lineal en AMC1302 y AMC1306x05")
    s.chk("SEN-01", "Fondo de escala frente a Ipk con margen", x.I_FS, x.I_margin * x.Ipk, ">=", "A", dec=1,
          req="SNS-01", deps="HW-02", expr="I_FS ≥ I_margin·Ipk")
    s.res("I_clip", "Corriente de recorte (AMC1302)", x.Sa_Vclip / x.R_shunt, "A", dec=1, expr="Sa_Vclip/R_shunt")
    s.res("V_sh_pk", "Tensión en el shunt a Ipk", x.Ipk * x.R_shunt, "mV", 1e-3, 1, expr="Ipk·R_shunt")
    s.chk("SEN-02", "Umbral de sobrecorriente por encima de Ipk", x.I_OC, x.Ipk, ">=", "A", dec=0, req="SAF-04",
          deps="HW-01", expr="I_OC ≥ Ipk")
    s.chk("SEN-03", "Umbral de sobrecorriente dentro del rango lineal", x.I_OC, x.I_FS, "<=", "A", dec=0, req="SAF-04",
          deps="HW-01", expr="I_OC ≤ I_FS")
    s.sub("7.2 Opción A1: amplificador aislado + ADC")
    s.res("V_out_pk", "Tensión diferencial de salida a Ipk", x.Ipk * x.R_shunt * x.Sa_G, "V", dec=3, expr="Ipk·R_shunt·Sa_G")
    s.res("LSB_A1", "Resolución (LSB) con el ADC", 2 * x.I_FS / 2 ** x.N_adc, "mA", 1e-3, 1, expr="2·I_FS/2^N_adc")
    s.res("ret_A1", "Retardo de la cadena / semiperiodo de PWM", x.Sa_td * 2 * x.fsw, "%", 0.01, 1, expr="Sa_td·2·fsw")
    s.sub("7.3 Opción A2: modulador ΔΣ + filtro sinc")
    s.chk_texto("SEN-04", "Frecuencia de reloj dentro del rango del modulador", x.Sd_fmin <= x.f_clk_ds <= x.Sd_fmax,
                fmt(x.f_clk_ds / 1e6, 1), f"{fmt(x.Sd_fmin / 1e6, 0)} a {fmt(x.Sd_fmax / 1e6, 0)}", "MHz",
                req="SNS-05", deps="FW-01", expr="Sd_fmin ≤ f_clk_ds ≤ Sd_fmax")
    s.res("f_data_ds", "Frecuencia de datos a la salida del filtro", x.f_clk_ds / x.OSR, "kHz", 1e3, 2, expr="f_clk_ds/OSR")
    s.res("n_pwm_ds", "Muestras por periodo de PWM", x.f_clk_ds / x.OSR / x.fsw, "–", dec=2, expr="f_clk_ds/(OSR·fsw)")
    s.res("bits_sinc", "Longitud de palabra a la salida del sinc", x.N_sinc * math.log2(x.OSR) + 1, "bit", dec=1,
          expr="N_sinc·log2(OSR) + 1")
    s.res("t_grupo_ds", "Retardo de grupo del filtro", x.N_sinc * (x.OSR - 1) / (2 * x.f_clk_ds), "µs", 1e-6, 2,
          expr="N_sinc·(OSR − 1)/(2·f_clk_ds)")
    s.chk("SEN-05", "Tiempo de establecimiento del filtro frente al semiperiodo de PWM", x.N_sinc * x.OSR / x.f_clk_ds,
          1 / (2 * x.fsw), "<=", "µs", 1e-6, 1, req="SNS-05 · SNS-06", deps="FW-01", blando=True,
          expr="N_sinc·OSR/f_clk_ds ≤ 1/(2·fsw)", nota="Una muestra independiente por semiperiodo (muestreo sincronizado)")
    s.res("LSB_A2", "Resolución efectiva (con el ENOB de la hoja de datos)", 2 * x.I_FS / 2 ** x.Sd_ENOB, "mA", 1e-3, 1,
          expr="2·I_FS/2^Sd_ENOB", nota="ENOB dado con OSR = 256; recalcular con el OSR elegido")

    s.sub("7.4 Tensión de bus (divisor + sensor aislado)")
    s.res("R_bot_eff", "Resistencia inferior efectiva (con la entrada del sensor)",
          x.R_div_bot * x.R_sens_in / (x.R_div_bot + x.R_sens_in), "Ω", dec=1, expr="R_div_bot ∥ R_sens_in")
    s.res("R_top", "Resistencia superior total", x.R_bot_eff * (x.V_meas_FS / x.V_sens_FS - 1), "kΩ", 1e3, 1,
          expr="R_bot_eff·(V_meas_FS/V_sens_FS − 1)")
    s.res("N_res", "Resistencias en serie necesarias en la rama superior",
          float(math.ceil(max(x.V_cont, x.V_fault_max) / x.V_res_rat)), "–", dec=0,
          expr="⌈max(V_cont, V_fault_max)/V_res_rat⌉")
    s.res("R_each", "Valor de cada resistencia superior", x.R_top / x.N_res, "kΩ", 1e3, 1, expr="R_top/N_res")
    i_div = x.V_cont / (x.R_top + x.R_bot_eff)
    s.res("I_div", "Corriente del divisor a V_cont", i_div, "µA", 1e-6, 0, expr="V_cont/(R_top + R_bot_eff)")
    s.chk("SEN-06", "Potencia en cada resistencia superior a V_cont", i_div ** 2 * x.R_top / x.N_res,
          x.k_res * x.P_res_rat, "<=", "mW", 1e-3, 1, req="SNS-02", deps="HW-02", expr="I_div²·R_top/N_res ≤ k_res·P_res_rat")
    s.chk("SEN-07", "Tensión en cada resistencia superior en el caso de fallo",
          x.V_fault_max * x.R_top / (x.R_top + x.R_bot_eff) / x.N_res, x.V_res_rat, "<=", "V", dec=0,
          req="DCB-02 · SNS-02", deps="HW-02, HW-03", expr="V_fault_max·R_top/(R_top + R_bot_eff)/N_res ≤ V_res_rat")
    s.chk("SEN-08", "Fondo de escala de Vbus frente a la tensión de fallo", x.V_meas_FS, x.V_fault_max, ">=", "V", dec=0,
          req="SNS-02 · DCB-08", deps="HW-03", expr="V_meas_FS ≥ V_fault_max")
    s.res("V_sens_Vmax", "Tensión en el sensor a Vbus_max", x.Vbus_max * x.R_bot_eff / (x.R_top + x.R_bot_eff), "mV",
          1e-3, 1, expr="Vbus_max·R_bot_eff/(R_top + R_bot_eff)")
    s.res("LSB_Vbus", "Resolución efectiva de Vbus", 2 * x.V_meas_FS / 2 ** x.Sd_ENOB, "V", dec=3,
          expr="2·V_meas_FS/2^Sd_ENOB", nota="Rango bipolar del sensor con bus unipolar: se usa la mitad de los códigos")
    s.chk("SEN-09", "Umbral de sobretensión por encima de Vbus_max", x.V_OV, x.Vbus_max, ">=", "V", dec=0,
          req="SAF-01", deps="HW-01", expr="V_OV ≥ Vbus_max")
    s.chk("SEN-10", "Umbral de sobretensión por debajo de V_cont", x.V_OV, x.V_cont, "<=", "V", dec=0,
          req="SAF-01 · DCB-02", deps="HW-01", expr="V_OV ≤ V_cont")
    s.res("V_sens_OV", "Tensión en el sensor en el umbral de sobretensión", x.V_OV * x.R_bot_eff / (x.R_top + x.R_bot_eff),
          "mV", 1e-3, 1, expr="V_OV·R_bot_eff/(R_top + R_bot_eff)")

    s.sub("7.5 NTC de bobina (modelo β)",
          "R(T) = R25·exp(β·(1/T − 1/298,15)); divisor con la NTC abajo: V = Vref·R/(R + R_pol). El modelo β pierde exactitud lejos de "
          "25–85 °C: para el umbral definitivo, use la tabla R-T del fabricante o Steinhart-Hart.")
    R = lambda T: x.NTC_R25 * math.exp(x.NTC_beta * (1 / (T + 273.15) - 1 / 298.15))
    V = lambda r: x.V_ntc_ref * r / (r + x.R_ntc_pu)
    dV = lambda T, r: x.V_ntc_ref * x.R_ntc_pu * (-x.NTC_beta * r / (T + 273.15) ** 2) / (r + x.R_ntc_pu) ** 2
    rmax = R(x.T_coil_max)
    s.res("R_ntc_max", "R de la NTC a T_coil_max", rmax, "Ω", dec=0, expr="R25·exp(β(1/T − 1/T25))")
    s.res("V_ntc_max", "Tensión del divisor a T_coil_max (umbral del comparador)", V(rmax), "V", dec=3,
          expr="V_ntc_ref·R/(R + R_ntc_pu)")
    s.res("S_ntc_max", "Sensibilidad a T_coil_max", dV(x.T_coil_max, rmax), "mV/°C", 1e-3, 2, expr="dV/dT")
    s.res("P_ntc_25", "Autocalentamiento: potencia en la NTC a 25 °C",
          x.V_ntc_ref ** 2 * x.NTC_R25 / (x.NTC_R25 + x.R_ntc_pu) ** 2, "mW", 1e-3, 2, expr="Vref²·R25/(R25 + R_pol)²",
          nota="Comparar con la constante de disipación de la NTC")
    filas = []
    for T in range(-20, 151, 10):
        r = R(T)
        filas.append([str(T), fmt(r / 1e3, 3), fmt(V(r), 3), fmt(dV(T, r) * 1e3, 2)])
    s.tabla(["T (°C)", "R_NTC (kΩ)", "V_NTC (V)", "dV/dT (mV/°C)"], filas, intro="Curva de la NTC con la polarización elegida.")
