# -*- coding: utf-8 -*-
"""Inspecciona una Test Execution completa (todos los campos), solo
lectura - para saber que atributos existen realmente en el modelo.

Uso: por stdin, {"password": "...", "ejecucion_id": 230}
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
    ejecucion_id = entrada["ejecucion_id"]

    rpc = connect(username=username, password=password)
    password = None

    ejecucion = rpc.TestExecution.filter({"id": ejecucion_id})[0]
    print(json.dumps(ejecucion, default=str))


if __name__ == "__main__":
    main()
