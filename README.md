# 🧾 Bot de Facturas

> Convierte una carpeta de facturas PDF de distintos proveedores en un **Excel listo para contabilidad**, con totales por mes y proveedor, y **detecta automáticamente las facturas con errores** antes de que alguien las pague.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![pdfplumber](https://img.shields.io/badge/PDF-pdfplumber-red)
![Excel](https://img.shields.io/badge/Excel-openpyxl-217346?logo=microsoftexcel&logoColor=white)
![Pruebas](https://github.com/angelcrack2501-bit/bot-facturas/actions/workflows/pruebas.yml/badge.svg)

## El problema

En una pyme alguien pasa horas copiando a mano los datos de cada factura a Excel: proveedor, NIT, fecha, subtotal, IVA y total. Es lento, aburrido y propenso a errores. Peor aún, nadie revisa si la factura **suma bien** o si **ya se pagó antes**.

## Qué hace

```
entrada/*.pdf ──► extraer ──► validar ──► salida/facturas_<fecha>.xlsx  +  reporte .txt
                  (texto)    (reglas de      (Resumen · Facturas ·
                              calidad)        Detalle · Revisar)
```

- **Entiende formatos distintos.** Cada proveedor escribe su factura diferente ("TOTAL A PAGAR", "Neto a pagar", "Total"; fechas `21/08/2026`, `2026-08-07` o `18 de septiembre de 2026`). Cada campo tiene una lista de patrones, y agregar un proveedor nuevo suele ser una sola línea.
- **Valida antes de aprobar:**
  - ¿subtotal + IVA = total?
  - ¿la suma de los productos da el subtotal?
  - ¿cantidad × precio unitario = valor de cada producto?
  - ¿falta NIT, número, fecha o total?
  - ¿la factura está **duplicada** (mismo proveedor y número)?
- **Humano en el bucle.** Una factura con cualquier problema **no se suma**; va a la hoja *Revisar* con la razón exacta.
- **Excel profesional:** encabezados con formato, formato de moneda, filas en rojo para revisar y paneles congelados.
- **Modo vigilancia:** `--vigilar` procesa solo cada PDF que llegue a la carpeta.

## Demo (con facturas ficticias incluidas)

```bash
python -m venv .venv && .venv\Scripts\activate     # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python demo/generar_facturas.py     # 13 facturas ficticias, 3 formatos, 3 con errores a propósito
python procesar.py
```

Salida real de la demo:

```
Procesadas: 13 · OK: 10 · Para revisar: 3
Total aprobado: $9.651.138 (IVA $1.540.938)

Requieren revisión humana:
  ⚠ andina_1020_copia.pdf: Factura duplicada (mismo proveedor y número ya procesados)
  ⚠ tecno_778.pdf: Falta NIT del proveedor
  ⚠ tornillo_4584.pdf: Total no cuadra: subtotal + IVA = 1.898.764, factura dice 1.948.764 (diferencia +50.000)
```

**Las tres facturas dañadas a propósito se detectaron, y ninguna de las correctas se marcó.**

## Uso diario

```bash
python procesar.py              # procesa todo lo que hay en entrada/
python procesar.py --mover      # además mueve los PDF procesados a procesadas/
python procesar.py --vigilar    # se queda corriendo y procesa cada PDF nuevo
pytest -q                       # 14 pruebas
```

## Estructura

```
bot/
  extraer.py    # PDF → texto → campos (patrones por campo, 3 formatos de fecha, números colombianos)
  validar.py    # reglas de calidad → lista de problemas por factura
  exportar.py   # 4 hojas de Excel con formato + reporte en texto
procesar.py     # orquesta: lote, --mover, --vigilar; un PDF dañado no detiene el lote
demo/generar_facturas.py
tests/test_bot.py
.github/workflows/pruebas.yml   # pruebas + demo completa en cada push
```

## Limitaciones y siguientes pasos
- Funciona con PDF que tienen texto (facturas electrónicas). Para facturas **escaneadas** se agregaría OCR (Tesseract).
- Las facturas electrónicas de la DIAN traen un **XML (UBL)**; leerlo directamente sería aún más exacto que leer el PDF.
- Enviar el reporte por correo o Telegram al terminar.
- Clasificar cada gasto por categoría con un modelo de IA.

## Autor

**Ángel Santiago Vargas Castro** — Estudiante de Ingeniería en Ciencias de la Computación e IA, UDES (Bucaramanga) · [GitHub](https://github.com/angelcrack2501-bit)

*Todas las empresas, NIT y valores de la demo son ficticios.*
