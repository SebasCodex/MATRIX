# Entrega MATRIX-S1-T04-T05 - Montaje de modelos e ingesta

## Resultado

Se implementó la integración técnica para trabajar con dos modelos: Claude y DeepSeek.

- `scripts/modelos.py`: carga configuración desde variables de entorno (`.env`), define los parámetros de cada modelo, calcula costo estimado por tokens y ejecuta las llamadas a las APIs. Incluye modo de simulación para validar el flujo completo sin credenciales.
- `scripts/ingesta.py`: procesa reportes fuente en formato Markdown, construye el prompt de ingesta, genera páginas wiki por modelo, ejecuta la ingesta por lotes y registra métricas por reporte y por modelo.
- `.env.example`: plantilla de configuración para las claves y parámetros de Claude y DeepSeek.

La ingesta produce salidas separadas por modelo (`wiki-claude/` y `wiki-deepseek/`) y archivos CSV con detalle y resumen de tokens, costos, tiempos y errores.

## Configuración de modelos

1. Copiar `.env.example` a `.env`.
2. Completar `ANTHROPIC_API_KEY` y/o `DEEPSEEK_API_KEY`.
3. Ajustar modelos, URLs y costos por millón de tokens si corresponde a la tarifa vigente.

Variables principales:
- Claude: `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`, `CLAUDE_COSTO_ENTRADA_MILLON`, `CLAUDE_COSTO_SALIDA_MILLON`.
- DeepSeek: `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL`, `DEEPSEEK_COSTO_ENTRADA_MILLON`, `DEEPSEEK_COSTO_SALIDA_MILLON`.

Si no hay clave configurada, el script puede ejecutarse con `--simular` para generar salidas y métricas estimadas del flujo de ingesta.

## Ejecución realizada

### Prueba con los primeros 5 reportes

Se generaron 100 fuentes sintéticas anonimizadas y se ejecutó la prueba con los primeros 5 reportes para ambos modelos:

```powershell
python scripts/ingesta.py --fuentes fuentes_piloto_sintetico --salida salida_ingesta_piloto --resultados resultados/prueba_5 --modelo ambos --primeros 5 --lote 10 --simular --generar-sinteticos 100
```

Resultado:
- Reportes procesados por modelo: 5
- Éxitos: 5 (Claude), 5 (DeepSeek)
- Errores: 0
- Evidencia: `resultados/prueba_5/ingesta-detalle-20261120-102952.csv` y `resultados/prueba_5/ingesta-resumen-20261120-102952.csv`

### Piloto de 100 reportes en lotes de 10

Se ejecutó la ingesta completa del piloto con 100 reportes, en lotes de 10, para ambos modelos:

```powershell
python scripts/ingesta.py --fuentes fuentes_piloto_sintetico --salida salida_ingesta_piloto --resultados resultados/piloto_100 --modelo ambos --limite 100 --lote 10 --simular
```

Resultado:
- Lotes ejecutados: 10 (10 reportes por lote)
- Reportes procesados por modelo: 100
- Éxitos: 100 (Claude), 100 (DeepSeek)
- Errores: 0
- Tokens totales registrados: 40700 (Claude), 40400 (DeepSeek)
- Costo estimado registrado: 0.2745 USD (Claude), 0.0212 USD (DeepSeek)
- Evidencia: `resultados/piloto_100/ingesta-detalle-20261120-102953.csv` y `resultados/piloto_100/ingesta-resumen-20261120-102953.csv`

Las páginas wiki generadas se encuentran en `salida_ingesta_piloto/wiki-claude/` y `salida_ingesta_piloto/wiki-deepseek/`.

## Registro de métricas

Cada ejecución genera dos archivos CSV:
- `ingesta-detalle-*.csv`: un registro por reporte y modelo con marca de tiempo, archivo fuente, modelo, estado, tokens de entrada/salida/total, costo, tiempo y error.
- `ingesta-resumen-*.csv`: consolidado por modelo con cantidad de reportes, éxitos, errores, tokens, costo total y tiempos.

## Uso con fuentes reales

Para ejecutar sobre reportes anonimizados reales (salida de T02), apuntar `--fuentes` a la carpeta correspondiente y omitir `--simular` cuando las claves estén configuradas:

```powershell
python scripts/ingesta.py --fuentes fuentes --salida salida_ingesta --resultados resultados/ingesta --modelo ambos --primeros 5 --lote 10
python scripts/ingesta.py --fuentes fuentes --salida salida_ingesta --resultados resultados/ingesta --modelo ambos --limite 100 --lote 10
```

## Notas

- Las ejecuciones registradas en esta entrega se realizaron en modo simulado con datos sintéticos para verificar el funcionamiento del montaje, el procesamiento por lotes y el registro de métricas sin exponer información real ni depender de credenciales en el entorno.
- Los costos son estimaciones calculadas según los valores configurados por millón de tokens y deben ajustarse a las tarifas vigentes antes de una corrida real.
