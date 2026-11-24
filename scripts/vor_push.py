#!/usr/bin/env python3
"""Pruefkette vor jedem Push - alles, woran PRs in CI wiederholt rot wurden, in einem Lauf.

Entstanden 19.11.2026: In zwei PRs wurden an einem Tag dreimal dieselben Ursachen rot - Register nicht neu erzeugt
(RLS-Inventar, Pflichtstruktur, Tabellenkatalog), Pruefstand hinter main, und DB-Tests, die still uebersprungen
wurden, weil TEST_DATABASE_URL leer war. Eine Checkliste vergisst man; dieses Skript nicht.

Regel: Neue Fehlerursache aus CI -> Pruefung hier ergaenzen, nicht in eine Liste schreiben.

    python scripts/vor_push.py                  # Pruefstand, Register, betroffene Tests
    python scripts/vor_push.py --ohne-tests     # nur Pruefstand und Register (schnell)
    python scripts/vor_push.py --base origin/main

Der gemeinsame Pruefstand wird nur lesend auf Bereitschaft geprueft. Wartung erfolgt separat und koordiniert
gemaess docs/quality-assurance/test-database-resource-policy-20261001.md.
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
BLOCK = 6  # Testdateien je pytest-Prozess (mehr legte Docker Desktop lahm)
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
IMMER = ["tests/test_mask_endpoint_inventory.py", "tests/test_rls_inventory_contract.py",
         # Woertliche Kopien der ScreenDefinitions im Frontend (23.11.2026: #172 erst in CI rot).
         "tests/test_multi_domain_uix_fixture_contract.py"]

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
    """Nur einen explizit konfigurierten Pruefstand verwenden, niemals Zugangsdaten ausgeben."""
    from sqlalchemy.engine import make_url

    url = os.environ.get("TEST_DATABASE_URL", "").strip()
    try:
        parsed = make_url(url)
        name = (parsed.database or "").lower()
        if (not parsed.drivername.startswith("postgresql") or not parsed.host
                or not parsed.username or not name or "valeo_neuro_erp" in name
                or not any(marker in name for marker in ("probe", "test", "pruefstand"))):
            raise ValueError("ungueltiger Pruefstand")
    except Exception:
        raise SystemExit("TEST_DATABASE_URL fehlt oder bezeichnet keinen gueltigen PostgreSQL-Pruefstand.") from None
    os.environ["DATABASE_URL"] = url
    os.environ.setdefault("PGAPPNAME", "agent:vor_push")
    return url


def _alembic_koepfe() -> set[str]:
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    return set(ScriptDirectory.from_config(Config(str(REPO / "alembic.ini"))).get_heads())


def _db_revisionen(url: str) -> set[str] | None:
    import sqlalchemy as sa

    engine = None
    try:
        engine = sa.create_engine(url, connect_args={"connect_timeout": 5})
        with engine.connect().execution_options(postgresql_readonly=True) as verbindung:
            return {str(z[0]) for z in verbindung.execute(sa.text("SELECT version_num FROM alembic_version"))}
    except Exception as fehler:  # noqa: BLE001
        print(f"  Pruefstand nicht lesbar ({type(fehler).__name__}).")
        return None
    finally:
        if engine is not None:
            engine.dispose()


def pruefe_pruefstand(url: str, base: str) -> bool:
    """Lesender Bereitschaftscheck; Wartung niemals automatisch ausfuehren."""
    _kopf("Pruefstand (lesende Bereitschaftspruefung)")
    stand, koepfe = _db_revisionen(url), _alembic_koepfe()
    if stand is None or stand != koepfe:
        print("  Pruefstand nicht auf dem Branch-Schemakopf; Wartung koordiniert nach Runbook durchfuehren.")
        return False
    if not _wie_ci(url):
        print("  benoetigte App-Rolle oder Schema-Recht fehlt; Wartung koordiniert nach Runbook durchfuehren.")
        return False
    print("  Revision und geprueftes Schema-Recht bereit; Seed und weitere Rechte nicht vollstaendig geprueft.")
    return True


def _wie_ci(url: str) -> bool:
    import sqlalchemy as sa

    engine = None
    try:
        engine = sa.create_engine(url, connect_args={"connect_timeout": 5})
        with engine.connect().execution_options(postgresql_readonly=True) as verbindung:
            return bool(verbindung.execute(sa.text(
                "SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'valeo_app') "
                "AND has_schema_privilege('valeo_app', 'domain_inventory', 'USAGE')")).scalar())
    except Exception:
        return False
    finally:
        if engine is not None:
            engine.dispose()


def konfliktdateien(base: str) -> list[str]:
    """Nur echte Marker am Zeilenanfang in geaenderten verfolgten Dateien melden."""
    pfade = set()
    for argumente in (("diff", "--name-only", f"{base}...HEAD"),
                       ("diff", "--name-only", "HEAD"), ("diff", "--cached", "--name-only"),
                       ("diff", "--name-only", "--diff-filter=U")):
        pfade.update(_git(*argumente).splitlines())
    marker = re.compile(r"^(?:<{7} .+|>{7} .+)\s*$", re.MULTILINE)
    rot = set(_git("diff", "--name-only", "--diff-filter=U").splitlines())
    for name in sorted(pfade):
        datei = REPO / name
        if datei.is_file():
            try:
                if marker.search(datei.read_text(encoding="utf-8")):
                    rot.add(name)
            except (UnicodeError, OSError):
                continue
    return sorted(rot)


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


def _migrationstabellen(pfade: set[str]) -> tuple[set[str], bool]:
    """Statische DROP-TABLE-Namen; bei nicht eindeutigem DDL konservativ bleiben."""
    namen: set[str] = set()
    unklar = False
    python_drop = re.compile(r"\b(?:op\.)?drop_table\s*\(\s*['\"]([A-Za-z_][\w]*)['\"]", re.I)
    sql_drop = re.compile(r"\bDROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:[\w]+\.)?([A-Za-z_][\w]*)", re.I)
    for pfad in pfade:
        datei = REPO / pfad
        if not datei.is_file():
            unklar = True
            continue
        try:
            quelle = datei.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            unklar = True
            continue
        py = python_drop.findall(quelle)
        sql = sql_drop.findall(quelle)
        namen.update(py + sql)
        if len(re.findall(r"\bdrop_table\s*\(", quelle, re.I)) > len(py):
            unklar = True
        if len(re.findall(r"\bDROP\s+TABLE\b", quelle, re.I)) > len(sql):
            unklar = True
        if re.search(r"\b(?:execute|executemany)\s*\(\s*(?:f['\"]|[A-Za-z_]\w*\s*[,)])", quelle):
            unklar = True
    return namen, unklar


def _base_gueltig(base: str) -> bool:
    lauf = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"],
                          cwd=REPO, capture_output=True, text=True, check=False)
    if lauf.returncode != 0:
        return False
    basis = subprocess.run(["git", "merge-base", base, "HEAD"], cwd=REPO,
                           capture_output=True, text=True, check=False)
    return basis.returncode == 0


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
    migrationen = {p for p in vorhanden | entfernt if p.startswith("alembic/versions/")
                   and p.endswith((".py", ".sql"))}
    if migrationen:
        namen, unklar = _migrationstabellen(migrationen)
        # Schema-Vertraege laufen immer; dynamische DDL erweitert auf DB-nahe Tests.
        schema = re.compile(r"(?:schema|migration|alembic|rls|database|postgres|db_)", re.I)
        for datei in (REPO / "tests").rglob("test_*.py"):
            rel = str(datei.relative_to(REPO)).replace("\\", "/")
            if schema.search(rel):
                tests.add(rel)
            if namen:
                try:
                    quelle = datei.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    unklar = True
                    continue
                if any(re.search(r"\b" + re.escape(name) + r"\b", quelle) for name in namen):
                    tests.add(rel)
        if unklar:
            # Nicht auf Vermutungen verlassen, wenn dynamisches DDL nicht aufloesbar ist.
            raise RuntimeError("Migration enthaelt nicht statisch auswertbares DDL; nach koordinierter Pruefstandsvorbereitung mit --volle-tests erneut pruefen.")
    tests.update(p for p in IMMER if (REPO / p).exists())
    tests.update(str(p.relative_to(REPO)).replace("\\", "/") for p in (REPO / "tests").glob("*ratsche*.py"))
    return sorted(t for t in tests if (REPO / t).exists() and "/fixtures/" not in t)


def alle_testdateien() -> list[str]:
    """Alle verfolgten Python-Testdateien fuer den ausdruecklichen Volltest."""
    lauf = subprocess.run(["git", "ls-files", "-z", "--", "tests"], cwd=REPO,
                          capture_output=True, check=False)
    if lauf.returncode != 0:
        raise RuntimeError("Verfolgte Testdateien konnten nicht ermittelt werden.")
    return sorted(p for p in lauf.stdout.decode("utf-8").split("\0")
                  if p and Path(p).name.startswith("test_") and p.endswith(".py")
                  and "/fixtures/" not in p and (REPO / p).is_file())


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


#: Eine Pruefkette zur Zeit: alle teilen valeo_probe und spielen Branch-Migrationen voruebergehend ein. Dieselbe
#: Sperrdatei nutzt der Claude-Code-Hook; er setzt VALEO_PRUEFSTAND_SPERRE=gehalten, damit hier nicht doppelt gesperrt
#: wird (24.11.2026: eine Sitzung rief vor_push direkt auf und baute den Pruefstand mitten in fremden Laeufen neu).
SPERRE = Path(os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp") / "valeo_vor_push.lock"
SPERRE_FRIST_S = 45 * 60


def _lebt(pid: int) -> bool:
    if os.name == "nt":
        ausgabe = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True,
                                 check=False).stdout
        return str(pid) in ausgabe
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


class _Sperre:
    """Dateisperre ueber alle Aufrufer (Hook, Sitzungen, Hand); eine verwaiste Sperre wird uebernommen."""

    def __enter__(self):
        self.eigene = os.environ.get("VALEO_PRUEFSTAND_SPERRE") != "gehalten"
        if not self.eigene:
            return self
        frist = time.monotonic() + SPERRE_FRIST_S
        gemeldet = False
        while True:
            try:
                fd = os.open(SPERRE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"{os.getpid()} {REPO}".encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    pid = int(SPERRE.read_text().split()[0])
                except (OSError, ValueError, IndexError):
                    pid = 0
                if not pid or not _lebt(pid):
                    SPERRE.unlink(missing_ok=True)
                    continue
                if not gemeldet:
                    print(f"  Pruefstand belegt ({SPERRE.read_text().strip()}) - warte.", flush=True)
                    gemeldet = True
                if time.monotonic() > frist:
                    raise SystemExit("Pruefstand seit 45 Minuten belegt - abgebrochen.")
                time.sleep(15)

    def __exit__(self, *_):
        if self.eigene:
            SPERRE.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/main")
    testmodus = parser.add_mutually_exclusive_group()
    testmodus.add_argument("--ohne-tests", action="store_true")
    testmodus.add_argument("--volle-tests", action="store_true", help="alle verfolgten Python-Testdateien pruefen")
    args = parser.parse_args()
    for strom in (sys.stdout, sys.stderr):
        if hasattr(strom, "reconfigure"):
            strom.reconfigure(errors="replace")

    if not _base_gueltig(args.base):
        print("Ungueltiger Vergleichsstand; Pruefung abgebrochen.")
        return 1
    konflikte = konfliktdateien(args.base)
    if konflikte:
        print("Konfliktmarker in geaenderten Dateien: " + ", ".join(konflikte))
        return 1
    url = _pruefstand_umgebung()
    with _Sperre():
        try:
            if not pruefe_pruefstand(url, args.base):
                print("  ROT - Pruefstand nicht bereit; Register und Tests nicht gestartet.")
                return 1
            try:
                testdateien = [] if args.ohne_tests else (
                    alle_testdateien() if args.volle_tests else betroffene_tests(args.base)
                )
            except RuntimeError as fehler:
                print(str(fehler))
                return 1
            register_rot = pruefe_register(args.base)
            tests_rot = [] if args.ohne_tests else pruefe_tests(testdateien)
        finally:
            stelle_pruefstand_zurueck()

    _kopf("Ergebnis")
    if not register_rot and not tests_rot:
        print("  GRUEN - Push freigegeben.")
        return 0
    for name in register_rot:
        print(f"  Register rot: {name}")
    if tests_rot:
        print(f"  {len(tests_rot)} rote oder still uebersprungene Tests")
    print("  ROT - nicht pushen.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
