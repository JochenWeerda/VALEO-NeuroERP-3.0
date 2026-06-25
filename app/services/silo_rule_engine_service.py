"""WM-SILO-RULE-ENGINE-001 — Automatische Zielzellen-Vorschlaege fuer Einlagerung.

Liest silo_cells und silo_lots aus domain_inventory und empfiehlt Zielzellen
basierend auf: Artikel-Kompatibilitaet, verfuegbarer Kapazitaet, QS-Status,
Erntejahr-Segregation und Belegungsgrad.

Regel-Prioritaet (absteigend):
  1. Gleicher Artikel + gleiches Erntejahr + QS FREIGEGEBEN + ausreichend Kapazitaet
  2. Leere Zelle (kein aktuelles Material) + ausreichend Kapazitaet
  3. Gleicher Artikel + beliebiges Erntejahr + ausreichend Kapazitaet
  4. Alle Zellen mit ausreichend freier Kapazitaet (generisch)
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class VorschlagGrund(str, Enum):
    GLEICHER_ARTIKEL_GLEICHES_ERNTEJAHR = "gleicher_artikel_gleiches_erntejahr"
    LEERE_ZELLE = "leere_zelle"
    GLEICHER_ARTIKEL = "gleicher_artikel"
    GENERISCH_KAPAZITAET = "generisch_kapazitaet"


@dataclass
class ZielzelleVorschlag:
    cell_id: str
    cell_code: str
    warehouse_id: str
    kapazitaet_kg: Decimal
    aktueller_bestand_kg: Decimal
    freie_kapazitaet_kg: Decimal
    belegungsgrad_pct: float
    aktuelles_material_id: str | None
    aktuelles_lot_id: str | None
    qs_status: str | None
    grund: VorschlagGrund
    rang: int
    hinweis: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "cell_code": self.cell_code,
            "warehouse_id": self.warehouse_id,
            "kapazitaet_kg": float(self.kapazitaet_kg),
            "aktueller_bestand_kg": float(self.aktueller_bestand_kg),
            "freie_kapazitaet_kg": float(self.freie_kapazitaet_kg),
            "belegungsgrad_pct": round(self.belegungsgrad_pct, 1),
            "aktuelles_material_id": self.aktuelles_material_id,
            "aktuelles_lot_id": self.aktuelles_lot_id,
            "qs_status": self.qs_status,
            "grund": self.grund.value,
            "rang": self.rang,
            "hinweis": self.hinweis,
        }


class SiloRuleEngineService:
    """Regelbasierte Zielzellen-Vorschlaege fuer Agrar-Einlagerung."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def _load_cells(self, warehouse_id: str | None = None) -> list[dict[str, Any]]:
        sql = """
            SELECT
                sc.id,
                sc.warehouse_id,
                sc.cell_code,
                sc.capacity_kg,
                COALESCE(sc.current_stock_kg, 0) AS current_stock_kg,
                sc.current_material_id,
                sc.current_lot_id,
                sc.qs_status,
                sc.is_active,
                sl.ernte_jahr,
                sl.qualitaetsklasse
            FROM domain_inventory.silo_cells sc
            LEFT JOIN domain_inventory.silo_lots sl
                ON sl.id = sc.current_lot_id
                AND sl.tenant_id = sc.tenant_id
            WHERE sc.tenant_id = :tid
              AND sc.is_active = true
              AND COALESCE(sc.qs_status, '') != 'gesperrt'
        """
        params: dict[str, Any] = {"tid": self.tenant_id}
        if warehouse_id:
            sql += " AND sc.warehouse_id = :wid"
            params["wid"] = warehouse_id
        rows = self.db.execute(text(sql), params).fetchall()
        return [dict(r._mapping) for r in rows]

    def _lot_info(self, lot_id: str) -> dict[str, Any] | None:
        row = self.db.execute(
            text("""
                SELECT l.id, l.article_id, l.ernte_jahr, l.qualitaetsklasse,
                       l.status, s.is_active as silo_active
                FROM domain_inventory.silo_lots l
                JOIN domain_inventory.silos s
                  ON s.id = l.silo_id AND s.tenant_id = l.tenant_id
                WHERE l.id = :lot_id AND l.tenant_id = :tid
            """),
            {"lot_id": lot_id, "tid": self.tenant_id},
        ).fetchone()
        return dict(row._mapping) if row else None

    def vorschlag(
        self,
        *,
        artikel_id: str,
        menge_kg: float,
        ernte_jahr: int | None = None,
        qualitaetsklasse: str | None = None,
        warehouse_id: str | None = None,
        max_vorschlaege: int = 5,
    ) -> list[dict[str, Any]]:
        """Gibt gerankte Zielzellen-Vorschlaege zurueck."""
        cells = self._load_cells(warehouse_id)
        menge = Decimal(str(menge_kg))
        vorschlaege: list[ZielzelleVorschlag] = []

        for c in cells:
            kap = Decimal(str(c.get("capacity_kg") or 0))
            bestand = Decimal(str(c.get("current_stock_kg") or 0))
            frei = kap - bestand
            if frei < menge:
                continue  # nicht genug Platz

            belegung = float((bestand / kap * 100) if kap > 0 else Decimal("0"))
            mat_id = c.get("current_material_id")
            lot_id_cell = c.get("current_lot_id")
            qs = c.get("qs_status")
            zell_erntejahr = c.get("ernte_jahr")
            zell_klasse = c.get("qualitaetsklasse")

            # Regel 1: Gleicher Artikel + gleiches Erntejahr + FREIGEGEBEN
            if (
                mat_id == artikel_id
                and ernte_jahr
                and zell_erntejahr == ernte_jahr
                and str(qs or "").upper() in ("FREIGEGEBEN", "QS_FREIGEGEBEN", "")
            ):
                vorschlaege.append(ZielzelleVorschlag(
                    cell_id=str(c["id"]),
                    cell_code=str(c["cell_code"]),
                    warehouse_id=str(c["warehouse_id"]),
                    kapazitaet_kg=kap,
                    aktueller_bestand_kg=bestand,
                    freie_kapazitaet_kg=frei,
                    belegungsgrad_pct=belegung,
                    aktuelles_material_id=mat_id,
                    aktuelles_lot_id=lot_id_cell,
                    qs_status=qs,
                    grund=VorschlagGrund.GLEICHER_ARTIKEL_GLEICHES_ERNTEJAHR,
                    rang=1,
                    hinweis=f"Gleicher Artikel {artikel_id}, Erntejahr {ernte_jahr}, QS freigegeben",
                ))
                continue

            # Regel 2: Leere Zelle
            if mat_id is None and bestand == Decimal("0"):
                vorschlaege.append(ZielzelleVorschlag(
                    cell_id=str(c["id"]),
                    cell_code=str(c["cell_code"]),
                    warehouse_id=str(c["warehouse_id"]),
                    kapazitaet_kg=kap,
                    aktueller_bestand_kg=bestand,
                    freie_kapazitaet_kg=frei,
                    belegungsgrad_pct=belegung,
                    aktuelles_material_id=None,
                    aktuelles_lot_id=None,
                    qs_status=qs,
                    grund=VorschlagGrund.LEERE_ZELLE,
                    rang=2,
                    hinweis="Leere Zelle — saubere Segregation moeglich",
                ))
                continue

            # Regel 3: Gleicher Artikel (beliebiges Erntejahr)
            if mat_id == artikel_id:
                hinweis = f"Gleicher Artikel {artikel_id}"
                if zell_erntejahr and ernte_jahr and zell_erntejahr != ernte_jahr:
                    hinweis += f" — Erntejahr {zell_erntejahr} abweichend von {ernte_jahr} (Mischung pruefen)"
                vorschlaege.append(ZielzelleVorschlag(
                    cell_id=str(c["id"]),
                    cell_code=str(c["cell_code"]),
                    warehouse_id=str(c["warehouse_id"]),
                    kapazitaet_kg=kap,
                    aktueller_bestand_kg=bestand,
                    freie_kapazitaet_kg=frei,
                    belegungsgrad_pct=belegung,
                    aktuelles_material_id=mat_id,
                    aktuelles_lot_id=lot_id_cell,
                    qs_status=qs,
                    grund=VorschlagGrund.GLEICHER_ARTIKEL,
                    rang=3,
                    hinweis=hinweis,
                ))
                continue

            # Regel 4: Generisch — nur Kapazitaet
            vorschlaege.append(ZielzelleVorschlag(
                cell_id=str(c["id"]),
                cell_code=str(c["cell_code"]),
                warehouse_id=str(c["warehouse_id"]),
                kapazitaet_kg=kap,
                aktueller_bestand_kg=bestand,
                freie_kapazitaet_kg=frei,
                belegungsgrad_pct=belegung,
                aktuelles_material_id=mat_id,
                aktuelles_lot_id=lot_id_cell,
                qs_status=qs,
                grund=VorschlagGrund.GENERISCH_KAPAZITAET,
                rang=4,
                hinweis=f"Freie Kapazitaet {float(frei):.0f} kg — Artikel-Mischung beachten",
            ))

        # Sortieren: Rang aufsteigend, dann freie Kapazitaet absteigend
        vorschlaege.sort(key=lambda v: (v.rang, -float(v.freie_kapazitaet_kg)))
        return [v.to_dict() for v in vorschlaege[:max_vorschlaege]]

    def vorschlag_fuer_lot(
        self,
        *,
        lot_id: str,
        menge_kg: float | None = None,
        warehouse_id: str | None = None,
        max_vorschlaege: int = 5,
    ) -> dict[str, Any]:
        """Vorschlag direkt aus einem Lot-Datensatz ableiten."""
        lot = self._lot_info(lot_id)
        if not lot:
            return {
                "fehler": f"Lot '{lot_id}' nicht gefunden oder nicht aktiv",
                "vorschlaege": [],
            }
        artikel_id = lot.get("article_id") or ""
        ernte_jahr = lot.get("ernte_jahr")
        qualitaetsklasse = lot.get("qualitaetsklasse")

        vorschlaege = self.vorschlag(
            artikel_id=artikel_id,
            menge_kg=menge_kg or 1.0,
            ernte_jahr=ernte_jahr,
            qualitaetsklasse=qualitaetsklasse,
            warehouse_id=warehouse_id,
            max_vorschlaege=max_vorschlaege,
        )
        return {
            "lot_id": lot_id,
            "artikel_id": artikel_id,
            "ernte_jahr": ernte_jahr,
            "qualitaetsklasse": qualitaetsklasse,
            "angefragte_menge_kg": menge_kg,
            "vorschlaege": vorschlaege,
            "anzahl_vorschlaege": len(vorschlaege),
        }
