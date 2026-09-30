"""Die Kasse erfindet keine Zahlarten.

Zwei Lagen, die vorher gleich aussahen und es nicht sind:

- **Nichts eingerichtet.** Ein Haus hat noch keine Zahlart gepflegt. Dann ist
  eine Startkonfiguration (Bargeld, Karte, SEPA) eine Hilfe.
- **Die Datenbank antwortet nicht.** Dann ist dieselbe Liste eine Luege: Ein
  Kassierer waehlt eine Zahlart, von der niemand weiss, ob das Haus sie
  annimmt.

Zuvor lieferte der Endpunkt in **beiden** Faellen dieselben drei Zahlarten.
Jetzt nur noch im ersten; der zweite ist ein 503.

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


@pytest.fixture(scope="module")
def client():
    from sqlalchemy import create_engine, text

    try:
        with create_engine(DB_URL).connect() as conn:
            vorhanden = conn.execute(
                text("SELECT to_regclass('domain_pos.payment_methods')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration pos_zahlarten_aktionen_20260930 nicht angewandt")

    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def mandant():
    from sqlalchemy import create_engine, text

    name = f"test-{uuid.uuid4().hex[:8]}"
    engine = create_engine(DB_URL)
    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :d, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": name, "d": f"{name}.test"},
        )
    try:
        yield name
    finally:
        with engine.begin() as v:
            for sql in (
                "DELETE FROM domain_pos.promotions WHERE tenant_id = :t",
                "DELETE FROM domain_pos.payment_methods WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                v.execute(text(sql), {"t": name})


def _kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
    }


def test_ohne_eingerichtete_zahlart_kommt_die_startkonfiguration(client, mandant) -> None:
    """Ein neues Haus soll kassieren koennen, bevor jemand etwas pflegt."""
    antwort = client.get("/api/v1/pos/payment-methods", headers=_kopf(mandant))
    assert antwort.status_code == 200, antwort.text
    kuerzel = {z["method_code"] for z in antwort.json()}
    assert kuerzel == {"BAR", "KARTE", "SEPA"}


def test_eine_gepflegte_zahlart_verdraengt_die_startkonfiguration(client, mandant) -> None:
    from sqlalchemy import create_engine, text

    with create_engine(DB_URL).begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_pos.payment_methods "
                "(id, tenant_id, method_code, name, is_active) "
                "VALUES (:id, :t, 'GUTSCHEIN', 'Gutschein', TRUE)"
            ),
            {"id": str(uuid.uuid4()), "t": mandant},
        )

    antwort = client.get("/api/v1/pos/payment-methods", headers=_kopf(mandant))
    assert antwort.status_code == 200, antwort.text
    kuerzel = {z["method_code"] for z in antwort.json()}
    assert kuerzel == {"GUTSCHEIN"}, (
        "Die Startkonfiguration ueberlagert die gepflegte Zahlart"
    )


def test_die_zahlart_des_anderen_hauses_erscheint_nicht(client, mandant) -> None:
    from sqlalchemy import create_engine, text

    fremd = f"test-{uuid.uuid4().hex[:8]}"
    engine = create_engine(DB_URL)
    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :d, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": fremd, "d": f"{fremd}.test"},
        )
        v.execute(
            text(
                "INSERT INTO domain_pos.payment_methods "
                "(id, tenant_id, method_code, name, is_active) "
                "VALUES (:id, :t, 'FIRMENKARTE', 'Firmenkarte', TRUE)"
            ),
            {"id": str(uuid.uuid4()), "t": fremd},
        )
    try:
        antwort = client.get("/api/v1/pos/payment-methods", headers=_kopf(mandant))
        assert "FIRMENKARTE" not in {z["method_code"] for z in antwort.json()}
    finally:
        with engine.begin() as v:
            v.execute(
                text("DELETE FROM domain_pos.payment_methods WHERE tenant_id = :t"),
                {"t": fremd},
            )
            v.execute(text("DELETE FROM domain_shared.tenants WHERE id = :t"), {"t": fremd})


def test_eine_datenbankstoerung_erfindet_keine_zahlart(client, mandant) -> None:
    """Der Kern: Eine Stoerung ist keine Konfiguration.

    Die Stoerung wird echt ausgeloest — die Spalte, nach der der Endpunkt
    filtert, wird kurzzeitig umbenannt. Zuvor lieferte der Endpunkt hier
    BAR/KARTE/SEPA, als waeren sie eingerichtet.
    """
    from sqlalchemy import create_engine, text

    engine = create_engine(DB_URL)
    with engine.begin() as v:
        v.execute(
            text(
                "ALTER TABLE domain_pos.payment_methods "
                "RENAME COLUMN is_active TO is_active_probe"
            )
        )
    try:
        antwort = client.get("/api/v1/pos/payment-methods", headers=_kopf(mandant))
        assert antwort.status_code == 503, antwort.text
        assert "pos_zahlarten_aktionen" in antwort.json()["detail"]
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "ALTER TABLE domain_pos.payment_methods "
                    "RENAME COLUMN is_active_probe TO is_active"
                )
            )


def test_der_endpunkt_legt_keine_tabelle_mehr_an() -> None:
    """Laufzeit-DDL macht das Schema davon abhaengig, ob jemand kassiert hat."""
    import pathlib
    import re

    quelle = (
        pathlib.Path(__file__).resolve().parents[1]
        / "app" / "api" / "v1" / "endpoints" / "pos_payments.py"
    ).read_text(encoding="utf-8")
    ohne_doku = "\n".join(
        zeile for zeile in quelle.splitlines()
        if not zeile.lstrip().startswith(("#", "*", "``"))
    )
    assert not re.search(r"""text\(\s*["']{1,3}\s*CREATE TABLE""", ohne_doku, re.I), (
        "Der Endpunkt legt wieder selbst eine Tabelle an"
    )
