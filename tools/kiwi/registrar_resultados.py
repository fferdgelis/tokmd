# -*- coding: utf-8 -*-
"""Aplica a Kiwi el veredicto que trajo QA (Kimi K3 vía OpenCode). Este
script es el "adaptador controlado" (ia-evaluator/ADR-001): sólo traslada un
veredicto ya producido por QA, nunca decide uno. Desarrollo no debe llamarlo
con un resultado propio.

Sólo marca PASSED lo que QA ejecutó de verdad, con evidencia. Lo que no
aparece en el veredicto queda IDLE.

Uso: por stdin, un JSON con:
{
  "password": "...",
  "run_id": 123,
  "veredictos": [
    {"caso": "TOK-001-C01 - ...", "status": "PASSED", "evidencia": "..."},
    ...
  ]
}
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
    veredictos = entrada["veredictos"]

    rpc = connect(username=username, password=password)
    password = None

    ejecuciones = rpc.TestExecution.filter({"run": run_id})
    por_summary = {}
    for ejecucion in ejecuciones:
        caso = rpc.TestCase.filter({"id": ejecucion["case"]})[0]
        por_summary[caso["summary"]] = ejecucion

    aplicados = 0
    no_encontrados = []
    for v in veredictos:
        ejecucion = por_summary.get(v["caso"])
        if not ejecucion:
            no_encontrados.append(v["caso"])
            continue
        estado = rpc.TestExecutionStatus.filter({"name": v["status"]})
        if not estado:
            raise SystemExit(f"Estado '{v['status']}' no existe en Kiwi.")
        rpc.TestExecution.update(ejecucion["id"], {"status": estado[0]["id"]})
        if v.get("evidencia"):
            rpc.TestExecution.add_comment(ejecucion["id"], v["evidencia"])
        aplicados += 1
        print(f"{v['caso']}: {v['status']} (execution_id={ejecucion['id']})")

    if no_encontrados:
        print(f"AVISO: {len(no_encontrados)} casos del veredicto no se encontraron en el run: {no_encontrados}")

    print(f"\nTotal aplicados: {aplicados}")


if __name__ == "__main__":
    main()
