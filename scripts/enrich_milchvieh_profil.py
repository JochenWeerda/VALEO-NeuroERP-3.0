"""DEV-Anreicherung: kunden_milchvieh_profil aus LKV-Daten (+ synthetische Zellzahl).

Matcht die geseedeten Kunden (GAP%/MV%) gegen ``dairy_herd_performance`` (über
normalisierten Namen + PLZ) und befüllt je Milchvieh haltendem Kunden ein
1:1-Profil:

- **Echt (LKV):** Herdengrößen-Klasse + geschätzte Kuhzahl (Klassen-Mittel),
  milch_kg, fett_%/kg, eiw_%/kg, fett+eiweiss_kg, Erstkalbealter.
- **DEV-synthetisch:** somatische Zellzahl (x1000/ml) — die LKV-Extraktion erfasst
  den Zellzahl-/Milchgüte-Abschnitt (noch) nicht. Werte sind deterministisch je
  Kunde, plausibel verteilt (Mittel ~220, höher bei großen Herden) und über
  ``zellzahl_quelle='dev_synthetik'`` klar markiert. Daraus ``hygiene_bedarf``
  (niedrig/mittel/hoch) als Indikator fuer Eutergesundheits-/Hygiene-Mittel.

Idempotent (UPSERT je kunden_nr). CLI:
    python -m scripts.enrich_milchvieh_profil            # Dry-Run (zählt nur)
    python -m scripts.enrich_milchvieh_profil --apply
"""

from __future__ import annotations

import random
import re
import sys

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.gap_pipeline import normalize_name

_HERD_RE = re.compile(r"(\d+(?:,\d+)?)\s*-\s*(\d+(?:,\d+)?)")


def parse_herd_size(group: str | None) -> int | None:
    """Klassen-Mittel aus z. B. ``"100,0 - 149,9 Kühe"`` → 125."""
    if not group:
        return None
    m = _HERD_RE.search(group)
    if m:
        lo = float(m.group(1).replace(",", "."))
        hi = float(m.group(2).replace(",", "."))
        return int(round((lo + hi) / 2))
    nums = re.findall(r"\d+(?:,\d+)?", group)
    if nums:
        return int(round(float(nums[0].replace(",", "."))))
    return None


def synth_zellzahl(kunden_nr: str, herd_kuehe: int | None) -> int:
    """Deterministische, plausible Zellzahl (x1000/ml) je Kunde (DEV-synthetisch).

    Log-normalnah um ~210; größere Herden leicht höher (Melkhygiene-Skalierung).
    Geclamped auf [90, 650]. Reproduzierbar über den kunden_nr-Seed.
    """
    rng = random.Random(f"zz::{kunden_nr}")
    base = rng.gauss(205, 85)
    if herd_kuehe and herd_kuehe >= 200:
        base += 35
    elif herd_kuehe and herd_kuehe >= 120:
        base += 15
    return max(90, min(650, int(round(base / 5) * 5)))


def hygiene_bedarf(zellzahl: int) -> str:
    """Eutergesundheits-/Hygiene-Bedarf aus Zellzahl (Mastitis-Risikoschwellen)."""
    if zellzahl < 150:
        return "niedrig"
    if zellzahl <= 300:
        return "mittel"
    return "hoch"


def enrich(db: Session, apply: bool = False) -> dict:
    dairy: dict[tuple, dict] = {}
    for r in db.execute(
        text(
            "SELECT name_norm, postal_code, ref_year, herd_size_group, milch_kg, "
            "fett_pct, fett_kg, eiw_pct, eiw_kg, fett_eiweiss_kg, alter_monate "
            "FROM dairy_herd_performance"
        )
    ).mappings().all():
        dairy.setdefault((r["name_norm"], r["postal_code"]), r)

    kunden = db.execute(
        text("SELECT kunden_nr, name1, plz FROM public.kunden WHERE kunden_nr LIKE 'GAP%' OR kunden_nr LIKE 'MV%'")
    ).all()

    matched = []
    for kn, name1, plz in kunden:
        d = dairy.get((normalize_name(name1), plz))
        if d:
            matched.append((kn, d))

    gap_n = sum(1 for kn, _ in matched if kn.startswith("GAP"))
    mv_n = sum(1 for kn, _ in matched if kn.startswith("MV"))
    result = {
        "kunden_betrachtet": len(kunden),
        "milchvieh_match": len(matched),
        "davon_GAP": gap_n,
        "davon_MV": mv_n,
        "applied": apply,
    }
    if not apply:
        result["hinweis_zellzahl"] = "dev_synthetik (LKV-Extraktion erfasst Zellzahl nicht)"
        return result

    upsert = text(
        """
        INSERT INTO public.kunden_milchvieh_profil
            (kunden_nr, ref_year, herd_size_group, herd_size_kuehe, milch_kg,
             fett_pct, fett_kg, eiw_pct, eiw_kg, fett_eiweiss_kg, erstkalbealter_monate,
             zellzahl_tsd_ml, zellzahl_quelle, hygiene_bedarf, quelle)
        VALUES
            (:kn, :ry, :hg, :hk, :milch, :fp, :fk, :ep, :ek, :fek, :alter,
             :zz, 'dev_synthetik', :hb, 'gap+lkv')
        ON CONFLICT (kunden_nr) DO UPDATE SET
            ref_year=EXCLUDED.ref_year, herd_size_group=EXCLUDED.herd_size_group,
            herd_size_kuehe=EXCLUDED.herd_size_kuehe, milch_kg=EXCLUDED.milch_kg,
            fett_pct=EXCLUDED.fett_pct, fett_kg=EXCLUDED.fett_kg,
            eiw_pct=EXCLUDED.eiw_pct, eiw_kg=EXCLUDED.eiw_kg,
            fett_eiweiss_kg=EXCLUDED.fett_eiweiss_kg,
            erstkalbealter_monate=EXCLUDED.erstkalbealter_monate,
            zellzahl_tsd_ml=EXCLUDED.zellzahl_tsd_ml, zellzahl_quelle=EXCLUDED.zellzahl_quelle,
            hygiene_bedarf=EXCLUDED.hygiene_bedarf, updated_at=now()
        """
    )
    hist = {"niedrig": 0, "mittel": 0, "hoch": 0}
    for kn, d in matched:
        hk = parse_herd_size(d["herd_size_group"])
        zz = synth_zellzahl(kn, hk)
        hb = hygiene_bedarf(zz)
        hist[hb] += 1
        db.execute(upsert, {
            "kn": kn, "ry": d["ref_year"], "hg": d["herd_size_group"], "hk": hk,
            "milch": d["milch_kg"], "fp": d["fett_pct"], "fk": d["fett_kg"],
            "ep": d["eiw_pct"], "ek": d["eiw_kg"], "fek": d["fett_eiweiss_kg"],
            "alter": d["alter_monate"], "zz": zz, "hb": hb,
        })
    db.commit()
    result["hygiene_bedarf_verteilung"] = hist
    result["profile_gesamt"] = db.execute(
        text("SELECT count(*) FROM public.kunden_milchvieh_profil")
    ).scalar()
    return result


def main() -> None:
    from app.core.database import SessionLocal

    apply = "--apply" in sys.argv
    db = SessionLocal()
    try:
        res = enrich(db, apply=apply)
        mode = "APPLY" if apply else "DRY-RUN"
        print(f"# Milchvieh-Profil-Anreicherung ({mode})")
        for k, v in res.items():
            print(f"- {k:26} {v}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
