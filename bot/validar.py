"""Reglas de calidad: el bot nunca da por buena una factura dudosa, la manda a revisión humana."""
from .extraer import Factura

TOLERANCIA = 1.0   # pesos de diferencia aceptables por redondeo


def pesos(v: float, signo: bool = False) -> str:
    """1898764 -> '1.898.764' (formato colombiano)."""
    return (f"{v:+,.0f}" if signo else f"{v:,.0f}").replace(",", ".")


def problemas(f: Factura, vistas: set[tuple[str, str]]) -> list[str]:
    """Devuelve la lista de problemas encontrados (vacía = factura OK).
    `vistas` acumula (nit|proveedor, número) para detectar duplicados entre archivos."""
    p = []
    for campo in ("numero", "fecha", "total"):
        if getattr(f, campo) is None:
            p.append(f"Falta {campo}")
    if not f.nit:
        p.append("Falta NIT del proveedor")
    if None not in (f.subtotal, f.iva, f.total) and abs(f.subtotal + f.iva - f.total) > TOLERANCIA:
        dif = f.total - (f.subtotal + f.iva)
        p.append(f"Total no cuadra: subtotal + IVA = {pesos(f.subtotal + f.iva)}, factura dice {pesos(f.total)} "
                 f"(diferencia {pesos(dif, signo=True)})")
    if f.items and f.subtotal is not None:
        suma = sum(i["valor_total"] for i in f.items)
        if abs(suma - f.subtotal) > TOLERANCIA:
            p.append(f"La suma de los productos ({pesos(suma)}) no coincide con el subtotal")
    for i in f.items:
        if abs(i["cantidad"] * i["valor_unitario"] - i["valor_total"]) > TOLERANCIA:
            p.append(f"Producto mal calculado: {i['descripcion']}")
    clave = (f.nit or f.proveedor, f.numero or f.archivo)
    if clave in vistas:
        p.append("Factura duplicada (mismo proveedor y número ya procesados)")
    vistas.add(clave)
    return p
