"""
Wave 6 Paket A — Agrar-P0 Tests
DüV-Bilanz, PSM-Protokoll, API-Endpoints
"""
from __future__ import annotations

import pytest
from datetime import date
from fastapi.testclient import TestClient


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_eintrag(schlag_id: str, naehrstoff: str, menge: float) -> dict:
    return {
        "duengemittel_name": "Test-Dünger",
        "naehrstoff": naehrstoff,
        "menge_kg_ha": menge,
        "ausbringdatum": "2025-03-15",
        "schlag_id": schlag_id,
    }


# ── DüV-Bilanz Tests (11) ─────────────────────────────────────────────────────

def test_duenge_bilanz_leer_null_zufuhr():
    """Leere Einträge → Zufuhr=0, alle Saldi negativ (= Bedarf)."""
    from app.core.duenge_bilanz import DuengeBilanz, NaehrstoffTyp
    bilanz = DuengeBilanz.berechne(
        tenant_id="t1",
        schlag_id="s1",
        wirtschaftsjahr=2025,
        eintraege=[],
        bedarf_n_kg_ha=170.0,
        bedarf_p_kg_ha=60.0,
        bedarf_k_kg_ha=80.0,
    )
    n_pos = next(p for p in bilanz.positionen if p.naehrstoff == NaehrstoffTyp.STICKSTOFF)
    assert n_pos.zufuhr_kg_ha == 0.0
    assert n_pos.saldo_kg_ha == -170.0
    assert bilanz.gesamt_n_saldo_kg_ha == -170.0


def test_duenge_bilanz_ausgeglichen():
    """Zufuhr exakt gleich Bedarf → Saldo=0, keine Warnung."""
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    eintraege = [
        DuengemittelEintrag(
            duengemittel_name="KAS",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=170.0,
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
        DuengemittelEintrag(
            duengemittel_name="TSP",
            naehrstoff=NaehrstoffTyp.PHOSPHOR,
            menge_kg_ha=60.0,
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
        DuengemittelEintrag(
            duengemittel_name="K60",
            naehrstoff=NaehrstoffTyp.KALIUM,
            menge_kg_ha=80.0,
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
    ]
    bilanz = DuengeBilanz.berechne("t1", "s1", 2025, eintraege)
    for pos in bilanz.positionen:
        assert pos.saldo_kg_ha == pytest.approx(0.0)
        assert pos.ueberschuss_warnung is False
    assert bilanz.gobd_konform is True


def test_duenge_bilanz_ueberschuss_n_warnung():
    """N-Saldo > 20 kg/ha → ueberschuss_warnung=True für N-Position."""
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    eintraege = [
        DuengemittelEintrag(
            duengemittel_name="KAS",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=200.0,  # Überschuss: 200 - 170 = 30 > 20
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
    ]
    bilanz = DuengeBilanz.berechne("t1", "s1", 2025, eintraege)
    n_pos = next(p for p in bilanz.positionen if p.naehrstoff == NaehrstoffTyp.STICKSTOFF)
    assert n_pos.ueberschuss_warnung is True
    assert n_pos.saldo_kg_ha == pytest.approx(30.0)


def test_duenge_bilanz_ueberschuss_p_warnung():
    """P-Saldo > 10 kg/ha → ueberschuss_warnung=True für P-Position."""
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    eintraege = [
        DuengemittelEintrag(
            duengemittel_name="TSP",
            naehrstoff=NaehrstoffTyp.PHOSPHOR,
            menge_kg_ha=75.0,  # Überschuss: 75 - 60 = 15 > 10
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
    ]
    bilanz = DuengeBilanz.berechne("t1", "s1", 2025, eintraege)
    p_pos = next(p for p in bilanz.positionen if p.naehrstoff == NaehrstoffTyp.PHOSPHOR)
    assert p_pos.ueberschuss_warnung is True
    assert p_pos.saldo_kg_ha == pytest.approx(15.0)


def test_duenge_bilanz_gobd_konform_false_bei_ueberschuss():
    """Überschuss N > 20 → gobd_konform=False."""
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    eintraege = [
        DuengemittelEintrag(
            duengemittel_name="KAS",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=210.0,
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
    ]
    bilanz = DuengeBilanz.berechne("t1", "s1", 2025, eintraege)
    assert bilanz.gobd_konform is False


def test_duenge_bilanz_gobd_konform_true_ohne_ueberschuss():
    """Kein Überschuss → gobd_konform=True."""
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    eintraege = [
        DuengemittelEintrag(
            duengemittel_name="KAS",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=185.0,  # Saldo = 15, nicht > 20
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
    ]
    bilanz = DuengeBilanz.berechne("t1", "s1", 2025, eintraege)
    assert bilanz.gobd_konform is True


def test_duenge_bilanz_mehrere_eintraege_summiert():
    """3 N-Einträge werden korrekt zu einer Summe zusammengefasst."""
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    eintraege = [
        DuengemittelEintrag(
            duengemittel_name="KAS",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=60.0,
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
        DuengemittelEintrag(
            duengemittel_name="AHL",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=60.0,
            ausbringdatum=date(2025, 4, 1),
            schlag_id="s1",
        ),
        DuengemittelEintrag(
            duengemittel_name="Harnstoff",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=60.0,
            ausbringdatum=date(2025, 5, 1),
            schlag_id="s1",
        ),
    ]
    bilanz = DuengeBilanz.berechne("t1", "s1", 2025, eintraege)
    n_pos = next(p for p in bilanz.positionen if p.naehrstoff == NaehrstoffTyp.STICKSTOFF)
    assert n_pos.zufuhr_kg_ha == pytest.approx(180.0)
    assert n_pos.saldo_kg_ha == pytest.approx(10.0)  # 180 - 170 = 10, kein Überschuss


def test_duenge_bilanz_schlag_filter():
    """Nur Einträge für den richtigen Schlag werden gezählt."""
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    eintraege = [
        DuengemittelEintrag(
            duengemittel_name="KAS",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=100.0,
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",  # Ziel-Schlag
        ),
        DuengemittelEintrag(
            duengemittel_name="KAS",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=999.0,
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s2",  # Anderer Schlag → ignoriert
        ),
    ]
    bilanz = DuengeBilanz.berechne("t1", "s1", 2025, eintraege)
    n_pos = next(p for p in bilanz.positionen if p.naehrstoff == NaehrstoffTyp.STICKSTOFF)
    assert n_pos.zufuhr_kg_ha == pytest.approx(100.0)


def test_duenge_bilanz_n_ueberschuss_grenzwert_genau_20():
    """Exakt N-Saldo = 20 kg/ha → keine Warnung (Grenzwert nicht überschritten)."""
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    eintraege = [
        DuengemittelEintrag(
            duengemittel_name="KAS",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=190.0,  # Saldo = 20.0 (genau an der Grenze)
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
    ]
    bilanz = DuengeBilanz.berechne("t1", "s1", 2025, eintraege)
    n_pos = next(p for p in bilanz.positionen if p.naehrstoff == NaehrstoffTyp.STICKSTOFF)
    assert n_pos.saldo_kg_ha == pytest.approx(20.0)
    assert n_pos.ueberschuss_warnung is False  # > 20, nicht >= 20


def test_duenge_bilanz_n_ueberschuss_grenzwert_ueber_20():
    """N-Saldo = 20.1 kg/ha → Warnung ausgelöst."""
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    eintraege = [
        DuengemittelEintrag(
            duengemittel_name="KAS",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=190.1,  # Saldo = 20.1
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
    ]
    bilanz = DuengeBilanz.berechne("t1", "s1", 2025, eintraege)
    n_pos = next(p for p in bilanz.positionen if p.naehrstoff == NaehrstoffTyp.STICKSTOFF)
    assert n_pos.saldo_kg_ha == pytest.approx(20.1)
    assert n_pos.ueberschuss_warnung is True


def test_duenge_bilanz_schema_version():
    """schema_version=1 in allen Modellobjekten."""
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    eintraege = [
        DuengemittelEintrag(
            duengemittel_name="KAS",
            naehrstoff=NaehrstoffTyp.STICKSTOFF,
            menge_kg_ha=170.0,
            ausbringdatum=date(2025, 3, 1),
            schlag_id="s1",
        ),
    ]
    bilanz = DuengeBilanz.berechne("t1", "s1", 2025, eintraege)
    assert bilanz.schema_version == 1
    for pos in bilanz.positionen:
        assert pos.schema_version == 1
    assert eintraege[0].schema_version == 1


# ── PSM-Protokoll Tests (5) ───────────────────────────────────────────────────

def test_psm_protokoll_vollstaendig():
    """Alle Pflichtfelder vorhanden → ist_gobd_vollstaendig()=True."""
    from app.core.psm_protokoll import PsmAnwendungProtokoll
    p = PsmAnwendungProtokoll(
        protokoll_id="pid-1",
        tenant_id="t1",
        schlag_id="s1",
        anwendungsdatum=date(2025, 5, 10),
        praeparat_name="Roundup PowerFlex",
        wirkstoff="Glyphosat",
        aufwandmenge_l_ha=3.0,
        sachkunde_nr="PSM-12345",
        wasser_schutzgebiet=False,
        wartezeit_tage=14,
        flaeche_ha=5.5,
        zulassungsnummer="0066015-00",
    )
    assert p.ist_gobd_vollstaendig() is True


def test_psm_protokoll_fehlende_sachkunde():
    """sachkunde_nr leer → ist_gobd_vollstaendig()=False."""
    from app.core.psm_protokoll import PsmAnwendungProtokoll
    p = PsmAnwendungProtokoll(
        protokoll_id="pid-2",
        tenant_id="t1",
        schlag_id="s1",
        anwendungsdatum=date(2025, 5, 10),
        praeparat_name="Roundup",
        wirkstoff="Glyphosat",
        aufwandmenge_l_ha=3.0,
        sachkunde_nr="",  # Fehlend
        flaeche_ha=5.5,
    )
    assert p.ist_gobd_vollstaendig() is False


def test_psm_protokoll_wasserschutzgebiet():
    """wasser_schutzgebiet=True wird korrekt gesetzt und ausgelesen."""
    from app.core.psm_protokoll import PsmAnwendungProtokoll
    p = PsmAnwendungProtokoll(
        protokoll_id="pid-3",
        tenant_id="t1",
        schlag_id="s1",
        anwendungsdatum=date(2025, 5, 10),
        praeparat_name="Fungizid XY",
        wirkstoff="Tebuconazol",
        aufwandmenge_l_ha=1.0,
        sachkunde_nr="PSM-99999",
        wasser_schutzgebiet=True,
        flaeche_ha=2.0,
    )
    assert p.wasser_schutzgebiet is True


def test_psm_protokoll_wartezeit_optional():
    """wartezeit_tage=None ist erlaubt; Protokoll bleibt dennoch vollständig."""
    from app.core.psm_protokoll import PsmAnwendungProtokoll
    p = PsmAnwendungProtokoll(
        protokoll_id="pid-4",
        tenant_id="t1",
        schlag_id="s1",
        anwendungsdatum=date(2025, 5, 10),
        praeparat_name="Herbizid Z",
        wirkstoff="Fluroxypyr",
        aufwandmenge_l_ha=1.5,
        sachkunde_nr="PSM-77777",
        wartezeit_tage=None,
        flaeche_ha=10.0,
    )
    assert p.wartezeit_tage is None
    assert p.ist_gobd_vollstaendig() is True


def test_psm_protokoll_schema_version():
    """schema_version=1 standardmäßig gesetzt."""
    from app.core.psm_protokoll import PsmAnwendungProtokoll
    p = PsmAnwendungProtokoll(
        protokoll_id="pid-5",
        tenant_id="t1",
        schlag_id="s1",
        anwendungsdatum=date(2025, 5, 10),
        praeparat_name="Test",
        wirkstoff="TestWirkstoff",
        aufwandmenge_l_ha=2.0,
        sachkunde_nr="PSM-11111",
        flaeche_ha=3.0,
    )
    assert p.schema_version == 1


# ── API Tests (4) ─────────────────────────────────────────────────────────────

AUTH_HEADERS = {"Authorization": "Bearer dev-token"}


@pytest.fixture(scope="module")
def client():
    from main import app
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


def test_api_duenge_bilanz_post(client):
    """POST /agrar/p0/duenge-bilanz gibt bilanz_id und gobd_konform zurück."""
    payload = {
        "tenant_id": "t1",
        "schlag_id": "s1",
        "wirtschaftsjahr": 2025,
        "eintraege": [
            {
                "duengemittel_name": "KAS",
                "naehrstoff": "N",
                "menge_kg_ha": 170.0,
                "ausbringdatum": "2025-03-15",
                "schlag_id": "s1",
            }
        ],
    }
    resp = client.post("/api/v1/agrar/p0/duenge-bilanz", json=payload, headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "bilanz_id" in data
    assert "gobd_konform" in data
    assert data["schema_version"] == 1


def test_api_psm_protokoll_post(client):
    """POST /agrar/p0/psm-protokoll gibt 201 + protokoll_id zurück."""
    payload = {
        "tenant_id": "t1",
        "schlag_id": "s1",
        "anwendungsdatum": "2025-05-10",
        "praeparat_name": "Roundup PowerFlex",
        "wirkstoff": "Glyphosat",
        "aufwandmenge_l_ha": 3.0,
        "sachkunde_nr": "PSM-12345",
        "wasser_schutzgebiet": False,
        "wartezeit_tage": 14,
        "flaeche_ha": 5.5,
        "zulassungsnummer": "0066015-00",
    }
    resp = client.post("/api/v1/agrar/p0/psm-protokoll", json=payload, headers=AUTH_HEADERS)
    assert resp.status_code == 201
    data = resp.json()
    assert "protokoll_id" in data
    assert data["gobd_vollstaendig"] is True
    assert data["schema_version"] == 1


def test_api_schlag_flik_get(client):
    """GET /agrar/p0/schlag/{id}/flik gibt schema_version=1 zurück."""
    resp = client.get("/api/v1/agrar/p0/schlag/schlag-abc-123/flik", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["schlag_id"] == "schlag-abc-123"
    assert data["schema_version"] == 1
    assert "flik_id" in data
    assert "geometry_wkt" in data
    assert "nuts3_region" in data


def test_api_duenge_bilanz_ueberschuss_warnung(client):
    """POST /agrar/p0/duenge-bilanz mit Überschuss → gobd_konform=False erkennbar."""
    payload = {
        "tenant_id": "t1",
        "schlag_id": "s1",
        "wirtschaftsjahr": 2025,
        "eintraege": [
            {
                "duengemittel_name": "KAS",
                "naehrstoff": "N",
                "menge_kg_ha": 210.0,  # Überschuss: 210 - 170 = 40 > 20
                "ausbringdatum": "2025-03-15",
                "schlag_id": "s1",
            }
        ],
    }
    resp = client.post("/api/v1/agrar/p0/duenge-bilanz", json=payload, headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["gobd_konform"] is False
    # Prüfe ob Warnung in den Positionen vorhanden
    positionen = data["positionen"]
    n_pos = next(p for p in positionen if p["naehrstoff"] == "N")
    assert n_pos["ueberschuss_warnung"] is True
