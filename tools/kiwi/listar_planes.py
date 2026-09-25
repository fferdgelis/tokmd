# -*- coding: utf-8 -*-
"""Lista todos los planes de tokmd, solo lectura. Para diagnosticar nombres
exactos antes de crear nada nuevo.

Uso: por stdin, {"password": "..."}
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

    rpc = connect(username=username, password=password)
    password = None

    producto = rpc.Product.filter({"name": PRODUCTO})[0]
    planes = rpc.TestPlan.filter({"product": producto["id"]})
    for plan in sorted(planes, key=lambda p: p["id"]):
        print(json.dumps({"id": plan["id"], "name": plan["name"]}))


if __name__ == "__main__":
    main()
