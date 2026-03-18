"""Wave 62: Process Templates + Workflow Deadline Contracts — 130+ tests."""
import pytest
from datetime import datetime, timedelta

from app.core.process_template_contracts import (
    TemplateTyp, TemplateStatus, InstanzierungsStatus,
    ProzessSchritt_Template, ProzessTemplate, InstanzierungsErgebnis,
    instanziere_template, get_default_templates,
)
from app.core.workflow_deadline_contracts import (
    DeadlineTyp, DeadlineStatus, EskalationsStufe,
    WorkflowDeadline, DeadlineMonitor,
    get_default_deadline_monitor,
)

# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

NOW = datetime(2026, 3, 16, 10, 0, 0)


def make_aktiv_template(pflicht_parameter=None):
    t = ProzessTemplate(
        "PT-TEST", "Test", "test_workflow",
        TemplateTyp.STANDARD, TemplateStatus.AKTIV, "1.0.0",
        pflicht_parameter=pflicht_parameter or [],
    )
    return t


def make_deadline(status=DeadlineStatus.AUSSTEHEND, offset_minutes=0):
    """offset_minutes > 0 = future; < 0 = past."""
    faellig = NOW + timedelta(minutes=offset_minutes)
    return WorkflowDeadline(
        "DL-X", "WI-X", DeadlineTyp.SLA, faellig,
        status, None, NOW, None, "user-x",
    )


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

def test_template_typ_values():
    assert TemplateTyp.STANDARD == "STANDARD"
    assert TemplateTyp.SAISONAL == "SAISONAL"
    assert TemplateTyp.TENANT_SPEZIFISCH == "TENANT_SPEZIFISCH"
    assert TemplateTyp.REGULATORISCH == "REGULATORISCH"


def test_template_status_values():
    assert TemplateStatus.ENTWURF == "ENTWURF"
    assert TemplateStatus.AKTIV == "AKTIV"
    assert TemplateStatus.ARCHIVIERT == "ARCHIVIERT"
    assert TemplateStatus.VERALTET == "VERALTET"


def test_instanzierungs_status_values():
    assert InstanzierungsStatus.ERFOLGREICH == "ERFOLGREICH"
    assert InstanzierungsStatus.FEHLGESCHLAGEN == "FEHLGESCHLAGEN"
    assert InstanzierungsStatus.VALIDIERUNGSFEHLER == "VALIDIERUNGSFEHLER"


def test_deadline_typ_values():
    assert DeadlineTyp.HART == "HART"
    assert DeadlineTyp.WEICH == "WEICH"
    assert DeadlineTyp.GESETZLICH == "GESETZLICH"
    assert DeadlineTyp.SLA == "SLA"


def test_deadline_status_values():
    assert DeadlineStatus.AUSSTEHEND == "AUSSTEHEND"
    assert DeadlineStatus.ERFUELLT == "ERFUELLT"
    assert DeadlineStatus.VERLETZT == "VERLETZT"
    assert DeadlineStatus.ESKALIERT == "ESKALIERT"


def test_eskalations_stufe_values():
    assert EskalationsStufe.STUFE_1 == "STUFE_1"
    assert EskalationsStufe.STUFE_2 == "STUFE_2"
    assert EskalationsStufe.STUFE_3 == "STUFE_3"
    assert EskalationsStufe.KRITISCH == "KRITISCH"


# ─────────────────────────────────────────────
# ProzessSchritt_Template
# ─────────────────────────────────────────────

def test_schritt_defaults():
    s = ProzessSchritt_Template("S1", "Erfassen")
    assert s.pflicht is True
    assert s.reihenfolge == 0
    assert s.standarddauer_minuten == 0


def test_schritt_custom_values():
    s = ProzessSchritt_Template("S2", "Validieren", False, 3, 45)
    assert s.schritt_id == "S2"
    assert s.name == "Validieren"
    assert s.pflicht is False
    assert s.reihenfolge == 3
    assert s.standarddauer_minuten == 45


# ─────────────────────────────────────────────
# ProzessTemplate.ist_verwendbar
# ─────────────────────────────────────────────

def test_ist_verwendbar_aktiv():
    t = ProzessTemplate("T1", "X", "w", TemplateTyp.STANDARD, TemplateStatus.AKTIV)
    assert t.ist_verwendbar() is True


def test_ist_verwendbar_entwurf():
    t = ProzessTemplate("T1", "X", "w", TemplateTyp.STANDARD, TemplateStatus.ENTWURF)
    assert t.ist_verwendbar() is False


def test_ist_verwendbar_archiviert():
    t = ProzessTemplate("T1", "X", "w", TemplateTyp.STANDARD, TemplateStatus.ARCHIVIERT)
    assert t.ist_verwendbar() is False


def test_ist_verwendbar_veraltet():
    t = ProzessTemplate("T1", "X", "w", TemplateTyp.STANDARD, TemplateStatus.VERALTET)
    assert t.ist_verwendbar() is False


# ─────────────────────────────────────────────
# ProzessTemplate.pflicht_schritte
# ─────────────────────────────────────────────

def test_pflicht_schritte_all_pflicht():
    t = make_aktiv_template()
    t.schritte = [
        ProzessSchritt_Template("S1", "A", True, 1, 10),
        ProzessSchritt_Template("S2", "B", True, 2, 20),
    ]
    result = t.pflicht_schritte()
    assert len(result) == 2


def test_pflicht_schritte_filters_optional():
    t = make_aktiv_template()
    t.schritte = [
        ProzessSchritt_Template("S1", "A", True, 1, 10),
        ProzessSchritt_Template("S2", "B", False, 2, 20),
        ProzessSchritt_Template("S3", "C", True, 3, 5),
    ]
    result = t.pflicht_schritte()
    assert len(result) == 2
    assert all(s.pflicht for s in result)


def test_pflicht_schritte_sorted_by_reihenfolge():
    t = make_aktiv_template()
    t.schritte = [
        ProzessSchritt_Template("S3", "C", True, 3, 5),
        ProzessSchritt_Template("S1", "A", True, 1, 10),
        ProzessSchritt_Template("S2", "B", True, 2, 20),
    ]
    result = t.pflicht_schritte()
    assert [s.reihenfolge for s in result] == [1, 2, 3]


def test_pflicht_schritte_empty_if_all_optional():
    t = make_aktiv_template()
    t.schritte = [
        ProzessSchritt_Template("S1", "A", False, 1, 10),
        ProzessSchritt_Template("S2", "B", False, 2, 20),
    ]
    assert t.pflicht_schritte() == []


def test_pflicht_schritte_empty_template():
    t = make_aktiv_template()
    assert t.pflicht_schritte() == []


# ─────────────────────────────────────────────
# ProzessTemplate.geschaetzte_gesamtdauer_minuten
# ─────────────────────────────────────────────

def test_gesamtdauer_only_pflicht():
    t = make_aktiv_template()
    t.schritte = [
        ProzessSchritt_Template("S1", "A", True, 1, 15),
        ProzessSchritt_Template("S2", "B", False, 2, 30),  # optional — excluded
        ProzessSchritt_Template("S3", "C", True, 3, 10),
    ]
    assert t.geschaetzte_gesamtdauer_minuten() == 25


def test_gesamtdauer_all_pflicht():
    t = make_aktiv_template()
    t.schritte = [
        ProzessSchritt_Template("S1", "A", True, 1, 20),
        ProzessSchritt_Template("S2", "B", True, 2, 30),
    ]
    assert t.geschaetzte_gesamtdauer_minuten() == 50


def test_gesamtdauer_empty():
    t = make_aktiv_template()
    assert t.geschaetzte_gesamtdauer_minuten() == 0


def test_gesamtdauer_all_optional():
    t = make_aktiv_template()
    t.schritte = [
        ProzessSchritt_Template("S1", "A", False, 1, 100),
    ]
    assert t.geschaetzte_gesamtdauer_minuten() == 0


# ─────────────────────────────────────────────
# instanziere_template — core logic
# ─────────────────────────────────────────────

def test_instanziere_nicht_aktiv_fehlgeschlagen():
    t = ProzessTemplate("T1", "X", "w", TemplateTyp.STANDARD, TemplateStatus.ENTWURF)
    ergebnis = instanziere_template(t, {}, "WI-001")
    assert ergebnis.status == InstanzierungsStatus.FEHLGESCHLAGEN
    assert "nicht aktiv" in ergebnis.fehler_nachricht


def test_instanziere_veraltet_fehlgeschlagen():
    t = ProzessTemplate("T1", "X", "w", TemplateTyp.STANDARD, TemplateStatus.VERALTET)
    ergebnis = instanziere_template(t, {}, "WI-001")
    assert ergebnis.status == InstanzierungsStatus.FEHLGESCHLAGEN


def test_instanziere_archiviert_fehlgeschlagen():
    t = ProzessTemplate("T1", "X", "w", TemplateTyp.STANDARD, TemplateStatus.ARCHIVIERT)
    ergebnis = instanziere_template(t, {}, "WI-001")
    assert ergebnis.status == InstanzierungsStatus.FEHLGESCHLAGEN


def test_instanziere_fehler_nachricht_template_nicht_aktiv():
    t = ProzessTemplate("T1", "X", "w", TemplateTyp.STANDARD, TemplateStatus.ENTWURF)
    ergebnis = instanziere_template(t, {}, "WI-001")
    assert ergebnis.fehler_nachricht == "Template nicht aktiv"


def test_instanziere_missing_one_param_validierungsfehler():
    t = make_aktiv_template(["param_a", "param_b"])
    ergebnis = instanziere_template(t, {"param_a": "x"}, "WI-001")
    assert ergebnis.status == InstanzierungsStatus.VALIDIERUNGSFEHLER
    assert "param_b" in ergebnis.fehlende_parameter


def test_instanziere_missing_all_params():
    t = make_aktiv_template(["p1", "p2", "p3"])
    ergebnis = instanziere_template(t, {}, "WI-001")
    assert ergebnis.status == InstanzierungsStatus.VALIDIERUNGSFEHLER
    assert set(ergebnis.fehlende_parameter) == {"p1", "p2", "p3"}


def test_instanziere_missing_multiple_params():
    t = make_aktiv_template(["p1", "p2", "p3"])
    ergebnis = instanziere_template(t, {"p1": 1}, "WI-001")
    assert ergebnis.status == InstanzierungsStatus.VALIDIERUNGSFEHLER
    assert "p2" in ergebnis.fehlende_parameter
    assert "p3" in ergebnis.fehlende_parameter


def test_instanziere_all_params_present_erfolgreich():
    t = make_aktiv_template(["p1", "p2"])
    ergebnis = instanziere_template(t, {"p1": "a", "p2": "b"}, "WI-001")
    assert ergebnis.status == InstanzierungsStatus.ERFOLGREICH
    assert ergebnis.workflow_instanz_id == "WI-001"


def test_instanziere_no_params_required_erfolgreich():
    t = make_aktiv_template([])
    ergebnis = instanziere_template(t, {}, "WI-NEW-042")
    assert ergebnis.status == InstanzierungsStatus.ERFOLGREICH
    assert ergebnis.workflow_instanz_id == "WI-NEW-042"


def test_instanziere_extra_params_erfolgreich():
    t = make_aktiv_template(["p1"])
    ergebnis = instanziere_template(t, {"p1": "x", "extra": "y"}, "WI-001")
    assert ergebnis.status == InstanzierungsStatus.ERFOLGREICH


def test_instanziere_sets_template_id():
    t = make_aktiv_template()
    t.template_id = "PT-XYZ"
    ergebnis = instanziere_template(t, {}, "WI-001")
    assert ergebnis.template_id == "PT-XYZ"


def test_instanziere_no_fehler_on_success():
    t = make_aktiv_template(["p1"])
    ergebnis = instanziere_template(t, {"p1": "v"}, "WI-001")
    assert ergebnis.fehler_nachricht == ""
    assert ergebnis.fehlende_parameter == []


def test_instanziere_no_instanz_id_on_failure():
    t = ProzessTemplate("T1", "X", "w", TemplateTyp.STANDARD, TemplateStatus.ENTWURF)
    ergebnis = instanziere_template(t, {}, "WI-001")
    assert ergebnis.workflow_instanz_id is None


# ─────────────────────────────────────────────
# Default Templates — PT-001
# ─────────────────────────────────────────────

def test_default_templates_count():
    templates = get_default_templates()
    assert len(templates) == 3


def test_pt001_exists():
    templates = {t.template_id: t for t in get_default_templates()}
    assert "PT-001" in templates


def test_pt001_status_aktiv():
    templates = {t.template_id: t for t in get_default_templates()}
    assert templates["PT-001"].status == TemplateStatus.AKTIV


def test_pt001_ist_verwendbar():
    templates = {t.template_id: t for t in get_default_templates()}
    assert templates["PT-001"].ist_verwendbar() is True


def test_pt001_version():
    templates = {t.template_id: t for t in get_default_templates()}
    assert templates["PT-001"].version == "2.1.0"


def test_pt001_workflow_typ():
    templates = {t.template_id: t for t in get_default_templates()}
    assert templates["PT-001"].workflow_typ == "kontrakt_freigabe"


def test_pt001_pflicht_schritte_count():
    """PT-001 has 5 steps; S4 Dokumentieren is optional → 4 pflicht."""
    templates = {t.template_id: t for t in get_default_templates()}
    ps = templates["PT-001"].pflicht_schritte()
    assert len(ps) == 4


def test_pt001_s4_not_pflicht():
    templates = {t.template_id: t for t in get_default_templates()}
    t = templates["PT-001"]
    s4 = next(s for s in t.schritte if s.schritt_id == "S4")
    assert s4.pflicht is False


def test_pt001_gesamtdauer():
    """PT-001: S1=15 + S2=10 + S3=30 + S5=5 = 60 min (S4 excluded)."""
    templates = {t.template_id: t for t in get_default_templates()}
    assert templates["PT-001"].geschaetzte_gesamtdauer_minuten() == 60


def test_pt001_pflicht_parameter():
    templates = {t.template_id: t for t in get_default_templates()}
    pp = templates["PT-001"].pflicht_parameter
    assert "lieferant_id" in pp
    assert "menge_tonnen" in pp
    assert "preis_eur_t" in pp


def test_pt001_instanziere_all_params():
    templates = {t.template_id: t for t in get_default_templates()}
    ergebnis = instanziere_template(
        templates["PT-001"],
        {"lieferant_id": "L1", "menge_tonnen": 100, "preis_eur_t": 250.0},
        "WI-K-001",
    )
    assert ergebnis.status == InstanzierungsStatus.ERFOLGREICH
    assert ergebnis.workflow_instanz_id == "WI-K-001"


def test_pt001_instanziere_missing_preis():
    templates = {t.template_id: t for t in get_default_templates()}
    ergebnis = instanziere_template(
        templates["PT-001"],
        {"lieferant_id": "L1", "menge_tonnen": 100},
        "WI-K-002",
    )
    assert ergebnis.status == InstanzierungsStatus.VALIDIERUNGSFEHLER
    assert "preis_eur_t" in ergebnis.fehlende_parameter


def test_pt001_pflicht_schritte_sorted():
    templates = {t.template_id: t for t in get_default_templates()}
    ps = templates["PT-001"].pflicht_schritte()
    reihenfol = [s.reihenfolge for s in ps]
    assert reihenfol == sorted(reihenfol)


# ─────────────────────────────────────────────
# Default Templates — PT-002
# ─────────────────────────────────────────────

def test_pt002_exists():
    templates = {t.template_id: t for t in get_default_templates()}
    assert "PT-002" in templates


def test_pt002_status_aktiv():
    templates = {t.template_id: t for t in get_default_templates()}
    assert templates["PT-002"].status == TemplateStatus.AKTIV


def test_pt002_ist_verwendbar():
    templates = {t.template_id: t for t in get_default_templates()}
    assert templates["PT-002"].ist_verwendbar() is True


def test_pt002_pflicht_schritte_count():
    """PT-002: S3 Benachrichtigen is optional → 2 pflicht."""
    templates = {t.template_id: t for t in get_default_templates()}
    assert len(templates["PT-002"].pflicht_schritte()) == 2


def test_pt002_gesamtdauer():
    """PT-002: S1=20 + S2=10 = 30 min."""
    templates = {t.template_id: t for t in get_default_templates()}
    assert templates["PT-002"].geschaetzte_gesamtdauer_minuten() == 30


def test_pt002_s3_not_pflicht():
    templates = {t.template_id: t for t in get_default_templates()}
    t = templates["PT-002"]
    s3 = next(s for s in t.schritte if s.schritt_id == "S3")
    assert s3.pflicht is False


def test_pt002_pflicht_parameter():
    templates = {t.template_id: t for t in get_default_templates()}
    pp = templates["PT-002"].pflicht_parameter
    assert "kontrakt_id" in pp
    assert "menge_ist" in pp


def test_pt002_instanziere_erfolgreich():
    templates = {t.template_id: t for t in get_default_templates()}
    ergebnis = instanziere_template(
        templates["PT-002"],
        {"kontrakt_id": "K-99", "menge_ist": 50.0},
        "WI-S-001",
    )
    assert ergebnis.status == InstanzierungsStatus.ERFOLGREICH


def test_pt002_instanziere_missing_menge():
    templates = {t.template_id: t for t in get_default_templates()}
    ergebnis = instanziere_template(
        templates["PT-002"],
        {"kontrakt_id": "K-99"},
        "WI-S-002",
    )
    assert ergebnis.status == InstanzierungsStatus.VALIDIERUNGSFEHLER
    assert "menge_ist" in ergebnis.fehlende_parameter


# ─────────────────────────────────────────────
# Default Templates — PT-003
# ─────────────────────────────────────────────

def test_pt003_exists():
    templates = {t.template_id: t for t in get_default_templates()}
    assert "PT-003" in templates


def test_pt003_status_veraltet():
    templates = {t.template_id: t for t in get_default_templates()}
    assert templates["PT-003"].status == TemplateStatus.VERALTET


def test_pt003_nicht_verwendbar():
    templates = {t.template_id: t for t in get_default_templates()}
    assert templates["PT-003"].ist_verwendbar() is False


def test_pt003_instanziere_fehlgeschlagen():
    templates = {t.template_id: t for t in get_default_templates()}
    ergebnis = instanziere_template(templates["PT-003"], {}, "WI-001")
    assert ergebnis.status == InstanzierungsStatus.FEHLGESCHLAGEN


# ─────────────────────────────────────────────
# InstanzierungsErgebnis dataclass
# ─────────────────────────────────────────────

def test_ergebnis_defaults():
    e = InstanzierungsErgebnis("PT-X", InstanzierungsStatus.ERFOLGREICH)
    assert e.workflow_instanz_id is None
    assert e.fehler_nachricht == ""
    assert e.fehlende_parameter == []


def test_ergebnis_with_values():
    e = InstanzierungsErgebnis("PT-X", InstanzierungsStatus.VALIDIERUNGSFEHLER,
                                fehlende_parameter=["p1", "p2"])
    assert len(e.fehlende_parameter) == 2


# ─────────────────────────────────────────────
# WorkflowDeadline — verbleibende_minuten
# ─────────────────────────────────────────────

def test_verbleibende_minuten_future():
    dl = make_deadline(offset_minutes=120)
    assert dl.verbleibende_minuten(NOW) == pytest.approx(120.0)


def test_verbleibende_minuten_past():
    dl = make_deadline(offset_minutes=-60)
    assert dl.verbleibende_minuten(NOW) == pytest.approx(-60.0)


def test_verbleibende_minuten_exactly_now():
    dl = make_deadline(offset_minutes=0)
    assert dl.verbleibende_minuten(NOW) == pytest.approx(0.0)


def test_verbleibende_minuten_fractional():
    dl = make_deadline(offset_minutes=90)
    assert dl.verbleibende_minuten(NOW) == pytest.approx(90.0)


# ─────────────────────────────────────────────
# WorkflowDeadline — ist_verletzt
# ─────────────────────────────────────────────

def test_ist_verletzt_ausstehend_future():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=60)
    assert dl.ist_verletzt(NOW) is False


def test_ist_verletzt_ausstehend_past():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-30)
    assert dl.ist_verletzt(NOW) is True


def test_ist_verletzt_ausstehend_exactly_now():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=0)
    assert dl.ist_verletzt(NOW) is True


def test_ist_verletzt_erfuellt_past():
    dl = make_deadline(DeadlineStatus.ERFUELLT, offset_minutes=-60)
    assert dl.ist_verletzt(NOW) is False


def test_ist_verletzt_verletzt_past():
    dl = make_deadline(DeadlineStatus.VERLETZT, offset_minutes=-60)
    assert dl.ist_verletzt(NOW) is False


def test_ist_verletzt_eskaliert_past():
    dl = make_deadline(DeadlineStatus.ESKALIERT, offset_minutes=-60)
    assert dl.ist_verletzt(NOW) is False


# ─────────────────────────────────────────────
# WorkflowDeadline — berechne_eskalations_stufe
# ─────────────────────────────────────────────

def test_eskalation_not_violated_returns_none():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=120)
    assert dl.berechne_eskalations_stufe(NOW) is None


def test_eskalation_erfuellt_returns_none():
    dl = make_deadline(DeadlineStatus.ERFUELLT, offset_minutes=-60)
    assert dl.berechne_eskalations_stufe(NOW) is None


def test_eskalation_30min_overdue_stufe1():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-30)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_1


def test_eskalation_1min_overdue_stufe1():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-1)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_1


def test_eskalation_59min_overdue_stufe1():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-59)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_1


def test_eskalation_60min_overdue_stufe2():
    """Exactly 60 min → STUFE_2 (< 60 exclusive)."""
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-60)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_2


def test_eskalation_120min_overdue_stufe2():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-120)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_2


def test_eskalation_239min_overdue_stufe2():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-239)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_2


def test_eskalation_240min_overdue_stufe3():
    """Exactly 240 min → STUFE_3."""
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-240)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_3


def test_eskalation_300min_overdue_stufe3():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-300)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_3


def test_eskalation_1439min_overdue_stufe3():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-1439)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_3


def test_eskalation_1440min_overdue_kritisch():
    """Exactly 1440 min (24h) → KRITISCH."""
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-1440)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.KRITISCH


def test_eskalation_2880min_overdue_kritisch():
    dl = make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=-2880)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.KRITISCH


def test_eskalation_verletzt_status_returns_none():
    """Status VERLETZT not AUSSTEHEND → ist_verletzt=False → None."""
    dl = make_deadline(DeadlineStatus.VERLETZT, offset_minutes=-500)
    assert dl.berechne_eskalations_stufe(NOW) is None


# ─────────────────────────────────────────────
# DeadlineMonitor — verletzte_deadlines
# ─────────────────────────────────────────────

def test_monitor_verletzte_deadlines_default():
    monitor = get_default_deadline_monitor()
    verletzt = monitor.verletzte_deadlines(NOW)
    verletzt_ids = {d.deadline_id for d in verletzt}
    # DL-002 (30min past), DL-003 (5h past), DL-004 (2 days past)
    assert "DL-002" in verletzt_ids
    assert "DL-003" in verletzt_ids
    assert "DL-004" in verletzt_ids


def test_monitor_verletzte_excludes_future():
    monitor = get_default_deadline_monitor()
    verletzt = monitor.verletzte_deadlines(NOW)
    verletzt_ids = {d.deadline_id for d in verletzt}
    # DL-001 (2h future) and DL-006 (1 day future) not violated
    assert "DL-001" not in verletzt_ids
    assert "DL-006" not in verletzt_ids


def test_monitor_verletzte_excludes_erfuellt():
    monitor = get_default_deadline_monitor()
    verletzt = monitor.verletzte_deadlines(NOW)
    verletzt_ids = {d.deadline_id for d in verletzt}
    # DL-005 is ERFUELLT even though past → not violated
    assert "DL-005" not in verletzt_ids


def test_monitor_verletzte_count_default():
    monitor = get_default_deadline_monitor()
    assert len(monitor.verletzte_deadlines(NOW)) == 3


def test_monitor_verletzte_empty_monitor():
    monitor = DeadlineMonitor("DM-TEST")
    assert monitor.verletzte_deadlines(NOW) == []


def test_monitor_verletzte_all_future():
    monitor = DeadlineMonitor("DM-TEST")
    monitor.deadlines = [
        make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=60),
        make_deadline(DeadlineStatus.AUSSTEHEND, offset_minutes=120),
    ]
    assert monitor.verletzte_deadlines(NOW) == []


# ─────────────────────────────────────────────
# DeadlineMonitor — kritische_deadlines
# ─────────────────────────────────────────────

def test_monitor_kritische_deadlines_default():
    monitor = get_default_deadline_monitor()
    kritisch = monitor.kritische_deadlines(NOW)
    # DL-004: 2 days overdue = 2880 min ≥ 1440 → KRITISCH
    kritisch_ids = {d.deadline_id for d in kritisch}
    assert "DL-004" in kritisch_ids


def test_monitor_kritische_only_dl004():
    monitor = get_default_deadline_monitor()
    kritisch = monitor.kritische_deadlines(NOW)
    assert len(kritisch) == 1
    assert kritisch[0].deadline_id == "DL-004"


def test_monitor_kritische_excludes_stufe1_2_3():
    monitor = get_default_deadline_monitor()
    kritisch = monitor.kritische_deadlines(NOW)
    kritisch_ids = {d.deadline_id for d in kritisch}
    # DL-002 (STUFE_1), DL-003 (STUFE_3) not KRITISCH
    assert "DL-002" not in kritisch_ids
    assert "DL-003" not in kritisch_ids


def test_monitor_kritische_empty_monitor():
    monitor = DeadlineMonitor("DM-TEST")
    assert monitor.kritische_deadlines(NOW) == []


# ─────────────────────────────────────────────
# DeadlineMonitor — sla_einhaltungs_rate_pct
# ─────────────────────────────────────────────

def test_sla_rate_no_completed_100():
    monitor = DeadlineMonitor("DM-TEST")
    assert monitor.sla_einhaltungs_rate_pct() == 100.0


def test_sla_rate_only_ausstehend_100():
    monitor = DeadlineMonitor("DM-TEST")
    monitor.deadlines = [
        make_deadline(DeadlineStatus.AUSSTEHEND, 60),
        make_deadline(DeadlineStatus.AUSSTEHEND, 120),
    ]
    assert monitor.sla_einhaltungs_rate_pct() == 100.0


def test_sla_rate_one_erfuellt_zero_verletzt_100():
    monitor = DeadlineMonitor("DM-TEST")
    monitor.deadlines = [make_deadline(DeadlineStatus.ERFUELLT, -30)]
    assert monitor.sla_einhaltungs_rate_pct() == 100.0


def test_sla_rate_default_monitor():
    """Default: DL-005 ERFUELLT, no VERLETZT/ESKALIERT in status → 100.0."""
    monitor = get_default_deadline_monitor()
    assert monitor.sla_einhaltungs_rate_pct() == 100.0


def test_sla_rate_with_verletzt():
    monitor = DeadlineMonitor("DM-TEST")
    monitor.deadlines = [
        make_deadline(DeadlineStatus.ERFUELLT, -10),
        make_deadline(DeadlineStatus.VERLETZT, -30),
    ]
    rate = monitor.sla_einhaltungs_rate_pct()
    assert rate == pytest.approx(50.0)


def test_sla_rate_with_eskaliert():
    monitor = DeadlineMonitor("DM-TEST")
    monitor.deadlines = [
        make_deadline(DeadlineStatus.ERFUELLT, -10),
        make_deadline(DeadlineStatus.ERFUELLT, -10),
        make_deadline(DeadlineStatus.ESKALIERT, -30),
    ]
    rate = monitor.sla_einhaltungs_rate_pct()
    assert rate == pytest.approx(200 / 3)


def test_sla_rate_all_verletzt_0():
    monitor = DeadlineMonitor("DM-TEST")
    monitor.deadlines = [
        make_deadline(DeadlineStatus.VERLETZT, -30),
        make_deadline(DeadlineStatus.VERLETZT, -60),
    ]
    assert monitor.sla_einhaltungs_rate_pct() == pytest.approx(0.0)


def test_sla_rate_ausstehend_not_counted():
    monitor = DeadlineMonitor("DM-TEST")
    # 1 ERFUELLT, 1 VERLETZT, 2 AUSSTEHEND → 50%
    monitor.deadlines = [
        make_deadline(DeadlineStatus.ERFUELLT, -10),
        make_deadline(DeadlineStatus.VERLETZT, -30),
        make_deadline(DeadlineStatus.AUSSTEHEND, 60),
        make_deadline(DeadlineStatus.AUSSTEHEND, 120),
    ]
    assert monitor.sla_einhaltungs_rate_pct() == pytest.approx(50.0)


# ─────────────────────────────────────────────
# Default Monitor — detailed checks
# ─────────────────────────────────────────────

def test_default_monitor_id():
    monitor = get_default_deadline_monitor()
    assert monitor.monitor_id == "DM-001"


def test_default_monitor_total_deadlines():
    monitor = get_default_deadline_monitor()
    assert len(monitor.deadlines) == 6


def test_dl001_future():
    monitor = get_default_deadline_monitor()
    dl = next(d for d in monitor.deadlines if d.deadline_id == "DL-001")
    assert dl.verbleibende_minuten(NOW) > 0
    assert dl.ist_verletzt(NOW) is False


def test_dl001_typ_sla():
    monitor = get_default_deadline_monitor()
    dl = next(d for d in monitor.deadlines if d.deadline_id == "DL-001")
    assert dl.deadline_typ == DeadlineTyp.SLA


def test_dl002_30min_overdue():
    monitor = get_default_deadline_monitor()
    dl = next(d for d in monitor.deadlines if d.deadline_id == "DL-002")
    assert dl.verbleibende_minuten(NOW) == pytest.approx(-30.0)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_1


def test_dl003_300min_overdue():
    monitor = get_default_deadline_monitor()
    dl = next(d for d in monitor.deadlines if d.deadline_id == "DL-003")
    assert dl.verbleibende_minuten(NOW) == pytest.approx(-300.0)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.STUFE_3


def test_dl004_2880min_overdue_kritisch():
    monitor = get_default_deadline_monitor()
    dl = next(d for d in monitor.deadlines if d.deadline_id == "DL-004")
    assert dl.verbleibende_minuten(NOW) == pytest.approx(-2880.0)
    assert dl.berechne_eskalations_stufe(NOW) == EskalationsStufe.KRITISCH


def test_dl005_erfuellt():
    monitor = get_default_deadline_monitor()
    dl = next(d for d in monitor.deadlines if d.deadline_id == "DL-005")
    assert dl.status == DeadlineStatus.ERFUELLT
    assert dl.ist_verletzt(NOW) is False
    assert dl.berechne_eskalations_stufe(NOW) is None


def test_dl006_future():
    monitor = get_default_deadline_monitor()
    dl = next(d for d in monitor.deadlines if d.deadline_id == "DL-006")
    assert dl.verbleibende_minuten(NOW) > 0
    assert dl.ist_verletzt(NOW) is False


def test_dl002_hart_typ():
    monitor = get_default_deadline_monitor()
    dl = next(d for d in monitor.deadlines if d.deadline_id == "DL-002")
    assert dl.deadline_typ == DeadlineTyp.HART


def test_dl003_weich_typ():
    monitor = get_default_deadline_monitor()
    dl = next(d for d in monitor.deadlines if d.deadline_id == "DL-003")
    assert dl.deadline_typ == DeadlineTyp.WEICH


def test_dl004_gesetzlich_typ():
    monitor = get_default_deadline_monitor()
    dl = next(d for d in monitor.deadlines if d.deadline_id == "DL-004")
    assert dl.deadline_typ == DeadlineTyp.GESETZLICH


# ─────────────────────────────────────────────
# API endpoint smoke tests (via TestClient)
# ─────────────────────────────────────────────

def test_api_template_vorlagen():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.get("/api/v1/process/template/vorlagen")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 3


def test_api_template_vorlagen_fields():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.get("/api/v1/process/template/vorlagen")
    t = next(x for x in resp.json() if x["template_id"] == "PT-001")
    assert t["ist_verwendbar"] is True
    assert t["pflicht_schritte_anzahl"] == 4
    assert t["geschaetzte_gesamtdauer_minuten"] == 60


def test_api_template_instanziere_erfolgreich():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    payload = {
        "template_id": "PT-001",
        "parameter": {"lieferant_id": "L1", "menge_tonnen": 100, "preis_eur_t": 250},
        "neue_instanz_id": "WI-TEST-001",
    }
    resp = client.post("/api/v1/process/template/instanziere", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ERFOLGREICH"
    assert data["workflow_instanz_id"] == "WI-TEST-001"


def test_api_template_instanziere_validierungsfehler():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    payload = {
        "template_id": "PT-001",
        "parameter": {"lieferant_id": "L1"},
        "neue_instanz_id": "WI-TEST-002",
    }
    resp = client.post("/api/v1/process/template/instanziere", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "VALIDIERUNGSFEHLER"
    assert "menge_tonnen" in data["fehlende_parameter"] or "preis_eur_t" in data["fehlende_parameter"]


def test_api_template_instanziere_not_found():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.post("/api/v1/process/template/instanziere",
                       json={"template_id": "PT-999", "parameter": {}, "neue_instanz_id": "WI-X"})
    assert resp.status_code == 200
    data = resp.json()
    assert "fehler" in data


def test_api_deadline_monitor():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.get("/api/v1/process/deadline/monitor")
    assert resp.status_code == 200
    data = resp.json()
    assert data["monitor_id"] == "DM-001"
    assert data["deadlines_gesamt"] == 6
    assert data["verletzte_deadlines"] == 3
    assert data["kritische_deadlines"] == 1


def test_api_deadline_monitor_sla_rate():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.get("/api/v1/process/deadline/monitor")
    data = resp.json()
    assert data["sla_einhaltungs_rate_pct"] == pytest.approx(100.0)


def test_api_pruefe_eskalation_dl002():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.post("/api/v1/process/deadline/pruefe-eskalation", json={"deadline_id": "DL-002"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ist_verletzt"] is True
    assert data["eskalations_stufe"] == "STUFE_1"


def test_api_pruefe_eskalation_dl004():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.post("/api/v1/process/deadline/pruefe-eskalation", json={"deadline_id": "DL-004"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["eskalations_stufe"] == "KRITISCH"


def test_api_pruefe_eskalation_not_found():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.post("/api/v1/process/deadline/pruefe-eskalation", json={"deadline_id": "DL-999"})
    assert resp.status_code == 200
    assert "fehler" in resp.json()


def test_api_pruefe_eskalation_dl001_not_violated():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.post("/api/v1/process/deadline/pruefe-eskalation", json={"deadline_id": "DL-001"})
    data = resp.json()
    assert data["ist_verletzt"] is False
    assert data["eskalations_stufe"] is None


# === Additional Tests to reach 130+ ===

def test_prozess_template_version_string():
    from app.core.process_template_contracts import ProzessTemplate, TemplateTyp, TemplateStatus
    t = ProzessTemplate("PT-X", "Test", "typ", TemplateTyp.STANDARD, TemplateStatus.AKTIV, "3.5.1")
    assert t.version == "3.5.1"


def test_prozess_template_tenant_id_none_by_default():
    from app.core.process_template_contracts import ProzessTemplate, TemplateTyp, TemplateStatus
    t = ProzessTemplate("PT-X", "Test", "typ", TemplateTyp.STANDARD)
    assert t.tenant_id is None


def test_prozess_template_tenant_id_set():
    from app.core.process_template_contracts import ProzessTemplate, TemplateTyp, TemplateStatus
    t = ProzessTemplate("PT-X", "Test", "typ", TemplateTyp.REGULATORISCH,
                         TemplateStatus.AKTIV, "1.0.0", tenant_id="TENANT-42")
    assert t.tenant_id == "TENANT-42"


def test_workflow_deadline_verantwortlich():
    from app.core.workflow_deadline_contracts import WorkflowDeadline, DeadlineTyp, DeadlineStatus
    from datetime import datetime
    dl = WorkflowDeadline("DL-X", "WI-X", DeadlineTyp.SLA,
                           datetime(2026, 3, 17, 12, 0, 0),
                           verantwortlich="user-99")
    assert dl.verantwortlich == "user-99"


def test_deadline_monitor_sla_rate_all_verletzt():
    from app.core.workflow_deadline_contracts import DeadlineMonitor, WorkflowDeadline, DeadlineTyp, DeadlineStatus
    from datetime import datetime
    monitor = DeadlineMonitor("DM-TEST")
    monitor.deadlines = [
        WorkflowDeadline("DL-A", "WI-A", DeadlineTyp.HART,
                          datetime(2026, 3, 15), DeadlineStatus.VERLETZT),
        WorkflowDeadline("DL-B", "WI-B", DeadlineTyp.HART,
                          datetime(2026, 3, 15), DeadlineStatus.VERLETZT),
    ]
    assert monitor.sla_einhaltungs_rate_pct() == 0.0
