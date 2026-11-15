"""Altlieferschein im Speicher domain_sales.delivery_notes anlegen - fuer Tests des alten Rechnungswegs (BELEG-052).

Der Router ``/sales/delivery-notes`` ist entfernt (Phase 1b); der alte Rechnungsweg ``/sales/invoices/from-delivery-notes``
liest bis Phase 2 noch diesen Speicher. Dieser Helfer legt einen Lieferschein so an, wie der Router es tat: Kopf,
Positionen (Nettopreis/-betrag wie dort gerechnet) und die Mengenquellen des Zuordnungsmodells. Den Kontrakt-Abruf
laesst er weg - der war auch im Router best effort.
"""
from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import Any, Iterable

from sqlalchemy import text


def lege_alt_lieferschein_an(mandant: str, *, kunde: str | None, lieferdatum: str = "2026-09-15",
                             positionen: Iterable[dict[str, Any]], status: str = "draft",
                             nummer: str | None = None, url: str | None = None) -> str:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.core.database import SessionLocal
    from app.services.document_allocation_service import DocumentAllocationService, LineToRegister

    kennung = str(uuid.uuid4())
    zeilen = []
    for nr, p in enumerate(positionen, start=1):
        menge = Decimal(str(p["menge"]))
        preis = Decimal(str(p.get("netto_preis", "0")))
        zeilen.append({"id": str(uuid.uuid4()), "pos_nr": p.get("pos_nr", nr), "artikel_id": p.get("artikel_id"),
                       "artikel_nr": p.get("artikel_nr"), "bezeichnung": p.get("bezeichnung"), "menge": menge,
                       "einheit": p.get("einheit"), "netto_preis": preis, "netto_betrag": preis * menge,
                       "mwst_prozent": p.get("mwst_prozent"), "kontrakt_nr": p.get("kontrakt_nr")})
    netto = sum((z["netto_betrag"] for z in zeilen), Decimal("0"))
    with (Session(create_engine(url)) if url else SessionLocal()) as db:
        db.execute(text("""
            INSERT INTO domain_sales.delivery_notes
                (id, tenant_id, delivery_note_number, customer_id, delivery_date, status, totals, created_at, updated_at)
            VALUES (:id, :t, :nr, :k, :d, :s, CAST(:summen AS jsonb), NOW(), NOW())
        """), {"id": kennung, "t": mandant, "nr": nummer or f"LS-T-{kennung[:8]}", "k": kunde, "d": lieferdatum,
               "s": status, "summen": json.dumps({"netto": float(netto)})})
        for z in zeilen:
            db.execute(text("""
                INSERT INTO domain_sales.delivery_note_positions
                    (id, tenant_id, delivery_note_id, pos_nr, artikel_id, artikel_nr, bezeichnung, menge, einheit, netto_preis,
                     netto_betrag, mwst_prozent, kontrakt_nr, created_at, updated_at)
                VALUES (:id, :t, :ls, :pos_nr, :artikel_id, :artikel_nr, :bezeichnung, :menge, :einheit, :netto_preis,
                        :netto_betrag, :mwst_prozent, :kontrakt_nr, NOW(), NOW())
            """), {**z, "ls": kennung, "t": mandant})
        DocumentAllocationService(db, mandant).register_document_lines(
            "delivery_note", kennung, [LineToRegister.from_mapping(z) for z in zeilen])
        db.commit()
    return kennung
