"""FEED-CHAIN-004 — Einzelfutter ↔ inventory.articles + Bewegungsbelege."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

TENANT_ID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT_ID}
FEED_CHAIN_004_REVISION = "feed_chain_article_map_20260623"


def _column_ready() -> bool:
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        n = db.execute(
            text(
                "SELECT count(*) FROM information_schema.columns "
                "WHERE table_schema = 'domain_shared' "
                "AND table_name = 'futtermittel_einzelfutter' "
                "AND column_name = 'inventory_article_id'"
            ),
        ).scalar()
        return int(n or 0) == 1
    finally:
        db.close()


def _ensure_schema() -> None:
    if _column_ready():
        return
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", FEED_CHAIN_004_REVISION],
        text=True,
        capture_output=True,
        env={**os.environ},
        timeout=180,
        check=False,
    )
    if result.returncode != 0 or not _column_ready():
        pytest.skip(f"FEED-CHAIN-004-Schema nicht migrierbar: {(result.stderr or '')[-400:]}")


def _ensure_warehouse(db) -> str:
    row = db.execute(
        text(
            "SELECT id FROM domain_inventory.warehouses "
            "WHERE tenant_id = :t AND COALESCE(is_active, true) = true LIMIT 1"
        ),
        {"t": TENANT_ID},
    ).first()
    if row:
        return str(row[0])
    wh_id = f"IT-WH-{uuid.uuid4().hex[:8]}"
    db.execute(
        text(
            "INSERT INTO domain_inventory.warehouses "
            "(id, tenant_id, warehouse_code, name, is_active, created_at) "
            "VALUES (:id, :t, :code, 'IT Feed WH', true, NOW())"
        ),
        {"id": wh_id, "t": TENANT_ID, "code": f"WH-{wh_id[-6:]}"},
    )
    db.flush()
    return wh_id


@pytest.fixture
def feed004_seed(require_db):
    _ensure_schema()
    from app.core.database import SessionLocal

    suffix = uuid.uuid4().hex[:8]
    db = SessionLocal()
    ids = {
        "ef1": f"IT-EF1-{suffix}",
        "ef2": f"IT-EF2-{suffix}",
        "rezept": f"IT-REZ-{suffix}",
        "k1": f"IT-RK1-{suffix}",
        "k2": f"IT-RK2-{suffix}",
        "wh": None,
        "article_ids": [],
    }
    try:
        ids["wh"] = _ensure_warehouse(db)
        db.execute(
            text(
                "INSERT INTO domain_shared.futtermittel_einzelfutter "
                "(id, tenant_id, artikel_nummer, name, art, verfuegbar_t, gvo_status, aktiv) VALUES "
                "(:ef1, :t, :an1, 'IT Weizen', 'Energiefutter', 100, 'gvo-frei', true), "
                "(:ef2, :t, :an2, 'IT Sojaschrot', 'Eiweißfutter', 100, 'gvo-frei-zertifiziert', true)"
            ),
            {
                "ef1": ids["ef1"],
                "ef2": ids["ef2"],
                "t": TENANT_ID,
                "an1": f"EF1-{suffix}",
                "an2": f"EF2-{suffix}",
            },
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
            {
                "k1": ids["k1"],
                "k2": ids["k2"],
                "r": ids["rezept"],
                "ef1": ids["ef1"],
                "ef2": ids["ef2"],
            },
        )
        db.commit()
        yield ids
    finally:
        db.rollback()
        for ef in (ids["ef1"], ids["ef2"]):
            aid = db.execute(
                text(
                    "SELECT inventory_article_id FROM domain_shared.futtermittel_einzelfutter WHERE id = :i"
                ),
                {"i": ef},
            ).scalar()
            if aid:
                db.execute(
                    text(
                        "DELETE FROM domain_inventory.inventory_stock_movements "
                        "WHERE article_id = :a AND tenant_id = :t"
                    ),
                    {"a": aid, "t": TENANT_ID},
                )
                db.execute(
                    text("DELETE FROM domain_inventory.articles WHERE id = :a AND tenant_id = :t"),
                    {"a": aid, "t": TENANT_ID},
                )
        db.execute(
            text("DELETE FROM domain_ops.ops_chargen WHERE produktionsprozess->>'rezept_id' = :r"),
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


@pytest.mark.integration
@pytest.mark.needs_live_db
class TestFeedChain004:
    @pytest.fixture(autouse=True)
    def _client(self):
        from main import app

        self.client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
        yield

    def test_ensure_article_link_creates_mapping(self, feed004_seed):
        r = self.client.post(
            f"/api/v1/produktion/mischfutter/inventory-links/{feed004_seed['ef1']}/ensure",
            headers=HEADERS,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ok"] is True
        assert body["article_id"]

        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    "SELECT ef.inventory_article_id, a.article_number "
                    "FROM domain_shared.futtermittel_einzelfutter ef "
                    "JOIN domain_inventory.articles a ON a.id = ef.inventory_article_id "
                    "WHERE ef.id = :id"
                ),
                {"id": feed004_seed["ef1"]},
            ).first()
            assert row is not None
        finally:
            db.close()

        r2 = self.client.post(
            f"/api/v1/produktion/mischfutter/inventory-links/{feed004_seed['ef1']}/ensure",
            headers=HEADERS,
        )
        assert r2.status_code == 200
        assert r2.json().get("created") is False

    def test_freigabe_schreibt_inventory_stock_movements(self, feed004_seed):
        auftrag = self.client.post(
            "/api/v1/produktion/mischfutter/auftrag",
            json={"rezept_id": feed004_seed["rezept"], "menge_t": 10.0},
            headers=HEADERS,
        )
        assert auftrag.status_code == 201, auftrag.text
        auftrag_id = auftrag.json()["id"]

        freigegeben = self.client.patch(
            f"/api/v1/produktion/mischfutter/auftrag/{auftrag_id}/status",
            json={"status": "freigegeben", "freigegeben_von": "it-feed004"},
            headers=HEADERS,
        )
        assert freigegeben.status_code == 200, freigegeben.text

        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            moves = db.execute(
                text(
                    "SELECT movement_type, quantity, source_document_type "
                    "FROM domain_inventory.inventory_stock_movements "
                    "WHERE tenant_id = :t AND source_document_type = 'feed_production' "
                    "AND source_document_id LIKE :doc"
                ),
                {"t": TENANT_ID, "doc": f"{auftrag_id}:%"},
            ).all()
            assert len(moves) == 2
            assert all(m[0] == "out" for m in moves)
            assert sum(float(m[1]) for m in moves) == pytest.approx(10.0)
        finally:
            db.close()

    def test_storno_idempotent_inventory_movements(self, feed004_seed):
        auftrag = self.client.post(
            "/api/v1/produktion/mischfutter/auftrag",
            json={"rezept_id": feed004_seed["rezept"], "menge_t": 5.0},
            headers=HEADERS,
        )
        auftrag_id = auftrag.json()["id"]
        self.client.patch(
            f"/api/v1/produktion/mischfutter/auftrag/{auftrag_id}/status",
            json={"status": "freigegeben", "freigegeben_von": "it"},
            headers=HEADERS,
        )
        storno = self.client.patch(
            f"/api/v1/produktion/mischfutter/auftrag/{auftrag_id}/status",
            json={"status": "storniert"},
            headers=HEADERS,
        )
        assert storno.status_code == 200, storno.text

        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            outs = db.execute(
                text(
                    "SELECT count(*) FROM domain_inventory.inventory_stock_movements "
                    "WHERE tenant_id = :t AND source_document_type = 'feed_production' "
                    "AND movement_type = 'out' AND source_document_id LIKE :doc"
                ),
                {"t": TENANT_ID, "doc": f"{auftrag_id}:%"},
            ).scalar()
            ins = db.execute(
                text(
                    "SELECT count(*) FROM domain_inventory.inventory_stock_movements "
                    "WHERE tenant_id = :t AND source_document_type = 'feed_production' "
                    "AND movement_type = 'in' AND source_document_id LIKE :doc"
                ),
                {"t": TENANT_ID, "doc": f"{auftrag_id}:%"},
            ).scalar()
            assert int(outs or 0) == 2
            assert int(ins or 0) == 2
        finally:
            db.close()

    def _find_link(self, einzelfutter_id: str, *, mapped: str):
        """Blaettert die gefilterte Mapping-Liste, bis der Datensatz gefunden ist.

        Der Bestand ist groesser als jede Seite; ein einzelner Abruf traegt
        daher keine Aussage ueber die Anwesenheit eines Datensatzes.
        """
        offset, last_body = 0, None
        while True:
            r = self.client.get(
                "/api/v1/produktion/mischfutter/inventory-links",
                params={"mapped": mapped, "limit": 500, "offset": offset},
                headers=HEADERS,
            )
            assert r.status_code == 200, r.text
            last_body = r.json()
            for item in last_body["items"]:
                if item["id"] == einzelfutter_id:
                    return item, last_body
            if last_body["returned"] < last_body["limit"]:
                return None, last_body
            offset += last_body["limit"]

    def test_list_inventory_links(self, feed004_seed):
        ensured = self.client.post(
            f"/api/v1/produktion/mischfutter/inventory-links/{feed004_seed['ef1']}/ensure",
            headers=HEADERS,
        )
        assert ensured.status_code == 200, ensured.text

        own, body = self._find_link(feed004_seed["ef1"], mapped="true")
        assert own is not None, "eigener Seed-Datensatz fehlt in der verknuepften Liste"
        assert own["inventory_article_id"] == ensured.json()["article_id"]
        assert body["filter_mapped"] is True
        assert body["mapped_count"] >= 1

    def test_inventory_link_counts_cover_full_stock_not_page(self, feed004_seed):
        """Zaehler beschreiben den Bestand, nicht die ausgelieferte Seite."""
        ensured = self.client.post(
            f"/api/v1/produktion/mischfutter/inventory-links/{feed004_seed['ef1']}/ensure",
            headers=HEADERS,
        )
        assert ensured.status_code == 200, ensured.text

        page = self.client.get(
            "/api/v1/produktion/mischfutter/inventory-links",
            params={"limit": 1},
            headers=HEADERS,
        )
        assert page.status_code == 200, page.text
        body = page.json()
        assert body["returned"] == 1
        assert body["total"] >= 2, "Seed legt zwei Einzelfuttermittel an"
        assert body["total"] > body["returned"], "Bestand muss groesser als die Seite sein"
        assert body["mapped_count"] >= 1
        assert body["mapped_count"] + body["unmapped_count"] == body["total"]

    def test_ensure_moves_entry_from_unmapped_to_mapped(self, feed004_seed):
        before = self.client.get(
            "/api/v1/produktion/mischfutter/inventory-links",
            params={"limit": 1},
            headers=HEADERS,
        )
        assert before.status_code == 200, before.text
        before_body = before.json()

        still_open, _ = self._find_link(feed004_seed["ef2"], mapped="false")
        assert still_open is not None, "ef2 muss vor dem Verknuepfen offen sein"
        assert still_open["inventory_article_id"] is None

        ensured = self.client.post(
            f"/api/v1/produktion/mischfutter/inventory-links/{feed004_seed['ef2']}/ensure",
            headers=HEADERS,
        )
        assert ensured.status_code == 200, ensured.text

        after = self.client.get(
            "/api/v1/produktion/mischfutter/inventory-links",
            params={"limit": 1},
            headers=HEADERS,
        )
        assert after.status_code == 200, after.text
        after_body = after.json()
        assert after_body["mapped_count"] == before_body["mapped_count"] + 1
        assert after_body["unmapped_count"] == before_body["unmapped_count"] - 1
        assert after_body["total"] == before_body["total"]
        assert self._find_link(feed004_seed["ef2"], mapped="false")[0] is None
