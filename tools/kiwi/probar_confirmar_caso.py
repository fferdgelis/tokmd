# -*- coding: utf-8 -*-
"""Prueba puntual: ¿el usuario qa-bot tiene permiso de Kiwi para pasar un
caso de PROPOSED a CONFIRMED? Sólo reporta si funciono o si Kiwi lo
rechaza por permisos - no asume el resultado de antemano.

Uso: por stdin, {"password": "...", "caso_id": 361}
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

    estados = rpc.TestCaseStatus.filter({})
    confirmed = next(e for e in estados if e["name"] == "CONFIRMED")

    caso_antes = rpc.TestCase.filter({"id": caso_id})[0]
    print(json.dumps({"antes": {"id": caso_antes["id"], "case_status": caso_antes["case_status"]}}))

    try:
        rpc.TestCase.update(caso_id, {"case_status": confirmed["id"]})
    except Exception as e:
        print(json.dumps({"resultado": "RECHAZADO", "error": str(e)}))
        return

    caso_despues = rpc.TestCase.filter({"id": caso_id})[0]
    print(json.dumps({"resultado": "PERMITIDO", "despues": {"id": caso_despues["id"], "case_status": caso_despues["case_status"]}}))


if __name__ == "__main__":
    main()
