"""
Wave 63 — Process Validation Contracts + Workflow Collaboration Contracts
130+ tests covering ValidierungsRegel, validiere_daten, KollaborationsEntscheidung,
default rules/decisions, and the 4 FastAPI endpoints.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# ── Core imports ────────────────────────────────────────────────────────────────
from app.core.process_validation_contracts import (
    ValidierungsSchwere, RegelTyp, ValidierungsStatus,
    ValidierungsRegel, ValidierungsFehler, ValidierungsErgebnis,
    validiere_daten, get_default_validierungs_regeln,
)
from app.core.workflow_collaboration_contracts import (
    AbstimmungsTyp, StimmeTyp, KollaborationsStatus,
    Stimme, KollaborationsEntscheidung,
    get_default_entscheidungen,
)


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Enum smoke tests
# ════════════════════════════════════════════════════════════════════════════════

class TestValidierungsEnums:
    def test_schwere_values(self):
        assert ValidierungsSchwere.FEHLER == "FEHLER"
        assert ValidierungsSchwere.WARNUNG == "WARNUNG"
        assert ValidierungsSchwere.HINWEIS == "HINWEIS"

    def test_regel_typ_values(self):
        assert RegelTyp.PFLICHTFELD == "PFLICHTFELD"
        assert RegelTyp.WERTEBEREICH == "WERTEBEREICH"
        assert RegelTyp.FORMAT == "FORMAT"
        assert RegelTyp.QUERVERWEIS == "QUERVERWEIS"
        assert RegelTyp.GESCHAEFTSREGEL == "GESCHAEFTSREGEL"

    def test_validierungs_status_values(self):
        assert ValidierungsStatus.GUELTIG == "GUELTIG"
        assert ValidierungsStatus.UNGUELTIG == "UNGUELTIG"
        assert ValidierungsStatus.WARNUNG == "WARNUNG"


class TestKollaborationsEnums:
    def test_abstimmungs_typ(self):
        assert AbstimmungsTyp.EINFACHE_MEHRHEIT == "EINFACHE_MEHRHEIT"
        assert AbstimmungsTyp.QUALIFIZIERTE_MEHRHEIT == "QUALIFIZIERTE_MEHRHEIT"
        assert AbstimmungsTyp.EINSTIMMIGKEIT == "EINSTIMMIGKEIT"
        assert AbstimmungsTyp.VETO == "VETO"

    def test_stimme_typ(self):
        assert StimmeTyp.JA == "JA"
        assert StimmeTyp.NEIN == "NEIN"
        assert StimmeTyp.ENTHALTEN == "ENTHALTEN"

    def test_kollaborations_status(self):
        assert KollaborationsStatus.OFFEN == "OFFEN"
        assert KollaborationsStatus.ANGENOMMEN == "ANGENOMMEN"
        assert KollaborationsStatus.ABGELEHNT == "ABGELEHNT"
        assert KollaborationsStatus.ABGELAUFEN == "ABGELAUFEN"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ValidierungsRegel.pruefe() — PFLICHTFELD
# ════════════════════════════════════════════════════════════════════════════════

def _pflicht(feld="x"):
    return ValidierungsRegel("R-TEST", "Test", RegelTyp.PFLICHTFELD,
                             ValidierungsSchwere.FEHLER, feld)


class TestPruefePflichtfeld:
    def test_present_non_empty_string(self):
        assert _pflicht("name").pruefe({"name": "Max"}) is True

    def test_present_integer_value(self):
        assert _pflicht("menge").pruefe({"menge": 100}) is True

    def test_present_float_value(self):
        assert _pflicht("preis").pruefe({"preis": 3.14}) is True

    def test_field_missing(self):
        assert _pflicht("name").pruefe({}) is False

    def test_field_none(self):
        assert _pflicht("name").pruefe({"name": None}) is False

    def test_field_empty_string(self):
        assert _pflicht("name").pruefe({"name": ""}) is False

    def test_field_zero_is_truthy_int(self):
        # 0 is not None and not "" so should be True
        assert _pflicht("count").pruefe({"count": 0}) is True

    def test_field_false_bool(self):
        # False is not None and not "" so should be True
        assert _pflicht("flag").pruefe({"flag": False}) is True

    def test_other_field_present_target_missing(self):
        assert _pflicht("target").pruefe({"other": "value"}) is False


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — ValidierungsRegel.pruefe() — WERTEBEREICH
# ════════════════════════════════════════════════════════════════════════════════

def _bereich(feld="val", min_wert=None, max_wert=None):
    return ValidierungsRegel("R-TEST", "Test", RegelTyp.WERTEBEREICH,
                             ValidierungsSchwere.FEHLER, feld,
                             min_wert=min_wert, max_wert=max_wert)


class TestPruefeWertebereich:
    def test_in_range_min_max(self):
        assert _bereich("v", 0.0, 100.0).pruefe({"v": 50}) is True

    def test_at_min_boundary(self):
        assert _bereich("v", 0.1, 100.0).pruefe({"v": 0.1}) is True

    def test_at_max_boundary(self):
        assert _bereich("v", 0.0, 100.0).pruefe({"v": 100.0}) is True

    def test_below_min(self):
        assert _bereich("v", 1.0, 100.0).pruefe({"v": 0.5}) is False

    def test_above_max(self):
        assert _bereich("v", 0.0, 100.0).pruefe({"v": 200.0}) is False

    def test_field_missing_returns_false(self):
        assert _bereich("v", 0.0, 100.0).pruefe({}) is False

    def test_non_numeric_value_returns_false(self):
        assert _bereich("v", 0.0, 100.0).pruefe({"v": "abc"}) is False

    def test_none_value_returns_false(self):
        assert _bereich("v", 0.0, 100.0).pruefe({"v": None}) is False

    def test_only_min_no_max_above_min(self):
        assert _bereich("v", 5.0, None).pruefe({"v": 999.0}) is True

    def test_only_min_no_max_below_min(self):
        assert _bereich("v", 5.0, None).pruefe({"v": 1.0}) is False

    def test_only_max_no_min_below_max(self):
        assert _bereich("v", None, 50.0).pruefe({"v": 25.0}) is True

    def test_only_max_no_min_above_max(self):
        assert _bereich("v", None, 50.0).pruefe({"v": 100.0}) is False

    def test_no_bounds_any_numeric(self):
        assert _bereich("v", None, None).pruefe({"v": 99999.0}) is True

    def test_string_numeric_coerced(self):
        # "50" can be float()-coerced
        assert _bereich("v", 0.0, 100.0).pruefe({"v": "50"}) is True


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 4 — ValidierungsRegel.pruefe() — QUERVERWEIS
# ════════════════════════════════════════════════════════════════════════════════

def _quer(felder):
    r = ValidierungsRegel("R-TEST", "Test", RegelTyp.QUERVERWEIS,
                          ValidierungsSchwere.FEHLER, "combined")
    r.pflicht_felder = felder
    return r


class TestPruefeQuerverweis:
    def test_all_fields_present(self):
        assert _quer(["a", "b"]).pruefe({"a": 1, "b": 2}) is True

    def test_one_field_missing(self):
        assert _quer(["a", "b"]).pruefe({"a": 1}) is False

    def test_all_fields_missing(self):
        assert _quer(["a", "b"]).pruefe({}) is False

    def test_empty_pflicht_felder(self):
        # all() of empty iterable → True
        assert _quer([]).pruefe({}) is True

    def test_three_fields_all_present(self):
        assert _quer(["x", "y", "z"]).pruefe({"x": 1, "y": 2, "z": 3}) is True

    def test_three_fields_last_missing(self):
        assert _quer(["x", "y", "z"]).pruefe({"x": 1, "y": 2}) is False


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 5 — ValidierungsRegel.pruefe() — FORMAT / GESCHAEFTSREGEL
# ════════════════════════════════════════════════════════════════════════════════

class TestPruefeFormatGeschaeftsregel:
    def test_format_always_true(self):
        r = ValidierungsRegel("R-F", "Test", RegelTyp.FORMAT,
                              ValidierungsSchwere.FEHLER, "feld")
        assert r.pruefe({}) is True

    def test_format_with_data(self):
        r = ValidierungsRegel("R-F", "Test", RegelTyp.FORMAT,
                              ValidierungsSchwere.FEHLER, "feld")
        assert r.pruefe({"feld": "anything"}) is True

    def test_geschaeftsregel_always_true(self):
        r = ValidierungsRegel("R-G", "Test", RegelTyp.GESCHAEFTSREGEL,
                              ValidierungsSchwere.FEHLER, "feld")
        assert r.pruefe({}) is True

    def test_geschaeftsregel_with_data(self):
        r = ValidierungsRegel("R-G", "Test", RegelTyp.GESCHAEFTSREGEL,
                              ValidierungsSchwere.FEHLER, "feld")
        assert r.pruefe({"feld": "anything"}) is True


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 6 — validiere_daten() function
# ════════════════════════════════════════════════════════════════════════════════

class TestValidiereDaten:
    def _regel(self, rid, typ, schwere, feld, **kw):
        return ValidierungsRegel(rid, rid, typ, schwere, feld, **kw)

    def test_all_pass_gueltig(self):
        regeln = [self._regel("R1", RegelTyp.PFLICHTFELD, ValidierungsSchwere.FEHLER, "a")]
        ergebnis = validiere_daten({"a": "x"}, regeln)
        assert ergebnis.status == ValidierungsStatus.GUELTIG
        assert ergebnis.ist_gueltig is True
        assert len(ergebnis.fehler) == 0
        assert len(ergebnis.warnungen) == 0

    def test_one_fehler_ungueltig(self):
        regeln = [self._regel("R1", RegelTyp.PFLICHTFELD, ValidierungsSchwere.FEHLER, "a")]
        ergebnis = validiere_daten({}, regeln)
        assert ergebnis.status == ValidierungsStatus.UNGUELTIG
        assert ergebnis.ist_gueltig is False
        assert len(ergebnis.fehler) == 1

    def test_only_warnung_warnung_status(self):
        regeln = [self._regel("R1", RegelTyp.PFLICHTFELD, ValidierungsSchwere.WARNUNG, "a")]
        ergebnis = validiere_daten({}, regeln)
        assert ergebnis.status == ValidierungsStatus.WARNUNG
        assert ergebnis.ist_gueltig is False
        assert len(ergebnis.warnungen) == 1
        assert len(ergebnis.fehler) == 0

    def test_only_hinweis_gueltig_status(self):
        regeln = [self._regel("R1", RegelTyp.PFLICHTFELD, ValidierungsSchwere.HINWEIS, "a")]
        ergebnis = validiere_daten({}, regeln)
        assert ergebnis.status == ValidierungsStatus.GUELTIG
        assert ergebnis.ist_gueltig is True
        assert len(ergebnis.hinweise) == 1

    def test_fehler_plus_warnung_ungueltig(self):
        regeln = [
            self._regel("R1", RegelTyp.PFLICHTFELD, ValidierungsSchwere.FEHLER, "a"),
            self._regel("R2", RegelTyp.PFLICHTFELD, ValidierungsSchwere.WARNUNG, "b"),
        ]
        ergebnis = validiere_daten({}, regeln)
        assert ergebnis.status == ValidierungsStatus.UNGUELTIG
        assert len(ergebnis.fehler) == 1
        assert len(ergebnis.warnungen) == 1

    def test_multiple_fehler_all_listed(self):
        regeln = [
            self._regel("R1", RegelTyp.PFLICHTFELD, ValidierungsSchwere.FEHLER, "a"),
            self._regel("R2", RegelTyp.PFLICHTFELD, ValidierungsSchwere.FEHLER, "b"),
            self._regel("R3", RegelTyp.PFLICHTFELD, ValidierungsSchwere.FEHLER, "c"),
        ]
        ergebnis = validiere_daten({}, regeln)
        assert len(ergebnis.fehler) == 3

    def test_empty_regeln_gueltig(self):
        ergebnis = validiere_daten({"a": "x"}, [])
        assert ergebnis.status == ValidierungsStatus.GUELTIG

    def test_fehler_object_fields(self):
        regeln = [self._regel("R-XYZ", RegelTyp.PFLICHTFELD, ValidierungsSchwere.FEHLER, "myfield")]
        ergebnis = validiere_daten({}, regeln)
        f = ergebnis.fehler[0]
        assert f.regel_id == "R-XYZ"
        assert f.feld == "myfield"
        assert f.schwere == ValidierungsSchwere.FEHLER
        assert "Validierung fehlgeschlagen" in f.nachricht

    def test_ist_gueltig_true_only_for_gueltig(self):
        regeln = [self._regel("R1", RegelTyp.PFLICHTFELD, ValidierungsSchwere.WARNUNG, "a")]
        ergebnis = validiere_daten({}, regeln)
        assert ergebnis.ist_gueltig is False

    def test_mixed_pass_fail(self):
        regeln = [
            self._regel("R1", RegelTyp.PFLICHTFELD, ValidierungsSchwere.FEHLER, "a"),
            self._regel("R2", RegelTyp.PFLICHTFELD, ValidierungsSchwere.FEHLER, "b"),
        ]
        ergebnis = validiere_daten({"a": "present"}, regeln)
        assert ergebnis.status == ValidierungsStatus.UNGUELTIG
        assert len(ergebnis.fehler) == 1
        assert ergebnis.fehler[0].regel_id == "R2"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 7 — Default Validierungsregeln (VR-001..VR-005)
# ════════════════════════════════════════════════════════════════════════════════

class TestDefaultValidierungsRegeln:
    def _valid_daten(self):
        return {"lieferant_id": "L1", "menge_tonnen": 100.0, "preis_eur_t": 200.0}

    def test_valid_data_gueltig(self):
        ergebnis = validiere_daten(self._valid_daten(), get_default_validierungs_regeln())
        assert ergebnis.status == ValidierungsStatus.GUELTIG

    def test_five_default_regeln(self):
        assert len(get_default_validierungs_regeln()) == 5

    def test_rule_ids(self):
        ids = [r.regel_id for r in get_default_validierungs_regeln()]
        assert "VR-001" in ids
        assert "VR-002" in ids
        assert "VR-003" in ids
        assert "VR-004" in ids
        assert "VR-005" in ids

    def test_missing_lieferant_ungueltig(self):
        daten = {"menge_tonnen": 100.0, "preis_eur_t": 200.0}
        ergebnis = validiere_daten(daten, get_default_validierungs_regeln())
        assert ergebnis.status == ValidierungsStatus.UNGUELTIG
        regel_ids = [f.regel_id for f in ergebnis.fehler]
        assert "VR-001" in regel_ids

    def test_menge_zero_ungueltig(self):
        daten = {**self._valid_daten(), "menge_tonnen": 0}
        ergebnis = validiere_daten(daten, get_default_validierungs_regeln())
        assert ergebnis.status == ValidierungsStatus.UNGUELTIG
        regel_ids = [f.regel_id for f in ergebnis.fehler]
        assert "VR-002" in regel_ids

    def test_menge_below_min_ungueltig(self):
        daten = {**self._valid_daten(), "menge_tonnen": 0.05}
        ergebnis = validiere_daten(daten, get_default_validierungs_regeln())
        assert ergebnis.status == ValidierungsStatus.UNGUELTIG

    def test_menge_above_max_ungueltig(self):
        daten = {**self._valid_daten(), "menge_tonnen": 99999}
        ergebnis = validiere_daten(daten, get_default_validierungs_regeln())
        assert ergebnis.status == ValidierungsStatus.UNGUELTIG

    def test_preis_below_min_warnung(self):
        daten = {**self._valid_daten(), "preis_eur_t": 5.0}
        ergebnis = validiere_daten(daten, get_default_validierungs_regeln())
        # VR-003 is WARNUNG severity
        assert ValidierungsStatus.WARNUNG == ergebnis.status or ergebnis.status == ValidierungsStatus.UNGUELTIG
        regel_ids = [w.regel_id for w in ergebnis.warnungen]
        assert "VR-003" in regel_ids

    def test_preis_above_max_warnung(self):
        daten = {**self._valid_daten(), "preis_eur_t": 2000.0}
        ergebnis = validiere_daten(daten, get_default_validierungs_regeln())
        regel_ids = [w.regel_id for w in ergebnis.warnungen]
        assert "VR-003" in regel_ids

    def test_no_kommentar_hinweis_still_gueltig(self):
        daten = self._valid_daten()  # no 'kommentar'
        ergebnis = validiere_daten(daten, get_default_validierungs_regeln())
        # VR-005 is HINWEIS only — status should still be GUELTIG
        assert ergebnis.status == ValidierungsStatus.GUELTIG
        assert len(ergebnis.hinweise) == 1
        assert ergebnis.hinweise[0].regel_id == "VR-005"

    def test_with_kommentar_no_hinweis(self):
        daten = {**self._valid_daten(), "kommentar": "Alles ok"}
        ergebnis = validiere_daten(daten, get_default_validierungs_regeln())
        assert len(ergebnis.hinweise) == 0

    def test_vr001_schwere_fehler(self):
        regeln = get_default_validierungs_regeln()
        vr001 = next(r for r in regeln if r.regel_id == "VR-001")
        assert vr001.schwere == ValidierungsSchwere.FEHLER

    def test_vr003_schwere_warnung(self):
        regeln = get_default_validierungs_regeln()
        vr003 = next(r for r in regeln if r.regel_id == "VR-003")
        assert vr003.schwere == ValidierungsSchwere.WARNUNG

    def test_vr005_schwere_hinweis(self):
        regeln = get_default_validierungs_regeln()
        vr005 = next(r for r in regeln if r.regel_id == "VR-005")
        assert vr005.schwere == ValidierungsSchwere.HINWEIS

    def test_vr004_querverweis_missing_menge(self):
        daten = {"lieferant_id": "L1", "preis_eur_t": 200.0}
        ergebnis = validiere_daten(daten, get_default_validierungs_regeln())
        # VR-002 (menge fehlt) + VR-004 (querverweis)
        assert ergebnis.status == ValidierungsStatus.UNGUELTIG

    def test_vr002_regel_typ(self):
        regeln = get_default_validierungs_regeln()
        vr002 = next(r for r in regeln if r.regel_id == "VR-002")
        assert vr002.regel_typ == RegelTyp.WERTEBEREICH

    def test_vr004_regel_typ(self):
        regeln = get_default_validierungs_regeln()
        vr004 = next(r for r in regeln if r.regel_id == "VR-004")
        assert vr004.regel_typ == RegelTyp.QUERVERWEIS


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 8 — KollaborationsEntscheidung helpers
# ════════════════════════════════════════════════════════════════════════════════

NOW = datetime(2026, 3, 16, 10, 0, 0)


def _entscheidung(typ, stimmer, stimmen):
    e = KollaborationsEntscheidung("E-T", "WI-T", typ, stimmer, [])
    e.abgegebene_stimmen = stimmen
    return e


def _stimme(sid, typ):
    return Stimme(sid, typ, NOW)


class TestAusstehende:
    def test_none_outstanding_all_voted(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA)])
        assert e.ausstehende_stimmer() == []

    def test_one_outstanding(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B", "C"],
                          [_stimme("A", StimmeTyp.JA)])
        outstanding = e.ausstehende_stimmer()
        assert "B" in outstanding
        assert "C" in outstanding
        assert "A" not in outstanding

    def test_all_outstanding(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B"], [])
        assert set(e.ausstehende_stimmer()) == {"A", "B"}

    def test_empty_erforderliche(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, [], [])
        assert e.ausstehende_stimmer() == []


class TestStimmeCounts:
    def test_ja_count(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, [],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA),
                           _stimme("C", StimmeTyp.NEIN)])
        assert e.ja_stimmen() == 2

    def test_nein_count(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, [],
                          [_stimme("A", StimmeTyp.NEIN), _stimme("B", StimmeTyp.ENTHALTEN)])
        assert e.nein_stimmen() == 1

    def test_no_votes(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, [], [])
        assert e.ja_stimmen() == 0
        assert e.nein_stimmen() == 0

    def test_enthalten_not_counted_as_ja_or_nein(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, [],
                          [_stimme("A", StimmeTyp.ENTHALTEN), _stimme("B", StimmeTyp.ENTHALTEN)])
        assert e.ja_stimmen() == 0
        assert e.nein_stimmen() == 0


class TestBeteiligungPct:
    def test_zero_no_required(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, [], [])
        assert e.beteiligung_pct() == 0.0

    def test_full_participation(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA)])
        assert e.beteiligung_pct() == 100.0

    def test_half_participation(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA)])
        assert e.beteiligung_pct() == 50.0

    def test_two_of_three(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B", "C"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA)])
        assert abs(e.beteiligung_pct() - 66.666666) < 0.01


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 9 — berechne_ergebnis() — VETO
# ════════════════════════════════════════════════════════════════════════════════

class TestBerechneErgebnisVeto:
    def test_veto_any_nein_abgelehnt(self):
        e = _entscheidung(AbstimmungsTyp.VETO, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.NEIN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ABGELEHNT

    def test_veto_all_ja_angenommen(self):
        e = _entscheidung(AbstimmungsTyp.VETO, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ANGENOMMEN

    def test_veto_all_enthalten_angenommen(self):
        e = _entscheidung(AbstimmungsTyp.VETO, ["A", "B"],
                          [_stimme("A", StimmeTyp.ENTHALTEN), _stimme("B", StimmeTyp.ENTHALTEN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ANGENOMMEN

    def test_veto_outstanding_offen(self):
        e = _entscheidung(AbstimmungsTyp.VETO, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA)])
        assert e.berechne_ergebnis() == KollaborationsStatus.OFFEN

    def test_veto_no_votes_offen(self):
        e = _entscheidung(AbstimmungsTyp.VETO, ["A", "B"], [])
        assert e.berechne_ergebnis() == KollaborationsStatus.OFFEN

    def test_veto_nein_overrides_outstanding(self):
        # Even if there are outstanding voters, NEIN already blocks
        e = _entscheidung(AbstimmungsTyp.VETO, ["A", "B", "C"],
                          [_stimme("A", StimmeTyp.NEIN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ABGELEHNT


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 10 — berechne_ergebnis() — EINSTIMMIGKEIT
# ════════════════════════════════════════════════════════════════════════════════

class TestBerechneErgebnisEinstimmigkeit:
    def test_all_ja_angenommen(self):
        e = _entscheidung(AbstimmungsTyp.EINSTIMMIGKEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ANGENOMMEN

    def test_one_nein_abgelehnt(self):
        e = _entscheidung(AbstimmungsTyp.EINSTIMMIGKEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.NEIN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ABGELEHNT

    def test_outstanding_offen(self):
        e = _entscheidung(AbstimmungsTyp.EINSTIMMIGKEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA)])
        assert e.berechne_ergebnis() == KollaborationsStatus.OFFEN

    def test_no_votes_outstanding_offen(self):
        e = _entscheidung(AbstimmungsTyp.EINSTIMMIGKEIT, ["A"], [])
        assert e.berechne_ergebnis() == KollaborationsStatus.OFFEN

    def test_nein_blocks_even_with_outstanding(self):
        e = _entscheidung(AbstimmungsTyp.EINSTIMMIGKEIT, ["A", "B", "C"],
                          [_stimme("A", StimmeTyp.NEIN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ABGELEHNT


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 11 — berechne_ergebnis() — EINFACHE_MEHRHEIT
# ════════════════════════════════════════════════════════════════════════════════

class TestBerechneErgebnisEinfacheMehrheit:
    def test_outstanding_offen(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA)])
        assert e.berechne_ergebnis() == KollaborationsStatus.OFFEN

    def test_majority_ja_angenommen(self):
        # 2 JA, 1 NEIN → 66.7% > 50%
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B", "C"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA),
                           _stimme("C", StimmeTyp.NEIN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ANGENOMMEN

    def test_half_not_majority_abgelehnt(self):
        # 1 JA, 1 NEIN → 50% which is NOT > 50%
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.NEIN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ABGELEHNT

    def test_all_nein_abgelehnt(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.NEIN), _stimme("B", StimmeTyp.NEIN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ABGELEHNT

    def test_all_enthalten_offen(self):
        # entscheidende = 0 → OFFEN
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.ENTHALTEN), _stimme("B", StimmeTyp.ENTHALTEN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.OFFEN

    def test_all_ja_angenommen(self):
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ANGENOMMEN

    def test_enthalten_ignored_in_calculation(self):
        # 1 JA, 1 ENTHALTEN, 1 NEIN → entscheidende=2, ja_pct=50% → ABGELEHNT
        e = _entscheidung(AbstimmungsTyp.EINFACHE_MEHRHEIT, ["A", "B", "C"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.ENTHALTEN),
                           _stimme("C", StimmeTyp.NEIN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ABGELEHNT


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 12 — berechne_ergebnis() — QUALIFIZIERTE_MEHRHEIT
# ════════════════════════════════════════════════════════════════════════════════

class TestBerechneErgebnisQualifizierteMehrheit:
    def test_outstanding_offen(self):
        e = _entscheidung(AbstimmungsTyp.QUALIFIZIERTE_MEHRHEIT, ["A", "B", "C"],
                          [_stimme("A", StimmeTyp.JA)])
        assert e.berechne_ergebnis() == KollaborationsStatus.OFFEN

    def test_above_threshold_angenommen(self):
        # 2 JA, 0 NEIN → 100% > 66.7%
        e = _entscheidung(AbstimmungsTyp.QUALIFIZIERTE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ANGENOMMEN

    def test_two_of_three_ja_angenommen(self):
        # 2 JA, 1 NEIN → 66.67% > 66.7%? No: 66.67 > 66.7 is False actually
        # 2/3 = 66.666... NOT > 66.7 → ABGELEHNT
        e = _entscheidung(AbstimmungsTyp.QUALIFIZIERTE_MEHRHEIT, ["A", "B", "C"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA),
                           _stimme("C", StimmeTyp.NEIN)])
        # 66.666 > 66.7 is False → ABGELEHNT
        assert e.berechne_ergebnis() == KollaborationsStatus.ABGELEHNT

    def test_three_of_four_ja_angenommen(self):
        # 3 JA, 1 NEIN → 75% > 66.7%
        e = _entscheidung(AbstimmungsTyp.QUALIFIZIERTE_MEHRHEIT, ["A", "B", "C", "D"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.JA),
                           _stimme("C", StimmeTyp.JA), _stimme("D", StimmeTyp.NEIN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ANGENOMMEN

    def test_below_threshold_abgelehnt(self):
        # 1 JA, 1 NEIN → 50% <= 66.7%
        e = _entscheidung(AbstimmungsTyp.QUALIFIZIERTE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.JA), _stimme("B", StimmeTyp.NEIN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.ABGELEHNT

    def test_all_enthalten_offen(self):
        e = _entscheidung(AbstimmungsTyp.QUALIFIZIERTE_MEHRHEIT, ["A", "B"],
                          [_stimme("A", StimmeTyp.ENTHALTEN), _stimme("B", StimmeTyp.ENTHALTEN)])
        assert e.berechne_ergebnis() == KollaborationsStatus.OFFEN


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 13 — Default decisions (E-001, E-002, E-003)
# ════════════════════════════════════════════════════════════════════════════════

class TestDefaultEntscheidungen:
    def setup_method(self):
        self.entscheidungen = get_default_entscheidungen()
        self.e1 = next(e for e in self.entscheidungen if e.entscheidung_id == "E-001")
        self.e2 = next(e for e in self.entscheidungen if e.entscheidung_id == "E-002")
        self.e3 = next(e for e in self.entscheidungen if e.entscheidung_id == "E-003")

    def test_three_default_decisions(self):
        assert len(self.entscheidungen) == 3

    def test_e001_is_einfache_mehrheit(self):
        assert self.e1.abstimmungs_typ == AbstimmungsTyp.EINFACHE_MEHRHEIT

    def test_e002_is_veto(self):
        assert self.e2.abstimmungs_typ == AbstimmungsTyp.VETO

    def test_e003_is_einstimmigkeit(self):
        assert self.e3.abstimmungs_typ == AbstimmungsTyp.EINSTIMMIGKEIT

    def test_e001_ergebnis_offen(self):
        assert self.e1.berechne_ergebnis() == KollaborationsStatus.OFFEN

    def test_e002_ergebnis_abgelehnt(self):
        assert self.e2.berechne_ergebnis() == KollaborationsStatus.ABGELEHNT

    def test_e003_ergebnis_angenommen(self):
        assert self.e3.berechne_ergebnis() == KollaborationsStatus.ANGENOMMEN

    def test_e001_ausstehende_user_c(self):
        assert self.e1.ausstehende_stimmer() == ["USER-C"]

    def test_e002_no_ausstehende(self):
        assert self.e2.ausstehende_stimmer() == []

    def test_e003_no_ausstehende(self):
        assert self.e3.ausstehende_stimmer() == []

    def test_e001_beteiligung_pct(self):
        # 2 of 3 voted → 66.67%
        pct = self.e1.beteiligung_pct()
        assert abs(pct - 66.6666) < 0.01

    def test_e002_beteiligung_pct_100(self):
        assert self.e2.beteiligung_pct() == 100.0

    def test_e003_beteiligung_pct_100(self):
        assert self.e3.beteiligung_pct() == 100.0

    def test_e001_ja_stimmen(self):
        assert self.e1.ja_stimmen() == 2

    def test_e002_nein_stimmen(self):
        assert self.e2.nein_stimmen() == 1

    def test_e003_ja_stimmen(self):
        assert self.e3.ja_stimmen() == 2

    def test_e002_ja_stimmen(self):
        assert self.e2.ja_stimmen() == 1

    def test_e001_workflow_instanz(self):
        assert self.e1.workflow_instanz_id == "WI-K-001"

    def test_e002_workflow_instanz(self):
        assert self.e2.workflow_instanz_id == "WI-AP-002"

    def test_e003_workflow_instanz(self):
        assert self.e3.workflow_instanz_id == "WI-S-003"

    def test_e002_kommentar_on_nein(self):
        nein = next(s for s in self.e2.abgegebene_stimmen if s.stimme == StimmeTyp.NEIN)
        assert nein.kommentar == "Preis zu hoch"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 14 — Stimme dataclass
# ════════════════════════════════════════════════════════════════════════════════

class TestStimmeDataclass:
    def test_stimme_fields(self):
        s = Stimme("U-001", StimmeTyp.JA, NOW, "Genehmigt")
        assert s.stimmer_id == "U-001"
        assert s.stimme == StimmeTyp.JA
        assert s.abgegeben_am == NOW
        assert s.kommentar == "Genehmigt"

    def test_default_kommentar(self):
        s = Stimme("U-001", StimmeTyp.ENTHALTEN, NOW)
        assert s.kommentar == ""


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 15 — ValidierungsErgebnis dataclass
# ════════════════════════════════════════════════════════════════════════════════

class TestValidierungsErgebnis:
    def test_ist_gueltig_true(self):
        e = ValidierungsErgebnis(ValidierungsStatus.GUELTIG)
        assert e.ist_gueltig is True

    def test_ist_gueltig_false_for_ungueltig(self):
        e = ValidierungsErgebnis(ValidierungsStatus.UNGUELTIG)
        assert e.ist_gueltig is False

    def test_ist_gueltig_false_for_warnung(self):
        e = ValidierungsErgebnis(ValidierungsStatus.WARNUNG)
        assert e.ist_gueltig is False

    def test_default_empty_lists(self):
        e = ValidierungsErgebnis(ValidierungsStatus.GUELTIG)
        assert e.fehler == []
        assert e.warnungen == []
        assert e.hinweise == []


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 16 — FastAPI endpoint tests
# ════════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


class TestValidierungRegelnEndpoint:
    def test_get_regeln_200(self, client):
        r = client.get("/api/v1/process/validierung/regeln")
        assert r.status_code == 200

    def test_get_regeln_returns_list(self, client):
        r = client.get("/api/v1/process/validierung/regeln")
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 5

    def test_get_regeln_has_expected_ids(self, client):
        r = client.get("/api/v1/process/validierung/regeln")
        ids = [item["regel_id"] for item in r.json()]
        for expected in ["VR-001", "VR-002", "VR-003", "VR-004", "VR-005"]:
            assert expected in ids

    def test_get_regeln_fields(self, client):
        r = client.get("/api/v1/process/validierung/regeln")
        item = r.json()[0]
        for key in ["regel_id", "name", "regel_typ", "schwere", "feld", "beschreibung"]:
            assert key in item


class TestValidierungPruefeEndpoint:
    def test_pruefe_valid_data(self, client):
        payload = {"daten": {"lieferant_id": "L1", "menge_tonnen": 100.0, "preis_eur_t": 200.0}}
        r = client.post("/api/v1/process/validierung/pruefe", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "GUELTIG"
        assert data["ist_gueltig"] is True

    def test_pruefe_missing_lieferant(self, client):
        payload = {"daten": {"menge_tonnen": 100.0, "preis_eur_t": 200.0}}
        r = client.post("/api/v1/process/validierung/pruefe", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "UNGUELTIG"
        assert data["fehler_anzahl"] >= 1

    def test_pruefe_response_fields(self, client):
        r = client.post("/api/v1/process/validierung/pruefe",
                        json={"daten": {"lieferant_id": "L1", "menge_tonnen": 100.0, "preis_eur_t": 200.0}})
        data = r.json()
        for key in ["status", "ist_gueltig", "fehler_anzahl", "warnungs_anzahl", "hinweis_anzahl", "fehler"]:
            assert key in data

    def test_pruefe_empty_daten_ungueltig(self, client):
        r = client.post("/api/v1/process/validierung/pruefe", json={"daten": {}})
        assert r.status_code == 200
        assert r.json()["status"] == "UNGUELTIG"

    def test_pruefe_missing_daten_key_uses_empty(self, client):
        r = client.post("/api/v1/process/validierung/pruefe", json={})
        assert r.status_code == 200
        # Falls back to empty dict
        assert r.json()["status"] == "UNGUELTIG"


class TestKollaborationEntscheidungenEndpoint:
    def test_get_entscheidungen_200(self, client):
        r = client.get("/api/v1/process/kollaboration/entscheidungen")
        assert r.status_code == 200

    def test_get_entscheidungen_returns_three(self, client):
        r = client.get("/api/v1/process/kollaboration/entscheidungen")
        assert len(r.json()) == 3

    def test_get_entscheidungen_fields(self, client):
        r = client.get("/api/v1/process/kollaboration/entscheidungen")
        item = r.json()[0]
        for key in ["entscheidung_id", "abstimmungs_typ", "status", "berechnetes_ergebnis",
                    "ausstehende_stimmer", "beteiligung_pct", "ja_stimmen", "nein_stimmen"]:
            assert key in item

    def test_e001_ergebnis_in_response(self, client):
        r = client.get("/api/v1/process/kollaboration/entscheidungen")
        e001 = next(e for e in r.json() if e["entscheidung_id"] == "E-001")
        assert e001["berechnetes_ergebnis"] == "OFFEN"

    def test_e002_abgelehnt_in_response(self, client):
        r = client.get("/api/v1/process/kollaboration/entscheidungen")
        e002 = next(e for e in r.json() if e["entscheidung_id"] == "E-002")
        assert e002["berechnetes_ergebnis"] == "ABGELEHNT"

    def test_e003_angenommen_in_response(self, client):
        r = client.get("/api/v1/process/kollaboration/entscheidungen")
        e003 = next(e for e in r.json() if e["entscheidung_id"] == "E-003")
        assert e003["berechnetes_ergebnis"] == "ANGENOMMEN"


class TestKollaborationPruefeErgebnisEndpoint:
    def test_pruefe_e001(self, client):
        r = client.post("/api/v1/process/kollaboration/pruefe-ergebnis",
                        json={"entscheidung_id": "E-001"})
        assert r.status_code == 200
        data = r.json()
        assert data["entscheidung_id"] == "E-001"
        assert data["berechnetes_ergebnis"] == "OFFEN"

    def test_pruefe_e002(self, client):
        r = client.post("/api/v1/process/kollaboration/pruefe-ergebnis",
                        json={"entscheidung_id": "E-002"})
        assert r.status_code == 200
        assert r.json()["berechnetes_ergebnis"] == "ABGELEHNT"

    def test_pruefe_e003(self, client):
        r = client.post("/api/v1/process/kollaboration/pruefe-ergebnis",
                        json={"entscheidung_id": "E-003"})
        assert r.status_code == 200
        assert r.json()["berechnetes_ergebnis"] == "ANGENOMMEN"

    def test_pruefe_unknown_returns_fehler(self, client):
        r = client.post("/api/v1/process/kollaboration/pruefe-ergebnis",
                        json={"entscheidung_id": "E-999"})
        assert r.status_code == 200
        assert "fehler" in r.json()

    def test_pruefe_response_has_beteiligung(self, client):
        r = client.post("/api/v1/process/kollaboration/pruefe-ergebnis",
                        json={"entscheidung_id": "E-001"})
        data = r.json()
        assert "beteiligung_pct" in data
        assert abs(data["beteiligung_pct"] - 66.6666) < 0.01

    def test_pruefe_response_has_ausstehende(self, client):
        r = client.post("/api/v1/process/kollaboration/pruefe-ergebnis",
                        json={"entscheidung_id": "E-001"})
        assert r.json()["ausstehende_stimmer"] == ["USER-C"]
