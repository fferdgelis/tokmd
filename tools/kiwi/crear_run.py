# -*- coding: utf-8 -*-
"""Crea un Test Run para un plan de tokmd, con todas sus Test Execution en
IDLE (ADR-005). Se corre al cerrar el desarrollo de una fase, ANTES de
llamar a QA. Nunca marca PASSED/FAILED: eso lo hace registrar_resultados.py
con el veredicto que trae QA (Kimi K3), nunca con un veredicto de Desarrollo.

Uso: se le pasa por stdin un JSON con:
  {"password": "...", "plan": "PBI-001 - Parser de secciones", "commit": "6be061d",
   "manager": "claude-code-sonnet", "qa": "opencode-kimi-k3"}
"manager"/"qa" son opcionales (default abajo) - identidades reales de Kiwi,
no el usuario de login (qa-bot). No las crea este script: User.create no
existe en la API de Kiwi, se dan de alta a mano en /admin primero.
"""
import json
import os
import sys

sys.path.insert(0, "/tmp/work")
from rpc_client import connect

PRODUCTO = "tokmd"
VERSION = "1.0.0"
MANAGER_USERNAME_DEFAULT = "claude-code-sonnet"
QA_USERNAME_DEFAULT = "opencode-kimi-k3"


def obtener_o_crear(recurso, filtro, valores):
    existentes = recurso.filter(filtro)
    if existentes:
        return existentes[0], False
    return recurso.create(valores), True


def main():
    username = os.environ.get("KIWI_USER", "qa-bot")
    entrada = json.loads(sys.stdin.read())
    password = entrada["password"]
    plan_nombre = entrada["plan"]
    commit = entrada["commit"]
    manager_username = entrada.get("manager", MANAGER_USERNAME_DEFAULT)
    qa_username = entrada.get("qa", QA_USERNAME_DEFAULT)

    rpc = connect(username=username, password=password)
    password = None

    producto = rpc.Product.filter({"name": PRODUCTO})[0]
    version = rpc.Version.filter({"product": producto["id"], "value": VERSION})[0]
    plan = rpc.TestPlan.filter({"name": plan_nombre, "product": producto["id"]})
    if not plan:
        raise SystemExit(f"Plan '{plan_nombre}' no existe.")
    plan = plan[0]

    manager = rpc.User.filter({"username": manager_username})
    if not manager:
        raise SystemExit(f"Usuario '{manager_username}' no existe en Kiwi. Crearlo primero en /admin.")
    qa = rpc.User.filter({"username": qa_username})
    if not qa:
        raise SystemExit(f"Usuario '{qa_username}' no existe en Kiwi. Crearlo primero en /admin.")

    build, _ = obtener_o_crear(
        rpc.Build,
        {"version": version["id"], "name": commit},
        {"version": version["id"], "name": commit, "is_active": True},
    )

    resumen_run = f"{plan_nombre} . build {commit} . kimi-k3/opencode"
    run, run_nuevo = obtener_o_crear(
        rpc.TestRun,
        {"summary": resumen_run, "plan": plan["id"], "build": build["id"]},
        {
            "summary": resumen_run,
            "plan": plan["id"],
            "build": build["id"],
            "manager": manager[0]["id"],
            "default_tester": qa[0]["id"],
            "notes": f"QA: {qa_username}, read-only sobre snapshot. Manager: {manager_username}.",
        },
    )
    print(f"TestRun: {run['summary']} (id={run['id']}) {'CREADO' if run_nuevo else 'ya existia'}")

    casos = rpc.TestCase.filter({"plan": plan["id"]})
    creadas = 0
    ya_existian = 0
    ejecuciones = {}
    for caso in casos:
        existentes = rpc.TestExecution.filter({"run": run["id"], "case": caso["id"]})
        if existentes:
            ejecucion = existentes[0]
            ya_existian += 1
        else:
            creado = rpc.TestRun.add_case(run["id"], caso["id"])
            ejecucion = creado[0] if isinstance(creado, list) else creado
            creadas += 1
        ejecuciones[caso["summary"]] = ejecucion["id"]

    print(f"Test Execution: {creadas} creadas (IDLE), {ya_existian} ya existian.")
    print(json.dumps({"run_id": run["id"], "build_id": build["id"], "executions": ejecuciones}))


if __name__ == "__main__":
    main()
