# -*- coding: utf-8 -*-
"""Crea, una sola vez, el catálogo de Kiwi TCMS para el producto tokmd.

IDEMPOTENTE: filtra antes de crear. Correrlo dos veces deja el mismo estado
que correrlo una. No se toca después de la Fase 0 (ADR-005).

Eje del catálogo (fijo):
  Clasificación: Herramientas de desarrollo
  Producto:      tokmd
  Versión:       1.0.0
  Categorías:    Functional, Error, Edge case, Performance, Security
  Componentes:   Sections parser, Tokenizers, CLI, Render, Verify,
                 Packaging, SonarQube gate

Corre DENTRO del contenedor kiwi_web (rpc_client.py se copia a /tmp/work
con `docker cp` antes de invocar este script, igual que en whatsapp-mcp).
La contraseña llega por stdin, nunca por argumento ni variable persistida.
"""
import os
import sys

sys.path.insert(0, "/tmp/work")
from rpc_client import connect

CLASIFICACION = "Herramientas de desarrollo"
PRODUCTO = "tokmd"
VERSION = "1.0.0"
CATEGORIAS = ["Functional", "Error", "Edge case", "Performance", "Security"]
COMPONENTES = {
    "Sections parser": "Parseo del árbol de secciones de un archivo Markdown",
    "Tokenizers": "Conteo de tokens Claude (ctok) y OpenAI (tiktoken)",
    "CLI": "Interfaz de línea de comandos y flag --platform",
    "Render": "Formatos de salida table/md/json/csv",
    "Verify": "Verificación contra POST /v1/messages/count_tokens",
    "Packaging": "Empaquetado y publicación en PyPI/GitHub",
    "SonarQube gate": "Integración con el Quality Gate de SonarQube",
}


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

    clasificacion, nueva = obtener_o_crear(
        rpc.Classification, {"name": CLASIFICACION}, {"name": CLASIFICACION}
    )
    print(f"Clasificacion: {clasificacion['name']} (id={clasificacion['id']}) {'CREADA' if nueva else 'ya existia'}")

    producto, nuevo = obtener_o_crear(
        rpc.Product,
        {"name": PRODUCTO},
        {
            "name": PRODUCTO,
            "description": "tokmd: conteo de tokens por sección con el tokenizador de cada plataforma",
            "classification": clasificacion["id"],
        },
    )
    print(f"Producto: {producto['name']} (id={producto['id']}) {'CREADO' if nuevo else 'ya existia'}")

    version, nueva = obtener_o_crear(
        rpc.Version,
        {"product": producto["id"], "value": VERSION},
        {"product": producto["id"], "value": VERSION},
    )
    print(f"Version: {version['value']} (id={version['id']}) {'CREADA' if nueva else 'ya existia'}")

    for nombre in CATEGORIAS:
        categoria, nueva = obtener_o_crear(
            rpc.Category,
            {"product": producto["id"], "name": nombre},
            {"product": producto["id"], "name": nombre, "description": f"Categoria {nombre} del metodo"},
        )
        print(f"Categoria: {categoria['name']} (id={categoria['id']}) {'CREADA' if nueva else 'ya existia'}")

    for nombre, descripcion in COMPONENTES.items():
        componente, nuevo = obtener_o_crear(
            rpc.Component,
            {"product": producto["id"], "name": nombre},
            {"product": producto["id"], "name": nombre, "description": descripcion},
        )
        print(f"Componente: {componente['name']} (id={componente['id']}) {'CREADO' if nuevo else 'ya existia'}")



if __name__ == "__main__":
    main()
