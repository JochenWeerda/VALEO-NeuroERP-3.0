"""Mitgelieferte Grundmengeneinheiten (a.eins: "die gaengigsten Mengeneinheiten werden als Grundeinheit mit
ausgeliefert"), Nutzerauftrag 24.11.2026.

Eine Quelle fuer Kuerzel, Bezeichnung, UN/ECE-Code (Recommendation 20, Pflicht in der E-Rechnung) und Rundung der
Grundeinheiten. Umrechnungsfaktoren nur fuer global exakte Groessen (Masse, Volumen - ``app/core/agrar_units.py``);
Zaehleinheiten (Sack, Palette, Big Bag) bekommen keinen Faktor, der haengt am Artikel (Gebinde).

``richte_grundeinheiten_ein`` legt fehlende Grundeinheiten fuer einen Mandanten an; vorhandene bleiben unveraendert.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


@dataclass(frozen=True)
class Grundeinheit:
    nummer: int
    kuerzel: str
    bezeichnung: str
    un_code: str
    dezimalstellen: int
    basis: Optional[str] = None
    faktor: Optional[Decimal] = None


GRUNDEINHEITEN: tuple[Grundeinheit, ...] = (
    Grundeinheit(1, "st", "Stück", "C62", 0),
    Grundeinheit(2, "kg", "Kilogramm", "KGM", 3),
    Grundeinheit(3, "dt", "Dezitonne (100 kg)", "DTN", 2, "kg", Decimal("100")),
    Grundeinheit(4, "t", "Tonne", "TNE", 3, "kg", Decimal("1000")),
    Grundeinheit(5, "g", "Gramm", "GRM", 0, "kg", Decimal("0.001")),
    Grundeinheit(6, "l", "Liter", "LTR", 3),
    Grundeinheit(7, "hl", "Hektoliter", "HLT", 2, "l", Decimal("100")),
    Grundeinheit(8, "ml", "Milliliter", "MLT", 0, "l", Decimal("0.001")),
    Grundeinheit(9, "m", "Meter", "MTR", 2),
    Grundeinheit(10, "m2", "Quadratmeter", "MTK", 2),
    Grundeinheit(11, "m3", "Kubikmeter", "MTQ", 3),
    Grundeinheit(12, "ha", "Hektar", "HAR", 4),
    Grundeinheit(13, "h", "Stunde", "HUR", 2),
    Grundeinheit(14, "sack", "Sack", "SA", 0),
    Grundeinheit(15, "pal", "Palette", "PF", 0),
)

UN_CODE = {g.kuerzel: g.un_code for g in GRUNDEINHEITEN}


def richte_grundeinheiten_ein(db: Session, tenant_id: str) -> list[str]:
    """Legt fehlende Grundeinheiten an und liefert ihre Kuerzel. Vorhandene (gleiches Kuerzel) bleiben, wie sie sind."""
    vorhanden = {str(r[0]).lower() for r in db.execute(text(
        "SELECT einheit_kuerzel FROM domain_shared.artikel_mengeneinheiten WHERE tenant_id = :t"),
        {"t": tenant_id}).fetchall()}
    belegt = {int(r[0]) for r in db.execute(text(
        "SELECT nummer FROM domain_shared.artikel_mengeneinheiten WHERE tenant_id = :t AND nummer IS NOT NULL"),
        {"t": tenant_id}).fetchall()}
    angelegt = []
    for g in GRUNDEINHEITEN:
        if g.kuerzel in vorhanden:
            continue
        db.execute(text(
            "INSERT INTO domain_shared.artikel_mengeneinheiten (id, tenant_id, nummer, einheit_kuerzel, bezeichnung, "
            "langtext, basis_einheit, umrechnungsfaktor, dezimalstellen, un_code, aktiv) "
            "VALUES (:id, :t, :nr, :kz, :bez, :bez, :basis, :faktor, :dez, :un, true)"),
            {"id": uuid7(), "t": tenant_id, "nr": None if g.nummer in belegt else g.nummer, "kz": g.kuerzel,
             "bez": g.bezeichnung, "basis": g.basis, "faktor": g.faktor, "dez": g.dezimalstellen, "un": g.un_code})
        angelegt.append(g.kuerzel)
    return angelegt
