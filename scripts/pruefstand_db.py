#!/usr/bin/env python3
"""Setzt die Pruefstand-Datenbank neu auf: loeschen, anlegen, migrieren.

Warum es dieses Skript gibt
---------------------------

Am 29.09.2026 waren neunundfuenfzig Tests rot. Keiner davon wegen eines
Programmierfehlers — geprueft worden war gegen die gewachsene
Entwicklungsdatenbank. Die weicht in **beide** Richtungen von einer frischen ab:

- Sie hat Bedingungen **verloren**: Fremdschluessel
  (``delivery_notes.customer_id`` auf ``customers``), Pruefbedingungen
  (``ck_delivery_notes_status``) und NOT-NULL-Regeln auf ``sales_orders``.
  Tests, die Kunden und Artikel nie anlegten, liefen deshalb gruen.
- Sie hat Spalten und Tabellen **gewonnen**, die keine Migration anlegt
  (``sales_offers.customer_name``, ``domain_crm.crm_customers`` und mehr). Auf
  einer frischen Installation scheiterte damit das Anlegen eines Angebots.

Dahinter standen drei echte Fehler, die niemand sah: Ein Lieferschein kam auf
einer Neuinstallation nie ueber den Entwurf hinaus, ein Angebot liess sich
nicht anlegen, und eine Loeschung nach Art. 17 DSGVO tat nichts und meldete
503.

**Fuer das Schema ist eine frische Datenbank der Pruefstand, fuer die Daten die
gewachsene.** Beide braucht es, und sie sind nicht austauschbar:

| Pruefstand | wofuer |
|---|---|
| frisch (dieses Skript) | Schema, Migrationen, Vertragstests, alles mit rohem SQL |
| gewachsen (``DATABASE_URL``) | Maskenabnahme, Statuswoerterbuecher, echte Datenlagen |

Aufruf
------

Ressourcenregel fuer alle Agenten (User-Vorgabe 2026-10-01): Vorhandenen
Pruefstand wiederverwenden. Keine Datenbank oder Dockerinstanz je Test/Suite/
Slice/Agent. Der Aufruf ohne Option setzt den gemeinsamen Pruefstand zurueck
und ist keine normale Testvorbereitung! Fuer Sitzungsstart --status verwenden;
--keep nur im abgestimmten Migrationsclaim. Frische-Schema-Abnahmen am selben
Pruefstand koordinieren, niemals waehrend fremder Nutzung zuruecksetzen.
Siehe AGENTS.md und docs/quality-assurance/test-database-resource-policy-20261001.md.

    python scripts/pruefstand_db.py             # aufsetzen (idempotent)
    python scripts/pruefstand_db.py --status    # nur nachsehen, nichts aendern
    python scripts/pruefstand_db.py --keep      # nicht loeschen, nur migrieren

Die Verbindung kommt aus ``TEST_DATABASE_URL``. Fehlt die, wird sie aus
``DATABASE_URL`` abgeleitet, indem der Datenbankname durch ``valeo_probe``
ersetzt wird — Host, Port und Zugangsdaten bleiben. Im Code steht keine
Zugangsdatei und kein Passwort.

Sicherung
---------

Das Skript loescht nur Datenbanken, deren Name als Pruefstand erkennbar ist
(``probe``, ``test`` oder ``pruefstand`` im Namen). Ein Zeigefehler auf
``valeo_neuro_erp`` bricht ab, statt die Arbeit von Monaten zu loeschen.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy.engine.url import URL, make_url

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Nur Namen, die eines dieser Woerter tragen, darf das Skript loeschen.
PRUEFSTAND_MARKER = ("probe", "test", "pruefstand")

#: Vorgabename, wenn nur DATABASE_URL gesetzt ist.
VORGABE_NAME = "valeo_probe"


def pruefstand_url() -> URL:
    """Die Verbindung zum Pruefstand — aus der Umgebung, nie aus dem Code."""
    roh = os.environ.get("TEST_DATABASE_URL")
    if roh:
        return make_url(roh)

    basis = os.environ.get("DATABASE_URL")
    if not basis:
        raise SystemExit(
            "Weder TEST_DATABASE_URL noch DATABASE_URL gesetzt.\n"
            "  export TEST_DATABASE_URL=postgresql://…/valeo_probe\n"
            "oder DATABASE_URL setzen; dann wird der Datenbankname durch "
            f"'{VORGABE_NAME}' ersetzt."
        )
    return make_url(basis).set(database=VORGABE_NAME)


def ist_pruefstand(url_oder_name: str | None) -> bool:
    """Darf diese Datenbank weggeworfen werden?

    Oeffentlich, weil nicht nur dieses Skript die Frage stellt: Tests, die das
    Schema aendern (eine Spalte umbenennen, eine Bedingung anlegen), duerfen
    nur gegen eine Wegwerf-Datenbank laufen. Bricht ein solcher Lauf zwischen
    Hin- und Rueckaenderung ab — abgeschnittene Sitzung, Speichermangel,
    gestoppter Dienst —, bleibt die Aenderung stehen. Auf einer geteilten
    Entwicklungsdatenbank waere das eine Stoerung fuer jeden, der danach
    arbeitet.

    Nimmt eine Verbindungszeichenfolge oder einen blossen Datenbanknamen.
    """
    if not url_oder_name:
        return False
    name = url_oder_name
    if "/" in name:
        try:
            name = make_url(url_oder_name).database or ""
        except Exception:  # noqa: BLE001 — unlesbare URL ist kein Pruefstand
            return False
    klein = name.lower()
    return any(marker in klein for marker in PRUEFSTAND_MARKER)


def _ist_pruefstand(name: str) -> bool:
    """Alter, modulinterner Name — bleibt, damit nichts bricht."""
    return ist_pruefstand(name)


def _verwaltungsverbindung(url: URL):
    """Verbindung auf 'postgres', denn eine Datenbank kann sich nicht selbst loeschen."""
    import psycopg2

    verwaltung = url.set(database="postgres")
    conn = psycopg2.connect(verwaltung.render_as_string(hide_password=False))
    conn.autocommit = True  # CREATE/DROP DATABASE geht nicht in einer Transaktion
    return conn


def _existiert(url: URL) -> bool:
    conn = _verwaltungsverbindung(url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (url.database,))
            return cur.fetchone() is not None
    finally:
        conn.close()


def _revision(url: URL) -> str | None:
    import psycopg2

    try:
        conn = psycopg2.connect(url.render_as_string(hide_password=False))
    except Exception:  # noqa: BLE001 — eine fehlende Datenbank ist keine Revision
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass('alembic_version')")
            if cur.fetchone()[0] is None:
                return None
            cur.execute("SELECT version_num FROM alembic_version")
            zeile = cur.fetchone()
            return zeile[0] if zeile else None
    finally:
        conn.close()


def _neu_anlegen(url: URL) -> None:
    conn = _verwaltungsverbindung(url)
    try:
        with conn.cursor() as cur:
            # Offene Verbindungen wuerden das DROP blockieren.
            cur.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (url.database,),
            )
            cur.execute(f'DROP DATABASE IF EXISTS "{url.database}"')
            cur.execute(f'CREATE DATABASE "{url.database}"')
    finally:
        conn.close()


def _migrieren(url: URL) -> int:
    umgebung = dict(os.environ)
    umgebung["DATABASE_URL"] = url.render_as_string(hide_password=False)
    ergebnis = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=REPO_ROOT,
        env=umgebung,
        capture_output=True,
        text=True,
    )
    if ergebnis.returncode != 0:
        # Der Alembic-Fehler ist die Auskunft, auf die es ankommt — nicht
        # "Migration fehlgeschlagen".
        print(ergebnis.stdout[-4000:])
        print(ergebnis.stderr[-4000:], file=sys.stderr)
    return ergebnis.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--status", action="store_true",
        help="Nur nachsehen: existiert der Pruefstand, auf welcher Revision steht er?",
    )
    parser.add_argument(
        "--keep", action="store_true",
        help="Nicht loeschen, nur migrieren (fuer einen Pruefstand, der schon steht).",
    )
    args = parser.parse_args()

    url = pruefstand_url()
    # Ohne Passwort ausgeben — die Zeile landet in Protokollen.
    sichtbar = url.render_as_string(hide_password=True)

    if args.status:
        if not _existiert(url):
            print(f"Pruefstand {sichtbar}: existiert nicht.")
            return 1
        rev = _revision(url)
        print(f"Pruefstand {sichtbar}: vorhanden, Revision {rev or 'keine'}.")
        return 0

    if not _ist_pruefstand(url.database or ""):
        raise SystemExit(
            f"'{url.database}' sieht nicht wie ein Pruefstand aus.\n"
            "Das Skript loescht nur Datenbanken, deren Name 'probe', 'test' oder "
            "'pruefstand' enthaelt — damit ein Zeigefehler nicht die "
            "Entwicklungsdatenbank trifft."
        )

    if args.keep:
        if not _existiert(url):
            raise SystemExit(f"--keep, aber {sichtbar} existiert nicht.")
        print(f"Pruefstand {sichtbar}: bleibt stehen, wird migriert.")
    else:
        print(f"Pruefstand {sichtbar}: wird neu angelegt.")
        _neu_anlegen(url)

    rc = _migrieren(url)
    if rc != 0:
        print("Die Migrationen sind nicht durchgelaufen — siehe Ausgabe oben.", file=sys.stderr)
        return rc

    print(f"Pruefstand steht auf Revision {_revision(url) or 'keine'}.")
    # Die Zeile zum Kopieren darf kein Passwort enthalten, muss aber
    # funktionieren — deshalb die Variable statt der ausgeschriebenen URL.
    print("\nSo wird er benutzt:")
    if os.environ.get("TEST_DATABASE_URL"):
        print('  DATABASE_URL="$TEST_DATABASE_URL" python -m pytest tests/… --no-cov -q')
    else:
        print(f"  export TEST_DATABASE_URL={sichtbar}   # Passwort einsetzen")
        print('  DATABASE_URL="$TEST_DATABASE_URL" python -m pytest tests/… --no-cov -q')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
