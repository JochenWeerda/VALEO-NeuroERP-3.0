"""Eine Buchungsperiode hat einen Zustand.

Drei Vokabulare standen in derselben Spalte: Die Maske prüft
`OPEN|CLOSED|ADJUSTING`, `close_period` schrieb `closed`, `reopen_period` schrieb
`offen`. Sieben Buchungswege verglichen jeder für sich `status != "OPEN"`.

Drei Folgen:

1. **Die Wiedereröffnung wirkte nicht.** Sie verlangte einen Grund,
   protokollierte ihn — und setzte `offen`. Die Wächter lasen `offen != OPEN`
   und sperrten weiter.
2. **`ADJUSTING` sperrte wie `CLOSED`** und war damit bedeutungslos.
3. **Ein Lesefehler schaltete die Sperre ab.** `check_period_open` endete mit
   `except Exception: pass  # allow through`.

Und: `/finance/closing/lock` und `/closing/run` meldeten bei jedem unerwarteten
Fehler Erfolg über einen Rückfall auf `domain_erp.accounting_periods` — ein
Schema, das es in keinem Migrationsstand gibt.

GoBD: Unveränderbarkeit (Rz. 107 ff.) und Nachvollziehbarkeit (Rz. 30 ff.).

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank. Die Testzeilen
tragen eigene Mandantenkennungen und werden hinterher entfernt.
"""

from __future__ import annotations

import os
import re
import uuid
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[1]

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe",
    ),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS = f"per-{uuid.uuid4().hex[:6]}"
PERIODE = "2026-07"
TABELLE = "public.finance_accounting_periods"


# 1 -- Das Woerterbuch ist eins ----------------------------------------------

@pytest.mark.unit
def test_das_woerterbuch_steht_an_einer_stelle():
    from app.core import finance_periods

    assert finance_periods.ZUSTAENDE == ("OPEN", "CLOSED", "ADJUSTING")
    assert finance_periods.SPERRT == frozenset({"CLOSED"})


@pytest.mark.unit
@pytest.mark.parametrize(
    "gelesen,erwartet",
    [
        ("OPEN", False),
        ("ADJUSTING", False),
        ("CLOSED", True),
        # Die Altschreibweisen, die vor dem 01.10.2026 geschrieben wurden.
        ("closed", True),
        ("geschlossen", True),
        ("offen", False),
        ("open", False),
        # Unbekanntes sperrt: Eine Periode, deren Zustand niemand benennen kann,
        # ist kein Freibrief zum Buchen.
        ("IRGENDWAS", True),
        ("", True),
    ],
)
def test_sperrt_entscheidet_nach_dem_woerterbuch(gelesen, erwartet):
    from app.core import finance_periods

    assert finance_periods.sperrt(gelesen) is erwartet


@pytest.mark.unit
def test_keine_zeile_heisst_offen():
    """Perioden entstehen beim ersten Abschluss. Eine nie angelegte Periode ist
    nicht abgeschlossen."""
    from app.core import finance_periods

    assert finance_periods.sperrt(None) is False


@pytest.mark.unit
def test_kein_waechter_vergleicht_mehr_selbst():
    """Sieben Stellen verglichen `status != "OPEN"` jede fuer sich. Kommt eine
    achte dazu, soll dieser Vertrag sie finden."""
    eigene = re.compile(r'!=\s*"OPEN"|!=\s*\'OPEN\'')
    funde = [
        str(pfad.relative_to(WURZEL))
        for verzeichnis in ("app", "modules")
        for pfad in (WURZEL / verzeichnis).rglob("*.py")
        if pfad.name != "finance_periods.py"
        and eigene.search(pfad.read_text(encoding="utf-8", errors="ignore"))
    ]
    assert not funde, (
        "Periodenzustand wird wieder an mehreren Stellen verglichen; "
        "gepruefft wird über app/core/finance_periods.py: " + ", ".join(funde)
    )


@pytest.mark.unit
def test_der_rueckfall_der_erfolg_meldete_ist_weg():
    quelle = (WURZEL / "app/api/v1/endpoints/finance_actions.py").read_text(
        encoding="utf-8"
    )
    assert "_legacy_close_accounting_period" not in quelle
    # Nur die Abfrage zaehlt, nicht der erklaerende Kommentar.
    assert not re.search(r"UPDATE\s+domain_erp\.accounting_periods", quelle, re.I)


@pytest.mark.unit
def test_ein_nicht_feststellbarer_zustand_laesst_nicht_durch():
    """`check_period_open` endete mit `except Exception: pass  # allow through`."""
    quelle = (WURZEL / "app/services/finance_transaction_service.py").read_text(
        encoding="utf-8"
    )
    assert "allow through" not in quelle
    assert "nicht feststellbar" in quelle


# 2 -- Gegen die Datenbank ----------------------------------------------------

@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            bedingung = conn.execute(
                text(
                    "SELECT conname FROM pg_constraint "
                    "WHERE conname = 'ck_finance_accounting_periods_status'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not bedingung:
        pytest.skip("Migration periode_statuswoerterbuch_20261001 nicht angewandt")
    return motor


@pytest.fixture(autouse=True)
def eigene_zeilen_weg(engine):
    from sqlalchemy import text

    yield
    with engine.begin() as v:
        v.execute(
            text(f"DELETE FROM {TABELLE} WHERE tenant_id = :t"), {"t": HAUS}
        )


def _periode_setzen(engine, zustand: str) -> None:
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {TABELLE} "
                "(id, tenant_id, period, status, start_date, end_date) "
                "VALUES (:id, :t, :p, :s, '2026-07-01', '2026-07-31') "
                "ON CONFLICT (tenant_id, period) DO UPDATE SET status = EXCLUDED.status"
            ),
            {"id": str(uuid.uuid4()), "t": HAUS, "p": PERIODE, "s": zustand},
        )


@pytest.mark.integration
def test_die_datenbank_haelt_das_woerterbuch(engine):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    f"INSERT INTO {TABELLE} "
                    "(id, tenant_id, period, status, start_date, end_date) "
                    "VALUES (:id, :t, :p, 'offen', '2026-07-01', '2026-07-31')"
                ),
                {"id": str(uuid.uuid4()), "t": HAUS, "p": PERIODE},
            )


@pytest.mark.integration
@pytest.mark.parametrize(
    "zustand,sperrt",
    [("OPEN", False), ("ADJUSTING", False), ("CLOSED", True)],
)
def test_gesperrter_zustand_liest_die_periode(engine, zustand, sperrt):
    from sqlalchemy.orm import Session

    from app.core import finance_periods

    _periode_setzen(engine, zustand)
    with Session(engine) as db:
        ergebnis = finance_periods.gesperrter_zustand(db, HAUS, PERIODE)
    assert (ergebnis is not None) is sperrt
    if sperrt:
        assert ergebnis == "CLOSED"


@pytest.mark.integration
def test_eine_nie_angelegte_periode_ist_offen(engine):
    from sqlalchemy.orm import Session

    from app.core import finance_periods

    with Session(engine) as db:
        assert finance_periods.gesperrter_zustand(db, HAUS, "1999-01") is None


# 3 -- Abschluss und Wiedereroeffnung ----------------------------------------

@pytest.mark.integration
def test_abschluss_und_wiedereroeffnung_wirken(engine):
    """Vorher setzte die Wiedereroeffnung `offen`, und die Waechter sperrten
    weiter. Die dokumentierte Wiedereroeffnung existierte nur auf dem Papier."""
    from sqlalchemy import text
    from sqlalchemy.orm import Session

    from app.core import finance_periods
    from app.services.finance_period_service import FinancePeriodService

    with Session(engine) as db:
        dienst = FinancePeriodService(db, HAUS)
        dienst.close_period(PERIODE, bediener="pruefer", force=True)

        with engine.connect() as conn:
            zustand = conn.execute(
                text(f"SELECT status FROM {TABELLE} WHERE tenant_id = :t AND period = :p"),
                {"t": HAUS, "p": PERIODE},
            ).scalar()
        assert zustand == "CLOSED"
        assert finance_periods.gesperrter_zustand(db, HAUS, PERIODE) == "CLOSED"

        dienst.reopen_period(PERIODE, grund="Nachbuchung Inventur", bediener="pruefer")

        with engine.connect() as conn:
            zeile = conn.execute(
                text(
                    f"SELECT status, closed_at, metadata FROM {TABELLE} "
                    "WHERE tenant_id = :t AND period = :p"
                ),
                {"t": HAUS, "p": PERIODE},
            ).mappings().one()
        assert zeile["status"] == "OPEN"
        assert zeile["closed_at"] is None
        # Der Grund bleibt protokolliert — das ist der GoBD-Teil.
        assert zeile["metadata"]["reopen_grund"] == "Nachbuchung Inventur"
        assert finance_periods.gesperrter_zustand(db, HAUS, PERIODE) is None


@pytest.mark.integration
def test_doppelter_abschluss_wird_abgewiesen(engine):
    from sqlalchemy.orm import Session

    from app.services.finance_period_service import FinancePeriodService, PeriodError

    with Session(engine) as db:
        dienst = FinancePeriodService(db, HAUS)
        dienst.close_period(PERIODE, bediener="pruefer", force=True)
        with pytest.raises(PeriodError):
            dienst.close_period(PERIODE, bediener="pruefer", force=True)


@pytest.mark.integration
def test_wiedereroeffnung_ohne_grund_wird_abgewiesen(engine):
    from sqlalchemy.orm import Session

    from app.services.finance_period_service import FinancePeriodService, PeriodError

    with Session(engine) as db:
        dienst = FinancePeriodService(db, HAUS)
        dienst.close_period(PERIODE, bediener="pruefer", force=True)
        with pytest.raises(PeriodError):
            dienst.reopen_period(PERIODE, grund="   ", bediener="pruefer")


# 4 -- Der Buchungsweg sperrt wirklich ---------------------------------------

@pytest.mark.integration
def test_buchung_in_geschlossene_periode_wird_abgewiesen(engine):
    from sqlalchemy.orm import Session

    from app.core.exceptions import ValidationFailedError
    from app.services.finance_transaction_service import FinanceTransactionService

    _periode_setzen(engine, "CLOSED")
    with Session(engine) as db:
        dienst = FinanceTransactionService(db, HAUS)
        with pytest.raises(ValidationFailedError) as fehler:
            dienst.check_period_open(PERIODE)
    assert "CLOSED" in str(fehler.value)


@pytest.mark.integration
@pytest.mark.parametrize("zustand", ["OPEN", "ADJUSTING"])
def test_buchung_in_offene_und_abschlussperiode_ist_erlaubt(engine, zustand):
    from sqlalchemy.orm import Session

    from app.services.finance_transaction_service import FinanceTransactionService

    _periode_setzen(engine, zustand)
    with Session(engine) as db:
        FinanceTransactionService(db, HAUS).check_period_open(PERIODE)


@pytest.mark.integration
def test_nicht_lesbarer_zustand_weist_die_buchung_ab(engine):
    """Die Spalte, nach der gelesen wird, wird kurzzeitig umbenannt.

    Vorher liess `except Exception: pass  # allow through` die Buchung durch —
    die Periodensperre entfiel bei einem Lesefehler **ganz**.
    """
    from sqlalchemy import text
    from sqlalchemy.orm import Session

    from app.core.exceptions import ValidationFailedError
    from app.services.finance_transaction_service import FinanceTransactionService

    _periode_setzen(engine, "CLOSED")
    with engine.begin() as v:
        v.execute(text(f"ALTER TABLE {TABELLE} RENAME COLUMN status TO status_weg"))
    try:
        with Session(engine) as db:
            with pytest.raises(ValidationFailedError) as fehler:
                FinanceTransactionService(db, HAUS).check_period_open(PERIODE)
        assert "nicht feststellbar" in str(fehler.value)
    finally:
        with engine.begin() as v:
            v.execute(text(f"ALTER TABLE {TABELLE} RENAME COLUMN status_weg TO status"))
