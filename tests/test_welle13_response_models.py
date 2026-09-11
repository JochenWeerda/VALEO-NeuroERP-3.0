"""SPEC-P1-06 Welle 13: Portal Intelligence, Interessent, Lohndienst."""

import pytest

from app.api.v1.endpoints import portal_intelligence as intel_module
from app.api.v1.endpoints import portal_interessent as interessent_module
from app.api.v1.endpoints import portal_lohndienst as lohn_module
from app.api.v1.schemas import portal_bundle_schemas as portal

pytestmark = pytest.mark.unit

WELLE13_MODULE = [intel_module, interessent_module, lohn_module]


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in getattr(route, "methods", []) or []:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = getattr(route, "response_model", None)
    return out


@pytest.mark.parametrize("module", WELLE13_MODULE, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        if model is None:
            continue
        text = str(model)
        if (
            model in (dict, list)
            or "dict[str, Any]" in text
            or "list[dict" in text
        ):
            schwach.append(f"{method} {path}")
    assert not schwach, f"noch schwach typisiert: {schwach}"


def _assert_kein_feldverlust(model, data, label=None):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{label or model.__name__} verliert Felder: {fehlend}"
    return dumped


def test_portal_shapes():
    emp = {
        "empfehlung_id": "e1",
        "tenant_id": "t1",
        "kunden_nr": "K-1",
        "typ": "rohware_angebot",
        "prioritaet": "hoch",
        "titel": "Angebot",
        "beschreibung": "Text",
        "cta_label": "Anfragen",
        "cta_ziel": "/portal",
        "kontext_schluessel": "ration",
        "kontext_wert": "Milchkühe",
        "artikel_id": "SES-001",
        "betrag_indikativ": 100.0,
        "gueltig_bis": "2026-12-31",
        "gesehen": False,
        "erstellt_am": "2026-09-01T10:00:00",
    }
    _assert_kein_feldverlust(portal.PortalEmpfehlungOut, emp)
    _assert_kein_feldverlust(
        portal.PortalEmpfehlungListOut, {"items": [emp], "count": 1}
    )
    _assert_kein_feldverlust(
        portal.PortalEmpfehlungSummaryOut,
        {
            "kunden_nr": "K-1",
            "gesamt": 2,
            "ungesehen": 1,
            "nach_typ": {"rohware_angebot": 1},
        },
    )
    _assert_kein_feldverlust(portal.PortalEmpfehlungAckOut, {"ok": True})
    _assert_kein_feldverlust(
        portal.PortalEmpfehlungGeneratedOut,
        {"neue_empfehlungen": [emp], "count": 1},
    )
    interessent = {
        "interessent_id": "i1",
        "tenant_id": "t1",
        "status": "interessent",
        "vorname": "Max",
        "nachname": "Mustermann",
        "vollname": "Max Mustermann",
        "email": "a@b.de",
        "telefon": None,
        "betrieb_name": "Hof",
        "betrieb_typ": "ackerbau",
        "flaeche_ha": 10.0,
        "hauptkulturen": ["Weizen"],
        "tiere_anzahl": None,
        "tierart": None,
        "plz": "12345",
        "ort": "Dorf",
        "interesse_themen": ["Saatgut"],
        "anmerkung": None,
        "zugewiesen_an": None,
        "kunden_nr": None,
        "qualifiziert_am": None,
        "konvertiert_am": None,
        "erstellt_am": "2026-09-01T10:00:00",
        "aktualisiert_am": "2026-09-01T10:00:00",
    }
    _assert_kein_feldverlust(portal.PortalInteressentOut, interessent)
    _assert_kein_feldverlust(
        portal.PortalInteressentListOut, {"items": [interessent], "count": 1}
    )
    auftrag = {
        "auftrag_id": "a1",
        "tenant_id": "t1",
        "kunden_nr": "K-1",
        "typ": "lohn_spritz",
        "typ_bezeichnung": "Lohnspritzen",
        "status": "angefragt",
        "schlag_ids": ["S-1"],
        "schlag_beschreibung": "",
        "flaeche_ha": 5.0,
        "wunsch_datum": "2026-09-15",
        "geplant_datum": None,
        "getreide_art": None,
        "menge_dt": None,
        "tierart": None,
        "tiere_anzahl": None,
        "psm_mittel": ["Mittel A"],
        "kultur": "Weizen",
        "anmerkung": None,
        "innendienst_notiz": None,
        "preis_indikativ_eur": None,
        "erstellt_am": "2026-09-01T10:00:00",
        "aktualisiert_am": "2026-09-01T10:00:00",
        "abgeschlossen": False,
    }
    _assert_kein_feldverlust(portal.PortalLohndienstAuftragOut, auftrag)
    _assert_kein_feldverlust(
        portal.PortalLohndienstListOut, {"items": [auftrag], "count": 1}
    )
