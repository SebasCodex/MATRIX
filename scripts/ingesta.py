"""Ingesta de reportes en wikis técnicas usando Claude y DeepSeek."""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

from comun import campo_canonico, leer_markdown
from modelos import cargar_env, generar, obtener_configuracion


SISTEMA = (
    "Eres un asistente técnico. Convierte reportes de servicio en páginas wiki "
    "claras y estructuradas en español. Conserva los identificadores anonimizados "
    "tal como aparecen, no inventes datos y cita el reporte fuente."
)


def construir_prompt(reporte: str, campos: list[tuple[str, str]]) -> str:
    lineas = [f"Reporte: {reporte}", "", "Contenido fuente:"]
    for etiqueta, valor in campos:
        lineas.append(f"- {etiqueta}: {valor}")
    lineas.extend([
        "",
        "Genera una página Markdown para la wiki técnica con estas secciones:",
        "# <título con el número de reporte>",
        "## Resumen",
        "## Datos del equipo y servicio",
        "## Diagnóstico y procedimiento",
        "## Repuestos y recomendaciones",
        "## Fuente",
        "En 'Fuente' incluye un enlace wiki al reporte: [[<nombre del reporte>]].",
        "No agregues información que no esté en la fuente.",
    ])
    return "\n".join(lineas)


def numero_reporte(ruta: Path, campos: list[tuple[str, str]]) -> str:
    for etiqueta, valor in campos:
        if campo_canonico(etiqueta) == "reporte" and valor.strip():
            return valor.strip()
    return ruta.stem


def generar_fuentes_sinteticos(destino: Path, cantidad: int) -> list[Path]:
    destino.mkdir(parents=True, exist_ok=True)
    rutas: list[Path] = []
    for indice in range(1, cantidad + 1):
        codigo = f"R-SINT-{indice:04d}"
        contenido = "\n".join([
            "# Reporte de servicio",
            f"- **Número de reporte**: {codigo}",
            f"- **Fecha**: 2026-11-{(indice % 28) + 1:02d}",
            f"- **Cliente/empresa**: CLI-{((indice - 1) % 20) + 1:04d}",
            f"- **Técnico**: TEC-{((indice - 1) % 5) + 1:02d}",
            "- **Equipo (modelo)**: Bomba MX-200",
            f"- **Serie**: EQ-{((indice - 1) % 20) + 1:04d}-01",
            f"- **Motivo**: Falla intermitente en ciclo de operación {indice}.",
            "- **Revisión inicial**: Se verificó presión, conexiones y estado general.",
            "- **Procedimiento**: Ajuste de parámetros, limpieza de componentes y prueba funcional.",
            "- **Conclusión**: Equipo operativo al finalizar la intervención.",
            "- **Recomendaciones**: Programar revisión preventiva en 90 días.",
            "- **Repuestos**: Kit de mantenimiento básico",
            "",
        ])
        ruta = destino / f"{codigo}.md"
        ruta.write_text(contenido, encoding="utf-8")
        rutas.append(ruta)
    return rutas


def descubrir_reportes(fuentes: Path, limite: int | None = None) -> list[Path]:
    if not fuentes.is_dir():
        raise ValueError(f"No existe la carpeta de fuentes: {fuentes}")
    rutas = sorted(fuentes.glob("*.md"))
    if limite is not None:
        rutas = rutas[:limite]
    if not rutas:
        raise ValueError(f"No se encontraron reportes Markdown en {fuentes}.")
    return rutas


def procesar_reporte(
    ruta: Path,
    modelo: str,
    salida_modelo: Path,
    simular: bool,
) -> dict[str, str | int | float | bool]:
    campos = leer_markdown(ruta)
    reporte = numero_reporte(ruta, campos)
    prompt = construir_prompt(reporte, campos)
    resultado = generar(modelo, prompt, sistema=SISTEMA, simular=simular)

    archivo_salida = ""
    if resultado.exito and resultado.contenido:
        salida_modelo.mkdir(parents=True, exist_ok=True)
        destino = salida_modelo / f"{ruta.stem}.wiki.md"
        destino.write_text(resultado.contenido.rstrip() + "\n", encoding="utf-8")
        archivo_salida = str(destino).replace("\\", "/")

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reporte": reporte,
        "archivo_fuente": str(ruta).replace("\\", "/"),
        "modelo_alias": modelo,
        "modelo": resultado.modelo,
        "proveedor": resultado.proveedor,
        "exito": resultado.exito,
        "simulado": resultado.simulado,
        "tokens_entrada": resultado.tokens_entrada,
        "tokens_salida": resultado.tokens_salida,
        "tokens_total": resultado.tokens_entrada + resultado.tokens_salida,
        "costo_usd": resultado.costo_usd,
        "tiempo_s": resultado.tiempo_s,
        "error": resultado.error,
        "archivo_salida": archivo_salida,
    }


def escribir_csv(ruta: Path, filas: list[dict[str, object]]) -> None:
    if not filas:
        return
    ruta.parent.mkdir(parents=True, exist_ok=True)
    columnas = list(filas[0].keys())
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)


def resumen_modelo(filas: list[dict[str, object]], modelo: str) -> dict[str, object]:
    datos = [f for f in filas if f["modelo_alias"] == modelo]
    exitos = [f for f in datos if bool(f["exito"])]
    errores = [f for f in datos if not bool(f["exito"])]
    tokens_entrada = sum(int(f["tokens_entrada"]) for f in datos)
    tokens_salida = sum(int(f["tokens_salida"]) for f in datos)
    costo = round(sum(float(f["costo_usd"]) for f in datos), 8)
    tiempo = round(sum(float(f["tiempo_s"]) for f in datos), 4)
    return {
        "modelo_alias": modelo,
        "modelo": datos[0]["modelo"] if datos else "",
        "reportes": len(datos),
        "exitos": len(exitos),
        "errores": len(errores),
        "tokens_entrada": tokens_entrada,
        "tokens_salida": tokens_salida,
        "tokens_total": tokens_entrada + tokens_salida,
        "costo_usd": costo,
        "tiempo_s": tiempo,
        "tiempo_promedio_s": round(tiempo / len(datos), 4) if datos else 0.0,
    }


def ejecutar_ingesta(
    fuentes: Path,
    salida_base: Path,
    resultados: Path,
    modelos: list[str],
    limite: int | None,
    lote: int,
    simular: bool,
) -> int:
    rutas = descubrir_reportes(fuentes, limite)
    registros: list[dict[str, object]] = []
    total = len(rutas)

    for inicio in range(0, total, lote):
        bloque = rutas[inicio : inicio + lote]
        numero_lote = (inicio // lote) + 1
        print(f"Lote {numero_lote}: reportes {inicio + 1}-{inicio + len(bloque)} de {total}")
        for ruta in bloque:
            for modelo in modelos:
                carpeta = salida_base / f"wiki-{modelo}"
                registro = procesar_reporte(ruta, modelo, carpeta, simular)
                registros.append(registro)
                estado = "OK" if registro["exito"] else "ERROR"
                marca = " (simulado)" if registro["simulado"] else ""
                print(
                    f"  [{estado}] {registro['reporte']} -> {modelo}{marca} "
                    f"tokens={registro['tokens_total']} tiempo={registro['tiempo_s']}s"
                )
                if registro["error"]:
                    print(f"       detalle: {registro['error']}")

    marca_tiempo = datetime.now().strftime("%Y%m%d-%H%M%S")
    detalle_path = resultados / f"ingesta-detalle-{marca_tiempo}.csv"
    resumen_path = resultados / f"ingesta-resumen-{marca_tiempo}.csv"
    escribir_csv(detalle_path, registros)
    resumenes = [resumen_modelo(registros, modelo) for modelo in modelos]
    escribir_csv(resumen_path, resumenes)

    print("")
    print(f"Detalle: {detalle_path}")
    print(f"Resumen: {resumen_path}")
    for resumen in resumenes:
        print(
            f"- {resumen['modelo_alias']}: reportes={resumen['reportes']} "
            f"exitos={resumen['exitos']} errores={resumen['errores']} "
            f"tokens={resumen['tokens_total']} costo_usd={resumen['costo_usd']} "
            f"tiempo_s={resumen['tiempo_s']}"
        )
    return 0 if all(int(r["errores"]) == 0 for r in resumenes) else 1


def main(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fuentes", type=Path, default=Path("fuentes"))
    parser.add_argument("--salida", type=Path, default=Path("salida_ingesta"))
    parser.add_argument("--resultados", type=Path, default=Path("resultados/ingesta"))
    parser.add_argument(
        "--modelo",
        choices=["claude", "deepseek", "ambos"],
        default="ambos",
        help="Modelo a ejecutar.",
    )
    parser.add_argument("--limite", type=int, help="Cantidad máxima de reportes a procesar.")
    parser.add_argument("--primeros", type=int, help="Procesa solo los primeros N reportes.")
    parser.add_argument("--lote", type=int, default=10, help="Tamaño de lote (por defecto 10).")
    parser.add_argument("--simular", action="store_true", help="No llama APIs; genera salida y métricas estimadas.")
    parser.add_argument("--env", type=Path, default=Path(".env"), help="Archivo .env a cargar.")
    parser.add_argument(
        "--generar-sinteticos",
        type=int,
        metavar="N",
        help="Genera N reportes fuente sintéticos en --fuentes antes de ingerir.",
    )
    opciones = parser.parse_args(argumentos)

    if opciones.lote < 1:
        parser.error("--lote debe ser un entero positivo.")
    limite = opciones.primeros if opciones.primeros is not None else opciones.limite
    if limite is not None and limite < 1:
        parser.error("--limite/--primeros debe ser un entero positivo.")
    if opciones.generar_sinteticos is not None and opciones.generar_sinteticos < 1:
        parser.error("--generar-sinteticos debe ser un entero positivo.")

    cargar_env(opciones.env)
    modelos = ["claude", "deepseek"] if opciones.modelo == "ambos" else [opciones.modelo]
    try:
        for modelo in modelos:
            obtener_configuracion(modelo)
        if opciones.generar_sinteticos:
            generar_fuentes_sinteticos(opciones.fuentes, opciones.generar_sinteticos)
            print(f"Fuentes sintéticas generadas: {opciones.generar_sinteticos} en {opciones.fuentes}")
        return ejecutar_ingesta(
            opciones.fuentes,
            opciones.salida,
            opciones.resultados,
            modelos,
            limite,
            opciones.lote,
            opciones.simular,
        )
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
