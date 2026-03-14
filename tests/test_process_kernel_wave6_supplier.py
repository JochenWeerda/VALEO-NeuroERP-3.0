"""
Wave 6 Paket B — Tests: Supplier Portal, Contract Pricing, Silo Operations
"""
from __future__ import annotations

import pytest
from datetime import date, datetime
import uuid

# ── PriceMatrix Tests ─────────────────────────────────────────────────────────

from app.core.contract_pricing import (
    PriceMatrix,
    PriceMatrixEintrag,
    PreisTyp,
    KonContractLot,
    KonContractLotStore,
)


def _make_matrix() -> PriceMatrix:
    eintraege = [
        PriceMatrixEintrag(
            sorte="Weizen",
            qualitaet="A",
            preis_eur_t=220.0,
            gueltig_von=date(2026, 1, 1),
            gueltig_bis=date(2026, 12, 31),
        ),
        PriceMatrixEintrag(
            sorte="Weizen",
            qualitaet="B",
            preis_eur_t=200.0,
            gueltig_von=date(2026, 1, 1),
            gueltig_bis=date(2026, 12, 31),
        ),
        PriceMatrixEintrag(
            sorte="Gerste",
            qualitaet="A",
            preis_eur_t=180.0,
            gueltig_von=date(2026, 6, 1),
            gueltig_bis=date(2026, 9, 30),
        ),
    ]
    return PriceMatrix(
        matrix_id=str(uuid.uuid4()),
        tenant_id="tenant-1",
        wirtschaftsjahr=2026,
        eintraege=eintraege,
    )


def test_price_matrix_get_preis_gefunden():
    matrix = _make_matrix()
    preis = matrix.get_preis("Weizen", "A", date(2026, 7, 1))
    assert preis == 220.0


def test_price_matrix_get_preis_nicht_gefunden():
    matrix = _make_matrix()
    # Datum liegt vor Gültigkeitsbeginn von Gerste
    preis = matrix.get_preis("Gerste", "A", date(2026, 5, 31))
    assert preis is None


def test_price_matrix_alle_preise_stichtag():
    matrix = _make_matrix()
    # Am 2026-07-01 gelten Weizen A, Weizen B und Gerste A
    result = matrix.alle_preise_am_stichtag(date(2026, 7, 1))
    assert len(result) == 3


def test_price_matrix_sorte_filter():
    matrix = _make_matrix()
    # Nur Weizen-Einträge am 2026-03-01 (Gerste noch nicht gültig)
    result = matrix.alle_preise_am_stichtag(date(2026, 3, 1))
    sorten = {e.sorte for e in result}
    assert sorten == {"Weizen"}
    assert len(result) == 2


def test_price_matrix_schema_version():
    matrix = _make_matrix()
    assert matrix.schema_version == 1
    for e in matrix.eintraege:
        assert e.schema_version == 1


def test_kontract_lot_wert_berechnung():
    lot = KonContractLot(
        lot_id=str(uuid.uuid4()),
        tenant_id="t1",
        kontrakt_id="k1",
        lieferant_id="l1",
        menge_t=100.0,
        sorte="Weizen",
        qualitaet="A",
        vereinbarter_preis_eur_t=220.0,
        preis_typ=PreisTyp.FEST,
        lieferdatum_soll=date(2026, 8, 1),
    )
    assert lot.wert_eur == pytest.approx(22000.0)


# ── KonContractLot Tests ──────────────────────────────────────────────────────

def test_lot_ist_geliefert_false():
    lot = KonContractLot(
        lot_id=str(uuid.uuid4()),
        tenant_id="t1",
        kontrakt_id="k1",
        lieferant_id="l1",
        menge_t=50.0,
        sorte="Gerste",
        qualitaet="B",
        vereinbarter_preis_eur_t=180.0,
        preis_typ=PreisTyp.FEST,
        lieferdatum_soll=date(2026, 8, 15),
    )
    assert lot.ist_geliefert is False


def test_lot_ist_geliefert_true():
    lot = KonContractLot(
        lot_id=str(uuid.uuid4()),
        tenant_id="t1",
        kontrakt_id="k1",
        lieferant_id="l1",
        menge_t=50.0,
        sorte="Gerste",
        qualitaet="B",
        vereinbarter_preis_eur_t=180.0,
        preis_typ=PreisTyp.FEST,
        lieferdatum_soll=date(2026, 8, 15),
        lieferdatum_ist=date(2026, 8, 14),
    )
    assert lot.ist_geliefert is True


def test_lot_ist_abgeschlossen():
    lot = KonContractLot(
        lot_id=str(uuid.uuid4()),
        tenant_id="t1",
        kontrakt_id="k1",
        lieferant_id="l1",
        menge_t=50.0,
        sorte="Gerste",
        qualitaet="B",
        vereinbarter_preis_eur_t=180.0,
        preis_typ=PreisTyp.FEST,
        lieferdatum_soll=date(2026, 8, 15),
        lieferdatum_ist=date(2026, 8, 14),
        abgerechnet=True,
    )
    assert lot.ist_abgeschlossen is True


def test_lot_store_by_kontrakt():
    store = KonContractLotStore()
    lot1 = KonContractLot(
        lot_id=str(uuid.uuid4()),
        tenant_id="t1",
        kontrakt_id="k-100",
        lieferant_id="l1",
        menge_t=30.0,
        sorte="Weizen",
        qualitaet="A",
        vereinbarter_preis_eur_t=220.0,
        preis_typ=PreisTyp.FEST,
        lieferdatum_soll=date(2026, 8, 1),
    )
    lot2 = KonContractLot(
        lot_id=str(uuid.uuid4()),
        tenant_id="t1",
        kontrakt_id="k-200",
        lieferant_id="l2",
        menge_t=70.0,
        sorte="Gerste",
        qualitaet="A",
        vereinbarter_preis_eur_t=180.0,
        preis_typ=PreisTyp.FEST,
        lieferdatum_soll=date(2026, 8, 20),
    )
    store.add(lot1)
    store.add(lot2)
    result = store.by_kontrakt("k-100")
    assert len(result) == 1
    assert result[0].kontrakt_id == "k-100"


# ── SiloCell Tests ────────────────────────────────────────────────────────────

from app.core.silo_operations import (
    SiloCell,
    SiloCellStore,
    SiloStatus,
    TransferTyp,
)


def _make_zelle(kapazitaet_t: float = 1000.0, eingelagert: float = 0.0) -> SiloCell:
    return SiloCell(
        silo_id=str(uuid.uuid4()),
        tenant_id="tenant-silo",
        bezeichnung="Zelle A1",
        kapazitaet_t=kapazitaet_t,
        aktuell_eingelagert_t=eingelagert,
    )


def test_silo_fuellstand_leer():
    zelle = _make_zelle(1000.0, 0.0)
    assert zelle.fuellstand_pct == pytest.approx(0.0)


def test_silo_fuellstand_halbvoll():
    zelle = _make_zelle(1000.0, 500.0)
    assert zelle.fuellstand_pct == pytest.approx(50.0)


def test_silo_status_aktualisierung_leer():
    zelle = _make_zelle(1000.0, 0.0)
    zelle.aktualisiere_status()
    assert zelle.status == SiloStatus.LEER


def test_silo_status_aktualisierung_voll():
    zelle = _make_zelle(1000.0, 960.0)  # 96% >= 95%
    zelle.aktualisiere_status()
    assert zelle.status == SiloStatus.VOLL


def test_silo_einlagern():
    store = SiloCellStore()
    zelle = _make_zelle(1000.0, 0.0)
    store.add_zelle(zelle)
    transfer = store.einlagern(zelle.silo_id, 300.0, "Weizen", beleg_nr="AN-001")
    assert transfer.menge_t == pytest.approx(300.0)
    assert transfer.transfer_typ == TransferTyp.EINLAGERUNG
    assert store.get_zelle(zelle.silo_id).aktuell_eingelagert_t == pytest.approx(300.0)


def test_silo_auslagern():
    store = SiloCellStore()
    zelle = _make_zelle(1000.0, 500.0)
    zelle.sorte = "Gerste"
    store.add_zelle(zelle)
    transfer = store.auslagern(zelle.silo_id, 200.0, beleg_nr="LS-042")
    assert transfer.menge_t == pytest.approx(200.0)
    assert transfer.transfer_typ == TransferTyp.AUSLAGERUNG
    assert store.get_zelle(zelle.silo_id).aktuell_eingelagert_t == pytest.approx(300.0)


def test_silo_einlagern_kapazitaet_ueberschritten():
    store = SiloCellStore()
    zelle = _make_zelle(100.0, 0.0)
    store.add_zelle(zelle)
    with pytest.raises(ValueError, match="Kapazität"):
        store.einlagern(zelle.silo_id, 200.0, "Weizen")


def test_silo_auslagern_zuviel():
    store = SiloCellStore()
    zelle = _make_zelle(1000.0, 100.0)
    zelle.sorte = "Weizen"
    store.add_zelle(zelle)
    with pytest.raises(ValueError, match="Nicht genug"):
        store.auslagern(zelle.silo_id, 500.0)


def test_silo_gesamtbestand():
    store = SiloCellStore()
    z1 = SiloCell(
        silo_id=str(uuid.uuid4()),
        tenant_id="t-silo",
        bezeichnung="Z1",
        kapazitaet_t=1000.0,
        aktuell_eingelagert_t=400.0,
    )
    z2 = SiloCell(
        silo_id=str(uuid.uuid4()),
        tenant_id="t-silo",
        bezeichnung="Z2",
        kapazitaet_t=500.0,
        aktuell_eingelagert_t=250.0,
    )
    z_other = SiloCell(
        silo_id=str(uuid.uuid4()),
        tenant_id="other-tenant",
        bezeichnung="Z-other",
        kapazitaet_t=500.0,
        aktuell_eingelagert_t=500.0,
    )
    store.add_zelle(z1)
    store.add_zelle(z2)
    store.add_zelle(z_other)
    assert store.gesamtbestand_t("t-silo") == pytest.approx(650.0)


def test_silo_transfers_protokolliert():
    store = SiloCellStore()
    zelle = _make_zelle(1000.0, 0.0)
    store.add_zelle(zelle)
    store.einlagern(zelle.silo_id, 100.0, "Weizen", beleg_nr="AN-010")
    store.einlagern(zelle.silo_id, 200.0, "Weizen", beleg_nr="AN-011")
    transfers = store.transfers_fuer_silo(zelle.silo_id)
    assert len(transfers) == 2
    beleg_nrs = {t.beleg_nr for t in transfers}
    assert "AN-010" in beleg_nrs
    assert "AN-011" in beleg_nrs


# ── API Tests ─────────────────────────────────────────────────────────────────

from fastapi.testclient import TestClient
from main import app

client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
AUTH_HEADERS = {"Authorization": "Bearer dev-token"}
TENANT_HEADER = {"X-Tenant-ID": "default"}
COMMON_HEADERS = {**AUTH_HEADERS, **TENANT_HEADER}


def test_api_price_matrix_post():
    payload = {
        "tenant_id": "tenant-test",
        "wirtschaftsjahr": 2026,
        "eintraege": [
            {
                "sorte": "Weizen",
                "qualitaet": "A",
                "preis_eur_t": 220.0,
                "gueltig_von": "2026-01-01",
                "gueltig_bis": "2026-12-31",
                "preis_typ": "fest",
            }
        ],
    }
    response = client.post(
        "/api/v1/contract-pricing/price-matrix", json=payload, headers=COMMON_HEADERS
    )
    assert response.status_code == 201
    data = response.json()
    assert "matrix_id" in data
    assert data["tenant_id"] == "tenant-test"
    assert data["wirtschaftsjahr"] == 2026
    assert len(data["eintraege"]) == 1


def test_api_lot_post():
    payload = {
        "tenant_id": "tenant-test",
        "kontrakt_id": "k-42",
        "lieferant_id": "lief-007",
        "menge_t": 75.0,
        "sorte": "Gerste",
        "qualitaet": "B",
        "vereinbarter_preis_eur_t": 185.0,
        "preis_typ": "fest",
        "lieferdatum_soll": "2026-08-15",
    }
    response = client.post(
        "/api/v1/contract-pricing/lots", json=payload, headers=COMMON_HEADERS
    )
    assert response.status_code == 201
    data = response.json()
    assert "lot_id" in data
    assert data["kontrakt_id"] == "k-42"
    assert data["menge_t"] == pytest.approx(75.0)


def test_api_supplier_lieferungen_get():
    response = client.get(
        "/api/v1/supplier-portal/lieferanten/lief-001/lieferungen",
        headers=COMMON_HEADERS,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_api_supplier_preisauskunft():
    response = client.get(
        "/api/v1/supplier-portal/preisauskunft",
        params={"sorte": "Weizen", "qualitaet": "A", "stichtag": "2026-07-01"},
        headers=COMMON_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sorte"] == "Weizen"
    assert data["qualitaet"] == "A"
    assert data["verfuegbar"] is False
