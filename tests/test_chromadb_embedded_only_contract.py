"""Optional remaining root adapter stays embedded; AI service has retired Chroma.

No vulnerable Chroma package or startup path may be reintroduced into the AI
service. Existing local-only root code is not a reason to waive advisories.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Produktivcode, der chromadb verwendet
CALL_SITES = [
    Path("app/infrastructure/rag/vector_store.py"),
]

# Serverbetrieb: genau diese Formen waeren gefaehrlich
SERVER_PATTERNS = [
    re.compile(r"\bchromadb\.HttpClient\b"),
    re.compile(r"\bHttpClient\s*\("),
    re.compile(r"\bchromadb\.AsyncHttpClient\b"),
    re.compile(r"chroma_server_host"),
    re.compile(r"chroma_server_http_port"),
]

EMBEDDED_PATTERNS = [
    re.compile(r"\bchromadb\.Client\s*\("),
    re.compile(r"\bchromadb\.PersistentClient\s*\("),
    re.compile(r"\bchromadb\.EphemeralClient\s*\("),
]


@pytest.mark.unit
@pytest.mark.parametrize("rel", CALL_SITES, ids=lambda p: str(p))
def test_call_site_uses_embedded_client(rel: Path) -> None:
    path = REPO / rel
    assert path.exists(), "Verbleibenden Root-Vertrag nicht still ueberspringen"
    source = path.read_text(encoding="utf-8")

    for pattern in SERVER_PATTERNS:
        assert not pattern.search(source), (
            f"{rel} betreibt ChromaDB im Servermodus ({pattern.pattern}). "
            "Damit werden CVE-2026-45833/45830/45831 erreichbar, fuer die es "
            "keinen Herstellerfix gibt. Risikobewertung neu treffen."
        )

    assert any(p.search(source) for p in EMBEDDED_PATTERNS), (
        f"{rel} nutzt chromadb, aber keinen erkennbaren eingebetteten Client. "
        "Bitte den Vertragstest an die neue Verwendung anpassen."
    )


@pytest.mark.unit
def test_no_chroma_server_in_compose() -> None:
    """Kein ChromaDB-Server in der Compose-Landschaft."""
    for compose in sorted(REPO.glob("docker-compose*.yml")):
        text = compose.read_text(encoding="utf-8", errors="replace").lower()
        assert "chromadb/chroma" not in text and "ghcr.io/chroma-core" not in text, (
            f"{compose.name} startet einen ChromaDB-Server. Siehe Modul-Docstring: "
            "die Risikobewertung setzt den eingebetteten Betrieb voraus."
        )


def test_ai_service_has_no_vulnerable_chroma_dependency_or_startup():
    manifest = (REPO / 'services/ai/requirements.txt').read_text(encoding='utf-8')
    assert not re.search(r'^\s*chromadb[=<>]', manifest, re.M | re.I)
    assert not (REPO / 'services/ai/app/services/vector_store.py').exists()
    assert 'initialize_vector_store' not in (REPO / 'services/ai/main.py').read_text(encoding='utf-8')
