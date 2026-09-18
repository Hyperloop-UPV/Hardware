"""Conversión de valores y unidades a SI."""
import math
import re

MICRO = "µ"  # U+00B5

# Factor que convierte la unidad indicada a la unidad SI (o a la unidad base indicada).
FACTORES = {
    "": 1.0, "–": 1.0, "-": 1.0, "—": 1.0, "V/V": 1.0, "bit": 1.0, "oz": 1.0,
    "%": 0.01,
    "V": 1.0, "mV": 1e-3, "kV": 1e3,
    "A": 1.0, "mA": 1e-3, "µA": 1e-6,
    "Ω": 1.0, "mΩ": 1e-3, "µΩ": 1e-6, "kΩ": 1e3, "MΩ": 1e6,
    "H": 1.0, "mH": 1e-3, "µH": 1e-6, "nH": 1e-9,
    "F": 1.0, "mF": 1e-3, "µF": 1e-6, "nF": 1e-9, "pF": 1e-12,
    "C": 1.0, "µC": 1e-6, "nC": 1e-9,
    "J": 1.0, "mJ": 1e-3, "µJ": 1e-6,
    "W": 1.0, "mW": 1e-3, "kW": 1e3,
    "s": 1.0, "ms": 1e-3, "µs": 1e-6, "ns": 1e-9, "ps": 1e-12,
    "Hz": 1.0, "kHz": 1e3, "MHz": 1e6,
    "m": 1.0, "mm": 1e-3, "µm": 1e-6, "mm²": 1e-6,
    "°C": 1.0, "K": 1.0, "K/W": 1.0, "W/(m·K)": 1.0,
    "L/min": 1.0 / 60000.0,
    "kV/µs": 1e9, "V/s": 1.0,
}

UNIDADES_TEXTO = {"", "–", "-", "—"}


def normaliza_unidad(u):
    u = (u or "").strip()
    u = u.replace("μ", MICRO).replace("Ω", "Ω")  # mu griega y ohmio compatible
    if u.startswith("u") and len(u) > 1 and u[1:] in {"A", "F", "H", "J", "m", "s", "Ω", "C"}:
        u = MICRO + u[1:]
    return u


def factor(u):
    u = normaliza_unidad(u)
    if u not in FACTORES:
        raise KeyError(u)
    return FACTORES[u]


_NUM = re.compile(r"^[+-]?(\d+([.,]\d*)?|[.,]\d+)([eE][+-]?\d+)?$")


def parse_numero(texto):
    """Devuelve float o None si el texto no es un número."""
    if texto is None:
        return None
    t = str(texto).strip().replace("−", "-").replace(" ", "").replace(" ", "")
    if not t or not _NUM.match(t):
        return None
    return float(t.replace(",", "."))


def fmt(v, dec=2):
    """Formato español: coma decimal; texto tal cual; None como guion."""
    if v is None:
        return "—"
    if isinstance(v, str):
        return v
    if isinstance(v, bool):
        return "Sí" if v else "No"
    if math.isinf(v) or math.isnan(v):
        return "—"
    if dec is None:
        s = f"{v:.4g}"
        if "e" in s:
            m, e = s.split("e")
            s = f"{m}·10^{int(e)}"
    else:
        s = f"{v:.{dec}f}"
    if s.startswith("-") and float(s.replace("·10^", "e").replace("-", "", 1) or 0) == 0:
        s = s[1:]
    return s.replace(".", ",").replace("-", "−")
