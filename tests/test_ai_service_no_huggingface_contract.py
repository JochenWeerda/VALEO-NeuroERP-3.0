"""Vertragstest: Service-Manifeste ohne ungenutzten Hugging-Face-Stack.

ADR-071: unbenutzte Pins entfernen statt Major-Bumps. Schlaegt ein Fall fehl,
ist die Entfernung hinfaellig: Import nachweisen und pinnen, oder den Ladepfad
begrenzen.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

HF_IMPORTS = (
    re.compile(r"\bfrom transformers\b"),
    re.compile(r"\bimport transformers\b"),
    re.compile(r"\bfrom sentence_transformers\b"),
    re.compile(r"\bimport sentence_transformers\b"),
    re.compile(r"\bSentenceTransformer\b"),
    re.compile(r"\bfrom torch\b"),
    re.compile(r"\bimport torch\b"),
)

CASES = (
    {
        "service": "services/ai",
        "pins": (
            re.compile(r"(?m)^sentence-transformers\s*(?:[<>=!~].*)?$"),
            re.compile(r"(?m)^transformers\s*(?:[<>=!~].*)?$"),
        ),
    },
    {
        "service": "services/crm-ai",
        "pins": (
            re.compile(r"(?m)^transformers\s*(?:[<>=!~].*)?$"),
            re.compile(r"(?m)^torch\s*(?:[<>=!~].*)?$"),
        ),
    },
)


@pytest.mark.unit
@pytest.mark.parametrize("case", CASES, ids=lambda c: c["service"])
def test_service_code_does_not_import_huggingface(case: dict) -> None:
    root = REPO / case["service"]
    hits: list[str] = []
    for path in sorted(root.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        for pattern in HF_IMPORTS:
            if pattern.search(source):
                hits.append(f"{path.relative_to(REPO)}: {pattern.pattern}")
    assert hits == [], (
        f"{case['service']} importiert Hugging Face oder Torch. "
        "Die Pin-Entfernung ist dann ungueltig. Treffer: " + "; ".join(hits)
    )


@pytest.mark.unit
@pytest.mark.parametrize("case", CASES, ids=lambda c: c["service"])
def test_service_manifest_does_not_pin_unused_huggingface(case: dict) -> None:
    text = (REPO / case["service"] / "requirements.txt").read_text(encoding="utf-8")
    for pattern in case["pins"]:
        assert not pattern.search(text), (
            f"{case['service']}/requirements.txt pinnt wieder ein ungenutztes "
            f"Paket ({pattern.pattern}). Entweder den Pin lassen und je Advisory "
            "bewerten, oder den Import nachweisen."
        )
