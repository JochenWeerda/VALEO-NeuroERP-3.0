"""
Wave 7 Paket B — Domain Contract Tests
Reklamation, Ausnahme-Workflow-Extension, Preisabsicherung HedgeReference, Silo-Protokolle
"""
from __future__ import annotations
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient

# ──────────────────────────────────────────────────────────────────────────────
# Imports from core modules
# ──────────────────────────────────────────────────────────────────────────────
from app.core.reklamation import (
    Reklamation, ReklamationStore, ReklamationZustandsmaschine,
    ReklamationsTyp, ReklamationsStatus, ReklamationsPosition,
)
from app.core.exception_workflow_extension import (
    AusnahmeKategorie, AusnahmeStatus, AusnahmeAntrag,
    AusnahmeGenehmigungsregel, DEFAULT_AUSNAHME_REGELN, pruefe_ausnahme_notwendig,
)
from app.core.price_hedge import (
    HedgeReference, HedgeTyp, HedgeStatus, HedgeStore,
    TerminmarktProdukt, KontraktHedgeBindung, berechne_hedge_quote,
)
from app.core.silo_protokolle import (
    SiloReinigungsprotokoll, TrocknungsProtokoll, SiloProtokolleStore,
    ReinigungsArt,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _make_position(**kwargs) -> ReklamationsPosition:
    defaults = dict(
        artikel_id="ART-001",
        beanstandete_menge=100.0,
        anerkannte_menge=0.0,
        beanstandeter_wert_eur=500.0,
        begruendung="Schimmelbefall",
    )
    defaults.update(kwargs)
    return ReklamationsPosition(**defaults)


def _make_reklamation(**kwargs) -> Reklamation:
    defaults = dict(
        reklamation_id="REK-001",
        tenant_id="TENANT-A",
        lieferant_id="LF-001",
        typ=ReklamationsTyp.QUALITAET,
        positionen=[_make_position()],
        zustaendiger="Max Muster",
        frist_datum=date(2026, 4, 1),
        erstellt_am=datetime(2026, 3, 12, 10, 0),
    )
    defaults.update(kwargs)
    return Reklamation(**defaults)


def _make_hedge(**kwargs) -> HedgeReference:
    defaults = dict(
        hedge_id="HG-001",
        tenant_id="TENANT-A",
        produkt=TerminmarktProdukt.WEIZEN_MATIF,
        typ=HedgeTyp.SHORT,
        menge_t=100.0,
        basis_preis_eur_t=200.0,
        verfall_datum=date(2026, 9, 30),
    )
    defaults.update(kwargs)
    return HedgeReference(**defaults)


def _make_reinigungsprotokoll(**kwargs) -> SiloReinigungsprotokoll:
    defaults = dict(
        protokoll_id="REIN-001",
        silo_id="SILO-01",
        tenant_id="TENANT-A",
        datum=date(2026, 3, 12),
        vorige_ware="Weizen",
        naechste_ware="Gerste",
        reinigungsart=ReinigungsArt.HOCHDRUCK,
        durchgefuehrt_von="Hans Meier",
    )
    defaults.update(kwargs)
    return SiloReinigungsprotokoll(**defaults)


def _make_trocknungsprotokoll(**kwargs) -> TrocknungsProtokoll:
    defaults = dict(
        lauf_id="TR-001",
        silo_id="SILO-01",
        tenant_id="TENANT-A",
        charge_id="CHG-001",
        sorte="A-Weizen",
        eingang_feuchte_pct=20.0,
        ausgang_feuchte_pct=14.0,
        eingang_temp_c=18.0,
        ausgang_temp_c=12.0,
        energie_kwh=1000.0,
        dauer_h=8.0,
        getrocknet_t=10.0,
        start_zeitpunkt=datetime(2026, 3, 12, 6, 0),
    )
    defaults.update(kwargs)
    return TrocknungsProtokoll(**defaults)


# ══════════════════════════════════════════════════════════════════════════════
# Reklamation Tests (8 tests)
# ══════════════════════════════════════════════════════════════════════════════

def test_reklamation_erstellen():
    """Reklamation wird erstellt mit status=OFFEN."""
    rek = _make_reklamation()
    assert rek.reklamation_id == "REK-001"
    assert rek.status == ReklamationsStatus.OFFEN
    assert rek.schema_version == 1


def test_reklamation_gesamtwert_beanstandet():
    """Summe der Positionswerte wird korrekt berechnet."""
    pos1 = _make_position(beanstandeter_wert_eur=300.0)
    pos2 = _make_position(artikel_id="ART-002", beanstandeter_wert_eur=700.0)
    rek = _make_reklamation(positionen=[pos1, pos2])
    assert rek.gesamtwert_beanstandet_eur == pytest.approx(1000.0)


def test_reklamation_transition_offen_zu_in_pruefung():
    """Übergang OFFEN → IN_PRUEFUNG ist gültig und löst keinen Fehler aus."""
    rek = _make_reklamation()
    result = ReklamationZustandsmaschine.transition(rek, ReklamationsStatus.IN_PRUEFUNG)
    assert result.status == ReklamationsStatus.IN_PRUEFUNG


def test_reklamation_transition_ungueltig():
    """Übergang OFFEN → GESCHLOSSEN ist ungültig und wirft ValueError."""
    rek = _make_reklamation()
    with pytest.raises(ValueError, match="Ungültiger Übergang"):
        ReklamationZustandsmaschine.transition(rek, ReklamationsStatus.GESCHLOSSEN)


def test_reklamation_transition_geschlossen_gesperrt():
    """Übergang aus GESCHLOSSEN heraus ist für jeden Zielstatus gesperrt."""
    rek = _make_reklamation(status=ReklamationsStatus.GESCHLOSSEN)
    with pytest.raises(ValueError):
        ReklamationZustandsmaschine.transition(rek, ReklamationsStatus.OFFEN)


def test_reklamation_ist_abgeschlossen_false():
    """Reklamation mit Status OFFEN ist nicht abgeschlossen."""
    rek = _make_reklamation()
    assert rek.ist_abgeschlossen is False


def test_reklamation_ist_abgeschlossen_true():
    """Reklamation mit Status GESCHLOSSEN ist abgeschlossen."""
    rek = _make_reklamation(status=ReklamationsStatus.GESCHLOSSEN)
    assert rek.ist_abgeschlossen is True


def test_reklamation_store_by_lieferant():
    """ReklamationStore.by_lieferant filtert korrekt nach lieferant_id."""
    store = ReklamationStore()
    rek_a = _make_reklamation(reklamation_id="RK-A", lieferant_id="LF-001")
    rek_b = _make_reklamation(reklamation_id="RK-B", lieferant_id="LF-002")
    store.add(rek_a)
    store.add(rek_b)
    result = store.by_lieferant("LF-001")
    assert len(result) == 1
    assert result[0].reklamation_id == "RK-A"


# ══════════════════════════════════════════════════════════════════════════════
# Ausnahme Tests (5 tests)
# ══════════════════════════════════════════════════════════════════════════════

def test_ausnahme_unter_schwellenwert():
    """Preis-Ausnahme unter 5000 EUR erzeugt keinen AusnahmeAntrag (None)."""
    result = pruefe_ausnahme_notwendig(
        kategorie=AusnahmeKategorie.PREIS_AUSNAHME,
        betrag_eur=4000.0,
        workflow_instance_id="WF-001",
        beantragende_rolle="trader",
    )
    assert result is None


def test_ausnahme_ueber_schwellenwert():
    """Preis-Ausnahme über 5000 EUR erzeugt einen AusnahmeAntrag."""
    result = pruefe_ausnahme_notwendig(
        kategorie=AusnahmeKategorie.PREIS_AUSNAHME,
        betrag_eur=6000.0,
        workflow_instance_id="WF-002",
        beantragende_rolle="trader",
    )
    assert result is not None
    assert isinstance(result, AusnahmeAntrag)
    assert result.kategorie == AusnahmeKategorie.PREIS_AUSNAHME
    assert result.schwellenwert_ueberschritten is True
    assert result.status == AusnahmeStatus.BEANTRAGT
    assert result.schema_version == 1


def test_ausnahme_sicherheit_immer():
    """Sicherheits-Ausnahme wird auch bei minimalem Betrag (0.01 EUR) ausgelöst."""
    result = pruefe_ausnahme_notwendig(
        kategorie=AusnahmeKategorie.SICHERHEITS_AUSNAHME,
        betrag_eur=0.01,
        workflow_instance_id="WF-003",
        beantragende_rolle="operator",
    )
    assert result is not None
    assert result.kategorie == AusnahmeKategorie.SICHERHEITS_AUSNAHME


def test_ausnahme_antrag_genehmigen():
    """genehmigen() setzt genehmigt_von und Status GENEHMIGT."""
    antrag = AusnahmeAntrag(
        antrag_id="ANT-001",
        workflow_instance_id="WF-004",
        kategorie=AusnahmeKategorie.PREIS_AUSNAHME,
        begruendung="Sonderkonditionen",
        beantragende_rolle="trader",
        schwellenwert_ueberschritten=True,
        betrag_eur=7500.0,
    )
    antrag.genehmigen("head_of_trading_user")
    assert antrag.status == AusnahmeStatus.GENEHMIGT
    assert antrag.genehmigt_von == "head_of_trading_user"
    assert antrag.genehmigt_am is not None


def test_ausnahme_antrag_ablehnen():
    """ablehnen() setzt Status ABGELEHNT."""
    antrag = AusnahmeAntrag(
        antrag_id="ANT-002",
        workflow_instance_id="WF-005",
        kategorie=AusnahmeKategorie.MENGEN_AUSNAHME,
        begruendung="Überschreitung",
        beantragende_rolle="trader",
        schwellenwert_ueberschritten=True,
        betrag_eur=12000.0,
    )
    antrag.ablehnen()
    assert antrag.status == AusnahmeStatus.ABGELEHNT


# ══════════════════════════════════════════════════════════════════════════════
# HedgeReference Tests (8 tests)
# ══════════════════════════════════════════════════════════════════════════════

def test_hedge_wert_eur():
    """wert_eur = menge_t * basis_preis_eur_t."""
    hedge = _make_hedge(menge_t=100.0, basis_preis_eur_t=200.0)
    assert hedge.wert_eur == pytest.approx(20000.0)


def test_hedge_ist_aktiv():
    """Hedge mit Status OFFEN ist aktiv."""
    hedge = _make_hedge()
    assert hedge.ist_aktiv is True


def test_hedge_ist_nicht_aktiv():
    """Hedge mit Status GESCHLOSSEN ist nicht aktiv."""
    hedge = _make_hedge(status=HedgeStatus.GESCHLOSSEN)
    assert hedge.ist_aktiv is False


def test_hedge_quote_null():
    """berechne_hedge_quote mit 0 Kontraktmenge ergibt 0%."""
    assert berechne_hedge_quote(0.0, 50.0) == pytest.approx(0.0)


def test_hedge_quote_vollstaendig():
    """Gleiche Mengen ergeben 100% Absicherungsquote."""
    assert berechne_hedge_quote(100.0, 100.0) == pytest.approx(100.0)


def test_hedge_quote_teilgesichert():
    """50t Hedge auf 100t Kontrakt ergibt 50%."""
    assert berechne_hedge_quote(100.0, 50.0) == pytest.approx(50.0)


def test_hedge_quote_uebersicherung_cap():
    """150t Hedge auf 100t Kontrakt wird auf max 100% gekappt."""
    assert berechne_hedge_quote(100.0, 150.0) == pytest.approx(100.0)


def test_kontrakt_hedge_bindung_quote():
    """KontraktHedgeBindung.hedge_quote_pct berechnet korrekte Quote."""
    bindung = KontraktHedgeBindung(
        bindung_id="BIND-001",
        tenant_id="TENANT-A",
        lot_id="LOT-001",
        kontrakt_id="KON-001",
        hedge_ids=["HG-001"],
        lot_menge_t=200.0,
        gesicherte_menge_t=150.0,
    )
    assert bindung.hedge_quote_pct == pytest.approx(75.0)
    assert bindung.ist_vollstaendig_gesichert is False


# ══════════════════════════════════════════════════════════════════════════════
# Silo-Protokoll Tests (5 tests)
# ══════════════════════════════════════════════════════════════════════════════

def test_reinigungsprotokoll_gobd_vollstaendig():
    """Vollständiges Reinigungsprotokoll besteht GoBD-Prüfung."""
    protokoll = _make_reinigungsprotokoll()
    assert protokoll.ist_gobd_vollstaendig() is True


def test_reinigungsprotokoll_fehlend():
    """Reinigungsprotokoll ohne durchgefuehrt_von besteht GoBD-Prüfung nicht."""
    protokoll = _make_reinigungsprotokoll(durchgefuehrt_von="")
    assert protokoll.ist_gobd_vollstaendig() is False


def test_trocknungsprotokoll_effekt():
    """Trocknungseffekt: eingang 20%, ausgang 14% → effekt = 6 Prozentpunkte."""
    protokoll = _make_trocknungsprotokoll(eingang_feuchte_pct=20.0, ausgang_feuchte_pct=14.0)
    assert protokoll.trocknungseffekt_pct == pytest.approx(6.0)


def test_trocknungsprotokoll_energie_je_t():
    """Energieverbrauch: 1000 kWh / 10t = 100 kWh/t."""
    protokoll = _make_trocknungsprotokoll(energie_kwh=1000.0, getrocknet_t=10.0)
    assert protokoll.energie_je_t_kwh == pytest.approx(100.0)


def test_trocknungsprotokoll_wirtschaftlich():
    """80 kWh/t bei max 100 kWh/t ist wirtschaftlich."""
    protokoll = _make_trocknungsprotokoll(energie_kwh=800.0, getrocknet_t=10.0)
    # energie_je_t = 80.0
    assert protokoll.ist_wirtschaftlich(max_kwh_je_t=100.0) is True


# ══════════════════════════════════════════════════════════════════════════════
# API Tests (2 tests)
# ══════════════════════════════════════════════════════════════════════════════

AUTH_HEADERS = {"Authorization": "Bearer dev-token"}


@pytest.fixture(scope="module")
def client():
    from main import app
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


def test_api_reklamation_post(client):
    """POST /api/v1/reklamationen gibt 201 mit reklamation_id zurück."""
    payload = {
        "tenant_id": "TENANT-TEST",
        "lieferant_id": "LF-TEST-001",
        "typ": "qualitaet",
        "positionen": [
            {
                "artikel_id": "ART-001",
                "beanstandete_menge": 50.0,
                "anerkannte_menge": 0.0,
                "beanstandeter_wert_eur": 250.0,
                "begruendung": "Feuchte zu hoch",
            }
        ],
        "zustaendiger": "Anna Beispiel",
        "frist_datum": "2026-04-30",
    }
    response = client.post("/api/v1/reklamationen", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 201
    data = response.json()
    assert "reklamation_id" in data
    assert data["status"] == "offen"
    assert data["schema_version"] == 1


def test_api_hedge_quote_get(client):
    """GET /api/v1/price-hedge/quote mit kontrakt_menge_t=100, hedge_menge_t=50 → 50%."""
    response = client.get("/api/v1/price-hedge/quote", params={"kontrakt_menge_t": 100.0, "hedge_menge_t": 50.0}, headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["hedge_quote_pct"] == pytest.approx(50.0)
    assert data["schema_version"] == 1
