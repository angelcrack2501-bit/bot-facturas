# Cómo defender el Bot de Facturas en una entrevista

## Pitch de 30 segundos
"Hice un bot en Python que lee facturas PDF de distintos proveedores, extrae proveedor, NIT, fecha, subtotal, IVA, total y productos, y genera un Excel con resumen por mes y proveedor. Lo más importante es que **valida**: si el total no cuadra, si falta el NIT o si la factura está duplicada, no la suma y la manda a una hoja de revisión con la razón. En la demo detecta los 3 errores que puse a propósito sin marcar ninguna factura buena."

## El flujo (dibújalo)
```
PDF → pdfplumber (texto) → regex por campo → Factura (dataclass)
    → reglas de validación → OK / REVISAR → pandas → Excel (openpyxl) + reporte
```

## Preguntas que te pueden hacer

**1. ¿Cómo manejas proveedores con formatos distintos?**
Cada campo tiene una *lista* de expresiones regulares en `PATRONES` (`bot/extraer.py`). Se prueban en orden y gana la primera que encaje. Un proveedor nuevo casi siempre es agregar un patrón, sin tocar el resto del código.

**2. Cuéntame un bug que hayas encontrado.**
En la ferretería, el IVA se leía como 64.800 porque el patrón `IVA` también encajaba en la línea "Valor antes de **IVA** 64.800". Lo corregí anclando el patrón al inicio de la línea (`^IVA`) y agregué una prueba (`test_iva_no_se_confunde_con_valor_antes_de_iva`) para que no vuelva a pasar.
Otro: la hoja Detalle repetía los productos de la factura duplicada. La regla ahora es que el detalle solo incluye facturas aprobadas, y también tiene su prueba.

**3. ¿Por qué no aprobar automáticamente todo?**
Porque en finanzas un error cuesta plata. El bot hace el 90 % del trabajo y deja a una persona solo lo dudoso, con la razón exacta. Eso es "humano en el bucle".

**4. ¿Cómo detectas duplicados?**
Con un `set` de claves `(NIT, número de factura)`. Si la clave ya existe, es duplicada aunque el archivo tenga otro nombre.

**5. ¿Por qué usas una tolerancia de $1?**
Por redondeos del IVA. Comparar dinero con `==` exacto da falsos errores.

**6. ¿Qué pasa si un PDF está dañado?**
Se captura la excepción, se informa ese archivo y el resto del lote sigue (`procesar.py`).

**7. ¿Cómo sabes que funciona?**
14 pruebas con pytest: números colombianos, 3 formatos de fecha, extracción completa, cada regla de validación y la estructura del Excel. GitHub Actions las corre en cada push, junto con la demo completa.

**8. ¿Qué mejorarías?**
OCR para facturas escaneadas, leer el XML de la factura electrónica DIAN (más exacto que el PDF), notificar por correo o Telegram, y clasificar gastos con IA.

## Practica
1. Corre `python demo/generar_facturas.py` y `python procesar.py` y abre el Excel.
2. Explica `parse_fecha` en voz alta: ¿por qué tres `if`?
3. Agrega un patrón nuevo, por ejemplo "Valor total:", y escribe su prueba.
