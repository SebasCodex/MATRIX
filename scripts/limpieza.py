"""Convierte exportaciones de RP-TECH en un Markdown por reporte."""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from comun import (
    NOMBRES_CAMPOS,
    campo_canonico,
    contenido_legal,
    encabezado_excluible,
    es_vacio,
    fecha_iso,
    leer_exportacion,
    leer_markdown,
    normalizar,
    renderizar_markdown,
    texto,
)


def contador_tokens(contenido: str) -> tuple[int, str]:
    try:
        import tiktoken
    except ImportError:
        return (math.ceil(len(contenido) / 4), "caracteres/4 (estimado)")
    codificacion = tiktoken.get_encoding("cl100k_base")
    return (len(codificacion.encode(contenido)), "tiktoken cl100k_base")


def nombre_archivo(reporte: str) -> str:
    limpio = re.sub(r"[^A-Za-z0-9._-]+", "-", reporte.strip()).strip("-.")
    if not limpio:
        raise ValueError("El número de reporte no puede convertirse en nombre de archivo.")
    if limpio.isdigit():
        limpio = f"R-{limpio.zfill(6)}"
    elif not limpio.upper().startswith("R-"):
        limpio = f"R-{limpio}"
    return limpio + ".md"


def valores_equivalentes(valor: str, etiqueta: str) -> str:
    return normalizar(fecha_iso(valor) if etiqueta == "fecha" else valor)


def procesar(ruta: Path, salida: Path, maximo: int | None) -> int:
    hojas = leer_exportacion(ruta)
    filas: list[tuple[str, list[tuple[str, str]], str, str]] = []
    for nombre_hoja, tabla in hojas:
        for numero_fila, (_, fila) in enumerate(tabla.iterrows(), start=2):
            originales = [
                f"{encabezado}: {texto(valor)}"
                for encabezado, valor in fila.items()
                if not es_vacio(valor)
            ]
            if not originales:
                continue
            campos: list[tuple[str, str]] = []
            reporte: str | None = None
            for encabezado, valor in fila.items():
                if es_vacio(valor) or encabezado_excluible(encabezado):
                    continue
                contenido = texto(valor)
                if contenido_legal(contenido):
                    continue
                canonico = campo_canonico(encabezado)
                if canonico == "fecha":
                    contenido = fecha_iso(valor)
                etiqueta = NOMBRES_CAMPOS.get(canonico, str(encabezado).strip())
                campos.append((etiqueta, contenido))
                if canonico == "reporte":
                    reporte = contenido
            if not campos:
                continue
            if not reporte:
                raise ValueError(
                    f"La hoja {nombre_hoja!r}, fila {numero_fila}, no tiene número de reporte."
                )
            filas.append((reporte, campos, "\n".join(originales), nombre_hoja))

    if maximo is not None:
        filas = filas[:maximo]
    if not filas:
        raise ValueError("La exportación no contiene reportes con campos poblados.")

    salida.mkdir(parents=True, exist_ok=True)
    nombres_vistos: set[str] = set()
    fallos: set[str] = set()
    total_entrada = 0
    total_salida = 0
    tokens_antes = 0
    tokens_despues = 0
    metodo_tokens = ""
    tabla_tokens: list[tuple[str, int, int]] = []

    for reporte, campos, entrada_cruda, hoja in filas:
        nombre = nombre_archivo(reporte)
        if nombre.casefold() in nombres_vistos:
            raise ValueError(f"Número de reporte duplicado: {reporte!r} (hoja {hoja}).")
        nombres_vistos.add(nombre.casefold())
        markdown = renderizar_markdown(campos)
        destino = salida / nombre
        destino.write_text(markdown, encoding="utf-8")

        conteo_entrada = Counter(
            (normalizar(etiqueta), valores_equivalentes(valor, campo_canonico(etiqueta)))
            for etiqueta, valor in campos
        )
        campos_leidos = leer_markdown(destino)
        conteo_salida = Counter(
            (normalizar(etiqueta), valores_equivalentes(valor, campo_canonico(etiqueta)))
            for etiqueta, valor in campos_leidos
        )
        perdidos = conteo_entrada - conteo_salida
        if perdidos:
            fallos.add(reporte)

        total_entrada += sum(conteo_entrada.values())
        total_salida += sum(conteo_salida.values())
        antes, metodo_tokens = contador_tokens(entrada_cruda)
        despues, metodo_tokens = contador_tokens(markdown)
        tokens_antes += antes
        tokens_despues += despues
        tabla_tokens.append((reporte, antes, despues))

    if fallos:
        print(
            "Error: se perdieron campos con contenido en los reportes: "
            + ", ".join(sorted(fallos)),
            file=sys.stderr,
        )
        return 1

    print(f"Reportes procesados: {len(filas)}")
    print(f"Campos con contenido: entrada={total_entrada}, salida={total_salida}, perdidos=0")
    print(f"Tokens ({metodo_tokens}):")
    print("| Reporte | Antes | Después |")
    print("|---|---:|---:|")
    for reporte, antes, despues in tabla_tokens:
        print(f"| {reporte} | {antes} | {despues} |")
    print(f"| TOTAL | {tokens_antes} | {tokens_despues} |")
    if tokens_antes:
        reduccion = (tokens_antes - tokens_despues) * 100 / tokens_antes
        print(f"Reducción estimada: {reduccion:.1f}%")
    return 0


def main(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path, help="Exportación .xlsx, .xls o .csv")
    parser.add_argument("--salida", type=Path, default=Path("limpio"))
    parser.add_argument("--max", dest="maximo", type=int)
    opciones = parser.parse_args(argumentos)
    if opciones.maximo is not None and opciones.maximo < 1:
        parser.error("--max debe ser un entero positivo.")
    if not opciones.entrada.is_file():
        parser.error(f"No existe el archivo de entrada: {opciones.entrada}")
    try:
        return procesar(opciones.entrada, opciones.salida, opciones.maximo)
    except (OSError, ValueError, ImportError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
