# -*- coding: utf-8 -*-
"""Revierte un Test Run marcado como Stop por error: limpia stop_date para
que deje de aparecer tachado/finalizado. No toca nada mas.

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

    antes = rpc.TestRun.filter({"id": run_id})[0]
    rpc.TestRun.update(run_id, {"stop_date": None})
    despues = rpc.TestRun.filter({"id": run_id})[0]
    print(json.dumps({
        "antes": {"start_date": antes["start_date"], "stop_date": antes["stop_date"]},
        "despues": {"start_date": despues["start_date"], "stop_date": despues["stop_date"]},
    }))


if __name__ == "__main__":
    main()
