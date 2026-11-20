"""Validador de integridad para la base de conocimiento en Markdown (MATRIX).

Comprueba:
1. Convención de nombres de archivos (prefijos normados y kebab-case).
2. Validez de frontmatter YAML y campos obligatorios.
3. Ausencia de placeholders residuales ({{...}}).
4. Integridad de enlaces internos ([[wikilinks]]) y ausencia de links rotos.
5. Detección de notas huérfanas (sin enlaces entrantes o sin enlaces salientes).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

PREFIJOS_VALIDOS = ("REP-", "EQP-", "FAL-", "PAR-", "MOC-", "RES-")
DIRECTORIOS_PERMITIDOS = {
    "reportes": "REP-",
    "equipos": "EQP-",
    "fallas": "FAL-",
    "repuestos": "PAR-",
    "indices": "MOC-",
    "resumenes": "RES-",
}

CAMPOS_OBLIGATORIOS_BASE = ["type", "id", "title", "created", "updated", "tags"]
CAMPOS_OBLIGATORIOS_REPORTE = [
    "service_date",
    "equipment",
    "failure_category",
    "source_report",
    "source_file",
    "anonymized",
]


def extraer_frontmatter(texto: str) -> tuple[dict[str, Any] | None, str]:
    if not texto.startswith("---"):
        return None, "El archivo no inicia con frontmatter YAML ('---')."
    partes = texto.split("---", 2)
    if len(partes) < 3:
        return None, "Bloque frontmatter incompleto (falta el segundo '---')."
    bloque_yaml = partes[1].strip()
    
    # Parser YAML simple para no depender de PyYAML si no está instalado
    metadatos: dict[str, Any] = {}
    lineas = bloque_yaml.splitlines()
    clave_actual: str | None = None
    es_lista = False
    
    for num_linea, linea in enumerate(lineas, start=1):
        linea_str = linea.rstrip()
        if not linea_str or linea_str.strip().startswith("#"):
            continue
        
        # Elemento de lista
        if linea_str.startswith("  - ") or linea_str.startswith("- "):
            if clave_actual:
                valor_item = linea_str.split("-", 1)[1].strip()
                if not isinstance(metadatos.get(clave_actual), list):
                    metadatos[clave_actual] = []
                metadatos[clave_actual].append(valor_item.strip('"\''))
            continue
        
        # Par clave: valor
        if ":" in linea_str:
            partes_kv = linea_str.split(":", 1)
            clave = partes_kv[0].strip()
            valor = partes_kv[1].strip().strip('"\'')
            clave_actual = clave
            
            if valor == "":
                metadatos[clave] = []
            elif valor.lower() == "true":
                metadatos[clave] = True
            elif valor.lower() == "false":
                metadatos[clave] = False
            elif valor.isdigit():
                metadatos[clave] = int(valor)
            else:
                metadatos[clave] = valor
        else:
            return None, f"Línea YAML no reconocida: {linea_str}"
            
    return metadatos, ""


def extraer_wikilinks(texto: str) -> list[str]:
    # Captura enlaces tipo [[destino]], [[destino|alias]], [[destino\|alias]], [[destino#seccion|alias]]
    coincidencias = re.findall(r"\[\[(.*?)\]\]", texto)
    destinos: list[str] = []
    for raw in coincidencias:
        # Reemplazar \| por | por compatibilidad con tablas markdown
        limpio = raw.replace(r"\|", "|")
        destino = limpio.split("|")[0].split("#")[0].strip()
        destino = destino.rstrip("\\").strip()
        if destino:
            # Eliminar extensión .md si la tiene
            if destino.endswith(".md"):
                destino = destino[:-3]
            destinos.append(destino)
    return destinos


def validar_wiki(raiz_wiki: Path) -> int:
    if not raiz_wiki.exists() or not raiz_wiki.is_dir():
        print(f"Error: El directorio {raiz_wiki} no existe.", file=sys.stderr)
        return 1

    errores: list[str] = []
    advertencias: list[str] = []

    archivos_por_nombre: dict[str, Path] = {}
    nombres_sin_ext: set[str] = set()
    todos_los_md: list[Path] = []

    for ruta in raiz_wiki.rglob("*.md"):
        # Ignorar plantillas en la validación de links rotos o placeholders
        if "_templates" in ruta.parts:
            continue
        nombre_sin_ext = ruta.stem
        archivos_por_nombre[nombre_sin_ext] = ruta
        nombres_sin_ext.add(nombre_sin_ext)
        todos_los_md.append(ruta)

    print(f"Analizando {len(todos_los_md)} archivos Markdown en {raiz_wiki}...")

    # Grafo de enlaces
    enlaces_salientes: dict[str, set[str]] = {n: set() for n in nombres_sin_ext}
    enlaces_entrantes: dict[str, set[str]] = {n: set() for n in nombres_sin_ext}

    for ruta in todos_los_md:
        nombre_archivo = ruta.name
        nombre_sin_ext = ruta.stem
        carpeta_padre = ruta.parent.name

        # 1. Validación de Nomenclatura
        prefijo_valido = False
        for p in PREFIJOS_VALIDOS:
            if nombre_archivo.startswith(p):
                prefijo_valido = True
                break
        if not prefijo_valido:
            errores.append(f"[{ruta.name}] Prefijo inválido. Debe iniciar con uno de: {PREFIJOS_VALIDOS}")

        slug_resto = nombre_sin_ext[4:]
        if nombre_archivo.startswith("REP-") and slug_resto.startswith("R-"):
            slug_resto = slug_resto[2:]
        if re.search(r"[A-Z]", slug_resto):
            errores.append(f"[{ruta.name}] El slug contiene letras mayúsculas tras el prefijo. Use kebab-case estricto.")

        if re.search(r"[\s_áéíóúÁÉÍÓÚñÑ]", nombre_archivo):
            errores.append(f"[{ruta.name}] Contiene espacios, tildes, guiones bajos o caracteres prohibidos.")

        # Verificar correspondencia carpeta - prefijo
        prefijo_esperado = DIRECTORIOS_PERMITIDOS.get(carpeta_padre)
        if prefijo_esperado and not nombre_archivo.startswith(prefijo_esperado):
            errores.append(f"[{ruta.name}] Ubicado en carpeta '{carpeta_padre}' pero su nombre no inicia con '{prefijo_esperado}'.")

        contenido = ruta.read_text(encoding="utf-8")

        # 2. Validación de Placeholders residuales
        placeholders = re.findall(r"\{\{[A-Za-z0-9_:-]+\}\}", contenido)
        if placeholders:
            errores.append(f"[{ruta.name}] Contiene placeholders sin resolver: {set(placeholders)}")

        # 3. Validación de Frontmatter
        meta, err_yaml = extraer_frontmatter(contenido)
        if err_yaml:
            errores.append(f"[{ruta.name}] Error en Frontmatter: {err_yaml}")
        elif meta:
            tipo = meta.get("type")
            for campo in CAMPOS_OBLIGATORIOS_BASE:
                if campo not in meta:
                    errores.append(f"[{ruta.name}] Falta campo obligatorio base en frontmatter: '{campo}'")
            if tipo == "reporte":
                for campo in CAMPOS_OBLIGATORIOS_REPORTE:
                    if campo not in meta:
                        errores.append(f"[{ruta.name}] Falta campo obligatorio de reporte: '{campo}'")

        # 4. Extracción de enlaces y validación de links rotos
        destinos = extraer_wikilinks(contenido)
        for dest in destinos:
            enlaces_salientes[nombre_sin_ext].add(dest)
            if dest in nombres_sin_ext:
                enlaces_entrantes[dest].add(nombre_sin_ext)
            else:
                errores.append(f"[{ruta.name}] Enlace roto: [[{dest}]] no apunta a ningún archivo existente.")

    # 5. Detección de páginas huérfanas
    for nombre in nombres_sin_ext:
        # El MOC general puede no tener enlaces entrantes si es la raíz
        if nombre == "MOC-indice-general":
            continue
        if len(enlaces_entrantes[nombre]) == 0:
            advertencias.append(f"[{nombre}] Página huérfana: sin enlaces entrantes (in-links: 0).")
        if len(enlaces_salientes[nombre]) == 0:
            advertencias.append(f"[{nombre}] Callejon sin salida: sin enlaces salientes (out-links: 0).")

    # Resumen
    print("\n--- RESULTADO DE LA VALIDACIÓN ---")
    if advertencias:
        print(f"\n⚠️  Advertencias encontradas ({len(advertencias)}):")
        for adv in advertencias:
            print(f"  - {adv}")

    if errores:
        print(f"\n❌ Errores detectados ({len(errores)}):", file=sys.stderr)
        for err in errores:
            print(f"  - {err}", file=sys.stderr)
        print(f"\nValidación FALLIDA con {len(errores)} errores.", file=sys.stderr)
        return 1

    print(f"\n✅ Validación EXITOSA: 0 errores detectados en {len(todos_los_md)} notas.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--directorio",
        type=Path,
        default=Path("wiki"),
        help="Ruta a la carpeta raíz de la wiki (por defecto: 'wiki').",
    )
    args = parser.parse_args()
    codigo_retorno = validar_wiki(args.directorio)
    sys.exit(codigo_retorno)


if __name__ == "__main__":
    main()
