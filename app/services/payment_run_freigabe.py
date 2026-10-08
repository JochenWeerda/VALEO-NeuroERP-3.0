"""Freigabe eines Zahlungslaufs: Mandant und Vier-Augen-Prinzip.

Bis 07.10.2026 nahm die Freigabe den Mandanten aus einem Query-Parameter (Vorgabe
"system") und den Freigeber als freien Text aus dem Rumpf. Freigeber ist jetzt der
angemeldete Nutzer, und wer den Lauf angelegt hat, gibt ihn nicht frei.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session


def pruefe_freigabe(db: Session, run_id: str, tenant_id: str, freigeber: str) -> None:
    """Sperrt den Lauf und prueft, ob dieser Freigeber ihn freigeben darf.

    404, wenn der Lauf nicht diesem Mandanten gehoert; 409, wenn der Freigeber ihn
    angelegt hat. Ohne belegten Ersteller und authentifizierten Freigeber ist
    das Vier-Augen-Prinzip nicht nachgewiesen; solche Laeufe bleiben gesperrt.
    """
    freigeber = str(freigeber or "").strip()
    if not freigeber:
        raise HTTPException(status_code=403, detail="Authentifizierter Freigeber fehlt.")
    lauf = db.execute(
        text(
            "SELECT status, created_by FROM domain_erp.payment_runs "
            "WHERE id = :run_id AND tenant_id = :tenant_id FOR UPDATE"
        ),
        {"run_id": run_id, "tenant_id": tenant_id},
    ).fetchone()
    if lauf is None:
        raise HTTPException(status_code=404, detail="Payment run not found")
    if lauf[0] != "draft":
        raise HTTPException(status_code=409, detail="Zahlungslauf ist nicht im Entwurf und kann nicht freigegeben werden.")
    ersteller = str(lauf[1] or "").strip()
    if not ersteller:
        raise HTTPException(status_code=409, detail="Ersteller des Zahlungslaufs nicht nachgewiesen; Vier-Augen-Freigabe gesperrt.")
    if ersteller == freigeber:
        raise HTTPException(
            status_code=409,
            detail="Vier-Augen-Prinzip: Wer den Zahlungslauf angelegt hat, gibt ihn nicht frei.",
        )
