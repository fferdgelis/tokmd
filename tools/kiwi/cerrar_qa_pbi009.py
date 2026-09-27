# -*- coding: utf-8 -*-
"""Cierra el ciclo de QA de PBI-009 en Kiwi: crea el Test Run sobre el
build de la implementacion, marca las 17 Test Execution con el veredicto
real de QA (Kimi K3/OpenCode, ver tools/qa/brief-qa-pbi009.md.prompt y su
resultado crudo), y linkea los cuatro bugs a la Test Execution que
corresponde via Bug.add_execution (no existe Bug.update en la API de
Kiwi: el estado del Bug no se puede pisar por API, se cierra a mano en
/admin si Fabian lo decide).

IDEMPOTENTE: reusa el TestRun/TestExecution si ya existen.

TRAMPA (ya documentada): el contenedor publica su 8443 en el 443 de
Windows; hay que conectar con port=443, no con el default de rpc_client.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpc_client import connect

PRODUCTO = "tokmd"
VERSION = "1.0.0"
PLAN_NOMBRE = "PBI-009 - Defaults del CLI y total"
COMMIT_IMPLEMENTACION = "421b8cb"
TESTED_BY_USERNAME = "claude-code-sonnet"  # unico usuario tecnico disponible

# (caso_id, status, evidencia)
VEREDICTOS = [
    ("TOK-009-C01", "PASSED", "test_default_platform_no_missing_option PASSED en corrida completa (77 passed)"),
    ("TOK-009-C02", "PASSED", "test_omitting_platform_equals_explicit_claude_code PASSED"),
    ("TOK-009-C03", "PASSED", "test_default_output_is_digits_only_and_matches_claude_code PASSED"),
    ("TOK-009-C04", "PASSED", "test_explicit_codex_platform_not_overridden PASSED"),
    ("TOK-009-C05", "PASSED", "uv run tokmd local/qa-fixtures/claude-md-global.md devolvio exactamente 17381"),
    ("TOK-009-C06", "PASSED", "test_empty_file_outputs_zero PASSED"),
    ("TOK-009-C07", "PASSED", "test_no_headings_file_outputs_digits_only PASSED"),
    ("TOK-009-C08", "PASSED", "test_heading_only_sections_have_nonempty_own_text PASSED"),
    ("TOK-009-C09", "PASSED", "test_heading_own_text_includes_heading_line_and_invariant_holds PASSED"),
    ("TOK-009-C10", "PASSED", "test_table_shows_root_and_section_rows_and_uneven_own_total PASSED"),
    ("TOK-009-C11", "PASSED", "test_root_total_is_injected_value_not_summed PASSED"),
    ("TOK-009-C12", "PASSED", "test_uneven_parent_own_less_than_total PASSED"),
    ("TOK-009-C13", "PASSED", "test_drift_positive_and_negative PASSED y test_drift_zero PASSED"),
    ("TOK-009-C14", "PASSED", "uv run tokmd local/qa-fixtures/claude-md-global.md --sections: boundary drift: +0"),
    ("TOK-009-C15", "PASSED", "test_tree_connectors_table_only PASSED"),
    ("TOK-009-C16", "PASSED", "test_windows_encoding_no_unicode_encode_error PASSED en table/md/csv/json"),
    ("TOK-009-C17", "PASSED", "test_windows_encoding_arrow_survives PASSED"),
]

# caso -> bug relacionado, para Bug.add_execution
CASO_A_BUG_PK = {
    "TOK-009-C08": 9, "TOK-009-C09": 9,           # BUG-008
    "TOK-009-C10": 10, "TOK-009-C11": 10, "TOK-009-C12": 10,  # BUG-009
    "TOK-009-C13": 11,                             # BUG-010
    "TOK-009-C16": 13, "TOK-009-C17": 13,          # BUG-011
}


def uno(lista, que):
    if not lista:
        raise SystemExit(f"no se encontro {que}")
    return lista[0]


def main():
    username = os.environ.get("KIWI_USER", "qa-bot")
    password = sys.stdin.readline().rstrip("\r\n")
    if not password:
        raise SystemExit("Falta la contrasena Kiwi por stdin.")
    rpc = connect(host="127.0.0.1", port=443, username=username, password=password)
    password = None

    print("[1/5] Resolviendo producto, version, plan y build ...")
    producto = uno(rpc.Product.filter({"name": PRODUCTO}), f"producto {PRODUCTO}")
    version = uno(rpc.Version.filter({"product": producto["id"], "value": VERSION}), f"version {VERSION}")
    plan = uno(rpc.TestPlan.filter({"name": PLAN_NOMBRE, "product": producto["id"]}), f"plan {PLAN_NOMBRE}")
    tested_by = uno(rpc.User.filter({"username": TESTED_BY_USERNAME}), f"usuario {TESTED_BY_USERNAME}")

    builds = rpc.Build.filter({"version": version["id"], "name": COMMIT_IMPLEMENTACION})
    if builds:
        build = builds[0]
        print(f"      build ya existia, id={build['id']}")
    else:
        build = rpc.Build.create({"name": COMMIT_IMPLEMENTACION, "version": version["id"], "is_active": True})
        print(f"      build CREADO id={build['id']}")

    print("[2/5] Test Run ...")
    resumen_run = f"{PLAN_NOMBRE} . build {COMMIT_IMPLEMENTACION} . kimi-k3/opencode"
    runs = rpc.TestRun.filter({"summary": resumen_run, "plan": plan["id"]})
    if runs:
        run = runs[0]
        print(f"      ya existia, id={run['id']}")
    else:
        run = rpc.TestRun.create({
            "summary": resumen_run,
            "plan": plan["id"],
            "build": build["id"],
            "manager": tested_by["id"],
            "default_tester": tested_by["id"],
            "notes": "QA independiente: Kimi K3/OpenCode, read-only sobre snapshot. Brief: tools/qa/brief-qa-pbi009.md.prompt.",
        })
        print(f"      CREADO id={run['id']}")

    print("[3/5] Test Executions (una por caso del plan) ...")
    casos_por_summary_prefix = {}
    for c in rpc.TestCase.filter({"plan": plan["id"]}):
        for caso_id, _, _ in VEREDICTOS:
            if c["summary"].startswith(caso_id + " - "):
                casos_por_summary_prefix[caso_id] = c
    ejecucion_por_caso = {}
    for caso_id, caso in casos_por_summary_prefix.items():
        existentes = rpc.TestExecution.filter({"run": run["id"], "case": caso["id"]})
        if existentes:
            ejecucion_por_caso[caso_id] = existentes[0]
        else:
            # case_text_version/status/build son obligatorios y no tienen
            # default server-side (verificado 2026-09-27): arranca en IDLE
            # (1), version de texto 1, sobre el mismo build del run. El
            # veredicto real se aplica despues con TestExecution.update.
            ejecucion_por_caso[caso_id] = rpc.TestExecution.create({
                "run": run["id"],
                "case": caso["id"],
                "case_text_version": 1,
                "status": 1,
                "build": build["id"],
            })
    print(f"      {len(ejecucion_por_caso)} ejecuciones listas")

    print("[4/5] Aplicando veredictos ...")
    for caso_id, status, evidencia in VEREDICTOS:
        ejecucion = ejecucion_por_caso.get(caso_id)
        if not ejecucion:
            print(f"      {caso_id}: NO ENCONTRADO en el plan, salteado")
            continue
        # Ids reales de TestExecutionStatus en esta instancia (verificado con
        # system.methodHelp/TestExecutionStatus.filter, 2026-09-27): IDLE=1,
        # RUNNING=2, PAUSED=3, PASSED=4, FAILED=5, BLOCKED=6, ERROR=7, WAIVED=8.
        rpc.TestExecution.update(ejecucion["id"], {
            "status": {"PASSED": 4, "FAILED": 5, "BLOCKED": 6}.get(status, 7),
            "tested_by": tested_by["id"],
        })
        rpc.TestExecution.add_comment(ejecucion["id"], evidencia)
        print(f"      {caso_id}: {status}")

    print("[5/5] Linkeando bugs a su Test Execution (Bug.add_execution) ...")
    for caso_id, bug_pk in CASO_A_BUG_PK.items():
        ejecucion = ejecucion_por_caso.get(caso_id)
        if not ejecucion:
            continue
        try:
            rpc.Bug.add_execution(bug_pk, ejecucion["id"])
            print(f"      Bug pk={bug_pk} <- Test Execution {ejecucion['id']} ({caso_id})")
        except Exception as exc:
            print(f"      Bug pk={bug_pk}: {exc}")

    print("\nListo. Run id=", run["id"])


if __name__ == "__main__":
    main()
