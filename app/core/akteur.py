"""Wer handelt — aus der geprueften Identitaet, nie aus einem Client-Header.

Bis zum 19.10.2026 nahmen rund dreissig Schreibwege den Audit-Urheber aus ``X-User-ID``, den jeder
Client frei setzt (Rueckfall: ein fester Platzhalter). Damit liessen sich Audit-Eintraege unter fremdem
Namen schreiben und Vier-Augen-Pruefungen (Freigeber != Ersteller) mit zwei Kopfzeilen umgehen.

``gepruefter_akteur`` liest den Urheber aus dem Nutzerobjekt, das die Rollen-Abhaengigkeit
(``require_roles``) aus dem geprueften Token liefert. Fehlt er, ist die Anfrage nicht zurechenbar: 403.
"""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException


def gepruefter_akteur(user: Any) -> str:
    """Audit-Urheber (``sub``) aus dem geprueften Token."""
    subject = user.get("sub") if isinstance(user, dict) else None
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(status_code=403, detail="Gepruefter Bearbeiter fehlt")
    return subject.strip()[:120]


def anzeigename(user: Any) -> str:
    """Lesbarer Name fuer Zustaendigkeiten (Anmeldename); faellt auf den Urheber zurueck."""
    from app.auth.deps import anmeldename

    return anmeldename(user if isinstance(user, dict) else None) or gepruefter_akteur(user)


def verlange_rolle(user: Any, *rollen: str) -> None:
    """Fuer Kommando-Wege mit mehreren Aktionen: die strengere Rolle einer einzelnen Aktion."""
    vorhanden = set(user.get("roles") or []) if isinstance(user, dict) else set()
    if not vorhanden.intersection(rollen):
        raise HTTPException(status_code=403, detail=f"Insufficient role. Required: {rollen}")
