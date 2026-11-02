"""Spricht der Endpunkt die Sprache der Maske?

Das Gate hinter dem Gate
------------------------

``tests/test_mask_endpoint_inventory.py`` prueft, ob die **Adresse** existiert.
Dieser Test prueft, ob die **Schluessel** stimmen. Der Unterschied ist der
zwischen einem sichtbaren und einem stillen Fehler:

- Falsche Adresse: 404, die Maske sagt „Vorgang konnte nicht geladen werden".
- Falsche Schluessel: 200, und der Kopf bleibt leer. Leer sieht aus wie „nichts
  erfasst" — und niemand fragt nach.

Zehn Masken hatten genau das: `beleg_nr` statt `rechnungsnr`, `ls_nr` statt
`delivery_note_number`, `wert` statt `amount`.

Grenze des Tests
----------------

Geprueft wird gegen das **deklarierte** Antwortschema. Endpunkte, die ihre
Antwort nicht typisieren (``extra="allow"`` ohne Felder), koennen nichts
zusagen — ihre Masken erscheinen als „nicht pruefbar". Diese Zahl steht hier
bewusst als Obergrenze im Test: Sie darf sinken, nicht steigen. Jede neue
ungetypte Maskenquelle ist eine Stelle, an der dieses Gate blind wird.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_field_contracts import pruefe

pytestmark = pytest.mark.unit

#: Stand nach P4: keine ungetypte Kopfquelle. sales/invoice hat Claude
#: typisiert (21642ae85); die zwoelf Bruecken-Koepfe Cursor.
NICHT_PRUEFBAR_MAX = 0

#: 17 generische Stubs (6 leere /masks/, 11 /mask-rollouts/) sind typisiert.
#: Darf sinken, nicht steigen. Auftrag/Rechnung bleiben Claude. R5 nicht hier.
ZEILEN_NICHT_PRUEFBAR_MAX = 0

#: Altlast Runtime46/batch15 (Workboard STUDIO-UMBAU-RUNTIME46): Masken und Quellen, die heute nicht passen.
#: Darf nur schrumpfen; eine reparierte Maske muss aus der Datei (sonst verdeckt sie Neues).
ALTLAST = json.loads((Path(__file__).resolve().parents[1] / "config/mask_field_contract_altlast.json")
                     .read_text(encoding="utf-8"))
PLATZHALTER_ALTLAST = frozenset(ALTLAST["abweichungen_masken"])
UNGETYPT_ALTLAST = frozenset(ALTLAST["nicht_pruefbar"])
ZEILEN_ALTLAST = frozenset(ALTLAST["zeilen_nicht_pruefbar"])


@pytest.fixture(scope="module")
def ergebnis() -> dict:
    # Immer derselbe Umfang wie im Gesamtlauf: volle App und registrierte Stamm-Masken.
    import app.main  # noqa: F401
    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry

    ensure_stamm_screen_registry()
    return pruefe()


def test_keine_maske_fragt_nach_feldern_die_es_nicht_gibt(ergebnis: dict) -> None:
    abweichungen = [a for a in ergebnis["abweichungen"] if a["screen"] not in PLATZHALTER_ALTLAST]
    beschreibung = "\n  ".join(
        f"{a['screen']}/{a['tab']}: '{a['feld']}' fehlt in {a['endpunkt']}"
        + (f" — meinten Sie '{a['vorschlag']}'?" if a["vorschlag"] else "")
        for a in abweichungen
    )
    assert abweichungen == [], "Maske und Antwort sprechen verschiedene Sprachen:\n  " + beschreibung


def test_altlasten_schrumpfen_nur(ergebnis: dict) -> None:
    """Eine reparierte Platzhalter- oder Kopfquelle muss aus der Altlast-Liste, sonst verdeckt sie Neues."""
    noch_platzhalter = {a["screen"] for a in ergebnis["abweichungen"]}
    assert PLATZHALTER_ALTLAST <= noch_platzhalter, sorted(PLATZHALTER_ALTLAST - noch_platzhalter)
    assert UNGETYPT_ALTLAST <= set(ergebnis["nicht_pruefbar"]), sorted(UNGETYPT_ALTLAST - set(ergebnis["nicht_pruefbar"]))
    zeilen = set(ergebnis["zeilen_nicht_pruefbar"])
    assert ZEILEN_ALTLAST <= zeilen, sorted(ZEILEN_ALTLAST - zeilen)


def test_es_wird_ueberhaupt_etwas_geprueft(ergebnis: dict) -> None:
    """Ein Gate, das nichts prueft, ist gruen und wertlos.

    197 Kopffelder plus die bereits typisierten Zeilen. Unter 250 waere der
    Zeilenteil wieder aus.
    """
    assert ergebnis["geprueft"] >= 250


def test_tabellenquellen_ohne_zeilenform_nehmen_nicht_zu(ergebnis: dict) -> None:
    """Die groessere Haelfte: 305 Spalten gegen 204 Kopffelder.

    Eine Spalte mit falschem Schluessel bleibt leer — dasselbe stille Versagen
    wie im Kopf, nur oefter. Wo die Zeilenform nicht deklariert ist, kann das
    Gate nichts sagen; diese Zahl haelt den Rest fest und darf nur sinken.
    """
    offen = [quelle for quelle in ergebnis["zeilen_nicht_pruefbar"] if quelle not in ZEILEN_ALTLAST]
    assert len(offen) <= ZEILEN_NICHT_PRUEFBAR_MAX, (
        "Neue Tabellenquellen ohne deklarierte Zeilenform: " + ", ".join(offen)
    )


def test_ungetypte_maskenquellen_nehmen_nicht_zu(ergebnis: dict) -> None:
    offen = [quelle for quelle in ergebnis["nicht_pruefbar"] if quelle not in UNGETYPT_ALTLAST]
    assert len(offen) <= NICHT_PRUEFBAR_MAX, (
        "Neue Maskenquellen ohne deklarierte Antwort — dort ist der Feldvertrag "
        "blind:\n  " + "\n  ".join(offen)
    )
