"""Pruebas de limpieza con fixtures generados en tiempo de ejecución."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from generar_datos_prueba import crear_exportacion


RAIZ = Path(__file__).resolve().parents[1]


class PruebasLimpieza(unittest.TestCase):
    def test_limpia_cien_reportes_sin_perder_campos(self) -> None:
        with tempfile.TemporaryDirectory(prefix="matrix-t01-") as temporal:
            base = Path(temporal)
            entrada = crear_exportacion(base / "exportacion_sintetica.xlsx")
            salida = base / "limpio"
            resultado = subprocess.run(
                [
                    sys.executable, str(RAIZ / "scripts" / "limpieza.py"),
                    str(entrada), "--salida", str(salida), "--max", "100",
                ],
                cwd=base,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            reportes = sorted(salida.glob("R-*.md"))
            self.assertEqual(len(reportes), 100)
            self.assertIn("perdidos=0", resultado.stdout)
            self.assertIn("Tokens (", resultado.stdout)
            self.assertIn("| TOTAL |", resultado.stdout)

            primero = (salida / "R-000001.md").read_text(encoding="utf-8")
            self.assertIn("2026-01-02", primero)
            self.assertNotIn("AVISO LEGAL SINTÉTICO", primero)
            self.assertNotIn("PIE DE PÁGINA SINTÉTICO", primero)
            self.assertNotIn("☐", primero)

            sin_serie = (salida / "R-000003.md").read_text(encoding="utf-8")
            self.assertNotIn("SERIE-SINT-0003", sin_serie)
            self.assertIn("Bomba MX-200", sin_serie)

            empresa_direccion = (salida / "R-000002.md").read_text(encoding="utf-8")
            self.assertIn("Av. Ficticia 123, Lima", empresa_direccion)


if __name__ == "__main__":
    unittest.main()
