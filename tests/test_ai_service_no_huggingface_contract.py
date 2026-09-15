"""Vertragstest: services/ai laedt keine Hugging-Face-Transformers-Pfade.

Hintergrund (ADR-071, SERVICE-REMAINDER-GAPS-20260914): pip-audit meldete
26 Befunde gegen transformers 4.46.3. Ein Sprung auf 4.57.6 ist unzulaessig,
weil chromadb 0.5.23 tokenizers<=0.20.3 verlangt. Die Pfadanalyse zeigt:

- Kein Import von transformers oder sentence_transformers unter services/ai.
- RAG-HTTP bleibt Mock; echte Embeddings laufen ueber OpenAI
  (app/services/openai_service.py) oder Chromas Default (ONNX), nicht HF.
- app/infrastructure/rag/vector_store.py nutzt SentenceTransformer — das ist
  der Monolith, nicht dieser Microservice.

Ungenutzte Pins wurden entfernt statt hochgezogen. Schlaegt dieser Test fehl,
ist die Entfernung hinfaellig: entweder den Import wieder pinnen und je CVE
bewerten, oder den neuen Ladepfad begrenzen.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
AI_ROOT = REPO / "services" / "ai"
MANIFEST = AI_ROOT / "requirements.txt"

FORBIDDEN_IMPORTS = [
    re.compile(r"\bfrom transformers\b"),
    re.compile(r"\bimport transformers\b"),
    re.compile(r"\bfrom sentence_transformers\b"),
    re.compile(r"\bimport sentence_transformers\b"),
    re.compile(r"\bSentenceTransformer\b"),
]

FORBIDDEN_PINS = (
    re.compile(r"(?m)^sentence-transformers\s*(?:[<>=!~].*)?$"),
    re.compile(r"(?m)^transformers\s*(?:[<>=!~].*)?$"),
)


@pytest.mark.unit
def test_ai_service_code_does_not_import_huggingface() -> None:
    hits: list[str] = []
    for path in sorted(AI_ROOT.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_IMPORTS:
            if pattern.search(source):
                hits.append(f"{path.relative_to(REPO)}: {pattern.pattern}")
    assert hits == [], (
        "services/ai importiert Hugging Face. Die Entfernung von transformers "
        "und sentence-transformers ist dann ungueltig. Treffer: " + "; ".join(hits)
    )


@pytest.mark.unit
def test_ai_service_manifest_does_not_pin_huggingface() -> None:
    text = MANIFEST.read_text(encoding="utf-8")
    for pattern in FORBIDDEN_PINS:
        assert not pattern.search(text), (
            "services/ai/requirements.txt pinnt wieder ein ungenutztes "
            f"Hugging-Face-Paket ({pattern.pattern}). Entweder den Pin lassen "
            "und je Advisory bewerten, oder den Import nachweisen."
        )
