# -*- coding: utf-8 -*-
"""Corrige retroactivamente manager/default_tester/tested_by en Test Runs
ya cerrados, a pedido explicito de Fabian (2026-09-25). No cambia status
ni evidencia de ninguna ejecucion, solo la identidad real de quien hizo
cada cosa.

Uso: por stdin, {"password": "...", "run_ids": [61,62,63,64,65],
                  "manager": "claude-code-sonnet", "qa": "opencode-kimi-k3"}
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
    run_ids = entrada["run_ids"]
    manager_username = entrada["manager"]
    qa_username = entrada["qa"]

    rpc = connect(username=username, password=password)
    password = None

    manager = rpc.User.filter({"username": manager_username})[0]
    qa = rpc.User.filter({"username": qa_username})[0]

    for run_id in run_ids:
        run_antes = rpc.TestRun.filter({"id": run_id})[0]
        rpc.TestRun.update(run_id, {"manager": manager["id"], "default_tester": qa["id"]})

        ejecuciones = rpc.TestExecution.filter({"run": run_id})
        for ejecucion in ejecuciones:
            rpc.TestExecution.update(ejecucion["id"], {"tested_by": qa["id"]})

        print(json.dumps({
            "run_id": run_id,
            "summary": run_antes["summary"],
            "manager_antes": run_antes["manager__username"],
            "manager_despues": manager_username,
            "default_tester_antes": run_antes["default_tester__username"],
            "default_tester_despues": qa_username,
            "ejecuciones_corregidas": len(ejecuciones),
        }))


if __name__ == "__main__":
    main()
