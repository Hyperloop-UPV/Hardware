#!/usr/bin/env python3
"""Calcula el Magnet Driver Abejorro y genera los informes.

Uso:
  python calculos/calcular.py              Vista previa: escribe en salida/ (no toca docs/)
  python calculos/calcular.py --publicar   Además actualiza docs/calculos/ (lo usa la GitHub Action)

Opciones:
  --commit SHA     Commit al que corresponden las entradas (por defecto, el de git si está disponible)
  --base FICHERO   resultados.json con el que comparar (por defecto, docs/calculos/resultados.json)
  --salida DIR     Carpeta de la vista previa (por defecto, salida/)
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

from motor.calculo import ejecuta          # noqa: E402
from motor.cambios import compara, historial_parametros  # noqa: E402
from motor.informe import informe, resultados_json  # noqa: E402
from motor.lector import ErrorEntradas     # noqa: E402

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Madrid")
except Exception:  # pragma: no cover
    TZ = None


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def meta_ejecucion(commit_arg):
    ahora = datetime.now(TZ) if TZ else datetime.now()
    commit = commit_arg or git("rev-parse", "HEAD")
    sucio = bool(git("status", "--porcelain", "--", "calculos"))
    if commit:
        version = f"commit `{commit[:7]}`" + (" + cambios locales sin confirmar en `calculos/`" if sucio and not commit_arg else "")
    else:
        version = "sin control de versiones"
    return {
        "fecha_iso": ahora.isoformat(timespec="seconds"),
        "fecha_texto": ahora.strftime("%d/%m/%Y %H:%M") + (" (hora de Madrid)" if TZ else ""),
        "fecha_fichero": ahora.strftime("%Y-%m-%d_%H%M"),
        "commit": commit,
        "version_texto": version,
    }


def escribe(ruta, texto):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def sin_cabecera(texto):
    """Informe sin las líneas de fecha y versión, para no reescribirlo solo por la fecha."""
    return "\n".join(l for l in texto.splitlines()
                     if not l.startswith("| Fecha |") and not l.startswith("| Versión de las entradas |"))


def indice_cambios(dir_cambios):
    ficheros = sorted((f for f in os.listdir(dir_cambios) if f.endswith(".md") and f != "README.md"), reverse=True)
    for fichero in ficheros[3:]:
        os.remove(os.path.join(dir_cambios, fichero))
    ficheros = ficheros[:3]
    L = ["# Historial de informes de cambios", "",
         "Se conservan los tres informes completos más recientes. Para la trazabilidad de parámetros, consulte el historial específico.", ""]
    L += [f"- [{f[:-3]}]({f})" for f in ficheros]
    escribe(os.path.join(dir_cambios, "README.md"), "\n".join(L) + "\n")


def actualiza_historial_parametros(ruta, entrada):
    if not entrada:
        return
    previo = ""
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            previo = f.read().rstrip()
    encabezado = "# Historial de cambios de parámetros\n\n"
    cuerpo = previo[len(encabezado):].rstrip() if previo.startswith(encabezado) else previo
    partes = [encabezado.rstrip(), entrada]
    if cuerpo:
        partes = [encabezado.rstrip(), cuerpo, entrada]
    escribe(ruta, "\n\n".join(partes) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--publicar", action="store_true")
    ap.add_argument("--commit")
    ap.add_argument("--base", default=os.path.join(RAIZ, "docs", "calculos", "resultados.json"))
    ap.add_argument("--salida", default=os.path.join(RAIZ, "salida"))
    a = ap.parse_args()

    try:
        ctx = ejecuta(os.path.join(AQUI, "entradas"), os.path.join(AQUI, "normas"))
    except ErrorEntradas as e:
        print("ERROR en las entradas:", file=sys.stderr)
        for m in e.errores:
            print("  -", m, file=sys.stderr)
        return 1
    except Exception as e:  # errores de cálculo con mensaje legible
        print(f"ERROR en el cálculo: {e}", file=sys.stderr)
        return 1

    meta = meta_ejecucion(a.commit)
    txt_informe = informe(ctx, meta)
    datos = resultados_json(ctx, meta)
    datos["fecha_texto"] = meta["fecha_texto"]
    anterior = None
    if os.path.exists(a.base):
        with open(a.base, encoding="utf-8") as f:
            anterior = json.load(f)
    txt_cambios, hay_cambios = compara(anterior, datos, meta)
    txt_parametros, hay_parametros = historial_parametros(anterior, datos, meta)
    js = json.dumps(datos, ensure_ascii=False, indent=1, sort_keys=True) + "\n"

    ff = meta["fecha_fichero"]
    escribe(os.path.join(a.salida, f"informe_{ff}.md"), txt_informe)
    escribe(os.path.join(a.salida, f"cambios_{ff}.md"), txt_cambios)
    escribe(os.path.join(a.salida, "resultados.json"), js)
    rc = ctx.recuento()
    print(f"Cálculo correcto: {rc['CUMPLE']} CUMPLE, {rc['NO CUMPLE']} NO CUMPLE, {rc['REVISAR']} REVISAR.")
    print(f"Vista previa: {os.path.relpath(os.path.join(a.salida, f'informe_{ff}.md'), RAIZ)}")
    print(f"Cambios:      {os.path.relpath(os.path.join(a.salida, f'cambios_{ff}.md'), RAIZ)}"
          + ("" if hay_cambios else " (sin cambios)"))

    if a.publicar:
        docs = os.path.join(RAIZ, "docs", "calculos")
        ruta_inf = os.path.join(docs, "informe.md")
        previo = open(ruta_inf, encoding="utf-8").read() if os.path.exists(ruta_inf) else None
        if hay_cambios or previo is None or sin_cabecera(previo) != sin_cabecera(txt_informe):
            escribe(ruta_inf, txt_informe)
        if hay_cambios:
            sha = (meta["commit"] or "local")[:7]
            dir_c = os.path.join(docs, "cambios")
            escribe(os.path.join(dir_c, f"{ff}_{sha}.md"), txt_cambios)
            indice_cambios(dir_c)
            actualiza_historial_parametros(os.path.join(docs, "historial_parametros.md"), txt_parametros)
            escribe(os.path.join(docs, "resultados.json"), js)
            print("Publicado en docs/calculos/ (con informe de cambios).")
        else:
            print("Sin cambios en los resultados: docs/calculos/resultados.json no se modifica.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
