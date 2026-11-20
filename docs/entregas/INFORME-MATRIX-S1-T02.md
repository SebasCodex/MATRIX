# Entrega MATRIX-S1-T02 — Anonimización

## Resultado

`scripts/anonimizar.py` procesa los Markdown de `limpio/`, reemplaza cliente por `CLI`,
técnico por `TEC` y serie/equipo por `EQ`, y conserva modelo y número de reporte. Omite
teléfono, correo, contacto, dirección y firma; también sanea nombres conocidos, teléfonos
y correos en texto libre. Los modelos se protegen al sanear texto.

Los códigos persistentes se guardan en `datos_privados/tabla_codigos.csv`; la relación por
reporte se guarda en `datos_privados/reportes_codigos.csv`. Ambos archivos contienen datos
sensibles, están ignorados por Git y deben entregarse a Coordinación por un canal
autorizado. `scripts/verificar_anonimizacion.py` busca valores registrados en `fuentes/`
y `wiki-*`, admite `--revertir CODIGO REPORTE` y termina con código 1 cuando encuentra una
coincidencia.

## Batería sintética ejecutada

Se generaron dos exportaciones ficticias con el mismo cliente, técnico y serie, además de
un equipo sin serie. La salida real relevante de consola fue:

```text
Reportes anonimizados: 3
Clientes codificados: 1
Verificación correcta: 0 coincidencias en 3 archivos.
Verificación fallida: 1 coincidencias.
Código de salida esperado con inyección: 1
Verificación correcta: 0 coincidencias en 3 archivos.
Compañía de Prueba S.A.C.
```

Los reportes de ambas exportaciones mostraron repetidamente `CLI-0001`, `TEC-01` y
`EQ-0001-01`; el equipo sin serie recibió `EQ-0001-02` y mantuvo `Bomba MX-200`. La
reversión de `CLI-0001` con `R-001905` devolvió el nombre sintético asociado a ese reporte.
La inyección probó además una variante sin acentos, en mayúsculas y con sufijo `S.R.L.`.

La batería completa se ejecutó con:

```powershell
python -m unittest discover -s pruebas -v
```

Resultado: dos pruebas de integración pasaron (`OK`), cubriendo 100 reportes de limpieza,
cero campos perdidos, cero coincidencias, detección con salida 1, persistencia de códigos,
modelo/fechas/números cortos y reversión. No se usaron exportaciones ni datos reales.

## Suposiciones y límites

- Los nombres de columnas reconocidos están en `ALIAS` de `scripts/comun.py`; los nombres
  y alias reales de RP-TECH no se pudieron confirmar sin ver encabezados.
- El verificador compara los datos registrados en `tabla_codigos.csv`. No puede descubrir
  nombres de texto libre que nunca se hayan registrado en campos estructurados.
- La detección automática de teléfono exige al menos ocho dígitos para no borrar fechas ni
  números cortos. Las variantes de formato de números telefónicos se comparan por dígitos.
- La reducción de tokens varía por reporte; el fixture legal sintético de T01 produjo
  87.4%, mientras que reportes cortos pueden no reducir tokens.

La implementación y sus pruebas fueron generadas con asistencia de inteligencia artificial.
