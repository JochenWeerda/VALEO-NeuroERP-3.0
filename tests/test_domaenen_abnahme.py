"""Domaenenabnahme (scripts/domaenen_abnahme.py): Pruefregeln und Aktualitaet der Abnahmeblaetter, ohne Datenbank."""
import pytest

from scripts.domaenen_abnahme import Pruefung, ist_platzhalter, main, pruefe_prozess

pytestmark = pytest.mark.unit

ROUTEN = {
    "kasse/tagesabschluss": {"screen_ids": ["kasse/tagesabschluss"], "stufe": "studio_versioniert"},
    "sales/angebote": {"screen_ids": ["beleg-liste/sales-offer"], "stufe": "studio_versioniert"},
}
PLATZHALTER = {"kasse/tagesabschluss"}
NACHWEIS = "tests/test_domaenen_abnahme.py"


def _liste(spalten, aktionen=("export",), zeilenaktionen=()):
    return {
        "mode": "list",
        "actions": [{"key": key} for key in aktionen],
        "tables": [{"columns": [{"key": key} for key in spalten], "rowActions": [{"key": k} for k in zeilenaktionen]}],
    }


def _prozess(**felder):
    return {"id": "VK-T", "status": "abgenommen", "routen": ["sales/angebote"], "nachweise": [NACHWEIS], **felder}


def test_abnahmeblaetter_sind_aktuell_und_halten_die_regeln(capsys):
    assert main(["--check"]) == 0, capsys.readouterr().out


def test_liste_mit_kennung_name_status_datum_und_nur_export_ist_platzhalter():
    assert ist_platzhalter(_liste(["id", "name", "status", "updated_at"]))


def test_fachspalte_oder_fachaktion_macht_keine_platzhaltermaske():
    assert not ist_platzhalter(_liste(["id", "restmenge", "status"]))
    assert not ist_platzhalter(_liste(["id", "name"], aktionen=("export", "buchen")))
    assert not ist_platzhalter(_liste(["id", "name"], zeilenaktionen=("oeffnen",)))


def test_nur_listenmasken_mit_tabelle_werden_bewertet():
    assert not ist_platzhalter({"mode": "detail", "tables": [{"columns": [{"key": "id"}]}]})
    assert not ist_platzhalter({"mode": "list", "tables": []})


def test_abgenommen_mit_nachweis_ohne_luecke_auf_echter_maske_ist_zulaessig():
    pruefung = Pruefung()
    pruefe_prozess(_prozess(), ROUTEN, PLATZHALTER, pruefung)
    assert pruefung.fehler == []


@pytest.mark.parametrize(
    ("felder", "meldung"),
    [
        ({"nachweise": []}, "abgenommen ohne Nachweis"),
        ({"luecken": [{"text": "Sammellauf fehlt", "prio": "P1"}]}, "trotz offener P0/P1-Luecke"),
        ({"routen": ["kasse/tagesabschluss"]}, "Platzhaltermaske hinter kasse/tagesabschluss"),
    ],
)
def test_abgenommen_verlangt_nachweis_keine_p0_p1_luecke_und_keine_platzhaltermaske(felder, meldung):
    pruefung = Pruefung()
    pruefe_prozess(_prozess(**felder), ROUTEN, PLATZHALTER, pruefung)
    assert any(meldung in fehler for fehler in pruefung.fehler), pruefung.fehler


def test_teilweise_darf_auf_platzhalter_und_p1_luecke_zeigen():
    pruefung = Pruefung()
    prozess = _prozess(status="teilweise", routen=["kasse/tagesabschluss"],
                       luecken=[{"text": "Abschlussaktion fehlt", "prio": "P1"}])
    pruefe_prozess(prozess, ROUTEN, PLATZHALTER, pruefung)
    assert pruefung.fehler == []


def test_unbekannte_route_fehlender_nachweis_falscher_status_und_luecke_ohne_prio_werden_gemeldet():
    pruefung = Pruefung()
    prozess = _prozess(status="fertig", routen=["gibt/es/nicht"], nachweise=["tests/fehlt.py::test_x"],
                       luecken=[{"text": "ohne Prioritaet"}])
    pruefe_prozess(prozess, ROUTEN, PLATZHALTER, pruefung)
    text = "\n".join(pruefung.fehler)
    assert "Status 'fertig' unbekannt" in text
    assert "Route 'gibt/es/nicht' nicht im Masken-Inventar" in text
    assert "Nachweis 'tests/fehlt.py::test_x' existiert nicht" in text
    assert "Luecke ohne Prioritaet" in text
