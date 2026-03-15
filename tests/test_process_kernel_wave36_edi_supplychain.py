"""
Wave-36 Tests: EDI-Hub-Contracts + Supply-Chain-Tracking

60 Tests covering:
  - app.core.edi_hub_contracts  (22 tests)
  - app.core.supply_chain_tracking (24 tests)
  - API endpoints via TestClient  (14 tests)
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.edi_hub_contracts import (
    EDIAcknowledgmentResult,
    EDINachricht,
    EDINachrichtenKatalogEintrag,
    EDINachrichtenStatus,
    EDINachrichtenTyp,
    EDIPartner,
    EDIPartnerTyp,
    EDIStandard,
    EDIUebertragungsKanal,
    evaluate_ack_status,
    get_default_edi_partners,
    get_edi_nachrichtentyp_katalog,
)
from app.core.supply_chain_tracking import (
    AbweichungsAlarm,
    AbweichungsSchwere,
    AbweichungsTyp,
    ETABerechnungsErgebnis,
    ETABerechnungsRequest,
    LieferkettenPhase,
    LieferkettenStatusErgebnis,
    TrackingEvent,
    TrackingEventTyp,
    TrackingStatusGesamtlage,
    TransportModus,
    berechne_eta,
    bewerte_lieferkettenstatus,
    bewerte_mengenabweichung,
    bewerte_zeitliche_abweichung,
    get_example_tracking_events,
)

client = TestClient(app)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_nachricht(
    typ: EDINachrichtenTyp = EDINachrichtenTyp.ORDERS,
    status: EDINachrichtenStatus = EDINachrichtenStatus.GESENDET,
    erstellt_am: datetime | None = None,
    quittiert_am: datetime | None = None,
) -> EDINachricht:
    if erstellt_am is None:
        erstellt_am = datetime.now(timezone.utc)
    return EDINachricht(
        nachricht_id="N-001",
        partner_id="EP-LFS-001",
        typ=typ,
        standard=EDIStandard.EDIFACT,
        richtung="AUSGEHEND",
        status=status,
        erstellt_am=erstellt_am,
        quittiert_am=quittiert_am,
    )


def _make_eta_request(
    distanz_km: float = 300.0,
    modus: TransportModus = TransportModus.LKW,
    zwischenstopps: int = 0,
    zoll: bool = False,
    priorisiert: bool = False,
) -> ETABerechnungsRequest:
    return ETABerechnungsRequest(
        lieferung_id="LF-TEST-001",
        transport_modus=modus,
        ursprungsort="Hamburg",
        zielort="München",
        geplante_abfahrt=datetime(2026, 3, 20, 8, 0),
        distanz_km=distanz_km,
        zwischenstopps=zwischenstopps,
        zoll_erforderlich=zoll,
        priorisiert=priorisiert,
    )


# ── EDI Hub Contracts ─────────────────────────────────────────────────────────

class TestEDIEnums:
    """4 tests — basic enum membership and string values."""

    def test_edi_standard_edifact_value(self):
        assert EDIStandard.EDIFACT.value == "EDIFACT"

    def test_edi_nachrichtentyp_orders_value(self):
        assert EDINachrichtenTyp.ORDERS.value == "ORDERS"

    def test_edi_uebertragungskanal_as2_value(self):
        assert EDIUebertragungsKanal.AS2.value == "AS2"

    def test_edi_nachrichtenstatus_pending_value(self):
        assert EDINachrichtenStatus.PENDING.value == "PENDING"


class TestEDIDefaultPartners:
    """3 tests — get_default_edi_partners()."""

    def test_returns_five_partners(self):
        partners = get_default_edi_partners()
        assert len(partners) == 5

    def test_lieferant_partner_exists(self):
        typen = {p.typ for p in get_default_edi_partners()}
        assert EDIPartnerTyp.LIEFERANT in typen

    def test_as_dict_contains_expected_keys(self):
        p = get_default_edi_partners()[0]
        d = p.as_dict()
        for key in ("partner_id", "name", "typ", "edi_standard", "kanal", "aktiv"):
            assert key in d


class TestEDINachrichtenKatalog:
    """4 tests — get_edi_nachrichtentyp_katalog()."""

    def test_returns_at_least_nine_entries(self):
        assert len(get_edi_nachrichtentyp_katalog()) >= 9

    def test_all_entries_are_katalog_instances(self):
        for e in get_edi_nachrichtentyp_katalog():
            assert isinstance(e, EDINachrichtenKatalogEintrag)

    def test_orders_is_quittungspflichtig(self):
        katalog = {e.typ: e for e in get_edi_nachrichtentyp_katalog()}
        assert katalog[EDINachrichtenTyp.ORDERS].quittungspflichtig is True

    def test_contrl_not_quittungspflichtig(self):
        katalog = {e.typ: e for e in get_edi_nachrichtentyp_katalog()}
        assert katalog[EDINachrichtenTyp.CONTRL].quittungspflichtig is False


class TestEDIAcknowledgment:
    """8 tests — evaluate_ack_status()."""

    def test_contrl_not_quittungspflichtig(self):
        msg = _make_nachricht(typ=EDINachrichtenTyp.CONTRL)
        result = evaluate_ack_status(msg, EDIUebertragungsKanal.AS2)
        assert result.erwartet_quittung is False

    def test_orders_requires_quittung(self):
        msg = _make_nachricht(typ=EDINachrichtenTyp.ORDERS)
        result = evaluate_ack_status(msg, EDIUebertragungsKanal.AS2)
        assert result.erwartet_quittung is True

    def test_sla_violated_when_overdue_as2(self):
        jetzt = datetime.now(timezone.utc)
        erstellt = jetzt - timedelta(seconds=400)  # 400s > AS2 SLA of 300s
        msg = _make_nachricht(
            typ=EDINachrichtenTyp.ORDERS,
            status=EDINachrichtenStatus.GESENDET,
            erstellt_am=erstellt,
            quittiert_am=None,
        )
        result = evaluate_ack_status(msg, EDIUebertragungsKanal.AS2, jetzt=jetzt)
        assert result.sla_ok is False

    def test_quittung_erhalten_when_status_quittiert(self):
        jetzt = datetime.now(timezone.utc)
        erstellt = jetzt - timedelta(seconds=20)
        quittiert = jetzt - timedelta(seconds=5)
        msg = _make_nachricht(
            typ=EDINachrichtenTyp.INVOIC,
            status=EDINachrichtenStatus.QUITTIERT,
            erstellt_am=erstellt,
            quittiert_am=quittiert,
        )
        result = evaluate_ack_status(msg, EDIUebertragungsKanal.NATS, jetzt=jetzt)
        assert result.quittung_erhalten is True

    def test_nats_sla_10_seconds(self):
        jetzt = datetime.now(timezone.utc)
        erstellt = jetzt - timedelta(seconds=15)  # 15s > NATS SLA of 10s
        msg = _make_nachricht(
            typ=EDINachrichtenTyp.DESADV,
            status=EDINachrichtenStatus.GESENDET,
            erstellt_am=erstellt,
        )
        result = evaluate_ack_status(msg, EDIUebertragungsKanal.NATS, jetzt=jetzt)
        assert result.sla_ok is False

    def test_non_quittungspflichtig_returns_sla_ok_true(self):
        msg = _make_nachricht(typ=EDINachrichtenTyp.PRICAT)
        result = evaluate_ack_status(msg, EDIUebertragungsKanal.EMAIL)
        # PRICAT not in _QUITTUNGSPFLICHTIG → sla_ok=True by default
        assert result.sla_ok is True


# ── Supply Chain Tracking ─────────────────────────────────────────────────────

class TestETABerechnung:
    """10 tests — berechne_eta()."""

    def test_basic_lkw_eta(self):
        req = _make_eta_request(distanz_km=300.0, modus=TransportModus.LKW)
        result = berechne_eta(req)
        assert isinstance(result, ETABerechnungsErgebnis)
        assert result.geschaetzte_ankunft > req.geplante_abfahrt

    def test_lkw_speed_75_kmh(self):
        req = _make_eta_request(distanz_km=750.0, modus=TransportModus.LKW)
        result = berechne_eta(req)
        # Pure drive time = 750/75 = 10h, puffer 15% = 1.5h → min 11.5h total
        delta_h = (result.geschaetzte_ankunft - req.geplante_abfahrt).total_seconds() / 3600
        assert delta_h >= 11.5

    def test_schiff_speed_25_kmh(self):
        req = _make_eta_request(distanz_km=500.0, modus=TransportModus.SCHIFF)
        result = berechne_eta(req)
        # 500/25 = 20h drive, puffer 15% = 3h → min 23h
        delta_h = (result.geschaetzte_ankunft - req.geplante_abfahrt).total_seconds() / 3600
        assert delta_h >= 23.0

    def test_zoll_adds_24_hours(self):
        req_no_zoll = _make_eta_request(distanz_km=300.0, zoll=False)
        req_zoll = _make_eta_request(distanz_km=300.0, zoll=True)
        result_no = berechne_eta(req_no_zoll)
        result_yes = berechne_eta(req_zoll)
        diff_h = (result_yes.geschaetzte_ankunft - result_no.geschaetzte_ankunft).total_seconds() / 3600
        assert abs(diff_h - 24.0) < 0.01

    def test_priorisiert_reduces_puffer(self):
        req_std = _make_eta_request(distanz_km=300.0, priorisiert=False)
        req_prio = _make_eta_request(distanz_km=300.0, priorisiert=True)
        result_std = berechne_eta(req_std)
        result_prio = berechne_eta(req_prio)
        assert result_prio.puffer_stunden < result_std.puffer_stunden

    def test_zwischenstopps_add_4h_each(self):
        req_0 = _make_eta_request(distanz_km=300.0, zwischenstopps=0)
        req_2 = _make_eta_request(distanz_km=300.0, zwischenstopps=2)
        r0 = berechne_eta(req_0)
        r2 = berechne_eta(req_2)
        diff_h = (r2.geschaetzte_ankunft - r0.geschaetzte_ankunft).total_seconds() / 3600
        assert abs(diff_h - 8.0) < 0.01

    def test_konfidenz_clamped_between_50_and_95(self):
        req = _make_eta_request(
            distanz_km=5000.0,
            modus=TransportModus.SCHIFF,
            zwischenstopps=10,
            zoll=True,
        )
        result = berechne_eta(req)
        assert 50 <= result.konfidenz_prozent <= 95

    def test_raises_value_error_for_zero_distanz(self):
        req = _make_eta_request(distanz_km=0.0)
        with pytest.raises(ValueError):
            berechne_eta(req)

    def test_raises_value_error_for_negative_distanz(self):
        req = _make_eta_request(distanz_km=-100.0)
        with pytest.raises(ValueError):
            berechne_eta(req)


class TestZeitlicheAbweichung:
    """6 tests — bewerte_zeitliche_abweichung()."""

    def test_less_than_4h_is_info(self):
        alarm = bewerte_zeitliche_abweichung("LF-001", "A-001", verzoegerung_stunden=2.0)
        assert alarm.schwere == AbweichungsSchwere.INFO

    def test_4h_is_warnung(self):
        alarm = bewerte_zeitliche_abweichung("LF-001", "A-002", verzoegerung_stunden=4.0)
        assert alarm.schwere == AbweichungsSchwere.WARNUNG

    def test_between_4_and_24h_is_warnung(self):
        alarm = bewerte_zeitliche_abweichung("LF-001", "A-003", verzoegerung_stunden=12.0)
        assert alarm.schwere == AbweichungsSchwere.WARNUNG

    def test_24h_is_kritisch(self):
        alarm = bewerte_zeitliche_abweichung("LF-001", "A-004", verzoegerung_stunden=24.0)
        assert alarm.schwere == AbweichungsSchwere.KRITISCH

    def test_kritisch_auto_eskaliert(self):
        alarm = bewerte_zeitliche_abweichung("LF-001", "A-005", verzoegerung_stunden=30.0)
        assert alarm.automatisch_eskaliert is True
        assert "leitung@valeo.de" in alarm.eskalations_empfaenger

    def test_warnung_empfaenger_disposition(self):
        alarm = bewerte_zeitliche_abweichung("LF-001", "A-006", verzoegerung_stunden=8.0)
        assert "disposition@valeo.de" in alarm.eskalations_empfaenger


class TestMengenabweichung:
    """6 tests — bewerte_mengenabweichung()."""

    def test_less_than_2pct_is_info(self):
        alarm = bewerte_mengenabweichung("LF-002", "M-001", soll_menge=1000.0, ist_menge=1010.0)
        assert alarm.schwere == AbweichungsSchwere.INFO

    def test_2_to_5pct_is_warnung(self):
        alarm = bewerte_mengenabweichung("LF-002", "M-002", soll_menge=1000.0, ist_menge=1030.0)
        assert alarm.schwere == AbweichungsSchwere.WARNUNG

    def test_5pct_or_more_is_kritisch(self):
        alarm = bewerte_mengenabweichung("LF-002", "M-003", soll_menge=1000.0, ist_menge=1060.0)
        assert alarm.schwere == AbweichungsSchwere.KRITISCH

    def test_kritisch_auto_eskaliert(self):
        alarm = bewerte_mengenabweichung("LF-002", "M-004", soll_menge=1000.0, ist_menge=900.0)
        assert alarm.automatisch_eskaliert is True

    def test_zero_soll_menge_raises(self):
        with pytest.raises(ValueError):
            bewerte_mengenabweichung("LF-002", "M-005", soll_menge=0.0, ist_menge=100.0)

    def test_result_typ_is_mengenabweichung(self):
        alarm = bewerte_mengenabweichung("LF-002", "M-006", soll_menge=500.0, ist_menge=490.0)
        assert alarm.typ == AbweichungsTyp.MENGENABWEICHUNG


class TestLieferkettenStatus:
    """6 tests — bewerte_lieferkettenstatus()."""

    def test_planmaessig_with_no_alarme(self):
        ergebnis = bewerte_lieferkettenstatus(
            "LF-003", LieferkettenPhase.TRANSPORT_EINGEHEND, [], []
        )
        assert ergebnis.gesamtlage == TrackingStatusGesamtlage.PLANMAESSIG

    def test_abgeschlossen_when_auslieferung_no_kritisch(self):
        ergebnis = bewerte_lieferkettenstatus(
            "LF-003", LieferkettenPhase.AUSLIEFERUNG, [], []
        )
        assert ergebnis.gesamtlage == TrackingStatusGesamtlage.ABGESCHLOSSEN

    def test_kritische_abweichung_when_kritisch_alarm(self):
        alarm = bewerte_zeitliche_abweichung("LF-003", "A-K1", 30.0)
        ergebnis = bewerte_lieferkettenstatus(
            "LF-003", LieferkettenPhase.TRANSPORT_EINGEHEND, [], [alarm]
        )
        assert ergebnis.gesamtlage == TrackingStatusGesamtlage.KRITISCHE_ABWEICHUNG

    def test_leichte_abweichung_when_warnung_alarm(self):
        alarm = bewerte_zeitliche_abweichung("LF-003", "A-W1", 8.0)
        ergebnis = bewerte_lieferkettenstatus(
            "LF-003", LieferkettenPhase.LAGERUNG, [], [alarm]
        )
        assert ergebnis.gesamtlage == TrackingStatusGesamtlage.LEICHTE_ABWEICHUNG

    def test_fortschritt_transport_eingehend_is_30(self):
        ergebnis = bewerte_lieferkettenstatus(
            "LF-003", LieferkettenPhase.TRANSPORT_EINGEHEND, [], []
        )
        assert ergebnis.fortschritt_prozent == 30

    def test_letzte_events_max_5(self):
        events = get_example_tracking_events("LF-003")
        # Duplicate events to have more than 5
        events = events * 3
        ergebnis = bewerte_lieferkettenstatus(
            "LF-003", LieferkettenPhase.LAGERUNG, events, []
        )
        assert len(ergebnis.letzte_events) <= 5


class TestExampleData:
    """2 tests — get_example_tracking_events()."""

    def test_returns_three_events(self):
        events = get_example_tracking_events()
        assert len(events) == 3

    def test_events_have_ist_meilenstein_field(self):
        events = get_example_tracking_events("LF-CUSTOM-001")
        for e in events:
            assert hasattr(e, "ist_meilenstein")


# ── API Endpoints ─────────────────────────────────────────────────────────────

class TestEDIPartnersEndpoint:
    """4 tests — GET /api/v1/process/edi/partners"""

    def test_returns_200_with_partner_count(self):
        resp = client.get("/api/v1/process/edi/partners")
        assert resp.status_code == 200
        data = resp.json()
        assert "partner_count" in data
        assert data["partner_count"] == 5

    def test_filter_by_typ_lieferant(self):
        resp = client.get("/api/v1/process/edi/partners?typ=LIEFERANT")
        assert resp.status_code == 200
        data = resp.json()
        assert data["partner_count"] >= 1
        for p in data["partner"]:
            assert p["typ"] == "LIEFERANT"

    def test_invalid_typ_returns_422(self):
        resp = client.get("/api/v1/process/edi/partners?typ=UNGUELTIG")
        assert resp.status_code == 422

    def test_filter_by_standard_edifact(self):
        resp = client.get("/api/v1/process/edi/partners?standard=EDIFACT")
        assert resp.status_code == 200
        data = resp.json()
        assert data["partner_count"] >= 1
        for p in data["partner"]:
            assert p["edi_standard"] == "EDIFACT"


class TestEDINachrichtentypenEndpoint:
    """2 tests — GET /api/v1/process/edi/nachrichtentypen"""

    def test_returns_200_with_typ_count(self):
        resp = client.get("/api/v1/process/edi/nachrichtentypen")
        assert resp.status_code == 200
        data = resp.json()
        assert "typ_count" in data
        assert data["typ_count"] >= 9

    def test_nachrichtentypen_list_not_empty(self):
        resp = client.get("/api/v1/process/edi/nachrichtentypen")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nachrichtentypen"]) >= 9


class TestSupplyChainEtaEndpoint:
    """4 tests — POST /api/v1/process/supply-chain/eta"""

    def test_valid_request_returns_200_with_ankunft(self):
        payload = {
            "lieferung_id": "LF-API-001",
            "transport_modus": "LKW",
            "ursprungsort": "Hamburg",
            "zielort": "München",
            "geplante_abfahrt": "2026-03-20T08:00:00",
            "distanz_km": 800.0,
        }
        resp = client.post("/api/v1/process/supply-chain/eta", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "geschaetzte_ankunft" in data

    def test_missing_required_field_returns_422(self):
        payload = {
            "lieferung_id": "LF-API-002",
            "transport_modus": "LKW",
            # missing distanz_km, geplante_abfahrt, etc.
        }
        resp = client.post("/api/v1/process/supply-chain/eta", json=payload)
        assert resp.status_code == 422

    def test_invalid_transport_modus_returns_422(self):
        payload = {
            "lieferung_id": "LF-API-003",
            "transport_modus": "FAHRRAD",
            "ursprungsort": "Berlin",
            "zielort": "Köln",
            "geplante_abfahrt": "2026-03-20T08:00:00",
            "distanz_km": 500.0,
        }
        resp = client.post("/api/v1/process/supply-chain/eta", json=payload)
        assert resp.status_code == 422

    def test_zoll_and_priorisiert_flags_accepted(self):
        payload = {
            "lieferung_id": "LF-API-004",
            "transport_modus": "BAHN",
            "ursprungsort": "Frankfurt",
            "zielort": "Wien",
            "geplante_abfahrt": "2026-03-21T06:00:00",
            "distanz_km": 620.0,
            "zoll_erforderlich": True,
            "priorisiert": True,
        }
        resp = client.post("/api/v1/process/supply-chain/eta", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["konfidenz_prozent"] <= 80  # zoll reduces confidence


class TestSupplyChainStatusEndpoint:
    """4 tests — POST /api/v1/process/supply-chain/status"""

    def test_planmaessig_with_no_alarme(self):
        payload = {
            "lieferung_id": "LF-STATUS-001",
            "aktuelle_phase": "TRANSPORT_EINGEHEND",
        }
        resp = client.post("/api/v1/process/supply-chain/status", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["gesamtlage"] == "PLANMAESSIG"
        assert data["fortschritt_prozent"] == 30

    def test_kritisch_alarm_from_30h_verzoegerung(self):
        payload = {
            "lieferung_id": "LF-STATUS-002",
            "aktuelle_phase": "TRANSPORT_EINGEHEND",
            "verzoegerung_stunden": 30.0,
        }
        resp = client.post("/api/v1/process/supply-chain/status", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["gesamtlage"] == "KRITISCHE_ABWEICHUNG"
        alarme = data["aktive_alarme"]
        assert any(a["schwere"] == "KRITISCH" for a in alarme)

    def test_missing_lieferung_id_returns_422(self):
        # Only aktuelle_phase provided — lieferung_id missing → 422
        payload = {
            "aktuelle_phase": "LAGERUNG",
        }
        resp = client.post("/api/v1/process/supply-chain/status", json=payload)
        assert resp.status_code == 422

    def test_invalid_phase_returns_422(self):
        payload = {
            "lieferung_id": "LF-STATUS-004",
            "aktuelle_phase": "UNGUELTIGE_PHASE",
        }
        resp = client.post("/api/v1/process/supply-chain/status", json=payload)
        assert resp.status_code == 422
