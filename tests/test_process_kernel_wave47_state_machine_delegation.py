"""
Wave 47 — Process State Machine & Workflow Delegation Contracts
Tests für:
  - app.core.process_state_machine_contracts
  - app.core.workflow_delegation_contracts

70+ Tests, kein Import aus app.api oder app.infrastructure.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.core.process_state_machine_contracts import (
    AutomatStatus,
    UebergangsBedingung,
    UebergangsErgebnis,
    Uebergang,
    ZustandTyp,
    Zustand,
    ZustandsAutomatDefinition,
    fuehre_uebergang_aus,
    get_default_zustandsautomat,
)
from app.core.workflow_delegation_contracts import (
    DelegationsEntscheidung,
    DelegationsRegel,
    DelegationsStatus,
    DelegationsTyp,
    EskalationsStufe,
    get_default_delegations_regeln,
    loeseauf_delegation,
)


# ===========================================================================
# Fixtures — State Machine
# ===========================================================================

@pytest.fixture()
def zustand_start() -> Zustand:
    return Zustand("Z-S", "Start", ZustandTyp.START, "Startzustand")


@pytest.fixture()
def zustand_normal() -> Zustand:
    return Zustand("Z-N", "Normal", ZustandTyp.NORMAL, "Normaler Zustand")


@pytest.fixture()
def zustand_warte() -> Zustand:
    return Zustand("Z-W", "Warte", ZustandTyp.WARTE, "Wartezustand")


@pytest.fixture()
def zustand_entscheidung() -> Zustand:
    return Zustand("Z-E", "Entscheidung", ZustandTyp.ENTSCHEIDUNG, "Entscheidungszustand")


@pytest.fixture()
def zustand_abschluss() -> Zustand:
    return Zustand("Z-A", "Abschluss", ZustandTyp.ABSCHLUSS, "Abschlusszustand")


@pytest.fixture()
def zustand_fehler() -> Zustand:
    return Zustand("Z-F", "Fehler", ZustandTyp.FEHLER, "Fehlerzustand")


@pytest.fixture()
def uebergang_immer() -> Uebergang:
    return Uebergang("U-IMM", "Z-S", "Z-N", UebergangsBedingung.IMMER, prioritaet=10)


@pytest.fixture()
def uebergang_feld() -> Uebergang:
    return Uebergang("U-FLD", "Z-N", "Z-A", UebergangsBedingung.FELD_VORHANDEN, feld="genehmigung", prioritaet=5)


@pytest.fixture()
def uebergang_wert_gleich() -> Uebergang:
    return Uebergang("U-WG", "Z-E", "Z-A", UebergangsBedingung.WERT_GLEICH,
                     feld="entscheidung", wert="ja", prioritaet=1)


@pytest.fixture()
def uebergang_rolle() -> Uebergang:
    return Uebergang("U-ROL", "Z-W", "Z-E", UebergangsBedingung.ROLLE_ERLAUBT,
                     wert="leiter", prioritaet=3)


@pytest.fixture()
def uebergang_groesser() -> Uebergang:
    return Uebergang("U-GR", "Z-N", "Z-W", UebergangsBedingung.WERT_GROESSER,
                     feld="betrag", wert="500", prioritaet=2)


@pytest.fixture()
def einfacher_automat(zustand_start, zustand_normal, zustand_abschluss,
                      uebergang_immer, uebergang_feld) -> ZustandsAutomatDefinition:
    return ZustandsAutomatDefinition(
        automat_id="ZA-TEST-001",
        automat_name="Test-Automat",
        zustande=[zustand_start, zustand_normal, zustand_abschluss],
        uebergaenge=[uebergang_immer, uebergang_feld],
        beschreibung="Einfacher Test-Automat",
    )


@pytest.fixture()
def default_automat() -> ZustandsAutomatDefinition:
    return get_default_zustandsautomat()


# ===========================================================================
# Fixtures — Delegation
# ===========================================================================

BASIS_DT = datetime(2026, 3, 10, 9, 0)


@pytest.fixture()
def regel_stellvertreter() -> DelegationsRegel:
    return DelegationsRegel(
        regel_id="T-DR-001",
        von_subjekt_id="anna",
        zu_subjekt_id="bernd",
        delegations_typ=DelegationsTyp.STELLVERTRETER,
        status=DelegationsStatus.AKTIV,
        gueltig_ab=datetime(2026, 3, 1),
        gueltig_bis=datetime(2026, 3, 31),
        beschreibung="Anna im Urlaub",
    )


@pytest.fixture()
def regel_eskalation() -> DelegationsRegel:
    return DelegationsRegel(
        regel_id="T-DR-002",
        von_subjekt_id="anna",
        zu_subjekt_id="chef",
        delegations_typ=DelegationsTyp.ESKALATION,
        status=DelegationsStatus.AKTIV,
        gueltig_ab=datetime(2026, 3, 1),
        eskalations_nach_minuten=90,
        eskalations_stufe=EskalationsStufe.STUFE_1,
        aufgaben_typen=["freigabe", "kontrakt_freigabe"],
        beschreibung="Eskalation nach 90 Minuten",
    )


@pytest.fixture()
def regel_widerrufen() -> DelegationsRegel:
    return DelegationsRegel(
        regel_id="T-DR-003",
        von_subjekt_id="anna",
        zu_subjekt_id="carla",
        delegations_typ=DelegationsTyp.DIREKT,
        status=DelegationsStatus.WIDERRUFEN,
        gueltig_ab=datetime(2026, 3, 1),
        beschreibung="Widerrufen",
    )


@pytest.fixture()
def default_regeln() -> list[DelegationsRegel]:
    return get_default_delegations_regeln()


# ===========================================================================
# --- MODUL 1: process_state_machine_contracts ---
# ===========================================================================

# ---------------------------------------------------------------------------
# ZustandTyp — Enum-Werte
# ---------------------------------------------------------------------------

def test_zustand_typ_start_existiert():
    assert ZustandTyp.START.value == "START"


def test_zustand_typ_normal_existiert():
    assert ZustandTyp.NORMAL.value == "NORMAL"


def test_zustand_typ_warte_existiert():
    assert ZustandTyp.WARTE.value == "WARTE"


def test_zustand_typ_entscheidung_existiert():
    assert ZustandTyp.ENTSCHEIDUNG.value == "ENTSCHEIDUNG"


def test_zustand_typ_abschluss_existiert():
    assert ZustandTyp.ABSCHLUSS.value == "ABSCHLUSS"


def test_zustand_typ_fehler_existiert():
    assert ZustandTyp.FEHLER.value == "FEHLER"


def test_zustand_typ_alle_sechs_werte():
    assert len(ZustandTyp) == 6


# ---------------------------------------------------------------------------
# UebergangsBedingung — Enum-Werte
# ---------------------------------------------------------------------------

def test_bedingung_immer_existiert():
    assert UebergangsBedingung.IMMER.value == "IMMER"


def test_bedingung_feld_vorhanden_existiert():
    assert UebergangsBedingung.FELD_VORHANDEN.value == "FELD_VORHANDEN"


def test_bedingung_wert_gleich_existiert():
    assert UebergangsBedingung.WERT_GLEICH.value == "WERT_GLEICH"


def test_bedingung_rolle_erlaubt_existiert():
    assert UebergangsBedingung.ROLLE_ERLAUBT.value == "ROLLE_ERLAUBT"


def test_bedingung_wert_groesser_existiert():
    assert UebergangsBedingung.WERT_GROESSER.value == "WERT_GROESSER"


def test_bedingung_fuenf_werte():
    assert len(UebergangsBedingung) == 5


# ---------------------------------------------------------------------------
# AutomatStatus — Enum-Werte
# ---------------------------------------------------------------------------

def test_automat_status_bereit():
    assert AutomatStatus.BEREIT.value == "BEREIT"


def test_automat_status_laufend():
    assert AutomatStatus.LAUFEND.value == "LAUFEND"


def test_automat_status_abgeschlossen():
    assert AutomatStatus.ABGESCHLOSSEN.value == "ABGESCHLOSSEN"


def test_automat_status_fehlgeschlagen():
    assert AutomatStatus.FEHLGESCHLAGEN.value == "FEHLGESCHLAGEN"


def test_automat_status_suspendiert():
    assert AutomatStatus.SUSPENDIERT.value == "SUSPENDIERT"


# ---------------------------------------------------------------------------
# Zustand.ist_endpunkt
# ---------------------------------------------------------------------------

def test_zustand_start_kein_endpunkt(zustand_start):
    assert zustand_start.ist_endpunkt is False


def test_zustand_normal_kein_endpunkt(zustand_normal):
    assert zustand_normal.ist_endpunkt is False


def test_zustand_warte_kein_endpunkt(zustand_warte):
    assert zustand_warte.ist_endpunkt is False


def test_zustand_entscheidung_kein_endpunkt(zustand_entscheidung):
    assert zustand_entscheidung.ist_endpunkt is False


def test_zustand_abschluss_ist_endpunkt(zustand_abschluss):
    assert zustand_abschluss.ist_endpunkt is True


def test_zustand_fehler_ist_endpunkt(zustand_fehler):
    assert zustand_fehler.ist_endpunkt is True


# ---------------------------------------------------------------------------
# Zustand.as_dict
# ---------------------------------------------------------------------------

def test_zustand_as_dict_enthaelt_pflichtfelder(zustand_abschluss):
    d = zustand_abschluss.as_dict()
    assert d["zustand_id"] == "Z-A"
    assert d["zustand_name"] == "Abschluss"
    assert d["typ"] == "ABSCHLUSS"
    assert d["ist_endpunkt"] is True
    assert "beschreibung" in d


def test_zustand_as_dict_endpunkt_false_bei_normal(zustand_normal):
    d = zustand_normal.as_dict()
    assert d["ist_endpunkt"] is False
    assert d["typ"] == "NORMAL"


def test_zustand_as_dict_beschreibung_leer_standardwert():
    z = Zustand("Z-X", "Leer", ZustandTyp.NORMAL)
    d = z.as_dict()
    assert d["beschreibung"] == ""


# ---------------------------------------------------------------------------
# Uebergang.pruefe — IMMER
# ---------------------------------------------------------------------------

def test_pruefe_immer_leerer_kontext(uebergang_immer):
    assert uebergang_immer.pruefe({}) is True


def test_pruefe_immer_beliebiger_kontext(uebergang_immer):
    assert uebergang_immer.pruefe({"x": 1, "y": "abc"}) is True


# ---------------------------------------------------------------------------
# Uebergang.pruefe — FELD_VORHANDEN
# ---------------------------------------------------------------------------

def test_pruefe_feld_vorhanden_true(uebergang_feld):
    assert uebergang_feld.pruefe({"genehmigung": "ja"}) is True


def test_pruefe_feld_vorhanden_false_fehlendes_feld(uebergang_feld):
    assert uebergang_feld.pruefe({}) is False


def test_pruefe_feld_vorhanden_false_anderes_feld(uebergang_feld):
    assert uebergang_feld.pruefe({"andere": "sache"}) is False


# ---------------------------------------------------------------------------
# Uebergang.pruefe — WERT_GLEICH
# ---------------------------------------------------------------------------

def test_pruefe_wert_gleich_true(uebergang_wert_gleich):
    assert uebergang_wert_gleich.pruefe({"entscheidung": "ja"}) is True


def test_pruefe_wert_gleich_false_anderer_wert(uebergang_wert_gleich):
    assert uebergang_wert_gleich.pruefe({"entscheidung": "nein"}) is False


def test_pruefe_wert_gleich_false_feld_fehlt(uebergang_wert_gleich):
    # Kontext ohne das Feld → str(kontext.get(..., "")) == "ja" → False
    assert uebergang_wert_gleich.pruefe({}) is False


def test_pruefe_wert_gleich_string_konvertierung():
    # Numerischer Wert im Kontext muss als String verglichen werden
    u = Uebergang("U-WGS", "A", "B", UebergangsBedingung.WERT_GLEICH, feld="zahl", wert="42")
    assert u.pruefe({"zahl": 42}) is True


# ---------------------------------------------------------------------------
# Uebergang.pruefe — ROLLE_ERLAUBT
# ---------------------------------------------------------------------------

def test_pruefe_rolle_erlaubt_true(uebergang_rolle):
    assert uebergang_rolle.pruefe({"rolle": "leiter"}) is True


def test_pruefe_rolle_erlaubt_false_falsche_rolle(uebergang_rolle):
    assert uebergang_rolle.pruefe({"rolle": "sachbearbeiter"}) is False


def test_pruefe_rolle_erlaubt_false_kein_rolle_key(uebergang_rolle):
    assert uebergang_rolle.pruefe({}) is False


# ---------------------------------------------------------------------------
# Uebergang.pruefe — WERT_GROESSER
# ---------------------------------------------------------------------------

def test_pruefe_wert_groesser_true(uebergang_groesser):
    assert uebergang_groesser.pruefe({"betrag": 1000}) is True


def test_pruefe_wert_groesser_false_kleiner(uebergang_groesser):
    assert uebergang_groesser.pruefe({"betrag": 100}) is False


def test_pruefe_wert_groesser_false_gleich(uebergang_groesser):
    assert uebergang_groesser.pruefe({"betrag": 500}) is False


def test_pruefe_wert_groesser_feld_fehlt_gibt_false(uebergang_groesser):
    # Fehlendes Feld → float(0) > float("500") → False
    assert uebergang_groesser.pruefe({}) is False


def test_pruefe_wert_groesser_string_zahl(uebergang_groesser):
    assert uebergang_groesser.pruefe({"betrag": "999"}) is True


def test_pruefe_wert_groesser_typfehler_gibt_false():
    u = Uebergang("U-GR2", "A", "B", UebergangsBedingung.WERT_GROESSER,
                  feld="betrag", wert="500")
    assert u.pruefe({"betrag": "kein_float"}) is False


def test_pruefe_wert_groesser_wert_none_gibt_false():
    u = Uebergang("U-GR3", "A", "B", UebergangsBedingung.WERT_GROESSER,
                  feld="betrag", wert="500")
    assert u.pruefe({"betrag": None}) is False


# ---------------------------------------------------------------------------
# Uebergang.as_dict
# ---------------------------------------------------------------------------

def test_uebergang_as_dict_vollstaendig(uebergang_groesser):
    d = uebergang_groesser.as_dict()
    assert d["uebergang_id"] == "U-GR"
    assert d["von_zustand_id"] == "Z-N"
    assert d["zu_zustand_id"] == "Z-W"
    assert d["bedingung"] == "WERT_GROESSER"
    assert d["feld"] == "betrag"
    assert d["wert"] == "500"
    assert d["prioritaet"] == 2
    assert "beschreibung" in d


# ---------------------------------------------------------------------------
# UebergangsErgebnis
# ---------------------------------------------------------------------------

def test_uebergangs_ergebnis_as_dict_erfolg():
    ts = datetime(2026, 3, 10, 12, 0, 0)
    e = UebergangsErgebnis(
        instanz_id="INST-1",
        von_zustand_id="Z-S",
        zu_zustand_id="Z-N",
        angewendeter_uebergang_id="U-01",
        erfolg=True,
        begruendung="Test",
        ausgefuehrt_am=ts,
    )
    d = e.as_dict()
    assert d["instanz_id"] == "INST-1"
    assert d["erfolg"] is True
    assert d["ausgefuehrt_am"] == ts.isoformat()
    assert d["angewendeter_uebergang_id"] == "U-01"


def test_uebergangs_ergebnis_as_dict_misserfolg():
    ts = datetime(2026, 3, 10, 13, 0, 0)
    e = UebergangsErgebnis(
        instanz_id="INST-2",
        von_zustand_id="Z-N",
        zu_zustand_id="Z-N",
        angewendeter_uebergang_id="",
        erfolg=False,
        ausgefuehrt_am=ts,
    )
    d = e.as_dict()
    assert d["erfolg"] is False
    assert d["angewendeter_uebergang_id"] == ""


# ---------------------------------------------------------------------------
# ZustandsAutomatDefinition — start_zustand
# ---------------------------------------------------------------------------

def test_automat_start_zustand_gefunden(einfacher_automat, zustand_start):
    assert einfacher_automat.start_zustand is not None
    assert einfacher_automat.start_zustand.zustand_id == "Z-S"


def test_automat_start_zustand_none_wenn_kein_start():
    automat = ZustandsAutomatDefinition(
        automat_id="ZA-LEER",
        automat_name="Ohne Start",
        zustande=[Zustand("Z-N", "Normal", ZustandTyp.NORMAL)],
    )
    assert automat.start_zustand is None


# ---------------------------------------------------------------------------
# ZustandsAutomatDefinition — endpunkt_ids
# ---------------------------------------------------------------------------

def test_automat_endpunkt_ids_enthaelt_abschluss_und_fehler():
    automat = ZustandsAutomatDefinition(
        automat_id="ZA-EP",
        automat_name="Endpunkte",
        zustande=[
            Zustand("Z-S", "Start", ZustandTyp.START),
            Zustand("Z-A", "Ende", ZustandTyp.ABSCHLUSS),
            Zustand("Z-F", "Fehler", ZustandTyp.FEHLER),
            Zustand("Z-N", "Mitte", ZustandTyp.NORMAL),
        ],
    )
    ids = automat.endpunkt_ids
    assert "Z-A" in ids
    assert "Z-F" in ids
    assert "Z-S" not in ids
    assert "Z-N" not in ids


def test_automat_endpunkt_ids_leer_wenn_keine_endpunkte():
    automat = ZustandsAutomatDefinition(
        automat_id="ZA-OE",
        automat_name="Ohne Endpunkte",
        zustande=[Zustand("Z-S", "Start", ZustandTyp.START)],
    )
    assert automat.endpunkt_ids == []


# ---------------------------------------------------------------------------
# ZustandsAutomatDefinition — finde_uebergaenge
# ---------------------------------------------------------------------------

def test_finde_uebergaenge_immer_gefunden(einfacher_automat):
    ergebnisse = einfacher_automat.finde_uebergaenge("Z-S", {})
    ids = [u.uebergang_id for u in ergebnisse]
    assert "U-IMM" in ids


def test_finde_uebergaenge_feld_nicht_gefunden_ohne_kontext(einfacher_automat):
    # U-FLD benötigt "genehmigung" im Kontext
    ergebnisse = einfacher_automat.finde_uebergaenge("Z-N", {})
    assert len(ergebnisse) == 0


def test_finde_uebergaenge_feld_gefunden_mit_kontext(einfacher_automat):
    ergebnisse = einfacher_automat.finde_uebergaenge("Z-N", {"genehmigung": "ja"})
    assert len(ergebnisse) == 1
    assert ergebnisse[0].uebergang_id == "U-FLD"


def test_finde_uebergaenge_prioritaet_aufsteigend():
    u_hoch = Uebergang("U-H", "Z-S", "Z-N", UebergangsBedingung.IMMER, prioritaet=20)
    u_niedrig = Uebergang("U-N", "Z-S", "Z-A", UebergangsBedingung.IMMER, prioritaet=5)
    automat = ZustandsAutomatDefinition(
        automat_id="ZA-PRIO",
        automat_name="Priorität-Test",
        zustande=[
            Zustand("Z-S", "Start", ZustandTyp.START),
            Zustand("Z-N", "Normal", ZustandTyp.NORMAL),
            Zustand("Z-A", "Ende", ZustandTyp.ABSCHLUSS),
        ],
        uebergaenge=[u_hoch, u_niedrig],
    )
    ergebnisse = automat.finde_uebergaenge("Z-S", {})
    assert len(ergebnisse) == 2
    # Niedrigere Zahl = höhere Priorität → zuerst
    assert ergebnisse[0].uebergang_id == "U-N"
    assert ergebnisse[1].uebergang_id == "U-H"


def test_finde_uebergaenge_falscher_von_zustand_leer(einfacher_automat):
    ergebnisse = einfacher_automat.finde_uebergaenge("Z-UNBEKANNT", {})
    assert ergebnisse == []


# ---------------------------------------------------------------------------
# ZustandsAutomatDefinition — as_dict
# ---------------------------------------------------------------------------

def test_automat_as_dict_vollstaendig(einfacher_automat):
    d = einfacher_automat.as_dict()
    assert d["automat_id"] == "ZA-TEST-001"
    assert d["anzahl_zustaende"] == 3
    assert d["anzahl_uebergaenge"] == 2
    assert d["start_zustand_id"] == "Z-S"
    assert isinstance(d["endpunkt_ids"], list)
    assert isinstance(d["zustande"], list)
    assert isinstance(d["uebergaenge"], list)


def test_automat_as_dict_start_zustand_id_none_wenn_kein_start():
    automat = ZustandsAutomatDefinition(
        automat_id="ZA-NS",
        automat_name="Kein Start",
        zustande=[Zustand("Z-N", "Normal", ZustandTyp.NORMAL)],
    )
    d = automat.as_dict()
    assert d["start_zustand_id"] is None


# ---------------------------------------------------------------------------
# fuehre_uebergang_aus
# ---------------------------------------------------------------------------

def test_fuehre_uebergang_aus_erfolg(einfacher_automat):
    ergebnis = fuehre_uebergang_aus("INST-A", einfacher_automat, "Z-S", {})
    assert ergebnis.erfolg is True
    assert ergebnis.zu_zustand_id == "Z-N"
    assert ergebnis.angewendeter_uebergang_id == "U-IMM"
    assert ergebnis.instanz_id == "INST-A"


def test_fuehre_uebergang_aus_kein_uebergang_moeglich(einfacher_automat):
    # Z-N ohne "genehmigung" im Kontext → kein Übergang
    ergebnis = fuehre_uebergang_aus("INST-B", einfacher_automat, "Z-N", {})
    assert ergebnis.erfolg is False
    assert ergebnis.zu_zustand_id == "Z-N"  # bleibt im selben Zustand
    assert ergebnis.angewendeter_uebergang_id == ""


def test_fuehre_uebergang_aus_prioritaet_gewinnt():
    u_low = Uebergang("U-LOW", "Z-S", "Z-N", UebergangsBedingung.IMMER, prioritaet=5)
    u_high = Uebergang("U-HIGH", "Z-S", "Z-A", UebergangsBedingung.IMMER, prioritaet=1)
    automat = ZustandsAutomatDefinition(
        automat_id="ZA-PWIN",
        automat_name="Priorität-Gewinner",
        zustande=[
            Zustand("Z-S", "Start", ZustandTyp.START),
            Zustand("Z-N", "Normal", ZustandTyp.NORMAL),
            Zustand("Z-A", "Ende", ZustandTyp.ABSCHLUSS),
        ],
        uebergaenge=[u_low, u_high],
    )
    ergebnis = fuehre_uebergang_aus("INST-C", automat, "Z-S", {})
    assert ergebnis.erfolg is True
    assert ergebnis.angewendeter_uebergang_id == "U-HIGH"
    assert ergebnis.zu_zustand_id == "Z-A"


def test_fuehre_uebergang_aus_mit_ausgefuehrt_am():
    ts = datetime(2026, 3, 15, 8, 30, 0)
    u = Uebergang("U-X", "Z-S", "Z-N", UebergangsBedingung.IMMER)
    automat = ZustandsAutomatDefinition(
        automat_id="ZA-TS",
        automat_name="Timestamp-Test",
        zustande=[
            Zustand("Z-S", "Start", ZustandTyp.START),
            Zustand("Z-N", "Normal", ZustandTyp.NORMAL),
        ],
        uebergaenge=[u],
    )
    ergebnis = fuehre_uebergang_aus("INST-D", automat, "Z-S", {}, ausgefuehrt_am=ts)
    assert ergebnis.ausgefuehrt_am == ts
    assert ergebnis.as_dict()["ausgefuehrt_am"] == ts.isoformat()


def test_fuehre_uebergang_aus_misserfolg_begruendung_gesetzt(einfacher_automat):
    ergebnis = fuehre_uebergang_aus("INST-E", einfacher_automat, "Z-A", {})
    assert ergebnis.erfolg is False
    assert len(ergebnis.begruendung) > 0


# ---------------------------------------------------------------------------
# get_default_zustandsautomat
# ---------------------------------------------------------------------------

def test_default_automat_id(default_automat):
    assert default_automat.automat_id == "ZA-KONTRAKT-001"


def test_default_automat_name(default_automat):
    assert "Kontrakt" in default_automat.automat_name


def test_default_automat_sechs_zustaende(default_automat):
    assert len(default_automat.zustande) == 6


def test_default_automat_sechs_uebergaenge(default_automat):
    assert len(default_automat.uebergaenge) == 6


def test_default_automat_start_zustand_z01(default_automat):
    assert default_automat.start_zustand is not None
    assert default_automat.start_zustand.zustand_id == "Z-01"
    assert default_automat.start_zustand.typ == ZustandTyp.START


def test_default_automat_endpunkt_ids_z05_und_z06(default_automat):
    ids = default_automat.endpunkt_ids
    assert "Z-05" in ids
    assert "Z-06" in ids
    assert len(ids) == 2


def test_default_automat_zustand_typen(default_automat):
    typen = {z.zustand_id: z.typ for z in default_automat.zustande}
    assert typen["Z-01"] == ZustandTyp.START
    assert typen["Z-02"] == ZustandTyp.NORMAL
    assert typen["Z-03"] == ZustandTyp.WARTE
    assert typen["Z-04"] == ZustandTyp.ENTSCHEIDUNG
    assert typen["Z-05"] == ZustandTyp.ABSCHLUSS
    assert typen["Z-06"] == ZustandTyp.FEHLER


def test_default_automat_uebergang_ids(default_automat):
    ids = {u.uebergang_id for u in default_automat.uebergaenge}
    for expected in ["U-01", "U-02", "U-03", "U-04", "U-05", "U-06"]:
        assert expected in ids


def test_default_automat_u05_genehmigt_pfad(default_automat):
    # U-05: Z-04 → Z-05 wenn entscheidung=="genehmigt"
    ergebnis = fuehre_uebergang_aus("TEST", default_automat, "Z-04", {"entscheidung": "genehmigt"})
    assert ergebnis.erfolg is True
    assert ergebnis.zu_zustand_id == "Z-05"


def test_default_automat_u06_abgelehnt_pfad(default_automat):
    # U-06: Z-04 → Z-06 wenn entscheidung=="abgelehnt"
    ergebnis = fuehre_uebergang_aus("TEST", default_automat, "Z-04", {"entscheidung": "abgelehnt"})
    assert ergebnis.erfolg is True
    assert ergebnis.zu_zustand_id == "Z-06"


def test_default_automat_u02_betrag_hoch_pfad(default_automat):
    # U-02 prio 5: Z-02 → Z-03 wenn betrag_eur > 10000
    ergebnis = fuehre_uebergang_aus("TEST", default_automat, "Z-02", {"betrag_eur": 50000})
    assert ergebnis.erfolg is True
    assert ergebnis.zu_zustand_id == "Z-03"


def test_default_automat_u03_standard_pfad(default_automat):
    # U-03 prio 10 (IMMER): Z-02 → Z-04 — nur wenn U-02 nicht greift
    ergebnis = fuehre_uebergang_aus("TEST", default_automat, "Z-02", {"betrag_eur": 100})
    assert ergebnis.erfolg is True
    assert ergebnis.zu_zustand_id == "Z-04"


# ===========================================================================
# --- MODUL 2: workflow_delegation_contracts ---
# ===========================================================================

# ---------------------------------------------------------------------------
# DelegationsTyp — Enum-Werte
# ---------------------------------------------------------------------------

def test_delegations_typ_direkt():
    assert DelegationsTyp.DIREKT.value == "DIREKT"


def test_delegations_typ_stellvertreter():
    assert DelegationsTyp.STELLVERTRETER.value == "STELLVERTRETER"


def test_delegations_typ_eskalation():
    assert DelegationsTyp.ESKALATION.value == "ESKALATION"


def test_delegations_typ_pool():
    assert DelegationsTyp.POOL.value == "POOL"


def test_delegations_typ_vier_werte():
    assert len(DelegationsTyp) == 4


# ---------------------------------------------------------------------------
# DelegationsStatus — Enum-Werte
# ---------------------------------------------------------------------------

def test_delegations_status_aktiv():
    assert DelegationsStatus.AKTIV.value == "AKTIV"


def test_delegations_status_abgelaufen():
    assert DelegationsStatus.ABGELAUFEN.value == "ABGELAUFEN"


def test_delegations_status_widerrufen():
    assert DelegationsStatus.WIDERRUFEN.value == "WIDERRUFEN"


def test_delegations_status_angenommen():
    assert DelegationsStatus.ANGENOMMEN.value == "ANGENOMMEN"


def test_delegations_status_abgelehnt():
    assert DelegationsStatus.ABGELEHNT.value == "ABGELEHNT"


# ---------------------------------------------------------------------------
# EskalationsStufe — Enum-Werte
# ---------------------------------------------------------------------------

def test_eskalations_stufe_stufe_1():
    assert EskalationsStufe.STUFE_1.value == "STUFE_1"


def test_eskalations_stufe_stufe_2():
    assert EskalationsStufe.STUFE_2.value == "STUFE_2"


def test_eskalations_stufe_stufe_3():
    assert EskalationsStufe.STUFE_3.value == "STUFE_3"


def test_eskalations_stufe_keine():
    assert EskalationsStufe.KEINE.value == "KEINE"


# ---------------------------------------------------------------------------
# DelegationsRegel.ist_aktiv
# ---------------------------------------------------------------------------

def test_delegations_regel_ist_aktiv_true(regel_stellvertreter):
    assert regel_stellvertreter.ist_aktiv is True


def test_delegations_regel_ist_aktiv_false_abgelaufen():
    r = DelegationsRegel(
        regel_id="X", von_subjekt_id="a", zu_subjekt_id="b",
        delegations_typ=DelegationsTyp.DIREKT,
        status=DelegationsStatus.ABGELAUFEN,
        gueltig_ab=datetime(2026, 1, 1),
    )
    assert r.ist_aktiv is False


def test_delegations_regel_ist_aktiv_false_widerrufen(regel_widerrufen):
    assert regel_widerrufen.ist_aktiv is False


def test_delegations_regel_ist_aktiv_false_angenommen():
    r = DelegationsRegel(
        regel_id="X", von_subjekt_id="a", zu_subjekt_id="b",
        delegations_typ=DelegationsTyp.DIREKT,
        status=DelegationsStatus.ANGENOMMEN,
        gueltig_ab=datetime(2026, 1, 1),
    )
    assert r.ist_aktiv is False


def test_delegations_regel_ist_aktiv_false_abgelehnt():
    r = DelegationsRegel(
        regel_id="X", von_subjekt_id="a", zu_subjekt_id="b",
        delegations_typ=DelegationsTyp.DIREKT,
        status=DelegationsStatus.ABGELEHNT,
        gueltig_ab=datetime(2026, 1, 1),
    )
    assert r.ist_aktiv is False


# ---------------------------------------------------------------------------
# DelegationsRegel.ist_gueltig
# ---------------------------------------------------------------------------

def test_delegations_regel_ist_gueltig_in_range(regel_stellvertreter):
    ts = datetime(2026, 3, 15, 12, 0)
    assert regel_stellvertreter.ist_gueltig(ts) is True


def test_delegations_regel_ist_gueltig_vor_start(regel_stellvertreter):
    ts = datetime(2026, 2, 28, 23, 59)
    assert regel_stellvertreter.ist_gueltig(ts) is False


def test_delegations_regel_ist_gueltig_nach_ende(regel_stellvertreter):
    ts = datetime(2026, 4, 1, 0, 0)
    assert regel_stellvertreter.ist_gueltig(ts) is False


def test_delegations_regel_ist_gueltig_kein_gueltig_bis(regel_eskalation):
    # Kein gueltig_bis → kein Ende gesetzt
    ts = datetime(2030, 1, 1)
    assert regel_eskalation.ist_gueltig(ts) is True


def test_delegations_regel_ist_gueltig_false_bei_widerrufen(regel_widerrufen):
    ts = datetime(2026, 3, 15)
    assert regel_widerrufen.ist_gueltig(ts) is False


# ---------------------------------------------------------------------------
# DelegationsRegel.gilt_fuer_aufgabe
# ---------------------------------------------------------------------------

def test_gilt_fuer_aufgabe_leere_liste_alle_aufgaben(regel_stellvertreter):
    # aufgaben_typen leer → gilt für alles
    assert regel_stellvertreter.gilt_fuer_aufgabe("beliebige_aufgabe") is True
    assert regel_stellvertreter.gilt_fuer_aufgabe("kontrakt_freigabe") is True


def test_gilt_fuer_aufgabe_spezifische_liste_match(regel_eskalation):
    assert regel_eskalation.gilt_fuer_aufgabe("freigabe") is True
    assert regel_eskalation.gilt_fuer_aufgabe("kontrakt_freigabe") is True


def test_gilt_fuer_aufgabe_spezifische_liste_kein_match(regel_eskalation):
    assert regel_eskalation.gilt_fuer_aufgabe("bestellvorschlag_pruefung") is False


# ---------------------------------------------------------------------------
# DelegationsRegel.eskalations_zeitpunkt
# ---------------------------------------------------------------------------

def test_eskalations_zeitpunkt_korrekt(regel_eskalation):
    erstellt = datetime(2026, 3, 10, 10, 0, 0)
    erwartet = datetime(2026, 3, 10, 11, 30, 0)  # + 90 Minuten
    assert regel_eskalation.eskalations_zeitpunkt(erstellt) == erwartet


def test_eskalations_zeitpunkt_standard_60_minuten(regel_stellvertreter):
    erstellt = datetime(2026, 3, 10, 8, 0, 0)
    erwartet = datetime(2026, 3, 10, 9, 0, 0)
    assert regel_stellvertreter.eskalations_zeitpunkt(erstellt) == erwartet


# ---------------------------------------------------------------------------
# DelegationsRegel.as_dict
# ---------------------------------------------------------------------------

def test_delegations_regel_as_dict_vollstaendig(regel_stellvertreter):
    d = regel_stellvertreter.as_dict()
    assert d["regel_id"] == "T-DR-001"
    assert d["von_subjekt_id"] == "anna"
    assert d["zu_subjekt_id"] == "bernd"
    assert d["delegations_typ"] == "STELLVERTRETER"
    assert d["status"] == "AKTIV"
    assert d["ist_aktiv"] is True
    assert d["gueltig_bis"] is not None
    assert d["eskalations_stufe"] == "KEINE"


def test_delegations_regel_as_dict_gueltig_bis_none(regel_eskalation):
    d = regel_eskalation.as_dict()
    assert d["gueltig_bis"] is None


def test_delegations_regel_as_dict_eskalations_stufe_stufe1(regel_eskalation):
    d = regel_eskalation.as_dict()
    assert d["eskalations_stufe"] == "STUFE_1"
    assert d["eskalations_nach_minuten"] == 90


# ---------------------------------------------------------------------------
# DelegationsEntscheidung.as_dict
# ---------------------------------------------------------------------------

def test_delegations_entscheidung_as_dict_delegiert():
    ts = datetime(2026, 3, 10, 9, 0)
    e = DelegationsEntscheidung(
        original_subjekt_id="anna",
        aufgaben_typ="freigabe",
        delegiert_an="bernd",
        angewendete_regel_id="T-DR-001",
        delegations_typ=DelegationsTyp.STELLVERTRETER,
        eskalations_stufe=EskalationsStufe.KEINE,
        ist_delegiert=True,
        begruendung="Vertretung",
        entschieden_am=ts,
    )
    d = e.as_dict()
    assert d["original_subjekt_id"] == "anna"
    assert d["delegiert_an"] == "bernd"
    assert d["delegations_typ"] == "STELLVERTRETER"
    assert d["ist_delegiert"] is True
    assert d["entschieden_am"] == ts.isoformat()


def test_delegations_entscheidung_as_dict_kein_typ():
    ts = datetime(2026, 3, 10, 9, 0)
    e = DelegationsEntscheidung(
        original_subjekt_id="anna",
        aufgaben_typ="freigabe",
        delegiert_an="anna",
        angewendete_regel_id="",
        delegations_typ=None,
        eskalations_stufe=EskalationsStufe.KEINE,
        ist_delegiert=False,
        entschieden_am=ts,
    )
    d = e.as_dict()
    assert d["delegations_typ"] is None
    assert d["ist_delegiert"] is False


# ---------------------------------------------------------------------------
# loeseauf_delegation
# ---------------------------------------------------------------------------

def test_loeseauf_delegation_kein_match_gibt_original_zurueck():
    ts = datetime(2026, 3, 10)
    result = loeseauf_delegation("unbekannt", "freigabe", [], zum_zeitpunkt=ts)
    assert result.ist_delegiert is False
    assert result.delegiert_an == "unbekannt"
    assert result.angewendete_regel_id == ""
    assert result.delegations_typ is None


def test_loeseauf_delegation_stellvertreter_match(regel_stellvertreter):
    ts = datetime(2026, 3, 15, 10, 0)
    result = loeseauf_delegation("anna", "beliebige_aufgabe", [regel_stellvertreter], zum_zeitpunkt=ts)
    assert result.ist_delegiert is True
    assert result.delegiert_an == "bernd"
    assert result.angewendete_regel_id == "T-DR-001"


def test_loeseauf_delegation_widerrufen_wird_ignoriert(regel_widerrufen):
    ts = datetime(2026, 3, 15, 10, 0)
    result = loeseauf_delegation("anna", "freigabe", [regel_widerrufen], zum_zeitpunkt=ts)
    assert result.ist_delegiert is False
    assert result.delegiert_an == "anna"


def test_loeseauf_delegation_eskalation_hat_vorrang(regel_stellvertreter, regel_eskalation):
    # Beide Regeln für anna aktiv — ESKALATION soll Vorrang haben
    ts = datetime(2026, 3, 15, 10, 0)
    result = loeseauf_delegation(
        "anna", "kontrakt_freigabe",
        [regel_stellvertreter, regel_eskalation],
        zum_zeitpunkt=ts,
    )
    assert result.ist_delegiert is True
    # Eskalation gewinnt
    assert result.angewendete_regel_id == "T-DR-002"
    assert result.delegations_typ == DelegationsTyp.ESKALATION


def test_loeseauf_delegation_aufgaben_typ_filter(regel_eskalation):
    # regel_eskalation gilt nur für "freigabe" und "kontrakt_freigabe"
    ts = datetime(2026, 3, 15, 10, 0)
    result = loeseauf_delegation("anna", "einkauf_pruefung", [regel_eskalation], zum_zeitpunkt=ts)
    assert result.ist_delegiert is False


def test_loeseauf_delegation_vor_gueltig_ab_kein_match(regel_stellvertreter):
    ts = datetime(2026, 2, 20, 0, 0)  # Vor gueltig_ab
    result = loeseauf_delegation("anna", "freigabe", [regel_stellvertreter], zum_zeitpunkt=ts)
    assert result.ist_delegiert is False


def test_loeseauf_delegation_eskalationsstufe_in_entscheidung(regel_eskalation):
    ts = datetime(2026, 3, 15, 10, 0)
    result = loeseauf_delegation("anna", "kontrakt_freigabe", [regel_eskalation], zum_zeitpunkt=ts)
    assert result.eskalations_stufe == EskalationsStufe.STUFE_1


# ---------------------------------------------------------------------------
# get_default_delegations_regeln
# ---------------------------------------------------------------------------

def test_default_regeln_fuenf_regeln(default_regeln):
    assert len(default_regeln) == 5


def test_default_regeln_ids(default_regeln):
    ids = {r.regel_id for r in default_regeln}
    for expected in ["DR-001", "DR-002", "DR-003", "DR-004", "DR-005"]:
        assert expected in ids


def test_default_regel_dr001_stellvertreter(default_regeln):
    regel = next(r for r in default_regeln if r.regel_id == "DR-001")
    assert regel.delegations_typ == DelegationsTyp.STELLVERTRETER
    assert regel.status == DelegationsStatus.AKTIV
    assert regel.von_subjekt_id == "mueller"
    assert regel.zu_subjekt_id == "schneider"
    assert regel.gueltig_bis is not None


def test_default_regel_dr002_eskalation_stufe1(default_regeln):
    regel = next(r for r in default_regeln if r.regel_id == "DR-002")
    assert regel.delegations_typ == DelegationsTyp.ESKALATION
    assert regel.eskalations_stufe == EskalationsStufe.STUFE_1
    assert regel.eskalations_nach_minuten == 120
    assert "kontrakt_freigabe" in regel.aufgaben_typen
    assert "settlement_freigabe" in regel.aufgaben_typen


def test_default_regel_dr003_eskalation_stufe2(default_regeln):
    regel = next(r for r in default_regeln if r.regel_id == "DR-003")
    assert regel.delegations_typ == DelegationsTyp.ESKALATION
    assert regel.eskalations_stufe == EskalationsStufe.STUFE_2
    assert regel.eskalations_nach_minuten == 240


def test_default_regel_dr004_pool(default_regeln):
    regel = next(r for r in default_regeln if r.regel_id == "DR-004")
    assert regel.delegations_typ == DelegationsTyp.POOL
    assert "bestellvorschlag_pruefung" in regel.aufgaben_typen
    assert regel.zu_subjekt_id == "fischer"


def test_default_regel_dr005_widerrufen(default_regeln):
    regel = next(r for r in default_regeln if r.regel_id == "DR-005")
    assert regel.status == DelegationsStatus.WIDERRUFEN
    assert regel.delegations_typ == DelegationsTyp.DIREKT
    assert regel.von_subjekt_id == "weber"
    assert regel.zu_subjekt_id == "mueller"


def test_default_regeln_dr002_loesung_sachbearbeiter(default_regeln):
    # sachbearbeiter soll an teamleiter delegiert werden (DR-002 ist ESKALATION)
    ts = datetime(2026, 3, 10, 9, 0)
    result = loeseauf_delegation("sachbearbeiter", "kontrakt_freigabe", default_regeln, zum_zeitpunkt=ts)
    assert result.ist_delegiert is True
    assert result.delegiert_an == "teamleiter"
    assert result.angewendete_regel_id == "DR-002"


def test_default_regeln_dr005_weber_kein_match(default_regeln):
    # DR-005 ist WIDERRUFEN → weber erhält keine Delegation
    ts = datetime(2026, 3, 10, 9, 0)
    result = loeseauf_delegation("weber", "freigabe", default_regeln, zum_zeitpunkt=ts)
    assert result.ist_delegiert is False
    assert result.delegiert_an == "weber"


def test_default_regeln_dr001_mueller_urlaub(default_regeln):
    ts = datetime(2026, 3, 15, 10, 0)
    result = loeseauf_delegation("mueller", "irgendwas", default_regeln, zum_zeitpunkt=ts)
    assert result.ist_delegiert is True
    assert result.delegiert_an == "schneider"
