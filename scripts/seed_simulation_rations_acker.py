#!/usr/bin/env python3
"""
Praxisnaher Simulations-Seed fuer Rationsoptimierung + Ackerschlagkartei.

Zwei Betriebsprofile eines norddeutschen Gemischtbetriebs (Milchvieh + Ackerbau):

  A) Milchviehfuetterung — Grundfutter-Analyseergebnisse (LKV-Laborwerte) und
     Kraftfutter-Rezepturen. Als JSON-Datenset exportiert (Import ins Rationstool
     bzw. als Referenz fuer Optimierungslaeufe).

  B) Ackerschlagkartei — 4 reale Schlaege mit Nmin, Bodenuntersuchung, Duengung
     (organisch Guelle + mineralisch KAS), Pflanzenschutz und Ernte. Wird ueber die
     echte Portal-API angelegt (rechnet Reinnaehrstoffe/DueV-Bilanz serverseitig).

Aufruf (Backend muss laufen):
    python scripts/seed_simulation_rations_acker.py \
        --base http://127.0.0.1:8000 --token dev-token \
        --tenant 00000000-0000-0000-0000-000000000001

Idempotent: vorhandene Schlaege (per Name) werden nicht doppelt angelegt.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("Bitte 'requests' installieren (pip install requests).", file=sys.stderr)
    raise


# ── A) Milchvieh: Grundfutter-Analysen + Kraftfutter-Rezepturen ───────────────
# Werte in g/kg TM (bzw. NEL MJ/kg TM), typische LKV-Laboranalytik Norddeutschland.
GRUNDFUTTER_ANALYSEN = [
    {
        "id": "gs1-2026", "name": "Grassilage 1. Schnitt (2026)", "futterart": "Grassilage",
        "konservierung": "Silage", "forage": True, "dm_frac": 0.35,
        "cp_g_kgdm": 165, "me_mj_kgdm": 10.6, "nel_mj_kgdm": 6.4, "ndf_g_kgdm": 420,
        "adf_g_kgdm": 270, "xf_g_kgdm": 235, "sugar_g_kgdm": 60, "xa_g_kgdm": 95,
        "ca_g_kgdm": 6.5, "p_g_kgdm": 3.4, "labor": "LKV Weser-Ems", "probe_datum": "2026-05-28",
    },
    {
        "id": "gs2-2026", "name": "Grassilage 2. Schnitt (2026)", "futterart": "Grassilage",
        "konservierung": "Silage", "forage": True, "dm_frac": 0.38,
        "cp_g_kgdm": 150, "me_mj_kgdm": 10.1, "nel_mj_kgdm": 6.1, "ndf_g_kgdm": 460,
        "adf_g_kgdm": 290, "xf_g_kgdm": 255, "sugar_g_kgdm": 45, "xa_g_kgdm": 100,
        "ca_g_kgdm": 7.2, "p_g_kgdm": 3.1, "labor": "LKV Weser-Ems", "probe_datum": "2026-07-02",
    },
    {
        "id": "ms-2025", "name": "Maissilage (Ernte 2025)", "futterart": "Maissilage",
        "konservierung": "Silage", "forage": True, "dm_frac": 0.335,
        "cp_g_kgdm": 78, "me_mj_kgdm": 11.0, "nel_mj_kgdm": 6.6, "ndf_g_kgdm": 380,
        "adf_g_kgdm": 210, "starch_g_kgdm": 330, "sugar_g_kgdm": 15, "xa_g_kgdm": 38,
        "ca_g_kgdm": 2.2, "p_g_kgdm": 2.3, "labor": "LKV Weser-Ems", "probe_datum": "2025-11-15",
    },
    {
        "id": "heu-2026", "name": "Wiesenheu (belueftet)", "futterart": "Heu",
        "konservierung": "Trocken", "forage": True, "dm_frac": 0.86,
        "cp_g_kgdm": 112, "me_mj_kgdm": 8.6, "nel_mj_kgdm": 5.1, "ndf_g_kgdm": 560,
        "adf_g_kgdm": 340, "xf_g_kgdm": 300, "sugar_g_kgdm": 90, "xa_g_kgdm": 78,
        "ca_g_kgdm": 5.5, "p_g_kgdm": 2.6, "labor": "LKV Weser-Ems", "probe_datum": "2026-06-20",
    },
]

# Kraftfutter-Rezepturen (Mischungen). Zusammensetzung als Anteil (Summe = 1.0).
KRAFTFUTTER_REZEPTUREN = [
    {
        "id": "mlf-183", "name": "Milchleistungsfutter 18/3", "futterart": "Kraftfutter",
        "forage": False, "dm_frac": 0.88, "cp_g_kgdm": 205, "me_mj_kgdm": 12.4,
        "nel_mj_kgdm": 7.5, "ndf_g_kgdm": 180, "starch_g_kgdm": 250, "sugar_g_kgdm": 70,
        "ca_g_kgdm": 9.0, "p_g_kgdm": 5.5, "price_eur_kgdm": 0.34,
        "rezeptur": [
            {"komponente": "Weizen", "anteil": 0.30},
            {"komponente": "Gerste", "anteil": 0.20},
            {"komponente": "Sojaextraktionsschrot", "anteil": 0.22},
            {"komponente": "Rapsextraktionsschrot", "anteil": 0.18},
            {"komponente": "Zuckerrübenschnitzel", "anteil": 0.07},
            {"komponente": "Mineralfutter 8-12-20", "anteil": 0.03},
        ],
    },
    {
        "id": "energie-konz", "name": "Energiekonzentrat (Getreide)", "futterart": "Kraftfutter",
        "forage": False, "dm_frac": 0.87, "cp_g_kgdm": 125, "me_mj_kgdm": 13.1,
        "nel_mj_kgdm": 8.1, "ndf_g_kgdm": 130, "starch_g_kgdm": 520, "sugar_g_kgdm": 30,
        "ca_g_kgdm": 0.8, "p_g_kgdm": 3.6, "price_eur_kgdm": 0.28,
        "rezeptur": [
            {"komponente": "Weizen", "anteil": 0.45},
            {"komponente": "Körnermais", "anteil": 0.35},
            {"komponente": "Gerste", "anteil": 0.20},
        ],
    },
    {
        "id": "eiweiss-konz", "name": "Eiweißkonzentrat (Raps/Soja)", "futterart": "Kraftfutter",
        "forage": False, "dm_frac": 0.89, "cp_g_kgdm": 380, "me_mj_kgdm": 11.6,
        "nel_mj_kgdm": 7.0, "ndf_g_kgdm": 240, "starch_g_kgdm": 40, "sugar_g_kgdm": 90,
        "ca_g_kgdm": 7.5, "p_g_kgdm": 10.5, "price_eur_kgdm": 0.42,
        "rezeptur": [
            {"komponente": "Rapsextraktionsschrot", "anteil": 0.55},
            {"komponente": "Sojaextraktionsschrot", "anteil": 0.45},
        ],
    },
    {
        "id": "mineral-transit", "name": "Mineralfutter Transitkuh (DCAB-arm)", "futterart": "Mineralfutter",
        "forage": False, "dm_frac": 0.97, "cp_g_kgdm": 0, "me_mj_kgdm": 0, "nel_mj_kgdm": 0,
        "ca_g_kgdm": 120, "p_g_kgdm": 60, "mg_g_kgdm": 80, "na_g_kgdm": 10, "price_eur_kgdm": 1.55,
        "hinweis": "Anionische Salze zur Milchfieberprophylaxe (DCAB negativ), Trockensteher.",
    },
]

# Fuetterungsgruppen (praxisnahe Leistungsklassen)
FUETTERUNGSGRUPPEN = [
    {"id": "hl-frisch", "name": "Frischmelker / Hochleistung", "milch_kg": 42, "fett_pct": 4.0, "eiweiss_pct": 3.4, "laktationstag": 60, "gewicht_kg": 650},
    {"id": "ml-mitte", "name": "Mittlere Laktation", "milch_kg": 32, "fett_pct": 4.1, "eiweiss_pct": 3.5, "laktationstag": 150, "gewicht_kg": 680},
    {"id": "trockensteher", "name": "Trockensteher (Transit)", "milch_kg": 0, "fett_pct": 0, "eiweiss_pct": 0, "laktationstag": -21, "gewicht_kg": 720},
]


# ── B) Ackerschlagkartei: Schlaege + Massnahmen ───────────────────────────────
def _iso(y: int, m: int, d: int) -> str:
    return datetime(y, m, d, 8, 0, tzinfo=timezone.utc).isoformat()


SCHLAEGE = [
    {
        "schlag": {
            "name": "Am Bach", "flik": "DENILI0512340001", "flaeche": 12.5, "kultur": "Winterweizen",
            "vorkultur": "Winterraps", "gemeinde": "Ostgroßefehn", "gemarkung": "Flur 3",
            "bodenart": "sandiger Lehm", "ackerzahl": 62, "status": "aktiv",
            "n_sollwert_kg_ha": 230, "ertragsniveau_dt_ha": 85, "nmin_fruehjahr_kg_ha": 45,
            "nmin_in_bedarf": True, "boden_p2o5_mg": 12, "boden_k2o_mg": 15, "boden_mgo_mg": 8,
            "boden_ph": 6.6, "boden_datum": _iso(2026, 2, 20), "versorgungsstufe": "C",
        },
        "massnahmen": [
            {"datum": _iso(2026, 3, 5), "typ": "duengung", "bezeichnung": "Rindergülle Andüngung", "mittel": "Rindergülle",
             "menge": 25000, "einheit": "kg/ha", "flaeche": 12.5, "duenger_form": "O",
             "n_gehalt": 0.35, "p2o5_gehalt": 0.15, "k2o_gehalt": 0.45, "preis_je_einheit": 0.004, "anwender": "J. Weerda"},
            {"datum": _iso(2026, 3, 25), "typ": "duengung", "bezeichnung": "KAS Schossergabe", "mittel": "KAS 27",
             "menge": 350, "einheit": "kg/ha", "flaeche": 12.5, "duenger_form": "M",
             "n_gehalt": 27, "s_gehalt": 0, "preis_je_einheit": 0.42, "anwender": "J. Weerda"},
            {"datum": _iso(2026, 4, 15), "typ": "psm", "bezeichnung": "Herbizid Nachauflauf", "mittel": "Broadway",
             "menge": 0.13, "einheit": "kg/ha", "flaeche": 12.5, "wirkungsbereich": "Herbizid",
             "begruendung": "Ackerfuchsschwanz + Klettenlabkraut über Schadschwelle", "anwender": "J. Weerda",
             "kosten_eur": 512.0},
            {"datum": _iso(2026, 5, 20), "typ": "psm", "bezeichnung": "Fungizid Blattetage", "mittel": "Ascra Xpro",
             "menge": 1.2, "einheit": "l/ha", "flaeche": 12.5, "wirkungsbereich": "Fungizid",
             "begruendung": "Septoria-Befall auf F-3, feuchte Witterung", "anwender": "J. Weerda", "kosten_eur": 615.0},
            {"datum": _iso(2026, 8, 5), "typ": "ernte", "bezeichnung": "Drusch Winterweizen", "mittel": "",
             "flaeche": 12.5, "ertrag_dt_ha": 88, "qualitaet": "A-Weizen, 13,2% RP", "erloes_eur": 23100.0,
             "nebenleistung_eur": 1250.0, "anwender": "Lohnunternehmer Janssen"},
        ],
    },
    {
        "schlag": {
            "name": "Hinterm Hof", "flik": "DENILI0512340002", "flaeche": 8.0, "kultur": "Wintergerste",
            "vorkultur": "Winterweizen", "gemeinde": "Ostgroßefehn", "gemarkung": "Flur 3",
            "bodenart": "sandiger Lehm", "ackerzahl": 55, "status": "aktiv",
            "n_sollwert_kg_ha": 180, "ertragsniveau_dt_ha": 78, "nmin_fruehjahr_kg_ha": 38,
            "nmin_in_bedarf": True, "boden_p2o5_mg": 9, "boden_k2o_mg": 11, "boden_mgo_mg": 6,
            "boden_ph": 6.3, "boden_datum": _iso(2026, 2, 20), "versorgungsstufe": "B",
        },
        "massnahmen": [
            {"datum": _iso(2026, 3, 8), "typ": "duengung", "bezeichnung": "KAS Andüngung", "mittel": "KAS 27",
             "menge": 300, "einheit": "kg/ha", "flaeche": 8.0, "duenger_form": "M",
             "n_gehalt": 27, "preis_je_einheit": 0.42, "anwender": "J. Weerda"},
            {"datum": _iso(2026, 4, 20), "typ": "psm", "bezeichnung": "Fungizid + Wachstumsregler", "mittel": "Prosaro + CCC",
             "menge": 1.0, "einheit": "l/ha", "flaeche": 8.0, "wirkungsbereich": "Fungizid",
             "begruendung": "Netzflecken + Standfestigkeit", "anwender": "J. Weerda", "kosten_eur": 288.0},
            {"datum": _iso(2026, 7, 12), "typ": "ernte", "bezeichnung": "Drusch Wintergerste", "mittel": "",
             "flaeche": 8.0, "ertrag_dt_ha": 76, "qualitaet": "Futtergerste 64 kg/hl", "erloes_eur": 10336.0,
             "nebenleistung_eur": 640.0, "anwender": "Lohnunternehmer Janssen"},
        ],
    },
    {
        "schlag": {
            "name": "Große Wiese", "flik": "DENILI0512340003", "flaeche": 15.0, "kultur": "Silomais",
            "vorkultur": "Silomais", "gemeinde": "Ostgroßefehn", "gemarkung": "Flur 5",
            "bodenart": "Sand", "ackerzahl": 42, "status": "aktiv",
            "n_sollwert_kg_ha": 200, "ertragsniveau_dt_ha": 480, "nmin_fruehjahr_kg_ha": 30,
            "nmin_in_bedarf": True, "boden_p2o5_mg": 15, "boden_k2o_mg": 18, "boden_mgo_mg": 9,
            "boden_ph": 5.9, "boden_datum": _iso(2026, 3, 2), "versorgungsstufe": "C",
        },
        "massnahmen": [
            {"datum": _iso(2026, 4, 10), "typ": "duengung", "bezeichnung": "Rindergülle vor Saat", "mittel": "Rindergülle",
             "menge": 30000, "einheit": "kg/ha", "flaeche": 15.0, "duenger_form": "O",
             "n_gehalt": 0.35, "p2o5_gehalt": 0.15, "k2o_gehalt": 0.45, "preis_je_einheit": 0.004, "anwender": "J. Weerda"},
            {"datum": _iso(2026, 4, 28), "typ": "duengung", "bezeichnung": "Unterfußdüngung DAP", "mittel": "DAP 18-46",
             "menge": 120, "einheit": "kg/ha", "flaeche": 15.0, "duenger_form": "M",
             "n_gehalt": 18, "p2o5_gehalt": 46, "preis_je_einheit": 0.58, "anwender": "J. Weerda"},
            {"datum": _iso(2026, 5, 15), "typ": "psm", "bezeichnung": "Herbizid Mais Nachauflauf", "mittel": "Elumis + Aspect",
             "menge": 1.5, "einheit": "l/ha", "flaeche": 15.0, "wirkungsbereich": "Herbizid",
             "begruendung": "Hirse + Gänsefuß im 4-Blatt-Stadium", "anwender": "J. Weerda", "kosten_eur": 675.0},
            {"datum": _iso(2026, 10, 2), "typ": "ernte", "bezeichnung": "Häckseln Silomais", "mittel": "",
             "flaeche": 15.0, "ertrag_dt_ha": 495, "qualitaet": "33% TM, 32% Stärke", "erloes_eur": 0.0,
             "nebenleistung_eur": 0.0, "anwender": "Lohnunternehmer Buss", "bemerkung": "innerbetrieblich verfüttert"},
        ],
    },
    {
        "schlag": {
            "name": "Sandkamp", "flik": "DENILI0512340004", "flaeche": 6.3, "kultur": "Zuckerrübe",
            "vorkultur": "Wintergerste", "gemeinde": "Ostgroßefehn", "gemarkung": "Flur 5",
            "bodenart": "sandiger Lehm", "ackerzahl": 58, "status": "aktiv",
            "n_sollwert_kg_ha": 170, "ertragsniveau_dt_ha": 650, "nmin_fruehjahr_kg_ha": 25,
            "nmin_in_bedarf": True, "boden_p2o5_mg": 14, "boden_k2o_mg": 16, "boden_mgo_mg": 10,
            "boden_ph": 6.9, "boden_datum": _iso(2026, 3, 2), "versorgungsstufe": "C",
        },
        "massnahmen": [
            {"datum": _iso(2026, 3, 30), "typ": "duengung", "bezeichnung": "KAS + Bittersalz", "mittel": "KAS 27",
             "menge": 400, "einheit": "kg/ha", "flaeche": 6.3, "duenger_form": "M",
             "n_gehalt": 27, "preis_je_einheit": 0.42, "anwender": "J. Weerda"},
            {"datum": _iso(2026, 5, 5), "typ": "psm", "bezeichnung": "Herbizid NAK 1", "mittel": "Betanal maxxPro",
             "menge": 1.25, "einheit": "l/ha", "flaeche": 6.3, "wirkungsbereich": "Herbizid",
             "begruendung": "Unkrautkeimung Keimblattstadium", "anwender": "J. Weerda", "kosten_eur": 315.0},
            {"datum": _iso(2026, 6, 18), "typ": "psm", "bezeichnung": "Fungizid Cercospora", "mittel": "Spyrale",
             "menge": 1.0, "einheit": "l/ha", "flaeche": 6.3, "wirkungsbereich": "Fungizid",
             "begruendung": "Cercospora-Erstbefall, Warndienst LWK", "anwender": "J. Weerda", "kosten_eur": 189.0},
            {"datum": _iso(2026, 10, 20), "typ": "ernte", "bezeichnung": "Rübenroden", "mittel": "",
             "flaeche": 6.3, "ertrag_dt_ha": 685, "qualitaet": "17,8% Zucker", "erloes_eur": 15477.0,
             "nebenleistung_eur": 0.0, "anwender": "Lohnunternehmer Rübenkontor"},
        ],
    },
]


def seed_feldbuch(base: str, headers: dict[str, str]) -> dict[str, int]:
    fb = f"{base}/api/v1/portal/feldbuch"
    existing = requests.get(f"{fb}/schlaege", headers=headers, timeout=15)
    existing.raise_for_status()
    have = {s.get("name") for s in existing.json()}
    created_schlaege = 0
    created_massn = 0
    for entry in SCHLAEGE:
        name = entry["schlag"]["name"]
        if name in have:
            print(f"  · Schlag '{name}' existiert bereits — übersprungen")
            continue
        r = requests.post(f"{fb}/schlaege", headers=headers, json=entry["schlag"], timeout=20)
        if not r.ok:
            print(f"  ! Schlag '{name}' FEHLER {r.status_code}: {r.text[:200]}")
            continue
        schlag_id = r.json().get("id")
        created_schlaege += 1
        print(f"  ✓ Schlag '{name}' angelegt ({schlag_id})")
        for m in entry["massnahmen"]:
            payload = dict(m, schlag_id=schlag_id)
            rm = requests.post(f"{fb}/massnahmen", headers=headers, json=payload, timeout=20)
            if rm.ok:
                created_massn += 1
            else:
                print(f"    ! Maßnahme '{m.get('bezeichnung')}' FEHLER {rm.status_code}: {rm.text[:160]}")
    return {"schlaege": created_schlaege, "massnahmen": created_massn}


def export_rations_dataset(out_path: str) -> None:
    dataset = {
        "betrieb": "Hof Ostfriesland — Milchvieh (Simulation)",
        "erstellt": datetime.now(timezone.utc).isoformat(),
        "grundfutter_analysen": GRUNDFUTTER_ANALYSEN,
        "kraftfutter_rezepturen": KRAFTFUTTER_REZEPTUREN,
        "fuetterungsgruppen": FUETTERUNGSGRUPPEN,
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(dataset, fh, ensure_ascii=False, indent=2)
    print(f"  ✓ Rations-Datenset geschrieben: {out_path}")
    print(f"    {len(GRUNDFUTTER_ANALYSEN)} Grundfutter-Analysen, "
          f"{len(KRAFTFUTTER_REZEPTUREN)} Kraftfutter-Rezepturen, "
          f"{len(FUETTERUNGSGRUPPEN)} Fütterungsgruppen")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("SEED_BASE", "http://127.0.0.1:8000"))
    ap.add_argument("--token", default=os.environ.get("SEED_TOKEN", "dev-token"))
    ap.add_argument("--tenant", default=os.environ.get("SEED_TENANT", "00000000-0000-0000-0000-000000000001"))
    ap.add_argument("--rations-out", default="data/seed/rations_hof_ostfriesland.json")
    ap.add_argument("--skip-feldbuch", action="store_true")
    args = ap.parse_args()

    headers = {
        "Authorization": f"Bearer {args.token}",
        "X-Tenant-ID": args.tenant,
        "X-Tenant-Id": args.tenant,
        "Content-Type": "application/json",
    }

    print("== A) Rationsoptimierung: Grundfutter-Analysen + Kraftfutter-Rezepturen ==")
    export_rations_dataset(args.rations_out)

    if not args.skip_feldbuch:
        print("== B) Ackerschlagkartei: Schläge + Maßnahmen (über Portal-API) ==")
        try:
            res = seed_feldbuch(args.base, headers)
            print(f"  Ergebnis: {res['schlaege']} Schläge, {res['massnahmen']} Maßnahmen neu angelegt.")
        except requests.RequestException as e:
            print(f"  ! Feldbuch-Seed fehlgeschlagen (Backend erreichbar?): {e}", file=sys.stderr)
            return 1
    print("Seed abgeschlossen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
