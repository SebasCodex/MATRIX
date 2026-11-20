---
type: moc
id: MOC-{{SLUG_MOC}}
title: "MOC: {{TITULO_MAPA_CONTENIDO}}"
created: "{{FECHA_CREACION}}"
updated: "{{FECHA_ACTUALIZACION}}"
category: "{{CATEGORIA_MOC: general | equipos | fallas | repuestos | cronologico}}"
tags:
  - moc
  - indice
  - "{{CATEGORIA_TAG}}"
status: active
---

# 🗺️ MOC: {{TITULO_MAPA_CONTENIDO}}

> [!ABSTRACT] Propósito del MOC
> {{DESCRIPCION_PROPOSITO_MOC}}
> Este mapa de contenido agrupa de forma centralizada todas las notas relacionadas con **{{TEMA_PRINCIPAL}}**, garantizando que ninguna nota quede huérfana en el grafo de conocimiento.

---

## 🧭 Navegación Superior
- Retorno al nivel superior: [[MOC-indice-general|MOC General — MATRIX]]
- MOCs hermanos:
  - [[MOC-equipos|Catálogo de Equipos]]
  - [[MOC-fallas|Catálogo de Fallas]]
  - [[MOC-reportes|Base de Reportes]]

---

## 📊 Métricas del Dominio
- **Total de elementos catalogados**: `{{CANTIDAD_ELEMENTOS}}`
- **Última actualización de ingesta**: `{{FECHA_ULTIMA_ACTUALIZACION}}`
- **Tasa de cobertura**: `{{PORCENTAJE_COBERTURA}}%`

---

## 🗂️ Categorías y Agrupaciones Principales

### {{GRUPO_1_TITULO}}
{{DESCRIPCION_GRUPO_1}}
- [[{{PREFIJO}}-{{SLUG_ELEMENTO_1}}|{{NOMBRE_ELEMENTO_1}}]] — {{BREVE_DESCRIPCION_1}}
- [[{{PREFIJO}}-{{SLUG_ELEMENTO_2}}|{{NOMBRE_ELEMENTO_2}}]] — {{BREVE_DESCRIPCION_2}}
- [[{{PREFIJO}}-{{SLUG_ELEMENTO_3}}|{{NOMBRE_ELEMENTO_3}}]] — {{BREVE_DESCRIPCION_3}}

### {{GRUPO_2_TITULO}}
{{DESCRIPCION_GRUPO_2}}
- [[{{PREFIJO}}-{{SLUG_ELEMENTO_4}}|{{NOMBRE_ELEMENTO_4}}]] — {{BREVE_DESCRIPCION_4}}
- [[{{PREFIJO}}-{{SLUG_ELEMENTO_5}}|{{NOMBRE_ELEMENTO_5}}]] — {{BREVE_DESCRIPCION_5}}

---

## 📋 Lista Maestra de Notas Vinculadas (Dataview / Estática)

| Código | Nota / Entidad | Categoría | Última Intervención | Total Reportes |
| :--- | :--- | :--- | :--- | :--- |
| `{{CODIGO_1}}` | [[{{PREFIJO}}-{{SLUG_1}}\|{{NOMBRE_1}}]] | `{{CATEGORIA_1}}` | `{{ULTIMA_FECHA_1}}` | `{{TOTAL_REVIEWS_1}}` |
| `{{CODIGO_2}}` | [[{{PREFIJO}}-{{SLUG_2}}\|{{NOMBRE_2}}]] | `{{CATEGORIA_2}}` | `{{ULTIMA_FECHA_2}}` | `{{TOTAL_REVIEWS_2}}` |

```dataview
TABLE file.mtime AS "Modificado", tags AS "Etiquetas"
FROM "{{CARPETA_DESTINO}}"
SORT file.name ASC
```

---
*MOC generado para el grafo de conocimiento de MATRIX. Mantener actualizado durante cada ciclo de ingesta.*
