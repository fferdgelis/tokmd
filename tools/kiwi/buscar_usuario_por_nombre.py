# -*- coding: utf-8 -*-
"""Busca usuarios por username exacto (a diferencia de listar todos, que
qa-bot no puede por permisos) - solo lectura.

Uso: por stdin, {"password": "...", "usernames": ["claude-code-sonnet", "opencode-kimi-k3"]}
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
    nombres = entrada["usernames"]

    rpc = connect(username=username, password=password)
    password = None

    for nombre in nombres:
        try:
            resultado = rpc.User.filter({"username": nombre})
            print(json.dumps({"username": nombre, "resultado": resultado}))
        except Exception as e:
            print(json.dumps({"username": nombre, "error": str(e)}))


if __name__ == "__main__":
    main()
