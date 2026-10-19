"""Wer handelt und welche Rollen gelten, sagt die gepruefte Anmeldung — nie eine Kopfzeile des Clients.

Bis zum 19.10.2026 lasen rund dreissig Wege ``X-User-ID`` (Audit-Urheber, Vier-Augen-Pruefungen von
Rechnungsstapel und Inventurfreigabe, persoenliche Ansichten), ``X-User-Email`` (FiBu-Audit) und ``X-Roles``
(Rollenpostfaecher des Mail-Arbeitsplatzes). Jeder Client konnte sich damit als jemand anderes ausgeben.
Urheber kommen aus ``app.core.akteur`` (Token), Rollen aus dem Nutzerobjekt der Rollen-Abhaengigkeit.

Dieser Vertrag haelt fest: Kein Code unter ``app/`` liest eine solche Kopfzeile. Erwaehnungen in
Kommentaren und Docstrings sind erlaubt.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

APP = Path(__file__).resolve().parents[1] / "app"
KOPFZEILEN = ("X-User-ID", "X-User-Id", "x-user-id", "X-User-Email", "X-Roles", "x-roles")
#: Lesender Zugriff: headers.get("..."), headers["..."], Header(alias="..."), getlist("...").
LESEN = re.compile(
    r"""(?:headers\s*(?:\.get|\.getlist)?\s*[\(\[]\s*|Header\([^)]*alias\s*=\s*)["'](?P<name>[^"']+)["']"""
)


def _code_zeilen(text: str):
    """Zeilen ohne Kommentare und Docstrings (grob, aber fuer diese Suche ausreichend)."""
    in_doc = False
    for nummer, zeile in enumerate(text.splitlines(), 1):
        roh = zeile.strip()
        zaehler = roh.count('"""') + roh.count("'''")
        if in_doc:
            if zaehler % 2 == 1:
                in_doc = False
            continue
        if roh.startswith(('"""', "'''")):
            if zaehler % 2 == 1:
                in_doc = True
            continue
        yield nummer, zeile.split("#", 1)[0]


def test_kein_weg_liest_identitaet_aus_kopfzeilen():
    funde = []
    for datei in sorted(APP.rglob("*.py")):
        for nummer, code in _code_zeilen(datei.read_text(encoding="utf-8")):
            for treffer in LESEN.finditer(code):
                if treffer.group("name") in KOPFZEILEN:
                    funde.append(f"{datei.relative_to(APP.parent)}:{nummer}: {treffer.group('name')}")
    assert funde == []


def test_suchmuster_erkennt_die_alten_formen():
    for beispiel in ('request.headers.get("X-User-ID")', "headers['X-Roles']", 'Header(None, alias="X-User-ID")'):
        assert any(t.group("name") in KOPFZEILEN for t in LESEN.finditer(beispiel)), beispiel


#: Bearbeiter aus Feldern des Anfragekoerpers (19.10.2026: ``operator``/``actor``/``created_by`` in sieben Routern
#: und im Compliance-Lebenszyklus — derselbe Fehler wie ``X-User-ID``, nur im Body).
BODY_URHEBER = re.compile(r"(?:body|payload)\.(?:operator|actor|created_by)")


def test_kein_weg_nimmt_den_bearbeiter_aus_dem_body():
    funde = []
    for datei in sorted((APP / "api").rglob("*.py")):
        for nummer, code in _code_zeilen(datei.read_text(encoding="utf-8")):
            if BODY_URHEBER.search(code):
                funde.append(f"{datei.relative_to(APP.parent)}:{nummer}")
    assert funde == []
