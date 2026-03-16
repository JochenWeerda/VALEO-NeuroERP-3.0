"""
Wave 46 — Process Quarantine Contracts & Workflow ACL Contracts
60 deterministic unit tests (no DB, no server, no mocking).
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.core.process_quarantine_contracts import (
    QuarantaeneGrund,
    QuarantaeneStatus,
    RetryStrategie,
    QuarantaeneEintrag,
    QuarantaeneStatistik,
    berechne_quarantaene_statistik,
    get_default_quarantaene_eintraege,
)
from app.core.workflow_acl_contracts import (
    AclAktion,
    AclEffekt,
    AclVererbung,
    AclRegel,
    AclEntscheidung,
    pruefe_acl,
    get_default_acl_regeln,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASIS = datetime(2026, 3, 15, 8, 0, 0)
_JETZT = datetime(2026, 3, 16, 10, 0, 0)


def _eintrag(
    eintrag_id="QE-X",
    status=QuarantaeneStatus.IN_QUARANTAENE,
    strategie=RetryStrategie.EXPONENTIELL,
    versuch=1,
    max_v=5,
    tenant="T-001",
    grund=QuarantaeneGrund.DATENFEHLER,
    fehlermeldung="",
) -> QuarantaeneEintrag:
    return QuarantaeneEintrag(
        eintrag_id=eintrag_id,
        workflow_instanz_id="WF-999",
        tenant_id=tenant,
        grund=grund,
        status=status,
        retry_strategie=strategie,
        versuch_anzahl=versuch,
        max_versuche=max_v,
        eingestellt_am=_BASIS,
        fehlermeldung=fehlermeldung,
    )


# ===========================================================================
# MODULE 1 — process_quarantine_contracts  (30 tests)
# ===========================================================================

# --- Enum membership ---

def test_quarantaene_grund_values():
    expected = {"VALIDIERUNGSFEHLER", "TIMEOUT", "KAPAZITAET_ERSCHOEPFT",
                "SICHERHEITSVERSTOS", "DATENFEHLER", "MANUELL"}
    assert {g.value for g in QuarantaeneGrund} == expected


def test_retry_strategie_values():
    expected = {"SOFORT", "EXPONENTIELL", "FESTER_INTERVALL", "KEIN_RETRY"}
    assert {s.value for s in RetryStrategie} == expected


def test_quarantaene_status_values():
    expected = {"IN_QUARANTAENE", "FREIGEGEBEN", "ABGEBROCHEN", "DEAD_LETTER"}
    assert {s.value for s in QuarantaeneStatus} == expected


# --- kann_wiederholt_werden ---

def test_kann_wiederholt_werden_true_exponentiell():
    e = _eintrag(status=QuarantaeneStatus.IN_QUARANTAENE, strategie=RetryStrategie.EXPONENTIELL,
                 versuch=1, max_v=5)
    assert e.kann_wiederholt_werden is True


def test_kann_wiederholt_werden_true_fester_intervall():
    e = _eintrag(status=QuarantaeneStatus.IN_QUARANTAENE, strategie=RetryStrategie.FESTER_INTERVALL,
                 versuch=2, max_v=3)
    assert e.kann_wiederholt_werden is True


def test_kann_wiederholt_werden_false_kein_retry():
    e = _eintrag(status=QuarantaeneStatus.IN_QUARANTAENE, strategie=RetryStrategie.KEIN_RETRY,
                 versuch=0, max_v=0)
    assert e.kann_wiederholt_werden is False


def test_kann_wiederholt_werden_false_dead_letter_status():
    e = _eintrag(status=QuarantaeneStatus.DEAD_LETTER, strategie=RetryStrategie.EXPONENTIELL,
                 versuch=5, max_v=5)
    assert e.kann_wiederholt_werden is False


def test_kann_wiederholt_werden_false_freigegeben():
    e = _eintrag(status=QuarantaeneStatus.FREIGEGEBEN, strategie=RetryStrategie.SOFORT,
                 versuch=1, max_v=3)
    assert e.kann_wiederholt_werden is False


def test_kann_wiederholt_werden_false_versuche_erschoepft():
    e = _eintrag(status=QuarantaeneStatus.IN_QUARANTAENE, strategie=RetryStrategie.EXPONENTIELL,
                 versuch=5, max_v=5)
    assert e.kann_wiederholt_werden is False


# --- ist_dead_letter ---

def test_ist_dead_letter_by_status():
    e = _eintrag(status=QuarantaeneStatus.DEAD_LETTER, versuch=5, max_v=5)
    assert e.ist_dead_letter is True


def test_ist_dead_letter_by_max_versuche_erreicht():
    e = _eintrag(status=QuarantaeneStatus.IN_QUARANTAENE, versuch=5, max_v=5)
    assert e.ist_dead_letter is True


def test_ist_dead_letter_false_versuche_nicht_erschoepft():
    e = _eintrag(status=QuarantaeneStatus.IN_QUARANTAENE, versuch=1, max_v=5)
    assert e.ist_dead_letter is False


def test_ist_dead_letter_qe005_abgebrochen_kein_retry():
    # versuch=0, max=0 → 0 >= 0 → ist_dead_letter True
    e = _eintrag(status=QuarantaeneStatus.ABGEBROCHEN, strategie=RetryStrategie.KEIN_RETRY,
                 versuch=0, max_v=0)
    assert e.ist_dead_letter is True


# --- berechne_naechsten_versuch ---

def test_naechster_versuch_kein_retry_returns_none():
    e = _eintrag(strategie=RetryStrategie.KEIN_RETRY)
    assert e.berechne_naechsten_versuch(jetzt=_JETZT) is None


def test_naechster_versuch_sofort_returns_jetzt():
    e = _eintrag(strategie=RetryStrategie.SOFORT)
    result = e.berechne_naechsten_versuch(basis_intervall_sekunden=60.0, jetzt=_JETZT)
    assert result == _JETZT


def test_naechster_versuch_fester_intervall_60s():
    e = _eintrag(strategie=RetryStrategie.FESTER_INTERVALL)
    result = e.berechne_naechsten_versuch(basis_intervall_sekunden=60.0, jetzt=_JETZT)
    assert result == _JETZT + timedelta(seconds=60)


def test_naechster_versuch_fester_intervall_custom():
    e = _eintrag(strategie=RetryStrategie.FESTER_INTERVALL)
    result = e.berechne_naechsten_versuch(basis_intervall_sekunden=300.0, jetzt=_JETZT)
    assert result == _JETZT + timedelta(seconds=300)


def test_naechster_versuch_exponentiell_versuch1():
    # versuch_anzahl=1 → 60 * 2^1 = 120s
    e = _eintrag(strategie=RetryStrategie.EXPONENTIELL, versuch=1)
    result = e.berechne_naechsten_versuch(basis_intervall_sekunden=60.0, jetzt=_JETZT)
    assert result == _JETZT + timedelta(seconds=120)


def test_naechster_versuch_exponentiell_versuch2():
    # versuch_anzahl=2 → 60 * 2^2 = 240s
    e = _eintrag(strategie=RetryStrategie.EXPONENTIELL, versuch=2)
    result = e.berechne_naechsten_versuch(basis_intervall_sekunden=60.0, jetzt=_JETZT)
    assert result == _JETZT + timedelta(seconds=240)


def test_naechster_versuch_exponentiell_versuch0():
    # versuch_anzahl=0 → 60 * 2^0 = 60s
    e = _eintrag(strategie=RetryStrategie.EXPONENTIELL, versuch=0)
    result = e.berechne_naechsten_versuch(basis_intervall_sekunden=60.0, jetzt=_JETZT)
    assert result == _JETZT + timedelta(seconds=60)


# --- as_dict ---

def test_as_dict_includes_kann_wiederholt_werden():
    e = _eintrag()
    d = e.as_dict()
    assert "kann_wiederholt_werden" in d
    assert d["kann_wiederholt_werden"] == e.kann_wiederholt_werden


def test_as_dict_includes_ist_dead_letter():
    e = _eintrag()
    d = e.as_dict()
    assert "ist_dead_letter" in d


def test_as_dict_letzter_versuch_none():
    e = _eintrag()
    d = e.as_dict()
    assert d["letzter_versuch"] is None


def test_as_dict_letzter_versuch_iso_string():
    e = _eintrag()
    e.letzter_versuch = _JETZT
    d = e.as_dict()
    assert d["letzter_versuch"] == _JETZT.isoformat()


# --- QuarantaeneStatistik ---

def test_statistik_gesamt():
    s = QuarantaeneStatistik("T-001", in_quarantaene=2, freigegeben=1, abgebrochen=1, dead_letter=1)
    assert s.gesamt == 5


def test_statistik_dead_letter_rate_pct():
    s = QuarantaeneStatistik("T-001", in_quarantaene=2, freigegeben=1, abgebrochen=1, dead_letter=1)
    assert s.dead_letter_rate_pct == 20.0


def test_statistik_dead_letter_rate_zero_wenn_gesamt_null():
    s = QuarantaeneStatistik("T-001", in_quarantaene=0, freigegeben=0, abgebrochen=0, dead_letter=0)
    assert s.dead_letter_rate_pct == 0.0


def test_statistik_as_dict_keys():
    s = QuarantaeneStatistik("T-001", in_quarantaene=2, freigegeben=1, abgebrochen=1, dead_letter=1)
    d = s.as_dict()
    for key in ("tenant_id", "in_quarantaene", "freigegeben", "abgebrochen", "dead_letter",
                "gesamt", "dead_letter_rate_pct"):
        assert key in d


# --- berechne_quarantaene_statistik ---

def test_berechne_statistik_default_eintraege():
    eintraege = get_default_quarantaene_eintraege("TENANT-001")
    stat = berechne_quarantaene_statistik(eintraege, "TENANT-001")
    assert stat.gesamt == 5
    assert stat.in_quarantaene == 2
    assert stat.freigegeben == 1
    assert stat.abgebrochen == 1
    assert stat.dead_letter == 1


def test_berechne_statistik_filtert_nach_tenant():
    e1 = _eintrag(tenant="T-A", status=QuarantaeneStatus.IN_QUARANTAENE)
    e2 = _eintrag(tenant="T-B", status=QuarantaeneStatus.FREIGEGEBEN)
    stat = berechne_quarantaene_statistik([e1, e2], "T-A")
    assert stat.gesamt == 1
    assert stat.in_quarantaene == 1


def test_berechne_statistik_leer():
    stat = berechne_quarantaene_statistik([], "T-001")
    assert stat.gesamt == 0
    assert stat.dead_letter_rate_pct == 0.0


# --- get_default_quarantaene_eintraege ---

def test_default_eintraege_laenge():
    eintraege = get_default_quarantaene_eintraege()
    assert len(eintraege) == 5


def test_default_eintraege_qe001_kann_wiederholt():
    eintraege = get_default_quarantaene_eintraege()
    qe001 = next(e for e in eintraege if e.eintrag_id == "QE-001")
    assert qe001.kann_wiederholt_werden is True


def test_default_eintraege_qe002_kann_wiederholt():
    eintraege = get_default_quarantaene_eintraege()
    qe002 = next(e for e in eintraege if e.eintrag_id == "QE-002")
    assert qe002.kann_wiederholt_werden is True


def test_default_eintraege_qe003_ist_dead_letter():
    eintraege = get_default_quarantaene_eintraege()
    qe003 = next(e for e in eintraege if e.eintrag_id == "QE-003")
    assert qe003.ist_dead_letter is True


def test_default_eintraege_qe005_kein_retry():
    eintraege = get_default_quarantaene_eintraege()
    qe005 = next(e for e in eintraege if e.eintrag_id == "QE-005")
    assert qe005.kann_wiederholt_werden is False


def test_default_eintraege_tenant_param():
    eintraege = get_default_quarantaene_eintraege(tenant_id="ACME")
    assert all(e.tenant_id == "ACME" for e in eintraege)


# ===========================================================================
# MODULE 2 — workflow_acl_contracts  (30 tests)
# ===========================================================================

_TS = datetime(2026, 3, 16, 12, 0, 0)


def _regel(
    regel_id="AR-X",
    ressource="*",
    subjekt="*",
    aktion=AclAktion.LESEN,
    effekt=AclEffekt.ERLAUBEN,
    prio=50,
    vererbung=AclVererbung.KEINE,
    beschreibung="",
) -> AclRegel:
    return AclRegel(
        regel_id=regel_id,
        ressource_id=ressource,
        subjekt_id=subjekt,
        aktion=aktion,
        effekt=effekt,
        prioritaet=prio,
        vererbung=vererbung,
        beschreibung=beschreibung,
    )


# --- Enum membership ---

def test_acl_aktion_values():
    expected = {"LESEN", "SCHREIBEN", "AUSFUEHREN", "FREIGEBEN", "ADMINISTRIEREN"}
    assert {a.value for a in AclAktion} == expected


def test_acl_effekt_values():
    assert {e.value for e in AclEffekt} == {"ERLAUBEN", "VERWEIGERN"}


def test_acl_vererbung_values():
    assert {v.value for v in AclVererbung} == {"KEINE", "VON_ELTERN", "AN_KINDER"}


# --- AclRegel properties ---

def test_acl_regel_ist_erlaubnis_true():
    r = _regel(effekt=AclEffekt.ERLAUBEN)
    assert r.ist_erlaubnis is True
    assert r.ist_verweigerung is False


def test_acl_regel_ist_verweigerung_true():
    r = _regel(effekt=AclEffekt.VERWEIGERN)
    assert r.ist_verweigerung is True
    assert r.ist_erlaubnis is False


def test_acl_regel_trifft_zu_exakt():
    r = _regel(ressource="workflow:kontrakt", subjekt="user1", aktion=AclAktion.SCHREIBEN)
    assert r._trifft_zu("workflow:kontrakt", "user1", AclAktion.SCHREIBEN) is True


def test_acl_regel_trifft_zu_wildcard_ressource():
    r = _regel(ressource="*", subjekt="user1", aktion=AclAktion.LESEN)
    assert r._trifft_zu("any:ressource", "user1", AclAktion.LESEN) is True


def test_acl_regel_trifft_zu_wildcard_subjekt():
    r = _regel(ressource="workflow:x", subjekt="*", aktion=AclAktion.LESEN)
    assert r._trifft_zu("workflow:x", "anybody", AclAktion.LESEN) is True


def test_acl_regel_trifft_zu_false_falsche_aktion():
    r = _regel(ressource="*", subjekt="*", aktion=AclAktion.LESEN)
    assert r._trifft_zu("res", "sub", AclAktion.SCHREIBEN) is False


def test_acl_regel_trifft_zu_false_falsche_ressource():
    r = _regel(ressource="workflow:a", subjekt="*", aktion=AclAktion.LESEN)
    assert r._trifft_zu("workflow:b", "*", AclAktion.LESEN) is False


def test_acl_regel_as_dict_keys():
    r = _regel()
    d = r.as_dict()
    for key in ("regel_id", "ressource_id", "subjekt_id", "aktion", "effekt",
                "prioritaet", "ist_erlaubnis", "ist_verweigerung"):
        assert key in d


def test_acl_regel_as_dict_aktion_string():
    r = _regel(aktion=AclAktion.AUSFUEHREN)
    assert r.as_dict()["aktion"] == "AUSFUEHREN"


# --- AclEntscheidung ---

def test_acl_entscheidung_ist_erlaubt_true():
    e = AclEntscheidung(
        ressource_id="r", subjekt_id="s", aktion=AclAktion.LESEN,
        effekt=AclEffekt.ERLAUBEN, entschieden_am=_TS
    )
    assert e.ist_erlaubt is True


def test_acl_entscheidung_ist_erlaubt_false():
    e = AclEntscheidung(
        ressource_id="r", subjekt_id="s", aktion=AclAktion.LESEN,
        effekt=AclEffekt.VERWEIGERN, entschieden_am=_TS
    )
    assert e.ist_erlaubt is False


def test_acl_entscheidung_as_dict_includes_ist_erlaubt():
    e = AclEntscheidung(
        ressource_id="r", subjekt_id="s", aktion=AclAktion.LESEN,
        effekt=AclEffekt.ERLAUBEN, entschieden_am=_TS
    )
    d = e.as_dict()
    assert "ist_erlaubt" in d
    assert d["effekt"] == "ERLAUBEN"


# --- pruefe_acl ---

def test_pruefe_acl_default_deny_kein_match():
    regeln = get_default_acl_regeln()
    entscheidung = pruefe_acl(
        "workflow:unbekannt", "unbekannter_user", AclAktion.AUSFUEHREN,
        regeln, entschieden_am=_TS
    )
    assert entscheidung.effekt == AclEffekt.VERWEIGERN
    assert entscheidung.angewandte_regel_id == ""


def test_pruefe_acl_admin_administrieren():
    regeln = get_default_acl_regeln()
    e = pruefe_acl("workflow:beliebig", "admin", AclAktion.ADMINISTRIEREN,
                   regeln, entschieden_am=_TS)
    assert e.ist_erlaubt is True
    assert e.angewandte_regel_id == "AR-001"


def test_pruefe_acl_sachbearbeiter_ausfuehren_kontrakt():
    regeln = get_default_acl_regeln()
    e = pruefe_acl("workflow:kontrakt_annahme", "sachbearbeiter",
                   AclAktion.AUSFUEHREN, regeln, entschieden_am=_TS)
    assert e.ist_erlaubt is True
    assert e.angewandte_regel_id == "AR-002"


def test_pruefe_acl_sachbearbeiter_freigeben_settlement_verweigert():
    regeln = get_default_acl_regeln()
    e = pruefe_acl("workflow:settlement_freigabe", "sachbearbeiter",
                   AclAktion.FREIGEBEN, regeln, entschieden_am=_TS)
    assert e.ist_erlaubt is False
    assert e.angewandte_regel_id == "AR-003"


def test_pruefe_acl_leiter_freigeben_settlement_erlaubt():
    regeln = get_default_acl_regeln()
    e = pruefe_acl("workflow:settlement_freigabe", "leiter",
                   AclAktion.FREIGEBEN, regeln, entschieden_am=_TS)
    assert e.ist_erlaubt is True
    assert e.angewandte_regel_id == "AR-004"


def test_pruefe_acl_alle_lesen_erlaubt():
    regeln = get_default_acl_regeln()
    e = pruefe_acl("workflow:irgendwas", "zufaellig_user",
                   AclAktion.LESEN, regeln, entschieden_am=_TS)
    assert e.ist_erlaubt is True
    assert e.angewandte_regel_id == "AR-005"


def test_pruefe_acl_extern_schreiben_compliance_verweigert():
    regeln = get_default_acl_regeln()
    e = pruefe_acl("workflow:compliance_pruefung", "extern",
                   AclAktion.SCHREIBEN, regeln, entschieden_am=_TS)
    assert e.ist_erlaubt is False
    assert e.angewandte_regel_id == "AR-006"


def test_pruefe_acl_deny_vor_erlauben_gleiche_prioritaet():
    """VERWEIGERN schlägt ERLAUBEN bei gleicher Priorität."""
    regeln = [
        _regel("R-DENY", ressource="res", subjekt="user", aktion=AclAktion.SCHREIBEN,
               effekt=AclEffekt.VERWEIGERN, prio=5),
        _regel("R-ALLOW", ressource="res", subjekt="user", aktion=AclAktion.SCHREIBEN,
               effekt=AclEffekt.ERLAUBEN, prio=5),
    ]
    e = pruefe_acl("res", "user", AclAktion.SCHREIBEN, regeln, entschieden_am=_TS)
    assert e.ist_erlaubt is False
    assert e.angewandte_regel_id == "R-DENY"


def test_pruefe_acl_niedrigere_prioritaet_gewinnt():
    """Niedrigere Prioritätszahl gewinnt."""
    regeln = [
        _regel("R-HIGH", ressource="res", subjekt="user", aktion=AclAktion.LESEN,
               effekt=AclEffekt.VERWEIGERN, prio=10),
        _regel("R-LOW", ressource="res", subjekt="user", aktion=AclAktion.LESEN,
               effekt=AclEffekt.ERLAUBEN, prio=1),
    ]
    e = pruefe_acl("res", "user", AclAktion.LESEN, regeln, entschieden_am=_TS)
    assert e.ist_erlaubt is True
    assert e.angewandte_regel_id == "R-LOW"


def test_pruefe_acl_entschieden_am_wird_gesetzt():
    regeln = get_default_acl_regeln()
    e = pruefe_acl("workflow:kontrakt_annahme", "sachbearbeiter",
                   AclAktion.AUSFUEHREN, regeln, entschieden_am=_TS)
    assert e.entschieden_am == _TS


# --- get_default_acl_regeln ---

def test_default_regeln_laenge():
    regeln = get_default_acl_regeln()
    assert len(regeln) == 6


def test_default_regeln_ids():
    ids = {r.regel_id for r in get_default_acl_regeln()}
    assert ids == {"AR-001", "AR-002", "AR-003", "AR-004", "AR-005", "AR-006"}


def test_default_regeln_ar001_wildcard_ressource():
    regeln = get_default_acl_regeln()
    ar001 = next(r for r in regeln if r.regel_id == "AR-001")
    assert ar001.ressource_id == "*"
    assert ar001.subjekt_id == "admin"
    assert ar001.effekt == AclEffekt.ERLAUBEN
    assert ar001.prioritaet == 1


def test_default_regeln_ar005_wildcard_alle():
    regeln = get_default_acl_regeln()
    ar005 = next(r for r in regeln if r.regel_id == "AR-005")
    assert ar005.ressource_id == "*"
    assert ar005.subjekt_id == "*"
    assert ar005.aktion == AclAktion.LESEN
    assert ar005.prioritaet == 100


def test_default_regeln_ar003_verweigern():
    regeln = get_default_acl_regeln()
    ar003 = next(r for r in regeln if r.regel_id == "AR-003")
    assert ar003.effekt == AclEffekt.VERWEIGERN
    assert ar003.ist_verweigerung is True


def test_default_regeln_ar006_verweigern():
    regeln = get_default_acl_regeln()
    ar006 = next(r for r in regeln if r.regel_id == "AR-006")
    assert ar006.effekt == AclEffekt.VERWEIGERN
    assert ar006.subjekt_id == "extern"
    assert ar006.aktion == AclAktion.SCHREIBEN
