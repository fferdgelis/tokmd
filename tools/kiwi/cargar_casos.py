# -*- coding: utf-8 -*-
"""Carga los Test Case de tokmd, PROPOSED, a partir de los AC de cada PBI.

IDEMPOTENTE: filtra por summary antes de crear. Se cargan ANTES de escribir
el código de la fase correspondiente (regla de los doce pasos, punto 12 del
método de QA: los casos se registran antes de ejecutar).

Id de caso: TOK-<PBI>-C<nn>. Categoria y componente se resuelven por nombre.
"""
import os
import sys

sys.path.insert(0, "/tmp/work")
from rpc_client import connect

PRODUCTO = "tokmd"
CATEGORIA_DEFAULT = "Functional"

# (id_caso, pbi, plan, categoria, componente, summary, texto, prioridad)
# Prioridad Kiwi: 1=P1 ... por defecto usamos 2 (P2) salvo que se indique.
CASOS = [
    # PBI-001 - Parser de secciones
    ("TOK-001-C01", "PBI-001 - Parser de secciones", "Functional", "Sections parser",
     "TOK-001-C01 - Front matter se detecta como fila propia",
     "Dado un archivo con front matter YAML delimitado por ---, cuando se parsea, "
     "entonces aparece una fila (front matter) con su texto completo. (AC-01)"),
    ("TOK-001-C02", "PBI-001 - Parser de secciones", "Functional", "Sections parser",
     "TOK-001-C02 - Preambulo antes del primer encabezado",
     "Dado texto antes del primer encabezado, cuando se parsea, entonces aparece "
     "una fila (preamble) con ese texto. (AC-02)"),
    ("TOK-001-C03", "PBI-001 - Parser de secciones", "Edge case", "Sections parser",
     "TOK-001-C03 - Salto de nivel de encabezado sin error",
     "Dado un salto de nivel (## seguido de ####), cuando se parsea, entonces el "
     "nodo hijo cuelga del ancestro de nivel inmediatamente menor sin excepcion. (AC-03)"),
    ("TOK-001-C04", "PBI-001 - Parser de secciones", "Edge case", "Sections parser",
     "TOK-001-C04 - Encabezado dentro de bloque de codigo se ignora",
     "Dado un caracter # dentro de un bloque de codigo delimitado por ```, cuando "
     "se parsea, entonces no se trata como encabezado real. (AC-04)"),
    ("TOK-001-C05", "PBI-001 - Parser de secciones", "Edge case", "Sections parser",
     "TOK-001-C05 - Archivo vacio o sin encabezados",
     "Dado un archivo vacio o sin ningun encabezado, cuando se parsea, entonces "
     "se devuelve un arbol valido sin excepcion. (AC-05)"),

    # PBI-002 - Tokenizador Claude
    ("TOK-002-C01", "PBI-002 - Tokenizador Claude", "Functional", "Tokenizers",
     "TOK-002-C01 - Marco medido y documentado por familia",
     "Dado un texto vacio, cuando se mide FRAME por familia (3, 4.7, 4.8), entonces "
     "el valor queda documentado en docs/investigation/20260924-ctok-marco-y-deriva.md. (AC-01)"),
    ("TOK-002-C02", "PBI-002 - Tokenizador Claude", "Edge case", "Tokenizers",
     "TOK-002-C02 - Deriva de borde reportada, no oculta",
     "Dado el archivo completo y la suma de sus secciones, cuando se comparan, "
     "entonces la deriva (si existe) se reporta explicitamente. (AC-02)"),
    ("TOK-002-C03", "PBI-002 - Tokenizador Claude", "Functional", "Tokenizers",
     "TOK-002-C03 - Las tres familias dan valores distintos y consistentes",
     "Dado --claude-family 3|4.7|4.8 sobre el mismo texto, cuando se cuenta, "
     "entonces los tres valores son distintos, con ~30% mas desde 4.7. (AC-03)"),

    # PBI-003 - Tokenizador OpenAI
    ("TOK-003-C01", "PBI-003 - Tokenizador OpenAI", "Functional", "Tokenizers",
     "TOK-003-C01 - Conteo exacto y determinista con o200k_base",
     "Dado un texto, cuando se cuenta con o200k_base, entonces el resultado es "
     "exacto y determinista entre corridas. (AC-01)"),
    ("TOK-003-C02", "PBI-003 - Tokenizador OpenAI", "Edge case", "Tokenizers",
     "TOK-003-C02 - Deriva de borde medida y reportada, no oculta",
     "Dado el mismo texto partido en secciones, cuando se suman los conteos, "
     "entonces la deriva contra el conteo del texto completo (si existe) se mide "
     "y se puede reportar - no se asume aditividad exacta. (AC-02, corregido "
     "2026-09-25: la hipotesis original de aditividad exacta era falsa, ver "
     "docs/investigation/20260925-tiktoken-deriva.md)"),
    ("TOK-003-C03", "PBI-003 - Tokenizador OpenAI", "Functional", "Tokenizers",
     "TOK-003-C03 - cl100k_base reproduce la medicion del 20/09",
     "Dado --encoding cl100k_base, cuando se cuenta, entonces el resultado "
     "reproduce lo que dio ttok -m gpt-4 el 20/09/2026. (AC-03)"),

    # PBI-004 - CLI y plataformas
    ("TOK-004-C01", "PBI-004 - CLI y plataformas", "Functional", "CLI",
     "TOK-004-C01 - platform claude-code usa Claude 4.8 por defecto",
     "Dado --platform claude-code sin mas flags, cuando se corre, entonces usa "
     "el tokenizador de Claude familia 4.8. (AC-01)"),
    ("TOK-004-C02", "PBI-004 - CLI y plataformas", "Functional", "CLI",
     "TOK-004-C02 - platform codex usa o200k_base",
     "Dado --platform codex, cuando se corre, entonces usa OpenAI o200k_base. (AC-02)"),
    ("TOK-004-C03", "PBI-004 - CLI y plataformas", "Error", "CLI",
     "TOK-004-C03 - opencode sin --model falla con mensaje claro",
     "Dado --platform opencode sin --model, cuando se corre, entonces falla con "
     "un mensaje de error legible, no con una excepcion cruda. (AC-03)"),
    ("TOK-004-C04", "PBI-004 - CLI y plataformas", "Functional", "CLI",
     "TOK-004-C04 - opencode con --model claude-* usa Claude",
     "Dado --platform opencode --model claude-opus-5, cuando se corre, entonces "
     "usa el tokenizador de Claude. (AC-04)"),
    ("TOK-004-C05", "PBI-004 - CLI y plataformas", "Error", "CLI",
     "TOK-004-C05 - antigravity sale con codigo 2 y mensaje planned",
     "Dado --platform antigravity, cuando se corre, entonces sale con codigo 2 "
     "y el mensaje 'Gemini tokenizer: planned for 1.1'. (AC-05)"),

    # PBI-005 - Render de salida
    ("TOK-005-C01", "PBI-005 - Render de salida", "Functional", "Render",
     "TOK-005-C01 - format json es JSON valido",
     "Dado --format json, cuando se corre, entonces la salida es JSON valido y "
     "parseable. (AC-01)"),
    ("TOK-005-C02", "PBI-005 - Render de salida", "Functional", "Render",
     "TOK-005-C02 - format table indenta por nivel",
     "Dado --format table (default), cuando se corre, entonces la indentacion "
     "refleja el nivel de anidamiento. (AC-02)"),
    ("TOK-005-C03", "PBI-005 - Render de salida", "Functional", "Render",
     "TOK-005-C03 - depth limita niveles sin romper totales",
     "Dado --depth 2, cuando se corre, entonces solo se muestran secciones "
     "hasta nivel 2, con sus totales acumulados intactos. (AC-03)"),
    ("TOK-005-C04", "PBI-005 - Render de salida", "Functional", "Render",
     "TOK-005-C04 - sort tokens ordena de mayor a menor",
     "Dado --sort tokens, cuando se corre, entonces las filas del mismo nivel "
     "se ordenan de mayor a menor cantidad de tokens. (AC-04)"),

    # PBI-006 - Verificacion contra la API
    ("TOK-006-C01", "PBI-006 - Verificacion contra la API", "Error", "Verify",
     "TOK-006-C01 - Sin ANTHROPIC_API_KEY, error legible",
     "Dado ANTHROPIC_API_KEY ausente del entorno, cuando se llama get_client(), "
     "entonces se levanta MissingApiKeyError y el mensaje nombra la variable "
     "faltante. (AC-01)"),
    ("TOK-006-C02", "PBI-006 - Verificacion contra la API", "Functional", "Verify",
     "TOK-006-C02 - count_verified resta el marco medido",
     "Dado un cliente falso con conteos fijos, cuando se llama measure_frame y "
     "count_verified, entonces el resultado es el conteo crudo menos el marco. "
     "(AC-02, parcial: no incluye el cableado de columnas API/Delta en cli.py, "
     "ver nota de alcance del PBI)"),
    ("TOK-006-C03", "PBI-006 - Verificacion contra la API", "Security", "Verify",
     "TOK-006-C03 - Ninguna llamada de red real en la suite de tests",
     "Dado que corren todos los tests de verify.py, cuando se inspecciona "
     "sys.modules, entonces 'anthropic' nunca aparece importado. (AC-03)"),
    ("TOK-006-C04", "PBI-006 - Verificacion contra la API", "Edge case", "Verify",
     "TOK-006-C04 - Mutante del parser de front matter, cazado por el test suite",
     "Dado FRONT_MATTER_RE roto a proposito (paso 10 de los doce), cuando corre "
     "la suite completa, entonces exactamente un test falla y senala la ruptura "
     "exacta. Ejercicio ya ejecutado y revertido el 2026-09-25 (ver "
     "docs/PBI/PBI-006-verificacion-contra-api.md); QA verifica la evidencia "
     "registrada, no repite la mutacion (mantiene el rol de solo lectura). (AC-04)"),
]


def main():
    username = os.environ.get("KIWI_USER", "qa-bot")
    password = sys.stdin.readline().rstrip("\r\n")
    if not password:
        raise SystemExit("Falta la contraseña Kiwi por stdin.")

    rpc = connect(username=username, password=password)
    password = None

    producto = rpc.Product.filter({"name": PRODUCTO})
    if not producto:
        raise SystemExit(f"Producto '{PRODUCTO}' no existe. Correr crear_catalogo.py primero.")
    producto = producto[0]

    planes_cache = {}
    categorias_cache = {}

    creados = 0
    actualizados = 0

    for id_caso, plan_nombre, categoria_nombre, componente_nombre, summary, texto in CASOS:
        if plan_nombre not in planes_cache:
            planes = rpc.TestPlan.filter({"name": plan_nombre, "product": producto["id"]})
            if not planes:
                raise SystemExit(f"Plan '{plan_nombre}' no existe. Correr crear_planes.py primero.")
            planes_cache[plan_nombre] = planes[0]
        plan = planes_cache[plan_nombre]

        if categoria_nombre not in categorias_cache:
            cats = rpc.Category.filter({"product": producto["id"], "name": categoria_nombre})
            if not cats:
                raise SystemExit(f"Categoria '{categoria_nombre}' no existe. Correr crear_catalogo.py primero.")
            categorias_cache[categoria_nombre] = cats[0]
        categoria = categorias_cache[categoria_nombre]

        valores = {
            "category": categoria["id"],
            "summary": summary,
            "priority": 2,
            "text": texto,
            "is_automated": False,
        }

        existentes = rpc.TestCase.filter({"summary": summary, "category": categoria["id"]})
        if existentes:
            tc_id = existentes[0]["id"]
            # BUG evitado (lección de ia-evaluator, 30/08/2026): nunca actualizar
            # case_status en una re-corrida, o se pisa la aprobación de Fabián
            # de vuelta a PROPOSED sin que nadie lo pida.
            rpc.TestCase.update(tc_id, valores)
            actualizados += 1
            accion = "ACTUALIZADO"
        else:
            valores["case_status"] = 1  # PROPOSED, sólo en creación
            creado = rpc.TestCase.create(valores)
            tc_id = creado["id"]
            creados += 1
            accion = "CREADO"

        ya_en_plan = rpc.TestCase.filter({"plan": plan["id"], "id": tc_id})
        if not ya_en_plan:
            rpc.TestPlan.add_case(plan["id"], tc_id)
            vinculo = "vinculado al plan"
        else:
            vinculo = "ya estaba en el plan"

        print(f"{id_caso}: {summary} (id={tc_id}) {accion}, {vinculo} '{plan_nombre}' [componente sugerido: {componente_nombre}]")

    print(f"\nTotal: {creados} creados, {actualizados} actualizados.")


if __name__ == "__main__":
    main()
