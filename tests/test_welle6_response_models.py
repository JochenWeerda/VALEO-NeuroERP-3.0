"""SPEC-P1-06 Welle 6: Kontrakt-Spine und CRM-Buendel.

Ab dieser Welle ist der Schnitt fachlich statt nach Dateigroesse — die
Kontraktdateien teilen sich ``FixingOut``, die CRM-Dateien ein gemeinsames
Modul.

Enthaelt zusaetzlich die repo-weite Klammer gegen einen Bugtyp, der in dieser
Welle dreimal gefunden wurde: ``response_model=dict[...]`` an einer Funktion,
die eine Liste liefert. FastAPI validiert die Antwort gegen das Modell — bei
einer Liste schlaegt das immer fehl und der Endpunkt liefert 500.
"""

import inspect
import typing

import pytest

from app.api.v1.endpoints import contract_engagement as engagement_module
from app.api.v1.endpoints import contract_fixing as fixing_module
from app.api.v1.endpoints import contract_settlement as settlement_module
from app.api.v1.endpoints import crm_contacts_ext as contacts_ext_module
from app.api.v1.endpoints import crm_gifts as gifts_module
from app.api.v1.endpoints import crm_kontakte as kontakte_module
from app.api.v1.endpoints import crm_lead_gen as lead_module
from app.api.v1.endpoints import crm_ownership as ownership_module
from app.api.v1.schemas import contract_spine_schemas as cs
from app.api.v1.schemas import crm_bundle_schemas as crm

pytestmark = pytest.mark.unit

WELLE6_MODULE = [
    fixing_module,
    engagement_module,
    settlement_module,
    lead_module,
    ownership_module,
    gifts_module,
    kontakte_module,
    contacts_ext_module,
]


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in route.methods:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = route.response_model
    return out


@pytest.mark.parametrize("module", WELLE6_MODULE, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        text = str(model)
        if (
            model is None
            or model in (dict, list)
            or "dict[str, Any]" in text
            or "list[dict" in text
        ):
            schwach.append(f"{method} {path}")
    assert not schwach, f"noch schwach typisiert: {schwach}"


# ── Repo-weite Klammer gegen den 500er-Bugtyp ───────────────────────────────


def _ist_dict_typ(t) -> bool:
    # Bei "from __future__ import annotations" sind Annotationen Strings.
    if isinstance(t, str):
        return t.startswith(("dict", "Dict"))
    return t is dict or typing.get_origin(t) is dict


def _ist_listen_typ(t) -> bool:
    if isinstance(t, str):
        return t.startswith(("list", "List"))
    return t is list or typing.get_origin(t) is list


def test_kein_endpunkt_widerspricht_seiner_rueckgabeform():
    """response_model und Rueckgabetyp duerfen sich nicht widersprechen.

    In Welle 6 gefunden und behoben (je ein garantierter 500er):
      GET /crm/kunden-kontakte/{kunden_nr}
      GET /crm/kim/customers/{kunden_nr}/gifts
      GET /crm/kim/contacts/{contact_id}/marketing-prefs
    """
    from app.main import app

    widersprueche = []
    for route in app.routes:
        modell = getattr(route, "response_model", None)
        fn = getattr(route, "endpoint", None)
        if modell is None or fn is None:
            continue
        try:
            rueck = inspect.signature(fn).return_annotation
        except (ValueError, TypeError):
            continue
        if rueck is inspect.Signature.empty:
            continue
        if _ist_dict_typ(modell) and _ist_listen_typ(rueck):
            widersprueche.append(f"{route.path}: dict deklariert, Liste geliefert")
        elif _ist_listen_typ(modell) and _ist_dict_typ(rueck):
            widersprueche.append(f"{route.path}: Liste deklariert, dict geliefert")
    assert not widersprueche, "\n".join(widersprueche)


def _assert_kein_feldverlust(model, data, label=None):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{label or model.__name__} verliert Felder: {fehlend}"
    return dumped


# ── Kontrakt-Spine ──────────────────────────────────────────────────────────


@pytest.fixture
def fixierung():
    return {
        "fixing_no": 1,
        "line_id": "l1",
        "menge": 100.0,
        "matif_price": 210.0,
        "praemie": 12.5,
        "effektiv_preis": 222.5,
        "datum": "2026-08-01",
        "referenz": "MATIF-SEP26",
        "notiz": None,
        "bediener": "KIM",
    }


def test_fixierung_ist_ein_schema_ueber_die_ganze_kette(fixierung):
    """FixingOut wird von drei Endpunkten geteilt — das ist der Gewinn des
    fachlichen Schnitts. Die reduzierte Settlement-Form muss ebenso passen."""
    _assert_kein_feldverlust(cs.FixingOut, fixierung, "Fixierung(voll)")

    reduziert = {
        "fixing_no": 1,
        "menge": 100.0,
        "effektiv_preis": 222.5,
        "status": "storniert",
        "fixing_id": "f1",
        "storno_grund": "Fehleingabe",
    }
    dumped = _assert_kein_feldverlust(cs.FixingOut, reduziert, "Fixierung(Settlement)")
    assert dumped["storno_grund"] == "Fehleingabe"


def test_fixierungs_arbeitsraum(fixierung):
    position = {
        "position_no": 1,
        "line_id": "l1",
        "artikel": "WEIZEN-A",
        "bezeichnung": "Weizen A",
        "is_matif": True,
        "menge_kontrakt": 500.0,
        "fixiert": 100.0,
        "offen_zu_fixieren": 400.0,
        "fixierungsgrad_pct": 20.0,
        "avg_fixpreis_effektiv": 222.5,
        "symbol": "EBM",
        "notierung": {
            "preis": 215.0,
            "datum": "2026-08-20",
            "markt_effektiv": 227.5,
            "quelle": "MATIF",
        },
        "bewertung_fixiert_eur": 22250.0,
        "marktwert_offen_eur": 91000.0,
        "fixings": [fixierung],
    }
    daten = {
        "found": True,
        "contract_no": "KT-2026-001",
        "contract_type": "EK",
        "party_id": "L1",
        "einheit": "t",
        "status": "aktiv",
        "pricing": {
            "modell": "matif",
            "praemie_typ": "fix",
            "praemie_wert": 12.5,
            "basis": "EBM",
        },
        "positionen": [position],
        "summary": {
            "menge_kontrakt": 500.0,
            "fixiert": 100.0,
            "offen_zu_fixieren": 400.0,
            "fixierungsgrad_pct": 20.0,
            "bewertbar": True,
            "bewertung_fixiert_eur": 22250.0,
            "marktwert_offen_eur": 91000.0,
        },
    }
    dumped = _assert_kein_feldverlust(cs.FixingWorkspaceOut, daten)
    assert dumped["positionen"][0]["notierung"]["markt_effektiv"] == 227.5
    assert dumped["positionen"][0]["fixings"][0]["effektiv_preis"] == 222.5

    nichttreffer = cs.FixingWorkspaceOut.model_validate(
        {"found": False, "detail": "Kontrakt nicht gefunden."}
    ).model_dump()
    assert nichttreffer["found"] is False


def test_engagement_nettoposition():
    dumped = _assert_kein_feldverlust(
        cs.EngagementOut,
        {
            "by_article": [
                {
                    "artikel": "WEIZEN-A",
                    "einkauf_offen": 500.0,
                    "verkauf_offen": 300.0,
                    "netto": 200.0,
                    "kontrakte": 3,
                }
            ],
            "by_party": [{"party_id": "L1", "offen": 500.0, "kontrakte": 2}],
            "summary": {
                "einkauf_offen": 500.0,
                "verkauf_offen": 300.0,
                "netto": 200.0,
                "artikel_anzahl": 1,
                "parteien_anzahl": 1,
            },
        },
    )
    assert dumped["by_article"][0]["netto"] == 200.0


def test_mahnkandidaten_und_mahnung():
    _assert_kein_feldverlust(
        cs.DunningCandidateListOut,
        {
            "items": [
                {
                    "contract_no": "KT-2026-001",
                    "typ": "EK",
                    "party_id": "L1",
                    "einheit": "t",
                    "valid_to": "2026-07-31",
                    "tage_ueberfaellig": 23,
                    "offen": 400.0,
                    "letzte_mahnstufe": 1,
                    "naechste_mahnstufe": 2,
                }
            ]
        },
    )
    _assert_kein_feldverlust(
        cs.ReminderListOut,
        {
            "items": [
                {
                    "mahnstufe": 1,
                    "offen": 400.0,
                    "text": "Bitte liefern",
                    "bediener": "KIM",
                    "datum": "2026-08-01T00:00:00",
                }
            ]
        },
    )
    _assert_kein_feldverlust(
        cs.ReminderCreatedOut,
        {"ok": True, "reminder_id": "r1", "contract_no": "KT-2026-001",
         "mahnstufe": 2, "offen": 400.0},
    )


def test_settlement_status_und_storno(fixierung):
    dumped = _assert_kein_feldverlust(
        cs.SettlementStatusOut,
        {
            "found": True,
            "contract_no": "KT-2026-001",
            "einheit": "t",
            "bewegungen": [
                {
                    "movement_id": "m1",
                    "menge": 50.0,
                    "datum": "2026-08-10",
                    "status": "abgerechnet",
                    "invoice_no": "ABR-KT-2026-001-1",
                    "settled_at": "2026-08-11T00:00:00",
                    "storno_grund": None,
                }
            ],
            "fixierungen": [fixierung],
            "summary": {
                "abgerufen": 100.0,
                "abgerechnet": 50.0,
                "offen_abruf": 50.0,
                "fixiert_aktiv": 100.0,
            },
        },
    )
    assert dumped["summary"]["offen_abruf"] == 50.0

    _assert_kein_feldverlust(
        cs.HandoverOut,
        {
            "ok": True,
            "contract_no": "KT-2026-001",
            "uebergeben": 1,
            "bewegungen": [
                {"movement_id": "m1", "menge": 50.0, "invoice_no": "ABR-KT-2026-001-1"}
            ],
        },
    )
    # Storno kennt zwei Auspraegungen — Bewegung oder Fixierung.
    _assert_kein_feldverlust(
        cs.StornoOut,
        {"ok": True, "movement_id": "m1", "frei_menge": 50.0, "status": "storniert"},
        "Storno(Bewegung)",
    )
    _assert_kein_feldverlust(
        cs.StornoOut,
        {"ok": True, "fixing_id": "f1", "frei_menge": 100.0, "status": "storniert"},
        "Storno(Fixierung)",
    )


# ── CRM-Buendel ─────────────────────────────────────────────────────────────


def test_lead_kandidaten_und_leads():
    dumped = _assert_kein_feldverlust(
        crm.LeadPreviewOut,
        {
            "quelle": "gap",
            "plz_min": "26500",
            "plz_max": "26999",
            "top_pct": 0.1,
            "anzahl": 1,
            "kandidaten": [
                {
                    "name": "Hof Meyer",
                    "plz": "26506",
                    "ort": "Norden",
                    "strasse": "Dorfstr. 1",
                    "score": 45000.0,
                    "quelle": "gap",
                    "score_label": "Foerdersumme EUR",
                }
            ],
        },
    )
    assert dumped["kandidaten"][0]["score_label"] == "Foerdersumme EUR"

    # Listen- und Detailform des Leads unterscheiden sich in der Schreibweise.
    _assert_kein_feldverlust(
        crm.LeadListOut,
        {
            "data": [
                {
                    "id": "l1",
                    "company": "Hof Meyer",
                    "contact_person": "H. Meyer",
                    "email": "",
                    "phone": "",
                    "source": "gap",
                    "potential": 45000.0,
                    "priority": "medium",
                    "status": "new",
                }
            ],
            "total": 1,
        },
    )
    _assert_kein_feldverlust(
        crm.LeadOut,
        {
            "id": "l1",
            "company": "Hof Meyer",
            "contactPerson": "H. Meyer",
            "email": "",
            "phone": "",
            "source": "gap",
            "potential": 45000.0,
            "priority": "medium",
            "status": "new",
            "notes": "",
            "address": "",
            "expectedCloseDate": "",
        },
        "Lead(Detail)",
    )
    _assert_kein_feldverlust(
        crm.LeadUebernahmeOut,
        {"uebernommen": 5, "uebersprungen": 2, "leads_gesamt": 40},
    )
    _assert_kein_feldverlust(
        crm.LeadConvertOut,
        {"lead_id": "l1", "kunden_nr": "K-100", "status": "CONVERTED"},
    )


def test_ownership_worklisten_und_historie():
    kunde = {"kunden_nr": "K-1", "name1": "Hof Meyer", "plz": "26506", "ort": "Norden"}
    _assert_kein_feldverlust(crm.UnassignedOut, {"items": [kunde], "total": 1})
    _assert_kein_feldverlust(
        crm.ByOwnerOut,
        {"sales_rep": "VB1", "items": [{**kunde, "dispatcher_disp": "DISP1"}], "total": 1},
    )
    # GET liefert nur die Zuordnung, PUT ergaenzt ok und geaendert.
    _assert_kein_feldverlust(
        crm.OwnershipOut,
        {"kunden_nr": "K-1", "sales_rep": "VB1", "dispatcher": "DISP1"},
        "Ownership(GET)",
    )
    dumped = _assert_kein_feldverlust(
        crm.OwnershipOut,
        {"ok": True, "kunden_nr": "K-1", "geaendert": ["sales_rep"],
         "sales_rep": "VB2", "dispatcher": "DISP1"},
        "Ownership(PUT)",
    )
    assert dumped["geaendert"] == ["sales_rep"]
    _assert_kein_feldverlust(
        crm.OwnershipHistoryOut,
        {
            "items": [
                {
                    "feld": "sales_rep",
                    "alt": "VB1",
                    "neu": "VB2",
                    "grund": "Gebietswechsel",
                    "bediener": "KIM",
                    "created_at": "2026-08-01T00:00:00",
                }
            ]
        },
    )


def test_praesent_und_kontakt():
    _assert_kein_feldverlust(
        crm.GiftOut,
        {
            "id": "g1",
            "tenant_id": "t",
            "kunden_nr": "K-1",
            "contact_id": "c1",
            "year": 2026,
            "gift_date": "2026-12-01",
            "occasion": "Weihnachten",
            "gift_name": "Praesentkorb",
            "quantity": 1.0,
            "sales_rep": "VB1",
            "operator": "KIM",
            "representative_officer": None,
            "sequence_number": 3,
            "created_at": "2026-08-01T00:00:00",
            "updated_at": None,
        },
    )
    kontakt = {
        "id": "k1",
        "kunden_nr": "K-1",
        "richtung": "aus",
        "art": "telefon",
        "kurzinfo": "Rueckruf",
        "notiz": None,
        "wiedervorlage": "2026-08-25",
        "weiterleitung_an": None,
        "bediener": "KIM",
        "verweis": None,
        "erledigt": False,
        "created_at": "2026-08-01T00:00:00",
    }
    _assert_kein_feldverlust(crm.KontaktOut, kontakt)
    # Die Wiedervorlagen-Sicht ergaenzt zwei berechnete Felder.
    dumped = _assert_kein_feldverlust(
        crm.WiedervorlagenOut,
        {"items": [{**kontakt, "kunde": "Hof Meyer", "ueberfaellig": True}]},
    )
    assert dumped["items"][0]["ueberfaellig"] is True


def test_marketingpraeferenzen():
    _assert_kein_feldverlust(
        crm.MarketingPrefOut,
        {
            "id": "m1",
            "contact_id": "c1",
            "kunden_nr": "K-1",
            "category_code": "NEWSLETTER",
            "category_label": "Newsletter",
            "preference": "opt_in",
            "updated_at": "2026-08-01T00:00:00",
        },
    )
    _assert_kein_feldverlust(
        crm.MarketingPrefSetOut,
        {
            "status": "success",
            "contact_id": "c1",
            "category_code": "NEWSLETTER",
            "preference": "opt_in",
        },
    )
