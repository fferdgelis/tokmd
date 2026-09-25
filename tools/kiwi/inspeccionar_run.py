# -*- coding: utf-8 -*-
"""Inspecciona un Test Run completo (todos los campos), solo lectura.

Uso: por stdin, {"password": "...", "run_id": 61}
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
    run_id = entrada["run_id"]

    rpc = connect(username=username, password=password)
    password = None

    run = rpc.TestRun.filter({"id": run_id})[0]
    print(json.dumps(run, default=str))


if __name__ == "__main__":
    main()
