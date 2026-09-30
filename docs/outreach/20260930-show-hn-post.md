---
title: "Borrador de difusión: post técnico sobre el hallazgo real de tokmd"
aliases:
  - "Show HN tokmd"
project: tokmd
document_type: outreach-draft
status: draft
version: 0.1.0
created: 2026-09-30
updated: 2026-09-30
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-sonnet-5"
llm_harness: "Claude Code Desktop"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription"
modified_by: "Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription"
reviewed_by: "pending"
review_status: "pending"
source_of_truth: true
tags:
  - project/tokmd
  - outreach
related_documents:
  - "[[20260927-count-tokens-api-vs-tokmd-ctok-ttok]]"
  - "[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]"
---

# Borrador de difusión: post técnico sobre el hallazgo real de tokmd

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación, a pedido de Fabián («arrancá con la 1» sobre la opción 1 de difusión: un post técnico con el hallazgo real). Primera carpeta `docs/outreach/` de este repo — no había convención previa para material de difusión, es la más obvia y se deja acá dicho. |

## Cómo usar esto

**Nada de esto se publicó.** Son tres textos listos para que vos los revises,
los edites si algo no suena a tu voz, y los postees **desde tu cuenta**:
publicar en Hacker News, Reddit o X es una acción hacia afuera que no tomo por
vos. Los tres cuentan la misma historia con tamaños distintos, para no
reescribir según el canal.

1. **Título + cuerpo para "Show HN"** (Hacker News). El público ahí es técnico
   y detesta el marketing; el ángulo es el hallazgo, no el producto.
2. **Post más largo**, mismo contenido, para Reddit (`r/ClaudeAI`,
   `r/LocalLLaMA`) o un blog/dev.to si preferís long-form.
3. **Hilo corto para X**, misma historia en 4 tuits.

Todos los números están verificados contra la API real el 27/09/2026
(`docs/investigation/20260927-count-tokens-api-vs-tokmd-ctok-ttok.md`); nada
inventado para que quede mejor.

---

## 1. Show HN (título + cuerpo)

**Título** (80 caracteres máx., HN lo corta):

```
Show HN: tokmd – I measured my CLAUDE.md against Anthropic's real token count
```

**Cuerpo:**

> I use Claude Code daily, and `CLAUDE.md` files get loaded into every
> request. I wanted to know exactly how many tokens mine costs, so I built
> `tokmd` — a CLI that counts tokens per Markdown section, with the right
> tokenizer for the target platform (Claude, OpenAI's o200k/cl100k).
>
> Then I did something most token counters skip: I checked it against
> Anthropic's real `POST /v1/messages/count_tokens` endpoint (it's free, no
> billing). My own tool was **8.5% off** — it wasn't counting the heading
> line of each Markdown section (`## Title` text), only the body below it.
> A file with 44 headings just silently dropped 1,478 tokens from the total.
>
> Root cause, fix, and the full before/after measurement are here:
> https://github.com/fferdgelis/tokmd/blob/main/docs/investigation/20260927-count-tokens-api-vs-tokmd-ctok-ttok.md
>
> Fixed in 2.0.0 (just shipped): `tokmd CLAUDE.md` now prints the real total
> in one line, matching the API exactly — verified: 17,381 tokens, same
> number the API bills. `--sections` gives the full breakdown with a
> `boundary drift: ±N` line that has to read `0` — if it ever doesn't, the
> tool tells you instead of hiding it.
>
> `pip install tokmd` / `uvx tokmd yourfile.md`. Offline by default (no API
> key needed), `--verify` cross-checks against the real endpoint when you
> want ground truth. MIT... Apache 2.0, source on GitHub, feedback on the
> approach very welcome — especially if anyone knows of other silent
> undercounts in similar tools.
>
> https://github.com/fferdgelis/tokmd

---

## 2. Post largo (Reddit / blog / dev.to)

**Título:**

```
My own token counter was lying to me by 8.5% — here's how I found out
```

**Cuerpo:**

> I built `tokmd`, a CLI that counts Markdown tokens per section for
> whichever AI platform you're targeting (Claude, OpenAI). Then I almost
> shipped a silent bug that would have undercounted every file with
> headings — here's the story, because I think the lesson generalizes past
> my tool.
>
> **The setup.** `tokmd` uses `ctok` (an offline, reverse-engineered
> reconstruction of Anthropic's tokenizer — Anthropic doesn't publish one)
> for Claude, and `tiktoken` for OpenAI. Fast, no API key, no network call.
>
> **The check I almost skipped.** Anthropic exposes
> `POST /v1/messages/count_tokens` — free, no billing, real ground truth for
> whatever model you pass. I ran my own `CLAUDE.md` (38KB, 44 Markdown
> headings) through both my tool and the real endpoint, just to sanity-check
> before a release.
>
> - Real API (`count_tokens`, Sonnet 5 / Opus 5): **17,381 tokens.**
> - `tokmd`: **15,903 tokens.**
> - Gap: **1,478 tokens, 8.5%.**
>
> **Root cause.** My section parser split each heading from its body —
> `own_text` started on the line *after* the `#` line, so the heading text
> itself (`## Some Title`) never got counted anywhere. Fine for a file with
> two or three headings. My `CLAUDE.md` has 44, several of them used as
> plain-text comments (`# note to self`, no body below) — those sections
> reported `0` tokens even though the heading line alone costs real tokens.
>
> **Why the offline tokenizer wasn't the problem.** I also checked `ctok`
> raw (no section splitting) against the same API call: **exact match,
> 17,381 = 17,381.** The reverse-engineered tokenizer was fine the whole
> time. The bug was in *my* code — the part that decided what text to hand
> to the tokenizer, not the tokenizer itself. Worth remembering before
> blaming the dependency.
>
> **The fix (shipped in 2.0.0, a breaking change on purpose):**
> - `tokmd file.md` with no flags now prints exactly one number: the real
>   total, single-pass count — no silent reconstruction from parts.
> - `--sections` gives the breakdown, now with *both* `own` and `total` per
>   row (there's a difference between "this section is short" and "this
>   section has expensive children").
> - A `boundary drift: ±N` line that has to read `0`. It's a built-in
>   canary: if the row sum and the single-pass total ever disagree again —
>   new tokenizer, new edge case, whatever — the tool says so instead of
>   quietly being wrong for another release cycle.
>
> Full writeup with every intermediate number, the probe experiments against
> the real endpoint, and the section-by-section math:
> https://github.com/fferdgelis/tokmd/blob/main/docs/investigation/20260927-count-tokens-api-vs-tokmd-ctok-ttok.md
>
> **Takeaway for anyone building a measurement tool of any kind:** if there's
> a free, real oracle available, check against it before you trust your own
> offline approximation — even (especially) the one you wrote yourself.
>
> `pip install tokmd` · https://github.com/fferdgelis/tokmd · MIT/Apache 2.0.
> Happy to answer questions about the tokenizer reconstruction approach or
> the section-parsing internals.

---

## 3. Hilo corto (X / Twitter)

> 1/ Built `tokmd`, a CLI that counts tokens per Markdown section for
> Claude/OpenAI. Then I checked it against Anthropic's real token-counting
> API before shipping. Good thing I did.
>
> 2/ My own tool was undercounting by 8.5% — it silently skipped every
> section's heading text. A file with 44 headings lost 1,478 tokens off the
> total. Sections that were just `# a comment` reported 0 tokens.
>
> 3/ The offline tokenizer (`ctok`, a reverse-engineered reconstruction —
> Anthropic doesn't publish one) was exact the whole time. The bug was in my
> own section-splitting code, not the dependency. Worth checking before you
> blame the library.
>
> 4/ Fixed in 2.0.0, now with a `boundary drift: ±N` canary that has to read
> 0 — if it's ever wrong again, the tool says so instead of hiding it.
> `pip install tokmd` · full writeup + real numbers:
> https://github.com/fferdgelis/tokmd

---

## Qué falta para que esto funcione

- **Elegir canal y fecha.** HN castiga postear en mal horario (la franja que
  mejor funciona es mañana US Este, martes a jueves). Reddit y X no tienen
  esa sensibilidad tan marcada.
- **Vos posteás, no yo.** Copiás el texto elegido, lo revisás con tu voz, y
  lo subís desde tu cuenta.
- **El link del writeup apunta a GitHub**, así que antes de postear conviene
  confirmar que `docs/investigation/20260927-count-tokens-api-vs-tokmd-ctok-ttok.md`
  se ve bien renderizado en GitHub (markdown con tablas, ya debería andar,
  pero vale la pena un vistazo).
- Si algo de estos tres textos no suena a como hablás vos, decime qué cambiar
  y lo ajusto acá mismo antes de que lo publiques.
