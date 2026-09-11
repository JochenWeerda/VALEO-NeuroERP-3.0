"""Vertragstest: ChromaDB wird ausschliesslich eingebettet betrieben.

Hintergrund (SECURITY-AGENT-CHROMADB-20260911): CVE-2026-45833 (CRITICAL,
Code Injection), CVE-2026-45830 und CVE-2026-45831 (je HIGH, fehlende
Mandanten-/Berechtigungspruefung) betreffen chromadb >= 0.4.17 bis
einschliesslich 1.5.9 - das ist die neueste Version, ein Herstellerfix
existiert nicht.

Alle drei Angriffswege fuehren ueber die HTTP-API des ChromaDB-*Servers*
(z. B. /api/v2/tenants/.../collections/{id} mit trust_remote_code). Wir
betreiben ausschliesslich den eingebetteten Client ohne Server, womit diese
Wege nicht erreichbar sind.

Dieser Test haelt genau diese Voraussetzung fest. Schlaegt er fehl, ist die
Risikobewertung hinfaellig und muss neu getroffen werden, bevor der Code
gemergt wird.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Produktivcode, der chromadb verwendet
CALL_SITES = [
    Path("app/infrastructure/rag/vector_store.py"),
    Path("services/ai/app/services/vector_store.py"),
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
    if not path.exists():
        pytest.skip(f"{rel} existiert nicht mehr")
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
