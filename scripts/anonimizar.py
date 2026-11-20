"""Anonimiza los reportes limpios y mantiene los códigos localmente."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from comun import (
    NOMBRES_CAMPOS,
    campo_canonico,
    leer_markdown,
    renderizar_markdown,
)
from privacidad import (
    clave_empresa,
    correos_en,
    patron_flexible,
    sanear_texto,
    telefonos_en,
)


COLUMNAS_TABLA = ["tipo", "clave", "valor_original", "codigo"]
COLUMNAS_REPORTES = ["reporte", "tipo", "codigo", "valor_real"]
CAMPOS_PERSONALES = {"telefono", "correo", "contacto", "direccion", "firma"}


def leer_csv_privado(ruta: Path, columnas: list[str]) -> list[dict[str, str]]:
    if not ruta.exists():
        return []
    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != columnas:
            raise ValueError(f"El esquema de {ruta.name} no coincide con {columnas}.")
        filas = []
        for fila in lector:
            if None in fila:
                raise ValueError(f"Fila CSV inválida en {ruta.name}.")
            filas.append({columna: fila.get(columna, "") or "" for columna in columnas})
        return filas


def escribir_csv_privado(ruta: Path, columnas: list[str], filas: list[dict[str, str]]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)


def indice_por_clave(filas: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    indice: dict[tuple[str, str], dict[str, str]] = {}
    codigos: dict[str, tuple[str, str]] = {}
    for fila in filas:
        clave = (fila["tipo"], fila["clave"])
        if clave in indice and indice[clave]["codigo"] != fila["codigo"]:
            raise ValueError("La tabla de códigos contiene claves duplicadas incompatibles.")
        if fila["codigo"]:
            propietario = codigos.get(fila["codigo"])
            if (
                propietario is not None
                and propietario != clave
                and not (propietario[0] == "cliente" and fila["tipo"] == "cliente_alias")
            ):
                raise ValueError("La tabla de códigos reutiliza un código para claves distintas.")
            codigos[fila["codigo"]] = clave
        indice[clave] = fila
    return indice


def siguiente_codigo(filas: list[dict[str, str]], prefijo: str) -> int:
    patron = re.compile(rf"^{re.escape(prefijo)}-(\d+)$")
    existentes = [
        int(coincidencia.group(1))
        for fila in filas
        if (coincidencia := patron.fullmatch(fila["codigo"])) is not None
    ]
    return max(existentes, default=0) + 1


def extraer_campos(ruta: Path) -> dict[str, object]:
    campos = leer_markdown(ruta)
    reporte = ""
    cliente = ""
    tecnico = ""
    modelo = ""
    serie = ""
    for etiqueta, valor in campos:
        canonico = campo_canonico(etiqueta)
        if canonico == "reporte" and not reporte:
            reporte = valor.strip()
        elif canonico == "cliente" and not cliente:
            cliente = valor.strip()
        elif canonico == "tecnico" and not tecnico:
            tecnico = valor.strip()
        elif canonico == "modelo" and not modelo:
            modelo = valor.strip()
        elif canonico == "serie" and not serie:
            serie = valor.strip()
    if not reporte:
        raise ValueError(f"{ruta.name}: falta el número de reporte.")
    if not cliente:
        raise ValueError(f"{reporte}: falta el campo de cliente/empresa.")
    if not (serie or modelo):
        raise ValueError(f"{reporte}: falta serie y modelo para identificar el equipo.")
    return {
        "ruta": ruta,
        "campos": campos,
        "reporte": reporte,
        "cliente": cliente,
        "tecnico": tecnico,
        "modelo": modelo,
        "serie": serie,
    }


def anonimizar(
    directorio_limpio: Path,
    directorio_fuentes: Path,
    directorio_privado: Path,
) -> int:
    if not directorio_limpio.is_dir():
        raise ValueError(f"No existe la carpeta de entrada: {directorio_limpio}")
    documentos = sorted(directorio_limpio.glob("*.md"))
    if not documentos:
        raise ValueError(f"No hay archivos Markdown en {directorio_limpio}.")
    registros = [extraer_campos(ruta) for ruta in documentos]

    ruta_tabla = directorio_privado / "tabla_codigos.csv"
    ruta_reportes = directorio_privado / "reportes_codigos.csv"
    tabla = leer_csv_privado(ruta_tabla, COLUMNAS_TABLA)
    reportes_existentes = leer_csv_privado(ruta_reportes, COLUMNAS_REPORTES)
    indice = indice_por_clave(tabla)
    secuencia_cliente = siguiente_codigo(tabla, "CLI")
    secuencia_tecnico = siguiente_codigo(tabla, "TEC")

    def codigo_cliente(valor: str) -> dict[str, str]:
        nonlocal secuencia_cliente
        clave = clave_empresa(valor)
        clave_mapa = ("cliente", clave)
        if clave_mapa not in indice:
            codigo = f"CLI-{secuencia_cliente:04d}"
            secuencia_cliente += 1
            fila = {
                "tipo": "cliente",
                "clave": clave,
                "valor_original": valor,
                "codigo": codigo,
            }
            tabla.append(fila)
            indice[clave_mapa] = fila
        fila = indice[clave_mapa]
        agregar_dato_pii("cliente_alias", valor, fila["codigo"])
        return fila

    def agregar_dato_pii(tipo: str, valor: str, codigo: str = "") -> None:
        if not valor:
            return
        clave = valor.strip().lower()
        clave_mapa = (tipo, clave)
        existente = indice.get(clave_mapa)
        if existente:
            if codigo and existente["codigo"] and existente["codigo"] != codigo:
                raise ValueError("Un dato personal existente tiene códigos incompatibles.")
            return
        fila = {
            "tipo": tipo,
            "clave": clave,
            "valor_original": valor,
            "codigo": codigo,
        }
        tabla.append(fila)
        indice[clave_mapa] = fila

    for registro in registros:
        fila_cliente = codigo_cliente(str(registro["cliente"]))
        registro["fila_cliente"] = fila_cliente
        tecnico = str(registro["tecnico"])
        if tecnico:
            clave_tecnico = tecnico.strip().lower()
            clave_mapa = ("tecnico", clave_tecnico)
            if clave_mapa not in indice:
                codigo = f"TEC-{secuencia_tecnico:02d}"
                secuencia_tecnico += 1
                fila = {
                    "tipo": "tecnico",
                    "clave": clave_tecnico,
                    "valor_original": tecnico,
                    "codigo": codigo,
                }
                tabla.append(fila)
                indice[clave_mapa] = fila
            registro["fila_tecnico"] = indice[clave_mapa]

        codigo_cli = str(fila_cliente["codigo"])
        numero_cliente = int(codigo_cli.split("-")[1])
        serie = str(registro["serie"])
        modelo = str(registro["modelo"])
        clave_equipo = (
            f"{clave_empresa(str(registro['cliente']))}|serie:{serie.strip().lower()}"
            if serie
            else f"{clave_empresa(str(registro['cliente']))}|modelo:{modelo.strip().lower()}"
        )
        clave_mapa_equipo = ("maquina", clave_equipo)
        if clave_mapa_equipo not in indice:
            secuencias = [
                int(coincidencia.group(1))
                for existente in tabla
                if (coincidencia := re.fullmatch(
                    rf"EQ-{numero_cliente:04d}-(\d+)", existente["codigo"]
                )) is not None
            ]
            consecutivo = max(secuencias, default=0) + 1
            fila = {
                "tipo": "maquina",
                "clave": clave_equipo,
                "valor_original": serie,
                "codigo": f"EQ-{numero_cliente:04d}-{consecutivo:02d}",
            }
            tabla.append(fila)
            indice[clave_mapa_equipo] = fila
        registro["fila_equipo"] = indice[clave_mapa_equipo]

        campos = registro["campos"]
        assert isinstance(campos, list)
        for etiqueta, valor in campos:
            canonico = campo_canonico(etiqueta)
            if canonico in CAMPOS_PERSONALES:
                tipo = canonico
                agregar_dato_pii(tipo, valor)
            for telefono in telefonos_en(valor):
                agregar_dato_pii("telefono", telefono)
            for correo in correos_en(valor):
                agregar_dato_pii("correo", correo)

    reemplazos: list[tuple[str, str, bool]] = []
    for fila in tabla:
        tipo = fila["tipo"]
        valor = fila["valor_original"]
        if not valor:
            continue
        if tipo in {"cliente", "cliente_alias"}:
            reemplazos.append((valor, fila["codigo"], True))
        elif tipo == "tecnico":
            reemplazos.append((valor, fila["codigo"], False))
        elif tipo == "maquina":
            reemplazos.append((valor, fila["codigo"], False))
        else:
            reemplazos.append((valor, "", False))
    modelos = sorted(
        {str(registro["modelo"]) for registro in registros if registro["modelo"]},
        key=len,
        reverse=True,
    )

    def sanear_sin_modelos(valor: str) -> str:
        protegidos: list[str] = []
        resultado = valor
        for modelo in modelos:
            patron = patron_flexible(modelo)
            if patron:
                resultado = patron.sub(
                    lambda coincidencia: proteger_modelo(coincidencia.group(0), protegidos),
                    resultado,
                )
        resultado = sanear_texto(resultado, reemplazos)
        for indice_modelo, modelo_original in enumerate(protegidos):
            resultado = resultado.replace(f"\uE100{indice_modelo}\uE101", modelo_original)
        return resultado

    def proteger_modelo(coincidencia: str, protegidos: list[str]) -> str:
        protegidos.append(coincidencia)
        return f"\uE100{len(protegidos) - 1}\uE101"

    reportes = {
        (fila["reporte"], fila["tipo"], fila["codigo"]): fila
        for fila in reportes_existentes
    }
    directorio_fuentes.mkdir(parents=True, exist_ok=True)
    for registro in registros:
        campos = registro["campos"]
        assert isinstance(campos, list)
        fila_cliente = registro["fila_cliente"]
        fila_equipo = registro["fila_equipo"]
        fila_tecnico = registro.get("fila_tecnico")
        assert isinstance(fila_cliente, dict) and isinstance(fila_equipo, dict)
        codigo_cliente_actual = fila_cliente["codigo"]
        codigo_equipo = fila_equipo["codigo"]
        codigo_tecnico = fila_tecnico["codigo"] if isinstance(fila_tecnico, dict) else ""
        reporte = str(registro["reporte"])
        campos_saneados: list[tuple[str, str]] = []
        tiene_serie = False

        for etiqueta, valor in campos:
            canonico = campo_canonico(etiqueta)
            if canonico in CAMPOS_PERSONALES:
                continue
            if canonico == "cliente":
                saneado = codigo_cliente_actual
            elif canonico == "tecnico" and codigo_tecnico:
                saneado = codigo_tecnico
            elif canonico == "serie":
                saneado = codigo_equipo
                tiene_serie = True
            elif canonico == "modelo":
                saneado = valor
            else:
                saneado = sanear_sin_modelos(valor)
            etiqueta_salida = NOMBRES_CAMPOS.get(canonico, etiqueta)
            campos_saneados.append((etiqueta_salida, saneado))

        if not tiene_serie:
            campos_saneados.append(("Código de equipo", codigo_equipo))
        destino = directorio_fuentes / Path(registro["ruta"]).name
        destino.write_text(renderizar_markdown(campos_saneados), encoding="utf-8")

        datos_reporte = [
            ("cliente", codigo_cliente_actual, str(registro["cliente"])),
            ("maquina", codigo_equipo, str(registro["serie"] or registro["modelo"])),
        ]
        if codigo_tecnico:
            datos_reporte.append(("tecnico", codigo_tecnico, str(registro["tecnico"])))
        for tipo, codigo, valor_real in datos_reporte:
            clave_reporte = (reporte, tipo, codigo)
            fila_existente = reportes.get(clave_reporte)
            if fila_existente:
                if fila_existente["valor_real"] != valor_real:
                    raise ValueError(
                        f"El reporte {reporte} ya tiene una reversión distinta para {codigo}."
                    )
            else:
                reportes[clave_reporte] = {
                    "reporte": reporte,
                    "tipo": tipo,
                    "codigo": codigo,
                    "valor_real": valor_real,
                }

    escribir_csv_privado(ruta_tabla, COLUMNAS_TABLA, tabla)
    escribir_csv_privado(ruta_reportes, COLUMNAS_REPORTES, list(reportes.values()))
    print(f"Reportes anonimizados: {len(registros)}")
    print(f"Clientes codificados: {sum(fila['tipo'] == 'cliente' for fila in tabla)}")
    print("Mapas privados actualizados en datos_privados/ (no versionar).")
    return 0


def main(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limpio", type=Path, default=Path("limpio"))
    parser.add_argument("--salida", type=Path, default=Path("fuentes"))
    parser.add_argument("--datos-privados", type=Path, default=Path("datos_privados"))
    opciones = parser.parse_args(argumentos)
    try:
        return anonimizar(opciones.limpio, opciones.salida, opciones.datos_privados)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
