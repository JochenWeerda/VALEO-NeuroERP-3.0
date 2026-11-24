"""Gebinderechnung nach den a.eins-Gebindetypen (Beispiele der a.eins-Hilfe, Nutzerauftrag 24.11.2026)."""
from __future__ import annotations

from decimal import Decimal as D

import pytest

from app.core.gebinde_rechnung import (
    Anbruch, Faktorherkunft, GebindeNichtRechenbar, anzahl_aus_menge, ergebnismenge, faktoren_nach_herkunft,
)

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
