"""Autonomieentscheidungen mit simulierter Datenbankgrenze, ohne Datenbankserver."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.exceptions import ValidationFailedError
from app.services import agent_autonomie as autonomy


NOW = datetime(2026, 11, 13, tzinfo=timezone.utc)
CAPABILITY = "sales.gutschrift.buchen"


class Result:
    def __init__(self, value):
        self.value = value

    def mappings(self):
        return self

    def first(self):
        return self.value

    def fetchall(self):
        return self.value


class Boundary:
    """Nur gespeicherte Fakten und Schreibaufrufe; keine fachlichen Entscheidungen."""

    def __init__(self, *, counts=None, test=("test_bestanden", NOW), approved=True,
                 delegated=True, limit=Decimal("1000")):
        self.counts, self.test, self.approved = counts or {}, test, approved
        self.delegated, self.limit = delegated, limit
        self.writes = []

    def execute(self, statement, params):
        sql = str(statement)
        if "GROUP BY kind" in sql:
            return Result(list(self.counts.items()))
        if "ORDER BY recorded_at DESC LIMIT 1" in sql:
            return Result(self.test)
        if "FROM domain_shared.agent_policy_approvals" in sql:
            return Result({"id": "approval"} if self.approved else None)
        if "FROM domain_shared.agent_delegations" in sql:
            return Result({"id": "delegation", "max_brutto": self.limit, "valid_until": None}
                          if self.delegated else None)
        if sql.startswith("INSERT") or sql.startswith("UPDATE"):
            self.writes.append((sql, params))
            return SimpleNamespace(rowcount=1)
        raise AssertionError(f"Unerwartete Datenbankabfrage: {sql}")


@pytest.mark.parametrize("counts,violation", [
    ({"ausgefuehrt": 19, "korrigiert": 1}, None),
    ({"ausgefuehrt": 19, "korrigiert": 2}, "Startphase"),
    ({"ausgefuehrt": 100, "korrigiert": 2}, None),
    ({"ausgefuehrt": 100, "korrigiert": 3}, "Fehlerquote"),
    ({"ausgefuehrt": 20, "befund": 2}, None),
    ({"ausgefuehrt": 20, "befund": 3}, "Befundquote"),
    ({"ausgefuehrt": 9, "einwand": 1}, None),
    ({"ausgefuehrt": 8, "einwand": 2}, "Einwandquote"),
])
def test_qualitaetsgrenzen_mit_tatsaechlicher_politik(counts, violation):
    q = autonomy.qualitaet(Boundary(counts=counts), "tenant", "agent", CAPABILITY, jetzt=NOW)
    assert q.im_rahmen is (violation is None)
    if violation:
        assert any(violation in v for v in q.verletzungen)


@pytest.mark.parametrize("test,expected", [
    (("test_bestanden", NOW - timedelta(days=30)), None),
    (("test_bestanden", NOW - timedelta(days=30, seconds=1)), "veraltet"),
    (("test_fehlgeschlagen", NOW), "fehlgeschlagen"),
    (None, "Kein Testnachweis"),
])
def test_testnachweis_und_exakte_altersgrenze(test, expected):
    q = autonomy.qualitaet(Boundary(test=test), "tenant", "agent", CAPABILITY, jetzt=NOW)
    assert q.im_rahmen is (expected is None)
    if expected:
        assert any(expected in v for v in q.verletzungen)


@pytest.mark.parametrize("case,expected,reason", [
    ("ok", "autonom", None),
    ("policy", "freigabe", "nicht fachlich freigegeben"),
    ("delegation", "freigabe", "Keine gueltige Delegation"),
    ("limit_equal", "autonom", None),
    ("limit_over", "freigabe", "delegierten Grenze"),
    ("policy_limit", "freigabe", "Politikgrenze"),
    ("missing_test", "freigabe", "Kein Testnachweis"),
    ("risk", "freigabe", "Risiko-Engine"),
    ("objection", "freigabe", "Einwand Pruefagent"),
    ("failed_check", "abgelehnt", "Fachpruefung"),
])
def test_entscheidung_und_anzeige_aus_denselben_fakten(case, expected, reason):
    # Ein frischer Nachweis relativ zur echten Laufzeit vermeidet einen datumsabhaengigen Test.
    db = Boundary(test=None if case == "missing_test" else ("test_bestanden", datetime.now(timezone.utc)),
                  approved=case != "policy", delegated=case != "delegation",
                  limit=Decimal("2000") if case == "policy_limit" else Decimal("100"))
    risk = SimpleNamespace(risiko="R3" if case == "risk" else "R2", zweitfreigabe=case == "risk", grund="Pruefung")
    decision = autonomy.entscheide(db, "tenant", agent_id="agent", faehigkeit=CAPABILITY, vorgang="doc",
        brutto=Decimal("1000.01") if case == "policy_limit" else
               (Decimal("100.01") if case == "limit_over" else Decimal("100")),
        fachpruefung="ungueltig" if case == "failed_check" else None, risiko=risk,
        einwaende=["Plausibilitaet"] if case == "objection" else [], protokoll="keins")
    assert decision.ergebnis == expected
    if reason:
        assert any(reason in item for item in decision.gruende)
    if case in {"ok", "policy", "delegation", "missing_test"}:
        assert autonomy.vertrauen(db, "tenant", "agent", CAPABILITY)["stufe"] == (
            "A2" if case == "ok" else "A1" if case == "missing_test" else "A0")


@pytest.mark.parametrize("user", [
    {"sub": "claude-code", "roles": ["GESCHAEFTSFUEHRUNG"]},
    {"sub": "person", "roles": ["FINANCE_BEARBEITEN"]},
    {"sub": "agent", "roles": ["GESCHAEFTSFUEHRUNG"], "raw": {"identity_type": "agent"}},
])
def test_politikfreigabe_verlangt_unabhaengige_berechtigte_person(user):
    db = Boundary(approved=False)
    with pytest.raises(ValidationFailedError):
        autonomy.gib_politik_frei(db, "tenant", user, "Fachlich geprueft und freigegeben")
    assert not db.writes


def test_kontexte_werden_auch_nach_ausnahme_verschachtelt_zurueckgesetzt():
    assert autonomy._AGENT.get() is None and not autonomy._EINZELFREIGABEN.get()
    with autonomy.als_agent("outer"), autonomy.menschlich_freigegeben("doc-a"):
        with pytest.raises(RuntimeError):
            with autonomy.als_agent("inner"), autonomy.menschlich_freigegeben("doc-b"):
                assert autonomy.handelnder_agent() == "inner"
                assert autonomy._EINZELFREIGABEN.get() == {"doc-a", "doc-b"}
                raise RuntimeError("abgebrochen")
        assert autonomy.handelnder_agent() == "outer"
        assert autonomy._EINZELFREIGABEN.get() == {"doc-a"}
    assert autonomy._AGENT.get() is None and not autonomy._EINZELFREIGABEN.get()
