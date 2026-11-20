# SOP-03: Procedimiento Operativo Estándar de Revisión y Auditoría de Calidad

---
codigo: SOP-MTX-03
version: 1.0.0
fecha: 2026-11-20
estado: aprobado
proposito: Establecer el protocolo de control de calidad, verificación de integridad del grafo y validación de citas y metadatos.
responsable: Coordinador de Wiki / Auditor Técnico
---

## 1. Objetivo y Alcance
Este procedimiento establece los controles de calidad sistemáticos que deben ejecutarse tras cada ciclo de ingesta o modificación en la base de conocimiento **MATRIX**. Su propósito es certificar que la wiki mantenga cero enlaces rotos, cero páginas huérfanas, metadatos YAML válidos, anonimización total de PII y trazabilidad absoluta hacia los reportes fuente.

---

## 2. Checklist de Validación Multidimensional

Antes de considerar cerrada una ingesta o actualización de la wiki, se debe verificar el cumplimiento del 100% de los siguientes puntos:

### A. Cumplimiento de Nomenclatura y Estructura
- [ ] **Prefijos Válidos**: Todo archivo en `wiki/` utiliza uno de los prefijos normados (`REP-`, `EQP-`, `FAL-`, `PAR-`, `MOC-`, `RES-`).
- [ ] **Kebab-Case Estricto**: No existen espacios, mayúsculas en el cuerpo del slug, tildes ni caracteres especiales (`ñ`, `/`, `\`, etc.).
- [ ] **Ubicación Correcta**: Cada archivo reside en su subdirectorio correspondiente (`wiki/reportes/`, `wiki/equipos/`, etc.).

### B. Integridad de Metadatos YAML (Frontmatter)
- [ ] **Apertura y Cierre Válidos**: El bloque inicia y culmina con `---` exactos.
- [ ] **Campos Obligatorios Presentes**:
  - `type`
  - `id`
  - `title`
  - `created`
  - `updated`
  - `tags`
  - `anonymized: true`
- [ ] **Sin Placeholders Residuales**: Ningún archivo contiene variables sin rellenar (ej. `{{ID_REPORTE}}`).

### C. Conectividad del Grafo y Enlaces Internos
- [ ] **Cero Enlaces Rotos**: Todos los `[[wikilinks]]` apuntan a archivos existentes en la wiki o MOCs definidos.
- [ ] **Cero Páginas Huérfanas**:
  - Ninguna nota tiene cero enlaces entrantes (*in-links*).
  - Ninguna nota tiene cero enlaces salientes (*out-links*).
- [ ] **Uso de Aliases**: Los enlaces contextuales usan la sintaxis `[[destino|Texto Descriptivo]]`.

### D. Trazabilidad Forense y Citas de Origen
- [ ] **Sección de Trazabilidad Presente**: Toda nota en `reportes/` contiene la sección `## Trazabilidad y Fuentes`.
- [ ] **Archivo Fuente Existente**: El archivo indicado en `source_file` existe en la carpeta `limpio/`.
- [ ] **Notas al Pie Completas**: Cada afirmación técnica de diagnóstico, procedimiento o conclusión cuenta con su footnote de respaldo.

### E. Privacidad y Anonimización (Zero-PII)
- [ ] **Sin Nombres Propios**: Ningún cliente o empleado figura con su nombre real (usar códigos `CLI-XXXX` y `TEC-XX`).
- [ ] **Sin Teléfonos o Correos Reales**: Se verificó la ausencia de cadenas con patrones telefónicos o dominios de correo de clientes reales.

---

## 3. Automatización de la Revisión (`scripts/validar_wiki.py`)

Para agilizar y objetivar el control de calidad, el repositorio cuenta con un script de auditoría automatizada.

### Comando de Ejecución:
```powershell
python scripts/validar_wiki.py
```

### Comprobaciones Automatizadas por el Script:
1. **Sintaxis YAML**: Parsea el frontmatter de todos los `.md` en `wiki/` y reporta errores de formato.
2. **Convención de Nombres**: Detecta archivos con mayúsculas ilegales, espacios, caracteres prohibidos o prefijos desconocidos.
3. **Validación de Enlaces (Broken Links)**: Escanea todas las referencias `[[...]]` y verifica la existencia física del archivo destino.
4. **Detección de Nodos Huérfanos**: Construye la matriz de adyacencia del grafo e identifica notas sin conexiones.
5. **Detección de Placeholders**: Alerta si persisten cadenas con patrón `{{...}}`.

---

## 4. Gestión de No Conformidades y Corrección

En caso de que el script o la revisión manual arroje fallas:

| Tipo de Falla | Causa Típica | Acción Correctiva Inmediata |
| :--- | :--- | :--- |
| **Enlace Roto** | Wikilink apunta a entidad no creada aún | Crear la ficha faltante en `equipos/` o `fallas/` usando la plantilla base. |
| **Nota Huérfana** | Reporte no fue indexado en su MOC | Agregar el enlace en el MOC temático correspondiente (`wiki/indices/`). |
| **Placeholder Residual** | Omisión del LLM durante la ingesta | Completar manualmente el campo o solicitar reingesta del fragmento. |
| **Falla YAML** | Indentación incorrecta en listas | Corregir los espacios a 2 niveles estándar en el archivo YAML. |

---

## 5. Criterio de Pase a Producción (Definition of Done)
Se considera que la wiki está en estado **Aprobado / Verified** cuando:
1. La ejecución de `python scripts/validar_wiki.py` termina con código de salida `0` y `0 errores reportados`.
2. El informe de entrega o registro de auditoría queda firmado y fechado en `docs/entregas/`.
