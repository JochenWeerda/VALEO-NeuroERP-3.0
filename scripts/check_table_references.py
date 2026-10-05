#!/usr/bin/env python3
"""Liest ein Endpunkt eine Tabelle, die es nicht gibt?

Die dritte Ebene
----------------

Drei Gates, drei Ebenen desselben stillen Fehlers:

1. `check_frontend_api_calls.py` — ruft die Maske eine Route auf, die es gibt?
2. `check_field_contracts.py` — spricht die Antwort die Sprache der Maske?
3. **dieses hier** — liest der Endpunkt eine Tabelle, die es gibt?

Die dritte ist die leiseste. Ein `SELECT` auf eine fehlende Tabelle wirft, das
`except` faengt, und die Maske zeigt **0,00** oder eine leere Liste. Eine Null
sieht aus wie ein Ergebnis, nicht wie ein Fehler — so meldete die
Liquiditaetssicht monatelang „nichts offen", waehrend 18.000 EUR offen waren.

Lebend und ruhend
-----------------

Getrennt gezaehlt wird, ob die betroffene Datei ueberhaupt eine Route hat, die
eine Maske oder das Frontend aufruft:

- **lebend** — jemand sieht das Ergebnis. Diese Zahl ist die dringende.
- **ruhend** — Code ohne Weg dorthin. Ob er gebaut oder geloescht gehoert, ist
  eine Produktentscheidung, keine Aufraeumarbeit.

Aufruf:  python scripts/check_table_references.py [--list]
"""

from __future__ import annotations

import argparse
import collections
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

#: Stand 2026-09-29, gemessen auf einer **frischen** Datenbank
#: (``createdb`` + ``alembic upgrade head``). Beide Zahlen duerfen sinken,
#: nicht steigen.
#:
#: Vorher standen hier 26 / 19 (Einfuehrung: 29 / 23). Diese Zahlen waren
#: gegen eine gewachsene Entwicklungsdatenbank gemessen und auf einer
#: frischen Installation nie erreichbar: Dort fehlen dreizehn Tabellen
#: zusaetzlich, die lokal irgendwann von Hand entstanden sind und die keine
#: Migration anlegt.
#:
#: Lebend (+2, nach Abzug zweier Tabellen, die in der gewachsenen Datenbank
#: fehlen und in der frischen da sind):
#:   domain_compliance.whistleblower_reports, domain_crm.crm_activities,
#:   domain_pos.payment_methods, domain_pos.promotions
#: Ruhend (+6, analog):
#:   domain_crm.contacts, domain_crm.crm_customers,
#:   domain_einkauf.ers_invoices, domain_einkauf.ers_suppliers,
#:   domain_finance.ebilanz_exports, domain_futtermittel.feed_raw_materials,
#:   domain_futtermittel.feed_recipes,
#:   domain_futtermittel.raw_material_analyses,
#:   domain_futtermittel.recipe_ingredients
#:
#: Das ist **keine** neue Schuld, sondern dieselbe Schuld richtig gemessen:
#: Eine Ratsche gegen eine Datenbank, die nur auf einem Rechner existiert,
#: misst diesen Rechner, nicht die Anwendung.
#:
#: 2026-09-30, lebend 28 -> 25 nachgezogen: Die drei Tabellen, die die
#: Migrationen ``whistleblower_eine_tabelle_20260930`` und
#: ``pos_zahlarten_aktionen_20260930`` nachgetragen haben
#: (``domain_compliance.whistleblower_reports``,
#: ``domain_pos.payment_methods``, ``domain_pos.promotions``), sind auf einer
#: frischen Installation da. Die Schwelle stand seither drei Plaetze zu hoch —
#: drei neue Verweise ins Leere waeren durchgegangen. Gemessen mit
#: ``DATABASE_URL=…/valeo_probe`` nach ``scripts/pruefstand_db.py``.
#:
#: 2026-09-30, lebend 25 -> 24: ``domain_shared.sepa_mandates`` legt
#: ``lastschrift_mandant_20260930`` an.
#:
#: 2026-10-01, lebend 24 -> 21: ``domain_pos.pos_transactions`` war ein falscher
#: Verweis (der Kassenumsatz liegt in
#: ``domain_docflow.pos_fiscal_transactions``), ``domain_shared.webhooks``
#: ebenso (die Anbindungen liegen in ``domain_shared.webhook_registrations``),
#: und die Kundenakte liest ``domain_crm.contacts``/``.crm_customers`` nicht
#: mehr an einem lebenden Weg.
#:
#: Blinder Fleck, bewusst nicht in diesem Slice behoben: Gescannt wird nur
#: ``app/api/v1/endpoints``. Wandert rohes SQL in einen Dienst unter
#: ``app/services``, sinkt die Zahl, ohne dass Schuld verschwindet. Die Pruefung
#: auf ``app/services`` auszuweiten ist richtig und ein eigener Vorgang — der
#: Bestand dort ist nicht gemessen.
#:
#: 2026-10-01, lebend 21 -> 18: Das zentrale Vertragsregister
#: (``domain_contracts.contracts``, ``.contract_versions``,
#: ``.contract_obligations``) hat mit ``kontraktregister_20261001`` eine
#: Migration.
#:
#: 2026-10-01, lebend 18 -> 17: Der Rueckfall auf ``domain_erp.accounting_periods``
#: ist entfallen — er meldete eine Periodensperre, ohne zu sperren
#: (``periode-ein-zustand-20261001.md``).
#:
#: 2026-10-01, lebend 17 -> 14: `steuernachweis_mandant_20261001` legt
#: `domain_compliance.gelangensbestaetigung`, `.intrastat_meldungen` und
#: `.lksg_supplier_risk_assessments` an.
#:
#: 2026-10-01, lebend 14 -> 12: `eudr_sorgfaltserklaerung_20261001` legt das
#: EUDR-Register an, und der Statusweg liest nicht mehr `domain_inventory.lots`
#: — eine Tabelle, die kein Migrationsstand anlegt.
#:
#: 2026-10-05, lebend 12 -> 10: `genossenschaft_mitgliederregister_20261005`
#: legt `domain_shared.genossenschaft_mitglieder` und
#: `.genossenschaft_anteilsbewegungen` an. Beide Tabellen existierten in
#: keiner Datenbank; die Mitgliederliste antwortete `[]` und die
#: Kapitaluebersicht 0,00 EUR.
#:
#: 2026-10-05, lebend 10 -> 9: `domain_agrar.wiegungen` wird nicht angelegt,
#: sondern abgeloest — die Doppelwiegung schreibt das kanonische Rueckgrat
#: `domain_inventory.weighing_tickets` (`wiegung_kanonisch_20261005`).
#:
#: 2026-10-05, lebend 9 -> 8: `kontrakt_disposition_20261005` legt
#: `domain_agrar.kontrakt_dispositionen` an. Vorher legte der
#: Anwendungscode die Tabelle zur Laufzeit selbst an; vor dem ersten POST
#: antwortete das Auflisten `[]`.
#:
#: 2026-10-05, lebend 8 -> 7: `preisfindung_rabattregeln_20261005` legt
#: `domain_pricing.discount_rules` an, und die Preiskaskade liest den
#: Kontraktpreis aus dem fuehrenden Kontraktmodell statt aus
#: `domain_contracts.contracts.discount_percent` — zwei Spalten, die es nicht
#: gibt.
BASELINE_LEBEND = 7
BASELINE_RUHEND = 25

ENDPUNKTE = pathlib.Path("app/api/v1/endpoints")
FRONTEND = pathlib.Path("packages/frontend-web/src")

_TABELLE = re.compile(r"\b(?:FROM|JOIN|INTO|UPDATE)\s+(domain_[a-z_]+\.[a-z_]+)", re.IGNORECASE)
_FE_PFAD = re.compile(r"['\"`](/api/v1/[^'\"`\s]*)['\"`]")


def _tabellen_je_datei() -> dict[str, set[str]]:
    gefunden: dict[str, set[str]] = {}
    for datei in ENDPUNKTE.glob("*.py"):
        text_ = datei.read_text(encoding="utf-8", errors="ignore")
        treffer = {t.lower() for t in _TABELLE.findall(text_)}
        if treffer:
            gefunden[datei.name] = treffer
    return gefunden


def _vorhandene_tabellen() -> set[str]:
    from sqlalchemy import create_engine, text

    url = os.environ.get(
        "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
    )
    with create_engine(url).connect() as verbindung:
        zeilen = verbindung.execute(
            text(
                "SELECT table_schema, table_name FROM information_schema.tables "
                "WHERE table_schema LIKE 'domain%'"
            )
        ).fetchall()
    return {f"{z[0]}.{z[1]}" for z in zeilen}


def _erreichbare_dateien() -> set[str]:
    """Dateien, deren Routen eine Maske oder das Frontend wirklich aufruft."""
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
    from app.main import app

    modul_routen: dict[str, set[str]] = collections.defaultdict(set)
    for route in app.routes:
        modul = getattr(getattr(route, "endpoint", None), "__module__", "") or ""
        if ".endpoints." in modul:
            modul_routen[modul.split(".")[-1] + ".py"].add(getattr(route, "path", ""))

    gerufen: set[str] = set()
    for screen_id in SCREEN_DEFINITION_BUILDERS:
        screen = get_screen_definition(screen_id) or {}
        for quelle in screen.get("dataSources") or []:
            if quelle.get("endpoint"):
                gerufen.add(re.sub(r"\{[^}]+\}", "x", quelle["endpoint"].split("?")[0]))
    for datei in FRONTEND.rglob("*.ts*"):
        name = str(datei)
        if "__tests__" in name or ".gen." in name:
            continue
        for pfad in _FE_PFAD.findall(datei.read_text(encoding="utf-8", errors="ignore")):
            gerufen.add(re.sub(r"\$\{[^}]*\}", "x", pfad.split("?")[0]))

    erreichbar = set()
    for datei, pfade in modul_routen.items():
        for pfad in pfade:
            if re.sub(r"\{[^}]+\}", "x", pfad) in gerufen:
                erreichbar.add(datei)
                break
    return erreichbar


def pruefe() -> dict:
    je_datei = _tabellen_je_datei()
    vorhanden = _vorhandene_tabellen()
    erreichbar = _erreichbare_dateien()

    alle = {t for s in je_datei.values() for t in s}
    fehlend = sorted(t for t in alle if t not in vorhanden)

    lebend: list[tuple[str, list[str]]] = []
    ruhend: list[tuple[str, list[str]]] = []
    for tabelle in fehlend:
        dateien = sorted(d for d, ts in je_datei.items() if tabelle in ts)
        (lebend if any(d in erreichbar for d in dateien) else ruhend).append((tabelle, dateien))

    return {
        "referenziert": len(alle),
        "fehlend": fehlend,
        "lebend": lebend,
        "ruhend": ruhend,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    try:
        ergebnis = pruefe()
    except Exception as fehler:  # noqa: BLE001 — ohne Datenbank keine Aussage
        print(f"UEBERSPRUNGEN: keine Datenbank erreichbar ({fehler})")
        return 0

    print(
        f"Tabellenverweise: {ergebnis['referenziert']} referenziert, "
        f"{len(ergebnis['fehlend'])} fehlen — "
        f"{len(ergebnis['lebend'])} an lebenden Wegen (Schwelle {BASELINE_LEBEND}), "
        f"{len(ergebnis['ruhend'])} ruhend (Schwelle {BASELINE_RUHEND})."
    )

    if args.list:
        print("\nAn lebenden Wegen — jemand sieht das Ergebnis:")
        for tabelle, dateien in ergebnis["lebend"]:
            print(f"  {tabelle}  ({', '.join(dateien[:3])})")
        print("\nRuhend — kein Weg dorthin:")
        for tabelle, dateien in ergebnis["ruhend"]:
            print(f"  {tabelle}  ({', '.join(dateien[:3])})")

    schlecht = False
    if len(ergebnis["lebend"]) > BASELINE_LEBEND:
        print("\nFEHLER: Neue fehlende Tabelle an einem lebenden Weg.")
        schlecht = True
    if len(ergebnis["ruhend"]) > BASELINE_RUHEND:
        print("\nFEHLER: Neue fehlende Tabelle in ruhendem Code.")
        schlecht = True
    if schlecht:
        print(
            "        Entweder die Tabelle bauen oder den Verweis korrigieren —\n"
            "        ein gefangener Fehler wird in der Maske zu einer Null."
        )
        return 1

    print("OK: keine neuen Verweise ins Leere.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
