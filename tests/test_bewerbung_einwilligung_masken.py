"""Die Masken zur Einwilligung — ueber Screen Definitions, nicht von Hand.

Erteilen, Widerrufen und Fassungen anlegen waren nur ueber die API erreichbar.
Art. 7 Abs. 3 DSGVO meint auch die Zugaenglichkeit: Der Widerruf gehoert an eine
Stelle, die das Personalbuero ohne Umwege findet. Diese Vertraege halten fest, dass
die zwei neuen Masken als Screen Definitions vollstaendig sind und die Zusagen der
Fachlogik in der Maske nicht verwaessern:

* Der Widerruf ist **ein** Klick mit Bestaetigung — kein Grund, kein Feld, keine
  Freigabe. Er ist nicht schwerer als die Erteilung.
* Eine Fassung hat in der Maske keinen Weg zum Aendern oder Loeschen.
* Kein Kopf zeigt einen technischen Schluessel.

Kein App-Import, keine Datenbank.
"""

from __future__ import annotations

import pytest

from app.api.v1.endpoints.mask_screen_definition import _check_readiness
from app.core.screen_definitions import (
    _AGENT_SYNONYMS,
    _SCREEN_LIST_ROUTE,
    SCREEN_DEFINITION_BUILDERS,
    get_screen_definition,
)
from app.core.screen_definitions_capture import (
    build_personal_bewerbung_einwilligung_screen_definition,
    build_personal_bewerbungen_screen_definition,
    build_personal_einwilligungserklaerungen_screen_definition,
)
from app.core.screen_governance import governance_errors, ux_lint

EINWILLIGUNG = "personal/bewerbung-einwilligung"
ERKLAERUNGEN = "personal/einwilligungserklaerungen"
BUILDER = {
    EINWILLIGUNG: build_personal_bewerbung_einwilligung_screen_definition,
    ERKLAERUNGEN: build_personal_einwilligungserklaerungen_screen_definition,
}


def felder(sd: dict) -> list[dict]:
    gesammelt = list(sd.get("fields") or [])
    for register in sd.get("tabs") or []:
        gesammelt.extend(register.get("fields") or [])
    return gesammelt


def aktion(sd: dict, schluessel: str) -> dict:
    return next(a for a in sd["actions"] if a["key"] == schluessel)


@pytest.mark.parametrize("screen_id", [EINWILLIGUNG, ERKLAERUNGEN])
class TestVollstaendig:
    def test_im_register_und_nicht_vorlaeufig(self, screen_id):
        assert SCREEN_DEFINITION_BUILDERS[screen_id] is BUILDER[screen_id]
        sd = get_screen_definition(screen_id)
        assert sd["adapter"]["temporary"] is False
        assert screen_id in _AGENT_SYNONYMS
        assert screen_id in _SCREEN_LIST_ROUTE

    def test_bereit_und_volle_punktzahl(self, screen_id):
        bereitschaft = _check_readiness(get_screen_definition(screen_id))
        assert bereitschaft["generatorReady"] is True, bereitschaft
        assert bereitschaft["advisoryScore"] == 1.0, bereitschaft

    def test_governance_und_ux_lint_ohne_fehler(self, screen_id):
        sd = BUILDER[screen_id]()
        assert governance_errors(sd) == []
        assert [f for f in ux_lint(sd) if f["severity"] == "error"] == []

    def test_kein_technischer_schluessel_als_feld(self, screen_id):
        for feld in felder(BUILDER[screen_id]()):
            assert not feld["key"].endswith("_id"), feld["key"]

    def test_jede_aktion_hat_einen_befehl(self, screen_id):
        # Die Seite verdrahtet Befehle, nicht Tastenschluessel — eine Aktion ohne
        # Befehl waere ein Knopf ohne Wirkung.
        for a in BUILDER[screen_id]()["actions"]:
            assert a.get("command", "").startswith("personal."), a


class TestEinwilligungsmaske:
    def test_widerruf_ist_ein_klick_ohne_grund(self):
        widerruf = aktion(build_personal_bewerbung_einwilligung_screen_definition(), "widerrufen")
        # Art. 7 Abs. 3: nicht schwerer als die Erteilung. Eine Bestaetigung ja —
        # ein Grund, eine Freigabe oder ein Eingabefeld nein.
        assert widerruf.get("auditReasonRequired") is not True
        assert widerruf.get("humanApprovalRequired") is not True
        assert widerruf.get("requiresConfirmation") is True
        assert widerruf.get("zone") == "header"

    def test_erteilen_und_widerrufen_stehen_gleich_weit_vorn(self):
        sd = build_personal_bewerbung_einwilligung_screen_definition()
        assert aktion(sd, "erteilen")["zone"] == aktion(sd, "widerrufen")["zone"] == "header"

    def test_erteilen_fragt_fassung_ende_und_kanal(self):
        schluessel = {f["key"]: f for f in felder(build_personal_bewerbung_einwilligung_screen_definition())}
        assert schluessel["fassung"]["type"] == "select"
        assert schluessel["gueltig_bis"]["type"] == "date"
        assert {o["value"] for o in schluessel["kanal"]["options"]} == {
            "WEB", "E_MAIL", "PAPIER", "MUENDLICH"
        }
        # Der Wortlaut ist Anzeige der gewaehlten Fassung, keine Eingabe: Zwei
        # Quellen fuer den Text liefen still auseinander.
        assert schluessel["wortlaut"]["readOnly"] is True

    def test_die_kanaele_sind_die_des_dienstes(self):
        from app.services.bewerbung_einwilligung_service import KANAELE

        schluessel = {f["key"]: f for f in felder(build_personal_bewerbung_einwilligung_screen_definition())}
        assert tuple(o["value"] for o in schluessel["kanal"]["options"]) == KANAELE

    def test_das_verzeichnis_ist_eine_tabelle(self):
        sd = build_personal_bewerbung_einwilligung_screen_definition()
        tabellen = [t for r in sd["tabs"] for t in r.get("tables") or []]
        verzeichnis = next(t for t in tabellen if t["key"] == "vorgaenge")
        spalten = [s["key"] for s in verzeichnis["columns"]]
        assert spalten[:3] == ["erfolgt_am", "vorgang", "fassung"]
        # Eine Zeile ist ein Nachweis — es gibt keine Zeilenaktion, die sie aendert.
        assert not verzeichnis.get("rowActions")

    def test_die_person_ist_sensibel(self):
        sensibel = build_personal_bewerbung_einwilligung_screen_definition()["agentContract"]["sensitiveFields"]
        assert "applicant_name" in sensibel


class TestErklaerungsmaske:
    def test_fassungen_haben_keinen_aenderungsweg(self):
        sd = build_personal_einwilligungserklaerungen_screen_definition()
        schluessel = {a["key"] for a in sd["actions"]}
        assert schluessel == {"anlegen", "neu"}
        fassungen = next(t for t in sd["tables"] if t["key"] == "fassungen")
        assert not fassungen.get("rowActions")

    def test_der_wortlaut_ist_ein_mehrzeiliges_feld(self):
        schluessel = {f["key"]: f for f in felder(build_personal_einwilligungserklaerungen_screen_definition())}
        assert schluessel["wortlaut"]["type"] == "textarea"
        assert schluessel["wortlaut"]["required"] is True


class TestArbeitsliste:
    def test_von_der_bewerbung_zur_einwilligung(self):
        sd = build_personal_bewerbungen_screen_definition()
        zeile = {a["key"]: a for a in sd["tables"][0]["rowActions"]}
        assert zeile["einwilligung"]["command"] == "personal.openEinwilligung"

    def test_von_der_arbeitsliste_zu_den_fassungen(self):
        sd = build_personal_bewerbungen_screen_definition()
        assert aktion(sd, "erklaerungen")["command"] == "personal.openErklaerungen"
