"""QS-CHARGE-001: Qualitätsprotokoll → Preisabschlag-Kalkulation.

Verbindet QualityProtocol mit HarvestAcceptance und berechnet automatische
Zu-/Abschläge (Feuchte, Protein, Mykotoxine, HL-Gewicht) für die Abrechnung.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


# Standard-Abschlagsregeln (Landhandel-Referenz)
_DEFAULT_DEDUCTION_RULES = {
    # Feuchte: Basis 14%. Jedes Prozent über Basis → Abzug per Tonne
    "feuchte": {"basis_pct": Decimal("14.0"), "abschlag_eur_per_pct_per_t": Decimal("2.00")},
    # Unreinheiten: Basis 2%. Jedes Prozent über Basis → Abzug per Tonne
    "unreinheiten": {"basis_pct": Decimal("2.0"), "abschlag_eur_per_pct_per_t": Decimal("1.50")},
    # HL-Gewicht: Basis 76 kg/hl Weizen. Jeder kg darunter → Abzug per Tonne
    "hl_gewicht": {"basis_kg_hl": Decimal("76.0"), "abschlag_eur_per_kg_hl_per_t": Decimal("0.50")},
    # Mykotoxine: Schwellenwert 1250 ppb DON; bei Überschreitung Vollsperrung
    "mykotoxine": {"grenzwert_ppb": Decimal("1250"), "abschlag_pct_vom_preis": Decimal("0")},
}


class QsChargeService:
    """Berechnet QS-basierte Zu-/Abschläge für Ernte-Annahmen."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def get_quality_protocol_for_acceptance(self, acceptance_id: str) -> dict | None:
        """Lädt das finale QS-Protokoll für eine Annahme."""
        row = self.db.execute(
            text("""
                SELECT qp.*
                FROM domain_agrar.quality_protocols qp
                WHERE qp.harvest_acceptance_id = :aid
                  AND qp.tenant_id = :tid
                ORDER BY qp.is_final DESC, qp.created_at DESC
                LIMIT 1
            """),
            {"aid": acceptance_id, "tid": self.tenant_id},
        ).mappings().first()
        return dict(row) if row else None

    def calculate_deductions(
        self,
        *,
        acceptance_id: str,
        net_weight_kg: Decimal,
        unit_price_eur_per_t: Decimal,
        quality_protocol: dict | None = None,
        custom_rules: dict | None = None,
    ) -> dict[str, Any]:
        """Berechnet QS-Abschläge für eine Annahme.

        Returns:
            {
              "deductions": [{"typ": ..., "beschreibung": ..., "abschlag_eur": ...}],
              "total_deduction_eur": Decimal,
              "sperrung": bool,
              "sperrgrund": str | None,
            }
        """
        if quality_protocol is None:
            quality_protocol = self.get_quality_protocol_for_acceptance(acceptance_id) or {}

        rules = custom_rules or _DEFAULT_DEDUCTION_RULES
        net_t = net_weight_kg / Decimal("1000")
        deductions: list[dict] = []
        sperrung = False
        sperrgrund = None

        # Feuchte-Abschlag
        feuchte = quality_protocol.get("moisture_pct")
        if feuchte is not None:
            feuchte = Decimal(str(feuchte))
            r = rules.get("feuchte", {})
            basis = Decimal(str(r.get("basis_pct", "14.0")))
            satz = Decimal(str(r.get("abschlag_eur_per_pct_per_t", "2.00")))
            if feuchte > basis:
                ueberschuss = (feuchte - basis).quantize(Decimal("0.01"))
                abschlag = (ueberschuss * satz * net_t).quantize(Decimal("0.01"))
                deductions.append({
                    "typ": "feuchte",
                    "beschreibung": f"Feuchte {feuchte}% (Basis {basis}%, +{ueberschuss}%)",
                    "menge": float(ueberschuss),
                    "einheit": "% über Basis",
                    "satz_eur": float(satz),
                    "abschlag_eur": float(abschlag),
                })

        # Unreinheiten-Abschlag
        unrein = quality_protocol.get("impurities_pct")
        if unrein is not None:
            unrein = Decimal(str(unrein))
            r = rules.get("unreinheiten", {})
            basis = Decimal(str(r.get("basis_pct", "2.0")))
            satz = Decimal(str(r.get("abschlag_eur_per_pct_per_t", "1.50")))
            if unrein > basis:
                ueberschuss = (unrein - basis).quantize(Decimal("0.01"))
                abschlag = (ueberschuss * satz * net_t).quantize(Decimal("0.01"))
                deductions.append({
                    "typ": "unreinheiten",
                    "beschreibung": f"Unreinheiten {unrein}% (Basis {basis}%, +{ueberschuss}%)",
                    "menge": float(ueberschuss),
                    "einheit": "% über Basis",
                    "satz_eur": float(satz),
                    "abschlag_eur": float(abschlag),
                })

        # HL-Gewicht-Abschlag
        hl_gew = quality_protocol.get("hl_weight_kg_per_hl")
        if hl_gew is not None:
            hl_gew = Decimal(str(hl_gew))
            r = rules.get("hl_gewicht", {})
            basis = Decimal(str(r.get("basis_kg_hl", "76.0")))
            satz = Decimal(str(r.get("abschlag_eur_per_kg_hl_per_t", "0.50")))
            if hl_gew < basis:
                unterschuss = (basis - hl_gew).quantize(Decimal("0.1"))
                abschlag = (unterschuss * satz * net_t).quantize(Decimal("0.01"))
                deductions.append({
                    "typ": "hl_gewicht",
                    "beschreibung": f"HL-Gew. {hl_gew} kg/hl (Basis {basis}, -{unterschuss})",
                    "menge": float(unterschuss),
                    "einheit": "kg/hl unter Basis",
                    "satz_eur": float(satz),
                    "abschlag_eur": float(abschlag),
                })

        # Mykotoxin-Sperrung
        myko = quality_protocol.get("mycotoxin_ppb")
        if myko is not None:
            myko = Decimal(str(myko))
            r = rules.get("mykotoxine", {})
            grenz = Decimal(str(r.get("grenzwert_ppb", "1250")))
            if myko > grenz:
                sperrung = True
                sperrgrund = f"Mykotoxin-Grenzwert überschritten: {myko} ppb (Limit {grenz} ppb)"

        total = Decimal(str(sum(d["abschlag_eur"] for d in deductions))).quantize(Decimal("0.01"))

        return {
            "acceptance_id": acceptance_id,
            "net_weight_kg": float(net_weight_kg),
            "net_weight_t": float(net_t),
            "unit_price_eur_per_t": float(unit_price_eur_per_t),
            "gross_amount_eur": float((net_t * unit_price_eur_per_t).quantize(Decimal("0.01"))),
            "deductions": deductions,
            "total_deduction_eur": float(total),
            "net_amount_eur": float((net_t * unit_price_eur_per_t - total).quantize(Decimal("0.01"))),
            "sperrung": sperrung,
            "sperrgrund": sperrgrund,
            "qualitaetsprotokoll_id": quality_protocol.get("id"),
        }

    def link_quality_protocol_to_acceptance(
        self,
        acceptance_id: str,
        quality_protocol_id: str,
    ) -> None:
        """Setzt quality_protocol_id auf harvest_acceptances (QS-CHARGE-001)."""
        self.db.execute(
            text("""
                UPDATE domain_agrar.harvest_acceptances
                SET quality_protocol_id = :qpid,
                    updated_at = NOW()
                WHERE id = :aid AND tenant_id = :tid
            """),
            {"qpid": quality_protocol_id, "aid": acceptance_id, "tid": self.tenant_id},
        )
        self.db.commit()
