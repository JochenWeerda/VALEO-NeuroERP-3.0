"""DEV-Seed: public.kunden mit Top-10%-Betrieben aus GAP + LKV befüllen.

Zielregion: Landkreise **Aurich, Emden, Leer, Wittmund, Friesland** sowie die
kreisfreie Stadt **Wilhelmshaven** (PLZ 263xx–268xx, ohne 2687x Papenburg/Emsland).

Zwei Quellen:
- **GAP-Empfänger** (`gap_payments`): je Betrieb (name_norm+PLZ) über alle Maßnahmen
  summiert; Top 10 % nach Förderbetrag. Offensichtliche Nicht-Betriebe
  (NLWKN, Verbände, Gemeinden) werden per Namensfilter ausgeschlossen.
- **Milchviehhalter** (`dairy_herd_performance`): Top 10 % nach Milchleistung (kg).

Schreibt nach `public.kunden` (kunden_nr-Präfix `GAP`/`MV` als Quell-Marker),
dedupliziert GAP↔Dairy über (name_norm, PLZ) und füllt anschließend die
Domänensatelliten via `kunden_backfill`. **Idempotent**: entfernt vorab die
zuvor geseedeten `GAP%`/`MV%`-Kunden (CASCADE), nie die Original-Testkunden.

Reiner DEV-Seed. CLI:
    python -m scripts.seed_kunden_from_gap_lkv            # Dry-Run (zählt nur)
    python -m scripts.seed_kunden_from_gap_lkv --apply    # schreibt
"""

from __future__ import annotations

import sys

from sqlalchemy import text
from sqlalchemy.orm import Session

# PLZ-Scope: 5 Kreise + Wilhelmshaven. Ausgeschlossen: 2687x Papenburg/Emsland
# sowie Ammerland/Cloppenburg-Ränder im 266xx-Band (Westerstede/Apen/Barßel/Saterland).
_PLZ_SCOPE = (
    "postal_code ~ '^26[3-8]' "
    "AND left(postal_code, 4) <> '2687' "
    "AND postal_code NOT IN ('26655', '26676', '26683', '26689')"
)

# Offensichtliche Nicht-Betriebe ausschließen: Behörden, Kommunen sowie
# Entwässerungs-/Flur-/Jagd-Körperschaften (Sielacht, Teich-/Teilnehmergemeinschaft
# "TG", Realverband/-gemeinde, Jagdgenossenschaft) — sie dominieren die GAP-Spitze,
# sind aber keine landwirtschaftlichen Betriebe.
_NAME_EXCLUDE = (
    "beneficiary_name_raw NOT ILIKE ALL (ARRAY["
    "'%NLWKN%', '%verband%', '%Gemeinde%', '%Samtgemeinde%', '%Landkreis%', "
    "'%Stadt %', '% Stadt%', '%e. V.%', '%e.V.%', '%Deich%', '%Wasser%', '%Amt %', "
    "'%Sielacht%', 'TG %', '%Realverband%', '%Realgemeinde%', '%Jagdgenossensch%', "
    "'%Teichgenoss%', '%Kirchengem%', '%Kloster%', '%Teilnehmergemeinschaft%', "
    "'%Nationalpark%', '%Wegegenoss%', '%Beregnung%', '%verwaltung%'])"
)


def fetch_gap_top(db: Session, pct: float) -> list[dict]:
    rows = db.execute(
        text(
            f"""
            WITH scoped AS (
                SELECT beneficiary_name_norm                  AS name_norm,
                       max(beneficiary_name_raw)              AS name,
                       postal_code                            AS plz,
                       replace(max(city), ', Stadt', '')      AS ort,
                       max(street_raw)                        AS strasse,
                       sum(amount_total)                      AS tot
                FROM gap_payments
                WHERE {_PLZ_SCOPE}
                  AND beneficiary_name_norm IS NOT NULL
                  AND {_NAME_EXCLUDE}
                GROUP BY beneficiary_name_norm, postal_code
            ), ranked AS (
                SELECT *, percent_rank() OVER (ORDER BY tot DESC) AS pr FROM scoped
            )
            SELECT name_norm, name, plz, ort, strasse, tot
            FROM ranked WHERE pr < :pct
            ORDER BY tot DESC, name_norm
            """
        ),
        {"pct": pct},
    ).mappings().all()
    return [dict(r) for r in rows]


def fetch_dairy_top(db: Session, pct: float) -> list[dict]:
    rows = db.execute(
        text(
            f"""
            WITH scoped AS (
                SELECT name_norm,
                       max(besitzer_raw)  AS name,
                       postal_code        AS plz,
                       max(ort)           AS ort,
                       max(milch_kg)      AS milch
                FROM dairy_herd_performance
                WHERE {_PLZ_SCOPE.replace('postal_code', 'postal_code')}
                  AND besitzer_raw IS NOT NULL
                GROUP BY name_norm, postal_code
            ), ranked AS (
                SELECT *, percent_rank() OVER (ORDER BY milch DESC NULLS LAST) AS pr FROM scoped
            )
            SELECT name_norm, name, plz, ort, milch
            FROM ranked WHERE pr < :pct
            ORDER BY milch DESC NULLS LAST, name_norm
            """
        ),
        {"pct": pct},
    ).mappings().all()
    return [dict(r) for r in rows]


def seed(db: Session, pct: float = 0.10, apply: bool = False) -> dict:
    gap = fetch_gap_top(db, pct)
    dairy = fetch_dairy_top(db, pct)

    gap_keys = {(g["name_norm"], g["plz"]) for g in gap}
    dairy_new = [d for d in dairy if (d["name_norm"], d["plz"]) not in gap_keys]
    overlap = len(dairy) - len(dairy_new)

    result = {
        "gap_top": len(gap),
        "dairy_top": len(dairy),
        "dairy_overlap_mit_gap": overlap,
        "dairy_neu": len(dairy_new),
        "gesamt_neu": len(gap) + len(dairy_new),
        "applied": apply,
    }
    if not apply:
        return result

    # Idempotenz: zuvor geseedete Datensätze entfernen (nie K0000x).
    db.execute(text("DELETE FROM public.kunden WHERE kunden_nr LIKE 'GAP%' OR kunden_nr LIKE 'MV%'"))

    ins = text(
        "INSERT INTO public.kunden (kunden_nr, name1, strasse, plz, ort, land, geloescht, erstellt_am) "
        "VALUES (:kn, :name, :strasse, :plz, :ort, 'DE', FALSE, now())"
    )
    for i, g in enumerate(gap, start=1):
        db.execute(ins, {
            "kn": f"GAP{i:05d}",
            "name": (g["name"] or g["name_norm"])[:200],
            "strasse": (g.get("strasse") or None),
            "plz": g["plz"],
            "ort": (g.get("ort") or None),
        })
    for i, d in enumerate(dairy_new, start=1):
        db.execute(ins, {
            "kn": f"MV{i:04d}",
            "name": (d["name"] or d["name_norm"])[:200],
            "strasse": None,
            "plz": d["plz"],
            "ort": (d.get("ort") or None),
        })
    db.commit()

    # Satelliten füllen (Adresse etc.) über das bestehende Backfill-Tool.
    from app.services.kunden_backfill import run_backfill
    bf = run_backfill(db, apply=True)
    result["backfill"] = bf.counts
    result["kunden_gesamt_danach"] = db.execute(
        text("SELECT count(*) FROM public.kunden WHERE coalesce(geloescht, FALSE) = FALSE")
    ).scalar()
    return result


def main() -> None:
    from app.core.database import SessionLocal

    apply = "--apply" in sys.argv
    pct = 0.10
    for a in sys.argv:
        if a.startswith("--pct="):
            pct = float(a.split("=", 1)[1]) / 100.0

    db = SessionLocal()
    try:
        res = seed(db, pct=pct, apply=apply)
        mode = "APPLY" if apply else "DRY-RUN"
        print(f"# Seed Kunden aus GAP+LKV ({mode}, top {pct*100:.0f}%) — Kreise Aurich/Emden/Leer/Wittmund/Friesland")
        for k, v in res.items():
            print(f"- {k:26} {v}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
