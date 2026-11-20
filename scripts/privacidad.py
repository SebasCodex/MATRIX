"""Funciones de detección y sustitución de información identificable."""

from __future__ import annotations

import re
from collections.abc import Iterable

from comun import normalizar


_SUFIJO_EMPRESA = re.compile(
    r"\s+(?:s\.?\s*a\.?\s*c\.?|s\.?\s*r\.?\s*l\.?|s\.?\s*a\.?|"
    r"s\.?\s*a\.?\s*s\.?|e\.?\s*i\.?\s*r\.?\s*l\.?)$",
    re.IGNORECASE,
)
_PATRON_FECHA = re.compile(
    r"\b(?:\d{4}-\d{1,2}-\d{1,2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})\b"
)
_PATRON_TELEFONO = re.compile(r"(?<!\w)\+?\d(?:[\d().\s-]{5,}\d)(?!\w)")
_PATRON_CORREO = re.compile(
    r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w-])",
    re.IGNORECASE,
)
_VARIANTES_LETRAS = {
    "a": "aáàäâã", "e": "eéèëê", "i": "iíìïî", "o": "oóòöôõ",
    "u": "uúùüû", "n": "nñ",
}
_SUFIJO_FLEXIBLE = (
    r"(?:\s*(?:s\.?\s*a\.?\s*c\.?|s\.?\s*r\.?\s*l\.?|s\.?\s*a\.?|"
    r"s\.?\s*a\.?\s*s\.?|e\.?\s*i\.?\s*r\.?\s*l\.?))?"
)


def clave_empresa(valor: str) -> str:
    return _SUFIJO_EMPRESA.sub("", normalizar(valor)).strip()


def patron_flexible(valor: str, sufijo_empresa: bool = False) -> re.Pattern[str] | None:
    base = clave_empresa(valor) if sufijo_empresa else normalizar(valor)
    if not base:
        return None
    partes: list[str] = []
    for caracter in base:
        if caracter.isspace():
            partes.append(r"\s+")
        elif caracter in _VARIANTES_LETRAS:
            partes.append("[" + re.escape(_VARIANTES_LETRAS[caracter]) + "]")
        else:
            partes.append(re.escape(caracter))
    sufijo = _SUFIJO_FLEXIBLE if sufijo_empresa else ""
    return re.compile(r"(?<!\w)" + "".join(partes) + sufijo + r"(?!\w)", re.IGNORECASE)


def telefonos_en(texto: str) -> list[str]:
    encontrados = []
    for coincidencia in _PATRON_TELEFONO.finditer(texto):
        candidato = coincidencia.group(0).strip()
        if _PATRON_FECHA.fullmatch(candidato):
            continue
        if sum(caracter.isdigit() for caracter in candidato) >= 8:
            encontrados.append(candidato)
    return encontrados


def correos_en(texto: str) -> list[str]:
    return [coincidencia.group(0) for coincidencia in _PATRON_CORREO.finditer(texto)]


def sanear_texto(texto: str, reemplazos: Iterable[tuple[str, str, bool]]) -> str:
    fechas: list[str] = []

    def proteger_fecha(coincidencia: re.Match[str]) -> str:
        fechas.append(coincidencia.group(0))
        return f"\uE000{len(fechas) - 1}\uE001"

    resultado = _PATRON_FECHA.sub(proteger_fecha, texto)
    for dato, sustitucion, es_empresa in sorted(
        reemplazos, key=lambda elemento: len(elemento[0]), reverse=True
    ):
        if not dato or (dato.isdigit() and len(dato) < 8):
            continue
        patron = patron_flexible(dato, sufijo_empresa=es_empresa)
        if patron:
            resultado = patron.sub(sustitucion, resultado)
    resultado = _PATRON_CORREO.sub("", resultado)

    def borrar_telefono(coincidencia: re.Match[str]) -> str:
        candidato = coincidencia.group(0)
        if sum(caracter.isdigit() for caracter in candidato) >= 8:
            return ""
        return candidato

    resultado = _PATRON_TELEFONO.sub(borrar_telefono, resultado)
    for indice, fecha in enumerate(fechas):
        resultado = resultado.replace(f"\uE000{indice}\uE001", fecha)
    return resultado
