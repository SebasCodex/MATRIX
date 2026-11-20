---
type: reporte
id: REP-{{ID_REPORTE}}
title: "Intervención {{EQUIPO_MODELO}} - {{FECHA}} - {{SINTOMA_CORTO}}"
aliases:
  - "{{NUMERO_REPORTE_ORIGINAL}}"
  - "Servicio {{EQUIPO_MODELO}} {{FECHA}}"
created: "{{FECHA_CREACION}}"
updated: "{{FECHA_ACTUALIZACION}}"
service_date: "{{FECHA_SERVICIO}}"
equipment: "[[EQP-{{SLUG_EQUIPO}}|{{EQUIPO_MODELO}}]]"
equipment_serial: "{{NUMERO_SERIE_ANONIMIZADO}}"
failure_category: "[[FAL-{{SLUG_FALLA}}|{{CATEGORIA_FALLA}}]]"
technician_id: "{{ID_TECNICO_ANONIMIZADO}}"
client_id: "{{ID_CLIENTE_ANONIMIZADO}}"
warranty: {{ES_GARANTIA_BOOLEAN}}
invoiced: {{ES_FACTURADO_BOOLEAN}}
parts_used:
  - "[[PAR-{{SLUG_REPUESTO_1}}|{{NOMBRE_REPUESTO_1}}]]"
status: ingested
anonymized: true
source_file: "{{NOMBRE_ARCHIVO_LIMPIO}}"
source_report: "{{NUMERO_REPORTE_ORIGINAL}}"
tags:
  - reporte
  - servicio-tecnico
  - equipo/{{SLUG_EQUIPO}}
  - falla/{{SLUG_FALLA}}
---

# 📋 Reporte Técnico: {{NUMERO_REPORTE_ORIGINAL}} — {{EQUIPO_MODELO}}

> [!INFO] Ficha de Servicio
> - **Fecha de intervención**: `{{FECHA_SERVICIO}}`
> - **Equipo intervenido**: [[EQP-{{SLUG_EQUIPO}}|{{EQUIPO_MODELO}}]] (Serie: `{{NUMERO_SERIE_ANONIMIZADO}}`)
> - **Diagnóstico clasificado**: [[FAL-{{SLUG_FALLA}}|{{CATEGORIA_FALLA}}]]
> - **Técnico responsable**: `{{ID_TECNICO_ANONIMIZADO}}` | **Cliente**: `{{ID_CLIENTE_ANONIMIZADO}}`
> - **Horario de atención**: `{{HORA_LLEGADA}}` a `{{HORA_SALIDA}}` (Garantía: `{{ESTADO_GARANTIA}}`)

---

## 1. Resumen Ejecutivo de la Atención
{{RESUMEN_EJECUTIVO_PARRAFO}}
<!-- Descripción sintética de 2 a 3 líneas del motivo, lo encontrado y la acción correctiva final. -->

---

## 2. Condición Inicial y Síntomas Reportados
- **Motivo de solicitud reportado**:
  > "{{TEXTO_MOTIVO_ORIGINAL}}"
- **Inspección inicial en sitio**:
  > "{{TEXTO_REVISION_INICIAL_ORIGINAL}}"
- **Severidad operativa**: `{{NIVEL_SEVERIDAD: Baja | Media | Alta | Crítica}}`
- **Impacto detectado**: {{DESCRIPCION_IMPACTO_OPERATIVO}}

---

## 3. Diagnóstico y Causa Raíz
- **Categoría de falla**: [[FAL-{{SLUG_FALLA}}|{{CATEGORIA_FALLA}}]]
- **Mecanismo o componente afectado**: {{COMPONENTE_ESPECIFICO_AFECTADO}}
- **Causa raíz identificada**:
  {{ANALISIS_CAUSA_RAIZ}}

---

## 4. Procedimiento Técnico Ejecutado
Acciones y maniobras de servicio llevadas a cabo para la resolución de la incidencia:
{{PROCEDIMIENTO_PASO_A_PASO}}

```markdown
1. {{PASO_1}}
2. {{PASO_2}}
3. {{PASO_3}}
```

---

## 5. Repuestos y Materiales Empleados
| Código / Slug | Denominación del Repuesto | Cantidad | Reemplazo previo |
| :--- | :--- | :--- | :--- |
| `{{SLUG_REPUESTO_1}}` | [[PAR-{{SLUG_REPUESTO_1}}\|{{NOMBRE_REPUESTO_1}}]] | {{CANTIDAD_1}} | {{ESTADO_PIEZA_PREVIA}} |

---

## 6. Conclusión Técnica y Estado Final
- **Estado final del equipo**: `{{ESTADO_FINAL: Operativo | En Observación | Inoperativo / Pendiente Repuesto}}`
- **Dictamen del servicio**:
  > "{{TEXTO_CONCLUSION_ORIGINAL}}"

---

## 7. Recomendaciones al Cliente / Mantenimiento
{{RECOMENDACIONES_TECNICAS}}
<!-- Recomendaciones preventivas, intervalos de revisión o cuidados sugeridos. -->

---

## 8. Trazabilidad y Citas del Dato Fuente

> [!NOTE] Metadatos de Auditoría y Respaldo
> - **Archivo de origen**: `limpio/{{NOMBRE_ARCHIVO_LIMPIO}}`
> - **Código de reporte**: `{{NUMERO_REPORTE_ORIGINAL}}`
> - **Hash / Integridad**: Transcripción verificada sin pérdida de campos respecto a la exportación de origen.
> - **Citas directas de respaldo**:
>   - *Motivo*: `[^REP-{{ID_REPORTE}}-MOT]`
>   - *Revisión Inicial*: `[^REP-{{ID_REPORTE}}-REV]`
>   - *Procedimiento*: `[^REP-{{ID_REPORTE}}-PROC]`
>   - *Conclusión*: `[^REP-{{ID_REPORTE}}-CONC]`

[^REP-{{ID_REPORTE}}-MOT]: Campo 'Motivo' del reporte original {{NUMERO_REPORTE_ORIGINAL}}.
[^REP-{{ID_REPORTE}}-REV]: Campo 'Revisión inicial' del reporte original {{NUMERO_REPORTE_ORIGINAL}}.
[^REP-{{ID_REPORTE}}-PROC]: Campo 'Procedimiento' del reporte original {{NUMERO_REPORTE_ORIGINAL}}.
[^REP-{{ID_REPORTE}}-CONC]: Campo 'Conclusión' del reporte original {{NUMERO_REPORTE_ORIGINAL}}.
