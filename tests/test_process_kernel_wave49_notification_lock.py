"""
Wave 49 Tests — Process Notification Contracts + Workflow Lock Contracts
Abdeckung: NotifikationsVorlage, NotifikationsZustellung, ZustellStatistik,
erstelle_zustellung, berechne_zustellstatistik, get_default_notifikations_vorlagen,
WorkflowLock, LockAkquisitionsErgebnis, akquiriere_lock, get_default_locks.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.core.process_notification_contracts_wave49 import (
    NotifikationsKanal,
    NotifikationsPrioritaet,
    NotifikationsVorlage,
    NotifikationsZustellung,
    ZustellStatistik,
    ZustellStatus,
    berechne_zustellstatistik,
    erstelle_zustellung,
    get_default_notifikations_vorlagen,
)
from app.core.workflow_lock_contracts import (
    KonfliktTyp,
    LockAkquisitionsErgebnis,
    LockStatus,
    LockTyp,
    WorkflowLock,
    akquiriere_lock,
    get_default_locks,
)


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def vorlage_email() -> NotifikationsVorlage:
    return NotifikationsVorlage(
        vorlage_id="V-TEST-001",
        vorlage_name="Test Email Vorlage",
        kanal=NotifikationsKanal.EMAIL,
        prioritaet=NotifikationsPrioritaet.HOCH,
        betreff_template="Betreff: {{titel}}",
        nachricht_template="Hallo {{name}}, Ihre Referenz: {{ref}}.",
        platzhalter=["titel", "name", "ref"],
        beschreibung="Test-Vorlage fuer Unit-Tests",
    )


@pytest.fixture
def vorlage_sms() -> NotifikationsVorlage:
    return NotifikationsVorlage(
        vorlage_id="V-TEST-002",
        vorlage_name="Test SMS Vorlage",
        kanal=NotifikationsKanal.SMS,
        prioritaet=NotifikationsPrioritaet.KRITISCH,
        betreff_template="ALARM {{code}}",
        nachricht_template="Kritisch: {{code}} um {{zeit}}",
        platzhalter=["code", "zeit"],
    )


@pytest.fixture
def ts_fixed() -> datetime:
    return datetime(2026, 3, 15, 12, 0, 0)


@pytest.fixture
def zustellung_zugestellt(ts_fixed: datetime) -> NotifikationsZustellung:
    return NotifikationsZustellung(
        zustellung_id="Z-001",
        vorlage_id="V-TEST-001",
        empfaenger_id="user-42",
        kanal=NotifikationsKanal.EMAIL,
        prioritaet=NotifikationsPrioritaet.HOCH,
        betreff="Betreff: Test",
        nachricht="Hallo Welt",
        status=ZustellStatus.ZUGESTELLT,
        erstellt_am=ts_fixed,
        zugestellt_am=ts_fixed + timedelta(minutes=2),
    )


@pytest.fixture
def zustellung_fehlgeschlagen(ts_fixed: datetime) -> NotifikationsZustellung:
    return NotifikationsZustellung(
        zustellung_id="Z-002",
        vorlage_id="V-TEST-001",
        empfaenger_id="user-99",
        kanal=NotifikationsKanal.EMAIL,
        prioritaet=NotifikationsPrioritaet.HOCH,
        betreff="Betreff: Test",
        nachricht="Hallo Welt",
        status=ZustellStatus.FEHLGESCHLAGEN,
        fehlermeldung="SMTP Timeout",
        versuch_anzahl=3,
        erstellt_am=ts_fixed,
    )


@pytest.fixture
def zustellung_ausstehend(ts_fixed: datetime) -> NotifikationsZustellung:
    return NotifikationsZustellung(
        zustellung_id="Z-003",
        vorlage_id="V-TEST-002",
        empfaenger_id="user-10",
        kanal=NotifikationsKanal.SMS,
        prioritaet=NotifikationsPrioritaet.KRITISCH,
        betreff="ALARM X1",
        nachricht="Kritisch: X1 um 12:00",
        status=ZustellStatus.AUSSTEHEND,
        erstellt_am=ts_fixed,
    )


@pytest.fixture
def lock_schreiben_aktiv(ts_fixed: datetime) -> WorkflowLock:
    return WorkflowLock(
        lock_id="LK-TEST-001",
        ressource_id="res:ABC",
        inhaber_id="user-A",
        lock_typ=LockTyp.SCHREIBEN,
        status=LockStatus.AKTIV,
        version=1,
        ttl_sekunden=300,
        erstellt_am=ts_fixed,
    )


@pytest.fixture
def lock_lesen_aktiv(ts_fixed: datetime) -> WorkflowLock:
    return WorkflowLock(
        lock_id="LK-TEST-002",
        ressource_id="res:ABC",
        inhaber_id="user-B",
        lock_typ=LockTyp.LESEN,
        status=LockStatus.AKTIV,
        version=1,
        ttl_sekunden=300,
        erstellt_am=ts_fixed,
    )


@pytest.fixture
def lock_optimistisch_v1(ts_fixed: datetime) -> WorkflowLock:
    return WorkflowLock(
        lock_id="LK-TEST-003",
        ressource_id="res:XYZ",
        inhaber_id="user-C",
        lock_typ=LockTyp.OPTIMISTISCH,
        status=LockStatus.AKTIV,
        version=1,
        ttl_sekunden=120,
        erstellt_am=ts_fixed,
    )


# ===========================================================================
# Section 1: Enum Tests — NotifikationsKanal
# ===========================================================================

def test_notifikations_kanal_email():
    assert NotifikationsKanal.EMAIL == "EMAIL"

def test_notifikations_kanal_sms():
    assert NotifikationsKanal.SMS == "SMS"

def test_notifikations_kanal_push():
    assert NotifikationsKanal.PUSH == "PUSH"

def test_notifikations_kanal_in_app():
    assert NotifikationsKanal.IN_APP == "IN_APP"

def test_notifikations_kanal_webhook():
    assert NotifikationsKanal.WEBHOOK == "WEBHOOK"


# ===========================================================================
# Section 2: Enum Tests — NotifikationsPrioritaet
# ===========================================================================

def test_prioritaet_niedrig():
    assert NotifikationsPrioritaet.NIEDRIG == "NIEDRIG"

def test_prioritaet_normal():
    assert NotifikationsPrioritaet.NORMAL == "NORMAL"

def test_prioritaet_hoch():
    assert NotifikationsPrioritaet.HOCH == "HOCH"

def test_prioritaet_kritisch():
    assert NotifikationsPrioritaet.KRITISCH == "KRITISCH"


# ===========================================================================
# Section 3: Enum Tests — ZustellStatus
# ===========================================================================

def test_zustellstatus_ausstehend():
    assert ZustellStatus.AUSSTEHEND == "AUSSTEHEND"

def test_zustellstatus_versendet():
    assert ZustellStatus.VERSENDET == "VERSENDET"

def test_zustellstatus_zugestellt():
    assert ZustellStatus.ZUGESTELLT == "ZUGESTELLT"

def test_zustellstatus_fehlgeschlagen():
    assert ZustellStatus.FEHLGESCHLAGEN == "FEHLGESCHLAGEN"

def test_zustellstatus_gedrosselt():
    assert ZustellStatus.GEDROSSELT == "GEDROSSELT"


# ===========================================================================
# Section 4: NotifikationsVorlage.render()
# ===========================================================================

def test_render_single_substitution(vorlage_email: NotifikationsVorlage):
    betreff, _ = vorlage_email.render({"titel": "Freigabe"})
    assert "Freigabe" in betreff
    assert "{{titel}}" not in betreff

def test_render_multiple_substitutions(vorlage_email: NotifikationsVorlage):
    betreff, nachricht = vorlage_email.render({"titel": "X", "name": "Hans", "ref": "R-99"})
    assert "X" in betreff
    assert "Hans" in nachricht
    assert "R-99" in nachricht

def test_render_unknown_placeholder_stays(vorlage_email: NotifikationsVorlage):
    betreff, nachricht = vorlage_email.render({"titel": "T"})
    # {{name}} and {{ref}} not in kontext → remain unchanged
    assert "{{name}}" in nachricht
    assert "{{ref}}" in nachricht

def test_render_empty_kontext_leaves_template_unchanged(vorlage_email: NotifikationsVorlage):
    betreff, nachricht = vorlage_email.render({})
    assert betreff == vorlage_email.betreff_template
    assert nachricht == vorlage_email.nachricht_template

def test_render_returns_tuple(vorlage_email: NotifikationsVorlage):
    result = vorlage_email.render({"titel": "X", "name": "Y", "ref": "Z"})
    assert isinstance(result, tuple)
    assert len(result) == 2

def test_render_converts_int_to_str(vorlage_sms: NotifikationsVorlage):
    _, nachricht = vorlage_sms.render({"code": 42, "zeit": "08:00"})
    assert "42" in nachricht


# ===========================================================================
# Section 5: NotifikationsVorlage.as_dict()
# ===========================================================================

def test_vorlage_as_dict_all_fields_present(vorlage_email: NotifikationsVorlage):
    d = vorlage_email.as_dict()
    assert d["vorlage_id"] == "V-TEST-001"
    assert d["vorlage_name"] == "Test Email Vorlage"
    assert d["kanal"] == "EMAIL"
    assert d["prioritaet"] == "HOCH"
    assert d["betreff_template"] == "Betreff: {{titel}}"
    assert "nachricht_template" in d
    assert d["platzhalter"] == ["titel", "name", "ref"]
    assert d["beschreibung"] == "Test-Vorlage fuer Unit-Tests"

def test_vorlage_as_dict_kanal_is_string(vorlage_email: NotifikationsVorlage):
    d = vorlage_email.as_dict()
    assert isinstance(d["kanal"], str)

def test_vorlage_as_dict_prioritaet_is_string(vorlage_email: NotifikationsVorlage):
    d = vorlage_email.as_dict()
    assert isinstance(d["prioritaet"], str)


# ===========================================================================
# Section 6: NotifikationsZustellung.ist_zugestellt
# ===========================================================================

def test_ist_zugestellt_true_for_zugestellt(zustellung_zugestellt: NotifikationsZustellung):
    assert zustellung_zugestellt.ist_zugestellt is True

def test_ist_zugestellt_false_for_fehlgeschlagen(zustellung_fehlgeschlagen: NotifikationsZustellung):
    assert zustellung_fehlgeschlagen.ist_zugestellt is False

def test_ist_zugestellt_false_for_ausstehend(zustellung_ausstehend: NotifikationsZustellung):
    assert zustellung_ausstehend.ist_zugestellt is False

def test_ist_zugestellt_false_for_versendet(ts_fixed: datetime):
    z = NotifikationsZustellung(
        zustellung_id="Z-V",
        vorlage_id="V-001",
        empfaenger_id="u1",
        kanal=NotifikationsKanal.EMAIL,
        prioritaet=NotifikationsPrioritaet.NORMAL,
        betreff="B",
        nachricht="N",
        status=ZustellStatus.VERSENDET,
        erstellt_am=ts_fixed,
    )
    assert z.ist_zugestellt is False

def test_ist_zugestellt_false_for_gedrosselt(ts_fixed: datetime):
    z = NotifikationsZustellung(
        zustellung_id="Z-G",
        vorlage_id="V-001",
        empfaenger_id="u1",
        kanal=NotifikationsKanal.EMAIL,
        prioritaet=NotifikationsPrioritaet.NORMAL,
        betreff="B",
        nachricht="N",
        status=ZustellStatus.GEDROSSELT,
        erstellt_am=ts_fixed,
    )
    assert z.ist_zugestellt is False


# ===========================================================================
# Section 7: NotifikationsZustellung.ist_fehlgeschlagen
# ===========================================================================

def test_ist_fehlgeschlagen_true_for_fehlgeschlagen(zustellung_fehlgeschlagen: NotifikationsZustellung):
    assert zustellung_fehlgeschlagen.ist_fehlgeschlagen is True

def test_ist_fehlgeschlagen_false_for_zugestellt(zustellung_zugestellt: NotifikationsZustellung):
    assert zustellung_zugestellt.ist_fehlgeschlagen is False

def test_ist_fehlgeschlagen_false_for_ausstehend(zustellung_ausstehend: NotifikationsZustellung):
    assert zustellung_ausstehend.ist_fehlgeschlagen is False


# ===========================================================================
# Section 8: NotifikationsZustellung.as_dict()
# ===========================================================================

def test_zustellung_as_dict_zugestellt_am_is_iso_string(zustellung_zugestellt: NotifikationsZustellung):
    d = zustellung_zugestellt.as_dict()
    assert d["zugestellt_am"] is not None
    assert isinstance(d["zugestellt_am"], str)
    assert "T" in d["zugestellt_am"]  # ISO 8601 format

def test_zustellung_as_dict_zugestellt_am_is_none_when_not_set(zustellung_fehlgeschlagen: NotifikationsZustellung):
    d = zustellung_fehlgeschlagen.as_dict()
    assert d["zugestellt_am"] is None

def test_zustellung_as_dict_status_is_string(zustellung_zugestellt: NotifikationsZustellung):
    d = zustellung_zugestellt.as_dict()
    assert isinstance(d["status"], str)
    assert d["status"] == "ZUGESTELLT"

def test_zustellung_as_dict_contains_ist_zugestellt(zustellung_zugestellt: NotifikationsZustellung):
    d = zustellung_zugestellt.as_dict()
    assert "ist_zugestellt" in d
    assert d["ist_zugestellt"] is True

def test_zustellung_as_dict_contains_ist_fehlgeschlagen(zustellung_fehlgeschlagen: NotifikationsZustellung):
    d = zustellung_fehlgeschlagen.as_dict()
    assert "ist_fehlgeschlagen" in d
    assert d["ist_fehlgeschlagen"] is True

def test_zustellung_as_dict_erstellt_am_is_iso(zustellung_zugestellt: NotifikationsZustellung):
    d = zustellung_zugestellt.as_dict()
    assert isinstance(d["erstellt_am"], str)
    assert "T" in d["erstellt_am"]

def test_zustellung_as_dict_kanal_is_string(zustellung_zugestellt: NotifikationsZustellung):
    d = zustellung_zugestellt.as_dict()
    assert d["kanal"] == "EMAIL"


# ===========================================================================
# Section 9: ZustellStatistik.erfolgsrate_pct
# ===========================================================================

def test_erfolgsrate_pct_zero_for_empty():
    stat = ZustellStatistik(
        kanal=NotifikationsKanal.EMAIL,
        gesamt=0,
        zugestellt=0,
        fehlgeschlagen=0,
        ausstehend=0,
    )
    assert stat.erfolgsrate_pct == 0.0

def test_erfolgsrate_pct_correct_calculation():
    stat = ZustellStatistik(
        kanal=NotifikationsKanal.EMAIL,
        gesamt=10,
        zugestellt=7,
        fehlgeschlagen=2,
        ausstehend=1,
    )
    assert stat.erfolgsrate_pct == 70.0

def test_erfolgsrate_pct_100_all_delivered():
    stat = ZustellStatistik(
        kanal=NotifikationsKanal.PUSH,
        gesamt=5,
        zugestellt=5,
        fehlgeschlagen=0,
        ausstehend=0,
    )
    assert stat.erfolgsrate_pct == 100.0

def test_erfolgsrate_pct_rounded_to_two_decimals():
    stat = ZustellStatistik(
        kanal=NotifikationsKanal.SMS,
        gesamt=3,
        zugestellt=1,
        fehlgeschlagen=1,
        ausstehend=1,
    )
    # 1/3 * 100 = 33.333... → rounded to 33.33
    assert stat.erfolgsrate_pct == 33.33


# ===========================================================================
# Section 10: ZustellStatistik.as_dict()
# ===========================================================================

def test_zustellstatistik_as_dict_all_fields():
    stat = ZustellStatistik(
        kanal=NotifikationsKanal.WEBHOOK,
        gesamt=20,
        zugestellt=18,
        fehlgeschlagen=1,
        ausstehend=1,
    )
    d = stat.as_dict()
    assert d["kanal"] == "WEBHOOK"
    assert d["gesamt"] == 20
    assert d["zugestellt"] == 18
    assert d["fehlgeschlagen"] == 1
    assert d["ausstehend"] == 1
    assert d["erfolgsrate_pct"] == 90.0


# ===========================================================================
# Section 11: erstelle_zustellung()
# ===========================================================================

def test_erstelle_zustellung_renders_template(vorlage_email: NotifikationsVorlage, ts_fixed: datetime):
    kontext = {"titel": "Freigabe-K99", "name": "Muller", "ref": "K-99"}
    z = erstelle_zustellung("Z-NEW-001", vorlage_email, "user-5", kontext, erstellt_am=ts_fixed)
    assert "Freigabe-K99" in z.betreff
    assert "Muller" in z.nachricht
    assert "K-99" in z.nachricht

def test_erstelle_zustellung_status_is_ausstehend(vorlage_email: NotifikationsVorlage, ts_fixed: datetime):
    z = erstelle_zustellung("Z-NEW-002", vorlage_email, "user-5", {}, erstellt_am=ts_fixed)
    assert z.status == ZustellStatus.AUSSTEHEND

def test_erstelle_zustellung_kanal_from_vorlage(vorlage_email: NotifikationsVorlage, ts_fixed: datetime):
    z = erstelle_zustellung("Z-NEW-003", vorlage_email, "user-5", {}, erstellt_am=ts_fixed)
    assert z.kanal == NotifikationsKanal.EMAIL

def test_erstelle_zustellung_prioritaet_from_vorlage(vorlage_email: NotifikationsVorlage, ts_fixed: datetime):
    z = erstelle_zustellung("Z-NEW-004", vorlage_email, "user-5", {}, erstellt_am=ts_fixed)
    assert z.prioritaet == NotifikationsPrioritaet.HOCH

def test_erstelle_zustellung_custom_erstellt_am(vorlage_sms: NotifikationsVorlage, ts_fixed: datetime):
    z = erstelle_zustellung("Z-NEW-005", vorlage_sms, "user-6", {}, erstellt_am=ts_fixed)
    assert z.erstellt_am == ts_fixed

def test_erstelle_zustellung_vorlage_id_copied(vorlage_email: NotifikationsVorlage, ts_fixed: datetime):
    z = erstelle_zustellung("Z-NEW-006", vorlage_email, "user-7", {}, erstellt_am=ts_fixed)
    assert z.vorlage_id == "V-TEST-001"

def test_erstelle_zustellung_empfaenger_id_set(vorlage_email: NotifikationsVorlage, ts_fixed: datetime):
    z = erstelle_zustellung("Z-NEW-007", vorlage_email, "user-XY", {}, erstellt_am=ts_fixed)
    assert z.empfaenger_id == "user-XY"

def test_erstelle_zustellung_zugestellt_am_is_none(vorlage_email: NotifikationsVorlage, ts_fixed: datetime):
    z = erstelle_zustellung("Z-NEW-008", vorlage_email, "user-5", {}, erstellt_am=ts_fixed)
    assert z.zugestellt_am is None


# ===========================================================================
# Section 12: berechne_zustellstatistik()
# ===========================================================================

def test_berechne_statistik_only_counts_matching_kanal(
    zustellung_zugestellt: NotifikationsZustellung,
    zustellung_ausstehend: NotifikationsZustellung,
):
    # zustellung_zugestellt is EMAIL, zustellung_ausstehend is SMS
    stat = berechne_zustellstatistik(
        [zustellung_zugestellt, zustellung_ausstehend],
        NotifikationsKanal.EMAIL,
    )
    assert stat.gesamt == 1
    assert stat.zugestellt == 1

def test_berechne_statistik_sms_kanal(
    zustellung_zugestellt: NotifikationsZustellung,
    zustellung_ausstehend: NotifikationsZustellung,
):
    stat = berechne_zustellstatistik(
        [zustellung_zugestellt, zustellung_ausstehend],
        NotifikationsKanal.SMS,
    )
    assert stat.gesamt == 1
    assert stat.ausstehend == 1

def test_berechne_statistik_correct_fehlgeschlagen_count(
    zustellung_fehlgeschlagen: NotifikationsZustellung,
    zustellung_zugestellt: NotifikationsZustellung,
):
    stat = berechne_zustellstatistik(
        [zustellung_fehlgeschlagen, zustellung_zugestellt],
        NotifikationsKanal.EMAIL,
    )
    assert stat.fehlgeschlagen == 1
    assert stat.zugestellt == 1
    assert stat.gesamt == 2

def test_berechne_statistik_empty_list():
    stat = berechne_zustellstatistik([], NotifikationsKanal.EMAIL)
    assert stat.gesamt == 0
    assert stat.erfolgsrate_pct == 0.0

def test_berechne_statistik_kanal_set_correctly():
    stat = berechne_zustellstatistik([], NotifikationsKanal.PUSH)
    assert stat.kanal == NotifikationsKanal.PUSH


# ===========================================================================
# Section 13: get_default_notifikations_vorlagen()
# ===========================================================================

def test_default_vorlagen_returns_5():
    vorlagen = get_default_notifikations_vorlagen()
    assert len(vorlagen) == 5

def test_default_vorlagen_nv001_email_hoch():
    vorlagen = get_default_notifikations_vorlagen()
    nv001 = next(v for v in vorlagen if v.vorlage_id == "NV-001")
    assert nv001.kanal == NotifikationsKanal.EMAIL
    assert nv001.prioritaet == NotifikationsPrioritaet.HOCH

def test_default_vorlagen_nv002_push():
    vorlagen = get_default_notifikations_vorlagen()
    nv002 = next(v for v in vorlagen if v.vorlage_id == "NV-002")
    assert nv002.kanal == NotifikationsKanal.PUSH

def test_default_vorlagen_nv003_sms_kritisch():
    vorlagen = get_default_notifikations_vorlagen()
    nv003 = next(v for v in vorlagen if v.vorlage_id == "NV-003")
    assert nv003.kanal == NotifikationsKanal.SMS
    assert nv003.prioritaet == NotifikationsPrioritaet.KRITISCH

def test_default_vorlagen_nv004_in_app_normal():
    vorlagen = get_default_notifikations_vorlagen()
    nv004 = next(v for v in vorlagen if v.vorlage_id == "NV-004")
    assert nv004.kanal == NotifikationsKanal.IN_APP
    assert nv004.prioritaet == NotifikationsPrioritaet.NORMAL

def test_default_vorlagen_nv005_webhook_kritisch():
    vorlagen = get_default_notifikations_vorlagen()
    nv005 = next(v for v in vorlagen if v.vorlage_id == "NV-005")
    assert nv005.kanal == NotifikationsKanal.WEBHOOK
    assert nv005.prioritaet == NotifikationsPrioritaet.KRITISCH

def test_default_vorlagen_all_have_platzhalter():
    vorlagen = get_default_notifikations_vorlagen()
    for v in vorlagen:
        assert len(v.platzhalter) > 0, f"{v.vorlage_id} has no platzhalter"

def test_default_vorlagen_all_have_beschreibung():
    vorlagen = get_default_notifikations_vorlagen()
    for v in vorlagen:
        assert v.beschreibung != "", f"{v.vorlage_id} missing beschreibung"


# ===========================================================================
# Section 14: Enum Tests — LockTyp
# ===========================================================================

def test_lock_typ_lesen():
    assert LockTyp.LESEN == "LESEN"

def test_lock_typ_schreiben():
    assert LockTyp.SCHREIBEN == "SCHREIBEN"

def test_lock_typ_optimistisch():
    assert LockTyp.OPTIMISTISCH == "OPTIMISTISCH"


# ===========================================================================
# Section 15: Enum Tests — LockStatus
# ===========================================================================

def test_lock_status_aktiv():
    assert LockStatus.AKTIV == "AKTIV"

def test_lock_status_abgelaufen():
    assert LockStatus.ABGELAUFEN == "ABGELAUFEN"

def test_lock_status_freigegeben():
    assert LockStatus.FREIGEGEBEN == "FREIGEGEBEN"

def test_lock_status_konflikt():
    assert LockStatus.KONFLIKT == "KONFLIKT"


# ===========================================================================
# Section 16: Enum Tests — KonfliktTyp
# ===========================================================================

def test_konflikt_typ_schreib_schreib():
    assert KonfliktTyp.SCHREIB_SCHREIB == "SCHREIB_SCHREIB"

def test_konflikt_typ_lese_schreib():
    assert KonfliktTyp.LESE_SCHREIB == "LESE_SCHREIB"

def test_konflikt_typ_version_konflikt():
    assert KonfliktTyp.VERSION_KONFLIKT == "VERSION_KONFLIKT"

def test_konflikt_typ_deadlock():
    assert KonfliktTyp.DEADLOCK == "DEADLOCK"


# ===========================================================================
# Section 17: WorkflowLock.__post_init__ — ablauf_am computation
# ===========================================================================

def test_ablauf_am_equals_erstellt_plus_ttl(ts_fixed: datetime):
    lock = WorkflowLock(
        lock_id="L-X",
        ressource_id="res:1",
        inhaber_id="u1",
        lock_typ=LockTyp.SCHREIBEN,
        status=LockStatus.AKTIV,
        version=1,
        ttl_sekunden=180,
        erstellt_am=ts_fixed,
    )
    assert lock.ablauf_am == ts_fixed + timedelta(seconds=180)

def test_ablauf_am_zero_ttl(ts_fixed: datetime):
    lock = WorkflowLock(
        lock_id="L-Y",
        ressource_id="res:2",
        inhaber_id="u2",
        lock_typ=LockTyp.LESEN,
        status=LockStatus.AKTIV,
        version=1,
        ttl_sekunden=0,
        erstellt_am=ts_fixed,
    )
    assert lock.ablauf_am == ts_fixed


# ===========================================================================
# Section 18: WorkflowLock.ist_aktiv
# ===========================================================================

def test_ist_aktiv_true_for_aktiv(lock_schreiben_aktiv: WorkflowLock):
    assert lock_schreiben_aktiv.ist_aktiv is True

def test_ist_aktiv_false_for_abgelaufen(ts_fixed: datetime):
    lock = WorkflowLock(
        lock_id="L-Z",
        ressource_id="res:3",
        inhaber_id="u3",
        lock_typ=LockTyp.SCHREIBEN,
        status=LockStatus.ABGELAUFEN,
        version=1,
        ttl_sekunden=60,
        erstellt_am=ts_fixed,
    )
    assert lock.ist_aktiv is False

def test_ist_aktiv_false_for_freigegeben(ts_fixed: datetime):
    lock = WorkflowLock(
        lock_id="L-W",
        ressource_id="res:4",
        inhaber_id="u4",
        lock_typ=LockTyp.LESEN,
        status=LockStatus.FREIGEGEBEN,
        version=1,
        ttl_sekunden=60,
        erstellt_am=ts_fixed,
    )
    assert lock.ist_aktiv is False

def test_ist_aktiv_false_for_konflikt(ts_fixed: datetime):
    lock = WorkflowLock(
        lock_id="L-K",
        ressource_id="res:5",
        inhaber_id="u5",
        lock_typ=LockTyp.SCHREIBEN,
        status=LockStatus.KONFLIKT,
        version=1,
        ttl_sekunden=60,
        erstellt_am=ts_fixed,
    )
    assert lock.ist_aktiv is False


# ===========================================================================
# Section 19: WorkflowLock.ist_abgelaufen()
# ===========================================================================

def test_ist_abgelaufen_true_when_jetzt_equals_ablauf(lock_schreiben_aktiv: WorkflowLock):
    assert lock_schreiben_aktiv.ist_abgelaufen(lock_schreiben_aktiv.ablauf_am) is True

def test_ist_abgelaufen_true_when_jetzt_after_ablauf(lock_schreiben_aktiv: WorkflowLock):
    jetzt = lock_schreiben_aktiv.ablauf_am + timedelta(seconds=1)
    assert lock_schreiben_aktiv.ist_abgelaufen(jetzt) is True

def test_ist_abgelaufen_false_before_ablauf(lock_schreiben_aktiv: WorkflowLock):
    jetzt = lock_schreiben_aktiv.ablauf_am - timedelta(seconds=1)
    assert lock_schreiben_aktiv.ist_abgelaufen(jetzt) is False

def test_ist_abgelaufen_false_just_created(lock_schreiben_aktiv: WorkflowLock, ts_fixed: datetime):
    assert lock_schreiben_aktiv.ist_abgelaufen(ts_fixed) is False


# ===========================================================================
# Section 20: WorkflowLock.pruefe_konflikt()
# ===========================================================================

def test_pruefe_konflikt_different_ressource_returns_none(ts_fixed: datetime):
    lock_a = WorkflowLock(
        lock_id="A", ressource_id="res:1", inhaber_id="u1",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    lock_b = WorkflowLock(
        lock_id="B", ressource_id="res:2", inhaber_id="u2",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    assert lock_a.pruefe_konflikt(lock_b) is None

def test_pruefe_konflikt_same_inhaber_returns_none(ts_fixed: datetime):
    lock_a = WorkflowLock(
        lock_id="A", ressource_id="res:1", inhaber_id="u1",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    lock_b = WorkflowLock(
        lock_id="B", ressource_id="res:1", inhaber_id="u1",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    assert lock_a.pruefe_konflikt(lock_b) is None

def test_pruefe_konflikt_one_not_aktiv_returns_none(ts_fixed: datetime):
    lock_a = WorkflowLock(
        lock_id="A", ressource_id="res:1", inhaber_id="u1",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    lock_b = WorkflowLock(
        lock_id="B", ressource_id="res:1", inhaber_id="u2",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.FREIGEGEBEN,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    assert lock_a.pruefe_konflikt(lock_b) is None

def test_pruefe_konflikt_schreiben_vs_schreiben(
    lock_schreiben_aktiv: WorkflowLock,
    ts_fixed: datetime,
):
    lock_b = WorkflowLock(
        lock_id="B", ressource_id="res:ABC", inhaber_id="user-C",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    result = lock_schreiben_aktiv.pruefe_konflikt(lock_b)
    assert result == KonfliktTyp.SCHREIB_SCHREIB

def test_pruefe_konflikt_schreiben_vs_lesen(
    lock_schreiben_aktiv: WorkflowLock,
    lock_lesen_aktiv: WorkflowLock,
):
    result = lock_schreiben_aktiv.pruefe_konflikt(lock_lesen_aktiv)
    assert result == KonfliktTyp.LESE_SCHREIB

def test_pruefe_konflikt_lesen_vs_schreiben(
    lock_lesen_aktiv: WorkflowLock,
    lock_schreiben_aktiv: WorkflowLock,
):
    result = lock_lesen_aktiv.pruefe_konflikt(lock_schreiben_aktiv)
    assert result == KonfliktTyp.LESE_SCHREIB

def test_pruefe_konflikt_optimistisch_same_version_no_conflict(
    lock_optimistisch_v1: WorkflowLock,
    ts_fixed: datetime,
):
    lock_b = WorkflowLock(
        lock_id="B", ressource_id="res:XYZ", inhaber_id="user-D",
        lock_typ=LockTyp.OPTIMISTISCH, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=120, erstellt_am=ts_fixed,
    )
    assert lock_optimistisch_v1.pruefe_konflikt(lock_b) is None

def test_pruefe_konflikt_optimistisch_different_version(
    lock_optimistisch_v1: WorkflowLock,
    ts_fixed: datetime,
):
    lock_b = WorkflowLock(
        lock_id="B", ressource_id="res:XYZ", inhaber_id="user-D",
        lock_typ=LockTyp.OPTIMISTISCH, status=LockStatus.AKTIV,
        version=2, ttl_sekunden=120, erstellt_am=ts_fixed,
    )
    result = lock_optimistisch_v1.pruefe_konflikt(lock_b)
    assert result == KonfliktTyp.VERSION_KONFLIKT

def test_pruefe_konflikt_lesen_vs_lesen_no_conflict(
    lock_lesen_aktiv: WorkflowLock,
    ts_fixed: datetime,
):
    lock_b = WorkflowLock(
        lock_id="B", ressource_id="res:ABC", inhaber_id="user-C",
        lock_typ=LockTyp.LESEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    assert lock_lesen_aktiv.pruefe_konflikt(lock_b) is None


# ===========================================================================
# Section 21: WorkflowLock.as_dict()
# ===========================================================================

def test_lock_as_dict_all_fields(lock_schreiben_aktiv: WorkflowLock):
    d = lock_schreiben_aktiv.as_dict()
    assert d["lock_id"] == "LK-TEST-001"
    assert d["ressource_id"] == "res:ABC"
    assert d["inhaber_id"] == "user-A"
    assert d["lock_typ"] == "SCHREIBEN"
    assert d["status"] == "AKTIV"
    assert d["version"] == 1
    assert d["ttl_sekunden"] == 300
    assert "erstellt_am" in d
    assert "ablauf_am" in d
    assert d["ist_aktiv"] is True

def test_lock_as_dict_ablauf_am_is_iso(lock_schreiben_aktiv: WorkflowLock):
    d = lock_schreiben_aktiv.as_dict()
    assert isinstance(d["ablauf_am"], str)
    assert "T" in d["ablauf_am"]

def test_lock_as_dict_lock_typ_is_string(lock_lesen_aktiv: WorkflowLock):
    d = lock_lesen_aktiv.as_dict()
    assert isinstance(d["lock_typ"], str)
    assert d["lock_typ"] == "LESEN"


# ===========================================================================
# Section 22: LockAkquisitionsErgebnis.as_dict()
# ===========================================================================

def test_akquisitions_ergebnis_as_dict_konflikt_typ_as_value(ts_fixed: datetime):
    ergebnis = LockAkquisitionsErgebnis(
        lock_id="L-1",
        ressource_id="res:1",
        inhaber_id="u1",
        lock_typ=LockTyp.SCHREIBEN,
        erfolg=False,
        konflikt_typ=KonfliktTyp.SCHREIB_SCHREIB,
        konflikt_lock_id="L-0",
        begruendung="Konflikt",
        versucht_am=ts_fixed,
    )
    d = ergebnis.as_dict()
    assert d["konflikt_typ"] == "SCHREIB_SCHREIB"
    assert d["erfolg"] is False

def test_akquisitions_ergebnis_as_dict_konflikt_typ_none_when_success(ts_fixed: datetime):
    ergebnis = LockAkquisitionsErgebnis(
        lock_id="L-2",
        ressource_id="res:2",
        inhaber_id="u2",
        lock_typ=LockTyp.LESEN,
        erfolg=True,
        versucht_am=ts_fixed,
    )
    d = ergebnis.as_dict()
    assert d["konflikt_typ"] is None
    assert d["erfolg"] is True

def test_akquisitions_ergebnis_as_dict_lock_typ_is_string(ts_fixed: datetime):
    ergebnis = LockAkquisitionsErgebnis(
        lock_id="L-3",
        ressource_id="res:3",
        inhaber_id="u3",
        lock_typ=LockTyp.OPTIMISTISCH,
        erfolg=True,
        versucht_am=ts_fixed,
    )
    d = ergebnis.as_dict()
    assert isinstance(d["lock_typ"], str)
    assert d["lock_typ"] == "OPTIMISTISCH"


# ===========================================================================
# Section 23: akquiriere_lock()
# ===========================================================================

def test_akquiriere_lock_no_existing_locks_success(ts_fixed: datetime):
    result = akquiriere_lock(
        lock_id="NEW-1",
        ressource_id="res:NEW",
        inhaber_id="u1",
        lock_typ=LockTyp.SCHREIBEN,
        version=1,
        ttl_sekunden=300,
        bestehende_locks=[],
        jetzt=ts_fixed,
    )
    assert result.erfolg is True

def test_akquiriere_lock_lesen_vs_lesen_no_conflict(ts_fixed: datetime):
    existing = WorkflowLock(
        lock_id="E-1", ressource_id="res:R", inhaber_id="user-X",
        lock_typ=LockTyp.LESEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    result = akquiriere_lock(
        lock_id="NEW-2",
        ressource_id="res:R",
        inhaber_id="user-Y",
        lock_typ=LockTyp.LESEN,
        version=1,
        ttl_sekunden=300,
        bestehende_locks=[existing],
        jetzt=ts_fixed,
    )
    assert result.erfolg is True

def test_akquiriere_lock_schreiben_vs_schreiben_conflict(ts_fixed: datetime):
    existing = WorkflowLock(
        lock_id="E-2", ressource_id="res:R", inhaber_id="user-X",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    result = akquiriere_lock(
        lock_id="NEW-3",
        ressource_id="res:R",
        inhaber_id="user-Y",
        lock_typ=LockTyp.SCHREIBEN,
        version=1,
        ttl_sekunden=300,
        bestehende_locks=[existing],
        jetzt=ts_fixed,
    )
    assert result.erfolg is False
    assert result.konflikt_typ == KonfliktTyp.SCHREIB_SCHREIB

def test_akquiriere_lock_schreiben_vs_lesen_conflict(ts_fixed: datetime):
    existing = WorkflowLock(
        lock_id="E-3", ressource_id="res:R", inhaber_id="user-X",
        lock_typ=LockTyp.LESEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    result = akquiriere_lock(
        lock_id="NEW-4",
        ressource_id="res:R",
        inhaber_id="user-Y",
        lock_typ=LockTyp.SCHREIBEN,
        version=1,
        ttl_sekunden=300,
        bestehende_locks=[existing],
        jetzt=ts_fixed,
    )
    assert result.erfolg is False
    assert result.konflikt_typ == KonfliktTyp.LESE_SCHREIB

def test_akquiriere_lock_expired_lock_ignored(ts_fixed: datetime):
    # Lock that expired 1 second before `ts_fixed`
    expired_ts = ts_fixed - timedelta(seconds=60)
    existing = WorkflowLock(
        lock_id="E-4", ressource_id="res:R", inhaber_id="user-X",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=1, erstellt_am=expired_ts,
    )
    result = akquiriere_lock(
        lock_id="NEW-5",
        ressource_id="res:R",
        inhaber_id="user-Y",
        lock_typ=LockTyp.SCHREIBEN,
        version=1,
        ttl_sekunden=300,
        bestehende_locks=[existing],
        jetzt=ts_fixed,
    )
    assert result.erfolg is True

def test_akquiriere_lock_freigegeben_lock_ignored(ts_fixed: datetime):
    existing = WorkflowLock(
        lock_id="E-5", ressource_id="res:R", inhaber_id="user-X",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.FREIGEGEBEN,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    result = akquiriere_lock(
        lock_id="NEW-6",
        ressource_id="res:R",
        inhaber_id="user-Y",
        lock_typ=LockTyp.SCHREIBEN,
        version=1,
        ttl_sekunden=300,
        bestehende_locks=[existing],
        jetzt=ts_fixed,
    )
    assert result.erfolg is True

def test_akquiriere_lock_same_inhaber_no_conflict(ts_fixed: datetime):
    existing = WorkflowLock(
        lock_id="E-6", ressource_id="res:R", inhaber_id="user-X",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    result = akquiriere_lock(
        lock_id="NEW-7",
        ressource_id="res:R",
        inhaber_id="user-X",
        lock_typ=LockTyp.SCHREIBEN,
        version=1,
        ttl_sekunden=300,
        bestehende_locks=[existing],
        jetzt=ts_fixed,
    )
    assert result.erfolg is True

def test_akquiriere_lock_result_contains_konflikt_lock_id(ts_fixed: datetime):
    existing = WorkflowLock(
        lock_id="BLOCKER-99", ressource_id="res:R", inhaber_id="user-X",
        lock_typ=LockTyp.SCHREIBEN, status=LockStatus.AKTIV,
        version=1, ttl_sekunden=300, erstellt_am=ts_fixed,
    )
    result = akquiriere_lock(
        lock_id="NEW-8",
        ressource_id="res:R",
        inhaber_id="user-Y",
        lock_typ=LockTyp.SCHREIBEN,
        version=1,
        ttl_sekunden=300,
        bestehende_locks=[existing],
        jetzt=ts_fixed,
    )
    assert result.konflikt_lock_id == "BLOCKER-99"


# ===========================================================================
# Section 24: get_default_locks()
# ===========================================================================

def test_get_default_locks_returns_5():
    locks = get_default_locks()
    assert len(locks) == 5

def test_get_default_locks_lk001_schreiben_aktiv():
    locks = get_default_locks()
    lk001 = next(l for l in locks if l.lock_id == "LK-001")
    assert lk001.lock_typ == LockTyp.SCHREIBEN
    assert lk001.status == LockStatus.AKTIV

def test_get_default_locks_lk002_lk003_lesen_same_resource():
    locks = get_default_locks()
    lk002 = next(l for l in locks if l.lock_id == "LK-002")
    lk003 = next(l for l in locks if l.lock_id == "LK-003")
    assert lk002.lock_typ == LockTyp.LESEN
    assert lk003.lock_typ == LockTyp.LESEN
    assert lk002.ressource_id == lk003.ressource_id
    assert lk002.status == LockStatus.AKTIV
    assert lk003.status == LockStatus.AKTIV

def test_get_default_locks_lk004_freigegeben():
    locks = get_default_locks()
    lk004 = next(l for l in locks if l.lock_id == "LK-004")
    assert lk004.status == LockStatus.FREIGEGEBEN

def test_get_default_locks_lk005_abgelaufen():
    locks = get_default_locks()
    lk005 = next(l for l in locks if l.lock_id == "LK-005")
    assert lk005.status == LockStatus.ABGELAUFEN

def test_get_default_locks_custom_jetzt():
    custom_ts = datetime(2026, 1, 1, 8, 0, 0)
    locks = get_default_locks(jetzt=custom_ts)
    for lock in locks:
        assert lock.erstellt_am == custom_ts

def test_get_default_locks_ablauf_am_computed():
    locks = get_default_locks()
    lk001 = next(l for l in locks if l.lock_id == "LK-001")
    expected = lk001.erstellt_am + timedelta(seconds=lk001.ttl_sekunden)
    assert lk001.ablauf_am == expected
