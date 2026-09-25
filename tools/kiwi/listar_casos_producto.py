# -*- coding: utf-8 -*-
"""Lista TODOS los casos del producto (no de un plan puntual), con
is_automated, para verificar cargas masivas. Solo lectura.

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
    casos = rpc.TestCase.filter({"category__product": producto["id"]})
    por_summary = {}
    for caso in casos:
        por_summary.setdefault(caso["summary"], []).append(caso["id"])

    duplicados = {s: ids for s, ids in por_summary.items() if len(ids) > 1}

    for caso in sorted(casos, key=lambda c: c["id"]):
        print(json.dumps({"id": caso["id"], "summary": caso["summary"], "is_automated": caso["is_automated"]}))

    print(json.dumps({"total": len(casos), "no_automatizados": sum(1 for c in casos if not c["is_automated"]), "duplicados": duplicados}))


if __name__ == "__main__":
    main()
