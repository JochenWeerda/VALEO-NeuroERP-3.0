#!/usr/bin/env python3
"""L3-Testdatenabzug lokal einlesen (M6 fruehe Testphase) - Runbook docs/migration/m6-l3-testdatenabzug.md.

    python scripts/l3_testdaten_import.py C:/VALEO-Testdaten/l3 --mandant l3-test
    python scripts/l3_testdaten_import.py --loeschen --mandant l3-test

DSGVO: Die Dateien bleiben auf diesem Rechner. Das Skript prueft jede Datei auf Klartext (E-Mail, Telefon, IBAN,
Strasse) und liest bei einem Fund nichts ein. Ausgegeben werden nur Zaehlwerte und Fehlerarten, nie Feldinhalte - die
Ausgabe darf deshalb auch in einem Agenten-Kontext erscheinen, die Dateien selbst nicht.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

#: L3-Spalte -> kanonisches Feld (Profil l3_spiegel). Gleiche Zuordnung wie in den Spiegeltests.
MAPPING = {
    "TYP": "record_type", "QUELLE": "source_ref",
    "ARTNR": "artikelnummer", "BEZEICHN1": "bezeichnung", "BEZEICHN2": "bezeichnung2", "ARTIKELGRP": "artikelgruppe",
    "ME1": "mengeneinheit_nr", "GESPERRT": "gesperrt",
    "KUNDENNR": "kundennummer", "KUNDNAME": "name", "PLZ": "plz", "STAAT": "land", "DEBITORKTO": "debitorkonto",
    "SPERRE": "gesperrt", "LIEFERANTENNR": "lieferantennummer", "KREDITORKTO": "kreditorkonto",
    "LAGER": "lager", "BESTAND": "menge",
    "KONTONR": "konto", "RECHNNR": "rechnungsnr", "OFFENBETRAG": "offener_betrag",
}
REIHENFOLGE = ("artikel", "kunde", "lieferant", "bestand", "offener_posten")
#: Schluesselspalten werden nicht auf Klartext geprueft (Nummern, keine Personendaten).
SCHLUESSEL = {"TYP", "QUELLE", "ARTNR", "ARTIKELGRP", "ME1", "KUNDENNR", "DEBITORKTO", "LIEFERANTENNR", "KREDITORKTO", "LAGER", "KONTONR", "RECHNNR",
              "BESTAND", "OFFENBETRAG", "RECHNBETRAG", "OFFEN", "MAHNSTUFE", "PLZ", "GESPERRT", "SPERRE", "STAAT", "KZSH",
              "RECHNDATUM"}
KLARTEXT = {
    "E-Mail": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "Telefon": re.compile(r"(?:\+49|\b0)\d{2,5}[ /-]?\d{4,}"),
    "IBAN": re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[0-9A-Z]{4}){3,7}\b"),
    "Strasse": re.compile(r"(?i)\b\w*(stra(ss|ß)e|str\.|weg|allee|platz|gasse)\s+\d"),
}


def klartext_funde(zeilen: list[dict[str, str]]) -> Counter:
    funde: Counter = Counter()
    for zeile in zeilen:
        for spalte, wert in zeile.items():
            if spalte and spalte.upper() in SCHLUESSEL or not wert:
                continue
            for art, muster in KLARTEXT.items():
                if muster.search(str(wert)):
                    funde[art] += 1
    return funde


def lies(datei: Path) -> list[dict[str, str]]:
    with datei.open(encoding="utf-8-sig", newline="") as f:
        probe = f.read(4096)
        f.seek(0)
        trenner = ";" if probe.count(";") >= probe.count(",") else ","
        return [{(k or "").strip().upper(): (v or "").strip() for k, v in z.items()}
                for z in csv.DictReader(f, delimiter=trenner)]


def fehlerart(text_: str | None) -> str:
    """Fehlermeldung ohne Werte: Ziffern und Zitate entfernt."""
    ohne = re.sub(r"'[^']*'|\"[^\"]*\"|\d[\d.,/@-]*", "#", text_ or "")
    return ohne.split(" - ")[0][:80]


def mandant_anlegen(db, mandant: str) -> None:
    from sqlalchemy import text

    db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, 'L3-Testdaten', true) "
                    "ON CONFLICT (id) DO NOTHING"), {"id": mandant})
    db.commit()
    # Grundeinheiten wie in jedem neuen Mandanten. Lager und Warengruppen werden NICHT erfunden: sie werden im
    # Testmandanten ueber die Studio-Masken gepflegt; bis dahin erscheinen fehlende als Fehlerart.
    from app.services.mengeneinheiten_grund import richte_grundeinheiten_ein

    richte_grundeinheiten_ein(db, mandant)
    db.commit()


def einlesen(ordner: Path, mandant: str) -> int:
    from app.core.database import SessionLocal
    from app.services.legacy_interface_adapter_service import LegacyInterfaceAdapterService
    from app.services.spiegel_uebernahme import differenzbericht, uebernehme

    dateien = sorted(ordner.glob("l3_abzug_*.csv"))
    if not dateien:
        print(f"Keine Dateien l3_abzug_*.csv in {ordner}.")
        return 1
    geladen: dict[str, list[tuple[Path, list[dict[str, str]]]]] = {}
    for datei in dateien:
        zeilen = lies(datei)
        funde = klartext_funde(zeilen)
        if funde:
            print(f"ABBRUCH {datei.name}: erkennbarer Klartext ({', '.join(f'{a} {n}x' for a, n in funde.items())}). "
                  "Nichts eingelesen - Datei loeschen und pseudonymisiert neu ziehen.")
            return 2
        arten = {z.get("TYP", "") for z in zeilen}
        if len(arten) != 1 or not arten <= set(REIHENFOLGE):
            print(f"ABBRUCH {datei.name}: Spalte TYP fehlt oder ist nicht eindeutig (erwartet eine von {REIHENFOLGE}).")
            return 2
        geladen.setdefault(arten.pop(), []).append((datei, zeilen))

    with SessionLocal() as db:
        mandant_anlegen(db, mandant)
        LegacyInterfaceAdapterService(db, mandant).configure(
            "l3_spiegel", {"format_contract": {"encoding": "utf-8", "record_types": list(REIHENFOLGE),
                                               "sample_hash": "l3-testdaten", "export_stand": "Testabzug"},
                           "field_mapping": MAPPING}, actor="l3_testdaten_import", reason="M6 Testdaten")
    for art in REIHENFOLGE:
        for datei, zeilen in geladen.get(art, []):
            inhalt = hashlib.sha256(datei.read_bytes()).hexdigest()[:16]
            with SessionLocal() as db:
                dienst = LegacyInterfaceAdapterService(db, mandant)
                batch = dienst.intake("l3_spiegel", f"{datei.name}:{inhalt}", {"records": zeilen},
                                      actor="l3_testdaten_import")["id"]
                for schritt in (dienst.stage, dienst.reconcile, dienst.approve):
                    try:
                        schritt(batch, actor="l3_testdaten_import", reason="M6 Testdaten")
                    except Exception as fehler:  # Zustand (bereits freigegeben, Quarantaene) wird unten gemeldet
                        print(f"  {datei.name}: {schritt.__name__} nicht moeglich ({fehlerart(str(fehler))})")
                        break
            with SessionLocal() as db:
                if art == "offener_posten":
                    try:
                        from app.services.spiegel_op_abgleich import abgleichen
                    except ImportError:
                        print(f"  {datei.name}: OP-Abgleich in diesem Stand nicht vorhanden - Batch nur angenommen.")
                        continue
                    ergebnis = abgleichen(db, mandant, batch, actor="l3_testdaten_import", reason="M6 Testdaten")
                    print(f"{art:15s} {datei.name}: gleich {ergebnis['unveraendert']}, abweichend {ergebnis['geaendert']}, "
                          f"fehler {ergebnis['fehler']}, fehlt in L3 {len(ergebnis['fehlt_in_l3'])}")
                    continue
                ergebnis = uebernehme(db, mandant, batch, actor="l3_testdaten_import", reason="M6 Testdaten")
                bericht = differenzbericht(db, mandant, batch)
            print(f"{art:15s} {datei.name}: neu {ergebnis['neu']}, geaendert {ergebnis['geaendert']}, "
                  f"unveraendert {ergebnis['unveraendert']}, fehler {ergebnis['fehler']}")
            for art_, anzahl in Counter(fehlerart(f["fehler"]) for f in bericht["fehler"]).most_common():
                print(f"    {anzahl:4d}x {art_}")
    return 0


#: Loeschreihenfolge (Fremdschluessel): erst Protokolle und Bewegungen, zuletzt Stammdaten und Mandant.
LOESCHEN = (
    "domain_integration.spiegel_protokoll", "domain_integration.spiegel_quellreferenzen",
    "domain_inventory.bestandsbuchung_schluessel", "domain_inventory.inventory_stock_movements",
    "domain_erp.offene_posten", "domain_crm.customers", "domain_einkauf.lieferanten", "domain_crm.business_partners",
    "domain_inventory.articles", "domain_inventory.warehouses",
    "domain_integration.legacy_adapter_staging", "domain_integration.legacy_adapter_audit",
    "domain_integration.legacy_adapter_batches", "domain_integration.legacy_adapter_profiles",
    "domain_shared.artikel_mengeneinheiten", "domain_shared.warengruppen", "domain_shared.oberwarengruppen",
    "domain_shared.hauptwarengruppen",
)


def loeschen(mandant: str) -> int:
    from sqlalchemy import text

    from app.core.database import SessionLocal

    if not mandant.startswith("l3-test"):
        print("ABBRUCH: Loeschen nur fuer Testmandanten (Praefix l3-test).")
        return 2
    with SessionLocal() as db:
        for tabelle in LOESCHEN:
            anzahl = db.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = :t"), {"t": mandant}).rowcount  # nosec B608 - Tabellen aus Konstante
            print(f"  {tabelle}: {anzahl} geloescht")
        db.execute(text("DELETE FROM domain_shared.tenants WHERE id = :t"), {"t": mandant})
        db.commit()
    print(f"Loeschprotokoll: Testmandant {mandant} geleert. CSV-Dateien bitte von Hand loeschen.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ordner", nargs="?", type=Path)
    parser.add_argument("--mandant", default="l3-test")
    parser.add_argument("--loeschen", action="store_true")
    args = parser.parse_args()
    if args.loeschen:
        return loeschen(args.mandant)
    if not args.ordner or not args.ordner.is_dir():
        parser.error("Ordner mit l3_abzug_*.csv angeben")
    return einlesen(args.ordner, args.mandant)


if __name__ == "__main__":
    raise SystemExit(main())
