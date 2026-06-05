"""Repariert + reichert die Betriebs-CSVs für Google My Maps an.

Probleme der Quell-CSVs:
- Adresse-Spalte teils leer, Straße in die PLZ-Spalte gerutscht → My Maps kann
  nicht geokodieren (die „ersten N fehlerhaften Zeilen").
- Tausender-Kommas in den €-Spalten („13,615.27 €") zerbrechen das Spaltenraster.

Fix: robustes Realign (PLZ = erster 5-stelliger Token; Adresse = Felder davor) →
saubere Spalten Name/Ortsteil/Adresse/PLZ/Ort. Dazu Anreicherung je Betrieb aus
der DB (Match über Tokenset(Name)+PLZ): GAP-Fläche/-Direktzahlung, Milchvieh-
Kennzahlen, Kunde-Flag, Cross-Sell-Potenzial, Käufergruppe.

Ausgabe je Datei: <stem>_angereichert.csv (My-Maps-ready, UTF-8-BOM, sauber
gequotet) + <stem>_recherche.csv (nicht rekonstruierbare Zeilen → manuelle
Adressrecherche). Reine Adress-/Read-Logik; keine DB-Mutation.

Aufruf: docker exec -e PYTHONPATH=/app valeo-neuro-erp-backend \
          python scripts/enrich_betriebe_csv.py /app/geo_export /app/*Landwirte*PLZ*.csv
"""

from __future__ import annotations

import csv
import glob
import os
import re
import sys

from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.gap_pipeline import normalize_name, tokenset

_PLZ = re.compile(r"^\d{5}$")

# WICHTIG: In Google My Maps als Standort-Spalte AUSSCHLIESSLICH "Volladresse"
# wählen (eine saubere "Straße, PLZ Ort"-Zeile) und als Titel "Name". Sonst baut
# My Maps die Adresse aus mehreren Spalten (inkl. Name/Zahlen) zusammen → Geocoder
# scheitert → fehlende POIs.
OUT_HEADER = [
    "Name", "Volladresse",
    "Ortsteil", "Adresse", "PLZ", "Ort",
    "Flaeche_ha", "GAP_Direktzahlung_EUR",
    "Milchvieh", "Milch_kg_Kuh", "FettEiweiss_kg", "Herdengruppe", "Zellzahl_tsd_ml", "Hygiene_Bedarf",
    "Kunde", "Kundennr", "CrossSell_Potenzial_EUR_Jahr", "Kraftfutter_t_Jahr", "Kaeufergruppe",
]


def _volladresse(rec: dict) -> str:
    """Eine saubere, geokodierbare Adresszeile: 'Straße, PLZ Ort' (ohne Name/Zahlen).
    Ortsteil nur, wenn keine Straße vorhanden (zur groben Verortung)."""
    strasse = rec["adresse"] or rec["ortsteil"]
    ort = f"{rec['plz']} {rec['ort']}".strip()
    return ", ".join(p for p in [strasse, ort, "Deutschland"] if p)


def _read_rows(path: str) -> list[list[str]]:
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, encoding=enc, newline="") as fh:
                return list(csv.reader(fh))
        except UnicodeDecodeError:
            continue
    with open(path, encoding="utf-8", errors="replace", newline="") as fh:
        return list(csv.reader(fh))


def _realign(row: list[str]) -> dict | None:
    plz_idx = next((i for i, v in enumerate(row) if _PLZ.match((v or "").strip())), None)
    if plz_idx is None or plz_idx < 2 or not (row[0] or "").strip():
        return None
    adr = ", ".join(p.strip() for p in row[2:plz_idx] if p and p.strip())
    return {
        "name": row[0].strip(),
        "ortsteil": (row[1].strip() if len(row) > 1 else ""),
        "adresse": adr,
        "plz": row[plz_idx].strip(),
        "ort": (row[plz_idx + 1].strip() if plz_idx + 1 < len(row) else ""),
    }


def _load_lookups(db) -> dict:
    # Direktzahlung ist eine Jahresgröße → nur jüngstes Jahr, je Begünstigtem summieren
    # (der View hat je Stadt eine Zeile). Über Jahre zu summieren würde verdoppeln.
    from app.services.gap_pipeline import latest_gap_year
    gap_year = latest_gap_year(db)
    gap: dict[tuple, float] = {}
    for nn, plz, direct in db.execute(text(
        "SELECT beneficiary_name_norm, postal_code, direct_total_eur FROM gap_payments_direct_agg "
        "WHERE direct_total_eur > 0 AND (:y IS NULL OR ref_year = :y)"), {"y": gap_year}).all():
        gap[(tokenset(nn), plz)] = gap.get((tokenset(nn), plz), 0.0) + float(direct or 0)

    dairy: dict[tuple, dict] = {}
    for nn, plz, milch, fe, grp in db.execute(text(
        "SELECT name_norm, postal_code, milch_kg, fett_eiweiss_kg, herd_size_group FROM dairy_herd_performance "
        "WHERE postal_code IS NOT NULL")).all():
        key = (tokenset(nn), plz)
        if key not in dairy or (fe or 0) > (dairy[key]["fe"] or 0):
            dairy[key] = {"milch": milch, "fe": fe, "group": grp}

    kunde: dict[tuple, str] = {}
    for kn, name1, plz in db.execute(text(
        "SELECT kunden_nr, name1, plz FROM public.kunden WHERE coalesce(geloescht,FALSE)=FALSE")).all():
        kunde.setdefault((tokenset(name1 or ""), plz), kn)

    mvp: dict[str, dict] = {}
    for kn, herd, milch, zz, hyg in db.execute(text(
        "SELECT kunden_nr, herd_size_kuehe, milch_kg, zellzahl_tsd_ml, hygiene_bedarf "
        "FROM public.kunden_milchvieh_profil")).all():
        mvp[kn] = {"herd": herd, "milch": milch, "zz": zz, "hyg": hyg}

    kg: dict[str, str] = {}
    for kn, grp in db.execute(text(
        "SELECT kunden_nr, buying_group FROM public.kunden_kaeufer_profil")).all():
        kg[kn] = grp

    # Cross-Sell-Potenzial je Milchvieh-Kunde (einmalig berechnet)
    from app.services.milchvieh_crosssell_service import MilchviehCrossSellService
    pot: dict[str, dict] = {}
    for it in MilchviehCrossSellService(db).list_items():
        pot[it["kunden_nr"]] = {"ziel": it["crosssell_ziel_eur"], "kf": it["kraftfutter_t_jahr_max"]}
    return {"gap": gap, "dairy": dairy, "kunde": kunde, "mvp": mvp, "kg": kg, "pot": pot}


_GRP_LABEL = {
    "preisabfrager_ohne_abschluss": "Preisabfrager", "preisverhandler_mit_abschluss": "Preisverhandler",
    "beziehungskaeufer": "Beziehungskäufer", "leistungskaeufer": "Leistungskäufer",
    "bequemlichkeitskaeufer": "Bequemlichkeitskäufer", "risiko_streuer": "Risiko-Streuer",
    "opportunist": "Opportunist", "saison_ergaenzer": "Saisonkäufer",
    "strategischer_stammkunde": "Stammkunde", "schlafender_potenzialkunde": "Schlafender Potenzialkunde",
    "unbekannt": "",
}


def _enrich_row(rec: dict, lk: dict) -> list:
    key = (tokenset(rec["name"]), rec["plz"])
    direct = lk["gap"].get(key, 0.0)
    flaeche = round(direct / 270.0, 1) if direct else ""
    d = lk["dairy"].get(key)
    kn = lk["kunde"].get(key)
    mvp = lk["mvp"].get(kn) if kn else None
    pot = lk["pot"].get(kn) if kn else None
    return [
        rec["name"], _volladresse(rec),
        rec["ortsteil"], rec["adresse"], rec["plz"], rec["ort"],
        flaeche, round(direct) if direct else "",
        "Ja" if d else "Nein",
        round(d["milch"]) if d and d["milch"] else "",
        round(d["fe"]) if d and d["fe"] else "",
        (d["group"] if d else ""),
        (mvp["zz"] if mvp and mvp.get("zz") else ""),
        (mvp["hyg"] if mvp and mvp.get("hyg") else ""),
        "Ja" if kn else "Nein", (kn or ""),
        (pot["ziel"] if pot else ""), (pot["kf"] if pot else ""),
        _GRP_LABEL.get(lk["kg"].get(kn or "", ""), ""),
    ]


def main() -> None:
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "/app/geo_export"
    os.makedirs(out_dir, exist_ok=True)
    patterns = sys.argv[2:] or ["/app/*Landwirte*PLZ*.csv"]
    files: list[str] = []
    for p in patterns:
        files.extend(sorted(glob.glob(p)))
    db = SessionLocal()
    try:
        lk = _load_lookups(db)
        for f in files:
            rows = _read_rows(f)
            stem = os.path.splitext(os.path.basename(f))[0]
            ok_path = os.path.join(out_dir, f"{stem}_angereichert.csv")
            rech_path = os.path.join(out_dir, f"{stem}_recherche.csv")
            n_ok = n_rech = 0
            with open(ok_path, "w", encoding="utf-8-sig", newline="") as oh, \
                 open(rech_path, "w", encoding="utf-8-sig", newline="") as rh:
                ow = csv.writer(oh); rw = csv.writer(rh)
                ow.writerow(OUT_HEADER); rw.writerow(["Name", "Roh-Zeile (Adresse recherchieren)"])
                for row in rows[1:]:
                    rec = _realign(row)
                    if rec is None or not rec["adresse"]:
                        rw.writerow([(row[0].strip() if row else ""), " | ".join(row)])
                        n_rech += 1
                        continue
                    ow.writerow(_enrich_row(rec, lk))
                    n_ok += 1
            print(f"{stem}: {n_ok} angereichert, {n_rech} → Recherche")
    finally:
        db.close()


if __name__ == "__main__":
    main()
