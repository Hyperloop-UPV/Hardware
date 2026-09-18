"""Orden de cálculo de los bloques."""
from . import aislamiento, alim_bt, mosfet, pistas, potencia, puerta, sensado, si, termico
from .lector import Entradas
from .nucleo import Ctx


def ejecuta(dir_entradas, dir_normas):
    ent = Entradas(dir_entradas, dir_normas)
    ctx = Ctx(ent)
    mosfet.selecciona(ctx)
    potencia.calcula(ctx)
    puerta.calcula(ctx)
    alim_bt.calcula(ctx)
    mosfet.perdidas(ctx)
    termico.cadena(ctx)
    mosfet.temperatura(ctx)
    termico.union(ctx)
    pistas.calcula(ctx)
    aislamiento.calcula(ctx)
    si.calcula(ctx)
    sensado.calcula(ctx)
    ctx.secciones.sort(key=lambda s: s.num)
    return ctx
