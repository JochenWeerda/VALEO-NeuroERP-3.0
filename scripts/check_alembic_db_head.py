#!/usr/bin/env python
"""Prueft, ob die Datenbank auf dem Alembic-Head des Repositories steht.

Warum es dieses Skript gibt
---------------------------
Am 2026-09-15 standen zwei Migrationen im Repository, die auf der
Entwicklungsdatenbank **nicht angewandt** waren — darunter der partielle
Unique-Index aus FSX-011. Code und Tests waren dabei durchgehend gruen: Die
Tests pruefen den Migrationstext, nicht den Datenbankzustand. Die Eindeutigkeit
war also zugesichert, aber **nicht erzwungen**; die Doppelanlage bei parallelem
Speichern haette real passieren koennen.

``check_alembic_single_head.py`` faengt das nicht: es prueft die Revisionskette
im Repository, nicht die Datenbank. Genau diese Luecke schliesst dieses Skript.

Es ist **kein CI-Gate** — in der CI gibt es keine Produktionsdatenbank, und
gegen eine frisch migrierte Wegwerf-Instanz waere die Pruefung wertlos. Es
gehoert vor die Abnahme eines Slices mit Migration und in die Betriebscheckliste
vor einem Release.

Aufruf
------
    python scripts/check_alembic_db_head.py
    DATABASE_URL=... python scripts/check_alembic_db_head.py

Exit 0: Datenbank ist auf dem Repo-Head.
Exit 1: Datenbank ist zurueck (Migrationen fehlen) — mit Liste.
Exit 2: Datenbank nicht erreichbar oder Stand nicht bestimmbar.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def repo_heads() -> set[str]:
    """Heads ueber Alembic selbst bestimmen, nicht ueber Textsuche.

    Ein erster Entwurf hat die Revisionsdateien mit regulaeren Ausdruecken
    gelesen und kam auf 71 Heads statt einem: Merge-Revisionen tragen ein
    **Tupel** in ``down_revision``, und der Ausdruck sah nur den ersten Eintrag.
    Alle uebrigen Eltern galten dadurch faelschlich als Head. Dieselbe Quelle
    wie ``check_alembic_single_head.py`` zu nutzen ist nicht nur kuerzer,
    sondern die einzige, die den Graphen wirklich kennt.
    """
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    return set(script.get_heads())


def db_revision(url: str) -> str | None:
    from sqlalchemy import create_engine, text

    engine = create_engine(url)
    with engine.connect() as conn:
        zeilen = [r[0] for r in conn.execute(text("SELECT version_num FROM alembic_version"))]
    return zeilen[0] if len(zeilen) == 1 else (zeilen[0] if zeilen else None)


def main() -> int:
    url = os.environ.get("DATABASE_URL") or (
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
    )

    heads = repo_heads()
    if len(heads) != 1:
        print(f"FEHLER: {len(heads)} Alembic-Heads im Repository: {sorted(heads)}")
        print("Zuerst check_alembic_single_head.py klaeren; ohne einen Head ist der")
        print("Soll-Zustand nicht definiert.")
        return 2
    head = heads.pop()

    try:
        aktuell = db_revision(url)
    except Exception as fehler:  # noqa: BLE001 - Ursache wird ausgegeben
        print(f"FEHLER: Datenbank nicht erreichbar oder alembic_version fehlt: {fehler}")
        print("Ohne Datenbank ist keine Aussage moeglich — das ist ausdruecklich")
        print("kein 'in Ordnung'.")
        return 2

    if aktuell == head:
        print(f"OK: Datenbank steht auf dem Repo-Head ({head}).")
        return 0

    print("FEHLER: Die Datenbank ist hinter dem Repository.")
    print(f"  Repo-Head:  {head}")
    print(f"  Datenbank:  {aktuell}")
    print("")
    print("Das heisst nicht nur 'ein Feld fehlt': Ein nicht angewandter Index ist")
    print("eine Zusicherung, die niemand erzwingt. Tests bleiben gruen, weil sie")
    print("den Migrationstext pruefen, nicht die Datenbank.")
    print("")
    print("  alembic upgrade head")
    return 1


if __name__ == "__main__":
    sys.exit(main())
