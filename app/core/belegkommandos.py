"""Verzeichnis der Belegkommandos: eine Fachaktion, mehrere Zugaenge (BELEG-013).

Jede Belegfunktion von DocFlow steht hier einmal — mit dem, was Maske und Agent ueber sie wissen muessen: ob sie
schreibt, welche Risikoklasse sie hat, ob eine Wiederholung mit demselben Schluessel gefahrlos ist, und unter
welcher Adresse sie liegt. Die Aktionen des Belegvertrags nennen ein Kommando aus diesem Verzeichnis; ein Test
haelt Verzeichnis und DocFlow-Wege deckungsgleich.

Verhaeltnis zum Standard MCP-WRITE (``docs/architecture/mcp-write-standard.md``, verbindlich seit 13.10.2026):

* Die Risikoklassen sind die des Standards (R0 Lesen … R4 kritisch); ab R3 braucht es eine Freigabe.
* Das Verzeichnis ist **keine zweite Capability-Registry**. Es beschreibt die vorhandenen DocFlow-Wege und ist
  die Zuarbeit der Belege fuer Stufe 2 des Standards („Bestehende Register vereinheitlichen"); dort werden die
  Namen auf die kanonischen Capability- und Command-Identitaeten abgebildet.
* Kein schreibendes Belegkommando hat ein MCP-Werkzeug (MCP-WRITE-014: zunaechst deaktiviert). Ueber MCP gibt es
  nur die lesenden Werkzeuge ``beleg.arten``, ``beleg.suchen``, ``beleg.lesen``.

Das Recht je Kommando steht hier und wird an den DocFlow-Wegen durchgesetzt (``app/auth/beleg_roles.py``).
Noch offen: Schemaversion und Freischaltzustand je Kommando (Stufe 2 des Standards).
"""
from __future__ import annotations

from dataclasses import dataclass

RISIKOKLASSEN: dict[str, str] = {
    "R0": "Lesen",
    "R1": "Entwurf",
    "R2": "Operative Änderung",
    "R3": "Geschäftlich verbindlich",
    "R4": "Kritisch",
}


@dataclass(frozen=True)
class Belegkommando:
    name: str
    bezeichnung: str
    methode: str
    pfad: str  # unter /api/v1
    risiko: str  # R0–R4 nach MCP-WRITE
    recht: str  # eines der Rechte aus app/auth/beleg_roles.py
    idempotent: bool = False  # Wiederholung mit demselben Idempotenzschluessel liefert dasselbe Ergebnis

    @property
    def schreibend(self) -> bool:
        return self.risiko != "R0"

    @property
    def freigabe_noetig(self) -> bool:
        """Ab R3: ausdrueckliche Freigabe oder vorab genehmigte, passende Richtlinie."""
        return self.risiko in {"R3", "R4"}


BELEGKOMMANDOS: dict[str, Belegkommando] = {
    k.name: k
    for k in (
        Belegkommando("beleg.lesen", "Beleg lesen", "GET", "/belege/{belegart}/{beleg_id}", "R0", "lesen", idempotent=True),
        Belegkommando("docflow.create", "Beleg anlegen", "POST", "/docflow/", "R1", "bearbeiten", idempotent=True),
        Belegkommando("docflow.update", "Beleg bearbeiten", "PUT", "/docflow/{doc_id}", "R1", "bearbeiten"),
        Belegkommando("docflow.delete_draft", "Entwurf löschen", "DELETE", "/docflow/{doc_id}", "R1", "bearbeiten"),
        Belegkommando("docflow.convert", "Folgebeleg erstellen", "POST", "/docflow/{doc_id}/convert", "R2", "bearbeiten", idempotent=True),
        Belegkommando("docflow.record_print", "Druck vermerken", "POST", "/docflow/{doc_id}/record-print", "R2", "bearbeiten"),
        Belegkommando("docflow.record_export", "Export vermerken", "POST", "/docflow/{doc_id}/record-export", "R2", "bearbeiten"),
        # Freigeben vergibt die endgueltige Belegnummer: Der Beleg ist danach ausgestellt.
        Belegkommando("docflow.release", "Beleg freigeben", "POST", "/docflow/{doc_id}/release", "R3", "ausstellen", idempotent=True),
        Belegkommando("docflow.post", "Beleg buchen", "POST", "/docflow/{doc_id}/post", "R3", "buchen", idempotent=True),
        Belegkommando("docflow.reverse", "Beleg stornieren", "POST", "/docflow/{doc_id}/reverse", "R4", "stornieren", idempotent=True),
    )
}

# Schreibende Methode, aber kein Belegkommando — mit Grund.
KEIN_BELEGKOMMANDO: dict[tuple[str, str], str] = {
    ("POST", "/docflow/source-proposals"): "liest nur: schlägt Kontrakt- und Fremdlagerquellen vor",
}


def als_dict(kommando: Belegkommando) -> dict[str, object]:
    return {
        "name": kommando.name, "bezeichnung": kommando.bezeichnung, "methode": kommando.methode,
        "pfad": f"/api/v1{kommando.pfad}", "schreibend": kommando.schreibend, "recht": kommando.recht, "risiko": kommando.risiko,
        "risiko_bezeichnung": RISIKOKLASSEN[kommando.risiko], "freigabe_noetig": kommando.freigabe_noetig,
        "idempotent": kommando.idempotent, "ueber_mcp": not kommando.schreibend,
    }
