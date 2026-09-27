# -*- coding: utf-8 -*-
"""Carga a Kiwi el plan y los 15 casos de PBI-009, y registra BUG-008/009/010.

IDEMPOTENTE: filtra por summary antes de crear, igual que cargar_casos.py.
Los casos se cargan como PROPOSED y ANTES de escribir el codigo, que es la
regla del metodo de QA (los doce pasos, punto 12).

Contrasena de Kiwi por stdin, cruda. Fuente de los casos:
docs/PBI/PBI-009-casos-de-prueba.md

TRAMPA PAGADA (27/09/2026): el contenedor publica su 8443 en el 443 de
Windows. El default port=8443 de rpc_client.connect sirve solo corriendo
ADENTRO del contenedor. Desde Windows hay que pasar port=443.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpc_client import connect

PRODUCTO = "tokmd"
VERSION = "1.0.0"
BUILD = "d9c42ff"
AUTOR_USERNAME = "claude-code-sonnet"
PLAN_NOMBRE = "PBI-009 - Defaults del CLI y total"
PLAN_TIPO = "Unit"

# (id, categoria, componente, summary, texto)
CASOS = [
    # --- Bloque A: defaults del CLI ---
    ("TOK-009-C01", "Functional", "CLI",
     "TOK-009-C01 - tokmd archivo.md corre sin ninguna opcion",
     "Dado un archivo Markdown valido, cuando se corre `tokmd archivo.md` SIN ninguna "
     "opcion, entonces sale con codigo 0 y no aparece ningun mensaje de tipo "
     "'Missing option'. (AC-01)\n\n"
     "QUE FALLA CAZA: volver --platform a required=True."),
    ("TOK-009-C02", "Functional", "CLI",
     "TOK-009-C02 - Sin --platform la plataforma resuelta es claude-code",
     "Dado que no se pasa --platform, cuando se corre `tokmd archivo.md`, entonces la "
     "salida es IDENTICA a `tokmd archivo.md --platform claude-code`. (AC-03)\n\n"
     "QUE FALLA CAZA: cambiar el default a codex o a cualquier otra plataforma."),
    ("TOK-009-C03", "Functional", "CLI",
     "TOK-009-C03 - La salida por defecto es el total, no el desglose",
     "Dado un archivo valido, cuando se corre `tokmd archivo.md`, entonces se imprime "
     "UNA linea con el total y NO aparece el desglose por secciones. (AC-03)\n\n"
     "QUE FALLA CAZA: dejar la tabla como salida por defecto."),
    ("TOK-009-C04", "Functional", "CLI",
     "TOK-009-C04 - --platform codex explicito sigue funcionando",
     "Dado --platform codex explicito, cuando se corre el comando, entonces resuelve el "
     "tokenizador de OpenAI, sin regresion de PBI-004. (AC-04)\n\n"
     "QUE FALLA CAZA: que el default de claude-code pise el valor explicito."),

    # --- Bloque B: el total es el valor real ---
    ("TOK-009-C05", "Functional", "Render",
     "TOK-009-C05 - El total es el del archivo de una pasada, no la suma de filas",
     "Dado el CLAUDE.md global sin editar, cuando se corre `tokmd CLAUDE.md`, entonces "
     "informa 17376 exacto (dato dorado medido 2026-09-27, ctok familia 4.8). (AC-02)\n\n"
     "QUE FALLA CAZA: calcular el total sumando filas con el metodo viejo."),
    ("TOK-009-C06", "Edge case", "Render",
     "TOK-009-C06 - Archivo vacio informa 0 sin traceback",
     "Dado tests/fixtures/empty.md.fixture, cuando se corre el comando, entonces informa "
     "0, sale con codigo 0 y NO tira traceback. (AC-09)\n\n"
     "QUE FALLA CAZA: que el camino del total no maneje texto vacio."),
    ("TOK-009-C07", "Edge case", "Render",
     "TOK-009-C07 - Archivo sin ningun encabezado informa el total",
     "Dado tests/fixtures/no_headings.md.fixture, cuando se corre el comando, entonces "
     "informa el total sin fallar. (AC-08)\n\n"
     "QUE FALLA CAZA: que el total dependa de que exista al menos un encabezado."),

    # --- Bloque C: regresion de BUG-008 ---
    ("TOK-009-C08", "Functional", "Sections parser",
     "TOK-009-C08 - Una seccion con encabezado no vacio no puede dar Own=0",
     "Dado un archivo con encabezados SIN cuerpo (# usado como comentario, el caso real "
     "del CLAUDE.md de Fabian), cuando se pide --sections, entonces NINGUNA fila con "
     "encabezado no vacio informa Own=0. (AC-10, regresion de BUG-008)\n\n"
     "QUE FALLA CAZA: volver content_start a token.map[1]."),
    ("TOK-009-C09", "Functional", "Sections parser",
     "TOK-009-C09 - El titulo del encabezado esta contado en su propia seccion",
     "Dado un archivo con un unico encabezado de texto conocido y cuerpo conocido, cuando "
     "se pide --sections, entonces el Own de esa fila INCLUYE los tokens del titulo. "
     "(AC-11, regresion de BUG-008)\n\n"
     "QUE FALLA CAZA: no contar el titulo, o contarlo en el padre en vez de en la seccion."),

    # --- Bloque D: regresion de BUG-009 (ADR-003) ---
    ("TOK-009-C10", "Functional", "Render",
     "TOK-009-C10 - Cada fila muestra Own y Total como dos numeros distinguibles",
     "Dado --sections, cuando se corre, entonces cada fila muestra Own Y Total como dos "
     "numeros distinguibles, como decidio ADR-003. (AC-12, regresion de BUG-009)\n\n"
     "QUE FALLA CAZA: volver Row a un solo campo tokens."),
    ("TOK-009-C11", "Functional", "Render",
     "TOK-009-C11 - Hay una fila raiz con el total del archivo",
     "Dado --sections, cuando se corre, entonces existe una fila raiz (nivel 0) cuyo Total "
     "es el total del archivo. (AC-13, regresion de BUG-009)\n\n"
     "QUE FALLA CAZA: volver a `return rows[1:]`, que descarta la raiz."),
    ("TOK-009-C12", "Functional", "Render",
     "TOK-009-C12 - Own != Total en una seccion con hijos que pesan",
     "Dado un archivo con un padre de cuerpo corto y un hijo de cuerpo largo, cuando se "
     "pide --sections, entonces en la fila del padre Own < Total. (AC-14, regresion de "
     "BUG-009)\n\n"
     "QUE FALLA CAZA: hacer que Own sea igual a Total, o sea no implementar Own de verdad."),

    # --- Bloque E: regresion de BUG-010 (ADR-002) ---
    ("TOK-009-C13", "Functional", "Render",
     "TOK-009-C13 - Si la suma de Own no coincide con el total, se informa",
     "Dado un archivo donde la suma de los Own no coincide con el total contado de una "
     "pasada, cuando se pide --sections, entonces se informa la deriva con su signo en vez "
     "de esconderla. (AC-15, regresion de BUG-010)\n\n"
     "QUE FALLA CAZA: borrar la linea de deriva, o imprimirla siempre en 0 sin calcularla."),

    # --- El caso que verifica el requisito del owner ---
    ("TOK-009-C14", "Functional", "Render",
     "TOK-009-C14 - La suma de Own es EXACTAMENTE el total, en cualquier archivo",
     "Dado cualquier archivo, con front matter o sin el, cuando se pide --sections, "
     "entonces boundary drift es exactamente +0. (AC-17)\n\n"
     "ES EL CASO MAS IMPORTANTE: verifica de punta a punta el requisito de Fabian de que "
     "el parser y el total den el mismo valor y que ese valor sea el real. YA ESTA MEDIDO "
     "QUE PASA: 17 archivos, residuo 0 en todos (ADR-007, 2026-09-27).\n\n"
     "QUE FALLA CAZA: restar el costo fijo por seccion en vez de por corte; usar 6 en vez "
     "de 5; no absorber las lineas en blanco al front matter."),
    ("TOK-009-C15", "Functional", "Render",
     "TOK-009-C15 - El desglose usa conectores de arbol",
     "Dado tests/fixtures/sample.md.fixture, cuando se pide --sections, entonces las filas "
     "anidadas se dibujan con los conectores de arbol, no con espacios. Variante B, "
     "aprobada por Fabian el 2026-09-27.\n\n"
     "QUE FALLA CAZA: volver a la indentacion por espacios."),
]

# (summary, severidad)
BUGS = [
    ("BUG-008: el texto de los encabezados no se cuenta en ninguna fila -- "
     "tokmd subestima 1472 tokens (8,5%) en el CLAUDE.md global", "High"),
    ("BUG-009: ADR-003 pidio arbol con Own y Total y fila raiz -- el codigo "
     "tiene una sola columna y descarta la raiz", "High"),
    ("BUG-010: ADR-002 promete imprimir 'boundary drift: +-N' y ese codigo "
     "no existe", "Medium"),
]


def uno(lista, que):
    if not lista:
        raise SystemExit(f"no se encontro {que}")
    return lista[0]


def main():
    username = os.environ.get("KIWI_USER", "qa-bot")
    password = sys.stdin.readline().rstrip("\r\n")
    if not password:
        raise SystemExit("Falta la contrasena Kiwi por stdin.")
    # El 8443 del contenedor sale por el 443 de Windows.
    rpc = connect(host="127.0.0.1", port=443, username=username, password=password)
    password = None

    print("[1/5] Resolviendo producto, version y autor ...")
    producto = uno(rpc.Product.filter({"name": PRODUCTO}), f"producto {PRODUCTO}")
    version = uno(rpc.Version.filter({"product": producto["id"], "value": VERSION}),
                  f"version {VERSION}")
    autor = uno(rpc.User.filter({"username": AUTOR_USERNAME}), f"usuario {AUTOR_USERNAME}")
    print(f"      producto id={producto['id']}  version id={version['id']}  autor id={autor['id']}")

    print("[2/5] Plan del PBI-009 ...")
    planes = rpc.TestPlan.filter({"product": producto["id"], "name": PLAN_NOMBRE})
    if planes:
        plan = planes[0]
        print(f"      ya existia, id={plan['id']}")
    else:
        tipo = uno(rpc.PlanType.filter({"name": PLAN_TIPO}), f"plan type {PLAN_TIPO}")
        plan = rpc.TestPlan.create({
            "name": PLAN_NOMBRE,
            "product": producto["id"],
            "product_version": version["id"],
            "type": tipo["id"],
            "is_active": True,
            "text": ("Casos de PBI-009 (defaults del CLI y total) y regresion de "
                     "BUG-008, BUG-009 y BUG-010. Fuente: "
                     "docs/PBI/PBI-009-casos-de-prueba.md"),
        })
        print(f"      CREADO id={plan['id']}")

    print(f"[3/5] Cargando {len(CASOS)} casos como PROPOSED ...")
    creados = actualizados = 0
    for id_caso, cat_nombre, comp_nombre, summary, texto in CASOS:
        categoria = uno(rpc.Category.filter({"product": producto["id"], "name": cat_nombre}),
                        f"categoria {cat_nombre}")
        valores = {
            "product": producto["id"],
            "category": categoria["id"],
            "summary": summary,
            "priority": 2,
            "text": texto,
            "is_automated": True,
        }
        existentes = rpc.TestCase.filter({"summary": summary, "category": categoria["id"]})
        if existentes:
            tc_id = existentes[0]["id"]
            rpc.TestCase.update(tc_id, valores)
            actualizados += 1
            accion = "ACTUALIZADO"
        else:
            valores["case_status"] = 1  # PROPOSED, solo al crear
            tc_id = rpc.TestCase.create(valores)["id"]
            creados += 1
            accion = "CREADO"
        rpc.TestCase.update(tc_id, {"author": autor["id"]})

        comps = rpc.Component.filter({"product": producto["id"], "name": comp_nombre})
        if comps:
            try:
                rpc.TestCase.add_component(tc_id, comps[0]["name"])
            except Exception:
                pass

        if not rpc.TestCase.filter({"plan": plan["id"], "id": tc_id}):
            rpc.TestPlan.add_case(plan["id"], tc_id)
            vinculo = "vinculado"
        else:
            vinculo = "ya estaba"
        print(f"      {id_caso}: id={tc_id} {accion}, {vinculo} al plan [{comp_nombre}]")
    print(f"      Total casos: {creados} creados, {actualizados} actualizados.")

    print(f"[4/5] Resolviendo el build {BUILD} ...")
    # TRAMPA: Bug.create espera el ID del Build, no su nombre. Con el string
    # del commit devuelve "Select a valid choice" (verificado 2026-09-27).
    builds = rpc.Build.filter({"version": version["id"], "name": BUILD})
    if builds:
        build = builds[0]
        print(f"      ya existia, id={build['id']}")
    else:
        build = rpc.Build.create({"name": BUILD, "version": version["id"], "is_active": True})
        print(f"      CREADO id={build['id']}")

    print(f"[5/6] Registrando {len(BUGS)} bugs ...")
    existentes_bugs = {b["summary"] for b in rpc.Bug.filter({})}
    for summary, sev_nombre in BUGS:
        if summary in existentes_bugs:
            print(f"      ya existia: {summary[:60]}")
            continue
        # El metodo es Severity.filter, NO BugSeverity.filter (verificado
        # 2026-09-27 con rpc.system.listMethods()).
        sev = uno(rpc.Severity.filter({"name": sev_nombre}), f"severidad {sev_nombre}")
        creado = rpc.Bug.create({
            "summary": summary,
            "product": producto["id"],
            "version": version["id"],
            "build": build["id"],
            "reporter": autor["id"],
            "severity": sev["id"],
            "status": True,  # True = abierto. No existe Bug.update: se pasa al crear.
        })
        print(f"      CREADO pk={creado.get('pk', creado.get('id'))} [{sev_nombre}]: {summary[:58]}")

    print("[6/6] Listo.")


if __name__ == "__main__":
    main()
