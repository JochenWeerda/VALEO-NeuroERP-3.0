"""Zielort trägt die Fahrtposition, solange Webfleet keine liefert."""

from app.domains.logistik.strecke import anreichern_stopp, fahrtposition, strecke_km, webfleet_punkt


def test_nur_status_a_ist_ein_webfleet_fix():
    fix = webfleet_punkt(53_550_000, 8_580_000, "A")
    assert fix is not None
    assert round(fix[0], 5) == 53.55
    assert round(fix[1], 5) == 8.58
    assert webfleet_punkt(53_550_000, 8_580_000, "L") is None
    assert webfleet_punkt(53_550_000, 8_580_000, "V") is None
    assert webfleet_punkt(53_550_000, 8_580_000, "0") is None
    assert fahrtposition(webfleet_punkt(53_100_000, 8_200_000, "L"), (53.55, 8.58)) == (53.55, 8.58)


def test_webfleet_gewinnt_vor_dem_zielort():
    assert fahrtposition((53.1, 8.2), (48.1, 11.5)) == (53.1, 8.2)


def test_ohne_webfleet_gilt_der_zielort():
    assert fahrtposition(None, (53.55, 8.58)) == (53.55, 8.58)


def test_ungueltige_koordinate_faellt_auf_den_zielort():
    assert fahrtposition((95.0, 0.0), (53.0, 8.0)) == (53.0, 8.0)


def test_ein_punkt_ist_keine_strecke():
    assert strecke_km([(53.55, 8.58)]) is None
    assert strecke_km([]) is None


def test_zwei_zielorte_ergeben_eine_luftlinie():
    km = strecke_km([(53.55, 8.58), (53.08, 8.80)])
    assert km is not None
    assert km > 0


def test_platzhalteradresse_weicht_der_abladestelle():
    stopp = anreichern_stopp(
        {"address": "Lieferschein 2026000001", "lat": None, "lng": None},
        ziel_lat=53.55,
        ziel_lng=8.58,
        ziel_adresse="Musterstrasse 12",
    )
    assert stopp["address"] == "Musterstrasse 12"
    assert stopp["lat"] == 53.55
    assert stopp["lng"] == 8.58


def test_vorhandene_stoppkoordinate_bleibt():
    stopp = anreichern_stopp(
        {"address": "Silo Ost", "lat": 52.0, "lng": 10.0},
        ziel_lat=53.55,
        ziel_lng=8.58,
        ziel_adresse="Anderswo",
    )
    assert stopp["lat"] == 52.0
    assert stopp["address"] == "Silo Ost"
