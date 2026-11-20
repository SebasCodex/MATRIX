# MATRIX

Base de conocimiento técnica de GO Service LATAM construida a partir de reportes de
servicio exportados de RP-TECH.

## Preparación

Desde la raíz del proyecto, instale las dependencias:

```powershell
python -m pip install -r requirements.txt
```

`tiktoken` es opcional; sin él se estima el conteo con caracteres/4. Para archivos `.xls`
se incluye `xlrd`.

## Limpieza de exportaciones

Guarde la exportación en `raw/` (carpeta local ignorada por Git) y ejecute:

```powershell
python scripts/limpieza.py raw/exportacion.xlsx --salida limpio --max 100
```

También se aceptan archivos `.xls` y `.csv`. Se genera un Markdown por reporte, con fecha
ISO, sin campos vacíos, casillas vacías, texto legal ni pie de página. El contenido técnico
y la ortografía no se corrigen. El programa compara los campos con contenido antes y
después de escribirlos y falla indicando los reportes si detecta pérdidas. Los alias de
encabezados se pueden extender en `scripts/comun.py`, en el diccionario `ALIAS`; se
comparan sin distinguir acentos ni mayúsculas.

La carpeta `limpio/` todavía puede contener datos personales. No la comparta ni la suba a
Git. `raw/`, `limpio/`, `fuentes/`, `datos_privados/`, archivos `.env`, hojas de cálculo y
CSV también están excluidos por `.gitignore`.

## Pruebas sintéticas

Las pruebas generan sus propios reportes ficticios y no leen exportaciones reales:

```powershell
python -m unittest discover -s pruebas -v
```

Para generar manualmente 100 filas sintéticas:

```powershell
python pruebas/generar_datos_prueba.py --salida $env:TEMP\exportacion_sintetica.xlsx --cantidad 100
```

## Privacidad y entrega

`datos_privados/tabla_codigos.csv` y `datos_privados/reportes_codigos.csv` son archivos
locales sensibles. La tabla de códigos se entrega a Coordinación por un canal autorizado y
nunca se sube a Git. No se deben incluir exportaciones reales, tablas de códigos ni datos
de clientes en las pruebas o en el control de versiones.

El código de este proyecto fue generado con asistencia de inteligencia artificial.
