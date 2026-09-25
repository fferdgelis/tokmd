# -*- coding: utf-8 -*-
"""Lista los casos de un plan con su case_status, solo lectura.

Uso: por stdin, {"password": "...", "plan": "PBI-006 - Verificacion contra la API"}
"""
import json
import os
import sys

sys.path.insert(0, "/tmp/work")
from rpc_client import connect

PRODUCTO = "tokmd"


def main():
    username = os.environ.get("KIWI_USER", "qa-bot")
    entrada = json.loads(sys.stdin.read())
    password = entrada["password"]
    plan_nombre = entrada["plan"]

    rpc = connect(username=username, password=password)
    password = None

    producto = rpc.Product.filter({"name": PRODUCTO})[0]
    plan = rpc.TestPlan.filter({"name": plan_nombre, "product": producto["id"]})[0]
    casos = rpc.TestCase.filter({"plan": plan["id"]})
    for caso in sorted(casos, key=lambda c: c["id"]):
        print(json.dumps({"id": caso["id"], "summary": caso["summary"], "status": caso["case_status__name"]}))


if __name__ == "__main__":
    main()
