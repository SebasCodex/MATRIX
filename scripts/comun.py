"""Utilidades compartidas para procesar reportes RP-TECH."""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd


ALIAS = {
    "reporte": [
        "numero de reporte", "número de reporte", "nro reporte", "n° reporte",
        "no reporte", "reporte", "orden de servicio", "numero de servicio",
        "número de servicio", "id reporte",
    ],
    "fecha": ["fecha", "fecha de servicio", "fecha del reporte"],
    "tecnico": ["tecnico", "técnico", "tecnico responsable", "tecnico de servicio"],
    "cliente": ["cliente", "empresa", "cliente/empresa", "razon social", "razón social"],
    "modelo": ["equipo", "modelo", "modelo de equipo", "equipo (modelo)", "marca y modelo"],
    "serie": ["serie", "numero de serie", "número de serie", "n° de serie", "serial"],
    "motivo": ["motivo", "motivo de servicio", "solicitud", "falla reportada"],
    "revision_inicial": [
        "revision inicial", "revisión inicial", "diagnostico inicial",
        "diagnóstico inicial", "inspeccion inicial", "inspección inicial",
    ],
    "procedimiento": ["procedimiento", "trabajo realizado", "servicio realizado"],
    "conclusion": ["conclusion", "conclusión", "resultado", "diagnostico final", "diagnóstico final"],
    "recomendaciones": ["recomendaciones", "recomendacion", "recomendación"],
    "repuestos": ["repuestos", "repuestos utilizados", "materiales", "partes utilizadas"],
    "hora_llegada": ["hora de llegada", "hora llegada", "llegada"],
    "hora_salida": ["hora de salida", "hora salida", "salida"],
    "garantia": ["garantia", "garantía", "en garantia", "en garantía"],
    "facturado": ["facturado", "factura", "estado de facturacion", "estado de facturación"],
    "telefono": ["telefono", "teléfono", "celular", "movil", "móvil", "telefono cliente"],
    "correo": ["correo", "email", "e-mail", "correo electronico", "correo electrónico"],
    "contacto": ["contacto", "persona de contacto", "nombre de contacto", "atendido por"],
    "direccion": ["direccion", "dirección", "domicilio", "direccion del cliente", "dirección del cliente"],
    "firma": ["firma", "firma del cliente", "firma de conformidad"],
}

NOMBRES_CAMPOS = {
    "reporte": "Número de reporte",
    "fecha": "Fecha",
    "tecnico": "Técnico",
    "cliente": "Cliente/empresa",
    "modelo": "Equipo (modelo)",
    "serie": "Serie",
    "motivo": "Motivo",
    "revision_inicial": "Revisión inicial",
    "procedimiento": "Procedimiento",
    "conclusion": "Conclusión",
    "recomendaciones": "Recomendaciones",
    "repuestos": "Repuestos",
    "hora_llegada": "Hora de llegada",
    "hora_salida": "Hora de salida",
    "garantia": "Garantía",
    "facturado": "Facturado",
    "telefono": "Teléfono",
    "correo": "Correo electrónico",
    "contacto": "Contacto",
    "direccion": "Dirección",
    "firma": "Firma",
}

VACIOS = {"", "-", "--", "n/a", "na", "null", "none", "nan", "☐", "□"}


def quitar_acentos(valor: str) -> str:
    return "".join(
        caracter for caracter in unicodedata.normalize("NFKD", valor)
        if not unicodedata.combining(caracter)
    )


_ALIAS_NORMALIZADOS = {
    normalizado: campo
    for campo, alias in ALIAS.items()
    for valor in [campo, *alias]
    for normalizado in [re.sub(r"\s+", " ", quitar_acentos(valor).lower()).strip()]
}
_COLUMNAS_LEGALES = (
    "aviso legal", "texto legal", "terminos y condiciones", "pie de pagina",
    "footer", "legal", "casilla", "checkbox",
)


def normalizar(valor: Any) -> str:
    texto = "" if valor is None else str(valor)
    return re.sub(r"\s+", " ", quitar_acentos(texto).lower()).strip()


def es_vacio(valor: Any) -> bool:
    if valor is None:
        return True
    if not isinstance(valor, (str, bytes)):
        try:
            if pd.isna(valor):
                return True
        except (TypeError, ValueError):
            pass
    texto = str(valor).strip()
    return normalizar(texto) in VACIOS or bool(re.fullmatch(r"[☐□\s]+", texto))


def texto(valor: Any) -> str:
    if isinstance(valor, (datetime, date, pd.Timestamp)):
        return valor.isoformat()
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()


def fecha_iso(valor: Any) -> str:
    if isinstance(valor, (datetime, date, pd.Timestamp)):
        return valor.strftime("%Y-%m-%d")
    bruto = str(valor).strip()
    es_iso = bool(re.match(r"^\d{4}-\d{2}-\d{2}(?:$|[ T])", bruto))
    convertido = pd.to_datetime(bruto, dayfirst=not es_iso, errors="coerce")
    if pd.isna(convertido):
        return texto(valor)
    return convertido.strftime("%Y-%m-%d")


def campo_canonico(encabezado: Any) -> str:
    bruto = str(encabezado).strip()
    clave = re.sub(r"\s+", " ", quitar_acentos(bruto).lower()).strip()
    return _ALIAS_NORMALIZADOS.get(clave, bruto)


def encabezado_excluible(encabezado: Any) -> bool:
    clave = normalizar(encabezado)
    if not clave or clave.startswith("unnamed:") or clave.startswith("sin nombre"):
        return True
    return any(indicador in clave for indicador in _COLUMNAS_LEGALES)


def contenido_legal(valor: str) -> bool:
    clave = normalizar(valor)
    frases = (
        "aviso legal", "terminos y condiciones", "todos los derechos reservados",
        "politica de privacidad", "proteccion de datos personales",
        "documento generado automaticamente por rp-tech",
    )
    return any(frase in clave for frase in frases)


def leer_exportacion(ruta: Path) -> list[tuple[str, pd.DataFrame]]:
    extension = ruta.suffix.lower()
    if extension == ".csv":
        return [("CSV", pd.read_csv(
            ruta, dtype=object, keep_default_na=False, encoding="utf-8-sig",
            sep=None, engine="python",
        ))]
    if extension not in {".xlsx", ".xls"}:
        raise ValueError("Formato no compatible. Use un archivo .xlsx, .xls o .csv.")
    hojas = pd.read_excel(ruta, sheet_name=None, dtype=object, keep_default_na=False)
    return list(hojas.items())


def leer_markdown(ruta: Path) -> list[tuple[str, str]]:
    campos: list[tuple[str, str]] = []
    actual: int | None = None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        coincidencia = re.match(r"^- \*\*(.+?)\*\*: ?(.*)$", linea)
        if coincidencia:
            campos.append((coincidencia.group(1), coincidencia.group(2)))
            actual = len(campos) - 1
        elif actual is not None and linea.startswith("  "):
            etiqueta, valor = campos[actual]
            campos[actual] = (etiqueta, valor + "\n" + linea[2:])
    return campos


def renderizar_markdown(campos: list[tuple[str, str]]) -> str:
    lineas = ["# Reporte de servicio"]
    for etiqueta, valor in campos:
        lineas.append(f"- **{etiqueta}**: {valor.replace(chr(10), chr(10) + '  ')}")
    return "\n".join(lineas) + "\n"
