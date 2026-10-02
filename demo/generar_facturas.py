"""Genera facturas PDF FICTICIAS para probar el bot.

Tres proveedores inventados, cada uno con un formato distinto (como en la vida real),
más casos con errores a propósito para demostrar la validación:
  - una factura cuyo total no cuadra con subtotal + IVA,
  - una factura duplicada (mismo proveedor y número),
  - una factura sin NIT.

    python demo/generar_facturas.py      -> entrada/*.pdf
"""
import random
from datetime import date, timedelta
from pathlib import Path

from fpdf import FPDF

SALIDA = Path(__file__).resolve().parents[1] / "entrada"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

PRODUCTOS = {
    "andina": [("Resma papel carta", 18_500), ("Tóner impresora", 245_000), ("Carpeta AZ", 9_800),
               ("Cuaderno argollado", 12_400), ("Marcadores x12", 21_000)],
    "tornillo": [("Tornillo drywall x100", 15_900), ("Taladro percutor", 389_000), ("Cinta métrica 5m", 22_500),
                 ("Juego destornilladores", 48_000), ("Silicona transparente", 13_200)],
    "tecno": [("Mouse inalámbrico", 54_900), ("Teclado USB", 69_000), ("Cable HDMI 2m", 24_000),
              ("Memoria USB 64GB", 39_900), ("Disco SSD 480GB", 189_000)],
}


def pesos(v: float) -> str:
    return f"{v:,.0f}".replace(",", ".")


def items_aleatorios(clave, rnd):
    elegidos = rnd.sample(PRODUCTOS[clave], k=rnd.randint(2, 4))
    return [(n, rnd.randint(1, 6), p) for n, p in elegidos]


def pdf_base():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(True, 15)
    return pdf


def factura_andina(num, fecha, items, nit="900.123.456-7", total_extra=0):
    pdf = pdf_base()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 9, "DISTRIBUIDORA ANDINA S.A.S.", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    if nit:
        pdf.cell(0, 6, f"NIT: {nit}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Cra 27 # 45-10, Bucaramanga", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, f"FACTURA ELECTRÓNICA DE VENTA No. FE-{num}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Fecha de emisión: {fecha:%d/%m/%Y}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Descripción  Cant  Valor unitario  Valor total", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    subtotal = 0
    for desc, cant, precio in items:
        pdf.cell(0, 6, f"{desc}  {cant}  $ {pesos(precio)}  $ {pesos(cant * precio)}", new_x="LMARGIN", new_y="NEXT")
        subtotal += cant * precio
    iva = round(subtotal * 0.19)
    pdf.ln(3)
    pdf.cell(0, 6, f"Subtotal: $ {pesos(subtotal)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"IVA 19%: $ {pesos(iva)}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, f"TOTAL A PAGAR: $ {pesos(subtotal + iva + total_extra)}", new_x="LMARGIN", new_y="NEXT")
    return pdf


def factura_tornillo(num, fecha, items, nit="800987654-1", total_extra=0):
    pdf = pdf_base()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Ferretería El Tornillo", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    if nit:
        pdf.cell(0, 5, f"Nit {nit} - Régimen común", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "Floridablanca, Santander", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 6, f"Factura N° {num}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Fecha: {fecha:%Y-%m-%d}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    subtotal = 0
    for desc, cant, precio in items:
        pdf.cell(0, 6, f"{desc}  {cant}  {pesos(precio)}  {pesos(cant * precio)}", new_x="LMARGIN", new_y="NEXT")
        subtotal += cant * precio
    iva = round(subtotal * 0.19)
    pdf.ln(3)
    pdf.cell(0, 6, f"Valor antes de IVA  {pesos(subtotal)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"IVA  {pesos(iva)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Total  {pesos(subtotal + iva + total_extra)}", new_x="LMARGIN", new_y="NEXT")
    return pdf


def factura_tecno(num, fecha, items, nit="901.555.222-3", total_extra=0):
    pdf = pdf_base()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 8, "TecnoSuministros Ltda.", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"No. Factura: TS-{num}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Fecha: {fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}", new_x="LMARGIN", new_y="NEXT")
    if nit:
        pdf.cell(0, 6, f"NIT {nit}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    subtotal = 0
    for desc, cant, precio in items:
        pdf.cell(0, 6, f"{desc}  {cant}  $ {pesos(precio)}  $ {pesos(cant * precio)}", new_x="LMARGIN", new_y="NEXT")
        subtotal += cant * precio
    iva = round(subtotal * 0.19)
    pdf.ln(3)
    pdf.cell(0, 6, f"Sub-total: $ {pesos(subtotal)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"I.V.A.: $ {pesos(iva)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Neto a pagar: $ {pesos(subtotal + iva + total_extra)}", new_x="LMARGIN", new_y="NEXT")
    return pdf


def main(semilla: int = 7):
    rnd = random.Random(semilla)
    SALIDA.mkdir(exist_ok=True)
    plantillas = [("andina", factura_andina, 1020), ("tornillo", factura_tornillo, 4580), ("tecno", factura_tecno, 770)]
    inicio = date(2026, 8, 1)
    n = 0
    for i in range(12):
        clave, fn, base = plantillas[i % 3]
        fecha = inicio + timedelta(days=rnd.randint(0, 60))
        num = base + i
        kwargs = {}
        if i == 4:
            kwargs["total_extra"] = 50_000      # error: el total no cuadra
        if i == 8:
            kwargs["nit"] = None                # error: falta el NIT
        pdf = fn(num, fecha, items_aleatorios(clave, rnd), **kwargs)
        pdf.output(SALIDA / f"{clave}_{num}.pdf")
        n += 1
        if i == 0:                              # error: la misma factura llega dos veces
            pdf.output(SALIDA / f"{clave}_{num}_copia.pdf")
            n += 1
    print(f"{n} facturas ficticias en {SALIDA}")


if __name__ == "__main__":
    main()
