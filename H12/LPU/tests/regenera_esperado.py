"""Regenera tests/datos_v0.2/esperado.json.

Úselo SOLO después de cambiar una fórmula a propósito y de comprobar que los nuevos
resultados son correctos:  python tests/regenera_esperado.py
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "calculos"))
from motor.calculo import ejecuta  # noqa: E402

DATOS = os.path.join(RAIZ, "tests", "datos_v0.2")
ctx = ejecuta(os.path.join(DATOS, "entradas"), os.path.join(DATOS, "normas"))
ruta = os.path.join(DATOS, "esperado.json")
with open(ruta, encoding="utf-8") as f:
    nota = json.load(f).get("_nota", "")
datos = {"_nota": nota, "comprobaciones": {c["id"]: {"estado": c["estado"], "valor": c["valor"], "limite": c["limite"]}
                                           for c in ctx.comprobaciones}}
with open(ruta, "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=1)
print(f"Actualizado {ruta} con {len(ctx.comprobaciones)} comprobaciones.")
