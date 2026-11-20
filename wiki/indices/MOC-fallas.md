---
type: moc
id: MOC-fallas
title: "MOC: Catálogo Taxonómico de Fallas y Diagnósticos"
created: 2026-11-20
updated: 2026-11-20
category: fallas
tags:
  - moc
  - indice
  - fallas
  - diagnosticos
status: active
---

# ⚠️ MOC: Catálogo Taxonómico de Fallas y Diagnósticos

> [!INFO] Propósito del MOC
> Este índice organiza las anomalías, síntomas y diagnósticos técnicos clasificados en las atenciones de campo.

---

## 🧭 Navegación
- Retorno al índice superior: [[MOC-indice-general|MOC Maestro]]
- Relacionados: [[MOC-equipos|Catálogo de Equipos]] | [[MOC-reportes|Base de Reportes]]

---

## 🗂️ Taxonomía por Sistema Afectado

### Sistema Mecánico e Hidráulico
- [[FAL-sobrecalentamiento-motor|Sobrecalentamiento de motor / unidad de potencia]] — Elevación térmica anómala por sobrecarga o fricción.

---

## 📊 Matriz de Diagnósticos y Severidad
*Lista dinámica en Obsidian:*
```dataview
TABLE system_affected AS "Sistema", typical_severity AS "Severidad", recurrence_rate AS "Recurrencia"
FROM "wiki/fallas"
SORT file.name ASC
```
