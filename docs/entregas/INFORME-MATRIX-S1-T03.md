# Entrega MATRIX-S1-T03 — Esquema de la Wiki

## 1. Resultado
Se diseñó e implementó la arquitectura de información completa para la base de conocimiento estructurada de **GO Service LATAM (MATRIX)** en Markdown, plenamente compatible con Obsidian (grafo bidireccional y Dataview) y optimizada para pipelines de ingesta y consulta mediante modelos de lenguaje (LLM / RAG) como Claude 3.5 Sonnet y DeepSeek V3.

Todos los componentes requeridos se encuentran documentados, estandarizados e integrados en el repositorio:
1. **Esquema general y taxonomía**: Especificación de la jerarquía de carpetas bajo `wiki/`, tipos de entidades y frontmatter YAML estandarizado (`docs/esquema/ESQUEMA_GENERAL.md`).
2. **Plantillas oficiales reutilizables**: 5 plantillas Markdown con placeholders estructurados (`wiki/_templates/`) para reportes individuales, MOCs/índices, entidades de equipo, fallas/diagnósticos y resúmenes ejecutivos.
3. **Reglas normativas de convención, enlaces y citas**: Guía estricta de nomenclatura kebab-case con prefijos, conectividad del grafo mediante `[[wikilinks]]` con aliases (regla anti-huérfanas) y trazabilidad probatoria con notas al pie (`docs/esquema/REGLAS_NOMENCLATURA_ENLACES_CITAS.md`).
4. **Flujos operativos (SOPs)**:
   - `SOP_INGESTA.md`: Procedimiento de extracción asistida por LLMs a partir de reportes limpios (`limpio/R-XXXXXX.md`).
   - `SOP_CONSULTA.md`: Procedimiento de búsqueda RAG y políticas de respuesta con citación ineludible y cero alucinaciones.
   - `SOP_REVISION.md`: Procedimiento y checklist multidimensional de auditoría y control de calidad.
5. **Herramienta de validación automatizada**: Script utilitario `scripts/validar_wiki.py` para la auditoría continua del grafo, sintaxis YAML, links rotos y páginas huérfanas.

---

## 2. Componentes Entregados en el Repositorio

```text
MATRIX/
├── docs/
│   ├── esquema/
│   │   ├── ESQUEMA_GENERAL.md                     # Arquitectura de información y taxonomía
│   │   ├── REGLAS_NOMENCLATURA_ENLACES_CITAS.md   # Convenciones, wikilinks y citas
│   │   ├── SOP_INGESTA.md                         # Protocolo de ingesta con LLM
│   │   ├── SOP_CONSULTA.md                        # Protocolo de consulta RAG antialucinación
│   │   └── SOP_REVISION.md                        # Protocolo de auditoría y checklist
│   └── entregas/
│       ├── INFORME-MATRIX-S1-T01.md
│       └── INFORME-MATRIX-S1-T03.md               # Este informe
├── scripts/
│   ├── comun.py
│   ├── limpieza.py
│   └── validar_wiki.py                            # Validador automático de la wiki
└── wiki/
    ├── _templates/                                # Plantillas maestras para LLMs y Obsidian
    │   ├── tpl-reporte-individual.md              # Plantilla para atenciones técnicas
    │   ├── tpl-moc-indice.md                      # Plantilla para mapas de contenido
    │   ├── tpl-entidad-equipo.md                  # Plantilla para modelos/familias
    │   ├── tpl-entidad-falla.md                   # Plantilla para síntomas y diagnósticos
    │   └── tpl-resumen-ejecutivo.md               # Plantilla para balances periódicos
    ├── indices/                                   # Mapas de Contenido (MOCs)
    │   ├── MOC-indice-general.md                  # Punto de entrada maestro del grafo
    │   ├── MOC-equipos.md                         # Índice de modelos
    │   ├── MOC-fallas.md                          # Índice de diagnósticos
    │   ├── MOC-reportes.md                        # Índice de atenciones
    │   └── MOC-resumenes.md                       # Índice de balances gerenciales
    ├── reportes/                                  # Notas de atenciones técnicas individuales
    │   └── REP-R-000001.md                        # Caso representativo auditado
    ├── equipos/                                   # Catálogo de modelos de equipo
    │   └── EQP-bomba-mx-200.md                    # Ficha técnica de modelo
    ├── fallas/                                    # Catálogo taxonómico de fallas
    │   └── FAL-sobrecalentamiento-motor.md        # Árbol de diagnóstico diferencial
    ├── repuestos/                                 # Catálogo de repuestos e insumos
    │   └── PAR-filtro-sintetico-fs-01.md          # Ficha de pieza crítica
    └── resumenes/                                 # Balances operativos de confiabilidad
        └── RES-2026-q1-flota.md                   # Síntesis ejecutiva de muestra
```

---

## 3. Verificación Automatizada Ejecutada

Se ejecutó la suite de auditoría técnica automatizada sobre el corpus inicial de la wiki:

```powershell
python scripts/validar_wiki.py
```

### Salida real del comando:
```text
Analizando 10 archivos Markdown en wiki...

--- RESULTADO DE LA VALIDACIÓN ---

✅ Validación EXITOSA: 0 errores detectados en 10 notas.
```

### Criterios validados con éxito:
- **Nomenclatura y Prefijos**: 100% de los archivos cumplen con el patrón `<PREFIJO>-<slug>.md` en minúsculas y kebab-case.
- **Integridad YAML**: Sintaxis válida en todos los frontmatters con tipado correcto y campos requeridos presentes.
- **Topología del Grafo**: Cero enlaces rotos (`broken links: 0`). Cero páginas huérfanas (`orphan pages: 0`). Todas las notas derivan o conducen a un MOC temático.
- **Trazabilidad y Citación**: Todo reporte de servicio cuenta con su ancla de respaldo hacia `limpio/` y citas al pie para cada campo técnico.

---

## 4. Guía de Adopción Rápida

1. **Para Operadores Humanos**:
   - Abrir la carpeta `wiki/` como bóveda (*vault*) en Obsidian.
   - Navegar comenzando desde `wiki/indices/MOC-indice-general.md` o la vista interactiva de grafo (*Graph View*).
2. **Para Ingesta con LLMs**:
   - Seguir las instrucciones y prompts de `docs/esquema/SOP_INGESTA.md`.
   - Rellenar la plantilla correspondiente de `wiki/_templates/`.
3. **Para Consultas RAG**:
   - Aplicar el pipeline de recuperación y la política antialucinación de `docs/esquema/SOP_CONSULTA.md`.
4. **Control de Calidad Continuo**:
   - Ejecutar `python scripts/validar_wiki.py` antes de cualquier confirmación (*commit*).

---

La implementación y sus pruebas fueron generadas con asistencia de inteligencia artificial.
