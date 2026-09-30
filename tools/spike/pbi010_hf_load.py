"""Spike AC-14 de PBI-010: ¿cargan los tokenizer.json reales con la librería
`tokenizers`, y el .spiece.model de Gemma con `sentencepiece`?

Corre FUERA de la suite de pytest (necesita red una vez). Baja sólo el archivo
del tokenizador de cada repo (nunca el modelo), cuenta el texto de control y
deja conteo + sha256 para copiar a docs/PBI/PBI-010-casos-de-prueba.md.

    uv run --with tokenizers --with huggingface_hub --with sentencepiece \
        python tools/spike/pbi010_hf_load.py
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

CONTROL = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "control_2kb.md.fixture"

HF_REPOS = {
    "deepseek-v4-pro": "deepseek-ai/DeepSeek-V4-Pro",
    "deepseek-v4-flash": "deepseek-ai/DeepSeek-V4-Flash",
    "glm-5.3": "zai-org/GLM-5.3",
    "qwen3.5": "Qwen/Qwen3.5-9B",
    "nemotron-3-super": "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8",
    "mistral-large-3": "mistralai/Mistral-Large-3-675B-Instruct-2512-NVFP4",
}

# Lo que google-genai usa por dentro para gemini-3-pro/flash-preview
# (_local_tokenizer_loader.py); el sha256 se registra en la salida.
GEMMA3_SPIECE = (
    "https://raw.githubusercontent.com/google/gemma_pytorch/"
    "014acb7ac4563a5f77c76d7ff98f31b568c16508/tokenizer/gemma3_cleaned_262144_v2.spiece.model"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    text = CONTROL.read_text(encoding="utf-8")
    print(f"[0/{len(HF_REPOS) + 1}] texto de control: {CONTROL.name}, {len(text)} chars, "
          f"sha256={hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}...")

    from huggingface_hub import hf_hub_download
    from tokenizers import Tokenizer

    failures = 0
    for i, (name, repo) in enumerate(HF_REPOS.items(), start=1):
        print(f"[{i}/{len(HF_REPOS) + 1}] {name}  <-  {repo}/tokenizer.json")
        try:
            path = Path(hf_hub_download(repo, "tokenizer.json"))
            tok = Tokenizer.from_file(str(path))
            n = len(tok.encode(text, add_special_tokens=False).ids)
            n_special = len(tok.encode(text).ids)
            print(f"      OK  tokens={n}  (con special tokens={n_special})  "
                  f"size={path.stat().st_size}  sha256={sha256(path)}")
        except Exception as exc:  # noqa: BLE001 - es un spike, se reporta todo
            failures += 1
            print(f"      FALLO  {type(exc).__name__}: {exc}")

    print(f"[{len(HF_REPOS) + 1}/{len(HF_REPOS) + 1}] gemini-3-flash  <-  gemma3 .spiece.model")
    try:
        import sentencepiece as spm

        dest = Path(__file__).with_name("gemma3.spiece.model")
        if not dest.exists():
            urllib.request.urlretrieve(GEMMA3_SPIECE, dest)
        sp = spm.SentencePieceProcessor(model_file=str(dest))
        n = len(sp.encode(text))
        print(f"      OK  tokens={n}  size={dest.stat().st_size}  sha256={sha256(dest)}")
    except Exception as exc:  # noqa: BLE001
        failures += 1
        print(f"      FALLO  {type(exc).__name__}: {exc}")

    print(f"\nRESULTADO: {failures} fallos de {len(HF_REPOS) + 1}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
