"""Contexto de cálculo, secciones del informe y comprobaciones."""
from .unidades import fmt

CUMPLE, NO_CUMPLE, REVISAR, SIN_DATO = "CUMPLE", "NO CUMPLE", "REVISAR", "—"


class ErrorCalculo(Exception):
    pass


class Valores:
    """Acceso por atributo a parámetros y resultados (en SI): x.Vbus_min"""

    def __init__(self, ctx):
        object.__setattr__(self, "_ctx", ctx)

    def __getattr__(self, nombre):
        ctx = self._ctx
        if nombre in ctx.v:
            return ctx.v[nombre]
        raise ErrorCalculo(f"Falta el parámetro o magnitud «{nombre}» (¿se ha borrado o renombrado en las entradas?)")


class Ctx:
    def __init__(self, entradas):
        self.ent = entradas
        self.v = {n: p.valor for n, p in entradas.params.items()}
        self.x = Valores(self)
        self.secciones = []
        self.resultados = {}      # clave -> dict
        self.comprobaciones = []  # lista de dict

    def define(self, clave, valor):
        if clave in self.ent.params:
            raise ErrorCalculo(f"La magnitud calculada «{clave}» coincide con un parámetro de entrada")
        self.v[clave] = valor

    def resuelve(self, texto, unidad_si=1.0, origen=""):
        """Número (en la unidad indicada) o nombre de una magnitud."""
        from .unidades import parse_numero
        if texto is None or texto == "":
            raise ErrorCalculo(f"{origen}: falta un valor")
        if isinstance(texto, (int, float)):
            return float(texto)
        n = parse_numero(texto)
        if n is not None:
            return n * unidad_si
        if texto in self.v and isinstance(self.v[texto], (int, float)):
            return self.v[texto]
        raise ErrorCalculo(f"{origen}: «{texto}» no es un número ni una magnitud calculada")

    def seccion(self, num, titulo, intro=""):
        s = Seccion(self, num, titulo, intro)
        self.secciones.append(s)
        return s

    def recuento(self):
        r = {CUMPLE: 0, NO_CUMPLE: 0, REVISAR: 0, SIN_DATO: 0}
        for c in self.comprobaciones:
            r[c["estado"]] = r.get(c["estado"], 0) + 1
        return r


def evalua(valor, limite, op, blando):
    if valor is None or limite is None:
        return SIN_DATO
    ok = valor <= limite if op == "<=" else valor >= limite
    return CUMPLE if ok else (REVISAR if blando else NO_CUMPLE)


class Seccion:
    def __init__(self, ctx, num, titulo, intro):
        self.ctx, self.num, self.titulo, self.intro = ctx, num, titulo, intro
        self.items = []

    # --- contenido
    def sub(self, titulo, intro=""):
        self.items.append(("sub", titulo, intro))

    def nota(self, texto):
        self.items.append(("nota", texto))

    def res(self, clave, etiqueta, valor, unidad="", esc=1.0, dec=2, expr="", nota=""):
        """Guarda la magnitud en SI (clave) y la muestra dividida por esc."""
        if clave:
            self.ctx.define(clave, valor)
        mostrado = valor / esc if isinstance(valor, (int, float)) else valor
        fila = {"clave": clave, "etiqueta": etiqueta, "valor": valor, "texto": fmt(mostrado, dec),
                "unidad": unidad, "expr": expr, "nota": nota, "seccion": f"{self.num}. {self.titulo}"}
        if clave:
            self.ctx.resultados[clave] = fila
        self.items.append(("res", fila))
        return valor

    def dato(self, nombre, etiqueta, unidad="", esc=1.0, dec=2):
        v = self.ctx.v[nombre]
        p = self.ctx.ent.params.get(nombre)
        estado = f" ({p.estado})" if p is not None and p.estado != "OK" else ""
        mostrado = v / esc if isinstance(v, (int, float)) else v
        self.items.append(("res", {"clave": None, "etiqueta": etiqueta, "valor": v, "texto": fmt(mostrado, dec),
                                   "unidad": unidad, "expr": f"`{nombre}`", "nota": f"Entrada{estado}"}))

    def chk(self, cid, etiqueta, valor, limite, op, unidad="", esc=1.0, dec=2, req="", deps="", nota="",
            blando=False, expr=""):
        estado = evalua(valor, limite, op, blando)
        c = {"id": cid, "etiqueta": etiqueta, "valor": valor, "limite": limite, "op": op,
             "texto_valor": fmt(None if valor is None else valor / esc, dec),
             "texto_limite": fmt(None if limite is None else limite / esc, dec),
             "esc": esc, "unidad": unidad, "estado": estado, "req": req, "deps": deps, "nota": nota,
             "expr": expr, "seccion": f"{self.num}. {self.titulo}"}
        if any(k["id"] == cid for k in self.ctx.comprobaciones):
            raise ErrorCalculo(f"Comprobación repetida: {cid}")
        self.ctx.comprobaciones.append(c)
        self.items.append(("chk", c))
        return estado

    def chk_texto(self, cid, etiqueta, ok, texto_valor, texto_limite, unidad="", req="", deps="", nota="",
                  blando=False, expr=""):
        estado = CUMPLE if ok else (REVISAR if blando else NO_CUMPLE)
        c = {"id": cid, "etiqueta": etiqueta, "valor": None, "limite": None, "op": "",
             "texto_valor": texto_valor, "texto_limite": texto_limite, "unidad": unidad, "estado": estado,
             "req": req, "deps": deps, "nota": nota, "expr": expr, "seccion": f"{self.num}. {self.titulo}"}
        self.ctx.comprobaciones.append(c)
        self.items.append(("chk", c))
        return estado

    def tabla(self, cabeceras, filas, intro="", registro=None):
        """filas: listas de textos ya formateados. registro: {clave: (valor, texto, unidad, etiqueta)}."""
        self.items.append(("tabla", cabeceras, filas, intro))
        for clave, (valor, texto, unidad, etiqueta) in (registro or {}).items():
            self.ctx.resultados[clave] = {"clave": clave, "etiqueta": etiqueta, "valor": valor, "texto": texto,
                                          "unidad": unidad, "seccion": f"{self.num}. {self.titulo}"}
