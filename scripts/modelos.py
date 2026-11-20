"""Configuración y clientes para Claude y DeepSeek."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ConfiguracionModelo:
    nombre: str
    proveedor: str
    modelo: str
    api_key_env: str
    base_url: str
    costo_entrada_millon: float
    costo_salida_millon: float
    max_tokens: int = 4096


MODELOS: dict[str, ConfiguracionModelo] = {
    "claude": ConfiguracionModelo(
        nombre="Claude",
        proveedor="anthropic",
        modelo=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
        api_key_env="ANTHROPIC_API_KEY",
        base_url=os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1/messages"),
        costo_entrada_millon=float(os.getenv("CLAUDE_COSTO_ENTRADA_MILLON", "3.0")),
        costo_salida_millon=float(os.getenv("CLAUDE_COSTO_SALIDA_MILLON", "15.0")),
    ),
    "deepseek": ConfiguracionModelo(
        nombre="DeepSeek",
        proveedor="deepseek",
        modelo=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        api_key_env="DEEPSEEK_API_KEY",
        base_url=os.getenv(
            "DEEPSEEK_BASE_URL",
            "https://api.deepseek.com/chat/completions",
        ),
        costo_entrada_millon=float(os.getenv("DEEPSEEK_COSTO_ENTRADA_MILLON", "0.27")),
        costo_salida_millon=float(os.getenv("DEEPSEEK_COSTO_SALIDA_MILLON", "1.10")),
    ),
}


@dataclass
class ResultadoGeneracion:
    modelo: str
    proveedor: str
    exito: bool
    contenido: str = ""
    tokens_entrada: int = 0
    tokens_salida: int = 0
    costo_usd: float = 0.0
    tiempo_s: float = 0.0
    error: str = ""
    simulado: bool = False
    detalle: dict[str, Any] = field(default_factory=dict)


def cargar_env(ruta: Path | None = None) -> None:
    archivo = ruta or Path(".env")
    if not archivo.is_file():
        return
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        texto = linea.strip()
        if not texto or texto.startswith("#") or "=" not in texto:
            continue
        clave, valor = texto.split("=", 1)
        clave = clave.strip()
        valor = valor.strip().strip("'").strip('"')
        if clave and clave not in os.environ:
            os.environ[clave] = valor


def obtener_configuracion(nombre: str) -> ConfiguracionModelo:
    clave = nombre.lower().strip()
    if clave not in MODELOS:
        raise ValueError(f"Modelo no soportado: {nombre}. Use claude o deepseek.")
    base = MODELOS[clave]
    # Refresca valores dependientes de entorno por si se cargó .env después.
    if clave == "claude":
        return ConfiguracionModelo(
            nombre=base.nombre,
            proveedor=base.proveedor,
            modelo=os.getenv("CLAUDE_MODEL", base.modelo),
            api_key_env=base.api_key_env,
            base_url=os.getenv("ANTHROPIC_BASE_URL", base.base_url),
            costo_entrada_millon=float(
                os.getenv("CLAUDE_COSTO_ENTRADA_MILLON", str(base.costo_entrada_millon))
            ),
            costo_salida_millon=float(
                os.getenv("CLAUDE_COSTO_SALIDA_MILLON", str(base.costo_salida_millon))
            ),
            max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", str(base.max_tokens))),
        )
    return ConfiguracionModelo(
        nombre=base.nombre,
        proveedor=base.proveedor,
        modelo=os.getenv("DEEPSEEK_MODEL", base.modelo),
        api_key_env=base.api_key_env,
        base_url=os.getenv("DEEPSEEK_BASE_URL", base.base_url),
        costo_entrada_millon=float(
            os.getenv("DEEPSEEK_COSTO_ENTRADA_MILLON", str(base.costo_entrada_millon))
        ),
        costo_salida_millon=float(
            os.getenv("DEEPSEEK_COSTO_SALIDA_MILLON", str(base.costo_salida_millon))
        ),
        max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", str(base.max_tokens))),
    )


def calcular_costo(config: ConfiguracionModelo, entrada: int, salida: int) -> float:
    costo = (entrada / 1_000_000) * config.costo_entrada_millon
    costo += (salida / 1_000_000) * config.costo_salida_millon
    return round(costo, 8)


def _estimar_tokens(texto: str) -> int:
    if not texto:
        return 0
    try:
        import tiktoken  # type: ignore

        codificacion = tiktoken.get_encoding("cl100k_base")
        return len(codificacion.encode(texto))
    except Exception:
        return max(1, (len(texto) + 3) // 4)


def _post_json(url: str, encabezados: dict[str, str], carga: dict[str, Any], timeout: int) -> dict[str, Any]:
    datos = json.dumps(carga).encode("utf-8")
    solicitud = urllib.request.Request(url, data=datos, headers=encabezados, method="POST")
    with urllib.request.urlopen(solicitud, timeout=timeout) as respuesta:
        cuerpo = respuesta.read().decode("utf-8", errors="replace")
    return json.loads(cuerpo) if cuerpo else {}


def generar(
    nombre_modelo: str,
    prompt: str,
    sistema: str = "",
    simular: bool = False,
    timeout: int = 120,
) -> ResultadoGeneracion:
    config = obtener_configuracion(nombre_modelo)
    api_key = os.getenv(config.api_key_env, "").strip()
    inicio = time.perf_counter()

    if simular or not api_key:
        contenido = _contenido_simulado(config, prompt)
        entrada = _estimar_tokens((sistema + "\n" + prompt).strip())
        salida = _estimar_tokens(contenido)
        tiempo = round(time.perf_counter() - inicio, 4)
        error = "" if simular else f"Falta variable de entorno {config.api_key_env}"
        # Sin clave y sin modo simular explícito se marca como no ejecutado real,
        # pero devolvemos estructura completa para no interrumpir lotes por accidente.
        exito = simular
        if not simular:
            error = f"No se encontró {config.api_key_env}; active --simular o configure la clave."
        return ResultadoGeneracion(
            modelo=config.modelo,
            proveedor=config.proveedor,
            exito=exito,
            contenido=contenido if simular else "",
            tokens_entrada=entrada,
            tokens_salida=salida if simular else 0,
            costo_usd=calcular_costo(config, entrada, salida if simular else 0),
            tiempo_s=tiempo,
            error=error,
            simulado=True,
            detalle={"motivo": "simulacion" if simular else "sin_api_key"},
        )

    try:
        if config.proveedor == "anthropic":
            respuesta = _llamar_anthropic(config, api_key, prompt, sistema, timeout)
        else:
            respuesta = _llamar_openai_compatible(config, api_key, prompt, sistema, timeout)
        tiempo = round(time.perf_counter() - inicio, 4)
        entrada = int(respuesta.get("tokens_entrada", 0))
        salida = int(respuesta.get("tokens_salida", 0))
        return ResultadoGeneracion(
            modelo=config.modelo,
            proveedor=config.proveedor,
            exito=True,
            contenido=str(respuesta.get("contenido", "")),
            tokens_entrada=entrada,
            tokens_salida=salida,
            costo_usd=calcular_costo(config, entrada, salida),
            tiempo_s=tiempo,
            detalle=respuesta.get("detalle", {}),
        )
    except Exception as exc:  # pragma: no cover - depende de red/API
        tiempo = round(time.perf_counter() - inicio, 4)
        return ResultadoGeneracion(
            modelo=config.modelo,
            proveedor=config.proveedor,
            exito=False,
            tiempo_s=tiempo,
            error=str(exc),
        )


def _llamar_anthropic(
    config: ConfiguracionModelo,
    api_key: str,
    prompt: str,
    sistema: str,
    timeout: int,
) -> dict[str, Any]:
    carga: dict[str, Any] = {
        "model": config.modelo,
        "max_tokens": config.max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if sistema:
        carga["system"] = sistema
    encabezados = {
        "content-type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01"),
    }
    datos = _post_json(config.base_url, encabezados, carga, timeout)
    bloques = datos.get("content", []) or []
    texto = "".join(
        bloque.get("text", "")
        for bloque in bloques
        if isinstance(bloque, dict) and bloque.get("type") == "text"
    )
    uso = datos.get("usage", {}) or {}
    return {
        "contenido": texto.strip(),
        "tokens_entrada": int(uso.get("input_tokens", 0) or 0),
        "tokens_salida": int(uso.get("output_tokens", 0) or 0),
        "detalle": {"id": datos.get("id"), "stop_reason": datos.get("stop_reason")},
    }


def _llamar_openai_compatible(
    config: ConfiguracionModelo,
    api_key: str,
    prompt: str,
    sistema: str,
    timeout: int,
) -> dict[str, Any]:
    mensajes = []
    if sistema:
        mensajes.append({"role": "system", "content": sistema})
    mensajes.append({"role": "user", "content": prompt})
    carga = {
        "model": config.modelo,
        "messages": mensajes,
        "max_tokens": config.max_tokens,
        "temperature": float(os.getenv("TEMPERATURA_INGESTA", "0.2")),
    }
    encabezados = {
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    datos = _post_json(config.base_url, encabezados, carga, timeout)
    opciones = datos.get("choices", []) or []
    mensaje = (opciones[0] or {}).get("message", {}) if opciones else {}
    contenido = mensaje.get("content", "") if isinstance(mensaje, dict) else ""
    uso = datos.get("usage", {}) or {}
    return {
        "contenido": str(contenido).strip(),
        "tokens_entrada": int(uso.get("prompt_tokens", 0) or 0),
        "tokens_salida": int(uso.get("completion_tokens", 0) or 0),
        "detalle": {"id": datos.get("id"), "finish_reason": (opciones[0] or {}).get("finish_reason") if opciones else None},
    }


def _contenido_simulado(config: ConfiguracionModelo, prompt: str) -> str:
    reporte = "reporte"
    for linea in prompt.splitlines():
        if linea.startswith("Reporte:"):
            reporte = linea.split(":", 1)[1].strip() or reporte
            break
    return (
        f"# Ficha técnica {reporte}\n\n"
        f"- **Fuente**: [[{reporte}]]\n"
        f"- **Modelo**: {config.modelo}\n"
        "- **Resumen**: Registro de servicio procesado para la wiki técnica.\n\n"
        "## Datos del servicio\n"
        "- Se conservaron los campos técnicos disponibles del reporte fuente.\n"
        "- Los identificadores personales permanecen anonimizados.\n\n"
        "## Hallazgos y acciones\n"
        "- Motivo, revisión, procedimiento y conclusión consolidados desde la fuente.\n\n"
        "## Seguimiento\n"
        "- Revisar recomendaciones y repuestos asociados en el reporte original.\n"
    )
