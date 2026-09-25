# -*- coding: utf-8 -*-
"""Pasa uno o mas casos de PROPOSED a CONFIRMED. Uso explicito, a pedido
directo de Fabian caso a caso o tanda a tanda - no se corre a criterio
propio de Desarrollo (separacion de roles, ADR-006).

Uso: por stdin, {"password": "...", "caso_ids": [362, 363, 364]}
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
    caso_ids = entrada["caso_ids"]

    rpc = connect(username=username, password=password)
    password = None

    confirmed = rpc.TestCaseStatus.filter({"name": "CONFIRMED"})[0]

    for caso_id in caso_ids:
        antes = rpc.TestCase.filter({"id": caso_id})[0]
        rpc.TestCase.update(caso_id, {"case_status": confirmed["id"]})
        despues = rpc.TestCase.filter({"id": caso_id})[0]
        print(json.dumps({
            "id": caso_id,
            "summary": antes["summary"],
            "antes": antes["case_status__name"],
            "despues": despues["case_status__name"],
        }))


if __name__ == "__main__":
    main()
