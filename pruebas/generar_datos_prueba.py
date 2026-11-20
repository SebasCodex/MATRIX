"""Genera exportaciones RP-TECH sintéticas; no usa datos de clientes."""

from __future__ import annotations

import argparse
import tempfile
from datetime import date
from pathlib import Path

import pandas as pd


LEGAL_SINTETICO = (
    "AVISO LEGAL SINTÉTICO: documento ficticio para pruebas. "
    "No representa a clientes reales. " * 35
)
PIE_SINTETICO = (
    "PIE DE PÁGINA SINTÉTICO: uso demostrativo únicamente. "
    "No distribuir como reporte real. " * 30
)


def crear_exportacion(destino: Path, cantidad: int = 100) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    registros = []
    for indice in range(1, cantidad + 1):
        serie = "" if indice % 3 == 0 else f"SERIE-SINT-{indice:04d}"
        empresa = (
            "Av. Ficticia 123, Lima"
            if indice == 2
            else f"Cliente Sintético {indice:04d} S.A.C."
        )
        registros.append({
            "Número de reporte": f"R-{indice:06d}",
            "Fecha": date(2026, 1, (indice % 28) + 1),
            "Técnico": f"Técnico Sintético {indice % 4 + 1:02d}",
            "Cliente/Empresa": empresa,
            "Equipo (modelo)": "Bomba MX-200",
            "Número de serie": serie,
            "Motivo": f"Falla ficticia reportada por Ana Sintética {indice:04d}.",
            "Revisión inicial": "Inspección sintética sin daños visibles.",
            "Procedimiento": "Prueba ficticia; correo prueba.sintetica@example.invalid.",
            "Conclusión": "Equipo sintético operativo.",
            "Recomendaciones": "Revisar el equipo en 90 días.",
            "Repuestos": "Filtro sintético FS-01",
            "Hora de llegada": "09:15",
            "Hora de salida": "10:40",
            "Garantía": "Sí",
            "Facturado": "No",
            "Teléfono": f"+51 900 000 {indice:04d}",
            "Contacto": f"Ana Sintética {indice:04d}",
            "Dirección": f"Calle Ficticia {indice:04d}, Lima",
            "Firma": f"Firma sintética {indice:04d}",
            "Aviso legal": LEGAL_SINTETICO,
            "Pie de página": PIE_SINTETICO,
            "Casilla vacía": "☐",
        })
    pd.DataFrame(registros).to_excel(destino, index=False)
    return destino


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path)
    parser.add_argument("--cantidad", type=int, default=100)
    opciones = parser.parse_args()
    if opciones.cantidad < 1:
        parser.error("--cantidad debe ser positivo.")
    if opciones.salida:
        destino = opciones.salida
    else:
        destino = Path(tempfile.mkdtemp(prefix="matrix-sintetico-")) / "exportacion_sintetica.xlsx"
    crear_exportacion(destino, opciones.cantidad)
    print(f"Exportación sintética creada: {destino}")


if __name__ == "__main__":
    main()
