# -*- coding: utf-8 -*-
"""Lista usuarios visibles para qa-bot, solo lectura.

Uso: por stdin, {"password": "..."}
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

    rpc = connect(username=username, password=password)
    password = None

    usuarios = rpc.User.filter({})
    print(json.dumps({"total": len(usuarios), "usuarios": [u.get("username") for u in usuarios]}))


if __name__ == "__main__":
    main()
