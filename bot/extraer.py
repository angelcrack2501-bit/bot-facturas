"""Extrae los datos de una factura en PDF.

Cada proveedor escribe su factura distinto ("TOTAL A PAGAR", "Neto a pagar", "Total"...),
así que cada campo tiene una LISTA de patrones: se prueba uno por uno hasta que alguno encaje.
Agregar un proveedor nuevo casi siempre es solo agregar un patrón.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pdfplumber

MESES = {m: i + 1 for i, m in enumerate(
    ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
     "septiembre", "octubre", "noviembre", "diciembre"])}

NUM = r"\$?\s*([\d.]+(?:,\d{1,2})?)"   # 1.487.500  |  1487500,00  |  $ 1.487.500

PATRONES = {
    "numero": [r"No\.\s*Factura:\s*([A-Z0-9-]+)", r"FACTURA[^\n]*?No\.\s*([A-Z0-9-]+)", r"Factura\s+N[°ºo]\.?\s*([A-Z0-9-]+)"],
    "nit": [r"\bNIT:?\s*([\d.]+-\d)", r"\bNit\s+([\d.]+-\d)"],
    "subtotal": [r"Sub-?total:?\s*" + NUM, r"Valor antes de IVA\s*" + NUM],
    # anclado al inicio de línea: si no, "Valor antes de IVA 64.800" se leería como IVA
    "iva": [r"^I\.?V\.?A\.?(?:\s*\d+%)?:?\s*" + NUM],
    "total": [r"TOTAL A PAGAR:?\s*" + NUM, r"Neto a pagar:?\s*" + NUM, r"^Total:?\s*" + NUM],
}
ITEM = re.compile(r"^(?P<desc>[^\d$][^$]*?)\s+(?P<cant>\d+)\s+" + NUM.replace("(", "(?P<unit>", 1)
                  + r"\s+" + NUM.replace("(", "(?P<valor>", 1) + r"$")


@dataclass
class Factura:
    archivo: str
    proveedor: str = ""
    nit: str | None = None
    numero: str | None = None
    fecha: date | None = None
    subtotal: float | None = None
    iva: float | None = None
    total: float | None = None
    items: list[dict] = field(default_factory=list)


def a_numero(texto: str) -> float:
    """'1.487.500' -> 1487500.0 ; '1487500,50' -> 1487500.5 (formato colombiano)."""
    return float(texto.replace(".", "").replace(",", "."))


def buscar(campo: str, texto: str) -> str | None:
    for patron in PATRONES[campo]:
        m = re.search(patron, texto, re.IGNORECASE | re.MULTILINE)
        if m:
            return m.group(1)
    return None


def parse_fecha(texto: str) -> date | None:
    if m := re.search(r"(\d{2})/(\d{2})/(\d{4})", texto):
        return date(int(m[3]), int(m[2]), int(m[1]))
    if m := re.search(r"(\d{4})-(\d{2})-(\d{2})", texto):
        return date(int(m[1]), int(m[2]), int(m[3]))
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    if m := re.search(r"(\d{1,2}) de ([a-z]+) de (\d{4})", sin_tildes):
        if m[2] in MESES:
            return date(int(m[3]), MESES[m[2]], int(m[1]))
    return None


def parse_texto(texto: str, archivo: str = "") -> Factura:
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]
    f = Factura(archivo=archivo, proveedor=lineas[0] if lineas else "")
    f.numero = buscar("numero", texto)
    f.nit = buscar("nit", texto)
    f.fecha = parse_fecha(texto)
    for campo in ("subtotal", "iva", "total"):
        valor = buscar(campo, texto)
        setattr(f, campo, a_numero(valor) if valor else None)
    for l in lineas:
        if m := ITEM.match(l):
            f.items.append({"descripcion": m["desc"].strip(), "cantidad": int(m["cant"]),
                            "valor_unitario": a_numero(m["unit"]), "valor_total": a_numero(m["valor"])})
    return f


def extraer(pdf: Path) -> Factura:
    with pdfplumber.open(pdf) as doc:
        texto = "\n".join(p.extract_text() or "" for p in doc.pages)
    return parse_texto(texto, pdf.name)
