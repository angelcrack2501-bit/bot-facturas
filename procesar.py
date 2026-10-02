"""Bot de facturas: PDFs en entrada/  ->  salida/facturas_<fecha>.xlsx + reporte.

    python procesar.py                 # procesa todo lo que haya en entrada/
    python procesar.py --vigilar       # se queda esperando PDFs nuevos (revisa cada 10 s)
    python procesar.py --mover         # mueve los PDFs ya procesados a procesadas/
"""
import argparse
import shutil
import time
from datetime import datetime
from pathlib import Path

from bot.exportar import a_excel, reporte, tablas
from bot.extraer import extraer
from bot.validar import problemas

RAIZ = Path(__file__).parent
ENTRADA, SALIDA, PROCESADAS = RAIZ / "entrada", RAIZ / "salida", RAIZ / "procesadas"


def procesar(pdfs: list[Path], mover: bool = False) -> Path | None:
    if not pdfs:
        print("No hay facturas en entrada/.")
        return None
    vistas: set = set()
    resultados = []
    for pdf in sorted(pdfs):
        try:
            f = extraer(pdf)
        except Exception as e:                      # PDF dañado o protegido: no detiene el lote
            print(f"✗ {pdf.name}: no se pudo leer ({e})")
            continue
        resultados.append((f, problemas(f, vistas)))
    hojas = tablas(resultados)
    SALIDA.mkdir(exist_ok=True)
    destino = SALIDA / f"facturas_{datetime.now():%Y-%m-%d_%H%M}.xlsx"
    a_excel(hojas, destino)
    texto = reporte(hojas)
    destino.with_suffix(".txt").write_text(texto, encoding="utf-8")
    print(texto, f"\n\nExcel: {destino}", sep="")
    if mover:
        PROCESADAS.mkdir(exist_ok=True)
        for pdf in pdfs:
            shutil.move(str(pdf), PROCESADAS / pdf.name)
    return destino


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vigilar", action="store_true")
    ap.add_argument("--mover", action="store_true")
    a = ap.parse_args()
    ENTRADA.mkdir(exist_ok=True)
    if not a.vigilar:
        procesar(list(ENTRADA.glob("*.pdf")), a.mover)
        return
    print("Vigilando entrada/ … (Ctrl+C para salir)")
    while True:
        nuevos = list(ENTRADA.glob("*.pdf"))
        if nuevos:
            time.sleep(2)                           # deja terminar de copiar el archivo
            procesar(nuevos, mover=True)
        time.sleep(10)


if __name__ == "__main__":
    main()
