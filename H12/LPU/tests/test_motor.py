"""Pruebas del motor de cálculo.

Usan una copia fija de las entradas (tests/datos_v0.2), así que no fallan al cambiar
los parámetros del proyecto: solo detectan cambios no intencionados en las fórmulas.
Si se modifica una fórmula a propósito, hay que regenerar esperado.json (ver calculos/README.md).
"""
import json
import os
import shutil
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "calculos"))

from motor.calculo import ejecuta          # noqa: E402
from motor.cambios import compara, historial_parametros  # noqa: E402
from motor.informe import informe, resultados_json  # noqa: E402
from motor.lector import ErrorEntradas     # noqa: E402
from motor.unidades import parse_numero, fmt  # noqa: E402

DATOS = os.path.join(RAIZ, "tests", "datos_v0.2")
META = {"fecha_iso": "2026-09-17T00:00:00", "fecha_texto": "17/09/2026 00:00", "fecha_fichero": "x",
        "commit": "0000000", "version_texto": "prueba"}


def calcula(dir_datos=DATOS):
    return ejecuta(os.path.join(dir_datos, "entradas"), os.path.join(dir_datos, "normas"))


@pytest.fixture
def copia(tmp_path):
    destino = tmp_path / "datos"
    shutil.copytree(DATOS, destino)
    return destino


def cambia_parametro(dir_datos, nombre, nuevo_valor):
    ruta = os.path.join(dir_datos, "entradas", "parametros.md")
    with open(ruta, encoding="utf-8") as f:
        lineas = f.read().splitlines()
    for i, ln in enumerate(lineas):
        if ln.startswith(f"| {nombre} |"):
            celdas = ln.split("|")
            celdas[3] = f" {nuevo_valor} "
            lineas[i] = "|".join(celdas)
            break
    else:
        raise AssertionError(nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


def test_regresion_frente_a_la_hoja_excel():
    with open(os.path.join(DATOS, "esperado.json"), encoding="utf-8") as f:
        esperado = json.load(f)["comprobaciones"]
    obtenido = {c["id"]: c for c in calcula().comprobaciones}
    assert set(obtenido) == set(esperado)
    for cid, e in esperado.items():
        o = obtenido[cid]
        assert o["estado"] == e["estado"], cid
        for k in ("valor", "limite"):
            if e[k] is None:
                assert o[k] is None, cid
            else:
                assert o[k] == pytest.approx(e[k], rel=1e-9), f"{cid} {k}"


def test_entradas_actuales_con_tablas_de_candidatos():
    ctx = ejecuta(os.path.join(RAIZ, "calculos", "entradas"), os.path.join(RAIZ, "calculos", "normas"))
    assert ctx.v["D_Isrc"] == pytest.approx(11)
    assert ctx.v["G_Vin"] == pytest.approx(5)
    assert ctx.v["ECP_V"] == pytest.approx(24)


def test_valores_del_documento_de_requisitos():
    ctx = calcula()
    assert ctx.v["V_coil_pk"] == pytest.approx(72)
    r = ctx.resultados
    assert r["rizado.L_EMS_min.unip_Vmax"]["valor"] == pytest.approx(1.302, abs=1e-3)   # §6.1.3: 1,30 A
    assert r["rizado.L_HEMS_min.unip_Vmax"]["valor"] == pytest.approx(0.403, abs=1e-3)  # §6.1.3: 0,40 A
    assert ctx.v["V_fault_min_map"] == pytest.approx(648.5, abs=0.5)                     # §6.3: ≈ 650 V
    assert ctx.v["V_fault_map"] == pytest.approx(691.4, abs=0.5)                         # §6.3: ≈ 690 V
    assert ctx.v["C_need_map"] == pytest.approx(167e-6, rel=1e-3)                        # §6.3: ≥ 167 µF
    assert ctx.v["E_const"] == pytest.approx(48.06, abs=0.01)                            # §6.3: 48 J


def test_numeros_y_formato():
    assert parse_numero("1,92") == 1.92
    assert parse_numero("1.92") == 1.92
    assert parse_numero("−5") == -5
    assert parse_numero("1e-3") == 0.001
    assert parse_numero("Encadenado") is None
    assert parse_numero("1.000,5") is None
    assert fmt(1.302, 2) == "1,30"
    assert fmt(-4.2255, 2) == "−4,23"


def test_decimal_con_punto_y_unidades(copia):
    cambia_parametro(copia, "L_EMS_min", "1.92")
    ctx = calcula(copia)
    assert ctx.v["L_EMS_min"] == pytest.approx(1.92e-3)
    assert ctx.v["dVdc_pct"] == pytest.approx(0.02)
    assert ctx.v["Cdc"] == pytest.approx(105e-6)


def test_errores_legibles(copia):
    cambia_parametro(copia, "Ipk", "sesenta")
    with pytest.raises(ErrorEntradas) as e:
        calcula(copia)
    assert "Ipk" in str(e.value) and "no es un número" in str(e.value)


def test_informe_de_cambios(copia):
    base = calcula(copia)
    ant = resultados_json(base, META)
    cambia_parametro(copia, "Cdc", "220")
    nuevo = calcula(copia)
    act = resultados_json(nuevo, META)
    texto, hay = compara(ant, act, META)
    assert hay
    assert "| Capacidad del DC-link en placa (`Cdc`) | 105 µF | 220 µF |" in texto
    estados = {c["id"]: c["estado"] for c in nuevo.comprobaciones}
    for cid in ("POT-04", "POT-07", "SEN-08"):
        assert estados[cid] == "CUMPLE"
        assert f"| {cid} |" in texto
    texto_igual, hay_igual = compara(act, act, META)
    assert not hay_igual and "Sin cambios" in texto_igual


def test_historial_solo_registra_cambios_de_parametros(copia):
    base = calcula(copia)
    ant = resultados_json(base, META)
    cambia_parametro(copia, "Cdc", "220")
    nuevo = calcula(copia)
    act = resultados_json(nuevo, META)
    texto, hay = historial_parametros(ant, act, META)
    assert hay
    assert "Capacidad del DC-link en placa (`Cdc`)" in texto
    assert "Comprobación" not in texto

    igual, hay_igual = historial_parametros(act, act, META)
    assert not hay_igual and not igual


def test_informe_general_se_genera():
    ctx = calcula()
    texto = informe(ctx, META)
    assert "## 1. Potencia y bus DC" in texto
    assert "## Anexo C. Parámetros pendientes" in texto
    assert texto.count("| POT-04 |") >= 2
