"""Hinweisgebermeldungen bleiben im eigenen Haus, und die Notiz bleibt JSON.

Die EU-Hinweisgeberrichtlinie verlangt Vertraulichkeit (Art. 16). Geprueft
werden deshalb nicht Formalien, sondern drei Aussagen, die vorher alle falsch
waren:

1. Ein Mandant sieht die Meldungen eines anderen **nicht** — auch nicht ihre
   Existenz, Kategorie oder Schwere.
2. Eine Notiz mit Anfuehrungszeichen zerlegt die JSON-Struktur **nicht**.
   Zuvor stand sie in einem f-String; ein Hinweisgeberformular ist die letzte
   Stelle, an der man auf wohlgeformte Eingaben hoffen sollte.
3. **Beide** Endpunkte koennen dieselbe Tabelle schreiben. Zuvor legte einer
   sie zur Laufzeit ohne ``tenant_id`` an, und der andere bekam dauerhaft 503.

Ohne erreichbare Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

TABELLE = "domain_compliance.whistleblower_reports"


@pytest.fixture(scope="module")
def client():
    from sqlalchemy import create_engine, text

    try:
        with create_engine(DB_URL).connect() as conn:
            vorhanden = conn.execute(text(f"SELECT to_regclass('{TABELLE}')")).scalar()
            mandantenspalte = conn.execute(
                text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_schema = 'domain_compliance' "
                    "AND table_name = 'whistleblower_reports' "
                    "AND column_name = 'tenant_id'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden or not mandantenspalte:
        pytest.skip("Migration whistleblower_eine_tabelle_20260930 nicht angewandt")

    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def _mandant() -> str:
    from sqlalchemy import create_engine, text

    name = f"test-{uuid.uuid4().hex[:8]}"
    with create_engine(DB_URL).begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :d, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": name, "d": f"{name}.test"},
        )
    return name


def _aufraeumen(*mandanten: str) -> None:
    from sqlalchemy import create_engine, text

    with create_engine(DB_URL).begin() as v:
        for m in mandanten:
            v.execute(text(f"DELETE FROM {TABELLE} WHERE tenant_id = :t"), {"t": m})  # nosec B608
            v.execute(text("DELETE FROM domain_shared.tenants WHERE id = :t"), {"t": m})


def _kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
    }


@pytest.fixture()
def zwei_haeuser():
    eins, zwei = _mandant(), _mandant()
    try:
        yield eins, zwei
    finally:
        _aufraeumen(eins, zwei)


# ── Vertraulichkeit ────────────────────────────────────────────────────


def test_ein_haus_sieht_die_meldung_des_anderen_nicht(client, zwei_haeuser) -> None:
    """Der Kern der Pflicht. Zuvor listete GET /reports alles, was da war."""
    eins, zwei = zwei_haeuser

    angelegt = client.post(
        "/api/v1/compliance/hinweisgeber/reports",
        headers=_kopf(eins),
        json={
            "category": "BESTECHUNG",
            "description": "Ein Hinweis, der nur das eigene Haus angeht.",
            "severity": "HOCH",
        },
    )
    assert angelegt.status_code == 201, angelegt.text

    eigene = client.get("/api/v1/compliance/hinweisgeber/reports", headers=_kopf(eins))
    assert eigene.status_code == 200, eigene.text
    assert len(eigene.json()) == 1

    fremde = client.get("/api/v1/compliance/hinweisgeber/reports", headers=_kopf(zwei))
    assert fremde.status_code == 200, fremde.text
    assert fremde.json() == [], (
        "Das andere Haus sieht die Meldung — Art. 16 der Hinweisgeberrichtlinie"
    )


def test_der_token_des_anderen_hauses_gibt_keine_auskunft(client, zwei_haeuser) -> None:
    """Auch nicht, dass es ihn gibt: 404 wie bei einem unbekannten Token."""
    eins, zwei = zwei_haeuser

    token = client.post(
        "/api/v1/compliance/hinweisgeber/reports",
        headers=_kopf(eins),
        json={"category": "SICHERHEIT", "description": "Ein Hinweis.", "severity": "MITTEL"},
    ).json()["token"]

    eigen = client.get(
        f"/api/v1/compliance/hinweisgeber/reports/status/{token}", headers=_kopf(eins)
    )
    assert eigen.status_code == 200, eigen.text

    fremd = client.get(
        f"/api/v1/compliance/hinweisgeber/reports/status/{token}", headers=_kopf(zwei)
    )
    assert fremd.status_code == 404, fremd.text
    unbekannt = client.get(
        "/api/v1/compliance/hinweisgeber/reports/status/GIBTESNICHT", headers=_kopf(zwei)
    )
    # Dieselbe Antwort fuer „gibt es nicht" und „gehoert einem anderen": Der
    # Unterschied waere selbst eine Auskunft.
    assert fremd.json()["detail"] == unbekannt.json()["detail"]


def test_ein_fremder_hinweis_laesst_sich_nicht_bearbeiten(client, zwei_haeuser) -> None:
    from sqlalchemy import create_engine, text

    eins, zwei = zwei_haeuser
    client.post(
        "/api/v1/compliance/hinweisgeber/reports",
        headers=_kopf(eins),
        json={"category": "BETRUG", "description": "Ein Hinweis.", "severity": "HOCH"},
    )
    with create_engine(DB_URL).connect() as c:
        meldungs_id = c.execute(
            text(f"SELECT id FROM {TABELLE} WHERE tenant_id = :t"),  # nosec B608
            {"t": eins},
        ).scalar()

    antwort = client.patch(
        f"/api/v1/compliance/hinweisgeber/reports/{meldungs_id}/update",
        headers=_kopf(zwei),
        json={"note": "Fremdzugriff", "new_status": "ABGESCHLOSSEN"},
    )
    assert antwort.status_code == 404, antwort.text

    with create_engine(DB_URL).connect() as c:
        stand = c.execute(
            text(f"SELECT status, notes FROM {TABELLE} WHERE id = :i"),  # nosec B608
            {"i": meldungs_id},
        ).mappings().first()
    assert stand["status"] == "EINGEGANGEN", "Der fremde Zugriff hat den Status geaendert"
    assert stand["notes"] == [], "Der fremde Zugriff hat eine Notiz hinterlassen"


# ── Die Notiz bleibt JSON ──────────────────────────────────────────────


def test_eine_notiz_mit_anfuehrungszeichen_zerlegt_nichts(client, zwei_haeuser) -> None:
    """Zuvor stand die Notiz in einem f-String — ein `"` brach die Struktur."""
    from sqlalchemy import create_engine, text

    eins, _ = zwei_haeuser
    client.post(
        "/api/v1/compliance/hinweisgeber/reports",
        headers=_kopf(eins),
        json={"category": "DATENSCHUTZ", "description": "Ein Hinweis.", "severity": "MITTEL"},
    )
    with create_engine(DB_URL).connect() as c:
        meldungs_id = c.execute(
            text(f"SELECT id FROM {TABELLE} WHERE tenant_id = :t"),  # nosec B608
            {"t": eins},
        ).scalar()

    boshaft = 'Er sagte "nimm das Geld", dann {"status": "ABGESCHLOSSEN"} \\ und weiter'
    antwort = client.patch(
        f"/api/v1/compliance/hinweisgeber/reports/{meldungs_id}/update",
        headers=_kopf(eins),
        json={"note": boshaft},
    )
    assert antwort.status_code == 200, antwort.text

    with create_engine(DB_URL).connect() as c:
        stand = c.execute(
            text(f"SELECT status, notes FROM {TABELLE} WHERE id = :i"),  # nosec B608
            {"i": meldungs_id},
        ).mappings().first()

    assert isinstance(stand["notes"], list) and len(stand["notes"]) == 1
    # Der Wortlaut kommt unveraendert an — nicht abgeschnitten, nicht entstellt.
    assert stand["notes"][0]["note"] == boshaft
    # Und die eingebettete Struktur hat nichts umgeschaltet.
    assert stand["status"] == "EINGEGANGEN"


# ── Eine Tabelle fuer beide Wege ───────────────────────────────────────


def test_beide_endpunkte_schreiben_dieselbe_tabelle(client, zwei_haeuser) -> None:
    """Zuvor legte einer sie zur Laufzeit an, der andere bekam dauerhaft 503."""
    from sqlalchemy import create_engine, text

    eins, _ = zwei_haeuser

    kurz = client.post(
        "/api/v1/compliance/hinweisgeber/reports",
        headers=_kopf(eins),
        json={"category": "SONSTIGE", "description": "Auf dem kurzen Weg.", "severity": "NIEDRIG"},
    )
    assert kurz.status_code == 201, kurz.text

    lksg = client.post(
        "/api/v1/compliance/whistleblower/reports",
        headers=_kopf(eins),
        json={
            "category": "ARBEITSSCHUTZ",
            "description": "Auf dem LkSG-Weg, mit mindestens zehn Zeichen.",
            "anonymous": True,
        },
    )
    assert lksg.status_code in (200, 201), lksg.text

    with create_engine(DB_URL).connect() as c:
        anzahl = c.execute(
            text(f"SELECT count(*) FROM {TABELLE} WHERE tenant_id = :t"),  # nosec B608
            {"t": eins},
        ).scalar()
    assert anzahl == 2, "Ein Weg hat nicht geschrieben — die Formen sind wieder auseinander"

    # Und beide Listen sehen beide Meldungen, weil es eine Tabelle ist.
    assert len(client.get(
        "/api/v1/compliance/hinweisgeber/reports", headers=_kopf(eins)
    ).json()) == 2
    assert len(client.get(
        "/api/v1/compliance/whistleblower/reports", headers=_kopf(eins)
    ).json()) == 2


def test_der_endpunkt_legt_keine_tabelle_mehr_an() -> None:
    """Laufzeit-DDL macht das Schema von der Aufrufreihenfolge abhaengig."""
    import pathlib

    quelle = (
        pathlib.Path(__file__).resolve().parents[1]
        / "app" / "api" / "v1" / "endpoints" / "compliance_whistleblower.py"
    ).read_text(encoding="utf-8")
    # Nur ausgefuehrtes SQL zaehlt, nicht die Erwaehnung im Docstring: Die
    # erste Fassung dieses Tests schlug an der eigenen Erklaerung an.
    import re

    ohne_doku = "\n".join(
        zeile
        for zeile in quelle.splitlines()
        if not zeile.lstrip().startswith(("#", "*", "``"))
    )
    assert not re.search(r"""text\(\s*["']{1,3}\s*CREATE TABLE""", ohne_doku, re.I), (
        "Der Endpunkt legt wieder selbst eine Tabelle an"
    )
