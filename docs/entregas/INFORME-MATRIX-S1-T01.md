# Entrega MATRIX-S1-T01 — Limpieza

## Resultado

`scripts/limpieza.py` procesa archivos XLSX, XLS y CSV, crea un Markdown por reporte en
`limpio/`, normaliza las fechas a `AAAA-MM-DD` y descarta campos vacíos, casillas vacías,
columnas legales y pies de página. `scripts/comun.py` mantiene el diccionario editable
`ALIAS` y las utilidades compartidas. El control de pérdida compara campos poblados y
termina con error si una lectura posterior no conserva alguno.

El conteo de tokens usa `tiktoken` si está instalado; en caso contrario estima con
caracteres/4 y lo indica. Los reportes conservan sin corregir su texto técnico y ortografía.

## Verificación sintética ejecutada

Se generaron 100 reportes ficticios y se ejecutó el script de limpieza. Salida real:

```text
Reportes procesados: 100
Campos con contenido: entrada=1967, salida=1967, perdidos=0
Tokens (caracteres/4 (estimado)):
| TOTAL | 161034 | 20334 |
Reducción estimada: 87.4%
```

Además, `python -m unittest discover -s pruebas -p 'test_limpieza.py' -v` terminó con
`OK` y verificó los 100 archivos, fecha ISO, exclusión del texto legal/pie/casillas y la
retención de una dirección aunque haya sido exportada en la columna de empresa.

## Suposiciones y límites

- Los nombres y variantes de encabezados asumidos están en `ALIAS` en
  `scripts/comun.py`; deben ajustarse a los encabezados de RP-TECH que use la organización.
- Se excluyen columnas cuyo encabezado identifica texto legal o pie de página y frases
  legales reconocidas; otros rótulos propios pueden requerir añadir alias o reglas.
- La reducción de tokens de esta verificación usa únicamente un fixture sintético
  deliberadamente largo en texto legal; no predice la reducción de una exportación real.

La implementación y sus pruebas fueron generadas con asistencia de inteligencia artificial.
