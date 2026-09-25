# -*- coding: utf-8 -*-
"""Borra un caso duplicado creado por error (nunca CONFIRMED, nunca en un
Test Run). Uso puntual, no una herramienta general - no reusar sin revisar
primero que el caso a borrar cumple esa condicion.

Uso: por stdin, {"password": "...", "caso_id": 360}
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

    caso = rpc.TestCase.filter({"id": caso_id})[0]
    if caso["case_status"] != 1:  # 1 = PROPOSED
        raise SystemExit(f"Caso {caso_id} no esta PROPOSED (case_status={caso['case_status']!r}) - no lo borro.")
    ejecuciones = rpc.TestExecution.filter({"case": caso_id})
    if ejecuciones:
        raise SystemExit(f"Caso {caso_id} tiene {len(ejecuciones)} Test Execution - no lo borro.")

    rpc.TestCase.remove({"id": caso_id})
    print(json.dumps({"borrado": caso_id, "summary": caso["summary"]}))


if __name__ == "__main__":
    main()
