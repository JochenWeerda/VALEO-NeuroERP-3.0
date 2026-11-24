"""Gebinderechnung nach den a.eins-Gebindetypen (Beispiele der a.eins-Hilfe, Nutzerauftrag 24.11.2026)."""
from __future__ import annotations

from decimal import Decimal as D

import pytest

from app.core.gebinde_rechnung import (
    Anbruch, FaktorFehlt, Faktorherkunft, FaktorpflegeNichtZulaessig, FaktorsatzUnvollstaendig, FaktorUngueltig,
    GebindeNichtRechenbar, anzahl_aus_menge, berechne_gebinde, ergebnismenge, faktoren_nach_herkunft,
    pruefe_faktorpflege, suchpfad,
)

H = Faktorherkunft

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(("typ", "anzahl", "faktoren", "erwartet"), [
    (0, D(7), [], D("7")),                                  # kein Gebinde
    (1, D(10), [D(25)], D("250")),                          # 10 Sack a 25 kg = 250 kg
    (2, D(10), [D(24), D(6)], D("1440")),                   # 10 Paletten a 24 Kartons a 6 Flaschen
    (3, D(10), [D(5), D(3), D(2)], D("300")),               # 10 Behaelter a 5 x 3 x 2 m = 300 m3
    (4, D(2), [D(10), D(5)], D("30")),
    (5, D(1), [D(12500), D(12000)], D("500")),              # Zaehlerstand alt - neu
    (8, D(2), [D(10), D(3), D(4)], D("15")),
    (9, D(1), [D(4), D(6), D(12), D("0.4")], D("115.2")),   # Palette/Lagen/Kartons/Dosen, kg je Dose
])
def test_ergebnismenge_je_gebindetyp(typ, anzahl, faktoren, erwartet):
    assert ergebnismenge(typ, anzahl, faktoren) == erwartet


def test_effektive_menge_ergibt_anzahl_mit_anbruch():
    # Karton a 8 Kanister a 5 Liter: 100 Liter = 2,5 Kartons
    assert anzahl_aus_menge(2, D(100), [D(8), D(5)]) == D("2.500")
    assert anzahl_aus_menge(2, D(100), [D(8), D(5)], Anbruch.AUFRUNDEN) == D(3)
    assert anzahl_aus_menge(2, D(100), [D(8), D(5)], Anbruch.ABRUNDEN) == D(2)


def test_rundung_bei_umrechnung():
    assert ergebnismenge(8, D(1), [D(10), D(1), D(3)], rundung=2) == D("3.33")


@pytest.mark.parametrize(("typ", "faktoren"), [
    (6, [D(5)]), (7, [D(5)]),        # deaktiv
    (12, [D(1)]),                    # unbekannt
    (2, [D(24)]),                    # Faktor 2 fehlt
    (1, [None]),
    (1, [D(0)]),
])
def test_nicht_rechenbar_wird_nicht_geraten(typ, faktoren):
    with pytest.raises(GebindeNichtRechenbar):
        ergebnismenge(typ, D(1), faktoren)


def test_faktorherkunft_speziell_vor_allgemein():
    stufen = {Faktorherkunft.MENGENEINHEIT: [D(25)], Faktorherkunft.ARTIKEL: [D(50)]}

    assert faktoren_nach_herkunft(Faktorherkunft.ARTIKEL, stufen) == (Faktorherkunft.ARTIKEL, [D(50)])
    assert faktoren_nach_herkunft(Faktorherkunft.AUSPRAEGUNG, stufen)[0] == Faktorherkunft.ARTIKEL
    assert faktoren_nach_herkunft(Faktorherkunft.ARTIKELSTAMM, stufen) == (Faktorherkunft.MENGENEINHEIT, [D(25)])
    with pytest.raises(GebindeNichtRechenbar):
        faktoren_nach_herkunft(Faktorherkunft.MENGENEINHEIT, {Faktorherkunft.ARTIKEL: [D(50)]})


# Pflanzenschutzmittel: auf allen vier Stufen ein Faktor (Liter je Kanister). Je nach Faktorherkunft ein anderes
# Ergebnis - speziellere Stufen oberhalb der eingestellten zaehlen nicht (Fachentscheid 24.11.2026).
PSM = {H.MENGENEINHEIT: [D(10)], H.ARTIKELSTAMM: [D(20)], H.ARTIKEL: [D(5)], H.AUSPRAEGUNG: [D(1)]}


@pytest.mark.parametrize(("herkunft", "pfad", "liter"), [
    (H.MENGENEINHEIT, (H.MENGENEINHEIT,), "30.000"),
    (H.ARTIKELSTAMM, (H.ARTIKELSTAMM, H.MENGENEINHEIT), "60.000"),
    (H.ARTIKEL, (H.ARTIKEL, H.ARTIKELSTAMM, H.MENGENEINHEIT), "15.000"),
    (H.AUSPRAEGUNG, (H.AUSPRAEGUNG, H.ARTIKEL, H.ARTIKELSTAMM, H.MENGENEINHEIT), "3.000"),
])
def test_vier_suchpfade_mit_faktoren_auf_allen_stufen(herkunft, pfad, liter):
    ergebnis = berechne_gebinde(1, D(3), herkunft, PSM)

    assert suchpfad(herkunft) == pfad
    assert (ergebnis.ergebnis, ergebnis.herkunft_verwendet) == (liter, int(herkunft))


@pytest.mark.parametrize(("herkunft", "fehlend", "verwendet", "liter"), [
    (H.ARTIKELSTAMM, {H.ARTIKELSTAMM}, H.MENGENEINHEIT, "30.000"),
    (H.ARTIKEL, {H.ARTIKEL}, H.ARTIKELSTAMM, "60.000"),
    (H.ARTIKEL, {H.ARTIKEL, H.ARTIKELSTAMM}, H.MENGENEINHEIT, "30.000"),
    (H.AUSPRAEGUNG, {H.AUSPRAEGUNG}, H.ARTIKEL, "15.000"),
    (H.AUSPRAEGUNG, {H.AUSPRAEGUNG, H.ARTIKEL, H.ARTIKELSTAMM}, H.MENGENEINHEIT, "30.000"),
])
def test_fehlende_stufe_sucht_weiter_unten(herkunft, fehlend, verwendet, liter):
    stufen = {s: (None if s in fehlend else w) for s, w in PSM.items()}

    ergebnis = berechne_gebinde(1, D(3), herkunft, stufen)

    assert (ergebnis.herkunft_verwendet, ergebnis.ergebnis) == (int(verwendet), liter)


@pytest.mark.parametrize("herkunft", list(H))
def test_ohne_faktor_im_suchpfad_kein_ergebnis_und_keine_1(herkunft):
    nur_oberhalb = {s: [D(7)] for s in H if s > herkunft}  # speziellere Stufen zaehlen nicht

    with pytest.raises(FaktorFehlt):
        berechne_gebinde(1, D(3), herkunft, nur_oberhalb)


def test_fehlend_und_ungueltig_sind_unterscheidbar():
    with pytest.raises(FaktorsatzUnvollstaendig):  # Stufe gefunden, Faktor 2 fehlt: nicht mischen, nicht weitersuchen
        berechne_gebinde(2, D(1), H.ARTIKEL, {H.ARTIKEL: [D(24), None], H.MENGENEINHEIT: [D(24), D(6)]})
    for falsch in ([D(0)], [D(-5)], ["abc"], [D("NaN")]):
        with pytest.raises(FaktorUngueltig):
            berechne_gebinde(1, D(1), H.MENGENEINHEIT, {H.MENGENEINHEIT: falsch})
    assert not issubclass(FaktorUngueltig, FaktorFehlt)
    assert berechne_gebinde(5, D(1), H.MENGENEINHEIT, {H.MENGENEINHEIT: [D(100), D(0)]}).ergebnis == "100.000"


@pytest.mark.parametrize(("herkunft", "stufe", "erlaubt"), [
    (H.MENGENEINHEIT, H.ARTIKEL, False),   # a.eins: bei Herkunft Mengeneinheit im Artikel nicht aenderbar
    (H.MENGENEINHEIT, H.MENGENEINHEIT, True),
    (H.ARTIKELSTAMM, H.ARTIKEL, False),
    (H.ARTIKEL, H.ARTIKELSTAMM, True),
    (H.ARTIKEL, H.AUSPRAEGUNG, False),
    (H.AUSPRAEGUNG, H.AUSPRAEGUNG, True),
])
def test_faktorpflege_nur_im_suchpfad(herkunft, stufe, erlaubt):
    if erlaubt:
        pruefe_faktorpflege(herkunft, stufe)
    else:
        with pytest.raises(FaktorpflegeNichtZulaessig):
            pruefe_faktorpflege(herkunft, stufe)


def test_abbild_fuer_den_beleg_haelt_faktoren_und_herkunft_fest():
    abbild = berechne_gebinde(2, D(10), H.ARTIKEL, {H.ARTIKEL: [D(24), D(6)]}, rundung=0).als_dict()

    assert abbild == {"gebindetyp": 2, "faktorherkunft": 3, "herkunft_verwendet": 3, "faktoren": ["24", "6"],
                      "anzahl": "10", "rundung": 0, "ergebnis": "1440"}
    assert berechne_gebinde(0, D(4), H.MENGENEINHEIT, {}).herkunft_verwendet is None
