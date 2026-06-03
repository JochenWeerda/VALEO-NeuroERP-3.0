"""CRM Lead-Generierung — region-universale Lead-Kandidaten aus offenen Quellen.

Erzeugt Lead-Kandidaten für den Außendienst aus:
- **GAP** (``gap_payments``): EU-Agrarförderempfänger, je Betrieb aggregiert,
  Top-Prozent nach Fördersumme.
- **LKV** (``dairy_herd_performance``): Milchviehbetriebe, Top-Prozent nach
  Milchleistung.

**Region-universal (DACH):** Filterung über einen freien PLZ-Bereich
(``plz_min``–``plz_max``), nicht auf eine Region hartcodiert. Damit für jede
Vertriebsregion (DE/AT/CH, sofern entsprechende Quelldaten geladen sind)
einsetzbar. Reine Lese-/Vorschau-Schicht (keine Mutation).
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

# Offensichtliche Nicht-Betriebe (Behörden/Verbände/Kommunen/Flur-/Jagdkörper).
_GAP_NAME_EXCLUDE = (
    "beneficiary_name_raw NOT ILIKE ALL (ARRAY["
    "'%NLWKN%', '%verband%', '%Gemeinde%', '%Samtgemeinde%', '%Landkreis%', "
    "'%Stadt %', '% Stadt%', '%e. V.%', '%e.V.%', '%Deich%', '%Wasser%', '%Amt %', "
    "'%Sielacht%', 'TG %', '%Realverband%', '%Realgemeinde%', '%Jagdgenossensch%', "
    "'%Teichgenoss%', '%Kirchengem%', '%Kloster%', '%Teilnehmergemeinschaft%', "
    "'%Nationalpark%', '%Wegegenoss%', '%Beregnung%', '%verwaltung%'])"
)


def _plz_clause(col: str, plz_min: Optional[str], plz_max: Optional[str], params: dict) -> str:
    if plz_min and plz_max:
        params["plz_min"], params["plz_max"] = plz_min, plz_max
        return f" AND {col} BETWEEN :plz_min AND :plz_max"
    if plz_min:
        params["plz_min"] = plz_min
        return f" AND {col} >= :plz_min"
    if plz_max:
        params["plz_max"] = plz_max
        return f" AND {col} <= :plz_max"
    return ""


def gap_candidates(db: Session, plz_min: Optional[str], plz_max: Optional[str],
                   top_pct: float, max_leads: int) -> list[dict]:
    params: dict = {"pct": top_pct, "lim": max_leads}
    clause = _plz_clause("postal_code", plz_min, plz_max, params)
    rows = db.execute(
        text(
            f"""
            WITH scoped AS (
                SELECT beneficiary_name_norm AS name_norm,
                       max(beneficiary_name_raw)            AS name,
                       postal_code                          AS plz,
                       replace(max(city), ', Stadt', '')    AS ort,
                       max(street_raw)                      AS strasse,
                       sum(amount_total)                    AS score
                FROM gap_payments
                WHERE beneficiary_name_norm IS NOT NULL AND {_GAP_NAME_EXCLUDE}{clause}
                GROUP BY beneficiary_name_norm, postal_code
            ), ranked AS (
                SELECT *, percent_rank() OVER (ORDER BY score DESC) AS pr FROM scoped
            )
            SELECT name, plz, ort, strasse, round(score) AS score
            FROM ranked WHERE pr < :pct ORDER BY score DESC LIMIT :lim
            """
        ),
        params,
    ).mappings().all()
    return [{**dict(r), "quelle": "gap", "score_label": "Fördersumme €"} for r in rows]


def lkv_candidates(db: Session, plz_min: Optional[str], plz_max: Optional[str],
                   top_pct: float, max_leads: int) -> list[dict]:
    params: dict = {"pct": top_pct, "lim": max_leads}
    clause = _plz_clause("postal_code", plz_min, plz_max, params)
    rows = db.execute(
        text(
            f"""
            WITH scoped AS (
                SELECT name_norm, max(besitzer_raw) AS name, postal_code AS plz,
                       max(ort) AS ort, max(milch_kg) AS score
                FROM dairy_herd_performance
                WHERE besitzer_raw IS NOT NULL{clause}
                GROUP BY name_norm, postal_code
            ), ranked AS (
                SELECT *, percent_rank() OVER (ORDER BY score DESC NULLS LAST) AS pr FROM scoped
            )
            SELECT name, plz, ort, NULL AS strasse, round(score) AS score
            FROM ranked WHERE pr < :pct ORDER BY score DESC NULLS LAST LIMIT :lim
            """
        ),
        params,
    ).mappings().all()
    return [{**dict(r), "quelle": "lkv", "score_label": "Milch kg/Kuh"} for r in rows]


class CrmLeadGenService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def preview(self, *, quelle: str = "gap", plz_min: Optional[str] = None,
                plz_max: Optional[str] = None, top_pct: float = 0.10,
                max_leads: int = 200) -> dict:
        """Lead-Kandidaten-Vorschau. quelle: 'gap' | 'lkv' | 'beide'."""
        top_pct = max(0.01, min(1.0, top_pct))
        max_leads = max(1, min(2000, max_leads))
        cands: list[dict] = []
        if quelle in ("gap", "beide"):
            cands += gap_candidates(self.db, plz_min, plz_max, top_pct, max_leads)
        if quelle in ("lkv", "beide"):
            cands += lkv_candidates(self.db, plz_min, plz_max, top_pct, max_leads)
        return {
            "quelle": quelle,
            "plz_min": plz_min,
            "plz_max": plz_max,
            "top_pct": top_pct,
            "anzahl": len(cands),
            "kandidaten": cands[:max_leads],
        }
