# -*- coding: utf-8 -*-
"""Actualiza summary/text de un caso ya existente. Uso puntual: corregir un
caso CONFIRMED cuya redaccion quedo obsoleta (autorizado por Fabian caso a
caso, nunca a criterio propio de Desarrollo o QA).

Uso: por stdin, {"password": "...", "caso_id": 349, "summary": "...", "text": "..."}
"""
import json
import os
import sys

sys.path.insert(0, "/tmp/work")
from rpc_client import connect


def main():
    username = os.environ.get("KIWI_USER", "qa-bot")
    entrada = json.loads(sys.stdin.read())
    password = entrada["password"]
    caso_id = entrada["caso_id"]

    rpc = connect(username=username, password=password)
    password = None

    valores = {}
    if "summary" in entrada:
        valores["summary"] = entrada["summary"]
    if "text" in entrada:
        valores["text"] = entrada["text"]

    rpc.TestCase.update(caso_id, valores)
    actualizado = rpc.TestCase.filter({"id": caso_id})[0]
    print(json.dumps({"id": actualizado["id"], "summary": actualizado["summary"], "text": actualizado["text"]}))


if __name__ == "__main__":
    main()
