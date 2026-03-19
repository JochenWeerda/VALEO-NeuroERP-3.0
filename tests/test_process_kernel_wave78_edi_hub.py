"""
Wave 78 — EDI/API Hub (Gap 043)

Tests für DigitalExchangeCoverage (KPI >=80%), PartnerApiKey,
EdiHubAuftrag (Dispatch-Queue) und EdiHubMonitor.

Gap 043: EDI/API Hub für Kunden/Lieferanten/Behörden
KPI: >=80% Dokumentenaustausch digital (EDIFACT oder REST_API)
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import pytest

from app.core.edi_hub_contracts import (
    DigitalExchangeCoverage,
    EDIAcknowledgmentResult,
    EDINachricht,
    EDINachrichtenStatus,
    EDINachrichtenTyp,
    EDIPartner,
    EDIPartnerTyp,
    EDIStandard,
    EDIUebertragungsKanal,
    EdiHubAuftrag,
    EdiHubMonitor,
    PartnerApiKey,
    _DIGITALE_STANDARDS,
    evaluate_digital_coverage,
    get_default_edi_partners,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _partner(
    partner_id: str = "P-001",
    standard: EDIStandard = EDIStandard.EDIFACT,
    kanal: EDIUebertragungsKanal = EDIUebertragungsKanal.AS2,
) -> EDIPartner:
    return EDIPartner(
        partner_id=partner_id,
        name="Test Partner",
        typ=EDIPartnerTyp.LIEFERANT,
        edi_standard=standard,
        kanal=kanal,
        interchangeId="4012345000001",
        unterstuetzte_nachrichten=[EDINachrichtenTyp.ORDERS, EDINachrichtenTyp.INVOIC],
    )


def _nachricht(
    nachricht_id: str = "N-001",
    partner_id: str = "P-001",
    standard: EDIStandard = EDIStandard.EDIFACT,
    status: EDINachrichtenStatus = EDINachrichtenStatus.VERARBEITET,
) -> EDINachricht:
    return EDINachricht(
        nachricht_id=nachricht_id,
        partner_id=partner_id,
        typ=EDINachrichtenTyp.INVOIC,
        standard=standard,
        richtung="AUSGEHEND",
        status=status,
        erstellt_am=_now(),
    )


def _api_key(
    key_id: str = "K-001",
    partner_id: str = "P-REST-001",
    ablauf: datetime | None = None,
    aktiv: bool = True,
) -> PartnerApiKey:
    raw = "test-secret-key-value"
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    return PartnerApiKey(
        key_id=key_id,
        partner_id=partner_id,
        key_hash=key_hash,
        erstellt_am=_now() - timedelta(days=30),
        laeuft_ab_am=ablauf,
        aktiv=aktiv,
    )


def _auftrag(
    auftrag_id: str = "A-001",
    prioritaet: int = 2,
    max_versuche: int = 3,
) -> EdiHubAuftrag:
    return EdiHubAuftrag(
        auftrag_id=auftrag_id,
        partner_id="P-001",
        nachrichtentyp=EDINachrichtenTyp.ORDERS,
        prioritaet=prioritaet,
        payload_ref="BEST-2026-001",
        erstellt_am=_now(),
        max_versuche=max_versuche,
    )


# ---------------------------------------------------------------------------
# TestDigitalExchangeCoverage
# ---------------------------------------------------------------------------

class TestDigitalExchangeCoverage:
    """KPI-Messung: >=80% Dokumentenaustausch digital."""

    def test_kpi_erfuellt_bei_100_prozent(self):
        cov = DigitalExchangeCoverage(gesamt_dokumente=100, digital_dokumente=100)
        assert cov.kpi_erfuellt is True
        assert cov.coverage_pct == 100.0

    def test_kpi_erfuellt_bei_genau_80_prozent(self):
        cov = DigitalExchangeCoverage(gesamt_dokumente=100, digital_dokumente=80)
        assert cov.kpi_erfuellt is True
        assert cov.coverage_pct == 80.0

    def test_kpi_nicht_erfuellt_bei_79_prozent(self):
        cov = DigitalExchangeCoverage(gesamt_dokumente=100, digital_dokumente=79)
        assert cov.kpi_erfuellt is False
        assert cov.coverage_pct == 79.0

    def test_coverage_pct_gerundet(self):
        cov = DigitalExchangeCoverage(gesamt_dokumente=3, digital_dokumente=2)
        assert cov.coverage_pct == 66.67

    def test_gesamt_null_ergibt_null_prozent(self):
        cov = DigitalExchangeCoverage(gesamt_dokumente=0, digital_dokumente=0)
        assert cov.coverage_pct == 0.0
        assert cov.kpi_erfuellt is False

    def test_fehlend_fuer_kpi_bei_nicht_erfuellt(self):
        # 100 Dokumente, 60 digital → fehlen 20
        cov = DigitalExchangeCoverage(gesamt_dokumente=100, digital_dokumente=60)
        assert cov.fehlend_fuer_kpi == 20

    def test_fehlend_fuer_kpi_bei_erfuellt_ist_null(self):
        cov = DigitalExchangeCoverage(gesamt_dokumente=100, digital_dokumente=85)
        assert cov.fehlend_fuer_kpi == 0

    def test_as_dict_enthält_alle_felder(self):
        cov = DigitalExchangeCoverage(gesamt_dokumente=50, digital_dokumente=45)
        d = cov.as_dict()
        assert d["gesamt_dokumente"] == 50
        assert d["digital_dokumente"] == 45
        assert "coverage_pct" in d
        assert "kpi_erfuellt" in d
        assert "fehlend_fuer_kpi" in d
        assert "periode_beschreibung" in d

    def test_periode_beschreibung_default(self):
        cov = DigitalExchangeCoverage(gesamt_dokumente=10, digital_dokumente=10)
        assert cov.periode_beschreibung == "letzte 30 Tage"

    def test_digitale_standards_enthalten_edifact_und_json(self):
        assert EDIStandard.EDIFACT in _DIGITALE_STANDARDS
        assert EDIStandard.JSON_API in _DIGITALE_STANDARDS
        assert EDIStandard.XML_UBL in _DIGITALE_STANDARDS
        # CSV_FLAT ist nicht digital
        assert EDIStandard.CSV_FLAT not in _DIGITALE_STANDARDS


class TestEvaluateDigitalCoverage:
    """evaluate_digital_coverage() berechnet KPI aus echten Nachrichten."""

    def test_alle_edifact_partner_zaehlen_digital(self):
        partner_map = {"P-001": _partner("P-001", EDIStandard.EDIFACT)}
        msgs = [_nachricht("N-001", "P-001"), _nachricht("N-002", "P-001")]
        cov = evaluate_digital_coverage(msgs, partner_map)
        assert cov.gesamt_dokumente == 2
        assert cov.digital_dokumente == 2
        assert cov.kpi_erfuellt is True

    def test_csv_partner_zaehlt_nicht_digital(self):
        partner_map = {"P-CSV": _partner("P-CSV", EDIStandard.CSV_FLAT)}
        msgs = [_nachricht("N-1", "P-CSV", EDIStandard.CSV_FLAT)]
        cov = evaluate_digital_coverage(msgs, partner_map)
        assert cov.digital_dokumente == 0
        assert cov.kpi_erfuellt is False

    def test_gemischte_partner_berechnet_anteil(self):
        partner_map = {
            "P-EDI": _partner("P-EDI", EDIStandard.EDIFACT),
            "P-CSV": _partner("P-CSV", EDIStandard.CSV_FLAT),
        }
        # 8 EDIFACT + 2 CSV = 80% digital
        msgs = [_nachricht(f"N-{i}", "P-EDI") for i in range(8)]
        msgs += [_nachricht(f"N-{i+8}", "P-CSV", EDIStandard.CSV_FLAT) for i in range(2)]
        cov = evaluate_digital_coverage(msgs, partner_map)
        assert cov.coverage_pct == 80.0
        assert cov.kpi_erfuellt is True

    def test_unbekannter_partner_nutzt_nachricht_standard(self):
        # Partner nicht in partner_map, Nachricht hat JSON_API
        msgs = [_nachricht("N-1", "P-UNBEKANNT", EDIStandard.JSON_API)]
        cov = evaluate_digital_coverage(msgs, {})
        assert cov.digital_dokumente == 1

    def test_leere_liste_ergibt_null_coverage(self):
        cov = evaluate_digital_coverage([], {})
        assert cov.gesamt_dokumente == 0
        assert cov.kpi_erfuellt is False


# ---------------------------------------------------------------------------
# TestPartnerApiKey
# ---------------------------------------------------------------------------

class TestPartnerApiKey:
    """REST-API-Schlüssel für non-EDIFACT Partner."""

    def test_gueltig_ohne_ablaufdatum(self):
        key = _api_key()
        assert key.ist_gueltig is True
        assert key.ist_abgelaufen is False

    def test_abgelaufen_wenn_ablauf_in_vergangenheit(self):
        ablauf = _now() - timedelta(hours=1)
        key = _api_key(ablauf=ablauf)
        assert key.ist_abgelaufen is True
        assert key.ist_gueltig is False

    def test_nicht_abgelaufen_wenn_ablauf_in_zukunft(self):
        ablauf = _now() + timedelta(days=365)
        key = _api_key(ablauf=ablauf)
        assert key.ist_abgelaufen is False
        assert key.ist_gueltig is True

    def test_deaktivierter_key_nicht_gueltig(self):
        key = _api_key(aktiv=False)
        assert key.ist_gueltig is False

    def test_verify_hash_korrekt(self):
        raw = "test-secret-key-value"
        key_hash = hashlib.sha256(raw.encode()).hexdigest()
        key = _api_key()
        assert key.verify_hash(key_hash) is True

    def test_verify_hash_falscher_hash(self):
        key = _api_key()
        assert key.verify_hash("falscherHash123") is False

    def test_verify_hash_fehlschlaegt_bei_abgelaufen(self):
        raw = "test-secret-key-value"
        key_hash = hashlib.sha256(raw.encode()).hexdigest()
        ablauf = _now() - timedelta(days=1)
        key = _api_key(ablauf=ablauf)
        assert key.verify_hash(key_hash) is False

    def test_as_dict_enthält_kein_plaintext(self):
        key = _api_key()
        d = key.as_dict()
        # Nie Plaintext-Key
        assert "test-secret-key-value" not in str(d)
        assert "key_hash" in d
        assert "ist_gueltig" in d


# ---------------------------------------------------------------------------
# TestEdiHubAuftrag
# ---------------------------------------------------------------------------

class TestEdiHubAuftrag:
    """Dispatch-Queue für ausgehende EDI-Nachrichten."""

    def test_neuer_auftrag_status_pending(self):
        auftrag = _auftrag()
        assert auftrag.status == EDINachrichtenStatus.PENDING
        assert auftrag.versuche == 0

    def test_versuch_starten_erhoeht_zaehler(self):
        auftrag = _auftrag()
        auftrag.versuch_starten()
        assert auftrag.versuche == 1
        assert auftrag.status == EDINachrichtenStatus.GESENDET

    def test_versuch_fehlgeschlagen_setzt_fehler_status(self):
        auftrag = _auftrag()
        auftrag.versuch_starten()
        auftrag.versuch_fehlgeschlagen("Connection refused")
        assert auftrag.status == EDINachrichtenStatus.FEHLER
        assert auftrag.letzter_fehler == "Connection refused"

    def test_kann_wiederholt_werden_nach_fehler(self):
        auftrag = _auftrag(max_versuche=3)
        auftrag.versuch_starten()
        auftrag.versuch_fehlgeschlagen("Timeout")
        assert auftrag.versuche == 1
        assert auftrag.kann_wiederholt_werden is True

    def test_kann_nicht_wiederholt_werden_nach_max_versuche(self):
        auftrag = _auftrag(max_versuche=2)
        for _ in range(2):
            auftrag.versuch_starten()
            auftrag.versuch_fehlgeschlagen("Fehler")
        assert auftrag.kann_wiederholt_werden is False

    def test_erfolgreich_setzt_quittiert_status(self):
        auftrag = _auftrag()
        auftrag.versuch_starten()
        auftrag.versuch_erfolgreich()
        assert auftrag.status == EDINachrichtenStatus.QUITTIERT
        assert auftrag.kann_wiederholt_werden is False

    def test_ungueltige_prioritaet_wirft_fehler(self):
        with pytest.raises(ValueError, match="Prioritaet"):
            _auftrag(prioritaet=0)
        with pytest.raises(ValueError, match="Prioritaet"):
            _auftrag(prioritaet=6)

    def test_ungueltige_max_versuche_wirft_fehler(self):
        with pytest.raises(ValueError, match="max_versuche"):
            EdiHubAuftrag(
                auftrag_id="A-X",
                partner_id="P-001",
                nachrichtentyp=EDINachrichtenTyp.ORDERS,
                prioritaet=1,
                payload_ref="X",
                erstellt_am=_now(),
                max_versuche=0,
            )

    def test_as_dict_vollstaendig(self):
        auftrag = _auftrag()
        d = auftrag.as_dict()
        assert d["auftrag_id"] == "A-001"
        assert d["status"] == "PENDING"
        assert d["kann_wiederholt_werden"] is False
        assert "prioritaet" in d
        assert "payload_ref" in d


# ---------------------------------------------------------------------------
# TestEdiHubMonitor
# ---------------------------------------------------------------------------

class TestEdiHubMonitor:
    """Monitoring-Snapshot des EDI/API Hubs."""

    def _gesunder_monitor(self) -> EdiHubMonitor:
        return EdiHubMonitor(
            snapshot_zeitpunkt=_now(),
            aktive_partner=5,
            nachrichten_gesamt_24h=200,
            nachrichten_fehler_24h=4,        # 2% Fehlerquote
            sla_verletzungen_24h=0,
            ausstehende_auftraege=3,
            digital_coverage=DigitalExchangeCoverage(
                gesamt_dokumente=200,
                digital_dokumente=180,       # 90% digital
            ),
        )

    def test_gesunder_hub(self):
        monitor = self._gesunder_monitor()
        assert monitor.hub_gesund is True
        assert monitor.alert_level == "OK"

    def test_fehlerquote_berechnung(self):
        monitor = self._gesunder_monitor()
        assert monitor.fehlerquote_pct == 2.0

    def test_hub_nicht_gesund_bei_kpi_verletzt(self):
        monitor = self._gesunder_monitor()
        monitor.digital_coverage = DigitalExchangeCoverage(
            gesamt_dokumente=100, digital_dokumente=70  # 70% < 80%
        )
        assert monitor.hub_gesund is False
        assert monitor.alert_level == "WARN"

    def test_hub_nicht_gesund_bei_hoher_fehlerquote(self):
        monitor = self._gesunder_monitor()
        monitor.nachrichten_fehler_24h = 15  # 7.5%
        assert monitor.hub_gesund is False
        assert monitor.alert_level == "WARN"

    def test_alert_level_critical_bei_vielen_sla_verletzungen(self):
        monitor = self._gesunder_monitor()
        monitor.sla_verletzungen_24h = 5
        assert monitor.alert_level == "CRITICAL"

    def test_alert_level_critical_bei_hoher_fehlerquote(self):
        monitor = self._gesunder_monitor()
        monitor.nachrichten_fehler_24h = 50  # 25%
        assert monitor.alert_level == "CRITICAL"

    def test_fehlerquote_null_bei_keine_nachrichten(self):
        monitor = self._gesunder_monitor()
        monitor.nachrichten_gesamt_24h = 0
        monitor.nachrichten_fehler_24h = 0
        assert monitor.fehlerquote_pct == 0.0

    def test_as_dict_vollstaendig(self):
        monitor = self._gesunder_monitor()
        d = monitor.as_dict()
        assert "snapshot_zeitpunkt" in d
        assert "aktive_partner" in d
        assert "fehlerquote_pct" in d
        assert "hub_gesund" in d
        assert "alert_level" in d
        assert "digital_coverage" in d
        assert d["digital_coverage"]["kpi_erfuellt"] is True


# ---------------------------------------------------------------------------
# TestIntegrationSzenario
# ---------------------------------------------------------------------------

class TestIntegrationSzenario:
    """End-to-End Szenarien für den EDI/API Hub."""

    def test_default_partner_katalog_liefert_gesunden_hub(self):
        """Default-Partner reichen für >80% digitale Abdeckung."""
        partner_map = {p.partner_id: p for p in get_default_edi_partners()}
        # Simuliere 100 Nachrichten: 80 EDIFACT-Partner, 20 Email-Partner
        msgs = []
        edi_partner_id = "EP-LFS-001"   # AS2/EDIFACT → digital
        for i in range(90):
            msgs.append(_nachricht(f"N-{i}", edi_partner_id, EDIStandard.EDIFACT))
        # 10 unbekannte CSV (nicht digital)
        for i in range(10):
            msgs.append(_nachricht(f"N-csv-{i}", "P-CSV-LEGACY", EDIStandard.CSV_FLAT))
        # P-CSV-LEGACY hat keinen Eintrag im partner_map → nutzt Nachrichtenstandard
        cov = evaluate_digital_coverage(msgs, partner_map)
        assert cov.coverage_pct == 90.0
        assert cov.kpi_erfuellt is True

    def test_vollstaendiger_dispatch_zyklus(self):
        """Auftrag → Versuch 1 Fehler → Versuch 2 Erfolg."""
        auftrag = _auftrag(max_versuche=3)
        assert auftrag.status == EDINachrichtenStatus.PENDING

        auftrag.versuch_starten()
        auftrag.versuch_fehlgeschlagen("AS2 timeout")
        assert auftrag.kann_wiederholt_werden is True
        assert auftrag.versuche == 1

        auftrag.versuch_starten()
        auftrag.versuch_erfolgreich()
        assert auftrag.status == EDINachrichtenStatus.QUITTIERT
        assert auftrag.versuche == 2
        assert auftrag.kann_wiederholt_werden is False

    def test_api_key_rotation_szenario(self):
        """Alter Key abgelaufen, neuer Key aktiv."""
        alter_key = _api_key("K-ALT", ablauf=_now() - timedelta(hours=1))
        neuer_key = _api_key("K-NEU", ablauf=_now() + timedelta(days=90))

        raw = "test-secret-key-value"
        guter_hash = hashlib.sha256(raw.encode()).hexdigest()

        assert alter_key.verify_hash(guter_hash) is False  # abgelaufen
        assert neuer_key.verify_hash(guter_hash) is True

    def test_monitor_aggregiert_kpi_korrekt(self):
        """Monitor zeigt richtigen Alert-Level bei Grenzwert-Coverage."""
        # Genau 80% digital → KPI erfüllt, aber gerade so
        coverage = DigitalExchangeCoverage(
            gesamt_dokumente=500, digital_dokumente=400  # 80.0%
        )
        monitor = EdiHubMonitor(
            snapshot_zeitpunkt=_now(),
            aktive_partner=8,
            nachrichten_gesamt_24h=500,
            nachrichten_fehler_24h=10,   # 2%
            sla_verletzungen_24h=0,
            ausstehende_auftraege=0,
            digital_coverage=coverage,
        )
        assert monitor.hub_gesund is True
        assert monitor.alert_level == "OK"

    def test_kpi_verbesserungspfad(self):
        """Dokument-Migration: zeigt fehlende Schritte bis zum KPI."""
        cov = DigitalExchangeCoverage(gesamt_dokumente=100, digital_dokumente=60)
        assert cov.kpi_erfuellt is False
        fehlend = cov.fehlend_fuer_kpi
        # 20 weitere migrieren
        cov_verbessert = DigitalExchangeCoverage(
            gesamt_dokumente=100,
            digital_dokumente=60 + fehlend,
        )
        assert cov_verbessert.kpi_erfuellt is True

    def test_hub_partner_typen_abgedeckt(self):
        """Default-Partner enthält Lieferant, Kunde, Behörde, Spediteur."""
        partner = get_default_edi_partners()
        typen = {p.typ for p in partner}
        assert EDIPartnerTyp.LIEFERANT in typen
        assert EDIPartnerTyp.KUNDE in typen
        assert EDIPartnerTyp.BEHOERDE in typen
        assert EDIPartnerTyp.SPEDITEUR in typen
