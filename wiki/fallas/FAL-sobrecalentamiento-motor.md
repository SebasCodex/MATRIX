---
type: falla
id: FAL-sobrecalentamiento-motor
title: "Diagnóstico: Sobrecalentamiento de Motor"
aliases:
  - "Sobrecalentamiento de Motor"
  - "Temperatura anómala en carcasa"
created: 2026-11-20
updated: 2026-11-20
system_affected: "Mecánico"
typical_severity: "Media"
recurrence_rate: "Frecuente"
tags:
  - entidad
  - diagnostico
  - falla
  - sistema/mecanico
status: active
---

# ⚠️ Falla / Síntoma: Sobrecalentamiento de Motor

> [!WARNING] Alerta de Diagnóstico
> - **Sistema Afectado**: `Mecánico / Eléctrico`
> - **Severidad Típica**: `Media`
> - **Índice Superior**: [[MOC-fallas|Catálogo Taxonómico de Fallas]]
> - **Tiempo promedio de resolución**: `1.5 horas`

---

## 1. Descripción del Síntoma y Manifestación
El cliente reporta elevación excesiva de temperatura en la superficie del estator o paradas térmicas intempestivas mediante relé de protección.

---

## 2. Árbol de Decisión y Diagnóstico Diferencial

```mermaid
flowchart TD
    S["Síntoma: Sobrecalentamiento"] --> C1{"¿Rejilla de ventilador bloqueada?"}
    C1 -- Sí --> R1["Limpiar cubierta y aletas disipadoras"]
    C1 -- No --> C2{"¿Presión diferencial de filtro alta?"}
    C2 -- Sí --> R2["Reemplazar [[PAR-filtro-sintetico-fs-01|Filtro FS-01]]"]
    C2 -- No --> R3["Verificar consumo eléctrico y rodamientos"]
```

---

## 3. Matriz de Causas Raíz y Soluciones Validadas en Campo

| Causa Raíz Identificada | Procedimiento de Corrección Comprobado | Repuestos Habituales | Fuente de Validación |
| :--- | :--- | :--- | :--- |
| Saturación de flujo en succión | Limpieza de línea y cambio de elemento | [[PAR-filtro-sintetico-fs-01\|Filtro sintético FS-01]] | [[REP-R-000001]] |

---

## 4. Equipos y Modelos Más Afectados
- [[EQP-bomba-mx-200|Bomba MX-200]] (1 caso registrado)

---

## 5. Casos de Referencia Documentados
- [[REP-R-000001|Reporte R-000001]] en [[EQP-bomba-mx-200]]: Reemplazo de filtro por elevación térmica. [^REP-R-000001]

---

## 6. Trazabilidad y Citas
[^REP-R-000001]: Intervención confirmada en `limpio/R-000001.md`, campos 'Motivo' y 'Procedimiento'.
