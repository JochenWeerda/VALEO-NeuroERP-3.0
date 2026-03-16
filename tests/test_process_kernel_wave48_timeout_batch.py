"""
Wave 48 — Process Kernel: Timeout Contracts + Workflow Batch Contracts
Tests for:
  - app.core.process_timeout_contracts
  - app.core.workflow_batch_contracts
"""
from datetime import datetime, timedelta

import pytest

# ---------------------------------------------------------------------------
# Module imports
# ---------------------------------------------------------------------------
from app.core.process_timeout_contracts import (
    TimeoutTyp,
    TimeoutAktion,
    TimeoutStatus,
    TimeoutRegel,
    TimeoutPruefung,
    pruefe_timeout,
    get_default_timeout_regeln,
)
from app.core.workflow_batch_contracts import (
    BatchTyp,
    BatchStatus,
    ChunkStatus,
    BatchChunk,
    BatchJob,
    berechne_batch_status,
    erstelle_chunks,
    get_default_batch_jobs,
)


# ===========================================================================
# MODULE 1: process_timeout_contracts
# ===========================================================================

class TestTimeoutTypEnum:
    def test_absolut_exists(self):
        assert TimeoutTyp.ABSOLUT is not None

    def test_relativ_exists(self):
        assert TimeoutTyp.RELATIV is not None

    def test_geschaeftszeit_exists(self):
        assert TimeoutTyp.GESCHAEFTSZEIT is not None

    def test_sla_gebunden_exists(self):
        assert TimeoutTyp.SLA_GEBUNDEN is not None

    def test_all_four_values(self):
        values = {t.name for t in TimeoutTyp}
        assert values == {"ABSOLUT", "RELATIV", "GESCHAEFTSZEIT", "SLA_GEBUNDEN"}


class TestTimeoutAktionEnum:
    def test_eskalieren_exists(self):
        assert TimeoutAktion.ESKALIEREN is not None

    def test_abbrechen_exists(self):
        assert TimeoutAktion.ABBRECHEN is not None

    def test_benachrichtigen_exists(self):
        assert TimeoutAktion.BENACHRICHTIGEN is not None

    def test_automatisch_fortfahren_exists(self):
        assert TimeoutAktion.AUTOMATISCH_FORTFAHREN is not None

    def test_all_four_values(self):
        values = {t.name for t in TimeoutAktion}
        assert values == {"ESKALIEREN", "ABBRECHEN", "BENACHRICHTIGEN", "AUTOMATISCH_FORTFAHREN"}


class TestTimeoutStatusEnum:
    def test_ausstehend_exists(self):
        assert TimeoutStatus.AUSSTEHEND is not None

    def test_mahnphase_exists(self):
        assert TimeoutStatus.MAHNPHASE is not None

    def test_abgelaufen_exists(self):
        assert TimeoutStatus.ABGELAUFEN is not None

    def test_aufgehoben_exists(self):
        assert TimeoutStatus.AUFGEHOBEN is not None

    def test_erledigt_exists(self):
        assert TimeoutStatus.ERLEDIGT is not None

    def test_all_five_values(self):
        values = {t.name for t in TimeoutStatus}
        assert values == {"AUSSTEHEND", "MAHNPHASE", "ABGELAUFEN", "AUFGEHOBEN", "ERLEDIGT"}


class TestTimeoutRegel:
    def _make_regel(self, **kwargs):
        defaults = dict(
            regel_id="TR-TEST",
            schritt_id="test_schritt",
            timeout_typ=TimeoutTyp.RELATIV,
            timeout_minuten=100,
            aktion_bei_timeout=TimeoutAktion.ESKALIEREN,
            mahngrenze_pct=80,
            beschreibung="Test-Regel",
        )
        defaults.update(kwargs)
        return TimeoutRegel(**defaults)

    def test_berechne_deadline_basic(self):
        regel = self._make_regel(timeout_minuten=60)
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        expected = datetime(2026, 3, 16, 11, 0, 0)
        assert regel.berechne_deadline(erstellt_am) == expected

    def test_berechne_deadline_240min(self):
        regel = self._make_regel(timeout_minuten=240)
        erstellt_am = datetime(2026, 3, 16, 8, 0, 0)
        expected = datetime(2026, 3, 16, 12, 0, 0)
        assert regel.berechne_deadline(erstellt_am) == expected

    def test_berechne_deadline_2880min(self):
        regel = self._make_regel(timeout_minuten=2880)
        erstellt_am = datetime(2026, 3, 14, 10, 0, 0)
        expected = datetime(2026, 3, 16, 10, 0, 0)
        assert regel.berechne_deadline(erstellt_am) == expected

    def test_berechne_mahnzeitpunkt_80pct(self):
        regel = self._make_regel(timeout_minuten=100, mahngrenze_pct=80)
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        expected = erstellt_am + timedelta(minutes=80)
        assert regel.berechne_mahnzeitpunkt(erstellt_am) == expected

    def test_berechne_mahnzeitpunkt_75pct(self):
        regel = self._make_regel(timeout_minuten=240, mahngrenze_pct=75)
        erstellt_am = datetime(2026, 3, 16, 8, 0, 0)
        expected = erstellt_am + timedelta(minutes=180)
        assert regel.berechne_mahnzeitpunkt(erstellt_am) == expected

    def test_berechne_mahnzeitpunkt_90pct(self):
        regel = self._make_regel(timeout_minuten=2880, mahngrenze_pct=90)
        erstellt_am = datetime(2026, 3, 14, 10, 0, 0)
        expected = erstellt_am + timedelta(minutes=2592)
        assert regel.berechne_mahnzeitpunkt(erstellt_am) == expected

    def test_as_dict_contains_all_fields(self):
        regel = self._make_regel()
        d = regel.as_dict()
        assert "regel_id" in d
        assert "schritt_id" in d
        assert "timeout_typ" in d
        assert "timeout_minuten" in d
        assert "aktion_bei_timeout" in d
        assert "mahngrenze_pct" in d
        assert "beschreibung" in d

    def test_default_beschreibung_empty(self):
        regel = TimeoutRegel(
            regel_id="TR-X",
            schritt_id="x",
            timeout_typ=TimeoutTyp.ABSOLUT,
            timeout_minuten=30,
            aktion_bei_timeout=TimeoutAktion.ABBRECHEN,
        )
        assert regel.beschreibung == ""

    def test_default_mahngrenze_pct_80(self):
        regel = TimeoutRegel(
            regel_id="TR-X",
            schritt_id="x",
            timeout_typ=TimeoutTyp.ABSOLUT,
            timeout_minuten=30,
            aktion_bei_timeout=TimeoutAktion.ABBRECHEN,
        )
        assert regel.mahngrenze_pct == 80


class TestTimeoutPruefung:
    def _make_pruefung(self, status=TimeoutStatus.AUSSTEHEND, aktion=None):
        jetzt = datetime(2026, 3, 16, 10, 30, 0)
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        deadline = datetime(2026, 3, 16, 11, 0, 0)
        mahnzeitpunkt = datetime(2026, 3, 16, 10, 48, 0)
        return TimeoutPruefung(
            instanz_id="INST-001",
            schritt_id="test",
            timeout_status=status,
            aktion=aktion,
            erstellt_am=erstellt_am,
            deadline=deadline,
            mahnzeitpunkt=mahnzeitpunkt,
            verbrauchte_minuten=30.0,
            verbleibende_minuten=30.0,
            auslastung_pct=50.0,
            geprueft_am=jetzt,
        )

    def test_ist_abgelaufen_true(self):
        p = self._make_pruefung(status=TimeoutStatus.ABGELAUFEN)
        assert p.ist_abgelaufen is True

    def test_ist_abgelaufen_false_for_ausstehend(self):
        p = self._make_pruefung(status=TimeoutStatus.AUSSTEHEND)
        assert p.ist_abgelaufen is False

    def test_ist_in_mahnphase_true(self):
        p = self._make_pruefung(status=TimeoutStatus.MAHNPHASE)
        assert p.ist_in_mahnphase is True

    def test_ist_in_mahnphase_false_for_ausstehend(self):
        p = self._make_pruefung(status=TimeoutStatus.AUSSTEHEND)
        assert p.ist_in_mahnphase is False

    def test_ist_in_mahnphase_false_for_abgelaufen(self):
        p = self._make_pruefung(status=TimeoutStatus.ABGELAUFEN)
        assert p.ist_in_mahnphase is False

    def test_as_dict_contains_required_keys(self):
        p = self._make_pruefung()
        d = p.as_dict()
        for key in [
            "instanz_id", "schritt_id", "timeout_status", "aktion",
            "erstellt_am", "deadline", "mahnzeitpunkt",
            "verbrauchte_minuten", "verbleibende_minuten", "auslastung_pct", "geprueft_am",
        ]:
            assert key in d, f"Missing key: {key}"

    def test_as_dict_aktion_none_when_none(self):
        p = self._make_pruefung(aktion=None)
        d = p.as_dict()
        assert d["aktion"] is None

    def test_as_dict_aktion_value_when_set(self):
        p = self._make_pruefung(aktion=TimeoutAktion.ESKALIEREN)
        d = p.as_dict()
        assert d["aktion"] == TimeoutAktion.ESKALIEREN.value


class TestPruefeTimeout:
    def _make_regel(self, minuten=100, mahngrenze_pct=80, aktion=TimeoutAktion.ESKALIEREN):
        return TimeoutRegel(
            regel_id="TR-T",
            schritt_id="schritt",
            timeout_typ=TimeoutTyp.RELATIV,
            timeout_minuten=minuten,
            aktion_bei_timeout=aktion,
            mahngrenze_pct=mahngrenze_pct,
        )

    def test_ausstehend_before_mahnphase(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=100, mahngrenze_pct=80)
        # 80% of 100 = 80 min → Mahnung at 10:20 → before that is AUSSTEHEND
        jetzt = erstellt_am + timedelta(minutes=10)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert result.timeout_status == TimeoutStatus.AUSSTEHEND
        assert result.aktion is None

    def test_mahnphase_between_mahnung_and_deadline(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=100, mahngrenze_pct=80)
        # Mahnung at 80min, Deadline at 100min → 90min is MAHNPHASE
        jetzt = erstellt_am + timedelta(minutes=90)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert result.timeout_status == TimeoutStatus.MAHNPHASE
        assert result.aktion == TimeoutAktion.BENACHRICHTIGEN

    def test_abgelaufen_after_deadline(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=100, mahngrenze_pct=80)
        jetzt = erstellt_am + timedelta(minutes=120)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert result.timeout_status == TimeoutStatus.ABGELAUFEN

    def test_abgelaufen_aktion_from_regel(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=100, aktion=TimeoutAktion.ABBRECHEN)
        jetzt = erstellt_am + timedelta(minutes=101)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert result.aktion == TimeoutAktion.ABBRECHEN

    def test_abgelaufen_with_automatisch_fortfahren(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=60, aktion=TimeoutAktion.AUTOMATISCH_FORTFAHREN)
        jetzt = erstellt_am + timedelta(minutes=65)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert result.timeout_status == TimeoutStatus.ABGELAUFEN
        assert result.aktion == TimeoutAktion.AUTOMATISCH_FORTFAHREN

    def test_mahnphase_always_benachrichtigen(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=100, mahngrenze_pct=80, aktion=TimeoutAktion.ABBRECHEN)
        jetzt = erstellt_am + timedelta(minutes=85)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert result.aktion == TimeoutAktion.BENACHRICHTIGEN

    def test_verbrauchte_minuten_calculation(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=100)
        jetzt = erstellt_am + timedelta(minutes=30)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert abs(result.verbrauchte_minuten - 30.0) < 0.01

    def test_verbleibende_minuten_calculation(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=100)
        jetzt = erstellt_am + timedelta(minutes=30)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert abs(result.verbleibende_minuten - 70.0) < 0.01

    def test_verbleibende_minuten_negative_when_past_deadline(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=100)
        jetzt = erstellt_am + timedelta(minutes=120)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert result.verbleibende_minuten < 0

    def test_auslastung_pct_calculation(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=100)
        jetzt = erstellt_am + timedelta(minutes=50)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert abs(result.auslastung_pct - 50.0) < 0.1

    def test_custom_jetzt_parameter(self):
        erstellt_am = datetime(2026, 1, 1, 0, 0, 0)
        regel = self._make_regel(minuten=60)
        custom_jetzt = datetime(2026, 1, 1, 0, 30, 0)
        result = pruefe_timeout("INST-002", "schritt", regel, erstellt_am, jetzt=custom_jetzt)
        assert result.timeout_status == TimeoutStatus.AUSSTEHEND

    def test_exact_deadline_is_abgelaufen(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=60)
        jetzt = erstellt_am + timedelta(minutes=60)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert result.timeout_status == TimeoutStatus.ABGELAUFEN

    def test_exact_mahnzeitpunkt_is_mahnphase(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(minuten=100, mahngrenze_pct=80)
        # Mahnzeitpunkt is exactly at 80 min
        jetzt = erstellt_am + timedelta(minutes=80)
        result = pruefe_timeout("INST-001", "schritt", regel, erstellt_am, jetzt=jetzt)
        assert result.timeout_status == TimeoutStatus.MAHNPHASE

    def test_result_contains_instanz_and_schritt_id(self):
        erstellt_am = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel()
        jetzt = erstellt_am + timedelta(minutes=10)
        result = pruefe_timeout("INST-XYZ", "schritt_abc", regel, erstellt_am, jetzt=jetzt)
        assert result.instanz_id == "INST-XYZ"
        assert result.schritt_id == "schritt_abc"


class TestGetDefaultTimeoutRegeln:
    def setup_method(self):
        self.regeln = get_default_timeout_regeln()
        self.regeln_by_id = {r.regel_id: r for r in self.regeln}

    def test_returns_five_rules(self):
        assert len(self.regeln) == 5

    def test_tr001_exists(self):
        assert "TR-001" in self.regeln_by_id

    def test_tr002_exists(self):
        assert "TR-002" in self.regeln_by_id

    def test_tr003_exists(self):
        assert "TR-003" in self.regeln_by_id

    def test_tr004_exists(self):
        assert "TR-004" in self.regeln_by_id

    def test_tr005_exists(self):
        assert "TR-005" in self.regeln_by_id

    def test_tr001_schritt_id(self):
        assert self.regeln_by_id["TR-001"].schritt_id == "kontrakt_freigabe"

    def test_tr001_timeout_typ_relativ(self):
        assert self.regeln_by_id["TR-001"].timeout_typ == TimeoutTyp.RELATIV

    def test_tr001_timeout_minuten(self):
        assert self.regeln_by_id["TR-001"].timeout_minuten == 240

    def test_tr001_aktion_eskalieren(self):
        assert self.regeln_by_id["TR-001"].aktion_bei_timeout == TimeoutAktion.ESKALIEREN

    def test_tr001_mahngrenze_75(self):
        assert self.regeln_by_id["TR-001"].mahngrenze_pct == 75

    def test_tr002_schritt_id(self):
        assert self.regeln_by_id["TR-002"].schritt_id == "settlement_freigabe"

    def test_tr002_timeout_typ_geschaeftszeit(self):
        assert self.regeln_by_id["TR-002"].timeout_typ == TimeoutTyp.GESCHAEFTSZEIT

    def test_tr002_timeout_minuten(self):
        assert self.regeln_by_id["TR-002"].timeout_minuten == 480

    def test_tr003_schritt_id(self):
        assert self.regeln_by_id["TR-003"].schritt_id == "ap_rechnungseingang"

    def test_tr003_timeout_typ_sla_gebunden(self):
        assert self.regeln_by_id["TR-003"].timeout_typ == TimeoutTyp.SLA_GEBUNDEN

    def test_tr003_timeout_minuten(self):
        assert self.regeln_by_id["TR-003"].timeout_minuten == 2880

    def test_tr003_aktion_benachrichtigen(self):
        assert self.regeln_by_id["TR-003"].aktion_bei_timeout == TimeoutAktion.BENACHRICHTIGEN

    def test_tr004_aktion_automatisch_fortfahren(self):
        assert self.regeln_by_id["TR-004"].aktion_bei_timeout == TimeoutAktion.AUTOMATISCH_FORTFAHREN

    def test_tr004_timeout_minuten(self):
        assert self.regeln_by_id["TR-004"].timeout_minuten == 60

    def test_tr005_aktion_abbrechen(self):
        assert self.regeln_by_id["TR-005"].aktion_bei_timeout == TimeoutAktion.ABBRECHEN

    def test_tr005_schritt_id_wildcard(self):
        assert self.regeln_by_id["TR-005"].schritt_id == "*"

    def test_tr005_timeout_minuten(self):
        assert self.regeln_by_id["TR-005"].timeout_minuten == 1440


# ===========================================================================
# MODULE 2: workflow_batch_contracts
# ===========================================================================

class TestBatchTypEnum:
    def test_import_exists(self):
        assert BatchTyp.IMPORT is not None

    def test_export_exists(self):
        assert BatchTyp.EXPORT is not None

    def test_verarbeitung_exists(self):
        assert BatchTyp.VERARBEITUNG is not None

    def test_abrechnung_exists(self):
        assert BatchTyp.ABRECHNUNG is not None

    def test_archivierung_exists(self):
        assert BatchTyp.ARCHIVIERUNG is not None

    def test_all_five_values(self):
        values = {t.name for t in BatchTyp}
        assert values == {"IMPORT", "EXPORT", "VERARBEITUNG", "ABRECHNUNG", "ARCHIVIERUNG"}


class TestBatchStatusEnum:
    def test_all_values_exist(self):
        values = {t.name for t in BatchStatus}
        assert values == {
            "AUSSTEHEND", "LAUFEND", "PAUSIERT",
            "ABGESCHLOSSEN", "FEHLGESCHLAGEN", "TEILWEISE_ERFOLGREICH"
        }


class TestChunkStatusEnum:
    def test_all_values_exist(self):
        values = {t.name for t in ChunkStatus}
        assert values == {"AUSSTEHEND", "LAUFEND", "ERFOLGREICH", "FEHLGESCHLAGEN", "UEBERSPRUNGEN"}


class TestBatchChunk:
    def _make_chunk(self, status=ChunkStatus.AUSSTEHEND):
        return BatchChunk(
            chunk_id="BJ-001-CHK-001",
            batch_id="BJ-001",
            chunk_nummer=1,
            anzahl_datensaetze=100,
            status=status,
        )

    def test_ist_abgeschlossen_erfolgreich(self):
        assert self._make_chunk(ChunkStatus.ERFOLGREICH).ist_abgeschlossen is True

    def test_ist_abgeschlossen_fehlgeschlagen(self):
        assert self._make_chunk(ChunkStatus.FEHLGESCHLAGEN).ist_abgeschlossen is True

    def test_ist_abgeschlossen_uebersprungen(self):
        assert self._make_chunk(ChunkStatus.UEBERSPRUNGEN).ist_abgeschlossen is True

    def test_ist_abgeschlossen_false_for_ausstehend(self):
        assert self._make_chunk(ChunkStatus.AUSSTEHEND).ist_abgeschlossen is False

    def test_ist_abgeschlossen_false_for_laufend(self):
        assert self._make_chunk(ChunkStatus.LAUFEND).ist_abgeschlossen is False

    def test_ist_erfolgreich_true(self):
        assert self._make_chunk(ChunkStatus.ERFOLGREICH).ist_erfolgreich is True

    def test_ist_erfolgreich_false_fehlgeschlagen(self):
        assert self._make_chunk(ChunkStatus.FEHLGESCHLAGEN).ist_erfolgreich is False

    def test_ist_erfolgreich_false_uebersprungen(self):
        assert self._make_chunk(ChunkStatus.UEBERSPRUNGEN).ist_erfolgreich is False

    def test_ist_erfolgreich_false_ausstehend(self):
        assert self._make_chunk(ChunkStatus.AUSSTEHEND).ist_erfolgreich is False

    def test_as_dict_contains_all_keys(self):
        chunk = self._make_chunk()
        d = chunk.as_dict()
        for key in ["chunk_id", "batch_id", "chunk_nummer", "anzahl_datensaetze", "status", "fehlermeldung", "verarbeitet_am"]:
            assert key in d, f"Missing key: {key}"

    def test_as_dict_verarbeitet_am_none(self):
        chunk = self._make_chunk()
        d = chunk.as_dict()
        assert d["verarbeitet_am"] is None

    def test_as_dict_verarbeitet_am_iso_when_set(self):
        chunk = BatchChunk(
            chunk_id="X",
            batch_id="B",
            chunk_nummer=1,
            anzahl_datensaetze=10,
            status=ChunkStatus.ERFOLGREICH,
            verarbeitet_am=datetime(2026, 3, 16, 12, 0, 0),
        )
        d = chunk.as_dict()
        assert isinstance(d["verarbeitet_am"], str)
        assert "2026" in d["verarbeitet_am"]

    def test_default_fehlermeldung_empty(self):
        chunk = self._make_chunk()
        assert chunk.fehlermeldung == ""


class TestBatchJob:
    def _make_job(self, chunks=None):
        return BatchJob(
            batch_id="BJ-T",
            batch_name="Test-Job",
            batch_typ=BatchTyp.VERARBEITUNG,
            tenant_id="TENANT-001",
            status=BatchStatus.AUSSTEHEND,
            gesamt_datensaetze=400,
            chunk_groesse=100,
            erstellt_am=datetime(2026, 3, 16, 8, 0, 0),
            chunks=chunks or [],
        )

    def _make_chunk(self, nr, status):
        return BatchChunk(
            chunk_id=f"BJ-T-CHK-{nr:03d}",
            batch_id="BJ-T",
            chunk_nummer=nr,
            anzahl_datensaetze=100,
            status=status,
        )

    def test_gesamt_chunks_no_chunks(self):
        job = self._make_job()
        assert job.gesamt_chunks == 0

    def test_gesamt_chunks_with_four(self):
        chunks = [self._make_chunk(i, ChunkStatus.AUSSTEHEND) for i in range(1, 5)]
        job = self._make_job(chunks)
        assert job.gesamt_chunks == 4

    def test_fortschritt_pct_no_chunks(self):
        job = self._make_job()
        assert job.fortschritt_pct == 0.0

    def test_fortschritt_pct_half_done(self):
        chunks = [
            self._make_chunk(1, ChunkStatus.ERFOLGREICH),
            self._make_chunk(2, ChunkStatus.ERFOLGREICH),
            self._make_chunk(3, ChunkStatus.AUSSTEHEND),
            self._make_chunk(4, ChunkStatus.AUSSTEHEND),
        ]
        job = self._make_job(chunks)
        assert job.fortschritt_pct == 50.0

    def test_fortschritt_pct_all_done(self):
        chunks = [self._make_chunk(i, ChunkStatus.ERFOLGREICH) for i in range(1, 5)]
        job = self._make_job(chunks)
        assert job.fortschritt_pct == 100.0

    def test_fehlerrate_pct_no_chunks(self):
        job = self._make_job()
        assert job.fehlerrate_pct == 0.0

    def test_fehlerrate_pct_one_of_four(self):
        chunks = [
            self._make_chunk(1, ChunkStatus.ERFOLGREICH),
            self._make_chunk(2, ChunkStatus.ERFOLGREICH),
            self._make_chunk(3, ChunkStatus.ERFOLGREICH),
            self._make_chunk(4, ChunkStatus.FEHLGESCHLAGEN),
        ]
        job = self._make_job(chunks)
        assert job.fehlerrate_pct == 25.0

    def test_verarbeitete_datensaetze_only_erfolgreich(self):
        chunks = [
            self._make_chunk(1, ChunkStatus.ERFOLGREICH),
            self._make_chunk(2, ChunkStatus.FEHLGESCHLAGEN),
            self._make_chunk(3, ChunkStatus.ERFOLGREICH),
        ]
        job = self._make_job(chunks)
        assert job.verarbeitete_datensaetze == 200

    def test_abgeschlossene_chunks_counts_all_terminal_states(self):
        chunks = [
            self._make_chunk(1, ChunkStatus.ERFOLGREICH),
            self._make_chunk(2, ChunkStatus.FEHLGESCHLAGEN),
            self._make_chunk(3, ChunkStatus.UEBERSPRUNGEN),
            self._make_chunk(4, ChunkStatus.AUSSTEHEND),
        ]
        job = self._make_job(chunks)
        assert job.abgeschlossene_chunks == 3

    def test_as_dict_contains_computed_properties(self):
        job = self._make_job()
        d = job.as_dict()
        for key in [
            "batch_id", "batch_name", "batch_typ", "tenant_id", "status",
            "gesamt_datensaetze", "chunk_groesse", "gesamt_chunks",
            "fortschritt_pct", "fehlerrate_pct", "verarbeitete_datensaetze",
        ]:
            assert key in d, f"Missing key: {key}"


class TestBerechneBatchStatus:
    def _make_job(self, chunks):
        return BatchJob(
            batch_id="BJ-S",
            batch_name="Status-Test",
            batch_typ=BatchTyp.VERARBEITUNG,
            tenant_id="TENANT-001",
            status=BatchStatus.AUSSTEHEND,
            gesamt_datensaetze=100,
            chunk_groesse=50,
            erstellt_am=datetime(2026, 3, 16, 8, 0, 0),
            chunks=chunks,
        )

    def _chunk(self, nr, status):
        return BatchChunk(
            chunk_id=f"BJ-S-CHK-{nr:03d}",
            batch_id="BJ-S",
            chunk_nummer=nr,
            anzahl_datensaetze=50,
            status=status,
        )

    def test_no_chunks_returns_ausstehend(self):
        job = self._make_job([])
        assert berechne_batch_status(job) == BatchStatus.AUSSTEHEND

    def test_any_laufend_returns_laufend(self):
        chunks = [
            self._chunk(1, ChunkStatus.ERFOLGREICH),
            self._chunk(2, ChunkStatus.LAUFEND),
        ]
        job = self._make_job(chunks)
        assert berechne_batch_status(job) == BatchStatus.LAUFEND

    def test_all_erfolgreich_returns_abgeschlossen(self):
        chunks = [self._chunk(i, ChunkStatus.ERFOLGREICH) for i in range(1, 3)]
        job = self._make_job(chunks)
        assert berechne_batch_status(job) == BatchStatus.ABGESCHLOSSEN

    def test_all_abgeschlossen_no_fehler_returns_abgeschlossen(self):
        chunks = [
            self._chunk(1, ChunkStatus.ERFOLGREICH),
            self._chunk(2, ChunkStatus.UEBERSPRUNGEN),
        ]
        job = self._make_job(chunks)
        assert berechne_batch_status(job) == BatchStatus.ABGESCHLOSSEN

    def test_all_fehlgeschlagen_returns_fehlgeschlagen(self):
        chunks = [self._chunk(i, ChunkStatus.FEHLGESCHLAGEN) for i in range(1, 3)]
        job = self._make_job(chunks)
        assert berechne_batch_status(job) == BatchStatus.FEHLGESCHLAGEN

    def test_mixed_returns_teilweise_erfolgreich(self):
        chunks = [
            self._chunk(1, ChunkStatus.ERFOLGREICH),
            self._chunk(2, ChunkStatus.FEHLGESCHLAGEN),
        ]
        job = self._make_job(chunks)
        assert berechne_batch_status(job) == BatchStatus.TEILWEISE_ERFOLGREICH

    def test_ausstehend_chunks_returns_ausstehend(self):
        chunks = [
            self._chunk(1, ChunkStatus.ERFOLGREICH),
            self._chunk(2, ChunkStatus.AUSSTEHEND),
        ]
        job = self._make_job(chunks)
        assert berechne_batch_status(job) == BatchStatus.AUSSTEHEND


class TestErstelle_Chunks:
    def test_empty_for_zero_records(self):
        result = erstelle_chunks("BJ-001", 0, 100)
        assert result == []

    def test_empty_for_negative_records(self):
        result = erstelle_chunks("BJ-001", -10, 100)
        assert result == []

    def test_empty_for_zero_chunk_groesse(self):
        result = erstelle_chunks("BJ-001", 100, 0)
        assert result == []

    def test_empty_for_negative_chunk_groesse(self):
        result = erstelle_chunks("BJ-001", 100, -50)
        assert result == []

    def test_correct_chunk_count_exact_multiple(self):
        result = erstelle_chunks("BJ-001", 300, 100)
        assert len(result) == 3

    def test_correct_chunk_count_non_multiple(self):
        result = erstelle_chunks("BJ-001", 350, 100)
        assert len(result) == 4

    def test_last_chunk_smaller_when_not_multiple(self):
        result = erstelle_chunks("BJ-001", 350, 100)
        assert result[-1].anzahl_datensaetze == 50

    def test_all_chunks_except_last_full_size(self):
        result = erstelle_chunks("BJ-001", 350, 100)
        for chunk in result[:-1]:
            assert chunk.anzahl_datensaetze == 100

    def test_all_chunks_ausstehend(self):
        result = erstelle_chunks("BJ-001", 300, 100)
        for chunk in result:
            assert chunk.status == ChunkStatus.AUSSTEHEND

    def test_chunk_id_format(self):
        result = erstelle_chunks("BJ-001", 300, 100)
        assert result[0].chunk_id == "BJ-001-CHK-001"
        assert result[1].chunk_id == "BJ-001-CHK-002"
        assert result[2].chunk_id == "BJ-001-CHK-003"

    def test_chunk_nummer_1_based(self):
        result = erstelle_chunks("BJ-001", 200, 100)
        assert result[0].chunk_nummer == 1
        assert result[1].chunk_nummer == 2

    def test_single_chunk_when_records_less_than_groesse(self):
        result = erstelle_chunks("BJ-001", 50, 100)
        assert len(result) == 1
        assert result[0].anzahl_datensaetze == 50

    def test_single_chunk_exact_match(self):
        result = erstelle_chunks("BJ-001", 100, 100)
        assert len(result) == 1
        assert result[0].anzahl_datensaetze == 100

    def test_batch_id_set_on_chunks(self):
        result = erstelle_chunks("BJ-XYZ", 200, 100)
        for chunk in result:
            assert chunk.batch_id == "BJ-XYZ"

    def test_large_batch_1500_records_250_chunk_groesse(self):
        result = erstelle_chunks("BJ-001", 1500, 250)
        assert len(result) == 6
        for chunk in result:
            assert chunk.anzahl_datensaetze == 250


class TestGetDefaultBatchJobs:
    def setup_method(self):
        self.jobs = get_default_batch_jobs()
        self.jobs_by_id = {j.batch_id: j for j in self.jobs}

    def test_returns_four_jobs(self):
        assert len(self.jobs) == 4

    def test_bj001_exists(self):
        assert "BJ-001" in self.jobs_by_id

    def test_bj002_exists(self):
        assert "BJ-002" in self.jobs_by_id

    def test_bj003_exists(self):
        assert "BJ-003" in self.jobs_by_id

    def test_bj004_exists(self):
        assert "BJ-004" in self.jobs_by_id

    def test_bj001_typ_import(self):
        assert self.jobs_by_id["BJ-001"].batch_typ == BatchTyp.IMPORT

    def test_bj001_status_abgeschlossen(self):
        assert self.jobs_by_id["BJ-001"].status == BatchStatus.ABGESCHLOSSEN

    def test_bj001_six_chunks(self):
        assert len(self.jobs_by_id["BJ-001"].chunks) == 6

    def test_bj001_all_chunks_erfolgreich(self):
        for chunk in self.jobs_by_id["BJ-001"].chunks:
            assert chunk.status == ChunkStatus.ERFOLGREICH

    def test_bj001_1500_records(self):
        assert self.jobs_by_id["BJ-001"].gesamt_datensaetze == 1500

    def test_bj002_typ_abrechnung(self):
        assert self.jobs_by_id["BJ-002"].batch_typ == BatchTyp.ABRECHNUNG

    def test_bj002_status_teilweise_erfolgreich(self):
        assert self.jobs_by_id["BJ-002"].status == BatchStatus.TEILWEISE_ERFOLGREICH

    def test_bj002_four_chunks(self):
        assert len(self.jobs_by_id["BJ-002"].chunks) == 4

    def test_bj002_chunk_mix(self):
        chunks = self.jobs_by_id["BJ-002"].chunks
        statuses = [c.status for c in chunks]
        assert statuses.count(ChunkStatus.ERFOLGREICH) == 2
        assert statuses.count(ChunkStatus.FEHLGESCHLAGEN) == 1
        assert statuses.count(ChunkStatus.UEBERSPRUNGEN) == 1

    def test_bj003_status_laufend(self):
        assert self.jobs_by_id["BJ-003"].status == BatchStatus.LAUFEND

    def test_bj003_ten_chunks(self):
        assert len(self.jobs_by_id["BJ-003"].chunks) == 10

    def test_bj003_chunk_mix(self):
        chunks = self.jobs_by_id["BJ-003"].chunks
        statuses = [c.status for c in chunks]
        assert statuses.count(ChunkStatus.ERFOLGREICH) == 1
        assert statuses.count(ChunkStatus.LAUFEND) == 1
        assert statuses.count(ChunkStatus.AUSSTEHEND) == 8

    def test_bj003_5000_records(self):
        assert self.jobs_by_id["BJ-003"].gesamt_datensaetze == 5000

    def test_bj004_typ_export(self):
        assert self.jobs_by_id["BJ-004"].batch_typ == BatchTyp.EXPORT

    def test_bj004_status_ausstehend(self):
        assert self.jobs_by_id["BJ-004"].status == BatchStatus.AUSSTEHEND

    def test_bj004_no_chunks(self):
        assert len(self.jobs_by_id["BJ-004"].chunks) == 0

    def test_bj004_300_records(self):
        assert self.jobs_by_id["BJ-004"].gesamt_datensaetze == 300

    def test_default_tenant_id(self):
        for job in self.jobs:
            assert job.tenant_id == "TENANT-001"

    def test_custom_tenant_id(self):
        jobs = get_default_batch_jobs(tenant_id="TENANT-999")
        for job in jobs:
            assert job.tenant_id == "TENANT-999"
