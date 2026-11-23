"""Mahnstufe eines offenen Postens: eskalieren und Verlauf - ueber den einen Mahnweg (M3, 23.11.2026).

Bis 23.11.2026 schrieb dieser Dienst einen eigenen Verlauf (``domain_finance.finance_mahnstufen_audit``) mit
eigenen Stufen (1, 2, 3, INKASSO) und Gebuehren - ohne Mahnung, ohne Stufe am offenen Posten. Die Maskenaktion
"Mahnung erstellen" meldete eine Mahnstufe, die der Mahnlauf nicht kannte. Jetzt erzeugt die Eskalation eine
Mahnung ueber ``FinanceDunningService.run_dunning`` (Regeln, Gebuehr, Zinsen, Frist, Stufe am Posten), und der
Verlauf sind die Mahnungen des Postens.
"""
from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session


class MahnstufeError(Exception):
    """Der Posten ist nicht mahnfaellig (nicht ueberfaellig, Frist der letzten Mahnung laeuft, hoechste Stufe)."""


def eskaliere_mahnstufe(db: Session, rechnungsnr: str, tenant_id: str, operator: str = "system") -> Dict[str, Any]:
    """Mahnt den Debitorenposten ``rechnungsnr`` eine Stufe weiter - eine Mahnung, keine Stufe ohne Mahnung."""
    from app.services.finance_dunning_service import FinanceDunningService

    ergebnis = FinanceDunningService(db, tenant_id).run_dunning(rechnungsnr=rechnungsnr, bediener=operator)
    if not ergebnis.get("erzeugt"):
        raise MahnstufeError(
            f"Rechnung {rechnungsnr} ist nicht mahnfällig: nicht überfällig, die Zahlungsfrist der letzten Mahnung "
            "läuft noch oder die höchste Mahnstufe ist erreicht."
        )
    mahnung = ergebnis["mahnungen"][0]
    vorher = mahnung.get("vorherige_stufe")
    return {
        "id": mahnung["id"],
        "tenant_id": tenant_id,
        "rechnungsnr": rechnungsnr,
        "stufe": str(mahnung["stufe"]),
        "vorherige_stufe": str(vorher) if vorher else None,
        "bearbeitungsgebuehr_eur": mahnung.get("gebuehr"),
        "operator": operator,
    }


def get_mahnstufen_trail(db: Session, rechnungsnr: str, tenant_id: str) -> List[Dict[str, Any]]:
    """Die Mahnungen des Postens chronologisch - der Verlauf seiner Mahnstufe."""
    rows = db.execute(
        text(
            "SELECT n.id, n.tenant_id, o.rechnungsnr, n.dunning_level, n.dunning_fee, n.notes, n.created_at "
            "FROM domain_erp.dunning_notices n "
            "JOIN domain_erp.offene_posten o ON o.id = n.op_id AND o.tenant_id = n.tenant_id "
            "WHERE n.tenant_id = :t AND o.rechnungsnr = :r "
            "ORDER BY n.dunning_date, n.created_at, n.dunning_level"
        ),
        {"t": tenant_id, "r": rechnungsnr},
    ).mappings().all()
    verlauf: List[Dict[str, Any]] = []
    vorher = None
    for r in rows:
        stufe = str(r["dunning_level"])
        verlauf.append({
            "id": str(r["id"]), "tenant_id": r["tenant_id"], "rechnungsnr": r["rechnungsnr"], "stufe": stufe,
            "vorherige_stufe": vorher, "bearbeitungsgebuehr_eur": float(r["dunning_fee"] or 0),
            "operator": r["notes"], "created_at": r["created_at"],
        })
        vorher = stufe
    return verlauf
