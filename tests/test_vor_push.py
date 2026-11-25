"""Vertrag der Pruefkette vor dem Push (scripts/vor_push.py)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

WURZEL = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("vor_push", WURZEL / "scripts" / "vor_push.py")
vor_push = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vor_push)


@pytest.mark.parametrize("zeile", [
    "SKIPPED [1] tests/test_x.py:12: TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt",
    "SKIPPED [5] tests/test_y.py:82: Datenbank nicht erreichbar: Could not parse SQLAlchemy URL from given URL string",
    "SKIPPED [1] tests/test_z.py:9: Existing shared PostgreSQL required",
])
def test_ein_skip_ohne_datenbank_gilt_als_fehler(zeile):
    """19.11.2026: leeres TEST_DATABASE_URL liess DB-Tests still ueberspringen; 'gruen' war nicht geprueft."""
    assert vor_push.STILLER_SKIP.search(zeile)


@pytest.mark.parametrize("zeile", [
    "SKIPPED [1] tests/test_a.py:3: keine Bestandszeile als Vorlage vorhanden",
    "SKIPPED [1] tests/test_b.py:7: Endpoint /api/v1/waagen-vorlagen antwortet mit 404",
])
def test_ein_fachlicher_skip_bleibt_ein_skip(zeile):
    assert not vor_push.STILLER_SKIP.search(zeile)


def test_der_pruefstand_ist_nie_die_entwicklungsdatenbank(monkeypatch):
    monkeypatch.setenv("TEST_DATABASE_URL", "postgresql://u:p@127.0.0.1:5432/valeo_neuro_erp")
    with pytest.raises(SystemExit):
        vor_push._pruefstand_umgebung()


@pytest.mark.parametrize("url", ["", "not-a-url", "postgresql://u:secret@localhost/production"])
def test_ungueltige_test_url_scheitert_ohne_zugangsdaten(monkeypatch, url):
    monkeypatch.setenv("TEST_DATABASE_URL", url)
    monkeypatch.setenv("DATABASE_URL", "unveraendert")
    with pytest.raises(SystemExit) as fehler:
        vor_push._pruefstand_umgebung()
    assert "secret" not in str(fehler.value)
    assert __import__("os").environ["DATABASE_URL"] == "unveraendert"


def test_expliziter_pruefstand_wird_verwendet(monkeypatch):
    url = "postgresql://u:secret@localhost/valeo_probe"
    monkeypatch.setenv("TEST_DATABASE_URL", url)
    assert vor_push._pruefstand_umgebung() == url
    assert __import__("os").environ["DATABASE_URL"] == url


def test_fehlende_test_url_wird_nicht_ersetzt(monkeypatch):
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    with pytest.raises(SystemExit):
        vor_push._pruefstand_umgebung()


def test_pruefstand_status_ist_lesend(monkeypatch):
    monkeypatch.setattr(vor_push, "_alembic_koepfe", lambda: {"head"})
    monkeypatch.setattr(vor_push, "_db_revisionen", lambda url: {"head"})
    monkeypatch.setattr(vor_push, "_wie_ci", lambda url: True)
    monkeypatch.setattr(vor_push.subprocess, "run", lambda *a, **k: pytest.fail("kein Prozess erwartet"))
    assert vor_push.pruefe_pruefstand("probe", "main")


@pytest.mark.parametrize("funktion", ["_db_revisionen", "_wie_ci"])
@pytest.mark.parametrize("fehler", [False, True])
def test_leseabfragen_schliessen_engine_auch_bei_fehler(monkeypatch, funktion, fehler):
    import sqlalchemy

    class Ergebnis:
        def __iter__(self):
            return iter([("head",)])

        def scalar(self):
            return True

    class Verbindung:
        def execution_options(self, **optionen):
            assert optionen == {"postgresql_readonly": True}
            return self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, query):
            if fehler:
                raise RuntimeError("ohne Zugangsdaten")
            return Ergebnis()

    class Engine:
        geschlossen = False

        def connect(self):
            return Verbindung()

        def dispose(self):
            self.geschlossen = True

    engine = Engine()
    monkeypatch.setattr(sqlalchemy, "create_engine", lambda *a, **k: engine)
    result = getattr(vor_push, funktion)("unused")
    assert engine.geschlossen
    if fehler:
        assert not result
    elif funktion == "_db_revisionen":
        assert result == {"head"}
    else:
        assert result is True


@pytest.mark.parametrize("ohne_tests", [False, True])
def test_nicht_bereiter_pruefstand_stoppt_vor_register_und_tests(monkeypatch, ohne_tests):
    import sys
    monkeypatch.setattr(sys, "argv", ["vor_push"] + (["--ohne-tests"] if ohne_tests else []))
    monkeypatch.setattr(vor_push, "_base_gueltig", lambda base: True)
    monkeypatch.setattr(vor_push, "konfliktdateien", lambda base: [])
    monkeypatch.setattr(vor_push, "_pruefstand_umgebung", lambda: "probe")
    monkeypatch.setattr(vor_push, "pruefe_pruefstand", lambda url, base: False)
    monkeypatch.setattr(vor_push, "pruefe_register", lambda base: pytest.fail("Register gestartet"))
    monkeypatch.setattr(vor_push, "betroffene_tests", lambda base: pytest.fail("Tests gestartet"))
    assert vor_push.main() == 1


def test_konfliktmarker_stoppt_vor_datenbank(monkeypatch):
    import sys
    monkeypatch.setattr(sys, "argv", ["vor_push"])
    monkeypatch.setattr(vor_push, "_base_gueltig", lambda base: True)
    monkeypatch.setattr(vor_push, "konfliktdateien", lambda base: ["datei"])
    monkeypatch.setattr(vor_push, "_pruefstand_umgebung", lambda: pytest.fail("Datenbank gestartet"))
    assert vor_push.main() == 1


def test_konfliktmarker_und_literal_unterscheiden(monkeypatch, tmp_path):
    monkeypatch.setattr(vor_push, "REPO", tmp_path)
    (tmp_path / "real.py").write_text("<<<<<<< branch\ncode\n=======\ncode\n>>>>>>> main\n")
    (tmp_path / "literal.py").write_text('x = "<<<<<<< branch"\ny = "======="\n')
    (tmp_path / "readme.md").write_text("Eine Ueberschrift\n=======\n")
    monkeypatch.setattr(vor_push, "_git", lambda *a: "" if "--diff-filter=U" in a else "real.py\nliteral.py\nreadme.md\n")
    assert vor_push.konfliktdateien("main") == ["real.py"]


def test_migration_erfasst_entfernte_tabelle_und_schemavertraege(monkeypatch, tmp_path):
    monkeypatch.setattr(vor_push, "REPO", tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "alembic" / "versions").mkdir(parents=True)
    (tmp_path / "alembic" / "versions" / "new.py").write_text("op.drop_table('bestellungen', schema='domain_einkauf')")
    (tmp_path / "tests" / "test_leser.py").write_text("TABLE = 'domain_einkauf.bestellungen'")
    (tmp_path / "tests" / "test_schema.py").write_text("")
    (tmp_path / "tests" / "test_frontend.py").write_text("")
    monkeypatch.setattr(vor_push, "_geaenderte_dateien", lambda base: ({"alembic/versions/new.py"}, set()))
    monkeypatch.setattr(vor_push, "_git", lambda *a: "")
    ausgewaehlt = vor_push.betroffene_tests("main")
    assert "tests/test_leser.py" in ausgewaehlt
    assert "tests/test_schema.py" in ausgewaehlt
    assert "tests/test_frontend.py" not in ausgewaehlt
    assert vor_push.BLOCK == 6


def test_dynamisches_ddl_verlangt_manuelle_vollpruefung(monkeypatch, tmp_path):
    monkeypatch.setattr(vor_push, "REPO", tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "alembic" / "versions").mkdir(parents=True)
    (tmp_path / "alembic" / "versions" / "new.py").write_text("op.drop_table(tabellenname)")
    monkeypatch.setattr(vor_push, "_geaenderte_dateien", lambda base: ({"alembic/versions/new.py"}, set()))
    monkeypatch.setattr(vor_push, "_git", lambda *a: "")
    with pytest.raises(RuntimeError, match="--volle-tests"):
        vor_push.betroffene_tests("main")


def test_ungueltige_base_stoppt_vor_datenbank(monkeypatch):
    import sys
    monkeypatch.setattr(sys, "argv", ["vor_push", "--base", "missing"])
    monkeypatch.setattr(vor_push, "_base_gueltig", lambda base: False)
    monkeypatch.setattr(vor_push, "_pruefstand_umgebung", lambda: pytest.fail("Datenbank gestartet"))
    assert vor_push.main() == 1


def test_unmerged_datei_ohne_marker_wird_gemeldet(monkeypatch, tmp_path):
    monkeypatch.setattr(vor_push, "REPO", tmp_path)
    (tmp_path / "konflikt.txt").write_text("bereits bereinigt, aber nicht vorgemerkt")
    monkeypatch.setattr(vor_push, "_git", lambda *a: "konflikt.txt\n")
    assert vor_push.konfliktdateien("main") == ["konflikt.txt"]


def test_vollmodus_prueft_alle_ausgewaehlten_tests_nach_sicherheitschecks(monkeypatch):
    import sys
    monkeypatch.setattr(sys, "argv", ["vor_push", "--volle-tests"])
    aufrufe = []
    monkeypatch.setattr(vor_push, "_base_gueltig", lambda base: aufrufe.append("base") or True)
    monkeypatch.setattr(vor_push, "konfliktdateien", lambda base: aufrufe.append("konflikte") or [])
    monkeypatch.setattr(vor_push, "_pruefstand_umgebung", lambda: aufrufe.append("url") or "probe")
    monkeypatch.setattr(vor_push, "pruefe_pruefstand", lambda url, base: aufrufe.append("stand") or True)
    monkeypatch.setattr(vor_push, "betroffene_tests", lambda base: pytest.fail("gezielte Auswahl im Vollmodus"))
    monkeypatch.setattr(vor_push, "alle_testdateien", lambda: ["tests/test_a.py", "tests/test_b.py"])
    monkeypatch.setattr(vor_push, "pruefe_register", lambda base: aufrufe.append("register") or [])
    monkeypatch.setattr(vor_push, "pruefe_tests", lambda dateien: aufrufe.append(dateien) or [])
    assert vor_push.main() == 0
    assert aufrufe == ["base", "konflikte", "url", "stand", "register", ["tests/test_a.py", "tests/test_b.py"]]


def test_vollmodus_ermittelt_nur_verfolgte_testdateien(monkeypatch, tmp_path):
    import subprocess
    monkeypatch.setattr(vor_push, "REPO", tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("")
    (tmp_path / "tests" / "test_untracked.py").write_text("")
    monkeypatch.setattr(vor_push.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, b"tests/test_a.py\0tests/helper.py\0"))
    assert vor_push.alle_testdateien() == ["tests/test_a.py"]


def test_die_register_aus_den_ci_befunden_sind_dabei():
    """Jeder Eintrag steht fuer eine CI-Runde, die schon einmal rot war."""
    namen = " ".join(name for name, _, _ in vor_push.REGISTER)
    for pflicht in ("Tabellenkatalog", "RLS-Inventar", "Pflichtstruktur", "Doc-Generatoren", "Improvement-Pipelines",
                    "Belegmasken-Versionen", "Maskenfamilien-Versionen", "Studio-Screen-Katalog"):
        assert pflicht in namen
    assert "tests/test_mask_endpoint_inventory.py" in vor_push.IMMER


def test_sperre_haelt_den_pruefstand_und_gibt_ihn_frei(tmp_path, monkeypatch):
    """24.11.2026: vor_push direkt aufgerufen baute den Pruefstand mitten in fremden Laeufen neu - jetzt gesperrt."""
    monkeypatch.setattr(vor_push, "SPERRE", tmp_path / "sperre.lock")
    monkeypatch.delenv("VALEO_PRUEFSTAND_SPERRE", raising=False)
    with vor_push._Sperre():
        assert vor_push.SPERRE.exists()
    assert not vor_push.SPERRE.exists()


def test_verwaiste_sperre_wird_uebernommen(tmp_path, monkeypatch):
    monkeypatch.setattr(vor_push, "SPERRE", tmp_path / "sperre.lock")
    monkeypatch.delenv("VALEO_PRUEFSTAND_SPERRE", raising=False)
    vor_push.SPERRE.write_text("999999999 anderswo")
    monkeypatch.setattr(vor_push, "_lebt", lambda pid: False)
    with vor_push._Sperre():
        assert vor_push.SPERRE.read_text().split()[0] != "999999999"


def test_vom_hook_gehaltene_sperre_wird_nicht_doppelt_genommen(tmp_path, monkeypatch):
    monkeypatch.setattr(vor_push, "SPERRE", tmp_path / "sperre.lock")
    monkeypatch.setenv("VALEO_PRUEFSTAND_SPERRE", "gehalten")
    vor_push.SPERRE.write_text("1 hook")
    with vor_push._Sperre():
        assert vor_push.SPERRE.read_text() == "1 hook"
    assert vor_push.SPERRE.exists()  # gehoert dem Hook
