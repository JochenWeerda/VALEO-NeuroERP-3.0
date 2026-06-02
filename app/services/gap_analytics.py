"""GAP-Analytik: Trend-/Wachstumsabschätzung aus mehreren Jahrgängen.

Baut auf den durch ``gap_pipeline`` befüllten Daten auf (View
``gap_payments_direct_agg``) und leitet aus dem Jahresvergleich der
Direktzahlungen ab, welche Betriebe **wachsen**, **stabil** sind,
**schrumpfen** oder **weichen** (aus der Liste verschwinden) – sowie
**Neueinsteiger**.

WICHTIG – relative statt absoluter Betrachtung:
Die EU-Direktzahlungen je ha sinken politisch gewollt von Jahr zu Jahr. Ein
Vergleich der absoluten EUR-Beträge (oder einer mit festem €/ha geschätzten
Fläche) würde daher fälschlich *alle* Betriebe als schrumpfend ausweisen.
Die Klassifizierung erfolgt deshalb über den **Anteil am Gebiets-Prämienpool**
(Share-of-Pool) je Jahr: ein gleichmäßiger €/ha-Schnitt kürzt Zähler und Nenner
gleich → Anteil bleibt konstant → korrekt „stabil". Nur wer seinen Anteil
relativ zu den Nachbarn steigert/verliert, gilt als wachsend/schrumpfend.

Matching erfolgt über (normalisierter Name, PLZ) – identisch zur
Begünstigten-Normalisierung des Imports.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.gap_pipeline import EUR_PER_HA, _plz_matches

# Wachstums-/Schrumpfungsschwelle (Prozent) für die Klassifizierung.
DEFAULT_GROWTH_THRESHOLD_PCT = 10.0

TREND_NEW = "neueinsteiger"
TREND_GROWING = "wachsend"
TREND_STABLE = "stabil"
TREND_SHRINKING = "schrumpfend"
TREND_EXITING = "weichend"


def _classify_relative(
    share0: Optional[float], share1: Optional[float], threshold_pct: float
) -> tuple[str, Optional[float]]:
    """Liefert (Trend-Label, relative Anteilsänderung in %).

    ``share0``/``share1`` = Anteil am Gebiets-Prämienpool im Vor-/Folgejahr.
    Die Klassifizierung ist damit unabhängig vom politisch sinkenden €/ha-Satz.
    """
    if not share0 and share1:
        return TREND_NEW, None
    if share0 and not share1:
        return TREND_EXITING, -100.0
    if not share0 and not share1:
        return TREND_STABLE, 0.0
    rel = (share1 - share0) / share0 * 100.0
    if rel > threshold_pct:
        return TREND_GROWING, rel
    if rel < -threshold_pct:
        return TREND_SHRINKING, rel
    return TREND_STABLE, rel


def growth_trend(
    db: Session,
    year_from: int,
    year_to: int,
    plz_filter: Optional[list[str]] = None,
    threshold_pct: float = DEFAULT_GROWTH_THRESHOLD_PCT,
    eur_per_ha: float = EUR_PER_HA,
) -> dict[str, Any]:
    """Vergleicht zwei Jahrgänge der GAP-Direktzahlungen je Begünstigtem.

    Returns ein Dict mit ``summary`` (Zähler je Trend, Flächen-Saldo) und
    ``rows`` (je Betrieb: Name, PLZ, Ort, Direktzahlung beide Jahre, Δ EUR,
    Δ %, geschätzte Fläche beide Jahre, Δ ha, Trend-Label).
    """
    rows_raw = db.execute(
        text(
            """
            WITH y0 AS (
                SELECT beneficiary_name_norm, postal_code,
                       MAX(city) AS city, SUM(direct_total_eur) AS d
                FROM gap_payments_direct_agg
                WHERE ref_year = :y0
                GROUP BY beneficiary_name_norm, postal_code
            ),
            y1 AS (
                SELECT beneficiary_name_norm, postal_code,
                       MAX(city) AS city, SUM(direct_total_eur) AS d
                FROM gap_payments_direct_agg
                WHERE ref_year = :y1
                GROUP BY beneficiary_name_norm, postal_code
            )
            SELECT
                COALESCE(y1.beneficiary_name_norm, y0.beneficiary_name_norm) AS name_norm,
                COALESCE(y1.postal_code, y0.postal_code)                     AS postal_code,
                COALESCE(y1.city, y0.city)                                   AS city,
                y0.d AS direct_from,
                y1.d AS direct_to
            FROM y0
            FULL OUTER JOIN y1
              ON y0.beneficiary_name_norm = y1.beneficiary_name_norm
             AND y0.postal_code = y1.postal_code
            """
        ),
        {"y0": year_from, "y1": year_to},
    ).mappings().all()

    # Pass 1: filtern und Gebiets-Prämienpool je Jahr bilden (Nenner für Share-of-Pool).
    farms: list[tuple[str, str, Optional[str], Optional[float], Optional[float]]] = []
    pool_from = 0.0
    pool_to = 0.0
    for r in rows_raw:
        plz = (r["postal_code"] or "").strip()
        if not _plz_matches(plz, plz_filter):
            continue
        d0 = float(r["direct_from"]) if r["direct_from"] is not None else None
        d1 = float(r["direct_to"]) if r["direct_to"] is not None else None
        pool_from += d0 or 0.0
        pool_to += d1 or 0.0
        farms.append((r["name_norm"], plz, r["city"], d0, d1))

    # Pass 2: Anteil am Pool je Jahr → relative Klassifizierung (€/ha-Politik herausgerechnet).
    counts = {TREND_NEW: 0, TREND_GROWING: 0, TREND_STABLE: 0, TREND_SHRINKING: 0, TREND_EXITING: 0}
    rows: list[dict[str, Any]] = []
    for name_norm, plz, city, d0, d1 in farms:
        share0 = (d0 / pool_from) if (d0 and pool_from) else None
        share1 = (d1 / pool_to) if (d1 and pool_to) else None
        trend, rel_pct = _classify_relative(share0, share1, threshold_pct)
        counts[trend] += 1
        # absolute EUR-Änderung nur als Kontext; Größe heute = geschätzte Fläche im Folgejahr.
        abs_pct = ((d1 - d0) / d0 * 100.0) if (d0 and d1) else None
        rows.append(
            {
                "name": name_norm,
                "postal_code": plz,
                "city": city,
                "direct_from_eur": round(d0, 2) if d0 is not None else None,
                "direct_to_eur": round(d1, 2) if d1 is not None else None,
                "share_from_pct": round(share0 * 100, 4) if share0 is not None else None,
                "share_to_pct": round(share1 * 100, 4) if share1 is not None else None,
                "rel_change_pct": round(rel_pct, 1) if rel_pct is not None else None,
                "abs_change_pct": round(abs_pct, 1) if abs_pct is not None else None,
                "area_to_ha": round((d1 / eur_per_ha), 1) if d1 else 0.0,
                "trend": trend,
            }
        )

    # Sortierung: stärkster relativer Anteilsgewinn zuerst (echte Wachstumskandidaten oben).
    rows.sort(key=lambda x: (x["rel_change_pct"] is None, x["rel_change_pct"] or 0), reverse=True)

    pool_change_pct = ((pool_to - pool_from) / pool_from * 100.0) if pool_from else None
    return {
        "year_from": year_from,
        "year_to": year_to,
        "plz_filter": plz_filter,
        "threshold_pct": threshold_pct,
        "method": "share_of_pool",  # relativ zum Gebiets-Prämienpool, €/ha-Politik herausgerechnet
        "summary": {
            "betriebe_gesamt": len(rows),
            **counts,
            "pool_from_eur": round(pool_from, 2),
            "pool_to_eur": round(pool_to, 2),
            "pool_change_pct": round(pool_change_pct, 1) if pool_change_pct is not None else None,
        },
        "rows": rows,
    }
