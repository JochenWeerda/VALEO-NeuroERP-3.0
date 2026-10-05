"""FEED-CHAIN-001 — Produktion→Charge-Durchstich (Mischfutter).

Reine Logik (Verbrauchs-Snapshot, Bestandsprüfung) + Integration gegen echte DB:
Freigabe persistiert Snapshot und zieht Bestand ab; Storno restauriert exakt den
Snapshot (auch nach Rezeptänderung); ``fertig`` erzeugt die Fertigwaren-Charge in
``domain_ops.ops_chargen`` fail-closed; Trace löst die Kette auf.
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.services.feed_production_chain_service import (
    compute_verbrauch,
    fehlende_komponenten,
)

TENANT_ID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT_ID}
FEED_REVISION = "feed_chain_verbrauch_20260612"


def _komp(name: str, anteil: float, ef_id: str | None, sortierung: int = 0):
    return SimpleNamespace(
        komponente_name=name, anteil=anteil, einzelfutter_id=ef_id, sortierung=sortierung
    )


class TestVerbrauchLogik:
    def test_compute_verbrauch_mengen_und_reihenfolge(self):
        snapshot = compute_verbrauch(
            10,
            [_komp("Mineral", 0.1, "ef-3", sortierung=2), _komp("Weizen", 0.6, "ef-1", sortierung=0), _komp("Soja", 0.3, "ef-2", sortierung=1)],
        )
        assert [r["name"] for r in snapshot] == ["Weizen", "Soja", "Mineral"]
        assert snapshot[0]["menge_t"] == pytest.approx(6.0)
        assert snapshot[1]["menge_t"] == pytest.approx(3.0)
        assert snapshot[2]["menge_t"] == pytest.approx(1.0)

    def test_fehlende_komponenten_fail_closed(self):
        snapshot = compute_verbrauch(10, [_komp("Weizen", 0.6, "ef-1"), _komp("Soja", 0.3, "ef-2")])
        fehlend = fehlende_komponenten(snapshot, {"ef-1": Decimal("5"), "ef-2": Decimal("99")})
        assert len(fehlend) == 1
        assert "Weizen" in fehlend[0]

    def test_fehlende_komponenten_ohne_ef_referenz_ignoriert(self):
        snapshot = compute_verbrauch(10, [_komp("Frei", 1.0, None)])
        assert fehlende_komponenten(snapshot, {}) == []


# ---------------------------------------------------------------------------
# Integration (echte DB + API)
# ---------------------------------------------------------------------------

pytestmark_integration = [pytest.mark.integration, pytest.mark.needs_live_db]


def _feed_columns_ready() -> bool:
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        n = db.execute(
            text(
                "SELECT count(*) FROM information_schema.columns "
                "WHERE table_schema = 'domain_shared' "
                "AND table_name = 'futtermittel_produktionsauftraege' "
                "AND column_name IN ('verbrauch','charge_id')"
            ),
        ).scalar()
        return int(n or 0) == 2
    finally:
        db.close()


def _ensure_feed_schema() -> None:
    if _feed_columns_ready():
        return
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", FEED_REVISION],
        text=True,
        capture_output=True,
        env={**os.environ},
        timeout=180,
        check=False,
    )
    if result.returncode != 0 or not _feed_columns_ready():
        pytest.skip(f"Feed-Chain-Schema nicht migrierbar: {(result.stderr or '')[-400:]}")


@pytest.fixture
def feed_seed(require_db):
    """Einzelfutter (2x) + Rezept mit Komponenten anlegen; alles wieder aufräumen."""
    _ensure_feed_schema()
    from app.core.database import SessionLocal

    suffix = uuid.uuid4().hex[:8]
    db = SessionLocal()
    ids = {
        "ef1": f"IT-EF1-{suffix}",
        "ef2": f"IT-EF2-{suffix}",
        "rezept": f"IT-REZ-{suffix}",
        "k1": f"IT-RK1-{suffix}",
        "k2": f"IT-RK2-{suffix}",
    }
    try:
        db.execute(
            text(
                "INSERT INTO domain_shared.futtermittel_einzelfutter "
                "(id, tenant_id, artikel_nummer, name, art, verfuegbar_t, gvo_status, aktiv) VALUES "
                "(:ef1, :t, :an1, 'IT Weizen', 'Energiefutter', 100, 'gvo-frei', true), "
                "(:ef2, :t, :an2, 'IT Sojaschrot', 'Eiweißfutter', 100, 'gvo-frei-zertifiziert', true)"
            ),
            {"ef1": ids["ef1"], "ef2": ids["ef2"], "t": TENANT_ID,
             "an1": f"EF1-{suffix}", "an2": f"EF2-{suffix}"},
        )
        db.execute(
            text(
                "INSERT INTO domain_shared.futtermittel_rezepte "
                "(id, tenant_id, rezept_code, name, tierart, aktiv) VALUES "
                "(:r, :t, :code, 'IT Milchleistungsfutter', 'Rind', true)"
            ),
            {"r": ids["rezept"], "t": TENANT_ID, "code": f"REZ-{suffix}"},
        )
        db.execute(
            text(
                "INSERT INTO domain_shared.futtermittel_rezept_komponenten "
                "(id, rezept_id, komponente_name, anteil, einzelfutter_id, sortierung) VALUES "
                "(:k1, :r, 'IT Weizen', 0.6, :ef1, 0), "
                "(:k2, :r, 'IT Sojaschrot', 0.4, :ef2, 1)"
            ),
            {"k1": ids["k1"], "k2": ids["k2"],
             "r": ids["rezept"], "ef1": ids["ef1"], "ef2": ids["ef2"]},
        )
        db.commit()
        yield ids
    finally:
        db.rollback()
        db.execute(
            text(
                "DELETE FROM domain_ops.ops_chargen WHERE produktionsprozess->>'rezept_id' = :r"
            ),
            {"r": ids["rezept"]},
        )
        db.execute(
            text("DELETE FROM domain_shared.futtermittel_produktionsauftraege WHERE rezept_id = :r"),
            {"r": ids["rezept"]},
        )
        db.execute(
            text("DELETE FROM domain_shared.futtermittel_rezept_komponenten WHERE rezept_id = :r"),
            {"r": ids["rezept"]},
        )
        db.execute(text("DELETE FROM domain_shared.futtermittel_rezepte WHERE id = :r"), {"r": ids["rezept"]})
        db.execute(
            text("DELETE FROM domain_shared.futtermittel_einzelfutter WHERE id IN (:e1, :e2)"),
            {"e1": ids["ef1"], "e2": ids["ef2"]},
        )
        db.commit()
        db.close()


def _bestand(ef_id: str) -> float:
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        v = db.execute(
            text("SELECT verfuegbar_t FROM domain_shared.futtermittel_einzelfutter WHERE id = :i"),
            {"i": ef_id},
        ).scalar()
        return float(v or 0)
    finally:
        db.close()


@pytest.mark.integration
@pytest.mark.needs_live_db
class TestFeedProductionChainIntegration:
    @pytest.fixture(autouse=True)
    def _client(self):
        from main import app

        self.client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
        yield

    def _create_auftrag(self, rezept_id: str, menge_t: float = 10.0):
        r = self.client.post(
            "/api/v1/produktion/mischfutter/auftrag",
            json={"rezept_id": rezept_id, "menge_t": menge_t},
            headers=HEADERS,
        )
        assert r.status_code == 201, r.text
        return r.json()

    def _patch_status(self, auftrag_id: str, status: str, expected: int = 200):
        r = self.client.patch(
            f"/api/v1/produktion/mischfutter/auftrag/{auftrag_id}/status",
            json={"status": status, "freigegeben_von": "it-test"},
            headers=HEADERS,
        )
        assert r.status_code == expected, r.text
        return r.json()

    def test_freigabe_snapshot_fertig_charge_und_trace(self, feed_seed):
        auftrag = self._create_auftrag(feed_seed["rezept"], 10.0)

        freigegeben = self._patch_status(auftrag["id"], "freigegeben")
        assert freigegeben["bestands_abzug_erfolgt"] is True
        snapshot = freigegeben["verbrauch"]
        assert snapshot and len(snapshot) == 2
        assert snapshot[0]["menge_t"] == pytest.approx(6.0)
        assert snapshot[1]["menge_t"] == pytest.approx(4.0)
        assert _bestand(feed_seed["ef1"]) == pytest.approx(94.0)
        assert _bestand(feed_seed["ef2"]) == pytest.approx(96.0)

        self._patch_status(auftrag["id"], "in_produktion")
        fertig = self._patch_status(auftrag["id"], "fertig")
        assert fertig["status"] == "fertig"
        assert fertig["charge_id"], "fertig muss die Fertigwaren-Charge anlegen"

        charge = self.client.get(f"/api/v1/chargen/{fertig['charge_id']}", headers=HEADERS)
        assert charge.status_code == 200, charge.text
        body = charge.json()
        assert body["chargenId"] == auftrag["chargen_id"]
        assert len(body["rohstoffe"]) == 2
        assert body["rohstoffe"][0]["gvo_status"] == "gvo-frei"
        assert body["produktionsprozess"]["produktionsauftrag_id"] == auftrag["id"]

        trace = self.client.get(
            f"/api/v1/produktion/mischfutter/auftraege/{auftrag['chargen_id']}/trace",
            headers=HEADERS,
        )
        assert trace.status_code == 200, trace.text
        t = trace.json()
        assert t["kette_geschlossen"] is True
        assert t["charge"]["id"] == fertig["charge_id"]
        assert len(t["komponenten"]) == 2

        # Idempotenz: erneutes fertig ist kein gültiger Übergang (409),
        # aber die Charge bleibt eindeutig.
        self._patch_status(auftrag["id"], "fertig", expected=409)

    def test_storno_restauriert_snapshot_trotz_rezeptaenderung(self, feed_seed):
        from app.core.database import SessionLocal

        auftrag = self._create_auftrag(feed_seed["rezept"], 10.0)
        self._patch_status(auftrag["id"], "freigegeben")
        assert _bestand(feed_seed["ef1"]) == pytest.approx(94.0)

        # Rezept nachträglich ändern — Storno muss trotzdem exakt 6.0/4.0 zurückgeben
        db = SessionLocal()
        try:
            db.execute(
                text(
                    "UPDATE domain_shared.futtermittel_rezept_komponenten "
                    "SET anteil = 0.9 WHERE id = :k"
                ),
                {"k": feed_seed["k1"]},
            )
            db.commit()
        finally:
            db.close()

        storniert = self._patch_status(auftrag["id"], "storniert")
        assert storniert["bestands_abzug_erfolgt"] is False
        assert _bestand(feed_seed["ef1"]) == pytest.approx(100.0)
        assert _bestand(feed_seed["ef2"]) == pytest.approx(100.0)

    def test_freigabe_fail_closed_bei_unterdeckung(self, feed_seed):
        auftrag = self._create_auftrag(feed_seed["rezept"], 10.0)

        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            db.execute(
                text(
                    "UPDATE domain_shared.futtermittel_einzelfutter "
                    "SET verfuegbar_t = 1 WHERE id = :i"
                ),
                {"i": feed_seed["ef1"]},
            )
            db.commit()
        finally:
            db.close()

        body = self._patch_status(auftrag["id"], "freigegeben", expected=409)
        assert "fehlend" in body["detail"]
        # Bestand unverändert, kein Snapshot persistiert
        assert _bestand(feed_seed["ef1"]) == pytest.approx(1.0)

    def test_fertig_fail_closed_bei_fremder_chargen_id(self, feed_seed):
        from app.core.database import SessionLocal

        fremd_chargen_id = f"IT-FREMD-{uuid.uuid4().hex[:8]}"
        db = SessionLocal()
        try:
            db.execute(
                text(
                    "INSERT INTO domain_ops.ops_chargen "
                    "(id, tenant_id, chargen_id, artikel, artikel_id, menge, lagerort, eingang, status, produktionsprozess) "
                    "VALUES (:i, :tid, :c, 'Fremdware', 'X', 1, 'Halle 1', NOW(), 'erfasst', "
                    "jsonb_build_object('rezept_id', :r))"
                ),
                {"i": f"CH-IT-{uuid.uuid4().hex[:8]}", "tid": TENANT_ID, "c": fremd_chargen_id, "r": feed_seed["rezept"]},
            )
            db.commit()
        finally:
            db.close()

        r = self.client.post(
            "/api/v1/produktion/mischfutter/auftrag",
            json={"rezept_id": feed_seed["rezept"], "menge_t": 5.0, "chargen_id": fremd_chargen_id},
            headers=HEADERS,
        )
        assert r.status_code == 201, r.text
        auftrag = r.json()
        self._patch_status(auftrag["id"], "freigegeben")
        self._patch_status(auftrag["id"], "in_produktion")
        body = self._patch_status(auftrag["id"], "fertig", expected=409)
        assert "fremde" in body["detail"]
