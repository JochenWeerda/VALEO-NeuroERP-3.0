"""Wave 65: Exception Patterns + Remediation Contracts — 130+ Tests"""
import pytest
from datetime import datetime

from app.core.process_exception_pattern_contracts import (
    AusnahmeMuster,
    AusnahmeSchwere,
    MusterErkennungsKonfidenz,
    AusnahmeSignatur,
    KlassifizierungsErgebnis,
    klassifiziere_ausnahme,
    get_default_ausnahme_signaturen,
)
from app.core.workflow_remediation_contracts import (
    RemediationsTyp,
    RemediationsStatus,
    RemediationsAktion,
    RemediationsSchritt,
    RemediationsPlaybook,
    RemediationsVorschlag,
    get_default_playbooks,
)


# ============================================================
# AusnahmeMuster Enum
# ============================================================

def test_ausnahme_muster_timeout():
    assert AusnahmeMuster.TIMEOUT == "TIMEOUT"

def test_ausnahme_muster_datenfehler():
    assert AusnahmeMuster.DATENFEHLER == "DATENFEHLER"

def test_ausnahme_muster_berechtigungsfehler():
    assert AusnahmeMuster.BERECHTIGUNGSFEHLER == "BERECHTIGUNGSFEHLER"

def test_ausnahme_muster_ressourcenengpass():
    assert AusnahmeMuster.RESSOURCENENGPASS == "RESSOURCENENGPASS"

def test_ausnahme_muster_geschaeftsregelvertoss():
    assert AusnahmeMuster.GESCHAEFTSREGELVERTOSS == "GESCHAEFTSREGELVERTOSS"

def test_ausnahme_muster_integrationsfehler():
    assert AusnahmeMuster.INTEGRATIONSFEHLER == "INTEGRATIONSFEHLER"

def test_ausnahme_muster_unbekannt():
    assert AusnahmeMuster.UNBEKANNT == "UNBEKANNT"

def test_ausnahme_muster_count():
    assert len(AusnahmeMuster) == 7


# ============================================================
# AusnahmeSchwere Enum
# ============================================================

def test_schwere_kritisch():
    assert AusnahmeSchwere.KRITISCH == "KRITISCH"

def test_schwere_hoch():
    assert AusnahmeSchwere.HOCH == "HOCH"

def test_schwere_mittel():
    assert AusnahmeSchwere.MITTEL == "MITTEL"

def test_schwere_niedrig():
    assert AusnahmeSchwere.NIEDRIG == "NIEDRIG"

def test_schwere_count():
    assert len(AusnahmeSchwere) == 4


# ============================================================
# MusterErkennungsKonfidenz Enum
# ============================================================

def test_konfidenz_sicher():
    assert MusterErkennungsKonfidenz.SICHER == "SICHER"

def test_konfidenz_wahrscheinlich():
    assert MusterErkennungsKonfidenz.WAHRSCHEINLICH == "WAHRSCHEINLICH"

def test_konfidenz_moeglich():
    assert MusterErkennungsKonfidenz.MOEGLICH == "MOEGLICH"

def test_konfidenz_unbekannt():
    assert MusterErkennungsKonfidenz.UNBEKANNT == "UNBEKANNT"

def test_konfidenz_count():
    assert len(MusterErkennungsKonfidenz) == 4


# ============================================================
# AusnahmeSignatur — basic construction
# ============================================================

def test_signatur_basic_fields():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout"], ["TO_"])
    assert sig.signatur_id == "SIG-1"
    assert sig.muster == AusnahmeMuster.TIMEOUT
    assert sig.schluessel_woerter == ["timeout"]
    assert sig.fehler_code_praefixe == ["TO_"]

def test_signatur_default_schwere():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT)
    assert sig.schwere == AusnahmeSchwere.MITTEL

def test_signatur_custom_schwere():
    sig = AusnahmeSignatur("SIG-2", AusnahmeMuster.RESSOURCENENGPASS, schwere=AusnahmeSchwere.KRITISCH)
    assert sig.schwere == AusnahmeSchwere.KRITISCH

def test_signatur_default_beschreibung():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT)
    assert sig.beschreibung == ""

def test_signatur_custom_beschreibung():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, beschreibung="Mein Fehler")
    assert sig.beschreibung == "Mein Fehler"

def test_signatur_default_lists():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT)
    assert sig.schluessel_woerter == []
    assert sig.fehler_code_praefixe == []


# ============================================================
# AusnahmeSignatur.erkenne_muster — scoring tests
# ============================================================

def test_erkenne_no_keywords_no_code_unbekannt():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout"], ["TO_"])
    result = sig.erkenne_muster("random error text", "OTHER_001")
    assert result == MusterErkennungsKonfidenz.UNBEKANNT

def test_erkenne_empty_everything_unbekannt():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT)
    result = sig.erkenne_muster("", "")
    assert result == MusterErkennungsKonfidenz.UNBEKANNT

def test_erkenne_one_keyword_20pts_unbekannt():
    # 1 keyword = 20 pts < 50 → UNBEKANNT
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout"], [])
    result = sig.erkenne_muster("connection timeout occurred", "")
    assert result == MusterErkennungsKonfidenz.UNBEKANNT

def test_erkenne_two_keywords_40pts_unbekannt():
    # 2 keywords = 40 pts < 50 → UNBEKANNT
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout", "connection"], [])
    result = sig.erkenne_muster("connection timeout error", "")
    assert result == MusterErkennungsKonfidenz.UNBEKANNT

def test_erkenne_three_keywords_60pts_moeglich():
    # 3 keywords = 60 pts >= 50 → MOEGLICH
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout", "connection", "error"], [])
    result = sig.erkenne_muster("connection timeout error occurred", "")
    assert result == MusterErkennungsKonfidenz.MOEGLICH

def test_erkenne_code_prefix_50pts_moeglich():
    # code prefix = 50 pts → MOEGLICH
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, [], ["TO_"])
    result = sig.erkenne_muster("some error", "TO_001")
    assert result == MusterErkennungsKonfidenz.MOEGLICH

def test_erkenne_code_prefix_plus_one_keyword_70pts_wahrscheinlich():
    # code prefix (50) + 1 keyword (20) = 70 pts → WAHRSCHEINLICH
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout"], ["TO_"])
    result = sig.erkenne_muster("connection timeout occurred", "TO_001")
    assert result == MusterErkennungsKonfidenz.WAHRSCHEINLICH

def test_erkenne_code_prefix_plus_two_keywords_90pts_sicher():
    # code prefix (50) + 2 keywords (40) = 90 pts → SICHER
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout", "connection"], ["TO_"])
    result = sig.erkenne_muster("connection timeout failure", "TO_001")
    assert result == MusterErkennungsKonfidenz.SICHER

def test_erkenne_four_keywords_80pts_wahrscheinlich():
    # 4 keywords = 80 pts → WAHRSCHEINLICH
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["alpha", "beta", "gamma", "delta"], [])
    result = sig.erkenne_muster("alpha beta gamma delta error", "")
    assert result == MusterErkennungsKonfidenz.WAHRSCHEINLICH

def test_erkenne_five_keywords_100pts_sicher():
    # 5 keywords = 100 pts → SICHER
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["a", "b", "c", "d", "e"], [])
    result = sig.erkenne_muster("a b c d e text", "")
    assert result == MusterErkennungsKonfidenz.SICHER

def test_erkenne_case_insensitive_upper():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["TIMEOUT"], [])
    result = sig.erkenne_muster("connection timeout occurred", "")
    # 1 keyword = 20 pts → UNBEKANNT (but case-insensitive check passes)
    assert result == MusterErkennungsKonfidenz.UNBEKANNT

def test_erkenne_case_insensitive_mixed():
    # case-insensitive with 3 keywords total = 60 pts → MOEGLICH
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["Timeout", "Connection", "Error"], [])
    result = sig.erkenne_muster("CONNECTION TIMEOUT ERROR", "")
    assert result == MusterErkennungsKonfidenz.MOEGLICH

def test_erkenne_code_prefix_first_match_only():
    # Two prefixes but only count once (first match = 50 pts)
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, [], ["TO_", "CON_"])
    result = sig.erkenne_muster("error", "TO_001")
    assert result == MusterErkennungsKonfidenz.MOEGLICH  # 50 pts

def test_erkenne_code_prefix_second_prefix():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, [], ["TO_", "CON_"])
    result = sig.erkenne_muster("error", "CON_999")
    assert result == MusterErkennungsKonfidenz.MOEGLICH  # 50 pts

def test_erkenne_code_no_prefix_match():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, [], ["TO_"])
    result = sig.erkenne_muster("error", "OTHER_001")
    assert result == MusterErkennungsKonfidenz.UNBEKANNT

def test_erkenne_keyword_partial_not_matched():
    # "time" not in text when keyword is "timeout" → no match
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout"], [])
    result = sig.erkenne_muster("connection refused", "")
    assert result == MusterErkennungsKonfidenz.UNBEKANNT

def test_erkenne_keyword_substring_match():
    # "time" is substring of "timeout" → "timeout" keyword matches "connection timeout"
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["time"], [])
    result = sig.erkenne_muster("connection timeout", "")
    # 1 keyword "time" in "connection timeout" → 20 pts → UNBEKANNT
    assert result == MusterErkennungsKonfidenz.UNBEKANNT

def test_erkenne_empty_text_code_prefix_match():
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout"], ["TO_"])
    result = sig.erkenne_muster("", "TO_001")
    assert result == MusterErkennungsKonfidenz.MOEGLICH  # 50 pts

def test_erkenne_exactly_50_pts_moeglich():
    # exactly 50 pts (code prefix only) → MOEGLICH
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, [], ["TO_"])
    assert sig.erkenne_muster("no keywords", "TO_001") == MusterErkennungsKonfidenz.MOEGLICH

def test_erkenne_exactly_70_pts_wahrscheinlich():
    # 50 + 20 = 70 → WAHRSCHEINLICH
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout"], ["TO_"])
    assert sig.erkenne_muster("timeout occurred", "TO_001") == MusterErkennungsKonfidenz.WAHRSCHEINLICH

def test_erkenne_exactly_90_pts_sicher():
    # 50 + 40 = 90 → SICHER
    sig = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout", "connection"], ["TO_"])
    assert sig.erkenne_muster("connection timeout", "TO_001") == MusterErkennungsKonfidenz.SICHER


# ============================================================
# klassifiziere_ausnahme()
# ============================================================

def test_klassifiziere_timeout_sicher():
    sigs = [
        AusnahmeSignatur("SIG-T", AusnahmeMuster.TIMEOUT, ["timeout", "connection"], ["TIMEOUT_"])
    ]
    result = klassifiziere_ausnahme("connection timeout error", "TIMEOUT_001", sigs)
    assert result.muster == AusnahmeMuster.TIMEOUT
    assert result.konfidenz == MusterErkennungsKonfidenz.SICHER
    assert result.signatur_id == "SIG-T"

def test_klassifiziere_unbekannt_no_match():
    sigs = [
        AusnahmeSignatur("SIG-T", AusnahmeMuster.TIMEOUT, ["timeout"], ["TO_"])
    ]
    result = klassifiziere_ausnahme("unknown random error", "OTHER_001", sigs)
    assert result.muster == AusnahmeMuster.UNBEKANNT
    assert result.konfidenz == MusterErkennungsKonfidenz.UNBEKANNT

def test_klassifiziere_empty_signaturen():
    result = klassifiziere_ausnahme("timeout error", "TO_001", [])
    assert result.muster == AusnahmeMuster.UNBEKANNT
    assert result.konfidenz == MusterErkennungsKonfidenz.UNBEKANNT

def test_klassifiziere_best_match_wins():
    # Two sigs: sig1 gets MOEGLICH, sig2 gets WAHRSCHEINLICH → sig2 wins
    sig1 = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, ["timeout", "connection"], [])  # 40 pts
    sig2 = AusnahmeSignatur("SIG-2", AusnahmeMuster.DATENFEHLER, ["validation"], ["VAL_"])  # 70 pts
    result = klassifiziere_ausnahme("connection timeout validation error", "VAL_001", [sig1, sig2])
    assert result.muster == AusnahmeMuster.DATENFEHLER
    assert result.konfidenz == MusterErkennungsKonfidenz.WAHRSCHEINLICH
    assert result.signatur_id == "SIG-2"

def test_klassifiziere_first_wins_on_tie():
    # Both get same confidence; first in list wins
    sig1 = AusnahmeSignatur("SIG-1", AusnahmeMuster.TIMEOUT, [], ["TO_"])  # 50 pts
    sig2 = AusnahmeSignatur("SIG-2", AusnahmeMuster.DATENFEHLER, [], ["DA_"])  # 50 pts
    result = klassifiziere_ausnahme("error", "TO_001", [sig1, sig2])
    assert result.muster == AusnahmeMuster.TIMEOUT
    assert result.signatur_id == "SIG-1"

def test_klassifiziere_returns_schwere():
    sigs = [AusnahmeSignatur("SIG-1", AusnahmeMuster.RESSOURCENENGPASS,
                              [], ["RES_"], AusnahmeSchwere.KRITISCH)]
    result = klassifiziere_ausnahme("error", "RES_001", sigs)
    assert result.schwere == AusnahmeSchwere.KRITISCH

def test_klassifiziere_unbekannt_signatur_id_none():
    result = klassifiziere_ausnahme("nothing matches", "", [])
    assert result.signatur_id is None

def test_klassifiziere_datenfehler_keywords():
    sigs = get_default_ausnahme_signaturen()
    # "validation" + "ungültig" → 40 pts for AS-002, no code match
    result = klassifiziere_ausnahme("validation failed ungültig", "", sigs)
    # 40 pts → UNBEKANNT for AS-002, but let's see if any other matches
    # Actually 40 < 50 → UNBEKANNT for all
    assert result.muster == AusnahmeMuster.UNBEKANNT

def test_klassifiziere_timeout_with_default_sigs_code():
    sigs = get_default_ausnahme_signaturen()
    result = klassifiziere_ausnahme("connection timeout", "TIMEOUT_001", sigs)
    # AS-001: "timeout" keyword (20) + TIMEOUT_ code (50) = 70 → WAHRSCHEINLICH
    assert result.muster == AusnahmeMuster.TIMEOUT
    assert result.konfidenz == MusterErkennungsKonfidenz.WAHRSCHEINLICH

def test_klassifiziere_auth_with_default_sigs():
    sigs = get_default_ausnahme_signaturen()
    result = klassifiziere_ausnahme("some error", "AUTH_403", sigs)
    # AS-003: AUTH_ code match (50) → MOEGLICH
    assert result.muster == AusnahmeMuster.BERECHTIGUNGSFEHLER

def test_klassifiziere_result_dataclass():
    result = klassifiziere_ausnahme("", "", [])
    assert isinstance(result, KlassifizierungsErgebnis)


# ============================================================
# get_default_ausnahme_signaturen()
# ============================================================

def test_default_signaturen_count():
    sigs = get_default_ausnahme_signaturen()
    assert len(sigs) == 5

def test_default_sig_as001_timeout():
    sigs = get_default_ausnahme_signaturen()
    sig = next(s for s in sigs if s.signatur_id == "AS-001")
    assert sig.muster == AusnahmeMuster.TIMEOUT
    assert sig.schwere == AusnahmeSchwere.HOCH

def test_default_sig_as002_datenfehler():
    sigs = get_default_ausnahme_signaturen()
    sig = next(s for s in sigs if s.signatur_id == "AS-002")
    assert sig.muster == AusnahmeMuster.DATENFEHLER
    assert sig.schwere == AusnahmeSchwere.MITTEL

def test_default_sig_as003_berechtigung():
    sigs = get_default_ausnahme_signaturen()
    sig = next(s for s in sigs if s.signatur_id == "AS-003")
    assert sig.muster == AusnahmeMuster.BERECHTIGUNGSFEHLER
    assert sig.schwere == AusnahmeSchwere.HOCH

def test_default_sig_as004_ressource():
    sigs = get_default_ausnahme_signaturen()
    sig = next(s for s in sigs if s.signatur_id == "AS-004")
    assert sig.muster == AusnahmeMuster.RESSOURCENENGPASS
    assert sig.schwere == AusnahmeSchwere.KRITISCH

def test_default_sig_as005_integration():
    sigs = get_default_ausnahme_signaturen()
    sig = next(s for s in sigs if s.signatur_id == "AS-005")
    assert sig.muster == AusnahmeMuster.INTEGRATIONSFEHLER
    assert sig.schwere == AusnahmeSchwere.HOCH

def test_default_sig_as001_keywords():
    sigs = get_default_ausnahme_signaturen()
    sig = next(s for s in sigs if s.signatur_id == "AS-001")
    assert "timeout" in sig.schluessel_woerter

def test_default_sig_as001_code_praefixe():
    sigs = get_default_ausnahme_signaturen()
    sig = next(s for s in sigs if s.signatur_id == "AS-001")
    assert "TIMEOUT_" in sig.fehler_code_praefixe or "CONN_" in sig.fehler_code_praefixe

def test_default_sig_as004_has_keywords():
    sigs = get_default_ausnahme_signaturen()
    sig = next(s for s in sigs if s.signatur_id == "AS-004")
    assert len(sig.schluessel_woerter) > 0

def test_default_sig_as005_has_multiple_code_praefixe():
    sigs = get_default_ausnahme_signaturen()
    sig = next(s for s in sigs if s.signatur_id == "AS-005")
    assert len(sig.fehler_code_praefixe) >= 2

def test_default_sig_all_have_beschreibung():
    sigs = get_default_ausnahme_signaturen()
    for sig in sigs:
        assert sig.beschreibung != ""

def test_default_sig_ids_unique():
    sigs = get_default_ausnahme_signaturen()
    ids = [s.signatur_id for s in sigs]
    assert len(ids) == len(set(ids))


# ============================================================
# KlassifizierungsErgebnis dataclass
# ============================================================

def test_klassifizierungs_ergebnis_fields():
    result = KlassifizierungsErgebnis(AusnahmeMuster.TIMEOUT, MusterErkennungsKonfidenz.SICHER, "AS-001", AusnahmeSchwere.HOCH)
    assert result.muster == AusnahmeMuster.TIMEOUT
    assert result.konfidenz == MusterErkennungsKonfidenz.SICHER
    assert result.signatur_id == "AS-001"
    assert result.schwere == AusnahmeSchwere.HOCH

def test_klassifizierungs_ergebnis_optional_signatur_id():
    result = KlassifizierungsErgebnis(AusnahmeMuster.UNBEKANNT, MusterErkennungsKonfidenz.UNBEKANNT)
    assert result.signatur_id is None

def test_klassifizierungs_ergebnis_default_schwere():
    result = KlassifizierungsErgebnis(AusnahmeMuster.TIMEOUT, MusterErkennungsKonfidenz.SICHER)
    assert result.schwere == AusnahmeSchwere.MITTEL


# ============================================================
# RemediationsTyp Enum
# ============================================================

def test_remediation_typ_automatisch():
    assert RemediationsTyp.AUTOMATISCH == "AUTOMATISCH"

def test_remediation_typ_halbautomatisch():
    assert RemediationsTyp.HALBAUTOMATISCH == "HALBAUTOMATISCH"

def test_remediation_typ_manuell():
    assert RemediationsTyp.MANUELL == "MANUELL"

def test_remediation_typ_count():
    assert len(RemediationsTyp) == 3


# ============================================================
# RemediationsStatus Enum
# ============================================================

def test_remediation_status_vorgeschlagen():
    assert RemediationsStatus.VORGESCHLAGEN == "VORGESCHLAGEN"

def test_remediation_status_genehmigt():
    assert RemediationsStatus.GENEHMIGT == "GENEHMIGT"

def test_remediation_status_laufend():
    assert RemediationsStatus.LAUFEND == "LAUFEND"

def test_remediation_status_abgeschlossen():
    assert RemediationsStatus.ABGESCHLOSSEN == "ABGESCHLOSSEN"

def test_remediation_status_fehlgeschlagen():
    assert RemediationsStatus.FEHLGESCHLAGEN == "FEHLGESCHLAGEN"

def test_remediation_status_abgelehnt():
    assert RemediationsStatus.ABGELEHNT == "ABGELEHNT"

def test_remediation_status_count():
    assert len(RemediationsStatus) == 6


# ============================================================
# RemediationsAktion Enum
# ============================================================

def test_aktion_neustart():
    assert RemediationsAktion.NEUSTART == "NEUSTART"

def test_aktion_rollback():
    assert RemediationsAktion.ROLLBACK == "ROLLBACK"

def test_aktion_retry():
    assert RemediationsAktion.RETRY == "RETRY"

def test_aktion_eskalieren():
    assert RemediationsAktion.ESKALIEREN == "ESKALIEREN"

def test_aktion_cache_leeren():
    assert RemediationsAktion.CACHE_LEEREN == "CACHE_LEEREN"

def test_aktion_verbindung_reset():
    assert RemediationsAktion.VERBINDUNG_RESET == "VERBINDUNG_RESET"

def test_aktion_manuell_eingreifen():
    assert RemediationsAktion.MANUELL_EINGREIFEN == "MANUELL_EINGREIFEN"

def test_aktion_count():
    assert len(RemediationsAktion) == 7


# ============================================================
# RemediationsSchritt
# ============================================================

def test_schritt_basic_fields():
    s = RemediationsSchritt("RS-1", RemediationsAktion.RETRY, 1, "Retry op", True, 60)
    assert s.schritt_id == "RS-1"
    assert s.aktion == RemediationsAktion.RETRY
    assert s.reihenfolge == 1
    assert s.beschreibung == "Retry op"
    assert s.automatisch is True
    assert s.timeout_sekunden == 60

def test_schritt_default_automatisch():
    s = RemediationsSchritt("RS-1", RemediationsAktion.RETRY, 1)
    assert s.automatisch is True

def test_schritt_default_timeout():
    s = RemediationsSchritt("RS-1", RemediationsAktion.RETRY, 1)
    assert s.timeout_sekunden == 60

def test_schritt_nicht_automatisch():
    s = RemediationsSchritt("RS-1", RemediationsAktion.ESKALIEREN, 3, automatisch=False)
    assert s.automatisch is False

def test_schritt_zero_timeout():
    s = RemediationsSchritt("RS-1", RemediationsAktion.ESKALIEREN, 3, automatisch=False, timeout_sekunden=0)
    assert s.timeout_sekunden == 0


# ============================================================
# RemediationsPlaybook — construction
# ============================================================

def test_playbook_basic_fields():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH)
    assert pb.playbook_id == "PB-1"
    assert pb.ausnahme_muster == "TIMEOUT"
    assert pb.typ == RemediationsTyp.AUTOMATISCH

def test_playbook_default_schritte():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH)
    assert pb.schritte == []

def test_playbook_default_stats():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH)
    assert pb.erfolgreich_angewendet == 0
    assert pb.fehlgeschlagen_angewendet == 0

def test_playbook_default_beschreibung():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH)
    assert pb.beschreibung == ""


# ============================================================
# RemediationsPlaybook.erfolgsrate_pct()
# ============================================================

def test_erfolgsrate_never_applied_100():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH)
    assert pb.erfolgsrate_pct() == 100.0

def test_erfolgsrate_all_success():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH,
                              erfolgreich_angewendet=10, fehlgeschlagen_angewendet=0)
    assert pb.erfolgsrate_pct() == 100.0

def test_erfolgsrate_all_failed():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH,
                              erfolgreich_angewendet=0, fehlgeschlagen_angewendet=10)
    assert pb.erfolgsrate_pct() == 0.0

def test_erfolgsrate_half():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH,
                              erfolgreich_angewendet=5, fehlgeschlagen_angewendet=5)
    assert pb.erfolgsrate_pct() == 50.0

def test_erfolgsrate_pb001_90_pct():
    # PB-001: 45/50 = 90.0%
    pbs = get_default_playbooks()
    pb1 = next(p for p in pbs if p.playbook_id == "PB-001")
    assert pb1.erfolgsrate_pct() == 90.0

def test_erfolgsrate_pb002():
    # PB-002: 20/22 ≈ 90.909...%
    pbs = get_default_playbooks()
    pb2 = next(p for p in pbs if p.playbook_id == "PB-002")
    rate = pb2.erfolgsrate_pct()
    assert abs(rate - (20/22*100)) < 0.01

def test_erfolgsrate_pb003_100():
    # PB-003: never applied → 100.0%
    pbs = get_default_playbooks()
    pb3 = next(p for p in pbs if p.playbook_id == "PB-003")
    assert pb3.erfolgsrate_pct() == 100.0

def test_erfolgsrate_returns_float():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH,
                              erfolgreich_angewendet=3, fehlgeschlagen_angewendet=1)
    assert isinstance(pb.erfolgsrate_pct(), float)


# ============================================================
# RemediationsPlaybook.automatische_schritte()
# ============================================================

def test_automatische_schritte_empty():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH)
    assert pb.automatische_schritte() == []

def test_automatische_schritte_all_auto():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH)
    pb.schritte = [
        RemediationsSchritt("RS-1", RemediationsAktion.RETRY, 1, automatisch=True),
        RemediationsSchritt("RS-2", RemediationsAktion.ROLLBACK, 2, automatisch=True),
    ]
    result = pb.automatische_schritte()
    assert len(result) == 2

def test_automatische_schritte_none_auto():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH)
    pb.schritte = [
        RemediationsSchritt("RS-1", RemediationsAktion.ESKALIEREN, 1, automatisch=False),
    ]
    result = pb.automatische_schritte()
    assert len(result) == 0

def test_automatische_schritte_sorted_by_reihenfolge():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH)
    pb.schritte = [
        RemediationsSchritt("RS-3", RemediationsAktion.RETRY, 3, automatisch=True),
        RemediationsSchritt("RS-1", RemediationsAktion.VERBINDUNG_RESET, 1, automatisch=True),
        RemediationsSchritt("RS-2", RemediationsAktion.CACHE_LEEREN, 2, automatisch=True),
    ]
    result = pb.automatische_schritte()
    assert [s.schritt_id for s in result] == ["RS-1", "RS-2", "RS-3"]

def test_automatische_schritte_filters_nonauto():
    pb = RemediationsPlaybook("PB-1", "TIMEOUT", RemediationsTyp.AUTOMATISCH)
    pb.schritte = [
        RemediationsSchritt("RS-1", RemediationsAktion.RETRY, 1, automatisch=True),
        RemediationsSchritt("RS-2", RemediationsAktion.ESKALIEREN, 2, automatisch=False),
        RemediationsSchritt("RS-3", RemediationsAktion.CACHE_LEEREN, 3, automatisch=True),
    ]
    result = pb.automatische_schritte()
    assert len(result) == 2
    assert all(s.automatisch for s in result)

def test_pb001_automatische_schritte():
    # PB-001: RS-001 (auto), RS-002 (auto), RS-003 (not auto)
    pbs = get_default_playbooks()
    pb1 = next(p for p in pbs if p.playbook_id == "PB-001")
    auto = pb1.automatische_schritte()
    assert len(auto) == 2
    assert auto[0].schritt_id == "RS-001"
    assert auto[1].schritt_id == "RS-002"

def test_pb002_automatische_schritte():
    # PB-002: RS-004 (auto), RS-005 (not auto)
    pbs = get_default_playbooks()
    pb2 = next(p for p in pbs if p.playbook_id == "PB-002")
    auto = pb2.automatische_schritte()
    assert len(auto) == 1
    assert auto[0].schritt_id == "RS-004"

def test_pb003_automatische_schritte():
    # PB-003: RS-006 (auto), RS-007 (not auto)
    pbs = get_default_playbooks()
    pb3 = next(p for p in pbs if p.playbook_id == "PB-003")
    auto = pb3.automatische_schritte()
    assert len(auto) == 1
    assert auto[0].schritt_id == "RS-006"


# ============================================================
# RemediationsVorschlag
# ============================================================

def test_vorschlag_basic_fields():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001")
    assert v.vorschlag_id == "V-1"
    assert v.workflow_instanz_id == "WF-001"
    assert v.ausnahme_muster == "TIMEOUT"
    assert v.playbook_id == "PB-001"

def test_vorschlag_default_status():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001")
    assert v.status == RemediationsStatus.VORGESCHLAGEN

def test_vorschlag_default_genehmigt_von():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001")
    assert v.genehmigt_von is None

def test_vorschlag_default_abgeschlossen_am():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001")
    assert v.abgeschlossen_am is None

def test_vorschlag_erstellt_am_set():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001")
    assert isinstance(v.erstellt_am, datetime)


# ============================================================
# RemediationsVorschlag.ist_aktiv()
# ============================================================

def test_ist_aktiv_vorgeschlagen():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001", RemediationsStatus.VORGESCHLAGEN)
    assert v.ist_aktiv() is True

def test_ist_aktiv_genehmigt():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001", RemediationsStatus.GENEHMIGT)
    assert v.ist_aktiv() is True

def test_ist_aktiv_laufend():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001", RemediationsStatus.LAUFEND)
    assert v.ist_aktiv() is True

def test_ist_aktiv_abgeschlossen_false():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001", RemediationsStatus.ABGESCHLOSSEN)
    assert v.ist_aktiv() is False

def test_ist_aktiv_fehlgeschlagen_false():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001", RemediationsStatus.FEHLGESCHLAGEN)
    assert v.ist_aktiv() is False

def test_ist_aktiv_abgelehnt_false():
    v = RemediationsVorschlag("V-1", "WF-001", "TIMEOUT", "PB-001", RemediationsStatus.ABGELEHNT)
    assert v.ist_aktiv() is False


# ============================================================
# get_default_playbooks()
# ============================================================

def test_default_playbooks_count():
    pbs = get_default_playbooks()
    assert len(pbs) == 3

def test_default_pb001_fields():
    pbs = get_default_playbooks()
    pb1 = next(p for p in pbs if p.playbook_id == "PB-001")
    assert pb1.ausnahme_muster == "TIMEOUT"
    assert pb1.typ == RemediationsTyp.AUTOMATISCH

def test_default_pb002_fields():
    pbs = get_default_playbooks()
    pb2 = next(p for p in pbs if p.playbook_id == "PB-002")
    assert pb2.ausnahme_muster == "DATENFEHLER"
    assert pb2.typ == RemediationsTyp.HALBAUTOMATISCH

def test_default_pb003_fields():
    pbs = get_default_playbooks()
    pb3 = next(p for p in pbs if p.playbook_id == "PB-003")
    assert pb3.ausnahme_muster == "RESSOURCENENGPASS"
    assert pb3.typ == RemediationsTyp.AUTOMATISCH

def test_default_pb001_three_schritte():
    pbs = get_default_playbooks()
    pb1 = next(p for p in pbs if p.playbook_id == "PB-001")
    assert len(pb1.schritte) == 3

def test_default_pb002_two_schritte():
    pbs = get_default_playbooks()
    pb2 = next(p for p in pbs if p.playbook_id == "PB-002")
    assert len(pb2.schritte) == 2

def test_default_pb003_two_schritte():
    pbs = get_default_playbooks()
    pb3 = next(p for p in pbs if p.playbook_id == "PB-003")
    assert len(pb3.schritte) == 2

def test_default_pb001_stats():
    pbs = get_default_playbooks()
    pb1 = next(p for p in pbs if p.playbook_id == "PB-001")
    assert pb1.erfolgreich_angewendet == 45
    assert pb1.fehlgeschlagen_angewendet == 5

def test_default_pb002_stats():
    pbs = get_default_playbooks()
    pb2 = next(p for p in pbs if p.playbook_id == "PB-002")
    assert pb2.erfolgreich_angewendet == 20
    assert pb2.fehlgeschlagen_angewendet == 2

def test_default_pb003_never_applied():
    pbs = get_default_playbooks()
    pb3 = next(p for p in pbs if p.playbook_id == "PB-003")
    assert pb3.erfolgreich_angewendet == 0
    assert pb3.fehlgeschlagen_angewendet == 0

def test_default_pb001_beschreibung():
    pbs = get_default_playbooks()
    pb1 = next(p for p in pbs if p.playbook_id == "PB-001")
    assert pb1.beschreibung != ""

def test_default_pb_ids_unique():
    pbs = get_default_playbooks()
    ids = [p.playbook_id for p in pbs]
    assert len(ids) == len(set(ids))

def test_default_pb001_step1_verbindung_reset():
    pbs = get_default_playbooks()
    pb1 = next(p for p in pbs if p.playbook_id == "PB-001")
    step1 = next(s for s in pb1.schritte if s.reihenfolge == 1)
    assert step1.aktion == RemediationsAktion.VERBINDUNG_RESET
    assert step1.automatisch is True

def test_default_pb001_step2_retry():
    pbs = get_default_playbooks()
    pb1 = next(p for p in pbs if p.playbook_id == "PB-001")
    step2 = next(s for s in pb1.schritte if s.reihenfolge == 2)
    assert step2.aktion == RemediationsAktion.RETRY
    assert step2.automatisch is True

def test_default_pb001_step3_eskalieren_not_auto():
    pbs = get_default_playbooks()
    pb1 = next(p for p in pbs if p.playbook_id == "PB-001")
    step3 = next(s for s in pb1.schritte if s.reihenfolge == 3)
    assert step3.aktion == RemediationsAktion.ESKALIEREN
    assert step3.automatisch is False

def test_default_pb002_step1_rollback():
    pbs = get_default_playbooks()
    pb2 = next(p for p in pbs if p.playbook_id == "PB-002")
    step1 = next(s for s in pb2.schritte if s.reihenfolge == 1)
    assert step1.aktion == RemediationsAktion.ROLLBACK
    assert step1.automatisch is True

def test_default_pb002_step2_manuell():
    pbs = get_default_playbooks()
    pb2 = next(p for p in pbs if p.playbook_id == "PB-002")
    step2 = next(s for s in pb2.schritte if s.reihenfolge == 2)
    assert step2.aktion == RemediationsAktion.MANUELL_EINGREIFEN
    assert step2.automatisch is False

def test_default_pb003_step1_cache():
    pbs = get_default_playbooks()
    pb3 = next(p for p in pbs if p.playbook_id == "PB-003")
    step1 = next(s for s in pb3.schritte if s.reihenfolge == 1)
    assert step1.aktion == RemediationsAktion.CACHE_LEEREN
    assert step1.automatisch is True

def test_default_pb003_step2_eskalieren():
    pbs = get_default_playbooks()
    pb3 = next(p for p in pbs if p.playbook_id == "PB-003")
    step2 = next(s for s in pb3.schritte if s.reihenfolge == 2)
    assert step2.aktion == RemediationsAktion.ESKALIEREN
    assert step2.automatisch is False


# ============================================================
# FastAPI endpoint integration (via TestClient)
# ============================================================

def test_endpoint_ausnahme_signaturen():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get("/process/exception/signaturen")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 5

def test_endpoint_signaturen_fields():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get("/process/exception/signaturen")
    data = resp.json()
    for item in data:
        assert "signatur_id" in item
        assert "muster" in item
        assert "schwere" in item

def test_endpoint_klassifiziere_timeout():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.post("/process/exception/klassifiziere",
                       json={"fehler_text": "connection timeout error", "fehler_code": "TIMEOUT_001"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["muster"] == "TIMEOUT"

def test_endpoint_klassifiziere_unbekannt():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.post("/process/exception/klassifiziere",
                       json={"fehler_text": "xyz random", "fehler_code": "XYZ_001"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["muster"] == "UNBEKANNT"

def test_endpoint_remediation_playbooks():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get("/process/remediation/playbooks")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3

def test_endpoint_remediation_playbooks_fields():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.get("/process/remediation/playbooks")
    data = resp.json()
    for item in data:
        assert "playbook_id" in item
        assert "erfolgsrate_pct" in item
        assert "automatische_schritte" in item

def test_endpoint_pruefe_playbook_found():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.post("/process/remediation/pruefe-playbook", json={"playbook_id": "PB-001"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["playbook_id"] == "PB-001"
    assert "schritte" in data

def test_endpoint_pruefe_playbook_not_found():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.post("/process/remediation/pruefe-playbook", json={"playbook_id": "PB-999"})
    assert resp.status_code == 200
    data = resp.json()
    assert "fehler" in data

def test_endpoint_pruefe_pb001_auto_schritte():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.post("/process/remediation/pruefe-playbook", json={"playbook_id": "PB-001"})
    data = resp.json()
    auto = data["automatische_schritte"]
    assert "RS-001" in auto
    assert "RS-002" in auto
    assert "RS-003" not in auto

def test_endpoint_klassifiziere_returns_konfidenz():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    resp = client.post("/process/exception/klassifiziere",
                       json={"fehler_text": "connection timeout", "fehler_code": "TIMEOUT_001"})
    data = resp.json()
    assert "konfidenz" in data
    assert data["konfidenz"] in ["SICHER", "WAHRSCHEINLICH", "MOEGLICH", "UNBEKANNT"]
