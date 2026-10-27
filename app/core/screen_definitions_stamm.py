"""Studio-Objektmasken fuer Stammdaten (MASKEN-STUDIO-ROLLOUT, Stammdatenwelle Batch 9)."""

from __future__ import annotations

from typing import Any

from app.core.stamm_object_page_parent import (
    build_stamm_object_page,
    patch_get_screen_definition_for_stamm,
    stamm_entity_source,
    stamm_entity_tab,
    stamm_kopf_tab,
    stamm_tab_source,
)

from app.core.screen_definitions_stamm_batch13 import (
    BATCH13_ROUTEN,
    BATCH13_SCREEN_BUILDERS,
    BATCH13_SYNONYME,
)



def _feld(key: str, label: str, typ: str = "text", **mehr: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "type": typ, **mehr}


def _eingabe(felder: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "key": f["key"],
            "label": f["label"],
            "type": "number" if f.get("type") == "currency" else f.get("type", "text"),
        }
        for f in felder
    ]


def _stamm(
    *,
    screen_id: str,
    domain: str,
    title: str,
    subtitle: str,
    endpoint: str,
    identity: str | None,
    felder: list[dict[str, Any]],
    edit_permission: str,
    test_id: str,
    purpose: str,
    prompts: list[str],
    bundle: str | None = None,
    creation: dict[str, Any] | None = None,
    extra_actions: list[dict[str, Any]] | None = None,
    edit_action_overrides: dict[str, Any] | None = None,
    entity_projection: dict[str, str] | None = None,
) -> dict[str, Any]:
    kopf = list(felder)
    if identity and not any(f["key"] == identity for f in kopf):
        kopf.insert(0, _feld(identity, "Kennung", readOnly=True))
    definition = build_stamm_object_page(
        screen_id=screen_id,
        domain=domain,
        title=title,
        subtitle=subtitle,
        identity_field=identity,
        data_sources=[stamm_entity_source(endpoint)],
        tabs=[stamm_kopf_tab(kopf)],
        edit_permission=edit_permission,
        no_workflow_reason=f"{title} ist ein Verwaltungsobjekt ohne Beleg-Lebenszyklus.",
        business_purpose=purpose,
        example_prompts=prompts,
        test_id=test_id,
        bundle_group=bundle or domain,
        creation=creation,
        extra_actions=extra_actions,
        edit_action_overrides=edit_action_overrides,
    )
    if entity_projection is not None:
        definition["entityProjection"] = entity_projection
    return definition



# Artikel (voller Stamm)
_ARTIKEL_STAMM = [
    _feld("article_number", "Artikel-Nr.", required=True),
    _feld("name", "Bezeichnung", required=True),
    _feld("unit", "Einheit", required=True, width=80),
    _feld("category", "Kategorie", required=True),
]
_ARTIKEL_PREISE = [_feld("sales_price", "Verkaufspreis", "currency", required=True)]
_ARTIKEL_LAGER = [_feld("lagerartikel", "Lagerartikel", "boolean")]
_ARTIKEL_QUALITAET = [_feld("qs_pruefung_erforderlich", "QS-Pruefung", "boolean")]

def _register(key: str, label: str, quelle: str, spalten: list[dict[str, Any]]) -> dict[str, Any]:
    from app.core.stamm_object_page_parent import stamm_lazy_table_tab  # noqa: PLC0415
    return stamm_lazy_table_tab(
        key=key, label=label, data_source_key=quelle, columns=spalten, server_pagination=False,
    )


ARTIKEL_BEARBEITEN_FELDER = tuple(
    f["key"] for f in (*_ARTIKEL_STAMM, *_ARTIKEL_PREISE, *_ARTIKEL_LAGER, *_ARTIKEL_QUALITAET)
)


def build_artikel_stamm() -> dict[str, Any]:
    """Artikelstamm: vollstaendige Register (Pilot Batch 9)."""
    return build_stamm_object_page(
        screen_id="artikel/stamm",
        domain="lager",
        title="Artikel",
        subtitle="Artikelstamm",
        identity_field="article_number",
        creation={
            "endpoint": "/api/v1/articles/",
            "permission": "artikel.create",
            "detailRoute": "/artikel/{entity_id}",
            "defaults": {"currency": "EUR", "lagerartikel": True, "rabattfaehig": True, "skontofaehig": True},
        },
        summary=[
            {"key": "article_number", "label": "Artikel-Nr.", "value": None, "kind": "identity"},
            {"key": "available_stock", "label": "Verfuegbar", "value": None, "kind": "kpi"},
            {"key": "sales_price", "label": "Verkaufspreis", "value": None, "kind": "kpi"},
        ],
        data_sources=[
            stamm_entity_source("/api/v1/articles/{entity_id}"),
            stamm_tab_source("lieferanten", "/api/v1/articles/{entity_id}/suppliers"),
            stamm_tab_source("preise", "/api/v1/articles/{entity_id}/prices"),
            stamm_tab_source("dokumente", "/api/v1/articles/{entity_id}/documents"),
        ],
        tabs=[
            stamm_kopf_tab([*_ARTIKEL_STAMM, _feld("is_active", "Aktiv", "boolean", readOnly=True)]),
            stamm_entity_tab(key="preise_steuer", label="Preise und Steuer", fields=_ARTIKEL_PREISE),
            stamm_entity_tab(
                key="lager",
                label="Lager",
                fields=[
                    *_ARTIKEL_LAGER,
                    _feld("current_stock", "Bestand", "number", readOnly=True),
                    _feld("reserved_stock", "Reserviert", "number", readOnly=True),
                    _feld("available_stock", "Verfuegbar", "number", readOnly=True),
                ],
            ),
            stamm_entity_tab(key="qualitaet", label="Qualitaet und Gefahrgut", fields=_ARTIKEL_QUALITAET),
            _register("lieferanten", "Lieferanten", "lieferanten", [
                {"key": "supplier_number", "label": "Lieferant", "width": 140, "sortable": True},
                {"key": "supplier_article_number", "label": "Lieferanten-Art.-Nr.", "width": 160},
                {"key": "purchase_price", "label": "EK-Preis", "numeric": True, "renderKind": "currency"},
                {"key": "lead_time_days", "label": "Lieferzeit (Tage)", "numeric": True},
                {"key": "is_preferred", "label": "Bevorzugt", "renderKind": "boolean", "width": 90},
            ]),
            _register("preise", "Preisvereinbarungen", "preise", [
                {"key": "partner_id", "label": "Partner", "width": 140, "sortable": True},
                {"key": "price_net", "label": "Netto", "numeric": True, "renderKind": "currency", "sortable": True},
                {"key": "price_unit", "label": "Preiseinheit", "width": 100},
                {"key": "valid_from", "label": "Gueltig ab", "renderKind": "date", "sortable": True},
                {"key": "valid_to", "label": "Gueltig bis", "renderKind": "date"},
            ]),
            _register("dokumente", "Dokumente", "dokumente", [
                {"key": "document_name", "label": "Dokument", "width": 220, "sortable": True},
                {"key": "document_type", "label": "Typ", "width": 120, "filterable": True},
                {"key": "document_category", "label": "Kategorie", "width": 120, "filterable": True},
                {"key": "created_at", "label": "Erfasst", "renderKind": "date", "sortable": True},
            ]),
        ],
        edit_permission="artikel.update",
        edit_action_key="bearbeiten",
        edit_action_overrides={
            "commandEndpoint": "/api/v1/articles/{entity_id}/actions/bearbeiten",
            "method": "POST",
            "inputFields": _eingabe([*_ARTIKEL_STAMM, *_ARTIKEL_PREISE, *_ARTIKEL_LAGER, *_ARTIKEL_QUALITAET]),
        },
        no_workflow_reason="Artikelstamm ist ein Verwaltungsobjekt — Ablaeufe liegen in den Belegen, nicht im Stammsatz.",
        business_purpose=(
            "Artikelstamm fuer Verkauf, Einkauf und Lager: Kennungen, Preise und Steuer, "
            "Lagerfuehrung, Qualitaet; Lieferanten, Preisvereinbarungen und Dokumente."
        ),
        example_prompts=[
            "Welchen Verkaufspreis und Steuerschluessel hat Artikel {entity_id}?",
            "Welche Lieferanten liefern Artikel {entity_id} und zu welchem EK-Preis?",
            "Ist Artikel {entity_id} chargen- oder QS-pflichtig?",
        ],
        sensitive_fields=["purchase_price"],
        test_id="artikel-stamm",
        density="expertDense",
        context_rail="combined",
        table_profile="inventory",
        payload_budget_kb=48,
        requires_virtual_tables=True,
        bundle_group="lager",
    )



def build_lager_charge_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="lager/charge",
        domain="lager",
        title="Charge",
        subtitle="Chargenstamm",
        endpoint="/api/v1/chargen/{entity_id}",
        identity="chargenId",
        felder=[
        _feld("chargenId", "Chargen-ID"),
        _feld("artikel", "Artikel"),
        _feld("menge", "Menge", "number"),
        _feld("status", "Status"),
        ],
        edit_permission="lager.charge.update",
        test_id="lager-charge-stamm",
        purpose="Chargenstamm mit QS- und Rückverfolgungsdaten.",
        prompts=['Welchen Status hat Charge {entity_id}?'],
    )



def build_personal_mitarbeiter_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="personal/mitarbeiter",
        domain="personal",
        title="Mitarbeiter",
        subtitle="Personalstamm",
        endpoint="/api/v1/personal/mitarbeiter/{entity_id}",
        identity="name",
        felder=[
        _feld("name", "Name"),
        _feld("email", "E-Mail", "email"),
        _feld("abteilung", "Abteilung"),
        _feld("status", "Status"),
        ],
        edit_permission="personal.mitarbeiter.update",
        test_id="personal-mitarbeiter-stamm",
        purpose="Mitarbeiterstammdaten fuer HR.",
        prompts=['In welcher Abteilung arbeitet Mitarbeiter {entity_id}?'],
    )



def build_agrar_psm_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="agrar/psm",
        domain="agrar",
        title="PSM",
        subtitle="Pflanzenschutzmittel",
        endpoint="/api/v1/agrar/psm/{entity_id}",
        identity="mittel",
        felder=[
        _feld("mittel", "Mittel"),
        _feld("wirkstoff", "Wirkstoff"),
        _feld("zulassungsnummer", "Zulassung"),
        _feld("status", "Status"),
        ],
        edit_permission="agrar.psm.update",
        test_id="agrar-psm-stamm",
        purpose="PSM-Stammdaten fuer Agrar.",
        prompts=['Welche Zulassung hat PSM {entity_id}?'],
    )



def build_crm_aktivitaet_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="crm/aktivitaet",
        domain="crm",
        title="Aktivitaet",
        subtitle="CRM-Aktivitaet",
        endpoint="/api/v1/crm/activities/{entity_id}",
        identity="subject",
        felder=[
        _feld("subject", "Betreff"),
        _feld("activity_type", "Typ"),
        _feld("status", "Status"),
        _feld("due_date", "Faellig", "date"),
        ],
        edit_permission="crm.activity.update",
        test_id="crm-aktivitaet-stamm",
        purpose="Aktivitaetsdetail im CRM.",
        prompts=['Wann ist Aktivitaet {entity_id} faellig?'],
    )



def build_crm_kontakt_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="crm/kontakt",
        domain="crm",
        title="Kontakt",
        subtitle="Ansprechpartner",
        endpoint="/api/v1/crm/contacts/{entity_id}",
        identity="name",
        felder=[
        _feld("name", "Name"),
        _feld("email", "E-Mail", "email"),
        _feld("phone", "Telefon"),
        _feld("position", "Funktion"),
        ],
        edit_permission="crm.contact.update",
        test_id="crm-kontakt-stamm",
        purpose="Kontaktstammdaten.",
        prompts=['Welche E-Mail hat Kontakt {entity_id}?'],
    )



def build_crm_betriebsprofil_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="crm/betriebsprofil",
        domain="crm",
        title="Betriebsprofil",
        subtitle="Betriebsprofil",
        endpoint="/api/v1/crm/betriebsprofile/{entity_id}",
        identity="name",
        felder=[
        _feld("name", "Betrieb"),
        _feld("vvvo_nr", "VVVO-Nr."),
        _feld("ort", "Ort"),
        _feld("status", "Status"),
        ],
        edit_permission="crm.betriebsprofil.update",
        test_id="crm-betriebsprofil-stamm",
        purpose="Betriebsprofil fuer Agrarkunden.",
        prompts=['Welche VVVO hat Betrieb {entity_id}?'],
    )



def build_crm_campaign_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="crm/campaign",
        domain="crm",
        title="Kampagne",
        subtitle="Marketingkampagne",
        endpoint="/api/v1/crm/campaigns/{entity_id}",
        identity="name",
        felder=[
        _feld("name", "Name"),
        _feld("status", "Status"),
        _feld("channel", "Kanal"),
        _feld("start_date", "Start", "date"),
        ],
        edit_permission="crm.campaign.update",
        test_id="crm-campaign-stamm",
        purpose="Kampagnendetail.",
        prompts=['Welchen Status hat Kampagne {entity_id}?'],
    )



def build_crm_campaign_template_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="crm/campaign-template",
        domain="crm",
        title="Kampagnenvorlage",
        subtitle="Vorlage",
        endpoint="/api/v1/crm/campaigns/templates/{entity_id}",
        identity="name",
        felder=[
        _feld("name", "Name"),
        _feld("channel", "Kanal"),
        _feld("subject", "Betreff"),
        ],
        edit_permission="crm.campaign.update",
        test_id="crm-campaign-template-stamm",
        purpose="Wiederverwendbare Kampagnenvorlage.",
        prompts=['Welchen Kanal nutzt Vorlage {entity_id}?'],
    )



def build_crm_consent_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="crm/consent",
        domain="crm",
        title="Einwilligung",
        subtitle="DSGVO-Einwilligung",
        endpoint="/api/v1/crm/consents/{entity_id}",
        identity="purpose",
        felder=[
        _feld("purpose", "Zweck"),
        _feld("status", "Status"),
        _feld("granted_at", "Erteilt am", "date"),
        ],
        edit_permission="crm.consent.update",
        test_id="crm-consent-stamm",
        purpose="Einwilligungsnachweis.",
        prompts=['Ist Einwilligung {entity_id} aktiv?'],
    )



def build_crm_gdpr_request_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="crm/gdpr-request",
        domain="crm",
        title="DSGVO-Anfrage",
        subtitle="Betroffenenanfrage",
        endpoint="/api/v1/gdpr/requests/{entity_id}",
        identity="request_type",
        felder=[
        _feld("request_type", "Typ"),
        _feld("status", "Status"),
        _feld("submitted_at", "Eingegangen", "date"),
        ],
        edit_permission="gdpr.request.update",
        test_id="crm-gdpr-request-stamm",
        purpose="DSGVO-Anfrage bearbeiten.",
        prompts=['Welchen Status hat Anfrage {entity_id}?'],
    )



def build_crm_segment_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="crm/segment",
        domain="crm",
        title="Segment",
        subtitle="Marketingsegment",
        endpoint="/api/v1/crm/segments/{entity_id}",
        identity="name",
        felder=[
        _feld("name", "Name"),
        _feld("description", "Beschreibung", "textarea"),
        _feld("member_count", "Mitglieder", "number", readOnly=True),
        ],
        edit_permission="crm.segment.update",
        test_id="crm-segment-stamm",
        purpose="Segmentdefinition.",
        prompts=['Wie viele Mitglieder hat Segment {entity_id}?'],
    )



def build_finance_bank_account_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="finance/bank-account",
        domain="finance",
        title="Bankkonto",
        subtitle="Bankverbindung",
        endpoint="/api/v1/finance/bank-accounts/{entity_id}",
        identity="iban",
        felder=[
        _feld("iban", "IBAN"),
        _feld("bank_name", "Bank"),
        _feld("account_holder", "Kontoinhaber"),
        _feld("currency", "Waehrung"),
        ],
        edit_permission="finance.bank_account.update",
        test_id="finance-bank-account-stamm",
        purpose="Bankkonto-Stammdaten.",
        prompts=['Welche IBAN hat Konto {entity_id}?'],
    )



def build_qualitaet_labor_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="qualitaet/labor-auftrag",
        domain="qualitaet",
        title="Laborauftrag",
        subtitle="Labor",
        endpoint="/api/v1/qualitaet/labor-auftraege/{entity_id}",
        identity="auftrags_nr",
        felder=[
        _feld("auftrags_nr", "Auftrags-Nr."),
        _feld("probe", "Probe"),
        _feld("status", "Status"),
        _feld("labor", "Labor"),
        ],
        edit_permission="qualitaet.labor.update",
        test_id="qualitaet-labor-stamm",
        purpose="Laborauftrag und Befund.",
        prompts=['Welchen Status hat Laborauftrag {entity_id}?'],
    )



def build_service_anfrage_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="service/anfrage",
        domain="service",
        title="Serviceanfrage",
        subtitle="Service",
        endpoint="/api/v1/service/anfragen/{entity_id}",
        identity="titel",
        felder=[
        _feld("titel", "Titel"),
        _feld("status", "Status"),
        _feld("prioritaet", "Prioritaet"),
        _feld("kunde", "Kunde"),
        ],
        edit_permission="service.anfrage.update",
        test_id="service-anfrage-stamm",
        purpose="Serviceanfrage bearbeiten.",
        prompts=['Welche Prioritaet hat Anfrage {entity_id}?'],
    )



def build_waage_wiegeschein_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="waage/wiegeschein",
        domain="waage",
        title="Wiegeschein",
        subtitle="Waage",
        endpoint="/api/v1/weighing-tickets/{entity_id}",
        identity="ticket_number",
        felder=[
        _feld("ticket_number", "Schein-Nr."),
        _feld("article", "Artikel"),
        _feld("net_weight", "Netto", "number"),
        _feld("status", "Status"),
        ],
        edit_permission="waage.ticket.update",
        test_id="waage-wiegeschein-stamm",
        purpose="Wiegeschein-Detail.",
        prompts=['Welches Nettogewicht hat Wiegeschein {entity_id}?'],
    )



def build_fibu_abschluss_checklist_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="fibu/abschluss-checklist",
        domain="finance",
        title="Abschluss-Checkliste",
        subtitle="FIBU-Abschluss",
        endpoint="/api/v1/finance/closing-checklists/{entity_id}",
        identity="name",
        felder=[
        _feld("name", "Bezeichnung"),
        _feld("period", "Periode"),
        _feld("status", "Status"),
        ],
        edit_permission="finance.closing.update",
        test_id="fibu-abschluss-checklist-stamm",
        purpose="Monatsabschluss-Checkliste.",
        prompts=['Welche Periode hat Checkliste {entity_id}?'],
    )



def build_agrar_kontrakt_detail_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="agrar/kontrakt-detail",
        domain="agrar",
        title="Kontrakt",
        subtitle="Kontraktdetail",
        endpoint="/api/v1/kontrakte/{entity_id}",
        identity="contract_number",
        felder=[
        _feld("contract_number", "Kontrakt-Nr."),
        _feld("partner_name", "Partner"),
        _feld("status", "Status"),
        _feld("restmenge", "Restmenge", "number"),
        ],
        edit_permission="agrar.kontrakt.update",
        test_id="agrar-kontrakt-detail-stamm",
        purpose="Kontraktdetail Agrar.",
        prompts=['Welche Restmenge hat Kontrakt {entity_id}?'],
    )



def build_silo_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="silo/silo",
        domain="lager",
        title="Silo",
        subtitle="Silostamm",
        endpoint="/api/v1/silo/silos/{entity_id}/details",
        identity="silo_id",
        felder=[
        _feld("silo_id", "Silo"),
        _feld("kapazitaet", "Kapazitaet", "number"),
        _feld("fuellstand", "Fuellstand", "number"),
        ],
        edit_permission="silo.update",
        test_id="silo-stamm",
        purpose="Silokapazitaeten und Bestand.",
        prompts=['Wie hoch ist der Fuellstand von Silo {entity_id}?'],
    )



def build_crm_vertreter_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="crm/vertreter",
        domain="crm",
        title="Vertreter",
        subtitle="Vertreterstamm",
        endpoint="/api/v1/crm/vertreter/{entity_id}",
        identity="vertreter_nr",
        felder=[
        _feld("vertreter_nr", "Vertreter-Nr."),
        _feld("name", "Name"),
        _feld("vertretergruppe_nr", "Gruppe"),
        ],
        edit_permission="crm.vertreter.update",
        test_id="crm-vertreter-stamm",
        purpose="Vertreterstammdaten.",
        prompts=['Welche Gruppe hat Vertreter {entity_id}?'],
    )



def build_stammdaten_hausbank_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="stammdaten/hausbank",
        domain="finance",
        title="Hausbank",
        subtitle="Hausbank",
        endpoint="/api/v1/stammdaten/hausbanken/{entity_id}",
        identity="bank_nr",
        felder=[
        _feld("bank_nr", "Bank-Nr.", readOnly=True),
        _feld("bezeichnung", "Bezeichnung"),
        _feld("iban", "IBAN"),
        _feld("bic", "BIC"),
        _feld("bank_name", "Bankname"),
        _feld("kontonummer", "Kontonummer"),
        _feld("blz", "BLZ"),
        _feld("waehrung", "Währung"),
        _feld("erechnung_aktiv", "E-Rechnung aktiv", "boolean"),
        _feld("sepa_glaeubiger_id", "SEPA-Gläubiger-ID"),
        _feld("standard", "Standardbank", "boolean"),
        _feld("aktiv", "Aktiv", "boolean", readOnly=True),
        ],
        edit_permission="finance.hausbank.update",
        test_id="stammdaten-hausbank-stamm",
        purpose="Hausbankenstamm.",
        prompts=['Welche BLZ hat Hausbank {entity_id}?'],
        edit_action_overrides={
            "commandEndpoint": "/api/v1/stammdaten/hausbanken/{entity_id}",
            "method": "PUT",
            "inputFields": [
                _feld("bank_nr", "Bank-Nr.", readOnly=True),
                _feld("bezeichnung", "Bezeichnung", required=True),
                _feld("iban", "IBAN", required=True),
                _feld("bic", "BIC"),
                _feld("bank_name", "Bankname"),
                _feld("kontonummer", "Kontonummer"),
                _feld("blz", "BLZ"),
                _feld("waehrung", "Währung"),
                _feld("erechnung_aktiv", "E-Rechnung aktiv", "boolean"),
                _feld("sepa_glaeubiger_id", "SEPA-Gläubiger-ID"),
                _feld("standard", "Standardbank", "boolean"),
            ],
        },
    )



def build_stammdaten_mengeneinheit_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="stammdaten/mengeneinheit",
        domain="lager",
        title="Mengeneinheit",
        subtitle="ME-Stamm",
        endpoint="/api/v1/artikel/mengeneinheiten/stamm/{entity_id}",
        identity="einheit_kuerzel",
        felder=[
        _feld("einheit_kuerzel", "Einheit", readOnly=True),
        _feld("bezeichnung", "Bezeichnung"),
        _feld("basis_einheit", "Basiseinheit"),
        _feld("umrechnungsfaktor", "Umrechnungsfaktor", "number"),
        _feld("dezimalstellen", "Dezimalstellen", "number"),
        _feld("aktiv", "Aktiv", "boolean", readOnly=True),
        ],
        edit_permission="stammdaten.mengeneinheit.update",
        test_id="stammdaten-mengeneinheit-stamm",
        purpose="Mengeneinheiten.",
        prompts=['Wie lautet Code von ME {entity_id}?'],
        edit_action_overrides={
            "commandEndpoint": "/api/v1/artikel/mengeneinheiten/stamm/{entity_id}",
            "method": "PUT",
            "inputFields": [
                _feld("einheit_kuerzel", "Einheit", readOnly=True),
                _feld("bezeichnung", "Bezeichnung", required=True),
                _feld("basis_einheit", "Basiseinheit"),
                _feld("umrechnungsfaktor", "Umrechnungsfaktor", "number"),
                _feld("dezimalstellen", "Dezimalstellen", "number"),
            ],
        },
    )



def build_portal_zertifikat_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="portal/zertifikat",
        domain="portal",
        title="Zertifikat",
        subtitle="Portal-Zertifikat",
        endpoint="/api/v1/portal/zertifikate/{entity_id}",
        identity="typ",
        felder=[
        _feld("typ", "Typ"),
        _feld("gueltig_bis", "Gueltig bis", "date"),
        _feld("status", "Status"),
        ],
        edit_permission="portal.zertifikat.update",
        test_id="portal-zertifikat-stamm",
        purpose="Kundenportal-Zertifikat.",
        prompts=['Bis wann ist Zertifikat {entity_id} gueltig?'],
    )



def build_produktion_rezepturgruppe_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="produktion/rezepturgruppe",
        domain="produktion",
        title="Rezepturgruppe",
        subtitle="Produktion",
        endpoint="/api/v1/produktion/mischfutter/rezepturgruppen/{entity_id}",
        identity="name",
        felder=[
        _feld("name", "Name"),
        _feld("beschreibung", "Beschreibung", "textarea"),
        ],
        edit_permission="produktion.rezepturgruppe.update",
        test_id="produktion-rezepturgruppe-stamm",
        purpose="Rezepturgruppen.",
        prompts=['Welche Rezepte gehoeren zu Gruppe {entity_id}?'],
    )



def build_rezepte_editor_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="rezepte/rezept",
        domain="produktion",
        title="Rezept",
        subtitle="Rezeptur",
        endpoint="/api/v1/futtermittel/rezepte/{entity_id}",
        identity="name",
        felder=[
        _feld("name", "Name"),
        _feld("artikel_nummer", "Artikel-Nr."),
        _feld("status", "Status"),
        ],
        edit_permission="futtermittel.rezept.update",
        test_id="rezepte-rezept-stamm",
        purpose="Rezeptur-Editor Stammdaten.",
        prompts=['Welche Artikelnummer hat Rezept {entity_id}?'],
    )



def build_fibu_anlage_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="fibu/anlage",
        domain="finance",
        title="Anlage",
        subtitle="Anlagevermoegen",
        endpoint="/api/v1/finance/asset-accounting/assets/{entity_id}",
        identity="asset_number",
        felder=[
        _feld("id", "ID", readOnly=True),
        _feld("asset_number", "Inventar-Nr."),
        _feld("description", "Bezeichnung"),
        _feld("acquisition_cost", "Anschaffungswert", "currency"),
        ],
        entity_projection={
            "id": "asset.id",
            "asset_number": "asset.asset_number",
            "description": "asset.description",
            "acquisition_cost": "asset.acquisition_cost",
        },
        edit_permission="finance.asset.update",
        test_id="fibu-anlage-stamm",
        purpose="Anlagevermoegen.",
        prompts=['Welchen Anschaffungswert hat Anlage {entity_id}?'],
    )



def build_stammdaten_individuelle_artikelnummer_stamm() -> dict[str, Any]:
    definition = _stamm(
        screen_id="stammdaten/individuelle-artikelnummer",
        domain="lager",
        title="Individuelle Artikelnummer",
        subtitle="Artikelnummer",
        endpoint="/api/v1/artikel/individuelle-nummern/{entity_id}",
        identity="id",
        felder=[
        _feld("id", "ID", readOnly=True),
        _feld("artikel_nr", "Artikel-Nr."),
        _feld("partner_nr", "Partner-Nr."),
        _feld("partner_typ", "Partner-Typ"),
        _feld("indiv_artikel_nr", "Individuelle Artikel-Nr."),
        _feld("indiv_bezeichnung", "Bezeichnung"),
        _feld("gueltig_von", "Gültig von", "date"),
        _feld("gueltig_bis", "Gültig bis", "date"),
        _feld("aktiv", "Aktiv", "boolean", readOnly=True),
        _feld("created_at", "Angelegt am", "datetime", readOnly=True),
        ],
        edit_permission="stammdaten.individuelle_artikelnummer.update",
        test_id="stammdaten-ind-artnr-stamm",
        purpose="Partner-spezifische Artikelnummern.",
        prompts=['Welcher Artikel steckt hinter Nummer {entity_id}?'],
        edit_action_overrides={
            "label": "Bearbeiten nicht verfügbar",
            "disabled": True,
            "stubReason": "Der bestehende API-Vertrag bietet für individuelle Artikelnummern keine Aktualisierung an.",
        },
    )
    return definition



def build_verkauf_kunde_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="verkauf/kunde",
        domain="verkauf",
        title="Kunde",
        subtitle="Verkaufskundenstamm",
        endpoint="/api/v1/crm/customers/{entity_id}",
        identity="customer_number",
        felder=[
        _feld("customer_number", "Kunden-Nr."),
        _feld("name", "Name"),
        _feld("ort", "Ort"),
        _feld("status", "Status"),
        ],
        edit_permission="crm.customer.update",
        test_id="verkauf-kunde-stamm",
        purpose="Kundenstamm Verkauf.",
        prompts=['Wo sitzt Kunde {entity_id}?'],
    )



def build_crm_lieferant_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="crm/lieferant",
        domain="crm",
        title="Lieferant",
        subtitle="CRM-Lieferantenstamm",
        endpoint="/api/v1/crm/business-partners/{entity_id}",
        identity="partner_number",
        felder=[
        _feld("partner_number", "Partner-Nr."),
        _feld("name", "Name"),
        _feld("ort", "Ort"),
        _feld("status", "Status"),
        ],
        edit_permission="crm.supplier.update",
        test_id="crm-lieferant-stamm",
        purpose="Lieferantenstamm CRM.",
        prompts=['Ist Lieferant {entity_id} aktiv?'],
    )



def build_futter_einzel_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="futter/einzel",
        domain="futtermittel",
        title="Einzelfuttermittel",
        subtitle="Futter Einzel",
        endpoint="/api/v1/futter/einzelfuttermittel/{entity_id}",
        identity="artikel_nummer",
        felder=[
        _feld("artikel_nummer", "Artikel-Nr."),
        _feld("bezeichnung", "Bezeichnung"),
        _feld("protein", "Protein %", "number"),
        ],
        edit_permission="futtermittel.einzelfuttermittel.update",
        test_id="futter-einzel-stamm",
        purpose="Einzelfuttermittel (Futter-Pfad).",
        prompts=['Welches Protein hat Einzelfutter {entity_id}?'],
    )



def build_futter_misch_stamm() -> dict[str, Any]:
    return _stamm(
        screen_id="futter/misch",
        domain="futtermittel",
        title="Mischfuttermittel",
        subtitle="Futter Misch",
        endpoint="/api/v1/futter/mischfuttermittel/{entity_id}",
        identity="produkt_code",
        felder=[
        _feld("produkt_code", "Produktcode"),
        _feld("bezeichnung", "Bezeichnung"),
        _feld("status", "Status"),
        ],
        edit_permission="futtermittel.mischfuttermittel.update",
        test_id="futter-misch-stamm",
        purpose="Mischfuttermittel (Futter-Pfad).",
        prompts=['Welchen Status hat Mischfutter {entity_id}?'],
    )


STAMM_SCREEN_BUILDERS = {
    "artikel/stamm": build_artikel_stamm,
    "lager/charge": build_lager_charge_stamm,
    "personal/mitarbeiter": build_personal_mitarbeiter_stamm,
    "agrar/psm": build_agrar_psm_stamm,
    "crm/aktivitaet": build_crm_aktivitaet_stamm,
    "crm/kontakt": build_crm_kontakt_stamm,
    "crm/betriebsprofil": build_crm_betriebsprofil_stamm,
    "crm/campaign": build_crm_campaign_stamm,
    "crm/campaign-template": build_crm_campaign_template_stamm,
    "crm/consent": build_crm_consent_stamm,
    "crm/gdpr-request": build_crm_gdpr_request_stamm,
    "crm/segment": build_crm_segment_stamm,
    "finance/bank-account": build_finance_bank_account_stamm,
    "qualitaet/labor-auftrag": build_qualitaet_labor_stamm,
    "service/anfrage": build_service_anfrage_stamm,
    "waage/wiegeschein": build_waage_wiegeschein_stamm,
    "fibu/abschluss-checklist": build_fibu_abschluss_checklist_stamm,
    "agrar/kontrakt-detail": build_agrar_kontrakt_detail_stamm,
    "silo/silo": build_silo_stamm,
    "crm/vertreter": build_crm_vertreter_stamm,
    "stammdaten/hausbank": build_stammdaten_hausbank_stamm,
    "stammdaten/mengeneinheit": build_stammdaten_mengeneinheit_stamm,
    "portal/zertifikat": build_portal_zertifikat_stamm,
    "produktion/rezepturgruppe": build_produktion_rezepturgruppe_stamm,
    "rezepte/rezept": build_rezepte_editor_stamm,
    "fibu/anlage": build_fibu_anlage_stamm,
    "stammdaten/individuelle-artikelnummer": build_stammdaten_individuelle_artikelnummer_stamm,
    "verkauf/kunde": build_verkauf_kunde_stamm,
    "crm/lieferant": build_crm_lieferant_stamm,
    "futter/einzel": build_futter_einzel_stamm,
    "futter/misch": build_futter_misch_stamm,
    **BATCH13_SCREEN_BUILDERS,
}

STAMM_ROUTEN = {
    "artikel/stamm": "/artikel",
    "lager/charge": "/charge/stamm",
    "personal/mitarbeiter": "/personal/mitarbeiter",
    "agrar/psm": "/agrar/psm/stamm",
    "crm/aktivitaet": "/crm/aktivitaet",
    "crm/kontakt": "/crm/kontakt",
    "crm/betriebsprofil": "/crm/betriebsprofil",
    "crm/campaign": "/crm/campaign",
    "crm/campaign-template": "/crm/campaign-template",
    "crm/consent": "/crm/consent",
    "crm/gdpr-request": "/crm/gdpr-request",
    "crm/segment": "/crm/segment",
    "finance/bank-account": "/finance/bankkonten",
    "qualitaet/labor-auftrag": "/qualitaet/labor",
    "service/anfrage": "/service/anfrage",
    "waage/wiegeschein": "/waage/wiegeschein",
    "fibu/abschluss-checklist": "/fibu/abschluss-checklist-detail",
    "agrar/kontrakt-detail": "/kontrakte",
    "silo/silo": "/silo/kapazitaeten",
    "crm/vertreter": "/crm/vertreterstamm",
    "stammdaten/hausbank": "/stammdaten/hausbanken",
    "stammdaten/mengeneinheit": "/stammdaten/mengeneinheiten",
    "portal/zertifikat": "/portal/zertifikate",
    "produktion/rezepturgruppe": "/produktion/rezepturgruppen",
    "rezepte/rezept": "/rezepte/editor",
    "fibu/anlage": "/fibu/anlage",
    "stammdaten/individuelle-artikelnummer": "/stammdaten/individuelle-artikelnummern",
    "verkauf/kunde": "/verkauf/kunde",
    "crm/lieferant": "/crm/lieferanten",
    "futter/einzel": "/futter/einzel",
    "futter/misch": "/futter/misch",
    **BATCH13_ROUTEN,
}

STAMM_SYNONYME = {
    "artikel/stamm": ['artikel', 'artikelstamm', 'stammartikel'],
    "lager/charge": ['charge', 'chargenstamm'],
    "personal/mitarbeiter": ['mitarbeiter', 'personalstamm'],
    "agrar/psm": ['psm', 'pflanzenschutzmittel'],
    "crm/aktivitaet": ['aktivitaet', 'crm-aktivitaet'],
    "crm/kontakt": ['kontakt', 'ansprechpartner'],
    "crm/betriebsprofil": ['betriebsprofil', 'betriebsprofil'],
    "crm/campaign": ['kampagne', 'marketingkampagne'],
    "crm/campaign-template": ['kampagnenvorlage', 'vorlage'],
    "crm/consent": ['einwilligung', 'dsgvo-einwilligung'],
    "crm/gdpr-request": ['dsgvo-anfrage', 'betroffenenanfrage'],
    "crm/segment": ['segment', 'marketingsegment'],
    "finance/bank-account": ['bankkonto', 'bankverbindung'],
    "qualitaet/labor-auftrag": ['laborauftrag', 'labor'],
    "service/anfrage": ['serviceanfrage', 'service'],
    "waage/wiegeschein": ['wiegeschein', 'waage'],
    "fibu/abschluss-checklist": ['abschluss-checkliste', 'fibu-abschluss'],
    "agrar/kontrakt-detail": ['kontrakt', 'kontraktdetail'],
    "silo/silo": ['silo', 'silostamm'],
    "crm/vertreter": ['vertreter', 'vertreterstamm'],
    "stammdaten/hausbank": ['hausbank', 'hausbank'],
    "stammdaten/mengeneinheit": ['mengeneinheit', 'me-stamm'],
    "portal/zertifikat": ['zertifikat', 'portal-zertifikat'],
    "produktion/rezepturgruppe": ['rezepturgruppe', 'produktion'],
    "rezepte/rezept": ['rezept', 'rezeptur'],
    "fibu/anlage": ['anlage', 'anlagevermoegen'],
    "stammdaten/individuelle-artikelnummer": ['individuelle artikelnummer', 'artikelnummer'],
    "verkauf/kunde": ['kunde', 'verkaufskundenstamm'],
    "crm/lieferant": ['lieferant', 'crm-lieferantenstamm'],
    "futter/einzel": ['einzelfuttermittel', 'futter'],
    "futter/misch": ['mischfuttermittel', 'futter'],
    **BATCH13_SYNONYME,
}

patch_get_screen_definition_for_stamm()
from app.core.stamm_object_page_parent import ensure_stamm_screen_registry

ensure_stamm_screen_registry()
