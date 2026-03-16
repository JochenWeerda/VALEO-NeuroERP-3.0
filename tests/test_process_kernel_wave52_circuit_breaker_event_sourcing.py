"""
Wave 52: Circuit Breaker + Event Sourcing Contracts
130+ tests covering CircuitBreaker state machine and EventSourcing replay/reconstruction.
"""
import pytest
from datetime import datetime, timedelta

from app.core.process_circuit_breaker_contracts import (
    CircuitBreakerZustand,
    AufrufErgebnis,
    CircuitBreakerKonfiguration,
    CircuitBreakerZustandsRecord,
    get_default_circuit_breaker_konfigurationen,
)
from app.core.workflow_event_sourcing_contracts import (
    EreignisTyp,
    ReplayModus,
    WorkflowEreignis,
    EreignisStream,
    rekonstruiere_zustand,
    get_default_ereignis_streams,
)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
NOW = datetime(2026, 3, 16, 12, 0, 0)


def default_config(schwellwert=5, timeout=60, halb_offen_max=3) -> CircuitBreakerKonfiguration:
    return CircuitBreakerKonfiguration(
        breaker_id="TEST",
        service_name="TestService",
        fehler_schwellwert=schwellwert,
        wiederherstellungs_timeout_sekunden=timeout,
        halb_offen_max_anfragen=halb_offen_max,
    )


def geschlossen_record(fehler_zaehler=0) -> CircuitBreakerZustandsRecord:
    return CircuitBreakerZustandsRecord(
        breaker_id="TEST",
        zustand=CircuitBreakerZustand.GESCHLOSSEN,
        fehler_zaehler=fehler_zaehler,
    )


def offen_record(letzter_fehler_vor_sek: int = 30) -> CircuitBreakerZustandsRecord:
    return CircuitBreakerZustandsRecord(
        breaker_id="TEST",
        zustand=CircuitBreakerZustand.OFFEN,
        fehler_zaehler=5,
        letzter_fehler_am=NOW - timedelta(seconds=letzter_fehler_vor_sek),
    )


def halb_offen_record(erfolg_zaehler=0) -> CircuitBreakerZustandsRecord:
    return CircuitBreakerZustandsRecord(
        breaker_id="TEST",
        zustand=CircuitBreakerZustand.HALB_OFFEN,
        erfolg_zaehler_halb_offen=erfolg_zaehler,
    )


def make_ereignis(version: int, typ: EreignisTyp, nutzlast: dict = None,
                  instanz_id: str = "WI-TEST-001",
                  delta_minutes: int = 0) -> WorkflowEreignis:
    return WorkflowEreignis(
        ereignis_id=f"EVT-{version:03d}",
        workflow_instanz_id=instanz_id,
        ereignis_typ=typ,
        version=version,
        nutzlast=nutzlast or {},
        ausgefuehrt_von="test-user",
        erstellt_am=NOW + timedelta(minutes=delta_minutes),
        tenant_id="TENANT-TEST",
    )


# ═════════════════════════════════════════════════════════════════════════════
# CIRCUIT BREAKER TESTS
# ═════════════════════════════════════════════════════════════════════════════

class TestCircuitBreakerZustandEnum:
    def test_geschlossen_value(self):
        assert CircuitBreakerZustand.GESCHLOSSEN == "GESCHLOSSEN"

    def test_offen_value(self):
        assert CircuitBreakerZustand.OFFEN == "OFFEN"

    def test_halb_offen_value(self):
        assert CircuitBreakerZustand.HALB_OFFEN == "HALB_OFFEN"

    def test_all_three_states_exist(self):
        states = list(CircuitBreakerZustand)
        assert len(states) == 3


class TestAufrufErgebnisEnum:
    def test_erfolg_value(self):
        assert AufrufErgebnis.ERFOLG == "ERFOLG"

    def test_fehler_value(self):
        assert AufrufErgebnis.FEHLER == "FEHLER"

    def test_zeitueberschreitung_value(self):
        assert AufrufErgebnis.ZEITUEBERSCHREITUNG == "ZEITUEBERSCHREITUNG"

    def test_all_three_results_exist(self):
        assert len(list(AufrufErgebnis)) == 3


class TestCircuitBreakerKonfiguration:
    def test_basic_creation(self):
        cfg = default_config()
        assert cfg.breaker_id == "TEST"
        assert cfg.service_name == "TestService"
        assert cfg.fehler_schwellwert == 5
        assert cfg.wiederherstellungs_timeout_sekunden == 60
        assert cfg.halb_offen_max_anfragen == 3

    def test_beschreibung_default_empty(self):
        cfg = default_config()
        assert cfg.beschreibung == ""

    def test_beschreibung_set(self):
        cfg = CircuitBreakerKonfiguration("X", "SvcX", 5, 60, 3, "Mein Service")
        assert cfg.beschreibung == "Mein Service"


class TestKannAnfrageDurchlassen:
    # GESCHLOSSEN → always True
    def test_geschlossen_allows_all(self):
        rec = geschlossen_record()
        cfg = default_config()
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is True

    def test_geschlossen_with_errors_still_allows(self):
        rec = geschlossen_record(fehler_zaehler=4)
        cfg = default_config()
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is True

    # OFFEN + timeout not expired → False
    def test_offen_timeout_not_expired(self):
        rec = offen_record(letzter_fehler_vor_sek=30)  # 30s < 60s timeout
        cfg = default_config(timeout=60)
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is False

    def test_offen_timeout_exactly_not_expired(self):
        rec = offen_record(letzter_fehler_vor_sek=59)  # 59s < 60s
        cfg = default_config(timeout=60)
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is False

    # OFFEN + timeout expired → True
    def test_offen_timeout_expired(self):
        rec = offen_record(letzter_fehler_vor_sek=61)  # 61s > 60s timeout
        cfg = default_config(timeout=60)
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is True

    def test_offen_timeout_exactly_expired(self):
        rec = offen_record(letzter_fehler_vor_sek=60)  # exactly 60s
        cfg = default_config(timeout=60)
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is True

    def test_offen_no_letzter_fehler_blocks(self):
        rec = CircuitBreakerZustandsRecord(
            breaker_id="TEST",
            zustand=CircuitBreakerZustand.OFFEN,
            letzter_fehler_am=None,
        )
        cfg = default_config()
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is False

    # HALB_OFFEN + under max → True
    def test_halb_offen_under_max_allows(self):
        rec = halb_offen_record(erfolg_zaehler=0)
        cfg = default_config(halb_offen_max=3)
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is True

    def test_halb_offen_under_max_allows_2(self):
        rec = halb_offen_record(erfolg_zaehler=2)
        cfg = default_config(halb_offen_max=3)
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is True

    # HALB_OFFEN + at max → False
    def test_halb_offen_at_max_blocks(self):
        rec = halb_offen_record(erfolg_zaehler=3)
        cfg = default_config(halb_offen_max=3)
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is False

    def test_halb_offen_over_max_blocks(self):
        rec = halb_offen_record(erfolg_zaehler=5)
        cfg = default_config(halb_offen_max=3)
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is False


class TestVerarbeiteErgebnis:
    # GESCHLOSSEN + FEHLER
    def test_geschlossen_fehler_increments_counter(self):
        rec = geschlossen_record(fehler_zaehler=0)
        cfg = default_config(schwellwert=5)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert new_rec.fehler_zaehler == 1
        assert new_rec.zustand == CircuitBreakerZustand.GESCHLOSSEN

    def test_geschlossen_fehler_sets_letzter_fehler_am(self):
        rec = geschlossen_record()
        cfg = default_config()
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert new_rec.letzter_fehler_am == NOW

    # GESCHLOSSEN + ZEITUEBERSCHREITUNG
    def test_geschlossen_zeitueberschreitung_increments_counter(self):
        rec = geschlossen_record(fehler_zaehler=1)
        cfg = default_config(schwellwert=5)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ZEITUEBERSCHREITUNG, cfg, NOW)
        assert new_rec.fehler_zaehler == 2
        assert new_rec.zustand == CircuitBreakerZustand.GESCHLOSSEN

    # GESCHLOSSEN + ERFOLG
    def test_geschlossen_erfolg_resets_counter(self):
        rec = geschlossen_record(fehler_zaehler=3)
        cfg = default_config()
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ERFOLG, cfg, NOW)
        assert new_rec.fehler_zaehler == 0
        assert new_rec.zustand == CircuitBreakerZustand.GESCHLOSSEN

    def test_geschlossen_erfolg_no_letzter_fehler_change(self):
        rec = geschlossen_record(fehler_zaehler=0)
        cfg = default_config()
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ERFOLG, cfg, NOW)
        assert new_rec.letzter_fehler_am is None

    # GESCHLOSSEN + exactly schwellwert failures → OFFEN
    def test_geschlossen_reaches_schwellwert_opens(self):
        rec = geschlossen_record(fehler_zaehler=4)  # one more → 5 == schwellwert
        cfg = default_config(schwellwert=5)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.OFFEN
        assert new_rec.fehler_zaehler == 5

    def test_geschlossen_reaches_schwellwert_sets_zustand_changed_am(self):
        rec = geschlossen_record(fehler_zaehler=4)
        cfg = default_config(schwellwert=5)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert new_rec.zustand_geaendert_am == NOW

    # GESCHLOSSEN + below schwellwert → stays GESCHLOSSEN
    def test_geschlossen_below_schwellwert_stays_closed(self):
        rec = geschlossen_record(fehler_zaehler=3)
        cfg = default_config(schwellwert=5)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.GESCHLOSSEN
        assert new_rec.fehler_zaehler == 4

    def test_geschlossen_zeitueberschreitung_reaches_schwellwert(self):
        rec = geschlossen_record(fehler_zaehler=4)
        cfg = default_config(schwellwert=5)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ZEITUEBERSCHREITUNG, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.OFFEN

    # HALB_OFFEN + ERFOLG increments
    def test_halb_offen_erfolg_increments_success_counter(self):
        rec = halb_offen_record(erfolg_zaehler=0)
        cfg = default_config(halb_offen_max=3)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ERFOLG, cfg, NOW)
        assert new_rec.erfolg_zaehler_halb_offen == 1
        assert new_rec.zustand == CircuitBreakerZustand.HALB_OFFEN

    # HALB_OFFEN + enough ERFOLG → GESCHLOSSEN
    def test_halb_offen_enough_erfolg_closes(self):
        rec = halb_offen_record(erfolg_zaehler=2)  # one more → 3 == max
        cfg = default_config(halb_offen_max=3)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ERFOLG, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.GESCHLOSSEN
        assert new_rec.fehler_zaehler == 0
        assert new_rec.erfolg_zaehler_halb_offen == 0

    def test_halb_offen_closes_sets_zustand_changed_am(self):
        rec = halb_offen_record(erfolg_zaehler=2)
        cfg = default_config(halb_offen_max=3)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ERFOLG, cfg, NOW)
        assert new_rec.zustand_geaendert_am == NOW

    # HALB_OFFEN + FEHLER → OFFEN
    def test_halb_offen_fehler_opens(self):
        rec = halb_offen_record(erfolg_zaehler=1)
        cfg = default_config(halb_offen_max=3)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.OFFEN
        assert new_rec.erfolg_zaehler_halb_offen == 0

    def test_halb_offen_fehler_sets_letzter_fehler_am(self):
        rec = halb_offen_record()
        cfg = default_config()
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert new_rec.letzter_fehler_am == NOW

    # HALB_OFFEN + ZEITUEBERSCHREITUNG → OFFEN
    def test_halb_offen_zeitueberschreitung_opens(self):
        rec = halb_offen_record(erfolg_zaehler=2)
        cfg = default_config(halb_offen_max=3)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ZEITUEBERSCHREITUNG, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.OFFEN
        assert new_rec.erfolg_zaehler_halb_offen == 0

    # OFFEN + results → stays OFFEN
    def test_offen_erfolg_stays_offen(self):
        rec = offen_record()
        cfg = default_config()
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ERFOLG, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.OFFEN

    def test_offen_fehler_stays_offen(self):
        rec = offen_record()
        cfg = default_config()
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.OFFEN

    def test_offen_zeitueberschreitung_stays_offen(self):
        rec = offen_record()
        cfg = default_config()
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ZEITUEBERSCHREITUNG, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.OFFEN


class TestCircuitBreakerImmutability:
    def test_original_unchanged_after_fehler(self):
        rec = geschlossen_record(fehler_zaehler=2)
        cfg = default_config()
        _ = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert rec.fehler_zaehler == 2
        assert rec.zustand == CircuitBreakerZustand.GESCHLOSSEN

    def test_original_unchanged_after_oeffnen(self):
        rec = geschlossen_record(fehler_zaehler=4)
        cfg = default_config(schwellwert=5)
        _ = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert rec.zustand == CircuitBreakerZustand.GESCHLOSSEN

    def test_original_unchanged_after_halb_offen_schliessen(self):
        rec = halb_offen_record(erfolg_zaehler=2)
        cfg = default_config(halb_offen_max=3)
        _ = rec.verarbeite_ergebnis(AufrufErgebnis.ERFOLG, cfg, NOW)
        assert rec.zustand == CircuitBreakerZustand.HALB_OFFEN
        assert rec.erfolg_zaehler_halb_offen == 2

    def test_returns_new_object(self):
        rec = geschlossen_record()
        cfg = default_config()
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert new_rec is not rec


class TestGetDefaultCircuitBreakerKonfigurationen:
    def test_returns_five_configs(self):
        configs = get_default_circuit_breaker_konfigurationen()
        assert len(configs) == 5

    def test_first_config_is_cb_001(self):
        configs = get_default_circuit_breaker_konfigurationen()
        assert configs[0].breaker_id == "CB-001"

    def test_last_config_is_cb_005(self):
        configs = get_default_circuit_breaker_konfigurationen()
        assert configs[4].breaker_id == "CB-005"

    def test_all_ids_present(self):
        configs = get_default_circuit_breaker_konfigurationen()
        ids = [c.breaker_id for c in configs]
        for i in range(1, 6):
            assert f"CB-{i:03d}" in ids

    def test_cb_001_service_name(self):
        configs = get_default_circuit_breaker_konfigurationen()
        cb001 = next(c for c in configs if c.breaker_id == "CB-001")
        assert cb001.service_name == "ERP-Settlement-API"

    def test_cb_002_edi_gateway(self):
        configs = get_default_circuit_breaker_konfigurationen()
        cb002 = next(c for c in configs if c.breaker_id == "CB-002")
        assert cb002.service_name == "EDI-Partner-Gateway"

    def test_cb_003_marktdaten(self):
        configs = get_default_circuit_breaker_konfigurationen()
        cb003 = next(c for c in configs if c.breaker_id == "CB-003")
        assert cb003.service_name == "Marktdaten-Feed"

    def test_cb_004_oidc(self):
        configs = get_default_circuit_breaker_konfigurationen()
        cb004 = next(c for c in configs if c.breaker_id == "CB-004")
        assert cb004.service_name == "OIDC-Token-Endpoint"

    def test_cb_005_lager_db(self):
        configs = get_default_circuit_breaker_konfigurationen()
        cb005 = next(c for c in configs if c.breaker_id == "CB-005")
        assert cb005.service_name == "Lager-Datenbank"

    def test_all_have_positive_schwellwert(self):
        for c in get_default_circuit_breaker_konfigurationen():
            assert c.fehler_schwellwert > 0

    def test_all_have_positive_timeout(self):
        for c in get_default_circuit_breaker_konfigurationen():
            assert c.wiederherstellungs_timeout_sekunden > 0

    def test_all_have_positive_halb_offen_max(self):
        for c in get_default_circuit_breaker_konfigurationen():
            assert c.halb_offen_max_anfragen > 0


# ═════════════════════════════════════════════════════════════════════════════
# EVENT SOURCING TESTS
# ═════════════════════════════════════════════════════════════════════════════

class TestEreignisTypEnum:
    def test_erstellt_value(self):
        assert EreignisTyp.ERSTELLT == "ERSTELLT"

    def test_zustand_geaendert_value(self):
        assert EreignisTyp.ZUSTAND_GEAENDERT == "ZUSTAND_GEAENDERT"

    def test_aktion_ausgefuehrt_value(self):
        assert EreignisTyp.AKTION_AUSGEFUEHRT == "AKTION_AUSGEFUEHRT"

    def test_kompensiert_value(self):
        assert EreignisTyp.KOMPENSIERT == "KOMPENSIERT"

    def test_abgeschlossen_value(self):
        assert EreignisTyp.ABGESCHLOSSEN == "ABGESCHLOSSEN"

    def test_fehler_aufgetreten_value(self):
        assert EreignisTyp.FEHLER_AUFGETRETEN == "FEHLER_AUFGETRETEN"

    def test_six_types_total(self):
        assert len(list(EreignisTyp)) == 6


class TestReplayModusEnum:
    def test_vollstaendig_value(self):
        assert ReplayModus.VOLLSTAENDIG == "VOLLSTAENDIG"

    def test_bis_zeitpunkt_value(self):
        assert ReplayModus.BIS_ZEITPUNKT == "BIS_ZEITPUNKT"

    def test_ab_version_value(self):
        assert ReplayModus.AB_VERSION == "AB_VERSION"

    def test_three_modes_total(self):
        assert len(list(ReplayModus)) == 3


class TestEreignisStreamAktuelleVersion:
    def test_empty_stream_returns_zero(self):
        s = EreignisStream("WI-EMPTY")
        assert s.aktuelle_version() == 0

    def test_single_event_returns_version(self):
        s = EreignisStream("WI-TEST")
        s.ereignisse.append(make_ereignis(1, EreignisTyp.ERSTELLT))
        assert s.aktuelle_version() == 1

    def test_multiple_events_returns_max(self):
        s = EreignisStream("WI-TEST")
        s.ereignisse.append(make_ereignis(1, EreignisTyp.ERSTELLT))
        s.ereignisse.append(make_ereignis(2, EreignisTyp.ZUSTAND_GEAENDERT))
        s.ereignisse.append(make_ereignis(3, EreignisTyp.ABGESCHLOSSEN))
        assert s.aktuelle_version() == 3

    def test_unordered_events_still_returns_max(self):
        s = EreignisStream("WI-TEST")
        s.ereignisse.append(make_ereignis(3, EreignisTyp.ABGESCHLOSSEN))
        s.ereignisse.append(make_ereignis(1, EreignisTyp.ERSTELLT))
        s.ereignisse.append(make_ereignis(2, EreignisTyp.ZUSTAND_GEAENDERT))
        assert s.aktuelle_version() == 3


class TestEreignisStreamFuegeHinzu:
    def test_returns_new_stream(self):
        s = EreignisStream("WI-TEST")
        evt = make_ereignis(1, EreignisTyp.ERSTELLT)
        new_s = s.fuege_ereignis_hinzu(evt)
        assert new_s is not s

    def test_original_unchanged(self):
        s = EreignisStream("WI-TEST")
        evt = make_ereignis(1, EreignisTyp.ERSTELLT)
        _ = s.fuege_ereignis_hinzu(evt)
        assert len(s.ereignisse) == 0

    def test_new_stream_has_event(self):
        s = EreignisStream("WI-TEST")
        evt = make_ereignis(1, EreignisTyp.ERSTELLT)
        new_s = s.fuege_ereignis_hinzu(evt)
        assert len(new_s.ereignisse) == 1

    def test_new_stream_event_is_correct(self):
        s = EreignisStream("WI-TEST")
        evt = make_ereignis(1, EreignisTyp.ERSTELLT)
        new_s = s.fuege_ereignis_hinzu(evt)
        assert new_s.ereignisse[0].ereignis_id == "EVT-001"

    def test_chained_adds(self):
        s = EreignisStream("WI-TEST")
        e1 = make_ereignis(1, EreignisTyp.ERSTELLT)
        e2 = make_ereignis(2, EreignisTyp.ZUSTAND_GEAENDERT)
        new_s = s.fuege_ereignis_hinzu(e1).fuege_ereignis_hinzu(e2)
        assert len(new_s.ereignisse) == 2
        assert new_s.aktuelle_version() == 2

    def test_stream_id_preserved(self):
        s = EreignisStream("WI-PRESERVED")
        evt = make_ereignis(1, EreignisTyp.ERSTELLT)
        new_s = s.fuege_ereignis_hinzu(evt)
        assert new_s.stream_id == "WI-PRESERVED"


class TestEreignisStreamReplay:
    def _build_stream(self) -> EreignisStream:
        s = EreignisStream("WI-REPLAY")
        for i in range(1, 6):
            s.ereignisse.append(make_ereignis(i, EreignisTyp.ZUSTAND_GEAENDERT, delta_minutes=i))
        return s

    def test_vollstaendig_returns_all(self):
        s = self._build_stream()
        result = s.replay(ReplayModus.VOLLSTAENDIG)
        assert len(result) == 5

    def test_vollstaendig_sorted_by_version(self):
        s = self._build_stream()
        result = s.replay(ReplayModus.VOLLSTAENDIG)
        versions = [e.version for e in result]
        assert versions == sorted(versions)

    def test_vollstaendig_empty_stream(self):
        s = EreignisStream("WI-EMPTY")
        result = s.replay(ReplayModus.VOLLSTAENDIG)
        assert result == []

    # BIS_ZEITPUNKT
    def test_bis_zeitpunkt_filters_correctly(self):
        s = self._build_stream()
        # Events at NOW+1min, +2min, +3min, +4min, +5min
        bis = NOW + timedelta(minutes=3)
        result = s.replay(ReplayModus.BIS_ZEITPUNKT, bis_zeitpunkt=bis)
        assert len(result) == 3  # versions 1, 2, 3

    def test_bis_zeitpunkt_exact_boundary(self):
        s = self._build_stream()
        bis = NOW + timedelta(minutes=3)
        result = s.replay(ReplayModus.BIS_ZEITPUNKT, bis_zeitpunkt=bis)
        # Event at exactly NOW+3min should be included (<=)
        assert any(e.version == 3 for e in result)

    def test_bis_zeitpunkt_none_returns_all(self):
        s = self._build_stream()
        result = s.replay(ReplayModus.BIS_ZEITPUNKT, bis_zeitpunkt=None)
        assert len(result) == 5

    def test_bis_zeitpunkt_before_all_returns_empty(self):
        s = self._build_stream()
        bis = NOW - timedelta(minutes=10)
        result = s.replay(ReplayModus.BIS_ZEITPUNKT, bis_zeitpunkt=bis)
        assert len(result) == 0

    def test_bis_zeitpunkt_sorted_by_version(self):
        s = self._build_stream()
        bis = NOW + timedelta(minutes=4)
        result = s.replay(ReplayModus.BIS_ZEITPUNKT, bis_zeitpunkt=bis)
        versions = [e.version for e in result]
        assert versions == sorted(versions)

    # AB_VERSION
    def test_ab_version_returns_from_version_onwards(self):
        s = self._build_stream()
        result = s.replay(ReplayModus.AB_VERSION, ab_version=3)
        assert len(result) == 3  # versions 3, 4, 5

    def test_ab_version_1_returns_all(self):
        s = self._build_stream()
        result = s.replay(ReplayModus.AB_VERSION, ab_version=1)
        assert len(result) == 5

    def test_ab_version_5_returns_last(self):
        s = self._build_stream()
        result = s.replay(ReplayModus.AB_VERSION, ab_version=5)
        assert len(result) == 1
        assert result[0].version == 5

    def test_ab_version_beyond_returns_empty(self):
        s = self._build_stream()
        result = s.replay(ReplayModus.AB_VERSION, ab_version=10)
        assert len(result) == 0

    def test_ab_version_sorted_by_version(self):
        s = self._build_stream()
        result = s.replay(ReplayModus.AB_VERSION, ab_version=2)
        versions = [e.version for e in result]
        assert versions == sorted(versions)


class TestRekonstruiereZustand:
    def test_empty_list_returns_empty_dict(self):
        assert rekonstruiere_zustand([]) == {}

    def test_single_erstellt_event(self):
        events = [make_ereignis(1, EreignisTyp.ERSTELLT)]
        zustand = rekonstruiere_zustand(events)
        assert zustand["workflow_instanz_id"] == "WI-TEST-001"
        assert zustand["zustand"] == "ERSTELLT"
        assert zustand["version"] == 1

    def test_zustand_geaendert_updates_zustand(self):
        events = [
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.ZUSTAND_GEAENDERT, {"neuer_zustand": "PRUEFUNG"}),
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["zustand"] == "PRUEFUNG"
        assert zustand["version"] == 2

    def test_aktion_ausgefuehrt_sets_letzte_aktion(self):
        events = [
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.AKTION_AUSGEFUEHRT, {"aktion": "freigabe_erteilt"}),
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["letzte_aktion"] == "freigabe_erteilt"

    def test_aktion_ausgefuehrt_empty_aktion(self):
        events = [
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.AKTION_AUSGEFUEHRT, {}),
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["letzte_aktion"] == ""

    def test_kompensiert_sets_zustand(self):
        events = [
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.KOMPENSIERT),
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["zustand"] == "KOMPENSIERT"

    def test_abgeschlossen_sets_zustand(self):
        events = [
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.ABGESCHLOSSEN),
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["zustand"] == "ABGESCHLOSSEN"

    def test_fehler_aufgetreten_sets_fehler(self):
        events = [
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.FEHLER_AUFGETRETEN, {"fehler": "Verbindungsfehler"}),
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["fehler"] == "Verbindungsfehler"

    def test_fehler_aufgetreten_default_unknown(self):
        events = [
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.FEHLER_AUFGETRETEN, {}),
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["fehler"] == "unbekannt"

    def test_multiple_events_version_reflects_last(self):
        events = [make_ereignis(i, EreignisTyp.ZUSTAND_GEAENDERT, {"neuer_zustand": "X"}) for i in range(1, 6)]
        # override first to ERSTELLT
        events[0] = make_ereignis(1, EreignisTyp.ERSTELLT)
        zustand = rekonstruiere_zustand(events)
        assert zustand["version"] == 5

    def test_events_processed_in_version_order(self):
        # Even if appended in reverse, result should be same
        events = [
            make_ereignis(3, EreignisTyp.ABGESCHLOSSEN),
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.ZUSTAND_GEAENDERT, {"neuer_zustand": "PRUEFUNG"}),
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["zustand"] == "ABGESCHLOSSEN"
        assert zustand["version"] == 3

    def test_full_sequence_kontrakt(self):
        events = [
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.ZUSTAND_GEAENDERT, {"neuer_zustand": "PRUEFUNG"}),
            make_ereignis(3, EreignisTyp.AKTION_AUSGEFUEHRT, {"aktion": "freigabe_erteilt"}),
            make_ereignis(4, EreignisTyp.ABGESCHLOSSEN),
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["zustand"] == "ABGESCHLOSSEN"
        assert zustand["letzte_aktion"] == "freigabe_erteilt"
        assert zustand["version"] == 4
        assert zustand["workflow_instanz_id"] == "WI-TEST-001"

    def test_full_sequence_settlement_kompensiert(self):
        events = [
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.FEHLER_AUFGETRETEN, {"fehler": "Buchungsfehler"}),
            make_ereignis(3, EreignisTyp.KOMPENSIERT),
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["zustand"] == "KOMPENSIERT"
        assert zustand["fehler"] == "Buchungsfehler"
        assert zustand["version"] == 3


class TestGetDefaultEreignisStreams:
    def test_returns_four_streams(self):
        streams = get_default_ereignis_streams()
        assert len(streams) == 4

    def test_stream_ids_correct(self):
        streams = get_default_ereignis_streams()
        ids = [s.stream_id for s in streams]
        assert "WI-KONTRAKT-001" in ids
        assert "WI-SETTLEMENT-002" in ids
        assert "WI-RECHNUNG-003" in ids
        assert "WI-LEER-004" in ids

    def test_wi_leer_004_is_empty(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        leer = streams["WI-LEER-004"]
        assert len(leer.ereignisse) == 0
        assert leer.aktuelle_version() == 0

    def test_wi_kontrakt_001_has_four_events(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        kontrakt = streams["WI-KONTRAKT-001"]
        assert len(kontrakt.ereignisse) == 4

    def test_wi_kontrakt_001_aktuelle_version_is_4(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        kontrakt = streams["WI-KONTRAKT-001"]
        assert kontrakt.aktuelle_version() == 4

    def test_wi_settlement_002_has_three_events(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        settlement = streams["WI-SETTLEMENT-002"]
        assert len(settlement.ereignisse) == 3

    def test_wi_settlement_002_aktuelle_version_is_3(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        settlement = streams["WI-SETTLEMENT-002"]
        assert settlement.aktuelle_version() == 3

    def test_wi_rechnung_003_has_two_events(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        rechnung = streams["WI-RECHNUNG-003"]
        assert len(rechnung.ereignisse) == 2

    def test_wi_kontrakt_001_first_event_is_erstellt(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        kontrakt = streams["WI-KONTRAKT-001"]
        first = min(kontrakt.ereignisse, key=lambda e: e.version)
        assert first.ereignis_typ == EreignisTyp.ERSTELLT

    def test_wi_kontrakt_001_last_event_is_abgeschlossen(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        kontrakt = streams["WI-KONTRAKT-001"]
        last = max(kontrakt.ereignisse, key=lambda e: e.version)
        assert last.ereignis_typ == EreignisTyp.ABGESCHLOSSEN

    def test_wi_settlement_002_contains_kompensiert(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        settlement = streams["WI-SETTLEMENT-002"]
        types = [e.ereignis_typ for e in settlement.ereignisse]
        assert EreignisTyp.KOMPENSIERT in types

    def test_wi_settlement_002_contains_fehler(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        settlement = streams["WI-SETTLEMENT-002"]
        types = [e.ereignis_typ for e in settlement.ereignisse]
        assert EreignisTyp.FEHLER_AUFGETRETEN in types

    def test_all_events_have_tenant_id(self):
        for stream in get_default_ereignis_streams():
            for e in stream.ereignisse:
                assert e.tenant_id != ""

    def test_wi_kontrakt_001_replay_vollstaendig(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        kontrakt = streams["WI-KONTRAKT-001"]
        result = kontrakt.replay(ReplayModus.VOLLSTAENDIG)
        assert len(result) == 4

    def test_wi_kontrakt_001_rekonstruierter_zustand_abgeschlossen(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        kontrakt = streams["WI-KONTRAKT-001"]
        zustand = rekonstruiere_zustand(kontrakt.replay(ReplayModus.VOLLSTAENDIG))
        assert zustand["zustand"] == "ABGESCHLOSSEN"

    def test_wi_settlement_002_rekonstruierter_zustand_kompensiert(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        settlement = streams["WI-SETTLEMENT-002"]
        zustand = rekonstruiere_zustand(settlement.replay(ReplayModus.VOLLSTAENDIG))
        assert zustand["zustand"] == "KOMPENSIERT"

    def test_wi_rechnung_003_rekonstruierter_zustand_freigabe(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        rechnung = streams["WI-RECHNUNG-003"]
        zustand = rekonstruiere_zustand(rechnung.replay(ReplayModus.VOLLSTAENDIG))
        assert zustand["zustand"] == "FREIGABE_AUSSTEHEND"

    def test_wi_leer_004_rekonstruierter_zustand_leer(self):
        streams = {s.stream_id: s for s in get_default_ereignis_streams()}
        leer = streams["WI-LEER-004"]
        zustand = rekonstruiere_zustand(leer.replay(ReplayModus.VOLLSTAENDIG))
        assert zustand == {}


# ─────────────────────────────────────────────────────────────────────────────
# Additional edge-case and integration tests
# ─────────────────────────────────────────────────────────────────────────────

class TestCircuitBreakerEdgeCases:
    def test_schwellwert_of_one_opens_immediately(self):
        rec = geschlossen_record(fehler_zaehler=0)
        cfg = default_config(schwellwert=1)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.OFFEN

    def test_halb_offen_max_one_closes_immediately(self):
        rec = halb_offen_record(erfolg_zaehler=0)
        cfg = default_config(halb_offen_max=1)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ERFOLG, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.GESCHLOSSEN

    def test_offen_timeout_zero_always_expired(self):
        rec = offen_record(letzter_fehler_vor_sek=1)
        cfg = default_config(timeout=0)
        assert rec.kann_anfrage_durchlassen(cfg, NOW) is True

    def test_multiple_failures_accumulate(self):
        rec = geschlossen_record()
        cfg = default_config(schwellwert=5)
        for _ in range(4):
            rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert rec.fehler_zaehler == 4
        assert rec.zustand == CircuitBreakerZustand.GESCHLOSSEN

    def test_fifth_failure_opens(self):
        rec = geschlossen_record()
        cfg = default_config(schwellwert=5)
        for _ in range(5):
            rec = rec.verarbeite_ergebnis(AufrufErgebnis.FEHLER, cfg, NOW)
        assert rec.zustand == CircuitBreakerZustand.OFFEN

    def test_success_after_failures_resets(self):
        rec = geschlossen_record(fehler_zaehler=3)
        cfg = default_config()
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ERFOLG, cfg, NOW)
        assert new_rec.fehler_zaehler == 0

    def test_halb_offen_one_short_of_closing(self):
        rec = halb_offen_record(erfolg_zaehler=1)
        cfg = default_config(halb_offen_max=3)
        new_rec = rec.verarbeite_ergebnis(AufrufErgebnis.ERFOLG, cfg, NOW)
        assert new_rec.zustand == CircuitBreakerZustand.HALB_OFFEN
        assert new_rec.erfolg_zaehler_halb_offen == 2

    def test_config_is_dataclass_with_all_fields(self):
        cfg = CircuitBreakerKonfiguration("X", "Y", 3, 45, 2, "desc")
        assert cfg.breaker_id == "X"
        assert cfg.service_name == "Y"
        assert cfg.fehler_schwellwert == 3
        assert cfg.wiederherstellungs_timeout_sekunden == 45
        assert cfg.halb_offen_max_anfragen == 2
        assert cfg.beschreibung == "desc"


class TestEventSourcingEdgeCases:
    def test_workflow_ereignis_fields(self):
        e = make_ereignis(1, EreignisTyp.ERSTELLT, {"key": "val"})
        assert e.ereignis_id == "EVT-001"
        assert e.workflow_instanz_id == "WI-TEST-001"
        assert e.ereignis_typ == EreignisTyp.ERSTELLT
        assert e.version == 1
        assert e.nutzlast == {"key": "val"}
        assert e.ausgefuehrt_von == "test-user"
        assert e.tenant_id == "TENANT-TEST"

    def test_zustand_geaendert_missing_key_preserves_existing(self):
        events = [
            make_ereignis(1, EreignisTyp.ERSTELLT),
            make_ereignis(2, EreignisTyp.ZUSTAND_GEAENDERT, {}),  # no neuer_zustand
        ]
        zustand = rekonstruiere_zustand(events)
        assert zustand["zustand"] == "ERSTELLT"  # fallback keeps previous

    def test_stream_id_matches_workflow_instanz_id(self):
        streams = get_default_ereignis_streams()
        for s in streams:
            for e in s.ereignisse:
                assert e.workflow_instanz_id == s.stream_id

    def test_ereignis_versions_monotonically_increasing(self):
        streams = get_default_ereignis_streams()
        for s in streams:
            if s.ereignisse:
                sorted_evts = sorted(s.ereignisse, key=lambda e: e.version)
                for i in range(len(sorted_evts) - 1):
                    assert sorted_evts[i].version < sorted_evts[i + 1].version

    def test_ab_version_2_skips_first(self):
        s = EreignisStream("WI-TEST")
        for i in range(1, 5):
            s.ereignisse.append(make_ereignis(i, EreignisTyp.ZUSTAND_GEAENDERT))
        result = s.replay(ReplayModus.AB_VERSION, ab_version=2)
        assert len(result) == 3
        assert result[0].version == 2

    def test_replay_does_not_modify_stream(self):
        s = EreignisStream("WI-TEST")
        s.ereignisse.append(make_ereignis(1, EreignisTyp.ERSTELLT))
        _ = s.replay(ReplayModus.VOLLSTAENDIG)
        assert len(s.ereignisse) == 1
