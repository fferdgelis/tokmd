---
title: "Configuración de motores y API keys: carpeta por sistema operativo, un archivo por motor, texto plano con permisos, 1Password por referencia"
aliases:
  - "Ronda de diseño motores y keys 20260930"
project: tokmd
document_type: decision-record
status: proposed
version: 0.1.0
created: 2026-09-30
updated: 2026-09-30
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-opus-5-5"
llm_harness: "Claude Code Desktop"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-opus-5-5 / Claude Code Desktop / subscription"
modified_by: "Anthropic / claude-opus-5-5 / Claude Code Desktop / subscription"
reviewed_by: "pending"
review_status: "pending"
source_of_truth: true
tags:
  - project/tokmd
  - decision
related_documents:
  - "[[ADR-008-registro-de-tokenizadores-por-configuracion]]"
  - "[[ADR-009-manejo-de-api-key-para-verify]]"
  - "[[PBI-011-api-key-interactiva-para-verify]]"
---

# Configuración de motores y API keys

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-opus-5-5 / Claude Code Desktop / subscription | Respuesta a la ronda «hable ahora o calle para siempre» de Fabián sobre PBI-011 v0.2.0. Cambia ADR-008 (un TOML → carpeta con un archivo por motor) y ADR-009 (keyring fuera de v1, texto plano con permisos, 1Password por referencia). Tres preguntas abiertas al final. |

## 1. Dónde vive la configuración, por sistema operativo

`/etc/<programa>/` es la convención de Linux para configuración **del
sistema**: la instala el administrador (root) o el gestor de paquetes, y
aplica a todos los usuarios. Sigue siendo así. Pero tokmd se instala con
`pip`/`uv` por usuario, sin root, y la key es de cada persona. Para eso la
convención vigente es XDG: `~/.config/<programa>/`. Las dos existen y se
usan juntas, como Nagios: el sistema pone el default, el usuario lo pisa.

| Sistema | Del usuario (lee y escribe) | Del sistema (sólo lee, lo pone un admin) |
|---|---|---|
| Windows | `%APPDATA%\tokmd\` | `%ProgramData%\tokmd\` |
| Linux | `$XDG_CONFIG_HOME/tokmd/` (por defecto `~/.config/tokmd/`) | `/etc/tokmd/` |
| macOS | `~/Library/Application Support/tokmd/` | `/Library/Application Support/tokmd/` |

Override de todo: variable `TOKMD_CONFIG_DIR`. Se resuelve con diez líneas
de Python, sin dependencias. **Lo de `ProgramData` que propuso Fabián queda:
es la capa del sistema en Windows.**

## 2. Motores: una carpeta con un archivo por motor (modelo Nagios)

Reemplaza el `tokenizers.toml` único de ADR-008:

```
~/.config/tokmd/
  engines/
    README.md            <- cómo se arma un archivo de motor
    claude-code.toml     <- entregado armado
    codex.toml           <- entregado armado
    deepseek.toml        <- entregado armado (ver nota)
```

Cada archivo es un motor completo, legible y editable con un editor de
texto: motor, parámetros y, si usa verificación online, su key. **No hay
archivo `credentials`**: la key vive dentro del archivo de su motor.

**SQLite, no para esto.** Un sysadmin no edita una base con el Bloc de
notas, no la puede comparar con `diff` ni versionar en git. Archivos para
la configuración; SQLite queda para lo que sí es una base: el historial de
mediciones del producto pago (opción C del informe de producto).

**Nota sobre DeepSeek:** DeepSeek **no tiene endpoint de conteo**
(relevamiento del 30/09: sólo un zip de demo). Su tokenizador es offline
(`tokenizer.json`, spike 7/7 en verde). Su archivo de motor no lleva
`api_key`: no hay a qué mandarla.

## 3. La key: texto plano en v1, protegida por permisos, no por el nombre

- **v1: texto plano** dentro del archivo del motor, como pidió Fabián.
  `keyring` sale de v1 (y con él la pregunta de Linux: Secret Service
  existe en escritorios con GNOME/KDE, no en servidores sin sesión gráfica;
  por eso la capa cifrada queda para más adelante, cuando se la pueda
  probar en su Ubuntu).
- **El nombre del archivo no protege nada.** tokmd es código abierto: el
  nombre de cualquier archivo que use está en el repo público, a un
  `grep` de distancia. Lo que sí protege son los **permisos**: tokmd crea
  el archivo con `0600` en Linux/macOS (sólo el dueño lee) y en Windows
  queda en `%APPDATA%`, que ya es del usuario. Cero costo, protección real.
- **1Password, por referencia, no por integración.** En el campo `api_key`
  se puede poner el valor literal **o** una referencia `op://bóveda/ítem/campo`.
  Si es referencia, tokmd ejecuta `op read` y usa lo que devuelve; si `op`
  no está instalado, error claro. Es la sintaxis oficial del CLI de
  1Password, funciona en Windows, macOS y Linux, y son unas veinte líneas.
  Quien no usa 1Password nunca se entera; quien lo usa no deja la key en
  disco. La passphrase la pide `op`, no tokmd.

Orden de resolución de v1: variable de entorno → archivo del motor del
usuario → archivo del motor del sistema → pregunta interactiva (sólo en
terminal).

## 4. Banner y pregunta

- Dibujo: se reemplaza el muñeco de videojuego por una lupa sobre un
  documento.
- «Motores soportados» → «Modelos soportados». Se agrega el email.
- Pregunta de tres opciones, como pidió Fabián:

```
  ┌──────────────────────────────────────────────┐
  │   .---.                                      │
  │  /  _  \      tokmd 2.1.0                    │
  │ |  (_)  |     Último release: 2026-10-xx     │
  │  \     /      Modelos soportados: 3          │
  │   '-.-'\\     Autor: Fabián Ferdgelis        │
  │         \\    fferdgelis@gmail.com           │
  └──────────────────────────────────────────────┘

  No se encontró la API key de Anthropic.
  tokmd funciona igual en modo offline (exacto para Claude).

    [1] Ingresar la API key y guardarla
    [2] Seguir en modo offline
    [3] Cancelar la solicitud de API key
```

## 5. Codex

Entra en v1. Se prueba contra la API real y se deja escrito si cobra o no.

## 6. Preguntas abiertas para Fabián

1. **Opciones 2 y 3 hacen lo mismo** como están descritas: las dos
   terminan con el software andando en offline. Propuesta: que la 3 sea
   **«No volver a preguntar»** — guarda la elección y las próximas veces
   sigue en offline sin mostrar la pregunta. Si no, la 3 sobra.
2. **1Password:** en el mismo mensaje dijo que tiene que estar en Windows y
   que prefiere dejar lo cifrado para más adelante. La referencia
   `op://` cumple las dos: no es cifrado propio de tokmd, es opcional, y
   funciona en los tres sistemas. ¿Va así?
3. **Nombre de la carpeta:** `engines/` (el código y los nombres de
   archivo del paquete están en inglés, para usuarios de cualquier país) o
   `motores/`. Recomendación: `engines/` con README en inglés y español.
