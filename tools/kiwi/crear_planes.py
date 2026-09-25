# -*- coding: utf-8 -*-
"""Crea los Test Plan de tokmd: uno Unit por PBI (8) + uno Acceptance de release.

IDEMPOTENTE. Corre después de crear_catalogo.py. Password por stdin.
"""
import os
import sys

sys.path.insert(0, "/tmp/work")
from rpc_client import connect

PRODUCTO = "tokmd"
VERSION = "1.0.0"
TIPO_UNIT = 1        # Unit
TIPO_ACCEPTANCE = 5  # Acceptance

PLANES_UNIT = [
    ("PBI-001 - Parser de secciones", "Árbol de secciones: front matter, preámbulo, saltos de nivel, bloques de código."),
    ("PBI-002 - Tokenizador Claude", "ctok + marco medido por familia (3, 4.7, 4.8)."),
    ("PBI-003 - Tokenizador OpenAI", "tiktoken, encoding o200k_base y cl100k_base."),
    ("PBI-004 - CLI y plataformas", "--platform, --model, --tokenizer, validación de errores."),
    ("PBI-005 - Render de salida", "table, md, json, csv, --depth, --sort."),
    ("PBI-006 - Verificacion contra la API", "--verify, columna API y Δ, test mutante."),
    ("PBI-007 - Empaquetado y publicacion", "CI, publish.yml, Trusted Publishing, uvx tokmd."),
    ("PBI-008 - Medicion CLAUDE.md global", "Medición final con tokmd sobre el CLAUDE.md global."),
]

PLAN_ACCEPTANCE = (
    "Release 1.0.0",
    "Casos de extremo a extremo: uvx tokmd responde, gate Sonar OK, "
    "medición del CLAUDE.md global, paquete publicado en PyPI.",
)


def obtener_o_crear(recurso, filtro, valores):
    existentes = recurso.filter(filtro)
    if existentes:
        return existentes[0], False
    return recurso.create(valores), True


def main():
    username = os.environ.get("KIWI_USER", "qa-bot")
    password = sys.stdin.readline().rstrip("\r\n")
    if not password:
        raise SystemExit("Falta la contraseña Kiwi por stdin.")

    rpc = connect(username=username, password=password)
    password = None

    producto = rpc.Product.filter({"name": PRODUCTO})
    if not producto:
        raise SystemExit(f"Producto '{PRODUCTO}' no existe. Correr crear_catalogo.py primero.")
    producto = producto[0]

    version = rpc.Version.filter({"product": producto["id"], "value": VERSION})
    if not version:
        raise SystemExit(f"Version '{VERSION}' no existe. Correr crear_catalogo.py primero.")
    version = version[0]

    for nombre, texto in PLANES_UNIT:
        plan, nuevo = obtener_o_crear(
            rpc.TestPlan,
            {"name": nombre, "product": producto["id"]},
            {
                "name": nombre,
                "text": texto,
                "product": producto["id"],
                "product_version": version["id"],
                "type": TIPO_UNIT,
                "is_active": True,
            },
        )
        print(f"Plan Unit: {plan['name']} (id={plan['id']}) {'CREADO' if nuevo else 'ya existia'}")

    nombre, texto = PLAN_ACCEPTANCE
    plan, nuevo = obtener_o_crear(
        rpc.TestPlan,
        {"name": nombre, "product": producto["id"]},
        {
            "name": nombre,
            "text": texto,
            "product": producto["id"],
            "product_version": version["id"],
            "type": TIPO_ACCEPTANCE,
            "is_active": True,
        },
    )
    print(f"Plan Acceptance: {plan['name']} (id={plan['id']}) {'CREADO' if nuevo else 'ya existia'}")


if __name__ == "__main__":
    main()
