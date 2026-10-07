"""GoBD-Archiveintrag in der Transaktion des Belegs; Bestell-Altbelege schreibgeschuetzt.

Bis zum 07.10.2026 committete ``register_artifact`` selbst — und schrieb damit die
halbe Arbeit des Aufrufers fest —, rollte bei einem Fehler **dessen** Transaktion
zurueck, gab ``None`` zurueck und protokollierte eine Warnung. Kein Aufrufer pruefte
das: Eine Rechnung galt als gebucht, deren Buchung verworfen war; eine E-Rechnung
wurde ohne Archivnachweis ausgeliefert; eine Buchungsuebergabe bei einem
Datenbankfehler leer exportiert und archiviert.

Bestellungen aus dem frueheren Dokumentspeicher liessen sich weiter aendern,
freigeben (``approvedBy = "system"``) und stornieren — ausserhalb der kanonischen
Bestellung. Die Bestellstatistik zaehlte nur diese Altbelege.
"""

from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS = f"gb-{uuid.uuid4().hex[:6]}"
LIEFERANT = str(uuid.uuid4())


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            v.execute(text("SELECT 1 FROM domain_docflow.document_artifacts LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    with motor.begin() as v:
        v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                  {"i": HAUS, "n": f"Pruefbetrieb {HAUS}"})
        v.execute(text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
                       "VALUES (:i, :h, :n, 'Landtechnik Sued')"), {"i": LIEFERANT, "h": HAUS, "n": f"LF-{LIEFERANT[:6]}"})
    yield motor
    with motor.begin() as v:
        v.execute(text("DELETE FROM documents WHERE doc_type = 'purchase_order' AND data->>'tenantId' = :h"), {"h": HAUS})
        v.execute(text("DELETE FROM domain_einkauf.bestellungen WHERE tenant_id = :h"), {"h": HAUS})
        v.execute(text("DELETE FROM domain_einkauf.lieferanten WHERE id = :i"), {"i": LIEFERANT})
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = :h"), {"h": HAUS})


@pytest.fixture
def sitzung(engine):
    """Eine Sitzung in einer aeusseren Transaktion, die am Ende verworfen wird.

    Archivierter Inhalt ist per Trigger gegen Loeschen geschuetzt; die Pruefdaten
    duerfen deshalb nie festgeschrieben werden. ``commit`` der Sitzung loest nur
    einen Savepoint auf.
    """
    from sqlalchemy.orm import Session

    verbindung = engine.connect()
    aussen = verbindung.begin()
    db = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    yield db, verbindung
    db.close()
    aussen.rollback()
    verbindung.close()


def anzahl(verbindung, beleg: str) -> int:
    from sqlalchemy import text

    return verbindung.execute(text(
        "SELECT count(*) FROM domain_docflow.document_artifacts a "
        "JOIN domain_docflow.document_headers h ON h.id = a.header_id "
        "WHERE h.tenant_id = :h AND h.doc_number = :k"), {"h": HAUS, "k": beleg}).scalar()


class TestArchiveintrag:
    def test_der_eintrag_gehoert_zur_transaktion_des_aufrufers(self, sitzung):
        from app.core.gobd_artifact import register_artifact, sha256_hex

        db, verbindung = sitzung
        beleg = f"RE-{uuid.uuid4().hex[:8]}"
        register_artifact(db, HAUS, beleg, "other", sha256_hex(b"x"), "invoice/ar", doc_type="sales_invoice",
                          content=b"x")
        db.rollback()
        assert anzahl(verbindung, beleg) == 0, "register_artifact darf nicht selbst committen"

        register_artifact(db, HAUS, beleg, "other", sha256_hex(b"x"), "invoice/ar", doc_type="sales_invoice",
                          content=b"x")
        db.commit()
        assert anzahl(verbindung, beleg) == 1

    def test_der_inhalt_liegt_im_archiv_und_der_schluessel_zeigt_darauf(self, sitzung):
        from sqlalchemy import text

        from app.core.gobd_artifact import register_artifact, sha256_hex

        db, verbindung = sitzung
        kennung = register_artifact(db, HAUS, "EXP-1", "other", sha256_hex(b"ASC"), "export/asc/x.ASC",
                                    doc_type="fibu_export", content=b"ASC")
        db.commit()
        zeile = verbindung.execute(text(
            "SELECT content_bytes, storage_key, freigabe_status FROM domain_docflow.document_artifacts WHERE id = :i"
        ), {"i": kennung}).mappings().one()
        assert bytes(zeile["content_bytes"]) == b"ASC"
        assert zeile["storage_key"] == f"postgresql:document_artifacts:{kennung}"
        assert zeile["freigabe_status"] == "archiviert"

    def test_ein_zweites_artefakt_zum_selben_beleg_bekommt_eine_neue_version(self, sitzung):
        from sqlalchemy import text

        from app.core.gobd_artifact import register_artifact, sha256_hex

        db, verbindung = sitzung
        erste = register_artifact(db, HAUS, "RE-V", "xml", sha256_hex(b"a"), "k", doc_type="sales_invoice", content=b"a")
        zweite = register_artifact(db, HAUS, "RE-V", "xml", sha256_hex(b"b"), "k", doc_type="sales_invoice", content=b"b")
        db.commit()
        versionen = dict(verbindung.execute(text(
            "SELECT id, version FROM domain_docflow.document_artifacts WHERE id = ANY(:i)"), {"i": [erste, zweite]}).all())
        assert (versionen[erste], versionen[zweite]) == (1, 2)

    def test_ein_falscher_hash_wird_nicht_archiviert(self, sitzung):
        from app.core.gobd_artifact import GobdArtifactError, register_artifact, sha256_hex

        db, _ = sitzung
        with pytest.raises(GobdArtifactError, match="Hash"):
            register_artifact(db, HAUS, "RE-H", "pdf", sha256_hex(b"anders"), "k", doc_type="sales_invoice",
                              content=b"inhalt")

    def test_ein_gescheiterter_eintrag_scheitert_laut(self, sitzung):
        from app.core.gobd_artifact import GobdArtifactError, register_artifact

        db, _ = sitzung
        with pytest.raises(GobdArtifactError):
            # content_hash_sha256 ist NOT NULL: der Eintrag kann nicht gelingen.
            register_artifact(db, HAUS, "RE-X", "pdf", None, "k", doc_type="sales_invoice")  # type: ignore[arg-type]


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf() -> dict[str, str]:
    return {"X-Tenant-ID": HAUS, "Authorization": "Bearer dev-token"}


def altbeleg(engine) -> str:
    import json

    from sqlalchemy import text

    nummer = f"PO-ALT-{uuid.uuid4().hex[:6]}"
    daten = {"id": str(uuid.uuid4()), "purchaseOrderNumber": nummer, "supplierId": "Landtechnik Sued",
             "status": "ENTWURF", "tenantId": HAUS, "items": [], "totalAmount": 100.0}
    with engine.begin() as v:
        v.execute(text("INSERT INTO documents (id, doc_type, doc_number, data, created_at, updated_at) "
                       "VALUES (:i, 'purchase_order', :n, CAST(:d AS jsonb), NOW(), NOW())"),
                  {"i": str(uuid.uuid4()), "n": nummer, "d": json.dumps(daten)})
    return nummer


class TestBestellAltbelege:
    def test_ein_altbeleg_bleibt_lesbar(self, engine, client):
        nummer = altbeleg(engine)
        antwort = client.get(f"/api/v1/purchase-orders/{nummer}", headers=kopf())
        assert antwort.status_code == 200, antwort.text

    @pytest.mark.parametrize("weg,rumpf", [
        ("/api/v1/purchase-orders/{}/approve", None),
        ("/api/v1/purchase-orders/{}/cancel-with-reason", {"reason": "Fehler"}),
    ])
    def test_ein_altbeleg_wird_nicht_mehr_fortgeschrieben(self, engine, client, weg, rumpf):
        nummer = altbeleg(engine)
        antwort = client.post(weg.format(nummer), headers=kopf(), json=rumpf or {})
        assert antwort.status_code == 409, antwort.text
        assert "schreibgeschuetzt" in antwort.json()["detail"]
        assert client.get(f"/api/v1/purchase-orders/{nummer}", headers=kopf()).json()["status"] == "ENTWURF"

    def test_aendern_eines_altbelegs_ebenso(self, engine, client):
        nummer = altbeleg(engine)
        antwort = client.patch(f"/api/v1/purchase-orders/{nummer}", headers=kopf(), json={"notes": "x"})
        assert antwort.status_code == 409

    def test_unbekannt_bleibt_404(self, client):
        assert client.post("/api/v1/purchase-orders/GIBT-ES-NICHT/approve", headers=kopf()).status_code == 404

    def test_die_statistik_zaehlt_auch_die_kanonischen_bestellungen(self, engine, client):
        from sqlalchemy import text

        with engine.begin() as v:
            v.execute(text("INSERT INTO domain_einkauf.bestellungen (id, tenant_id, bestellnummer, lieferant_id, "
                           " bestelldatum, status) VALUES (:i, :h, :n, :l, CURRENT_DATE, 'entwurf')"),
                      {"i": str(uuid.uuid4()), "h": HAUS, "n": f"EK-{uuid.uuid4().hex[:6]}", "l": LIEFERANT})
        statistik = client.get("/api/v1/purchase-orders/statistics", headers=kopf()).json()
        liste = client.get("/api/v1/purchase-orders?pageSize=500", headers=kopf()).json()
        assert statistik["totalOrders"] == liste["total"]
        assert statistik["totalOrders"] >= 1


def test_kein_aufrufer_verschluckt_den_archivfehler():
    from pathlib import Path

    quelle = Path("app/api/v1/endpoints/sales_invoice_einvoice.py").read_text(encoding="utf-8-sig")
    assert "GoBD-Archivierung ist best-effort" not in quelle
    assert "db.commit()" not in Path("app/core/gobd_artifact.py").read_text(encoding="utf-8-sig")
