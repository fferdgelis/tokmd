# -*- coding: utf-8 -*-
"""Punto de entrada Python del rol TDD (ADR-006): arma la especificación y
llama al wrapper PowerShell que usa el modulo compartido de conexion DeepSeek
(C:\\IA\\modulo-conexion-deepseek). No reimplementa la conexion: la delega.

Uso:
    uv run python tools/deepseek/generar_tests.py PBI-001

Lee tools/deepseek/specs/<PBI>.md (contrato publico + AC, escrito a mano por
Desarrollo, SIN el cuerpo de la implementacion) y produce tests/test_<modulo>.py.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECS_DIR = Path(__file__).resolve().parent / "specs"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Uso: generar_tests.py <PBI-NNN>")
    pbi = sys.argv[1]
    spec_path = SPECS_DIR / f"{pbi}.md.prompt"
    if not spec_path.exists():
        raise SystemExit(f"No existe la especificacion {spec_path}")

    ps1 = Path(__file__).parent / "Invoke-TddDeepSeek.ps1"
    result = subprocess.run(
        [
            "pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(ps1),
            "-SpecPath", str(spec_path),
            "-Pbi", pbi,
        ],
        cwd=str(ROOT),
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
