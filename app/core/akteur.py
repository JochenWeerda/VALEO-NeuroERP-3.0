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
    return subject


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
        return subject
    return fallback


def gepruefter_akteur_aus_request(request: Any) -> str:
    """Wie ``akteur_aus_request``, aber ohne gepruefte Identitaet ist die Anfrage nicht zurechenbar: 403."""
    akteur = akteur_aus_request(request)
    if akteur is None:
        raise HTTPException(status_code=403, detail="Gepruefter Bearbeiter fehlt")
    return akteur


def bekannter_nutzer(db: Any, akteur: str | None, *, tenant_id: str) -> str:
    """Resolve a verified subject to exactly one active tenant-local profile.

    Missing/ambiguous mappings deny the action. Database failures propagate;
    neither a fabricated system actor nor an aborted transaction is concealed.
    """
    if not isinstance(akteur, str) or not akteur.strip() or not tenant_id:
        raise HTTPException(status_code=403, detail="Gepruefte lokale Nutzerzuordnung fehlt")
    from sqlalchemy import text

    matches = db.execute(text("""
        SELECT id FROM domain_shared.users
        WHERE tenant_id = :tenant_id AND is_active IS TRUE
          AND (id = :actor OR keycloak_id = :actor)
        FOR SHARE
    """), {"actor": akteur, "tenant_id": tenant_id}).all()
    if len(matches) != 1:
        raise HTTPException(status_code=403, detail="Keine eindeutige lokale Nutzerzuordnung")
    return matches[0][0]
