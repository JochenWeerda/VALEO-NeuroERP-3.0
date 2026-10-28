"""Wer handelt und welche Rollen gelten, sagt die gepruefte Anmeldung — nie eine Kopfzeile des Clients.

Bis zum 19.10.2026 lasen rund dreissig Wege ``X-User-ID`` (Audit-Urheber, Vier-Augen-Pruefungen von
Rechnungsstapel und Inventurfreigabe, persoenliche Ansichten), ``X-User-Email`` (FiBu-Audit) und ``X-Roles``
(Rollenpostfaecher des Mail-Arbeitsplatzes). Jeder Client konnte sich damit als jemand anderes ausgeben.
Urheber kommen aus ``app.core.akteur`` (Token), Rollen aus dem Nutzerobjekt der Rollen-Abhaengigkeit.

Dieser Vertrag haelt fest: Kein Code unter ``app/`` liest eine solche Kopfzeile. Erwaehnungen in
Kommentaren und Docstrings sind erlaubt.
"""
from __future__ import annotations

import ast
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
    """Zeilen ohne Kommentare und Docstrings.

    Bis 28.10.2026 zaehlte diese Funktion dreifache Anfuehrungszeichen nur am Zeilenanfang; ein ``text(\"\"\"`` mitten
    in der Zeile verschob die Zaehlung, und der Code dahinter galt als Docstring (so blieb ``payload.createdBy`` im
    Lohnexport unentdeckt). Docstrings und alleinstehende Zeichenketten bestimmt jetzt der Syntaxbaum.
    """
    doc = set()
    for knoten in ast.walk(ast.parse(text)):
        if isinstance(knoten, ast.Expr) and isinstance(knoten.value, ast.Constant) and isinstance(knoten.value.value, str):
            doc.update(range(knoten.lineno, knoten.end_lineno + 1))
    for nummer, zeile in enumerate(text.splitlines(), 1):
        if nummer not in doc:
            yield nummer, zeile.split("#", 1)[0]


def test_code_zeilen_erkennt_docstrings_am_syntaxbaum():
    quelle = 'def f():\n    """Doku: payload.createdBy"""\n    x = text("""SELECT 1""")\n    return payload.createdBy\n'
    assert [n for n, c in _code_zeilen(quelle) if "payload.createdBy" in c] == [4]


#: FastAPI leitet den Kopfnamen aus dem Parameter ab: ``x_user_email: str = Header(None)`` liest X-User-Email.
#: Diese Form uebersah das Muster oben bis 27.10.2026 (Grundfutteranalysen, Rations-Zugaenge).
PARAMETER = re.compile(r"\b(?P<name>x_user_id|x_user_email|x_user_name|x_roles)\s*:[^=]*=\s*Header\(")


def test_kein_weg_liest_identitaet_aus_kopfzeilen():
    funde = []
    for datei in sorted(APP.rglob("*.py")):
        for nummer, code in _code_zeilen(datei.read_text(encoding="utf-8-sig")):
            for treffer in LESEN.finditer(code):
                if treffer.group("name") in KOPFZEILEN:
                    funde.append(f"{datei.relative_to(APP.parent)}:{nummer}: {treffer.group('name')}")
            for treffer in PARAMETER.finditer(code):
                funde.append(f"{datei.relative_to(APP.parent)}:{nummer}: {treffer.group('name')}")
    assert funde == []


def test_suchmuster_erkennt_die_alten_formen():
    for beispiel in ('request.headers.get("X-User-ID")', "headers['X-Roles']", 'Header(None, alias="X-User-ID")'):
        assert any(t.group("name") in KOPFZEILEN for t in LESEN.finditer(beispiel)), beispiel
    for beispiel in ("x_user_email: Optional[str] = Header(default=None),", "x_user_id: str = Header(None)"):
        assert PARAMETER.search(beispiel), beispiel
    assert not PARAMETER.search("x_share_token: Optional[str] = Header(default=None),")


#: Bearbeiter aus Feldern des Anfragekoerpers (19.10.2026: ``operator``/``actor``/``created_by`` in sieben Routern
#: und im Compliance-Lebenszyklus, ``aktor_id`` in fuenf Reklamationswegen und deren Maskenaktion — derselbe Fehler
#: wie ``X-User-ID``, nur im Body).
#: Seit 28.10.2026 auch camelCase (``createdBy``: Vertragsnachtrag, Lohnexport), ein Audit-Unterobjekt
#: (``payload.audit.created_by``: Geschaeftspartner) und die Router unter ``app/routers``.
_URHEBERFELDER = r"(?:operator|actor|created_by|updated_by|createdBy|updatedBy|aktor_id|sender_id)"
BODY_URHEBER = re.compile(
    rf"\b(?:body|payload|req)(?:\.audit)?\.{_URHEBERFELDER}\b"
    rf"|\b(?:body|payload|req)\.get\(\s*[\"']{_URHEBERFELDER}[\"']"
)


def test_kein_weg_nimmt_den_bearbeiter_aus_dem_body():
    funde = []
    for datei in sorted([*(APP / "api").rglob("*.py"), *(APP / "routers").rglob("*.py")]):
        for nummer, code in _code_zeilen(datei.read_text(encoding="utf-8-sig")):
            if BODY_URHEBER.search(code):
                funde.append(f"{datei.relative_to(APP.parent)}:{nummer}")
    assert funde == []


def test_suchmuster_erkennt_bearbeiter_im_body():
    for beispiel in ("req.aktor_id", 'payload.get("aktor_id")', "body.operator", "payload.get('actor')",
                     "payload.sender_id", "body.createdBy", "payload.audit.created_by", "payload.audit.updated_by"):
        assert BODY_URHEBER.search(beispiel), beispiel
