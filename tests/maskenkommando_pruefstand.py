"""Gemeinsamer Pruefrahmen der Kommando-Wege von Masken (MASK-COMMANDS-ROLLOUT-20261019).

Jede Maske mit Kommando-Endpunkt beweist dieselben Eigenschaften gegen die Pruefstand-Datenbank: Trockenlauf
schreibt nichts, Wiederholung wirkt einmal, fremder Mandant findet nichts, Urheber kommt aus der geprueften
Identitaet. Dieser Rahmen liefert dafuer die Anwendung mit **umschaltbarer** Identitaet (zwei Personen fuer
Vier-Augen-Pruefungen) und den Mandanten aus dem Kopf — ausdrueckliche Testgrenze wie ``tests/testgrenze.py``.
Anmeldung und Mandantentrennung selbst pruefen die Identitaetsvertraege.

    from maskenkommando_pruefstand import Pruefstand
    ps = Pruefstand("bbt", tabellen=("domain_finance.billing_batches", ...))
    engine, client, haeuser = ps.fixtures()   # in Modulebene als Fixtures registrieren
"""
from __future__ import annotations

import os
import uuid
from typing import Any

import pytest
from fastapi import Request  # Modulebene: FastAPI loest die Annotation hier auf

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)

#: Spuren der Laufzeit (Audit, Ereignis), die jede Maskenaktion hinterlaesst.
RUNTIME_TABELLEN = ("domain_crm.crm_action_audit_log", "public.outbox_events")


class Identitaet:
    """Die geprueften Personen des Tests; ``als(...)`` wechselt, wer die naechste Anfrage stellt."""

    def __init__(self) -> None:
        self.sub = "pruefer-anna"
        self.name = "anna.pruefer"
        self.roles: list[str] = []

    def als(self, sub: str, *roles: str, name: str | None = None) -> "Identitaet":
        self.sub, self.name, self.roles = sub, name or sub, list(roles)
        return self

    def nutzer(self) -> dict[str, Any]:
        return {"sub": self.sub, "name": self.name, "roles": list(self.roles),
                "raw": {"sub": self.sub, "preferred_username": self.name}}


class Pruefstand:
    def __init__(self, kuerzel: str, *, tabellen: tuple[str, ...], probe_sql: str) -> None:
        self.haus_a = f"{kuerzel}-a-{uuid.uuid4().hex[:6]}"
        self.haus_b = f"{kuerzel}-b-{uuid.uuid4().hex[:6]}"
        self.tabellen = tuple(tabellen) + RUNTIME_TABELLEN
        self.probe_sql = probe_sql
        self.identitaet = Identitaet()

    # ------------------------------------------------------------------ Datenbank
    def engine(self):
        from sqlalchemy import create_engine, text

        from testgrenze import pruefstand_erlaubt

        if not pruefstand_erlaubt(DB_URL):
            pytest.skip("Schreibende Tests nur gegen den Pruefstand")
        try:
            motor = create_engine(DB_URL)
            with motor.connect() as conn:
                conn.execute(text(self.probe_sql))
        except Exception as fehler:  # noqa: BLE001 — ohne Pruefstand kein Nachweis, aber kein Fehlschlag
            pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
        return motor

    def aufraeumen(self, engine) -> None:
        from sqlalchemy import text

        with engine.begin() as v:
            for tabelle in self.tabellen:
                v.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"),  # nosec B608
                          {"h": [self.haus_a, self.haus_b]})

    def haeuser_anlegen(self, engine) -> None:
        from sqlalchemy import text

        with engine.begin() as v:
            for haus in (self.haus_a, self.haus_b):
                v.execute(
                    text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :n) ON CONFLICT (id) DO NOTHING"),
                    {"id": haus, "n": f"Pruefbetrieb {haus}"},
                )

    def haeuser_entfernen(self, engine) -> None:
        from sqlalchemy import text

        self.aufraeumen(engine)
        with engine.begin() as v:
            v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [self.haus_a, self.haus_b]})

    def wert(self, engine, sql: str, **parameter):
        from sqlalchemy import text

        with engine.connect() as v:
            return v.execute(text(sql), parameter).scalar()

    def ausfuehren(self, engine, sql: str, **parameter) -> None:
        from sqlalchemy import text

        with engine.begin() as v:
            v.execute(text(sql), parameter)

    # ------------------------------------------------------------------ Anwendung
    def identitaet_installieren(self) -> None:
        """Pro Test nach ``tests/conftest.py`` (dessen Attrappe heisst immer ``dev``/admin) einsetzen."""
        from app.auth.deps import get_current_user
        from app.core.security import require_bearer_token
        from app.core.tenant import get_tenant_id
        from app.main import app
        from testgrenze import mandant_aus_kopf

        identitaet = self.identitaet

        def geprueft(request: Request) -> str:
            tenant = mandant_aus_kopf(request)
            request.state.tenant_id = tenant
            request.state.tenant_verified = True
            request.state.token_claims = {"sub": identitaet.sub, "tenant_id": tenant, "roles": list(identitaet.roles)}
            return "pruefstand"

        app.dependency_overrides[require_bearer_token] = geprueft
        app.dependency_overrides[get_current_user] = identitaet.nutzer
        app.dependency_overrides[get_tenant_id] = mandant_aus_kopf

    @staticmethod
    def client():
        from fastapi.testclient import TestClient

        from app.main import app

        return TestClient(app, raise_server_exceptions=False)

    @staticmethod
    def identitaet_entfernen() -> None:
        from app.core.tenant import get_tenant_id
        from app.main import app

        app.dependency_overrides.pop(get_tenant_id, None)

    def kopf(self, haus: str | None = None) -> dict[str, str]:
        # X-User-ID ist absichtlich gefaelscht: Kein Kommando-Weg darf ihn als Urheber nehmen.
        return {"X-Tenant-ID": haus or self.haus_a, "Authorization": "Bearer pruefstand",
                "X-User-ID": "gefaelschter-bearbeiter"}

    def post(self, client, pfad: str, haus: str | None = None, **body: Any):
        return client.post(pfad, headers=self.kopf(haus), json=body)

    @staticmethod
    def auftrag(grund: str = "Fachlich geprueft im Test", **extra: Any) -> dict[str, Any]:
        return {"_auditReason": grund, "_idempotencyKey": str(uuid.uuid4()), **extra}

    def spuren(self, engine, haus: str, aktion: str) -> int:
        """Audit-Zeilen dieser Maskenaktion im Mandanten."""
        return int(self.wert(
            engine,
            "SELECT COUNT(*) FROM domain_crm.crm_action_audit_log WHERE tenant_id = :h AND action_key = :a",
            h=haus, a=aktion,
        ) or 0)


def registriere(ps: Pruefstand, namespace: dict[str, Any]) -> None:
    """Fixtures ``engine``, ``client`` und die autouse-Aufraeumer im Testmodul anlegen."""

    @pytest.fixture(scope="module")
    def engine():
        return ps.engine()

    @pytest.fixture(scope="module", autouse=True)
    def _haeuser(engine):
        ps.haeuser_anlegen(engine)
        yield
        ps.haeuser_entfernen(engine)

    @pytest.fixture(autouse=True)
    def _leer(engine):
        ps.aufraeumen(engine)
        ps.identitaet.als("pruefer-anna", "admin")
        ps.identitaet_installieren()
        yield
        ps.identitaet_entfernen()

    @pytest.fixture(scope="module")
    def client(engine):
        return ps.client()

    namespace.update(engine=engine, _haeuser=_haeuser, _leer=_leer, client=client)
