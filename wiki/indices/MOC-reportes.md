---
type: moc
id: MOC-reportes
title: "MOC: Registro Maestro de Reportes Técnicos"
created: 2026-11-20
updated: 2026-11-20
category: reportes
tags:
  - moc
  - indice
  - reportes
status: active
---

# 📋 MOC: Registro Maestro de Reportes Técnicos

> [!INFO] Propósito del MOC
> Este índice organiza cronológicamente y por código todas las intervenciones de servicio técnico individualizadas.

---

## 🧭 Navegación
- Retorno al índice superior: [[MOC-indice-general|MOC Maestro]]
- Relacionados: [[MOC-equipos|Catálogo de Equipos]] | [[MOC-fallas|Catálogo de Fallas]]

---

## 🗂️ Registro de Intervenciones Ingeridas

### Lote Piloto / Inicial
- [[REP-R-000001|Reporte R-000001]] — Intervención inicial en [[EQP-bomba-mx-200|Bomba MX-200]].

---

## 📊 Explorador de Reportes (Obsidian Dataview)
```dataview
TABLE service_date AS "Fecha", equipment AS "Equipo", failure_category AS "Falla", technician_id AS "Técnico"
FROM "wiki/reportes"
SORT service_date DESC
```
