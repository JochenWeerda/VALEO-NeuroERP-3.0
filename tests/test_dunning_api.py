"""
Tests für app/api/v1/endpoints/dunning.py

Abgedeckte Pfade:
  GET  /dunning/rules        — list_dunning_rules (DB-Pfad + Fallback)
  POST /dunning/rules        — create_dunning_rule (OK, Duplikat-Fehler, DB-Fehler)
  POST /dunning/process      — process_dunning (ruft seit 23.11.2026 den einen Mahnweg)
  POST /dunning/run          — run_dunning
  GET  /dunning              — list_dunnings
  PUT  /dunning/{id}/send    — send_dunning
  Berechnung: Zinsen, Gebühren, Gesamtbetrag, payment_deadline
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import dunning
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import register_domain_exception_handlers
from testgrenze import ersetze_mandant

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NOW = datetime(2026, 4, 24, 10, 0, tzinfo=timezone.utc)
TODAY = date.today()


def _rule_row(
    level: int = 1,
    days_min: int = 14,
    days_max: int | None = 29,
    fee: str = "5.00",
    fee_pct: str = "0.00",
    rate: str = "9.00",
    deadline: int = 14,
    block: bool = False,
    escalate: bool = False,
    active: bool = True,
    rule_id: str = "rule-1",
):
    return (
        rule_id, level, days_min, days_max,
        Decimal(fee), Decimal(fee_pct), Decimal(rate),
        deadline, block, escalate,
        f"Mahnung Stufe {level}: {{{{days_overdue}}}} Tage überfällig.",
        active, NOW, NOW,
    )


def _notice_row(
    notice_id: str = "notice-1",
    op_id: str = "op-1",
    debtor_id: str = "deb-1",
    level: int = 1,
    open_amount: str = "1000.00",
    fee: str = "5.00",
    interest: str = "2.47",
    total: str = "1007.47",
    status: str = "created",
):
    dunning_date = TODAY
    due_date = TODAY - timedelta(days=20)
    payment_deadline = TODAY + timedelta(days=14)
    return (
        notice_id, op_id, debtor_id, level,
        dunning_date, due_date,
        Decimal(open_amount), Decimal(fee), Decimal(interest), Decimal(total),
        payment_deadline, status,
        None,   # sent_date
        None,   # payment_date
        "Mahnung Stufe 1: 20 Tage überfällig.",
        NOW, NOW,
    )


# ---------------------------------------------------------------------------
# Fake DB
# ---------------------------------------------------------------------------

class _FakeResult:
    def __init__(self, *, fetchone=None, fetchall=None, rowcount: int = 0):
        self._one = fetchone
        self._all = list(fetchall or [])
        self.rowcount = rowcount

    def fetchone(self):
        return self._one

    def fetchall(self):
        return list(self._all)

    def mappings(self):
        return self

    def first(self):
        return self._one


def _notice_mapping(notice_id: str = "notice-1", status: str = "created") -> dict:
    """Die Zeile, die ``send_notice`` vor dem Versand liest."""
    return {"id": notice_id, "debtor_id": "deb-1", "dunning_level": 1, "open_amount": Decimal("1000.00"),
            "dunning_fee": Decimal("5.00"), "interest": Decimal("2.47"), "total_amount": Decimal("1007.47"),
            "payment_deadline": TODAY + timedelta(days=14), "status": status, "rechnungsnr": "RE-1",
            "kunde_id": "deb-1", "kunde_name": "Hof Probe"}


class FakeDb:
    def __init__(self):
        self.commit_count = 0
        self.rollback_count = 0
        self._rules: list = []
        self._notices: list = []
        self._ops: list = []
        self._raise_on_execute: Exception | None = None
        self._exec_results: list[_FakeResult] = []

    def _next_result(self) -> _FakeResult:
        if self._exec_results:
            return self._exec_results.pop(0)
        return _FakeResult()

    def execute(self, query, params=None):
        if self._raise_on_execute:
            raise self._raise_on_execute
        return self._next_result()

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1

    def close(self):
        pass


def _make_app(db: FakeDb) -> TestClient:
    app = FastAPI()
    ersetze_mandant(app)
    app.include_router(dunning.router)  # router already has prefix="/dunning"
    register_domain_exception_handlers(app)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: {"sub": "buchhalter", "roles": ["FINANCE_ADMIN"]}
    # Der Mandant kommt aus dem Header (seit 08.10.2026), nicht aus Query/Rumpf.
    return TestClient(app, headers={"X-Tenant-ID": "system"})


# ---------------------------------------------------------------------------
# GET /dunning/rules
# ---------------------------------------------------------------------------

class TestListDunningRules:
    def test_returns_db_rules(self):
        db = FakeDb()
        db._exec_results = [_FakeResult(fetchall=[_rule_row(1), _rule_row(2, days_min=30)])]
        client = _make_app(db)
        r = client.get("/dunning/rules")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2
        assert data[0]["level"] == 1
        assert data[1]["level"] == 2

    def test_db_fehler_erfindet_keine_regeln(self):
        """Bis 08.10.2026 kamen hier drei erfundene Mahnstufen mit Gebuehren zurueck."""
        from sqlalchemy.exc import OperationalError

        db = FakeDb()
        db._raise_on_execute = OperationalError("SELECT", {}, Exception("table missing"))
        client = _make_app(db)
        r = client.get("/dunning/rules")
        assert r.status_code == 503
        assert db.rollback_count >= 1

    def test_mahnlauf_mahnt_nicht_mit_erfundenen_regeln(self):
        from sqlalchemy.exc import OperationalError

        db = FakeDb()
        db._raise_on_execute = OperationalError("SELECT", {}, Exception("table missing"))
        r = _make_app(db).post("/dunning/process", json={})
        assert r.status_code == 503
        assert db.commit_count == 0

    def test_db_fehler_ist_keine_leere_mahnliste(self):
        from sqlalchemy.exc import OperationalError

        db = FakeDb()
        db._raise_on_execute = OperationalError("SELECT", {}, Exception("table missing"))
        assert _make_app(db).get("/dunning").status_code == 503

    def test_active_only_false_passes_param(self):
        db = FakeDb()
        db._exec_results = [_FakeResult(fetchall=[_rule_row(active=True), _rule_row(2, active=False)])]
        client = _make_app(db)
        r = client.get("/dunning/rules?active_only=false")
        assert r.status_code == 200
        assert len(r.json()) == 2


# ---------------------------------------------------------------------------
# POST /dunning/rules
# ---------------------------------------------------------------------------

class TestCreateDunningRule:
    def _payload(self, level: int = 1) -> dict:
        return {
            "level": level,
            "days_overdue_min": 14,
            "days_overdue_max": 29,
            "fee_amount": "5.00",
            "fee_percentage": "0.00",
            "interest_rate": "9.00",
            "payment_deadline_days": 14,
            "block_customer": False,
            "escalate_to_collection": False,
            "description_template": "Mahnung {{days_overdue}}",
            "active": True,
        }

    def test_create_ok(self):
        db = FakeDb()
        # check_query → no existing; insert → returning row
        db._exec_results = [
            _FakeResult(fetchone=None),
            _FakeResult(fetchone=_rule_row()),
        ]
        client = _make_app(db)
        r = client.post("/dunning/rules", json=self._payload())
        assert r.status_code == 201
        assert r.json()["level"] == 1
        assert db.commit_count == 1

    def test_duplicate_returns_400(self):
        db = FakeDb()
        db._exec_results = [_FakeResult(fetchone=("existing-id",))]
        client = _make_app(db)
        r = client.post("/dunning/rules", json=self._payload())
        assert r.status_code == 400
        assert "already exists" in r.json()["detail"]

    def test_db_error_returns_500(self):
        db = FakeDb()
        db._raise_on_execute = RuntimeError("insert failed")
        client = _make_app(db)
        r = client.post("/dunning/rules", json=self._payload())
        assert r.status_code == 500
        assert db.rollback_count == 1


# ---------------------------------------------------------------------------
# GET /dunning
# ---------------------------------------------------------------------------

class TestListDunnings:
    def test_list_returns_notices(self):
        db = FakeDb()
        db._exec_results = [_FakeResult(fetchall=[_notice_row(), _notice_row("notice-2")])]
        client = _make_app(db)
        r = client.get("/dunning")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_list_empty(self):
        db = FakeDb()
        db._exec_results = [_FakeResult(fetchall=[])]
        client = _make_app(db)
        r = client.get("/dunning")
        assert r.status_code == 200
        assert r.json() == []


# ---------------------------------------------------------------------------
# PUT /dunning/{id}/send
# ---------------------------------------------------------------------------

class TestSendDunning:
    def test_send_ok(self, monkeypatch):
        from app.api.v1.endpoints import dunning as modul

        db = FakeDb()
        # Postversand: der Mailweg laeuft echt in tests/test_versandwege_vertrag.py.
        db._exec_results = [
            _FakeResult(fetchone=_notice_mapping("n-1")),
            _FakeResult(fetchone=_notice_row(notice_id="n-1", status="sent")),
        ]
        archiviert: list[tuple[str, int]] = []
        # Der Archiveintrag laeuft in derselben Transaktion: vor dem Commit.
        monkeypatch.setattr(modul, "register_artifact",
                            lambda *a, **k: archiviert.append((k["doc_type"], db.commit_count)) or "art-1")
        client = _make_app(db)
        r = client.put("/dunning/n-1/send", params={"versand_art": "post"})
        assert r.status_code == 200
        assert archiviert == [("dunning_notice", 0)]
        assert db.commit_count == 1

    def test_ohne_archiveintrag_kein_versand(self, monkeypatch):
        from app.api.v1.endpoints import dunning as modul
        from app.core.gobd_artifact import GobdArtifactError

        db = FakeDb()
        db._exec_results = [_FakeResult(fetchone=_notice_mapping("n-1")),
                            _FakeResult(fetchone=_notice_row(notice_id="n-1", status="sent"))]

        def scheitert(*_a, **_k):
            raise GobdArtifactError("Archiv nicht erreichbar")

        monkeypatch.setattr(modul, "register_artifact", scheitert)
        r = _make_app(db).put("/dunning/n-1/send", params={"versand_art": "post"})
        assert r.status_code == 500
        assert db.commit_count == 0
        assert db.rollback_count >= 1

    def test_send_not_found_returns_404(self):
        db = FakeDb()
        db._exec_results = [_FakeResult(fetchone=None)]
        client = _make_app(db)
        r = client.put("/dunning/missing/send")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Berechnungslogik (unit, kein HTTP)
# ---------------------------------------------------------------------------

class TestMoneyHelper:
    def test_money_rounds_to_two_decimals(self):
        from app.api.v1.endpoints.dunning import _money
        assert _money(Decimal("1.999")) == Decimal("2.00")
        assert _money(Decimal("0.001")) == Decimal("0.00")
        assert _money(Decimal("5.006")) == Decimal("5.01")


# ---------------------------------------------------------------------------
# Mandant aus dem Kontext (08.10.2026)
# ---------------------------------------------------------------------------

class _MandantenSpion(FakeDb):
    def __init__(self):
        super().__init__()
        self.mandanten: list[str] = []

    def execute(self, query, params=None):
        if params and "tenant_id" in params:
            self.mandanten.append(params["tenant_id"])
        return super().execute(query, params)


class TestMandantAusDemKontext:
    def test_query_parameter_waehlt_keinen_mandanten(self):
        db = _MandantenSpion()
        client = _make_app(db)
        client.get("/dunning/rules?tenant_id=fremd", headers={"X-Tenant-ID": "haus-a"})
        client.get("/dunning?tenant_id=fremd", headers={"X-Tenant-ID": "haus-a"})
        assert db.mandanten and set(db.mandanten) == {"haus-a"}

    def test_rumpf_waehlt_keinen_mandanten(self, monkeypatch):
        from app.services.finance_dunning_service import FinanceDunningService

        db = _MandantenSpion()
        # Der Mahnweg selbst ist in tests/test_ein_mahnweg.py echt geprueft; hier zaehlt nur der Mandant.
        monkeypatch.setattr(FinanceDunningService, "run_dunning",
                            lambda self, **_: db.mandanten.append(self.tenant_id) or {"erzeugt": 0, "mahnungen": []})
        client = _make_app(db)
        client.post("/dunning/process", json={"tenant_id": "fremd"}, headers={"X-Tenant-ID": "haus-a"})
        client.post("/dunning/run", json={"tenant_id": "fremd", "as_of_date": "2026-10-08"},
                    headers={"X-Tenant-ID": "haus-a"})
        assert db.mandanten and set(db.mandanten) == {"haus-a"}

    def test_kein_weg_nimmt_den_mandanten_aus_query_oder_rumpf(self):
        from pathlib import Path

        quelle = Path("app/api/v1/endpoints/dunning.py").read_text(encoding="utf-8-sig")
        assert 'tenant_id: str = Query(' not in quelle
        assert "request.tenant_id" not in quelle
