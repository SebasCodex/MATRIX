"""Pruebas de anonimización con identidades completamente inventadas."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from generar_datos_prueba import crear_exportacion_repetida


RAIZ = Path(__file__).resolve().parents[1]


def ejecutar(*argumentos: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *argumentos],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


class PruebasAnonimizacion(unittest.TestCase):
    def test_codigos_persisten_verificacion_falla_y_reversion(self) -> None:
        with tempfile.TemporaryDirectory(prefix="matrix-t02-") as temporal:
            base = Path(temporal)
            limpio = base / "limpio"
            fuentes = base / "fuentes"
            privado = base / "datos_privados"
            wiki = base / "wiki-tecnica"
            wiki.mkdir()
            (wiki / "guia.md").write_text("Guía técnica sintética.\n", encoding="utf-8")

            primera = crear_exportacion_repetida(
                base / "primera_exportacion.xlsx",
                [("R-001905", True)],
            )
            segunda = crear_exportacion_repetida(
                base / "segunda_exportacion.xlsx",
                [("R-001906", True), ("R-001907", False)],
            )
            for exportacion in (primera, segunda):
                resultado = ejecutar(
                    str(RAIZ / "scripts" / "limpieza.py"),
                    str(exportacion),
                    "--salida", str(limpio),
                    cwd=base,
                )
                self.assertEqual(resultado.returncode, 0, resultado.stderr)
                self.assertIn("perdidos=0", resultado.stdout)

            resultado = ejecutar(
                str(RAIZ / "scripts" / "anonimizar.py"),
                "--limpio", str(limpio),
                "--salida", str(fuentes),
                "--datos-privados", str(privado),
                cwd=base,
            )
            self.assertEqual(resultado.returncode, 0, resultado.stderr)

            verificacion = [
                str(RAIZ / "scripts" / "verificar_anonimizacion.py"),
                "--fuentes", str(fuentes),
                "--datos-privados", str(privado),
                "--raiz-wiki", str(base),
            ]
            resultado = ejecutar(*verificacion, cwd=base)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertIn("0 coincidencias", resultado.stdout)

            reporte_uno = (fuentes / "R-001905.md").read_text(encoding="utf-8")
            reporte_dos = (fuentes / "R-001906.md").read_text(encoding="utf-8")
            reporte_sin_serie = (fuentes / "R-001907.md").read_text(encoding="utf-8")
            self.assertIn("CLI-0001", reporte_uno)
            self.assertIn("CLI-0001", reporte_dos)
            self.assertIn("TEC-01", reporte_uno)
            self.assertIn("TEC-01", reporte_dos)
            self.assertIn("EQ-0001-01", reporte_uno)
            self.assertIn("EQ-0001-01", reporte_dos)
            self.assertIn("EQ-0001-02", reporte_sin_serie)
            self.assertIn("Bomba MX-200", reporte_sin_serie)
            self.assertIn("2026-03-14", reporte_uno)
            self.assertIn("42 días", reporte_uno)
            for dato in (
                "Compañía de Prueba", "Lucía Técnica", "María Contacto",
                "+51 987 654 321", "persona.prueba@example.invalid",
                "Av. Inventada 456", "SN-CLIENTE-778899",
            ):
                self.assertNotIn(dato, reporte_uno)

            reporte_inyectado = fuentes / "R-001905.md"
            original = reporte_inyectado.read_text(encoding="utf-8")
            reporte_inyectado.write_text(
                original + "\nCOMPANIA DE PRUEBA S.R.L.\n",
                encoding="utf-8",
            )
            resultado = ejecutar(*verificacion, cwd=base)
            self.assertEqual(resultado.returncode, 1)
            self.assertIn("Coincidencia:", resultado.stdout)
            reporte_inyectado.write_text(original, encoding="utf-8")

            resultado = ejecutar(
                str(RAIZ / "scripts" / "verificar_anonimizacion.py"),
                "--datos-privados", str(privado),
                "--revertir", "CLI-0001", "R-001905",
                cwd=base,
            )
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertEqual(resultado.stdout.strip(), "Compañía de Prueba S.A.C.")


if __name__ == "__main__":
    unittest.main()
