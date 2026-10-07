"""Vertrag: Python-Builder und TypeScript-Fallback beschreiben denselben Vorgang."""

from __future__ import annotations

from pathlib import Path

from app.core.screen_definitions import get_screen_definition
from app.core.screen_definitions_capture import (
    build_fuhrpark_fahrzeuge_screen_definition,
    build_logistik_frachttabellen_screen_definition,
    build_logistik_tour_fracht_arbeitsraum_screen_definition,
    build_logistik_tourenplanung_screen_definition,
    build_fuhrpark_ausgehende_dokumente_screen_definition,
    build_fuhrpark_fahrzeug_stamm_screen_definition,
    build_personal_onboarding_screen_definition,
    build_personal_schulungen_screen_definition,
    build_personal_bewerbungen_screen_definition,
    build_personal_qualifikationen_screen_definition,
    build_fuhrpark_rechnungen_screen_definition,
    build_fuhrpark_terminarten_screen_definition,
    build_logistik_versandprofile_screen_definition,
    build_transporte_fahrer_screen_definition,
)
from app.core.screen_governance import derived_screen_type, governance_errors

ROOT = Path(__file__).resolve().parents[1]
FALLBACK = (ROOT / "packages/frontend-web/src/masks/capture-screens.ts").read_text(encoding="utf-8")

TOUR_FIELDS = ["datum", "tour_id", "tour_status", "ziel", "lieferschein", "fahrzeug_id", "fahrer_id"]
TOUR_ENDPOINTS = ["/api/v1/logistik/tours", "/api/v1/fuhrpark/fahrzeuge", "/api/v1/transporte/fahrer"]
FAHRZEUG_PRIORITY = {
    "kennzeichen": "primary",
    "status": "primary",
    "typ": "secondary",
    "kilometerstand": "secondary",
    "ro_nummer": "tertiary",
    "naechste_inspektion": "tertiary",
}


def _block(name: str) -> str:
    marker = f"export const {name} = "
    start = FALLBACK.index(marker)
    nxt = FALLBACK.find("\nexport const ", start + len(marker))
    return FALLBACK[start:] if nxt < 0 else FALLBACK[start:nxt]


def _first_keys(block: str, keys: list[str]) -> list[int]:
    return [block.index(f"key: '{key}'") for key in keys]


def test_tour_builder_und_fallback_stimmen_ueberein() -> None:
    definition = build_logistik_tourenplanung_screen_definition()
    block = _block("tourenplanungScreen")
    assert definition["id"] == "logistik/tourenplanung"
    assert definition["title"] == "Tourenplanung"
    assert [field["key"] for field in definition["fields"]] == TOUR_FIELDS
    assert _first_keys(block, TOUR_FIELDS) == sorted(_first_keys(block, TOUR_FIELDS))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert "statusPlacement: 'afterFields'" in block
    summary = [item["key"] for item in definition["summary"]]
    assert summary == ["heute", "geplant", "unterwegs", "abgeschlossen"]
    assert _first_keys(block, summary) == sorted(_first_keys(block, summary))
    endpoints = [source["endpoint"] for source in definition["dataSources"]]
    assert endpoints == TOUR_ENDPOINTS
    for endpoint in TOUR_ENDPOINTS:
        assert endpoint in block
    assert "DEMO-LS-001" not in block
    assert get_screen_definition("logistik/tourenplanung")["id"] == "logistik/tourenplanung"


def test_fahrzeugspalten_haben_dieselbe_prioritaet() -> None:
    definition = build_fuhrpark_fahrzeuge_screen_definition()
    block = _block("fuhrparkFahrzeugeScreen")
    assert definition["title"] == "Fahrzeuge"
    assert definition["tables"][0]["label"] == "Fahrzeuge"
    assert "title: 'Fahrzeuge'" in block
    priorities = {column["key"]: column["priority"] for column in definition["tables"][0]["columns"]}
    assert priorities == FAHRZEUG_PRIORITY
    for key, priority in FAHRZEUG_PRIORITY.items():
        assert f"key: '{key}'" in block
        assert f"priority: '{priority}'" in block


def test_fahrer_zaehlt_touren_aus_demselben_endpunkt() -> None:
    definition = build_transporte_fahrer_screen_definition()
    block = _block("transporteFahrerScreen")
    assert definition["id"] == "transporte/fahrer"
    assert definition["title"] == "Fahrer"
    endpoints = [source["endpoint"] for source in definition["dataSources"]]
    assert "/api/v1/transporte/fahrer" in endpoints
    assert "/api/v1/logistik/tours" in endpoints
    assert "/api/v1/transporte/fahrer" in block
    assert "/api/v1/logistik/tours" in block
    footer = [action["key"] for action in definition["actions"] if action["zone"] == "footer"]
    assert footer[:1] == ["verfuegbar"]
    assert "zone: 'footer'" in block
    assert "DEMO-LS-001" not in block
    assert get_screen_definition("transporte/fahrer")["title"] == "Fahrer"


def test_arbeitsraum_folgt_denselben_listen() -> None:
    definition = build_logistik_tour_fracht_arbeitsraum_screen_definition()
    block = _block("tourFrachtArbeitsraumScreen")
    assert definition["id"] == "logistik/tour-fracht-arbeitsraum"
    assert definition["title"] == "Tour & Fracht"
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert "statusPlacement: 'afterFields'" in block
    assert [table["key"] for table in definition["tables"]] == ["touren", "fracht", "tarife"]
    assert [source["endpoint"] for source in definition["dataSources"]] == [
        "/api/v1/logistik/tours",
        "/api/v1/logistik/frachtbriefe",
        "/api/v1/logistik/freight-tariffs",
    ]
    for endpoint in ("/api/v1/logistik/tours", "/api/v1/logistik/frachtbriefe", "/api/v1/logistik/freight-tariffs"):
        assert endpoint in block
    assert get_screen_definition("logistik/tour-fracht-arbeitsraum")["title"] == "Tour & Fracht"


def test_frachttabellen_staffel_folgt_der_tabelle() -> None:
    definition = build_logistik_frachttabellen_screen_definition()
    block = _block("frachttabellenScreen")
    felder = ["tabelle_nr", "bezeichnung", "einheit", "waehrung", "staffel", "ab_menge", "frachtsatz_eur", "mindestfracht_eur"]
    assert definition["title"] == "Frachttabellen"
    assert [field["key"] for field in definition["fields"]] == felder
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert "statusPlacement: 'afterFields'" in block
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/logistik/frachttabellen"
    assert "/api/v1/logistik/frachttabellen" in block
    assert definition["tables"][0]["columns"][0]["priority"] == "primary"
    assert definition["tables"][0]["columns"][-1]["priority"] == "tertiary"
    assert get_screen_definition("logistik/frachttabellen")["id"] == "logistik/frachttabellen"


def test_versandprofile_register_folgen_den_eingaben() -> None:
    definition = build_logistik_versandprofile_screen_definition()
    block = _block("versandprofileScreen")
    felder = [
        "profil_nr",
        "bezeichnung",
        "versandart",
        "absender_email",
        "absender_name",
        "betreff_vorlage",
        "avis_datum",
        "lieferdatum_erwartet",
        "lieferant_nr",
        "kunden_nr",
        "artikel_nr",
        "menge",
        "notiz",
    ]
    assert definition["id"] == "logistik/versandprofile"
    assert definition["title"] == "Versandprofile"
    assert [field["key"] for tab in definition["tabs"] for field in tab["fields"]] == felder
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert definition["layout"]["columnNavigation"] == "single"
    assert derived_screen_type(definition) == "WORKLIST"
    assert "statusPlacement: 'afterFields'" in block
    endpoints = [source["endpoint"] for source in definition["dataSources"]]
    assert endpoints == ["/api/v1/logistik/versand/profile", "/api/v1/logistik/versand/avise"]
    for endpoint in endpoints:
        assert endpoint in block
    assert [action["key"] for action in definition["actions"] if action["kind"] == "primary"] == ["profil"]
    assert definition["actions"][1]["zone"] == "footer"
    assert "DEMO" not in block
    assert governance_errors(definition) == []
    assert get_screen_definition("logistik/versandprofile")["id"] == "logistik/versandprofile"


def test_terminarten_folgen_der_bezeichnung() -> None:
    definition = build_fuhrpark_terminarten_screen_definition()
    block = _block("fuhrparkTerminartenScreen")
    felder = ["terminart", "intervall_monate", "intervall_km"]
    assert definition["id"] == "fuhrpark/terminarten"
    assert definition["title"] == "Terminarten"
    assert [field["key"] for field in definition["fields"]] == felder
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert definition["layout"]["columnNavigation"] == "single"
    assert derived_screen_type(definition) == "WORKLIST"
    assert "statusPlacement: 'afterFields'" in block
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/fuhrpark/terminarten"
    assert "/api/v1/fuhrpark/terminarten" in block
    assert [action["key"] for action in definition["actions"] if action["kind"] == "primary"] == ["speichern"]
    assert definition["tables"][0]["columns"][0]["priority"] == "primary"
    assert definition["tables"][0]["columns"][-1]["priority"] == "tertiary"
    assert "DEMO" not in block
    assert governance_errors(definition) == []
    assert get_screen_definition("fuhrpark/terminarten")["id"] == "fuhrpark/terminarten"


def test_fuhrpark_rechnungen_folgen_dem_beleg() -> None:
    definition = build_fuhrpark_rechnungen_screen_definition()
    block = _block("fuhrparkRechnungenScreen")
    felder = [
        "rechnungs_nr",
        "datum",
        "fahrzeug_kennzeichen",
        "sachkonto",
        "kostenart",
        "betrag_eur",
        "notiz",
    ]
    assert definition["id"] == "fuhrpark/rechnungen"
    assert definition["title"] == "Fuhrpark-Rechnungen"
    assert [field["key"] for field in definition["fields"]] == felder
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert definition["layout"]["tableProfile"] == "financial"
    assert derived_screen_type(definition) == "WORKLIST"
    assert "statusPlacement: 'afterFields'" in block
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/fuhrpark/rechnungen"
    assert "/api/v1/fuhrpark/rechnungen" in block
    assert [action["key"] for action in definition["actions"] if action["kind"] == "primary"] == ["speichern"]
    assert definition["tables"][0]["columns"][0]["priority"] == "primary"
    assert definition["tables"][0]["columns"][-1]["priority"] == "tertiary"
    assert "DEMO" not in block
    assert governance_errors(definition) == []
    assert get_screen_definition("fuhrpark/rechnungen")["id"] == "fuhrpark/rechnungen"


def test_ausgehende_belege_folgen_dem_formular() -> None:
    definition = build_fuhrpark_ausgehende_dokumente_screen_definition()
    block = _block("fuhrparkAusgehendeDokumenteScreen")
    felder = ["beleg_typ", "formular", "ziel_modul", "beschreibung", "aktiv"]
    assert definition["id"] == "fuhrpark/ausgehende-dokumente"
    assert definition["title"] == "Ausgehende Belege"
    assert [field["key"] for field in definition["fields"]] == felder
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert derived_screen_type(definition) == "WORKLIST"
    assert "statusPlacement: 'afterFields'" in block
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/fuhrpark/ausgehende-dokumente"
    assert "/api/v1/fuhrpark/ausgehende-dokumente" in block
    assert "/versand/versand-avis" in block
    assert [action["key"] for action in definition["actions"] if action["kind"] == "primary"] == ["speichern"]
    assert definition["tables"][0]["columns"][0]["priority"] == "primary"
    assert definition["tables"][0]["columns"][-1]["priority"] == "tertiary"
    assert "DEMO" not in block
    assert governance_errors(definition) == []
    assert get_screen_definition("fuhrpark/ausgehende-dokumente")["id"] == "fuhrpark/ausgehende-dokumente"


def test_fahrzeug_stamm_folgt_kennzeichen_und_typ() -> None:
    definition = build_fuhrpark_fahrzeug_stamm_screen_definition()
    block = _block("fuhrparkFahrzeugStammScreen")
    register = ["allgemein", "technik", "erwerb", "termine", "funktionen"]
    felder = ["kennzeichen", "typ", "kaufsumme_eur", "naechster_tuev_termin", "drucker_name"]
    assert definition["id"] == "fuhrpark/fahrzeug-stamm"
    assert definition["title"] == "Fahrzeug-Stamm"
    assert definition["identityField"] == "kennzeichen"
    assert [tab["key"] for tab in definition["tabs"]] == register
    assert _first_keys(block, register) == sorted(_first_keys(block, register))
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["floorplan"] == "objectPage"
    assert definition["layout"]["contextRail"] == "workflow"
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert derived_screen_type(definition) == "DETAIL"
    assert "statusPlacement: 'afterFields'" in block
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/fuhrpark/fahrzeuge"
    assert "/api/v1/fuhrpark/fahrzeuge" in block
    assert [action["key"] for action in definition["actions"] if action["kind"] == "primary"] == ["speichern"]
    loeschen = next(action for action in definition["actions"] if action["key"] == "loeschen")
    assert loeschen["dangerLevel"] == "high"
    assert loeschen["requiresConfirmation"] is True
    assert "DEMO" not in block
    assert governance_errors(definition) == []
    assert get_screen_definition("fuhrpark/fahrzeug-stamm")["id"] == "fuhrpark/fahrzeug-stamm"


def test_qualifikationen_folgen_der_gueltigkeit() -> None:
    definition = build_personal_qualifikationen_screen_definition()
    block = _block("personalQualifikationenScreen")
    felder = ["employee_ref", "role_code", "qualification_level", "skills", "valid_until"]
    assert definition["id"] == "personal/qualifikationen"
    assert definition["title"] == "Qualifikationen"
    assert definition["domain"] == "hr"
    assert [field["key"] for field in definition["fields"]] == felder
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert derived_screen_type(definition) == "WORKLIST"
    assert "Grundkenntnis" in block
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/training/qualifications"
    assert "/api/v1/training/qualifications" in block
    assert [action["key"] for action in definition["actions"] if action["kind"] == "primary"] == ["speichern"]
    assert definition["tables"][0]["columns"][0]["priority"] == "primary"
    assert definition["tables"][0]["columns"][-1]["priority"] == "tertiary"
    assert "DEMO" not in block
    assert governance_errors(definition) == []
    assert get_screen_definition("personal/qualifikationen")["id"] == "personal/qualifikationen"


def test_onboarding_folgt_den_offenen_laeufen() -> None:
    definition = build_personal_onboarding_screen_definition()
    block = _block("personalOnboardingScreen")
    felder = ["employee_ref", "checklist_id", "assigned_by", "due_date"]
    assert definition["id"] == "personal/onboarding"
    assert definition["title"] == "Onboarding"
    assert definition["domain"] == "hr"
    assert [field["key"] for field in definition["fields"]] == felder
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert derived_screen_type(definition) == "WORKLIST"
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/training/onboarding/runs"
    assert "/api/v1/training/onboarding/runs" in block
    assert [action["key"] for action in definition["actions"] if action["kind"] == "primary"] == ["speichern"]
    assert definition["tables"][0]["columns"][0]["priority"] == "primary"
    assert definition["tables"][0]["columns"][-1]["priority"] == "tertiary"
    assert "DEMO" not in block
    assert governance_errors(definition) == []
    assert get_screen_definition("personal/onboarding")["id"] == "personal/onboarding"


def test_schulungen_folgen_der_faelligkeit() -> None:
    definition = build_personal_schulungen_screen_definition()
    block = _block("personalSchulungenScreen")
    felder = ["employee_ref", "course_id", "assigned_by", "due_date"]
    assert definition["id"] == "personal/schulungen"
    assert definition["title"] == "Schulungen"
    assert definition["domain"] == "hr"
    assert [field["key"] for field in definition["fields"]] == felder
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert derived_screen_type(definition) == "WORKLIST"
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/training/assignments"
    assert "/api/v1/training/assignments" in block
    assert [action["key"] for action in definition["actions"] if action["kind"] == "primary"] == ["speichern"]
    assert definition["tables"][0]["columns"][0]["priority"] == "primary"
    assert definition["tables"][0]["columns"][-1]["priority"] == "tertiary"
    assert "DEMO" not in block
    assert governance_errors(definition) == []
    assert get_screen_definition("personal/schulungen")["id"] == "personal/schulungen"


def test_bewerbungen_folgen_der_pipeline() -> None:
    definition = build_personal_bewerbungen_screen_definition()
    block = _block("personalBewerbungenScreen")
    felder = ["applicant_name", "applicant_email", "position_title", "source"]
    assert definition["id"] == "personal/bewerbungen"
    assert definition["title"] == "Bewerbungen"
    assert definition["domain"] == "hr"
    assert [field["key"] for field in definition["fields"]] == felder
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert derived_screen_type(definition) == "WORKLIST"
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/personal/applications"
    assert "/api/v1/personal/applications" in block
    assert [action["key"] for action in definition["actions"] if action["kind"] == "primary"] == ["speichern"]
    actions = {action["key"]: action for action in definition["tables"][0]["rowActions"]}
    assert {"einwilligung", "loeschen"} <= actions.keys()
    assert actions["loeschen"]["disabledWhen"] == {"field": "gesperrt", "values": [True]}
    assert definition["tables"][0]["columns"][0]["priority"] == "primary"
    assert definition["tables"][0]["columns"][-1]["priority"] == "tertiary"
    assert "DEMO" not in block
    assert governance_errors(definition) == []
    assert get_screen_definition("personal/bewerbungen")["id"] == "personal/bewerbungen"


def test_applications_haben_loesch_route() -> None:
    from app.api.v1.endpoints import personal_bewerbungen as personal_ep

    loesch = [
        route
        for route in personal_ep.router.routes
        if getattr(route, "path", "").endswith("/applications/{application_id}")
        and "DELETE" in (getattr(route, "methods", set()) or set())
    ]
    assert len(loesch) == 1, "Genau ein DELETE-Weg am kanonischen Bewerbungsrouter erforderlich"
