"""
Wave 59 Tests — Consent Management + Workflow Trigger Contracts
130+ tests covering:
  - Einwilligung.ist_aktiv() and aktueller_status()
  - EinwilligungsRegister operations
  - Default register at reference time 2026-03-16 10:00:00
  - TriggerBedingung.pruefe() for all operators
  - WorkflowTrigger.pruefe_bedingungen()
  - Default triggers behaviour
  - FastAPI endpoints via TestClient
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Reference datetime used throughout
JETZT = datetime(2026, 3, 16, 10, 0, 0)
PAST = JETZT - timedelta(days=1)
FUTURE = JETZT + timedelta(days=1)


# ---------------------------------------------------------------------------
# Import core modules
# ---------------------------------------------------------------------------
from app.core.process_consent_contracts import (
    EinwilligungsTyp, EinwilligungsStatus, RechtsgrundlageTyp,
    Einwilligung, VerarbeitungsProtokoll, EinwilligungsRegister,
    get_default_einwilligungs_register,
)
from app.core.workflow_trigger_contracts import (
    TriggerTyp, TriggerStatus, BedingungsOperator,
    TriggerBedingung, WorkflowTrigger,
    get_default_workflow_trigger,
)


# ===========================================================================
# CONSENT TESTS (65+)
# ===========================================================================

class TestEinwilligungsTyp:
    def test_alle_typen_vorhanden(self):
        typen = [t.value for t in EinwilligungsTyp]
        assert "DATENVERARBEITUNG" in typen
        assert "MARKETING" in typen
        assert "ANALYSE" in typen
        assert "DRITTANBIETER" in typen
        assert "NOTWENDIG" in typen

    def test_typ_ist_str(self):
        assert EinwilligungsTyp.MARKETING == "MARKETING"


class TestEinwilligungsStatus:
    def test_alle_status_vorhanden(self):
        stati = [s.value for s in EinwilligungsStatus]
        assert "ERTEILT" in stati
        assert "WIDERRUFEN" in stati
        assert "AUSSTEHEND" in stati
        assert "ABGELAUFEN" in stati


class TestRechtsgrundlageTyp:
    def test_alle_grundlagen_vorhanden(self):
        grundlagen = [g.value for g in RechtsgrundlageTyp]
        assert "EINWILLIGUNG" in grundlagen
        assert "VERTRAG" in grundlagen
        assert "RECHTLICHE_PFLICHT" in grundlagen
        assert "BERECHTIGTES_INTERESSE" in grundlagen


class TestEinwilligungIstAktiv:
    def _make(self, status, gueltig_bis=None):
        return Einwilligung(
            "EW-T", "SUBJ-T", "TEN-T",
            EinwilligungsTyp.DATENVERARBEITUNG,
            RechtsgrundlageTyp.EINWILLIGUNG,
            status=status,
            erteilt_am=JETZT - timedelta(days=1),
            gueltig_bis=gueltig_bis,
        )

    def test_erteilt_ohne_ablauf_ist_aktiv(self):
        e = self._make(EinwilligungsStatus.ERTEILT)
        assert e.ist_aktiv(JETZT) is True

    def test_erteilt_mit_zukunft_ablauf_ist_aktiv(self):
        e = self._make(EinwilligungsStatus.ERTEILT, gueltig_bis=FUTURE)
        assert e.ist_aktiv(JETZT) is True

    def test_erteilt_mit_vergangenem_ablauf_nicht_aktiv(self):
        e = self._make(EinwilligungsStatus.ERTEILT, gueltig_bis=PAST)
        assert e.ist_aktiv(JETZT) is False

    def test_erteilt_ablauf_exakt_jetzt_nicht_aktiv(self):
        e = self._make(EinwilligungsStatus.ERTEILT, gueltig_bis=JETZT)
        assert e.ist_aktiv(JETZT) is False

    def test_widerrufen_nicht_aktiv(self):
        e = self._make(EinwilligungsStatus.WIDERRUFEN)
        assert e.ist_aktiv(JETZT) is False

    def test_ausstehend_nicht_aktiv(self):
        e = self._make(EinwilligungsStatus.AUSSTEHEND)
        assert e.ist_aktiv(JETZT) is False

    def test_abgelaufen_status_nicht_aktiv(self):
        e = self._make(EinwilligungsStatus.ABGELAUFEN)
        assert e.ist_aktiv(JETZT) is False

    def test_notwendig_erteilt_aktiv(self):
        e = Einwilligung(
            "EW-N", "SUBJ", "TEN",
            EinwilligungsTyp.NOTWENDIG,
            RechtsgrundlageTyp.VERTRAG,
            status=EinwilligungsStatus.ERTEILT,
        )
        assert e.ist_aktiv(JETZT) is True

    def test_marketing_erteilt_aktiv(self):
        e = Einwilligung(
            "EW-M", "SUBJ", "TEN",
            EinwilligungsTyp.MARKETING,
            RechtsgrundlageTyp.EINWILLIGUNG,
            status=EinwilligungsStatus.ERTEILT,
        )
        assert e.ist_aktiv(JETZT) is True

    def test_ablauf_einen_tag_vor_jetzt(self):
        e = self._make(EinwilligungsStatus.ERTEILT, gueltig_bis=JETZT - timedelta(days=1))
        assert e.ist_aktiv(JETZT) is False

    def test_ablauf_einen_tag_nach_jetzt(self):
        e = self._make(EinwilligungsStatus.ERTEILT, gueltig_bis=JETZT + timedelta(days=1))
        assert e.ist_aktiv(JETZT) is True


class TestEinwilligungAktuellerStatus:
    def _make(self, status, gueltig_bis=None):
        return Einwilligung(
            "EW-T", "SUBJ-T", "TEN-T",
            EinwilligungsTyp.DATENVERARBEITUNG,
            RechtsgrundlageTyp.EINWILLIGUNG,
            status=status,
            gueltig_bis=gueltig_bis,
        )

    def test_erteilt_mit_abgelaufenem_ablauf_gibt_abgelaufen(self):
        e = self._make(EinwilligungsStatus.ERTEILT, gueltig_bis=PAST)
        assert e.aktueller_status(JETZT) == EinwilligungsStatus.ABGELAUFEN

    def test_erteilt_mit_zukunft_ablauf_gibt_erteilt(self):
        e = self._make(EinwilligungsStatus.ERTEILT, gueltig_bis=FUTURE)
        assert e.aktueller_status(JETZT) == EinwilligungsStatus.ERTEILT

    def test_erteilt_ohne_ablauf_gibt_erteilt(self):
        e = self._make(EinwilligungsStatus.ERTEILT)
        assert e.aktueller_status(JETZT) == EinwilligungsStatus.ERTEILT

    def test_widerrufen_gibt_widerrufen(self):
        e = self._make(EinwilligungsStatus.WIDERRUFEN)
        assert e.aktueller_status(JETZT) == EinwilligungsStatus.WIDERRUFEN

    def test_ausstehend_gibt_ausstehend(self):
        e = self._make(EinwilligungsStatus.AUSSTEHEND)
        assert e.aktueller_status(JETZT) == EinwilligungsStatus.AUSSTEHEND

    def test_abgelaufen_status_gibt_abgelaufen(self):
        e = self._make(EinwilligungsStatus.ABGELAUFEN)
        assert e.aktueller_status(JETZT) == EinwilligungsStatus.ABGELAUFEN

    def test_erteilt_ablauf_exakt_jetzt_gibt_abgelaufen(self):
        e = self._make(EinwilligungsStatus.ERTEILT, gueltig_bis=JETZT)
        assert e.aktueller_status(JETZT) == EinwilligungsStatus.ABGELAUFEN


class TestEinwilligungsRegister:
    def _register_mit(self, einwilligungen):
        r = EinwilligungsRegister("REG-T", "TENANT-T", einwilligungen)
        return r

    def _aktiv(self, eid, sid, typ):
        return Einwilligung(eid, sid, "TEN", typ, RechtsgrundlageTyp.EINWILLIGUNG,
                            EinwilligungsStatus.ERTEILT, JETZT - timedelta(days=1),
                            gueltig_bis=JETZT + timedelta(days=100))

    def _inaktiv(self, eid, sid, typ):
        return Einwilligung(eid, sid, "TEN", typ, RechtsgrundlageTyp.EINWILLIGUNG,
                            EinwilligungsStatus.WIDERRUFEN)

    def test_aktive_einwilligungen_leer_bei_keinen(self):
        r = self._register_mit([])
        assert r.aktive_einwilligungen(JETZT) == []

    def test_aktive_einwilligungen_filtert_korrekt(self):
        e1 = self._aktiv("E1", "S1", EinwilligungsTyp.MARKETING)
        e2 = self._inaktiv("E2", "S2", EinwilligungsTyp.MARKETING)
        r = self._register_mit([e1, e2])
        aktiv = r.aktive_einwilligungen(JETZT)
        assert len(aktiv) == 1
        assert aktiv[0].einwilligungs_id == "E1"

    def test_einwilligungen_nach_typ_korrekt(self):
        e1 = self._aktiv("E1", "S1", EinwilligungsTyp.MARKETING)
        e2 = self._aktiv("E2", "S2", EinwilligungsTyp.ANALYSE)
        e3 = self._inaktiv("E3", "S3", EinwilligungsTyp.MARKETING)
        r = self._register_mit([e1, e2, e3])
        marketing = r.einwilligungen_nach_typ(EinwilligungsTyp.MARKETING, JETZT)
        assert len(marketing) == 1
        assert marketing[0].einwilligungs_id == "E1"

    def test_einwilligungen_nach_typ_leer(self):
        e1 = self._aktiv("E1", "S1", EinwilligungsTyp.MARKETING)
        r = self._register_mit([e1])
        assert r.einwilligungen_nach_typ(EinwilligungsTyp.ANALYSE, JETZT) == []

    def test_hat_gueltige_einwilligung_true(self):
        e1 = self._aktiv("E1", "KUNDE-X", EinwilligungsTyp.DATENVERARBEITUNG)
        r = self._register_mit([e1])
        assert r.hat_gueltige_einwilligung("KUNDE-X", EinwilligungsTyp.DATENVERARBEITUNG, JETZT) is True

    def test_hat_gueltige_einwilligung_false_widerrufen(self):
        e1 = self._inaktiv("E1", "KUNDE-X", EinwilligungsTyp.DATENVERARBEITUNG)
        r = self._register_mit([e1])
        assert r.hat_gueltige_einwilligung("KUNDE-X", EinwilligungsTyp.DATENVERARBEITUNG, JETZT) is False

    def test_hat_gueltige_einwilligung_false_andere_subjekt(self):
        e1 = self._aktiv("E1", "KUNDE-X", EinwilligungsTyp.DATENVERARBEITUNG)
        r = self._register_mit([e1])
        assert r.hat_gueltige_einwilligung("KUNDE-Y", EinwilligungsTyp.DATENVERARBEITUNG, JETZT) is False

    def test_hat_gueltige_einwilligung_false_andere_typ(self):
        e1 = self._aktiv("E1", "KUNDE-X", EinwilligungsTyp.DATENVERARBEITUNG)
        r = self._register_mit([e1])
        assert r.hat_gueltige_einwilligung("KUNDE-X", EinwilligungsTyp.MARKETING, JETZT) is False


class TestDefaultEinwilligungsRegister:
    """Test the default register at reference time 2026-03-16 10:00:00"""

    def setup_method(self):
        self.register = get_default_einwilligungs_register()
        self.jetzt = JETZT

    def test_register_id(self):
        assert self.register.register_id == "ER-001"

    def test_tenant_id(self):
        assert self.register.tenant_id == "TENANT-A"

    def test_gesamt_einwilligungen_count(self):
        assert len(self.register.einwilligungen) == 5

    def test_aktive_einwilligungen_count(self):
        aktiv = self.register.aktive_einwilligungen(self.jetzt)
        assert len(aktiv) == 2

    def test_aktive_einwilligungen_sind_ew001_und_ew003(self):
        aktiv_ids = {e.einwilligungs_id for e in self.register.aktive_einwilligungen(self.jetzt)}
        assert "EW-001" in aktiv_ids
        assert "EW-003" in aktiv_ids

    # EW-001: ERTEILT, expires in 335 days from now → active
    def test_ew001_ist_aktiv(self):
        ew001 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-001")
        assert ew001.ist_aktiv(self.jetzt) is True

    def test_ew001_aktueller_status_ist_erteilt(self):
        ew001 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-001")
        assert ew001.aktueller_status(self.jetzt) == EinwilligungsStatus.ERTEILT

    def test_ew001_typ_ist_datenverarbeitung(self):
        ew001 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-001")
        assert ew001.typ == EinwilligungsTyp.DATENVERARBEITUNG

    # EW-002: WIDERRUFEN → not active
    def test_ew002_nicht_aktiv(self):
        ew002 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-002")
        assert ew002.ist_aktiv(self.jetzt) is False

    def test_ew002_aktueller_status_ist_widerrufen(self):
        ew002 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-002")
        assert ew002.aktueller_status(self.jetzt) == EinwilligungsStatus.WIDERRUFEN

    def test_ew002_typ_ist_marketing(self):
        ew002 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-002")
        assert ew002.typ == EinwilligungsTyp.MARKETING

    # EW-003: ERTEILT, no expiry → active
    def test_ew003_ist_aktiv(self):
        ew003 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-003")
        assert ew003.ist_aktiv(self.jetzt) is True

    def test_ew003_kein_ablauf(self):
        ew003 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-003")
        assert ew003.gueltig_bis is None

    def test_ew003_typ_ist_notwendig(self):
        ew003 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-003")
        assert ew003.typ == EinwilligungsTyp.NOTWENDIG

    # EW-004: ERTEILT but expired 35 days ago → not active, aktueller_status = ABGELAUFEN
    def test_ew004_nicht_aktiv(self):
        ew004 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-004")
        assert ew004.ist_aktiv(self.jetzt) is False

    def test_ew004_aktueller_status_ist_abgelaufen(self):
        ew004 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-004")
        assert ew004.aktueller_status(self.jetzt) == EinwilligungsStatus.ABGELAUFEN

    def test_ew004_status_war_erteilt(self):
        ew004 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-004")
        assert ew004.status == EinwilligungsStatus.ERTEILT

    # EW-005: AUSSTEHEND → not active
    def test_ew005_nicht_aktiv(self):
        ew005 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-005")
        assert ew005.ist_aktiv(self.jetzt) is False

    def test_ew005_aktueller_status_ist_ausstehend(self):
        ew005 = next(e for e in self.register.einwilligungen if e.einwilligungs_id == "EW-005")
        assert ew005.aktueller_status(self.jetzt) == EinwilligungsStatus.AUSSTEHEND

    # Subject-level checks
    def test_kunde001_hat_datenverarbeitung(self):
        assert self.register.hat_gueltige_einwilligung(
            "KUNDE-001", EinwilligungsTyp.DATENVERARBEITUNG, self.jetzt) is True

    def test_kunde001_hat_kein_marketing(self):
        assert self.register.hat_gueltige_einwilligung(
            "KUNDE-001", EinwilligungsTyp.MARKETING, self.jetzt) is False

    def test_kunde002_hat_notwendig(self):
        assert self.register.hat_gueltige_einwilligung(
            "KUNDE-002", EinwilligungsTyp.NOTWENDIG, self.jetzt) is True

    def test_kunde002_hat_keine_analyse(self):
        assert self.register.hat_gueltige_einwilligung(
            "KUNDE-002", EinwilligungsTyp.ANALYSE, self.jetzt) is False

    def test_kunde003_hat_keine_datenverarbeitung(self):
        # EW-005 is AUSSTEHEND
        assert self.register.hat_gueltige_einwilligung(
            "KUNDE-003", EinwilligungsTyp.DATENVERARBEITUNG, self.jetzt) is False

    def test_unbekannter_kunde_hat_keine_einwilligung(self):
        assert self.register.hat_gueltige_einwilligung(
            "KUNDE-999", EinwilligungsTyp.DATENVERARBEITUNG, self.jetzt) is False

    def test_datenverarbeitung_nach_typ_count(self):
        result = self.register.einwilligungen_nach_typ(EinwilligungsTyp.DATENVERARBEITUNG, self.jetzt)
        assert len(result) == 1  # only EW-001 (EW-005 is AUSSTEHEND)

    def test_notwendig_nach_typ_count(self):
        result = self.register.einwilligungen_nach_typ(EinwilligungsTyp.NOTWENDIG, self.jetzt)
        assert len(result) == 1  # EW-003

    def test_marketing_nach_typ_leer(self):
        result = self.register.einwilligungen_nach_typ(EinwilligungsTyp.MARKETING, self.jetzt)
        assert len(result) == 0  # EW-002 is WIDERRUFEN

    def test_analyse_nach_typ_leer(self):
        result = self.register.einwilligungen_nach_typ(EinwilligungsTyp.ANALYSE, self.jetzt)
        assert len(result) == 0  # EW-004 expired


class TestVerarbeitungsProtokoll:
    def test_erstellen(self):
        p = VerarbeitungsProtokoll(
            "VP-001", "EW-001", "Abrechnungsverarbeitung",
            JETZT, "settlement-service", ["name", "adresse"]
        )
        assert p.protokoll_id == "VP-001"
        assert p.einwilligungs_id == "EW-001"
        assert p.verarbeitet_von == "settlement-service"
        assert len(p.datenkategorien) == 2

    def test_default_datenkategorien_leer(self):
        p = VerarbeitungsProtokoll("VP-002", "EW-001", "test", JETZT, "sys")
        assert p.datenkategorien == []


# ===========================================================================
# TRIGGER TESTS (65+)
# ===========================================================================

class TestBedingungsOperatorEnum:
    def test_alle_operatoren_vorhanden(self):
        ops = [o.value for o in BedingungsOperator]
        assert "GLEICH" in ops
        assert "UNGLEICH" in ops
        assert "GROESSER" in ops
        assert "KLEINER" in ops
        assert "GROESSER_GLEICH" in ops
        assert "KLEINER_GLEICH" in ops
        assert "ENTHAELT" in ops


class TestTriggerBedingungGleich:
    def test_gleich_match(self):
        b = TriggerBedingung("status", BedingungsOperator.GLEICH, "AKTIV")
        assert b.pruefe({"status": "AKTIV"}) is True

    def test_gleich_no_match(self):
        b = TriggerBedingung("status", BedingungsOperator.GLEICH, "AKTIV")
        assert b.pruefe({"status": "INAKTIV"}) is False

    def test_gleich_int(self):
        b = TriggerBedingung("menge", BedingungsOperator.GLEICH, 100)
        assert b.pruefe({"menge": 100}) is True
        assert b.pruefe({"menge": 99}) is False

    def test_gleich_missing_field(self):
        b = TriggerBedingung("fehlend", BedingungsOperator.GLEICH, "x")
        assert b.pruefe({}) is False


class TestTriggerBedingungUngleich:
    def test_ungleich_match(self):
        b = TriggerBedingung("status", BedingungsOperator.UNGLEICH, "AKTIV")
        assert b.pruefe({"status": "INAKTIV"}) is True

    def test_ungleich_no_match(self):
        b = TriggerBedingung("status", BedingungsOperator.UNGLEICH, "AKTIV")
        assert b.pruefe({"status": "AKTIV"}) is False

    def test_ungleich_missing_field(self):
        b = TriggerBedingung("fehlend", BedingungsOperator.UNGLEICH, "x")
        assert b.pruefe({}) is False


class TestTriggerBedingungGroesser:
    def test_groesser_true(self):
        b = TriggerBedingung("menge", BedingungsOperator.GROESSER, 100)
        assert b.pruefe({"menge": 101}) is True

    def test_groesser_false_gleich(self):
        b = TriggerBedingung("menge", BedingungsOperator.GROESSER, 100)
        assert b.pruefe({"menge": 100}) is False

    def test_groesser_false_kleiner(self):
        b = TriggerBedingung("menge", BedingungsOperator.GROESSER, 100)
        assert b.pruefe({"menge": 99}) is False

    def test_groesser_float(self):
        b = TriggerBedingung("feuchte", BedingungsOperator.GROESSER, 15.0)
        assert b.pruefe({"feuchte": 15.1}) is True
        assert b.pruefe({"feuchte": 15.0}) is False

    def test_groesser_type_error_gibt_false(self):
        b = TriggerBedingung("wert", BedingungsOperator.GROESSER, 100)
        assert b.pruefe({"wert": "abc"}) is False


class TestTriggerBedingungKleiner:
    def test_kleiner_true(self):
        b = TriggerBedingung("menge", BedingungsOperator.KLEINER, 100)
        assert b.pruefe({"menge": 99}) is True

    def test_kleiner_false_gleich(self):
        b = TriggerBedingung("menge", BedingungsOperator.KLEINER, 100)
        assert b.pruefe({"menge": 100}) is False

    def test_kleiner_false_groesser(self):
        b = TriggerBedingung("menge", BedingungsOperator.KLEINER, 100)
        assert b.pruefe({"menge": 101}) is False

    def test_kleiner_missing_field(self):
        b = TriggerBedingung("x", BedingungsOperator.KLEINER, 10)
        assert b.pruefe({}) is False


class TestTriggerBedingungGroesserGleich:
    def test_groesser_gleich_groesser(self):
        b = TriggerBedingung("menge", BedingungsOperator.GROESSER_GLEICH, 100)
        assert b.pruefe({"menge": 101}) is True

    def test_groesser_gleich_gleich(self):
        b = TriggerBedingung("menge", BedingungsOperator.GROESSER_GLEICH, 100)
        assert b.pruefe({"menge": 100}) is True

    def test_groesser_gleich_kleiner(self):
        b = TriggerBedingung("menge", BedingungsOperator.GROESSER_GLEICH, 100)
        assert b.pruefe({"menge": 99}) is False


class TestTriggerBedingungKleinerGleich:
    def test_kleiner_gleich_kleiner(self):
        b = TriggerBedingung("menge", BedingungsOperator.KLEINER_GLEICH, 100)
        assert b.pruefe({"menge": 99}) is True

    def test_kleiner_gleich_gleich(self):
        b = TriggerBedingung("menge", BedingungsOperator.KLEINER_GLEICH, 100)
        assert b.pruefe({"menge": 100}) is True

    def test_kleiner_gleich_groesser(self):
        b = TriggerBedingung("menge", BedingungsOperator.KLEINER_GLEICH, 100)
        assert b.pruefe({"menge": 101}) is False


class TestTriggerBedingungEnthaelt:
    def test_enthaelt_string_in_string(self):
        b = TriggerBedingung("text", BedingungsOperator.ENTHAELT, "abc")
        assert b.pruefe({"text": "xabcy"}) is True

    def test_enthaelt_string_nicht_in_string(self):
        b = TriggerBedingung("text", BedingungsOperator.ENTHAELT, "xyz")
        assert b.pruefe({"text": "abcdef"}) is False

    def test_enthaelt_item_in_liste(self):
        b = TriggerBedingung("items", BedingungsOperator.ENTHAELT, "settlement")
        assert b.pruefe({"items": ["settlement", "archivierung"]}) is True

    def test_enthaelt_item_nicht_in_liste(self):
        b = TriggerBedingung("items", BedingungsOperator.ENTHAELT, "fehlend")
        assert b.pruefe({"items": ["settlement", "archivierung"]}) is False

    def test_enthaelt_missing_field(self):
        b = TriggerBedingung("fehlend", BedingungsOperator.ENTHAELT, "x")
        assert b.pruefe({}) is False


class TestWorkflowTriggerPruefeBedingungen:
    def test_inaktiv_gibt_false(self):
        t = WorkflowTrigger("T1", "test", TriggerTyp.MANUELL, [], TriggerStatus.INAKTIV)
        assert t.pruefe_bedingungen({}) is False

    def test_ausgeloest_gibt_false(self):
        t = WorkflowTrigger("T1", "test", TriggerTyp.MANUELL, [], TriggerStatus.AUSGELOEST)
        assert t.pruefe_bedingungen({}) is False

    def test_fehler_status_gibt_false(self):
        t = WorkflowTrigger("T1", "test", TriggerTyp.MANUELL, [], TriggerStatus.FEHLER)
        assert t.pruefe_bedingungen({}) is False

    def test_aktiv_ohne_bedingungen_gibt_true(self):
        t = WorkflowTrigger("T1", "test", TriggerTyp.ZEITPLAN, [], TriggerStatus.AKTIV)
        assert t.pruefe_bedingungen({}) is True

    def test_aktiv_alle_bedingungen_true(self):
        bedingungen = [
            TriggerBedingung("a", BedingungsOperator.GLEICH, 1),
            TriggerBedingung("b", BedingungsOperator.GROESSER, 0),
        ]
        t = WorkflowTrigger("T1", "test", TriggerTyp.SCHWELLWERT, bedingungen, TriggerStatus.AKTIV)
        assert t.pruefe_bedingungen({"a": 1, "b": 5}) is True

    def test_aktiv_eine_bedingung_false(self):
        bedingungen = [
            TriggerBedingung("a", BedingungsOperator.GLEICH, 1),
            TriggerBedingung("b", BedingungsOperator.GROESSER, 10),
        ]
        t = WorkflowTrigger("T1", "test", TriggerTyp.SCHWELLWERT, bedingungen, TriggerStatus.AKTIV)
        assert t.pruefe_bedingungen({"a": 1, "b": 5}) is False

    def test_aktiv_alle_bedingungen_false(self):
        bedingungen = [
            TriggerBedingung("a", BedingungsOperator.GLEICH, 99),
        ]
        t = WorkflowTrigger("T1", "test", TriggerTyp.EREIGNIS, bedingungen, TriggerStatus.AKTIV)
        assert t.pruefe_bedingungen({"a": 1}) is False


class TestDefaultWorkflowTrigger:
    def setup_method(self):
        self.trigger_list = get_default_workflow_trigger()
        self.trigger_map = {t.trigger_id: t for t in self.trigger_list}

    def test_fuenf_trigger(self):
        assert len(self.trigger_list) == 5

    def test_alle_trigger_ids_vorhanden(self):
        ids = [t.trigger_id for t in self.trigger_list]
        assert "WT-001" in ids
        assert "WT-002" in ids
        assert "WT-003" in ids
        assert "WT-004" in ids
        assert "WT-005" in ids

    # WT-001: kontrakt_freigabe, SCHWELLWERT, 2 Bedingungen
    def test_wt001_typ(self):
        assert self.trigger_map["WT-001"].trigger_typ == TriggerTyp.SCHWELLWERT

    def test_wt001_workflow_typ(self):
        assert self.trigger_map["WT-001"].workflow_typ == "kontrakt_freigabe"

    def test_wt001_bedingungen_count(self):
        assert len(self.trigger_map["WT-001"].bedingungen) == 2

    def test_wt001_erfuellt_bei_100t_geprueft(self):
        t = self.trigger_map["WT-001"]
        assert t.pruefe_bedingungen({"menge_tonnen": 100, "status": "GEPRUEFT"}) is True

    def test_wt001_erfuellt_bei_150t_geprueft(self):
        t = self.trigger_map["WT-001"]
        assert t.pruefe_bedingungen({"menge_tonnen": 150, "status": "GEPRUEFT"}) is True

    def test_wt001_nicht_erfuellt_bei_99t(self):
        t = self.trigger_map["WT-001"]
        assert t.pruefe_bedingungen({"menge_tonnen": 99, "status": "GEPRUEFT"}) is False

    def test_wt001_nicht_erfuellt_bei_falsem_status(self):
        t = self.trigger_map["WT-001"]
        assert t.pruefe_bedingungen({"menge_tonnen": 100, "status": "NEU"}) is False

    # WT-002: settlement_automatisch, EREIGNIS
    def test_wt002_typ(self):
        assert self.trigger_map["WT-002"].trigger_typ == TriggerTyp.EREIGNIS

    def test_wt002_erfuellt_bei_waage_abgeschlossen(self):
        t = self.trigger_map["WT-002"]
        assert t.pruefe_bedingungen({"ereignis_typ": "WAAGE_ABGESCHLOSSEN"}) is True

    def test_wt002_nicht_erfuellt_bei_anderem_ereignis(self):
        t = self.trigger_map["WT-002"]
        assert t.pruefe_bedingungen({"ereignis_typ": "WAAGE_GESTARTET"}) is False

    # WT-003: mahnlauf, ZEITPLAN, keine Bedingungen
    def test_wt003_typ(self):
        assert self.trigger_map["WT-003"].trigger_typ == TriggerTyp.ZEITPLAN

    def test_wt003_keine_bedingungen(self):
        assert len(self.trigger_map["WT-003"].bedingungen) == 0

    def test_wt003_immer_true_bei_aktiv(self):
        t = self.trigger_map["WT-003"]
        assert t.pruefe_bedingungen({}) is True
        assert t.pruefe_bedingungen({"irgendwas": "egal"}) is True

    # WT-004: archivierung, ABHAENGIGKEIT, INAKTIV
    def test_wt004_status_inaktiv(self):
        assert self.trigger_map["WT-004"].status == TriggerStatus.INAKTIV

    def test_wt004_immer_false(self):
        t = self.trigger_map["WT-004"]
        assert t.pruefe_bedingungen({"abgeschlossen_workflows": ["settlement"]}) is False
        assert t.pruefe_bedingungen({}) is False

    def test_wt004_typ(self):
        assert self.trigger_map["WT-004"].trigger_typ == TriggerTyp.ABHAENGIGKEIT

    # WT-005: qualitaets_eskalation, SCHWELLWERT, feuchte > 15
    def test_wt005_erfuellt_bei_feuchte_15_1(self):
        t = self.trigger_map["WT-005"]
        assert t.pruefe_bedingungen({"feuchte_pct": 15.1}) is True

    def test_wt005_nicht_erfuellt_bei_feuchte_15_0(self):
        t = self.trigger_map["WT-005"]
        assert t.pruefe_bedingungen({"feuchte_pct": 15.0}) is False

    def test_wt005_nicht_erfuellt_bei_feuchte_14_9(self):
        t = self.trigger_map["WT-005"]
        assert t.pruefe_bedingungen({"feuchte_pct": 14.9}) is False

    def test_wt005_typ(self):
        assert self.trigger_map["WT-005"].trigger_typ == TriggerTyp.SCHWELLWERT

    def test_wt005_status_aktiv(self):
        assert self.trigger_map["WT-005"].status == TriggerStatus.AKTIV


# ===========================================================================
# FastAPI Endpoint Tests
# ===========================================================================

@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app, raise_server_exceptions=True)


BASE_URL = "/api/v1/process"


class TestConsentRegisterEndpoint:
    def test_get_consent_register_200(self, client):
        r = client.get(f"{BASE_URL}/consent/register")
        assert r.status_code == 200

    def test_get_consent_register_fields(self, client):
        r = client.get(f"{BASE_URL}/consent/register")
        data = r.json()
        assert "register_id" in data
        assert "tenant_id" in data
        assert "gesamt_einwilligungen" in data
        assert "aktive_einwilligungen" in data
        assert "einwilligungen" in data

    def test_get_consent_register_gesamt(self, client):
        r = client.get(f"{BASE_URL}/consent/register")
        data = r.json()
        assert data["gesamt_einwilligungen"] == 5

    def test_get_consent_register_aktiv_count(self, client):
        r = client.get(f"{BASE_URL}/consent/register")
        data = r.json()
        assert data["aktive_einwilligungen"] == 2

    def test_get_consent_register_einwilligungen_list(self, client):
        r = client.get(f"{BASE_URL}/consent/register")
        einwilligungen = r.json()["einwilligungen"]
        assert len(einwilligungen) == 5

    def test_get_consent_register_einwilligung_fields(self, client):
        r = client.get(f"{BASE_URL}/consent/register")
        first = r.json()["einwilligungen"][0]
        assert "einwilligungs_id" in first
        assert "subjekt_id" in first
        assert "typ" in first
        assert "status" in first
        assert "aktueller_status" in first
        assert "ist_aktiv" in first


class TestConsentPruefeEndpoint:
    def test_pruefe_datenverarbeitung_kunde001_true(self, client):
        r = client.post(f"{BASE_URL}/consent/pruefe",
                        json={"subjekt_id": "KUNDE-001", "typ": "DATENVERARBEITUNG"})
        assert r.status_code == 200
        assert r.json()["hat_gueltige_einwilligung"] is True

    def test_pruefe_marketing_kunde001_false(self, client):
        r = client.post(f"{BASE_URL}/consent/pruefe",
                        json={"subjekt_id": "KUNDE-001", "typ": "MARKETING"})
        assert r.status_code == 200
        assert r.json()["hat_gueltige_einwilligung"] is False

    def test_pruefe_notwendig_kunde002_true(self, client):
        r = client.post(f"{BASE_URL}/consent/pruefe",
                        json={"subjekt_id": "KUNDE-002", "typ": "NOTWENDIG"})
        assert r.status_code == 200
        assert r.json()["hat_gueltige_einwilligung"] is True

    def test_pruefe_analyse_kunde002_false(self, client):
        r = client.post(f"{BASE_URL}/consent/pruefe",
                        json={"subjekt_id": "KUNDE-002", "typ": "ANALYSE"})
        assert r.status_code == 200
        assert r.json()["hat_gueltige_einwilligung"] is False

    def test_pruefe_response_fields(self, client):
        r = client.post(f"{BASE_URL}/consent/pruefe",
                        json={"subjekt_id": "KUNDE-001", "typ": "DATENVERARBEITUNG"})
        data = r.json()
        assert "subjekt_id" in data
        assert "typ" in data
        assert "hat_gueltige_einwilligung" in data


class TestTriggerRegelnEndpoint:
    def test_get_trigger_regeln_200(self, client):
        r = client.get(f"{BASE_URL}/trigger/regeln")
        assert r.status_code == 200

    def test_get_trigger_regeln_count(self, client):
        r = client.get(f"{BASE_URL}/trigger/regeln")
        assert len(r.json()) == 5

    def test_get_trigger_regeln_fields(self, client):
        r = client.get(f"{BASE_URL}/trigger/regeln")
        first = r.json()[0]
        assert "trigger_id" in first
        assert "workflow_typ" in first
        assert "trigger_typ" in first
        assert "status" in first
        assert "bedingungen_anzahl" in first
        assert "beschreibung" in first

    def test_get_trigger_regeln_wt001_bedingungen(self, client):
        r = client.get(f"{BASE_URL}/trigger/regeln")
        wt001 = next(t for t in r.json() if t["trigger_id"] == "WT-001")
        assert wt001["bedingungen_anzahl"] == 2

    def test_get_trigger_regeln_wt003_keine_bedingungen(self, client):
        r = client.get(f"{BASE_URL}/trigger/regeln")
        wt003 = next(t for t in r.json() if t["trigger_id"] == "WT-003")
        assert wt003["bedingungen_anzahl"] == 0

    def test_get_trigger_regeln_wt004_inaktiv(self, client):
        r = client.get(f"{BASE_URL}/trigger/regeln")
        wt004 = next(t for t in r.json() if t["trigger_id"] == "WT-004")
        assert wt004["status"] == "INAKTIV"


class TestTriggerPruefeBedingungen:
    def test_pruefe_wt001_erfuellt(self, client):
        r = client.post(f"{BASE_URL}/trigger/pruefe-bedingungen",
                        json={"trigger_id": "WT-001",
                              "kontext": {"menge_tonnen": 100, "status": "GEPRUEFT"}})
        assert r.status_code == 200
        assert r.json()["bedingungen_erfuellt"] is True

    def test_pruefe_wt001_nicht_erfuellt(self, client):
        r = client.post(f"{BASE_URL}/trigger/pruefe-bedingungen",
                        json={"trigger_id": "WT-001",
                              "kontext": {"menge_tonnen": 99, "status": "GEPRUEFT"}})
        assert r.status_code == 200
        assert r.json()["bedingungen_erfuellt"] is False

    def test_pruefe_wt003_immer_true(self, client):
        r = client.post(f"{BASE_URL}/trigger/pruefe-bedingungen",
                        json={"trigger_id": "WT-003", "kontext": {}})
        assert r.status_code == 200
        assert r.json()["bedingungen_erfuellt"] is True

    def test_pruefe_wt004_inaktiv_false(self, client):
        r = client.post(f"{BASE_URL}/trigger/pruefe-bedingungen",
                        json={"trigger_id": "WT-004",
                              "kontext": {"abgeschlossen_workflows": ["settlement"]}})
        assert r.status_code == 200
        assert r.json()["bedingungen_erfuellt"] is False

    def test_pruefe_unbekannter_trigger(self, client):
        r = client.post(f"{BASE_URL}/trigger/pruefe-bedingungen",
                        json={"trigger_id": "WT-999", "kontext": {}})
        assert r.status_code == 200
        assert "fehler" in r.json()

    def test_pruefe_response_fields(self, client):
        r = client.post(f"{BASE_URL}/trigger/pruefe-bedingungen",
                        json={"trigger_id": "WT-002",
                              "kontext": {"ereignis_typ": "WAAGE_ABGESCHLOSSEN"}})
        data = r.json()
        assert "trigger_id" in data
        assert "bedingungen_erfuellt" in data
        assert "status" in data
