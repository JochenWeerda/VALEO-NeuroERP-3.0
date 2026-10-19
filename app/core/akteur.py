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


def akteur_aus_request(request: Any, fallback: str | None = None) -> str | None:
    """Urheber aus den Claims, die ``require_bearer_token`` geprueft im Request ablegt — nie aus einem Kopf.

    Fuer Wege, die keinen Nutzer per Abhaengigkeit bekommen. Ohne gepruefte Claims: ``fallback``.
    """
    state = getattr(request, "state", None)
    claims = getattr(state, "token_claims", None) if state is not None else None
    subject = claims.get("sub") if isinstance(claims, dict) else None
    if isinstance(subject, str) and subject.strip():
        return subject.strip()[:120]
    return fallback


def gepruefter_akteur_aus_request(request: Any) -> str:
    """Wie ``akteur_aus_request``, aber ohne gepruefte Identitaet ist die Anfrage nicht zurechenbar: 403."""
    akteur = akteur_aus_request(request)
    if akteur is None:
        raise HTTPException(status_code=403, detail="Gepruefter Bearbeiter fehlt")
    return akteur


def bekannter_nutzer(db: Any, akteur: str | None, fallback: str = "system") -> str:
    """Kennung fuer Spalten mit Fremdschluessel auf ``domain_shared.users``.

    Die gepruefte Kennung, wenn es den Nutzer im Verzeichnis gibt; sonst ``fallback`` (wie vor dem 19.10.2026,
    als dort ohne Kopfzeile immer ``system`` stand). So scheitert kein Vorgang an einem Nutzer, den das
    Verzeichnis noch nicht kennt, und kein Client bestimmt den Namen.
    """
    if not akteur:
        return fallback
    try:
        from sqlalchemy import text

        known = db.execute(text("SELECT 1 FROM domain_shared.users WHERE id = :id"), {"id": akteur}).first()
    except Exception:  # noqa: BLE001 — ohne lesbares Verzeichnis bleibt die FK-sichere Kennung
        return fallback
    return akteur if known is not None else fallback
