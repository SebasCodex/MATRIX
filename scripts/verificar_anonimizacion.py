"""Busca información identificable en fuentes y permite revertir códigos autorizados."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from anonimizar import (
    COLUMNAS_REPORTES,
    COLUMNAS_TABLA,
    leer_csv_privado,
)
from privacidad import clave_empresa, telefonos_en
from comun import normalizar


EXTENSIONES_TEXTO = {
    ".md", ".txt", ".csv", ".json", ".html", ".htm", ".rst", ".yaml", ".yml", ".xml",
}


def revertir_codigo(codigo: str, reporte: str, directorio_privado: Path) -> int:
    ruta = directorio_privado / "reportes_codigos.csv"
    if not ruta.is_file():
        raise ValueError(f"No existe el mapa privado de reportes: {ruta}")
    filas = leer_csv_privado(ruta, COLUMNAS_REPORTES)
    coincidencias = [
        fila for fila in filas
        if fila["codigo"].casefold() == codigo.casefold()
        and fila["reporte"].casefold() == reporte.casefold()
    ]
    if not coincidencias:
        print(
            f"No existe el código {codigo} asociado al reporte {reporte}.",
            file=sys.stderr,
        )
        return 1
    valores = {fila["valor_real"] for fila in coincidencias}
    if len(valores) != 1:
        raise ValueError(f"El par {codigo}/{reporte} tiene más de un dato reversible.")
    print(next(iter(valores)))
    return 0


def archivos_texto(raiz: Path) -> list[Path]:
    if not raiz.is_dir():
        raise ValueError(f"No existe la carpeta que se debe verificar: {raiz}")
    return sorted(
        ruta for ruta in raiz.rglob("*")
        if ruta.is_file() and ruta.suffix.lower() in EXTENSIONES_TEXTO
    )


def claves_de_busqueda(filas: list[dict[str, str]]) -> list[tuple[str, str, str]]:
    valores: set[tuple[str, str, str]] = set()
    for fila in filas:
        dato = fila["valor_original"].strip()
        if not dato:
            continue
        tipo = fila["tipo"]
        if tipo == "cliente":
            base = clave_empresa(dato)
            if base:
                valores.add((tipo, base, "texto"))
        elif tipo == "cliente_alias":
            base = clave_empresa(dato)
            if base:
                valores.add(("cliente", base, "texto"))
        elif tipo == "telefono":
            digitos = "".join(caracter for caracter in dato if caracter.isdigit())
            if len(digitos) >= 8:
                valores.add((tipo, digitos, "telefono"))
        else:
            normalizado = normalizar(dato)
            if normalizado:
                valores.add((tipo, normalizado, "texto"))
    return sorted(valores)


def verificar(directorio_fuentes: Path, directorio_privado: Path, raiz_wiki: Path) -> int:
    ruta_tabla = directorio_privado / "tabla_codigos.csv"
    if not ruta_tabla.is_file():
        raise ValueError(f"No existe la tabla privada de códigos: {ruta_tabla}")
    tabla = leer_csv_privado(ruta_tabla, COLUMNAS_TABLA)
    candidatos = claves_de_busqueda(tabla)
    raices = [directorio_fuentes]
    raices.extend(
        ruta for ruta in raiz_wiki.glob("wiki-*")
        if ruta.is_dir() and ruta != directorio_fuentes
    )
    archivos = [
        (raiz, archivo)
        for raiz in raices
        for archivo in archivos_texto(raiz)
    ]
    if not archivos:
        raise ValueError("No hay archivos de texto que verificar.")
    hallazgos: set[tuple[Path, str]] = set()

    for raiz, archivo in archivos:
        contenido = archivo.read_text(encoding="utf-8")
        contenido_verificable = contenido + "\n" + archivo.relative_to(raiz).as_posix()
        normalizado = normalizar(contenido_verificable)
        telefonos = {
            "".join(caracter for caracter in numero if caracter.isdigit())
            for numero in telefonos_en(contenido_verificable)
        }
        for tipo, dato, metodo in candidatos:
            encontrado = dato in telefonos if metodo == "telefono" else dato in normalizado
            if encontrado:
                hallazgos.add((archivo, tipo))

    if hallazgos:
        for archivo, tipo in sorted(hallazgos):
            print(f"Coincidencia: {archivo} (tipo: {tipo})")
        print(f"Verificación fallida: {len(hallazgos)} coincidencias.", file=sys.stderr)
        return 1
    print(f"Verificación correcta: 0 coincidencias en {len(archivos)} archivos.")
    return 0


def main(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fuentes", type=Path, default=Path("fuentes"))
    parser.add_argument("--datos-privados", type=Path, default=Path("datos_privados"))
    parser.add_argument("--raiz-wiki", type=Path, default=Path("."))
    parser.add_argument("--revertir", nargs=2, metavar=("CODIGO", "REPORTE"))
    opciones = parser.parse_args(argumentos)
    try:
        if opciones.revertir:
            codigo, reporte = opciones.revertir
            return revertir_codigo(codigo, reporte, opciones.datos_privados)
        return verificar(opciones.fuentes, opciones.datos_privados, opciones.raiz_wiki)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
