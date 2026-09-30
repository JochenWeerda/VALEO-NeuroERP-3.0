"""Was der Waechter fuer eine tote Transaktion haelt — und was nicht.

Diese Tests brauchen keine Datenbank: Geprueft wird die Erkennung, nicht das
Verhalten von Postgres. Jeder Fall ist ein kleines Stueck Python, das genau
eine Unterscheidung festhaelt.

Die Unterscheidungen sind nicht erfunden, sondern aus der Arbeit am 29./30.09.:

- Der **Fund**: ``except`` ohne Rollback, danach wird weitergearbeitet. Genau
  so lief der Loeschweg nach Art. 17 DSGVO ins Leere.
- Der **falsche Fund**, den die erste Fassung des Skripts produzierte: Der
  Savepoint liegt *innerhalb* des ``try``. Das ist der richtige Weg und wurde
  trotzdem gemeldet.
- Der **harmlose Fall**: Nach dem ``except`` passiert nichts mehr. Die Anfrage
  endet, die Sitzung wird geschlossen, niemand sieht ein Scheinergebnis.
"""

from __future__ import annotations

import ast
import pathlib
import sys

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from check_dead_transactions import _Besuch  # noqa: E402


def _funde(quelle: str) -> list[dict]:
    """Die Fundstellen eines Codeausschnitts."""
    besuch = _Besuch(pathlib.Path(__file__).resolve().parents[1] / "app" / "x.py")
    besuch.visit(ast.parse(quelle))
    return besuch.funde


# ── Das Muster selbst ──────────────────────────────────────────────────


def test_geschluckter_fehler_mit_weiterarbeit_ist_ein_fund() -> None:
    """Der Fall, der die Loeschung nach Art. 17 wertlos machte."""
    funde = _funde(
        """
def loeschen(db):
    try:
        db.execute("DELETE FROM a")
    except Exception as fehler:
        protokoll.append({"error": str(fehler)})
    db.execute("UPDATE antrag SET status = 'fertig'")
    db.commit()
"""
    )
    assert len(funde) == 1
    assert "Zeile" in funde[0]["grund"]


def test_geschluckter_fehler_in_der_schleife_ist_ein_fund() -> None:
    """Der naechste Durchlauf faellt mit — ohne dass jemand es erfaehrt."""
    funde = _funde(
        """
def loeschen(db, schritte):
    for tabelle, sql in schritte:
        try:
            db.execute(sql)
        except Exception as fehler:
            protokoll.append({"table": tabelle, "error": str(fehler)})
"""
    )
    assert len(funde) == 1
    assert "Schleife" in funde[0]["grund"]


# ── Was kein Fund ist ──────────────────────────────────────────────────


def test_savepoint_innerhalb_des_try_ist_kein_fund() -> None:
    """Der richtige Weg. Die erste Fassung des Skripts meldete ihn faelschlich."""
    funde = _funde(
        """
def loeschen(db, schritte):
    for tabelle, sql in schritte:
        try:
            with db.begin_nested():
                db.execute(sql)
        except Exception as fehler:
            protokoll.append({"table": tabelle, "error": str(fehler)})
"""
    )
    assert funde == []


def test_rollback_ist_kein_fund() -> None:
    funde = _funde(
        """
def buchen(db):
    try:
        db.execute("INSERT INTO buchung VALUES (1)")
        db.commit()
    except Exception:
        db.rollback()
    db.execute("SELECT 1")
"""
    )
    assert funde == []


def test_weitergegebener_fehler_ist_kein_fund() -> None:
    funde = _funde(
        """
def buchen(db):
    try:
        db.execute("INSERT INTO buchung VALUES (1)")
    except Exception:
        raise
    db.commit()
"""
    )
    assert funde == []


def test_nutzersichtbarer_fehler_ist_kein_fund() -> None:
    """Wer eine HTTPException wirft, liefert kein Scheinergebnis."""
    funde = _funde(
        """
def buchen(db):
    try:
        db.execute("INSERT INTO buchung VALUES (1)")
    except Exception:
        raise HTTPException(status_code=409, detail="schon gebucht")
    db.commit()
"""
    )
    assert funde == []


def test_ohne_weiterarbeit_ist_kein_fund() -> None:
    """Nach dem except passiert nichts mehr — die Sitzung wird geschlossen."""
    funde = _funde(
        """
def lesen(db):
    try:
        return db.execute("SELECT 1").scalar()
    except Exception:
        return None
"""
    )
    assert funde == []


def test_ohne_datenbankanweisung_ist_kein_fund() -> None:
    """Ein try um etwas anderes hat mit Transaktionen nichts zu tun."""
    funde = _funde(
        """
def rechnen(db):
    try:
        wert = 1 / 0
    except ZeroDivisionError:
        wert = 0
    db.execute("SELECT 1")
    return wert
"""
    )
    assert funde == []


# ── Mehrere Zweige ────────────────────────────────────────────────────


def test_nur_der_unbehandelte_zweig_zaehlt() -> None:
    """Zwei except-Zweige, einer sauber — gemeldet wird nur der andere."""
    funde = _funde(
        """
def loeschen(db):
    try:
        db.execute("DELETE FROM a")
    except ProgrammingError:
        db.rollback()
        raise
    except Exception as fehler:
        protokoll.append({"error": str(fehler)})
    db.commit()
"""
    )
    assert len(funde) == 1
    assert funde[0]["ausnahme"] == "Exception"


def test_die_fundstelle_nennt_zeile_und_ausnahme() -> None:
    """Ohne Zeile und Ausnahmeart ist eine Fundliste nicht abarbeitbar."""
    funde = _funde(
        """
def loeschen(db):
    try:
        db.execute("DELETE FROM a")
    except ValueError:
        pass
    db.commit()
"""
    )
    assert len(funde) == 1
    assert funde[0]["ausnahme"] == "ValueError"
    assert funde[0]["zeile"] == 5
