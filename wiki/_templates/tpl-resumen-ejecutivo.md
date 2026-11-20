---
type: resumen
id: RES-{{SLUG_PERIODO}}
title: "Informe Ejecutivo de Confiabilidad y Servicios: {{TITULO_PERIODO}}"
aliases:
  - "Resumen Ejecutivo {{TITULO_PERIODO}}"
created: "{{FECHA_CREACION}}"
updated: "{{FECHA_ACTUALIZACION}}"
period_start: "{{FECHA_INICIO_ISO}}"
period_end: "{{FECHA_FIN_ISO}}"
total_reports_analyzed: {{TOTAL_REPORTES}}
tags:
  - resumen-ejecutivo
  - analitica
  - flota
  - periodo/{{SLUG_PERIODO}}
status: approved
---

# 📊 Resumen Ejecutivo: {{TITULO_PERIODO}}

> [!NOTE] Metadatos del Informe
> - **Período analizado**: `{{FECHA_INICIO_ISO}}` al `{{FECHA_FIN_ISO}}`
> - **Volumen de órdenes/reportes**: `{{TOTAL_REPORTES}}` reportes procesados
> - **Tasa de equipos recuperados**: `{{PORCENTAJE_OPERATIVOS}}%`
> - **Navegación general**: [[MOC-resumenes|Índice de Informes Ejecutivos]] | [[MOC-indice-general|MOC General]]

---

## 1. Conclusiones Ejecutivas Principales
{{PARRAFO_SINTESIS_GERENCIAL}}
1. **Comportamiento general**: {{PUNTO_CLAVE_1}}
2. **Cuello de botella / Vulnerabilidad detectada**: {{PUNTO_CLAVE_2}}
3. **Optimización de stock / repuestos**: {{PUNTO_CLAVE_3}}

---

## 2. Métricas Operativas Clave (KPIs)

| Indicador (KPI) | Valor en Período | Tendencia vs Anterior | Meta Operativa |
| :--- | :--- | :--- | :--- |
| Total de Intervenciones | `{{TOTAL_REPORTES}}` | `{{TENDENCIA_VOLUMEN}}` | `{{META_VOLUMEN}}` |
| Tiempo Promedio de Atención (MTTR est.) | `{{MTTR_HORAS}} hrs` | `{{TENDENCIA_MTTR}}` | `< {{META_MTTR}} hrs` |
| Tasa de Servicios en Garantía | `{{PORCENTAJE_GARANTIA}}%` | `{{TENDENCIA_GARANTIA}}` | `< {{META_GARANTIA}}%` |
| Primer Contacto Resuelto (FTFR) | `{{PORCENTAJE_FTFR}}%` | `{{TENDENCIA_FTFR}}` | `> {{META_FTFR}}%` |

---

## 3. Distribución por Modelos de Equipo y Fallas Críticas

### ⚙️ Top Equipos con Mayor Frecuencia de Falla
1. [[EQP-{{SLUG_EQUIPO_1}}|{{NOMBRE_EQUIPO_1}}]]: `{{CANT_CASOS_EQP_1}}` casos (`{{PORC_EQP_1}}%`) — Falla dominante: [[FAL-{{SLUG_FALLA_EQP_1}}]]
2. [[EQP-{{SLUG_EQUIPO_2}}|{{NOMBRE_EQUIPO_2}}]]: `{{CANT_CASOS_EQP_2}}` casos (`{{PORC_EQP_2}}%`) — Falla dominante: [[FAL-{{SLUG_FALLA_EQP_2}}]]

### ⚠️ Top Causas y Síntomas Diagnosticados
1. [[FAL-{{SLUG_FALLA_A}}|{{NOMBRE_FALLA_A}}]]: `{{CANT_FALLA_A}}` ocurrencias. (Referencias: [[REP-{{ID_REP_A1}}]], [[REP-{{ID_REP_A2}}]])
2. [[FAL-{{SLUG_FALLA_B}}|{{NOMBRE_FALLA_B}}]]: `{{CANT_FALLA_B}}` ocurrencias. (Referencias: [[REP-{{ID_REP_B1}}]])

---

## 4. Consumo y Proyección de Repuestos
Top repuestos utilizados durante las intervenciones del período:

| Repuesto / Insumo | Cantidad Utilizada | Costo/Impacto Est. | Reportes de Muestra |
| :--- | :--- | :--- | :--- |
| [[PAR-{{SLUG_REP_1}}\|{{NOMBRE_REP_1}}]] | `{{CANT_REP_1}}` uds | `{{IMPACTO_1}}` | [[REP-{{ID_REP_A1}}]], [[REP-{{ID_REP_A2}}]] |
| [[PAR-{{SLUG_REP_2}}\|{{NOMBRE_REP_2}}]] | `{{CANT_REP_2}}` uds | `{{IMPACTO_2}}` | [[REP-{{ID_REP_B1}}]] |

---

## 5. Recomendaciones Estratégicas y Planes de Acción
- [ ] **Capacitación técnica**: {{ACCION_CAPACITACION}}
- [ ] **Ajuste de inventario**: {{ACCION_STOCK}}
- [ ] **Acción preventiva con clientes**: {{ACCION_CLIENTES}}

---

## 6. Fuentes y Respaldo Documental
Este resumen ejecutivo fue compilado a partir de los reportes técnicos individuales anonimizados:
- Base de datos de origen: `limpio/` (Total `{{TOTAL_REPORTES}}` archivos analizados).
- Auditoría de datos: Trazabilidad completa a través de enlaces [[REP-{{ID_REPORTE_1}}]] a [[REP-{{ID_REPORTE_N}}]].
