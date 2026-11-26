"""Lizenzpruefung fuer das Verkaufsprodukt (M7, 26.11.2026) - auf dem Modulregister.

Eine Lizenz ist eine JSON-Datei mit Inhalt und Ed25519-Signatur::

    {"lizenz": {"kunde": "...", "mandanten": ["..."] | null, "module": ["core", "agrar", ...],
                "gueltig_bis": "JJJJ-MM-TT", "ausgestellt": "JJJJ-MM-TT"},
     "signatur": "<base64>"}

Signiert wird die kanonische JSON-Form von ``lizenz`` (sortierte Schluessel, ohne Leerraum). VALEO kennt nur den
oeffentlichen Schluessel (``VALEO_LIZENZ_OEFFENTLICHER_SCHLUESSEL``, base64 der 32 Rohbytes); der private Schluessel
bleibt beim Hersteller (``scripts/lizenz_ausstellen.py``) und kommt nie ins Repository.

Durchgesetzt wird nur, wenn ``VALEO_UMGEBUNG`` ausdruecklich ``staging`` oder ``production`` ist. Ohne gueltige
Lizenz bleibt dann nur ``core`` aktiv - eine fehlende oder manipulierte Lizenz schaltet nichts frei. Lokal und in der CI
gilt das Modulregister wie bisher.
"""
from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Optional

KERNMODUL = "core"
UMGEBUNGEN_MIT_LIZENZ = frozenset({"staging", "production"})


class LizenzUngueltig(ValueError):
    """Die Lizenz fehlt, ist manipuliert, abgelaufen oder gilt nicht fuer diesen Mandanten."""


@dataclass(frozen=True)
class Lizenz:
    kunde: str
    module: frozenset[str]
    mandanten: Optional[frozenset[str]]
    gueltig_bis: date

    def erlaubt(self, modul: str, tenant_id: Optional[str]) -> bool:
        if self.mandanten is not None and tenant_id is not None and tenant_id not in self.mandanten:
            return modul == KERNMODUL
        return modul == KERNMODUL or modul in self.module


def kanonisch(inhalt: dict[str, Any]) -> bytes:
    return json.dumps(inhalt, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def pruefe(dokument: dict[str, Any], oeffentlicher_schluessel_b64: str, *, heute: date) -> Lizenz:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    inhalt, signatur = dokument.get("lizenz"), dokument.get("signatur")
    if not isinstance(inhalt, dict) or not isinstance(signatur, str):
        raise LizenzUngueltig("Lizenzdatei hat kein Feld 'lizenz' oder 'signatur'")
    try:
        schluessel = Ed25519PublicKey.from_public_bytes(base64.b64decode(oeffentlicher_schluessel_b64))
        schluessel.verify(base64.b64decode(signatur), kanonisch(inhalt))
    except (InvalidSignature, ValueError) as fehler:
        raise LizenzUngueltig("Signatur der Lizenz ist ungueltig") from fehler
    try:
        gueltig_bis = date.fromisoformat(str(inhalt["gueltig_bis"]))
    except (KeyError, ValueError) as fehler:
        raise LizenzUngueltig("Lizenz ohne gueltiges Ablaufdatum") from fehler
    if heute > gueltig_bis:
        raise LizenzUngueltig(f"Lizenz ist seit {gueltig_bis.isoformat()} abgelaufen")
    mandanten = inhalt.get("mandanten")
    return Lizenz(kunde=str(inhalt.get("kunde") or ""), module=frozenset(map(str, inhalt.get("module") or [])),
                  mandanten=frozenset(map(str, mandanten)) if mandanten is not None else None, gueltig_bis=gueltig_bis)


def lizenzpflichtig() -> bool:
    """Nur wenn die Umgebung ausdruecklich STAGING oder PRODUCTION ist (nicht der geschlossene Vorgabewert)."""
    return os.environ.get("VALEO_UMGEBUNG", "").strip().lower() in UMGEBUNGEN_MIT_LIZENZ


def aktuelle_lizenz(*, heute: Optional[date] = None) -> Optional[Lizenz]:
    """Die gueltige Lizenz dieser Installation - oder ``None`` (fehlt, ungueltig, abgelaufen)."""
    from app.core.business_time import business_today

    pfad = os.environ.get("VALEO_LIZENZ_DATEI", "").strip()
    schluessel = os.environ.get("VALEO_LIZENZ_OEFFENTLICHER_SCHLUESSEL", "").strip()
    if not pfad or not schluessel or not Path(pfad).is_file():
        return None
    try:
        dokument = json.loads(Path(pfad).read_text(encoding="utf-8"))
        return pruefe(dokument, schluessel, heute=heute or business_today())
    except (LizenzUngueltig, json.JSONDecodeError, OSError):
        return None  # ungueltig wie fehlend: nur das Kernmodul bleibt aktiv (siehe modul_lizenziert)


def modul_lizenziert(modul: str, tenant_id: Optional[str] = None) -> bool:
    """Darf das Modul nach der Lizenz laufen? Ohne Lizenzpflicht immer ja."""
    if not lizenzpflichtig():
        return True
    lizenz = aktuelle_lizenz()
    if lizenz is None:
        return modul == KERNMODUL
    return lizenz.erlaubt(modul, tenant_id)
