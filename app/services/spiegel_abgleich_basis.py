"""Gemeinsame Bausteine der lesenden Spiegelabgleiche (OP, Belege) - M6, 26.11.2026.

Ein Abgleich liest die freigegebenen Staging-Zeilen einer Objektart, bewertet jede Zeile und schreibt das Ergebnis
ins Spiegelprotokoll; am Ende ein Audit-Eintrag. Diese Schritte stehen hier einmal.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.services.legacy_interface_adapter_service import LegacyAdapterError, LegacyInterfaceAdapterService


def freigegebene_zeilen(db: Session, tenant_id: str, batch_id: str, objektart: str) -> tuple[str, list[Any]]:
    """Profil des Batches und seine gueltigen Staging-Zeilen der Objektart; nur freigegebene ``l3_spiegel``-Batches."""
    batch = db.execute(text(
        "SELECT profile_key, status FROM domain_integration.legacy_adapter_batches "
        "WHERE id = :id AND tenant_id = :t"), {"id": batch_id, "t": tenant_id}).mappings().first()
    if not batch or batch["status"] != "approved" or batch["profile_key"] != "l3_spiegel":
        raise LegacyAdapterError("Nur freigegebene Batches mit Profil l3_spiegel sind abgleichsfaehig")
    zeilen = db.execute(text(
        "SELECT line_no, source_ref, canonical_payload FROM domain_integration.legacy_adapter_staging "
        "WHERE tenant_id = :t AND batch_id = :b AND validation_status = 'valid' AND record_type = :o "
        "ORDER BY line_no"), {"t": tenant_id, "b": batch_id, "o": objektart}).mappings().all()
    return str(batch["profile_key"]), list(zeilen)


def protokolliere(db: Session, tenant_id: str, batch_id: str, zeile: Any, objektart: str, ergebnis: str,
                  differenzen: dict[str, Any], fehler: str | None) -> None:
    db.execute(text(
        "INSERT INTO domain_integration.spiegel_protokoll (id, tenant_id, batch_id, line_no, objektart, "
        "quellschluessel, ergebnis, differenzen, fehler) VALUES (:id, :t, :b, :n, :o, :k, :e, CAST(:d AS JSONB), :f)"),
        {"id": str(uuid7()), "t": tenant_id, "b": batch_id, "n": zeile["line_no"], "o": objektart,
         "k": zeile["source_ref"], "e": ergebnis, "d": json.dumps(differenzen), "f": fehler})


def abschliessen(db: Session, tenant_id: str, batch_id: str, profil: str, aktion: str, actor: str, reason: str,
                 details: dict[str, Any]) -> None:
    LegacyInterfaceAdapterService(db, tenant_id)._audit(profil, aktion, actor, reason, batch_id=batch_id,
                                                        details=details)
    db.commit()


def neuer_zaehler() -> dict[str, int]:
    return {"neu": 0, "geaendert": 0, "unveraendert": 0, "fehler": 0}
