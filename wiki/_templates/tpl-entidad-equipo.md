---
type: equipo
id: EQP-{{SLUG_EQUIPO}}
title: "Ficha Técnica: {{NOMBRE_EQUIPO_MODELO}}"
aliases:
  - "{{NOMBRE_EQUIPO_MODELO}}"
  - "{{FABRICANTE_O_FAMILIA}}"
created: "{{FECHA_CREACION}}"
updated: "{{FECHA_ACTUALIZACION}}"
family: "{{FAMILIA_TECNOLOGICA}}"
model_name: "{{NOMBRE_EQUIPO_MODELO}}"
status: active
total_interventions: {{TOTAL_INTERVENCIONES}}
tags:
  - entidad
  - equipo
  - familia/{{SLUG_FAMILIA}}
---

# ⚙️ Equipo: {{NOMBRE_EQUIPO_MODELO}}

> [!INFO] Ficha de Identificación de Modelo
> - **Familia / Tipo**: `{{FAMILIA_TECNOLOGICA}}`
> - **Total de intervenciones registradas**: `{{TOTAL_INTERVENCIONES}}`
> - **Índice superior**: [[MOC-equipos|Catálogo de Equipos y Familias]]
> - **Severidad histórica promedio**: `{{SEVERIDAD_PROMEDIO}}`

---

## 1. Descripción Técnica y Aplicación
{{DESCRIPCION_GENERAL_MODELO}}
<!-- Especificaciones clave, uso en plantas/clientes y características de operación. -->

---

## 2. Síntomas y Fallas Recurrentes
Fallas más comunes diagnosticadas en este modelo según el histórico de reportes:

| Falla / Síntoma | Frecuencia | Severidad | Referencia Técnica | Causa Típica |
| :--- | :--- | :--- | :--- | :--- |
| [[FAL-{{SLUG_FALLA_1}}\|{{NOMBRE_FALLA_1}}]] | `{{FREC_1}}` | `{{SEV_1}}` | (Fuente: [[REP-{{ID_REPORTE_EJEMPLO_1}}]]) | {{CAUSA_TIPICA_1}} |
| [[FAL-{{SLUG_FALLA_2}}\|{{NOMBRE_FALLA_2}}]] | `{{FREC_2}}` | `{{SEV_2}}` | (Fuente: [[REP-{{ID_REPORTE_EJEMPLO_2}}]]) | {{CAUSA_TIPICA_2}} |

---

## 3. Repuestos y Consumibles Críticos
Piezas y repuestos de mayor rotación asociados a este equipo:
- [[PAR-{{SLUG_REPUESTO_1}}|{{NOMBRE_REPUESTO_1}}]]: {{USO_FRECUENTE_REPUESTO_1}}
- [[PAR-{{SLUG_REPUESTO_2}}|{{NOMBRE_REPUESTO_2}}]]: {{USO_FRECUENTE_REPUESTO_2}}

---

## 4. Guía Rápida de Troubleshooting y Mantenimiento
Procedimientos recomendados consolidados a partir de las intervenciones exitosas de campo:
1. **Inspección primaria**: {{PASO_INSPECCION_PRIMARIA}}
2. **Puntos de chequeo críticos**: {{PUNTOS_CHEQUEO}}
3. **Pauta preventiva recomendada**: {{INTERVALO_MANTENIMIENTO}}

---

## 5. Historial de Reportes Vinculados (Backlinks)

```dataview
TABLE service_date AS "Fecha", failure_category AS "Falla", technician_id AS "Técnico", status AS "Estado"
FROM "wiki/reportes"
WHERE contains(equipment, "{{NOMBRE_EQUIPO_MODELO}}")
SORT service_date DESC
```

### Lista estática de trazabilidad
- [[REP-{{ID_REPORTE_1}}|Reporte {{ID_REPORTE_1}}]] (`{{FECHA_1}}`): {{SINTOMA_CORTO_1}} [^REP-{{ID_REPORTE_1}}]
- [[REP-{{ID_REPORTE_2}}|Reporte {{ID_REPORTE_2}}]] (`{{FECHA_2}}`): {{SINTOMA_CORTO_2}} [^REP-{{ID_REPORTE_2}}]

---

## 6. Referencias y Trazabilidad
[^REP-{{ID_REPORTE_1}}]: Intervención técnica registrada en `limpio/R-{{ID_REPORTE_1}}.md`.
[^REP-{{ID_REPORTE_2}}]: Intervención técnica registrada en `limpio/R-{{ID_REPORTE_2}}.md`.
