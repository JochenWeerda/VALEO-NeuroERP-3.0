#!/usr/bin/env python3
"""Pruefkette vor jedem Push - alles, woran PRs in CI wiederholt rot wurden, in einem Lauf.

Entstanden 19.11.2026: In zwei PRs wurden an einem Tag dreimal dieselben Ursachen rot - Register nicht neu erzeugt
(RLS-Inventar, Pflichtstruktur, Tabellenkatalog), Pruefstand hinter main, und DB-Tests, die still uebersprungen
wurden, weil TEST_DATABASE_URL leer war. Eine Checkliste vergisst man; dieses Skript nicht.

Regel: Neue Fehlerursache aus CI -> Pruefung hier ergaenzen, nicht in eine Liste schreiben.

    python scripts/vor_push.py                  # Pruefstand, Register, betroffene Tests
    python scripts/vor_push.py --ohne-tests     # nur Pruefstand und Register (schnell)
    python scripts/vor_push.py --base origin/main

Pruefstand ist immer die gemeinsame Datenbank valeo_probe (keine weitere Test-DB anlegen). Steht sie hinter dem
Alembic-Kopf und bringt der Branch keine eigene Migration mit, wird sie unter demselben Namen neu aufgebaut.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# VOR_PUSH_REPO: der zu pruefende Baum, wenn das Skript von aussen kommt (Hook auf Branches ohne dieses Skript).
REPO = Path(os.environ.get("VOR_PUSH_REPO") or Path(__file__).resolve().parents[1]).resolve()
HIER = Path(__file__).resolve().parent
VORGABE_PRUEFSTAND = "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"
BLOCK = 6  # Testdateien je pytest-Prozess (mehr legte Docker Desktop lahm)
RUECKWEG: str | None = None  # Revision, auf die der Pruefstand nach voruebergehend eingespielten Branch-Migrationen zurueckgeht
#: Tabellen, die die Branch-Migrationen entfernen: Tests, die sie nennen, laufen mit (19.11.2026: S5 entfernte
#: domain_einkauf.bestellungen; der RLS-Test nannte sie, aber keines der geaenderten Module - lokal gruen, CI rot).
ENTFERNTE_TABELLEN: set[str] = set()

#: Register und Verzeichnisse: (Name, Pruefbefehl, Befehl zum Neuerzeugen)
REGISTER: list[tuple[str, list[str], str]] = [
    ("Baseline-Integritaet", ["python", "scripts/check_baseline_integrity.py", "--base", "{base}"], "-"),
    ("Improvement-Pipelines (Godfiles, Paginierung, ...)", ["python", "scripts/run_improvement_pipelines.py"],
     "python scripts/check_file_size.py --update-baseline; python scripts/check_pagination.py --update-baseline "
     "(Ratschen nur senken: nach Entfernen von Code)"),
    ("Doc-Generatoren (OpenAPI, C4, Architektur-Index, MCP, Aktionsmatrix)",
     ["bash", "scripts/check_all_doc_generators.sh", "--check"],
     "python scripts/generate_openapi.py; python scripts/generate_code_inventories.py; "
     "bash scripts/check_all_doc_generators.sh  (das Sammelskript schreibt OpenAPI und Inventare nicht)"),
    ("Tabellenkatalog (Lineage)", ["python", "scripts/tabellenkatalog_lineage.py", "--check"],
     "python scripts/tabellenkatalog_lineage.py"),
    ("RLS-Inventar (frisches Schema)", ["python", "scripts/rls_inventory.py", "--check"], "python scripts/rls_inventory.py"),
    ("RLS-Domaenenmatrix", ["python", "scripts/rls_domain_matrix.py", "--check"], "python scripts/rls_domain_matrix.py"),
    ("Pflichtstruktur der Domaenen", ["python", "scripts/check_required_domain_schemas.py"],
     "REQUIRED_STRUCTURE in scripts/check_required_domain_schemas.py anpassen"),
    ("Tabellenzuordnung der Domaenen", ["python", "scripts/check_domain_table_ownership.py"], "siehe Ausgabe"),
    ("CLI-Register der Maskenaktionen", ["python", "scripts/generate_cli_mask_commands.py", "--check"],
     "python scripts/generate_cli_mask_commands.py"),
    ("Aktionskatalog der KI-Bedienung", ["python", "scripts/generate_screen_action_catalog.py", "--check"],
     "python scripts/generate_screen_action_catalog.py"),
    ("Masken-Studio-Ratsche", ["python", "scripts/mask_studio_inventory.py", "--check"], "python scripts/mask_studio_inventory.py"),
    ("Maskenfamilien-Versionen", ["python", "scripts/generate_mask_family_versions.py", "--check"],
     "python scripts/generate_mask_family_versions.py"),
    ("Belegmasken-Versionen", ["python", "scripts/generate_document_screen_versions.py", "--check"],
     "python scripts/generate_document_screen_versions.py"),
    ("Studio-Screen-Katalog", ["python", "scripts/generate_studio_screen_versions.py", "--check"],
     "python scripts/generate_studio_screen_versions.py"),
    ("Docs-Governance", ["node", "scripts/docs-governance-check.cjs"], "siehe Ausgabe"),
]

#: Tests, die bei jeder Aenderung mitlaufen: Register, die ein Grep auf Namen nicht findet.
IMMER = ["tests/test_mask_endpoint_inventory.py", "tests/test_rls_inventory_contract.py"]

#: Skip-Gruende, die heissen: die Datenbank fehlte - das ist ein Fehler, kein Skip.
STILLER_SKIP = re.compile(
    r"TEST_DATABASE_URL|DATABASE_URL|Datenbank nicht erreichbar|nicht erreichbar|Could not parse SQLAlchemy URL|"
    r"Pruefstand.*nicht gesetzt|PostgreSQL required", re.I)


def _bash() -> str:
    """Unter Windows die Git-Bash - ``bash`` aus Python traefe sonst die WSL-Bash (System32)."""
    if os.name != "nt":
        return "bash"
    ausfuehrung = Path(_git("--exec-path").strip())  # ...\Git\mingw64\libexec\git-core
    for kandidat in (ausfuehrung.parents[2] / "bin" / "bash.exe", ausfuehrung.parents[2] / "usr" / "bin" / "bash.exe"):
        if kandidat.exists():
            return str(kandidat)
    return "bash"


def _git(*argumente: str) -> str:
    return subprocess.run(["git", *argumente], cwd=REPO, capture_output=True, text=True, check=False).stdout


def _kopf(titel: str) -> None:
    print(f"\n=== {titel}", flush=True)


# ── Pruefstand ────────────────────────────────────────────────────────────────

def _pruefstand_umgebung() -> str:
    """Beide Variablen auf denselben Pruefstand - ein leerer Wert liess DB-Tests still ueberspringen."""
    url = os.environ.get("TEST_DATABASE_URL") or VORGABE_PRUEFSTAND
    if not url.strip() or "valeo_neuro_erp" in url:
        raise SystemExit(f"TEST_DATABASE_URL zeigt nicht auf den Pruefstand: {url!r}")
    os.environ["TEST_DATABASE_URL"] = url
    os.environ["DATABASE_URL"] = url
    os.environ.setdefault("PGAPPNAME", "agent:vor_push")
    return url


def _alembic_koepfe() -> set[str]:
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    return set(ScriptDirectory.from_config(Config(str(REPO / "alembic.ini"))).get_heads())


def _db_revisionen(url: str) -> set[str] | None:
    import sqlalchemy as sa

    try:
        engine = sa.create_engine(url, connect_args={"connect_timeout": 5})
        with engine.connect() as verbindung:
            return {str(z[0]) for z in verbindung.execute(sa.text("SELECT version_num FROM alembic_version"))}
    except Exception as fehler:  # noqa: BLE001
        print(f"  Pruefstand nicht lesbar: {type(fehler).__name__}: {fehler}".splitlines()[0])
        return None


def _laufe(befehl: list[str], titel: str) -> bool:
    lauf = subprocess.run(befehl, cwd=REPO, capture_output=True, text=True, check=False, encoding="utf-8",
                          errors="replace")
    letzte = [z for z in (lauf.stdout + lauf.stderr).splitlines() if z.strip()][-1:] or [""]
    print(f"  {'OK ' if lauf.returncode == 0 else 'ROT'}   {titel}: {letzte[0][:160]}", flush=True)
    return lauf.returncode == 0


def pruefe_pruefstand(url: str, base: str) -> bool:
    """valeo_probe so herrichten wie die CI ihre Datenbank: Migrationen, Seed, getrennte Rollen.

    Rollen mit --eigentum wie im Betrieb: sonst migriert Alembic als valeo_owner gegen Objekte von valeo_dev und
    scheitert ("must be owner").
    Nur Alembic (pruefstand_db.py) reichte nicht: Ohne Seed fehlten die Bestandszeilen, ohne provision_db_roles die
    Rechte der App-Rolle - Tests waren lokal rot oder still uebersprungen, in CI gruen (19.11.2026: Inventur- und
    POS-Retoure-Tests, galten lange als "Umgebung"). Bewusst OHNE create_all: RLS-Inventar und Schemavertraege gelten
    dem rein migrierten Stand (die CI prueft sie vor create_all); ORM-Zusatztabellen verfaelschten sie.
    """
    _kopf("Pruefstand (wie CI)")
    eigene = [p for p in _git("diff", "--name-only", "--diff-filter=A", f"{base}...HEAD", "--", "alembic/versions").split()
              if p.endswith(".py")]
    koepfe, stand = _alembic_koepfe(), _db_revisionen(url)
    if stand is None:
        return False
    py = sys.executable
    if eigene:
        # Die CI prueft den Branch MIT seiner Migration. Ohne sie meldeten DB-gestuetzte Register und Tests den alten
        # Schemastand (19.11.2026, S5: entfernte Tabellen "gefunden"). Deshalb fuer die Dauer der Pruefung einspielen
        # und danach auf den vorherigen Stand zurueck (main() -> stelle_pruefstand_zurueck). Scheitert der Rueckweg,
        # baut der naechste Lauf aus main den Pruefstand neu (unbekannte Revision != Kopf).
        global RUECKWEG
        if len(stand) != 1:
            print(f"  Pruefstand hat mehrere Revisionen {sorted(stand)}; ohne eindeutigen Rueckweg kein Einspielen.")
            return False
        print(f"  Branch bringt eigene Migrationen mit ({len(eigene)}): fuer die Pruefung auf {sorted(koepfe)}, "
              f"danach zurueck auf {sorted(stand)}.")
        rollen = [py, "scripts/provision_db_roles.py", "--url", url, "--anwenden", "--eigentum"]
        if not _laufe(rollen, "Rollen und Eigentum (vor dem Einspielen)"):
            return False
        RUECKWEG = next(iter(stand))
        vorher = _tabellen(url)
        if not _laufe([py, "-m", "alembic", "upgrade", "head"], "Branch-Migrationen voruebergehend einspielen"):
            return False
        ENTFERNTE_TABELLEN.update(vorher - _tabellen(url))
        if ENTFERNTE_TABELLEN:
            print(f"  Entfernte Tabellen: {len(ENTFERNTE_TABELLEN)} - Tests, die sie nennen, laufen mit.")
        return _laufe(rollen, "Rechte auf neue Objekte")
    neu_aufgebaut = stand != koepfe
    if neu_aufgebaut:
        print(f"  Pruefstand {sorted(stand)} != Kopf {sorted(koepfe)}: wird unter demselben Namen neu aufgebaut.")
        if not _laufe([py, "scripts/pruefstand_db.py"], "Neuaufbau aus den Migrationen"):
            return False
    else:
        print(f"  Revision: {sorted(koepfe)}")
    schritte = []
    # Seed einmal nach dem Aufbau; Merkmal "schon wie CI": die App-Rolle hat Rechte.
    if neu_aufgebaut or not _wie_ci(url):
        schritte.append(([py, "-m", "app.seeds.inventory_seed"], "Bestands-Seed"))
    schritte.append(([py, "scripts/provision_db_roles.py", "--url", url, "--anwenden", "--eigentum"], "Rollen und Rechte"))
    return all([_laufe(befehl, titel) for befehl, titel in schritte])


def _tabellen(url: str) -> set[str]:
    import sqlalchemy as sa

    with sa.create_engine(url).connect() as verbindung:
        return {f"{s}.{n}" for s, n in verbindung.execute(sa.text(
            "SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema')"))}


def _wie_ci(url: str) -> bool:
    import sqlalchemy as sa

    try:
        with sa.create_engine(url).connect() as verbindung:
            return bool(verbindung.execute(sa.text(
                "SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'valeo_app') "
                "AND has_schema_privilege('valeo_app', 'domain_inventory', 'USAGE')")).scalar())
    except Exception:  # noqa: BLE001 - fehlt die Rolle, ist der Pruefstand eben noch nicht wie CI
        return False


# ── Register ──────────────────────────────────────────────────────────────────

def pruefe_register(base: str) -> list[str]:
    _kopf("Register und Verzeichnisse")
    rot = []
    for name, befehl, abhilfe in REGISTER:
        befehl = [teil.replace("{base}", base) for teil in befehl]
        if befehl[0] == "bash":
            befehl[0] = _bash()
        if befehl[0] == "python":
            befehl[0] = sys.executable
            if not (REPO / befehl[1]).exists() and (HIER / Path(befehl[1]).name).exists():
                befehl[1] = str(HIER / Path(befehl[1]).name)  # mitgebrachte Fassung (z. B. Lineage-Pruefung)
        beginn = time.monotonic()
        lauf = subprocess.run(befehl, cwd=REPO, capture_output=True, text=True, check=False,
                              encoding="utf-8", errors="replace")
        dauer = time.monotonic() - beginn
        if lauf.returncode == 0:
            print(f"  OK    {name} ({dauer:.0f}s)", flush=True)
            continue
        letzte = [z for z in (lauf.stdout + lauf.stderr).splitlines() if z.strip() and "Warning" not in z][-4:]
        print(f"  ROT   {name} ({dauer:.0f}s)\n        " + "\n        ".join(letzte) + f"\n        Abhilfe: {abhilfe}",
              flush=True)
        rot.append(name)
    return rot


# ── Tests ─────────────────────────────────────────────────────────────────────

def _geaenderte_dateien(base: str) -> tuple[set[str], set[str]]:
    vorhanden, entfernt = set(), set()
    for zeile in (_git("diff", "--name-status", f"{base}...HEAD") + _git("diff", "--name-status", "HEAD")).splitlines():
        teile = zeile.split("\t")
        if len(teile) < 2:
            continue
        status, pfad = teile[0], teile[-1]
        (entfernt if status.startswith("D") else vorhanden).add(pfad)
        if status.startswith("R") and len(teile) == 3:
            entfernt.add(teile[1])
    return vorhanden, entfernt


def betroffene_tests(base: str) -> list[str]:
    vorhanden, entfernt = _geaenderte_dateien(base)
    tests = {p for p in vorhanden if p.startswith("tests/") and Path(p).name.startswith("test_") and p.endswith(".py")}
    begriffe = set()
    for pfad in vorhanden | entfernt:
        if not pfad.endswith(".py") or not pfad.startswith(("app/", "modules/", "scripts/")):
            continue
        modul = pfad[:-3].replace("/", ".")
        begriffe.add(modul)
        stamm = Path(pfad).stem
        if len(stamm) >= 8 and stamm not in {"__init__", "service", "schemas", "router", "models"}:
            begriffe.add(stamm)
    for begriff in sorted(begriffe):
        for treffer in _git("grep", "-l", "-F", begriff, "--", "tests/*.py", "tests/**/*.py").split():
            tests.add(treffer)
    for tabelle in sorted(ENTFERNTE_TABELLEN):
        # schema.name oder f"{SCHEMA}.name": der Name nach einem Punkt, als ganzes Wort
        name = tabelle.split(".", 1)[1]
        genau = re.compile(r"\." + re.escape(name) + r"\b")
        for treffer in _git("grep", "-l", "-F", f".{name}", "--", "tests/*.py", "tests/**/*.py").split():
            if genau.search((REPO / treffer).read_text(encoding="utf-8", errors="ignore")):
                tests.add(treffer)
    tests.update(p for p in IMMER if (REPO / p).exists())
    tests.update(str(p.relative_to(REPO)).replace("\\", "/") for p in (REPO / "tests").glob("*ratsche*.py"))
    return sorted(t for t in tests if (REPO / t).exists() and "/fixtures/" not in t)


def pruefe_tests(dateien: list[str]) -> list[str]:
    _kopf(f"Tests ({len(dateien)} Dateien, Bloecke zu {BLOCK})")
    rot: list[str] = []
    for start in range(0, len(dateien), BLOCK):
        block = dateien[start:start + BLOCK]
        lauf = subprocess.run(
            [sys.executable, "-m", "pytest", *block, "-q", "-o", "addopts=", "-p", "no:cacheprovider", "-rfEs"],
            cwd=REPO, capture_output=True, text=True, check=False, encoding="utf-8", errors="replace")
        zeilen = lauf.stdout.splitlines()
        fehler = [z for z in zeilen if z.startswith(("FAILED ", "ERROR "))]
        still = [z for z in zeilen if z.startswith("SKIPPED") and STILLER_SKIP.search(z)]
        summe = next((z for z in reversed(zeilen) if re.search(r"\d+ (passed|failed|error)", z)), "keine Summe")
        print(f"  [{start // BLOCK + 1}] {summe.strip('= ')}", flush=True)
        if lauf.returncode not in (0, 5) and not fehler:
            fehler = [f"Abbruch ohne Testergebnis: {block} (Exit {lauf.returncode})"]
        for z in fehler + [f"STILL UEBERSPRUNGEN (DB fehlte): {z}" for z in still]:
            print(f"        {z[:240]}")
        rot.extend(fehler + still)
    return rot


def stelle_pruefstand_zurueck() -> None:
    if RUECKWEG is None:
        return
    _kopf("Pruefstand zurueck auf die Basis")
    if not _laufe([sys.executable, "-m", "alembic", "downgrade", RUECKWEG], f"Downgrade auf {RUECKWEG}"):
        print("  Rueckweg gescheitert: der naechste Lauf auf main baut valeo_probe neu auf "
              "(oder sofort: python scripts/pruefstand_db.py in einem Baum auf main).")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--ohne-tests", action="store_true")
    args = parser.parse_args()
    for strom in (sys.stdout, sys.stderr):  # Windows-Codepage: Umlaute und Ersatzzeichen nicht abstuerzen lassen
        strom.reconfigure(errors="replace")

    url = _pruefstand_umgebung()
    try:
        stand_ok = pruefe_pruefstand(url, args.base)
        register_rot = pruefe_register(args.base)
        tests_rot = [] if args.ohne_tests else pruefe_tests(betroffene_tests(args.base))
    finally:
        stelle_pruefstand_zurueck()

    _kopf("Ergebnis")
    if stand_ok and not register_rot and not tests_rot:
        print("  GRUEN - Push freigegeben.")
        return 0
    if not stand_ok:
        print("  Pruefstand nicht bereit.")
    for name in register_rot:
        print(f"  Register rot: {name}")
    if tests_rot:
        print(f"  {len(tests_rot)} rote oder still uebersprungene Tests")
    print("  ROT - nicht pushen.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
