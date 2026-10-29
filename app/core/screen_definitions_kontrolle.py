"""Kontroll-/Freigabe-/Pruef-Worklists (KontrollWorklistParent, Taxonomie §2.4)."""
from __future__ import annotations

from typing import Any

from app.core.kontroll_worklist_legacy_payloads import KONTROLL_WORKLIST_LEGACY_PAYLOADS
from app.core.screen_definitions_kontrolle_batch12 import BATCH12_BUILDERS, BATCH12_KONTROLL_TEST_IDS
from app.core.kontroll_worklist_parent import (
    build_document_control_variant,
    build_document_control_worklist,
    build_kontroll_worklist_screen,
    build_queue_kontroll_screen,
    build_sanctions_kontroll_worklist,
    kontroll_entity_and_queue_sources,
    kontroll_from_legacy_definition,
    kontroll_queue_table,
)

SCREEN_ID = "finance/pruefkorb"


def build_pruefkorb_screen_definition() -> dict[str, Any]:
    """Native Arbeitsliste des Controllers ueber die Befunde der Kontroll-Engine."""
    nur_offen = {"field": "status", "values": ["offen"]}
    return build_kontroll_worklist_screen(
        screen_id=SCREEN_ID,
        domain="finance",
        title="Prüfkorb",
        subtitle="Auffälligkeiten an gebuchten Vorgängen: Warnungen und freigegebene kritische Befunde",
        data_sources=kontroll_entity_and_queue_sources(
            summary_endpoint="/api/v1/kontrolle/lagebild",
            queue_endpoint="/api/v1/kontrolle/pruefkorb",
            queue_key="befunde",
        ),
        summary=[
            {"key": "offen", "label": "Offen", "tone": "warning"},
            {"key": "kritisch_offen", "label": "Kritisch, noch nicht bewertet", "tone": "danger"},
            {"key": "warnung_offen", "label": "Warnungen", "tone": "warning"},
            {"key": "wartend", "label": "Älter als 7 Tage", "tone": "danger"},
            {"key": "geprueft_30_tage", "label": "Geprüft in 30 Tagen", "tone": "info"},
            {"key": "lage", "label": "Lage", "tone": "info"},
        ],
        tables=[
            kontroll_queue_table(
                table_key="befunde",
                label="Befunde",
                columns=[
                    {"key": "erfasst", "label": "Erfasst", "renderKind": "datetime", "sortable": True, "width": 150},
                    {"key": "schwere", "label": "Schwere", "renderKind": "status", "sortable": True, "filterable": True, "width": 110},
                    {"key": "art", "label": "Art", "sortable": True, "filterable": True, "width": 220},
                    {"key": "vorgang", "label": "Vorgang", "width": 170},
                    {"key": "aktion", "label": "Aktion", "width": 100},
                    {"key": "beleg", "label": "Beleg", "width": 140},
                    {"key": "betrag", "label": "Betrag", "renderKind": "currency", "sortable": True, "width": 120},
                    {"key": "hinweis", "label": "Hinweis", "width": 320},
                    {"key": "ausgeloest_von", "label": "Ausgelöst von", "sortable": True, "filterable": True, "width": 140},
                    {"key": "status", "label": "Stand", "renderKind": "status", "sortable": True, "filterable": True, "width": 110},
                    {"key": "geprueft_von", "label": "Geprüft von", "width": 140},
                    {"key": "bewertung", "label": "Bewertung", "width": 260},
                ],
                row_actions=[
                    {"key": "pruefen", "label": "Bewerten", "visibleWhen": nur_offen},
                    {"key": "open_source", "label": "Zum Beleg"},
                ],
            ),
        ],
        no_workflow_reason=(
            "Ein Befund hat nur zwei Stände (offen, geprüft); die Bewertung wird am Befund festgehalten."
        ),
        table_profile="financial",
        bundle_group="finance",
        business_purpose="Auffälligkeiten an Buchungen, Stornos und Importen für den Controller priorisieren.",
        example_prompts=[
            "Welche Befunde sind im Prüfkorb offen?",
            "Zeige die kritischen Befunde.",
            "Welche Auffälligkeiten warten seit mehr als einer Woche?",
        ],
        sensitive_fields=["ausgeloest_von", "geprueft_von", "bewertung", "betrag"],
        forbidden_agent_tasks=["Befunde bewerten oder als geprüft kennzeichnen"],
        test_id="finanz-pruefkorb",
    )


def _lift_legacy_kontroll_worklist(screen_id: str):
    def _build() -> dict[str, Any]:
        return kontroll_from_legacy_definition(KONTROLL_WORKLIST_LEGACY_PAYLOADS[screen_id])

    return _build


def build_beleg_kontrolle_screen_definition() -> dict[str, Any]:
    return build_document_control_worklist(
        screen_id="auswertungen/beleg-kontrolle",
        title="Beleg-Kontrolle",
        subtitle="Unerledigte Bestellungen, fehlende Eingangsbelege und Lieferschein-Ausnahmen",
    )


def build_sanktionspruefung_personal_screen_definition() -> dict[str, Any]:
    return build_sanctions_kontroll_worklist(
        screen_id="auswertungen/sanktionspruefung-personal",
        title="Terrorschutzpruefung Personal",
        scope="personal",
        subject_label="Personal",
    )


def build_sanktionspruefung_kunden_screen_definition() -> dict[str, Any]:
    return build_sanctions_kontroll_worklist(
        screen_id="auswertungen/sanktionspruefung-kunden",
        title="Terrorschutzpruefung Kunden",
        scope="customers",
        subject_label="Kunden",
    )


def _std_cols(*keys: tuple[str, str, int]) -> list[dict[str, Any]]:
    return [
        {"key": key, "label": label, "sortable": True, "filterable": True, "width": width}
        for key, label, width in keys
    ]


def _batch8_builders() -> dict[str, Any]:
    """Batch-8: hand_built Kontroll-/Inbox-/Freigabe-Worklists (OpenAPI-validierte GETs)."""
    specs: list[dict[str, Any]] = [
        {
            "screen_id": "dms/inbox",
            "domain": "dms-compliance",
            "title": "DMS-Eingangskorb",
            "subtitle": "OCR-Dokumente pruefen, Belege anlegen oder verwerfen",
            "queue_endpoint": "/api/v1/dms/inbox",
            "columns": _std_cols(
                ("id", "ID", 120),
                ("status", "Status", 110),
                ("confidence", "Konfidenz", 100),
                ("file_name", "Datei", 200),
                ("created_at", "Eingang", 150),
            ),
            "row_actions": [
                {"key": "create_beleg", "label": "Belegmaske öffnen", "permission": "dms.inbox.read", "commandEndpoint": "/api/mcp/documents/inbox/{entity_id}/prepare", "method": "POST"},
                {"key": "discard", "label": "Verwerfen", "dangerLevel": "moderate", "permission": "dms.inbox.write", "commandEndpoint": "/api/v1/dms/inbox/{entity_id}", "method": "DELETE"},
            ],
            "business_purpose": "Eingescannte Belege priorisieren und in den Belegfluss ueberfuehren.",
            "example_prompts": ["Welche Inbox-Dokumente haben niedrige OCR-Konfidenz?"],
        },
        {
            "screen_id": "crm/bestell-inbox",
            "domain": "crm",
            "title": "Bestell-Inbox",
            "subtitle": "WhatsApp- und Freitext-Bestellungen parsen, bestaetigen oder verwerfen",
            "queue_endpoint": "/api/v1/crm/bestell-inbox",
            "columns": _std_cols(
                ("eingegangen_am", "Eingang", 150),
                ("status", "Status", 110),
                ("absender", "Absender", 140),
                ("kunden_nr", "Kunde", 110),
                ("beleg_typ", "Belegtyp", 110),
            ),
            "row_actions": [
                {"key": "bestaetigen", "label": "Bestaetigen", "permission": "crm.bestell_inbox.write"},
                {"key": "verwerfen", "label": "Verwerfen", "dangerLevel": "moderate", "permission": "crm.bestell_inbox.write"},
            ],
            "business_purpose": "Medienbruch zwischen Messenger und ERP reduzieren.",
            "example_prompts": ["Welche Bestellungen warten auf Bestaetigung?"],
        },
        {
            "screen_id": "crm/klaerfall-inbox",
            "domain": "crm",
            "title": "Klaerfall-Inbox",
            "subtitle": "Auto-Capture-Kontakte ohne Kundenmatch zuordnen oder verwerfen",
            "queue_endpoint": "/api/v1/crm/kim/capture-inbox",
            "columns": _std_cols(
                ("created_at", "Eingang", 150),
                ("channel", "Kanal", 100),
                ("peer", "Peer", 140),
                ("betreff", "Betreff", 200),
                ("status", "Status", 110),
            ),
            "row_actions": [
                {"key": "assign", "label": "Zuordnen", "permission": "crm.capture_inbox.write"},
                {"key": "dismiss", "label": "Verwerfen", "dangerLevel": "moderate", "permission": "crm.capture_inbox.write"},
            ],
            "business_purpose": "KIM-Erfassungen ohne Kundenmatch sichtbar machen.",
            "example_prompts": ["Welche Klaerfaelle sind offen?"],
        },
        {
            "screen_id": "admin/ai-approvals",
            "domain": "admin",
            "title": "AI-Freigaben",
            "subtitle": "AP-Rechnungen im Status ZUR_FREIGABE (Human-in-the-loop)",
            "queue_endpoint": "/api/v1/finance/ap/invoices/?status=ZUR_FREIGABE",
            "table_profile": "financial",
            "columns": _std_cols(
                ("number", "Rechnung", 140),
                ("amount", "Betrag", 120),
                ("status", "Status", 120),
                ("created_at", "Eingang", 150),
            ),
            "row_actions": [{"key": "open_source", "label": "Zur Rechnung"}],
            "business_purpose": "AI-/Agent-Vorschlaege fuer Einkaufsrechnungen freigeben.",
            "example_prompts": ["Welche Rechnungen warten auf Freigabe?"],
        },
        {
            "screen_id": "qualitaet/ausnahmen",
            "domain": "operations",
            "title": "Betriebs-Ausnahmen",
            "subtitle": "Offene Abweichungen und Eskalationen priorisieren",
            "queue_endpoint": "/api/v1/operations/exceptions",
            "columns": _std_cols(
                ("erstellt_am", "Erfasst", 150),
                ("typ", "Typ", 140),
                ("domäne", "Domäne", 120),
                ("priorität", "Prioritaet", 110),
                ("status", "Status", 110),
            ),
            "business_purpose": "QS- und Leitungs-Ausnahmen mandantensicher bearbeiten.",
            "example_prompts": ["Welche Ausnahmen sind eskaliert?"],
        },
        {
            "screen_id": "finance/audit-trail",
            "domain": "finance",
            "title": "Finanz-Audit-Trail",
            "subtitle": "Aenderungen und Zugriffe im Finanzkontext nachvollziehen",
            "summary_endpoint": "/api/v1/audit/stats",
            "queue_endpoint": "/api/v1/audit/logs",
            "queue_key": "logs",
            "summary": [
                {"key": "total", "label": "Eintraege", "tone": "info"},
                {"key": "last_24h", "label": "24h", "tone": "warning"},
            ],
            "table_profile": "financial",
            "columns": _std_cols(
                ("timestamp", "Zeit", 170),
                ("action", "Aktion", 140),
                ("user_id", "Benutzer", 130),
                ("resource", "Ressource", 180),
            ),
            "business_purpose": "Revisionssichere Finanz-Audit-Eintraege durchsuchen.",
            "example_prompts": ["Zeige kritische Audit-Eintraege der letzten Woche."],
        },
        {
            "screen_id": "compliance/sanktionspruefung",
            "domain": "compliance",
            "title": "Sanktionspruefung",
            "subtitle": "Treffer und Pruefprotokoll der Compliance-Sanktionslisten",
            "queue_endpoint": "/api/v1/compliance/sanctions/eintraege",
            "queue_key": "eintraege",
            "table_profile": "audit",
            "columns": _std_cols(
                ("geprueft_am", "Geprueft", 150),
                ("name", "Name", 200),
                ("status", "Ergebnis", 120),
                ("entity_ref", "Referenz", 130),
            ),
            "business_purpose": "Sanktionstreffer getrennt vom Auswertungs-Cockpit nachverfolgen.",
            "example_prompts": ["Welche Sanktionstreffer sind offen?"],
        },
        {
            "screen_id": "compliance/pcn-ufi",
            "domain": "compliance",
            "title": "PCN / UFI-Meldungen",
            "subtitle": "PCN-Meldungen und UFI-Referenzen in der Compliance-Queue",
            "queue_endpoint": "/api/v1/compliance/pcn-meldungen",
            "columns": _std_cols(
                ("meldung_id", "Meldung", 140),
                ("status", "Status", 110),
                ("artikel", "Artikel", 160),
                ("faellig", "Faellig", 120),
            ),
            "business_purpose": "PCN/UFI-Pflichten ohne Medienbruch nachverfolgen.",
            "example_prompts": ["Welche PCN-Meldungen sind faellig?"],
        },
        {
            "screen_id": "annahme/warteschlange",
            "domain": "agrar",
            "title": "Annahme-Warteschlange",
            "subtitle": "LKW-Warteschlange zur Ernteannahme steuern",
            "queue_endpoint": "/api/v1/annahme/warteschlange",
            "table_profile": "inventory",
            "columns": _std_cols(
                ("kennzeichen", "Kennzeichen", 130),
                ("lieferant", "Lieferant", 160),
                ("artikel", "Artikel", 140),
                ("status", "Status", 110),
            ),
            "row_actions": [{"key": "open_harvest", "label": "Zur Annahme"}],
            "business_purpose": "Warteschlange an der Waage priorisieren.",
            "example_prompts": ["Welche LKW warten laenger als 30 Minuten?"],
        },
        {
            "screen_id": "workflow/workflow-monitoring",
            "domain": "platform",
            "title": "Workflow-Monitoring",
            "subtitle": "Laufende und fehlgeschlagene Prozessinstanzen",
            "summary_endpoint": "/api/v1/workflow/cockpit/summary",
            "queue_endpoint": "/api/v1/workflow/runtime/instances",
            "queue_key": "instances",
            "columns": _std_cols(
                ("started_at", "Gestartet", 170),
                ("process_key", "Prozess", 160),
                ("status", "Status", 110),
                ("trigger_entity", "Ausloeser", 160),
            ),
            "business_purpose": "Workflow-Ausfuehrungen und Fehler transparent machen.",
            "example_prompts": ["Welche Workflows sind fehlgeschlagen?"],
        },
        {
            "screen_id": "docflow/wiedervorlagen",
            "domain": "dms-compliance",
            "title": "Docflow-Wiedervorlagen",
            "subtitle": "Bescheide, Rueckmeldungen und Wiedervorlagen",
            "queue_endpoint": "/api/v1/docflow/evidence/wiedervorlagen",
            "columns": _std_cols(
                ("faellig_am", "Faellig", 150),
                ("art", "Art", 120),
                ("betreff", "Betreff", 220),
                ("status", "Status", 110),
            ),
            "row_actions": [
                {"key": "complete", "label": "Erledigen", "permission": "docflow.followup.write"},
            ],
            "business_purpose": "Follow-ups im Nachweisraum nicht verlieren.",
            "example_prompts": ["Welche Wiedervorlagen sind ueberfaellig?"],
        },
        {
            "screen_id": "docflow/gobd-export",
            "domain": "dms-compliance",
            "title": "GoBD-Export",
            "subtitle": "Vorgaenge fuer revisionssichere Exportpakete auswaehlen",
            "queue_endpoint": "/api/v1/docflow/evidence/documents",
            "queue_key": "documents",
            "columns": _std_cols(
                ("doc_number", "Beleg", 140),
                ("subject_type", "Typ", 110),
                ("status", "Status", 110),
                ("updated_at", "Geaendert", 150),
            ),
            "row_actions": [
                {"key": "export_gobd", "label": "GoBD-Paket", "permission": "docflow.gobd.export"},
            ],
            "business_purpose": "GoBD-Exporte aus dem Nachweisraum anstossen.",
            "example_prompts": ["Welche Vorgaenge haben offene Artefakte?"],
        },
        {
            "screen_id": "docflow/nachweisraum",
            "domain": "dms-compliance",
            "title": "Nachweisraum",
            "subtitle": "Revisionssichere Beleg- und Artefakt-Uebersicht",
            "queue_endpoint": "/api/v1/docflow/evidence/documents",
            "queue_key": "documents",
            "context_rail": "combined",
            "columns": _std_cols(
                ("doc_number", "Beleg", 140),
                ("subject_type", "Bezug", 110),
                ("partner_name", "Partner", 180),
                ("status", "Status", 110),
            ),
            "row_actions": [{"key": "open_detail", "label": "Nachweis oeffnen"}],
            "business_purpose": "Nachweisraum-Worklist fuer Audit und GoBD.",
            "example_prompts": ["Zeige Vorgaenge ohne freigegebene Artefakte."],
        },
        {
            "screen_id": "docflow/artefakt-freigabe",
            "domain": "dms-compliance",
            "title": "Artefakt-Freigabe",
            "subtitle": "Artefakte hochladen, freigeben und archivieren",
            "queue_endpoint": "/api/v1/docflow/evidence/artifacts",
            "queue_key": "artifacts",
            "columns": _std_cols(
                ("file_name", "Datei", 200),
                ("version", "Version", 80),
                ("freigabe_status", "Freigabe", 120),
                ("sha256", "Hash", 180),
            ),
            "row_actions": [
                {"key": "freigeben", "label": "Freigeben", "permission": "docflow.artifact.write"},
                {"key": "archivieren", "label": "Archivieren", "permission": "docflow.artifact.write"},
            ],
            "business_purpose": "Artefakt-Lebenszyklus entwurf→freigegeben→archiviert steuern.",
            "example_prompts": ["Welche Artefakte warten auf Freigabe?"],
        },
        {
            "screen_id": "compliance/meldewesen-konsole",
            "domain": "compliance",
            "title": "Meldewesen-Konsole",
            "subtitle": "Jobs, Connectoren und Meldelaeufe ueberwachen",
            "summary_endpoint": "/api/v1/config/connectors",
            "queue_endpoint": "/api/v1/jobs",
            "queue_key": "jobs",
            "columns": _std_cols(
                ("name", "Job", 180),
                ("status", "Status", 110),
                ("last_run_at", "Letzter Lauf", 170),
                ("next_run_at", "Naechster Lauf", 170),
            ),
            "business_purpose": "Meldewesen-Jobs und Konnektoren im Blick behalten.",
            "example_prompts": ["Welche Melde-Jobs sind fehlgeschlagen?"],
        },
        {
            "screen_id": "annahme/qualitaets-check",
            "domain": "agrar",
            "title": "Qualitaets-Check",
            "subtitle": "Qualitaetsprotokolle zur Ernteannahme pruefen",
            "queue_endpoint": "/api/v1/agrar/quality-protocols",
            "queue_key": "protocols",
            "columns": _std_cols(
                ("created_at", "Erfasst", 150),
                ("harvest_acceptance_id", "Annahme", 140),
                ("protocol_number", "Protokoll", 130),
                ("is_final", "Finalisiert", 110),
                ("moisture_pct", "Feuchte %", 90),
            ),
            "business_purpose": "Qualitaetsprotokolle vor Freigabe sichten.",
            "example_prompts": ["Welche Protokolle sind noch offen?"],
        },
        {
            "screen_id": "sales/kreditlimit-pruefung",
            "domain": "sales",
            "title": "Kreditlimit-Pruefung",
            "subtitle": "Kunden-Ampel und Auftrags-Kreditwirkung",
            "queue_endpoint": "/api/v1/sales/credit-check/customers",
            "table_profile": "financial",
            "columns": _std_cols(
                ("kunde", "Kunde", 200),
                ("ampel", "Ampel", 100),
                ("limit", "Limit", 110),
                ("exposure", "Exposure", 110),
            ),
            "business_purpose": "Kreditrisiko vor Auftragsfreigabe bewerten.",
            "example_prompts": ["Welche Kunden sind blockiert?"],
        },
        {
            "screen_id": "futtermittel/futtermittel-qualitaetskontrolle",
            "domain": "futtermittel",
            "title": "Futtermittel-Qualitaetskontrolle",
            "subtitle": "QS-Pruefungen und Freigaben fuer Futtermittelchargen",
            "queue_endpoint": "/api/v1/futter/qualitaetskontrolle",
            "columns": _std_cols(
                ("title", "Pruefung", 220),
                ("status", "Status", 110),
                ("priority", "Prioritaet", 110),
                ("dueDate", "Faellig", 120),
            ),
            "business_purpose": "Futtermittel-QS-Worklist zentral bearbeiten.",
            "example_prompts": ["Welche QS-Pruefungen sind ueberfaellig?"],
        },
        {
            "screen_id": "process/approval-density",
            "domain": "platform",
            "title": "Freigabe-Dichte",
            "subtitle": "Pending Approvals und Engpaesse im Freigabeprozess",
            "queue_endpoint": "/api/v1/process/approval-density/overview",
            "queue_key": "overview",
            "columns": _std_cols(
                ("process_key", "Prozess", 160),
                ("pending", "Offen", 90),
                ("avg_hours", "Ø Stunden", 110),
                ("bottleneck", "Engpass", 140),
            ),
            "business_purpose": "Freigabe-Engpaesse fuer Leitung sichtbar machen.",
            "example_prompts": ["Wo staut sich die Freigabe?"],
        },
        {
            "screen_id": "process/background-jobs",
            "domain": "platform",
            "title": "Hintergrund-Jobs",
            "subtitle": "Asynchrone Job-Queue und Fehlversuche",
            "queue_endpoint": "/api/v1/process/background-jobs/queue",
            "queue_key": "queue",
            "columns": _std_cols(
                ("job_type", "Typ", 160),
                ("status", "Status", 110),
                ("created_at", "Eingestellt", 170),
                ("attempts", "Versuche", 90),
            ),
            "business_purpose": "Hintergrundverarbeitung ueberwachen und nachsteuern.",
            "example_prompts": ["Welche Jobs sind in der Queue fehlgeschlagen?"],
        },
        {
            "screen_id": "strecke/nawaro-vertraege-pruefen",
            "domain": "agrar",
            "title": "NaWaRo-Vertraege pruefen",
            "subtitle": "Contract-Sheets auf Vollstaendigkeit pruefen",
            "queue_endpoint": "/api/v1/agrar/nawaro/contract-sheets",
            "queue_key": "sheets",
            "columns": _std_cols(
                ("id", "Sheet", 140),
                ("harvest_year", "Erntejahr", 100),
                ("status", "Status", 110),
                ("row_count", "Positionen", 100),
            ),
            "business_purpose": "NaWaRo-Vertragssheets vor Druck validieren.",
            "example_prompts": ["Welche Sheets haben fehlende Vertragsnummern?"],
        },
        {
            "screen_id": "compliance/export-pruefprotokoll",
            "domain": "compliance",
            "title": "Export-Pruefprotokoll",
            "subtitle": "Gefahrstoff-Exportzeilen und Chargen-Trace pruefen",
            "queue_endpoint": "/api/v1/compliance/exports/gefahrstoffdoku",
            "queue_key": "rows",
            "columns": _std_cols(
                ("deliveryNumber", "Lieferschein", 140),
                ("article", "Artikel", 160),
                ("compliant", "Konform", 100),
                ("sachkundeStatus", "Sachkunde", 120),
            ),
            "business_purpose": "Compliance-Exporte vor Abgabe stichprobenartig pruefen.",
            "example_prompts": ["Welche Lieferungen sind nicht compliant?"],
        },
        {
            "screen_id": "lager/foreign-goods-queue",
            "domain": "inventory",
            "title": "Fremdware-Queue",
            "subtitle": "Fremdware-Vorgaenge abschliessen und umlagern",
            "summary_endpoint": "/api/v1/foreign-goods/summary",
            "queue_endpoint": "/api/v1/foreign-goods",
            "queue_key": "foreign_goods",
            "table_profile": "inventory",
            "columns": _std_cols(
                ("reference", "Referenz", 140),
                ("partner_name", "Partner", 180),
                ("status", "Status", 110),
                ("quantity", "Menge", 100),
            ),
            "row_actions": [
                {"key": "complete", "label": "Abschliessen", "permission": "inventory.foreign_goods.write"},
                {"key": "transfer", "label": "Umlagern", "permission": "inventory.foreign_goods.write"},
            ],
            "business_purpose": "Fremdware-Worklist parallel zur Detailmaske bedienen.",
            "example_prompts": ["Welche Fremdware-Vorgaenge sind offen?"],
        },
        {
            "screen_id": "inbox",
            "domain": "dms-compliance",
            "title": "Posteingang",
            "subtitle": "Alias-Route fuer den DMS-Eingangskorb",
            "queue_endpoint": "/api/v1/dms/inbox",
            "columns": _std_cols(
                ("id", "ID", 120),
                ("status", "Status", 110),
                ("confidence", "Konfidenz", 100),
                ("file_name", "Datei", 200),
            ),
            "row_actions": [
                {"key": "create_beleg", "label": "Belegmaske öffnen", "permission": "dms.inbox.read", "commandEndpoint": "/api/mcp/documents/inbox/{entity_id}/prepare", "method": "POST"},
                {"key": "discard", "label": "Verwerfen", "dangerLevel": "moderate", "permission": "dms.inbox.write", "commandEndpoint": "/api/v1/dms/inbox/{entity_id}", "method": "DELETE"},
            ],
            "business_purpose": "Kurzroute /inbox auf dieselbe DMS-Inbox-Queue.",
            "example_prompts": ["Was liegt im Posteingang?"],
        },
    ]
    builders: dict[str, Any] = {}
    for spec in specs:
        sid = spec["screen_id"]

        def _make(s: dict[str, Any] = spec, screen_id: str = sid) -> dict[str, Any]:
            return build_queue_kontroll_screen(
                screen_id=screen_id,
                domain=s["domain"],
                title=s["title"],
                subtitle=s["subtitle"],
                queue_endpoint=s["queue_endpoint"],
                columns=s["columns"],
                queue_key=s.get("queue_key", "items"),
                summary_endpoint=s.get("summary_endpoint"),
                summary=s.get("summary"),
                row_actions=s.get("row_actions"),
                table_profile=s.get("table_profile", "standard"),
                context_rail=s.get("context_rail", "audit"),
                business_purpose=s["business_purpose"],
                example_prompts=s["example_prompts"],
            )

        builders[sid] = _make
    return builders


BATCH8_KONTROLL_BUILDERS = _batch8_builders()
BATCH8_KONTROLL_SCREEN_IDS: tuple[str, ...] = tuple(sorted(BATCH8_KONTROLL_BUILDERS))


KONTROLLE_SCREEN_BUILDERS: dict[str, Any] = {
    SCREEN_ID: build_pruefkorb_screen_definition,
    "auswertungen/beleg-kontrolle": build_beleg_kontrolle_screen_definition,
    "auswertungen/auftrags-kontrolle": lambda: build_document_control_variant(
        screen_id="auswertungen/auftrags-kontrolle",
        title="Auftrags-Kontrolle",
        subtitle="Unerledigte Bestellungen priorisieren und bis zum Quellbeleg verfolgen.",
        exception_type="open_purchase_order",
    ),
    "auswertungen/lieferschein-kontrolle": lambda: build_document_control_variant(
        screen_id="auswertungen/lieferschein-kontrolle",
        title="Lieferschein-Kontrolle",
        subtitle="Nicht fakturierte Lieferscheine priorisieren und klaeren.",
        exception_type="uninvoiced_delivery_note",
    ),
    "abrechnung/eb-lieferschein-kontrolle": lambda: build_document_control_variant(
        screen_id="abrechnung/eb-lieferschein-kontrolle",
        title="EB-Lieferschein-Kontrolle",
        subtitle="Fehlende Eingangsbelege und Warenzugaenge kontrollieren.",
        exception_type="missing_inbound_document",
    ),
    "auswertungen/sanktionspruefung-personal": build_sanktionspruefung_personal_screen_definition,
    "auswertungen/sanktionspruefung-kunden": build_sanktionspruefung_kunden_screen_definition,
    **{sid: _lift_legacy_kontroll_worklist(sid) for sid in KONTROLL_WORKLIST_LEGACY_PAYLOADS},
    **BATCH8_KONTROLL_BUILDERS,
    **BATCH12_BUILDERS,
}

KONTROLL_WORKLIST_SCREEN_IDS: tuple[str, ...] = (
    "auswertungen/beleg-kontrolle",
    "auswertungen/auftrags-kontrolle",
    "auswertungen/lieferschein-kontrolle",
    "abrechnung/eb-lieferschein-kontrolle",
    "auswertungen/sanktionspruefung-personal",
    "auswertungen/sanktionspruefung-kunden",
    SCREEN_ID,
    *tuple(sorted(KONTROLL_WORKLIST_LEGACY_PAYLOADS)),
    *BATCH8_KONTROLL_SCREEN_IDS,
    *BATCH12_KONTROLL_TEST_IDS,
)

KONTROLLE_SYNONYME = {
    SCREEN_ID: [
        "prüfkorb",
        "pruefkorb",
        "kontrollbefunde",
        "auffälligkeiten",
        "controller",
        "dubletten",
        "unregelmäßigkeiten",
    ],
}
KONTROLLE_ROUTEN = {
    SCREEN_ID: "/finance/pruefkorb",
    "dms/inbox": "/inbox",
    "inbox": "/inbox",
    "crm/bestell-inbox": "/crm/bestell-inbox",
    "crm/klaerfall-inbox": "/crm/klaerfall-inbox",
    "admin/ai-approvals": "/admin/ai-approvals",
    "qualitaet/ausnahmen": "/qualitaet/ausnahmen",
    "finance/audit-trail": "/finance/audit-trail",
    "compliance/sanktionspruefung": "/compliance/sanktionspruefung",
    "compliance/pcn-ufi": "/compliance/pcn-ufi",
    "annahme/warteschlange": "/annahme/warteschlange",
    "workflow/workflow-monitoring": "/workflow/workflow-monitoring",
    "docflow/wiedervorlagen": "/docflow/wiedervorlagen",
    "docflow/gobd-export": "/docflow/gobd-export",
    "docflow/nachweisraum": "/docflow/nachweisraum",
    "docflow/artefakt-freigabe": "/docflow/artefakt-freigabe",
    "compliance/meldewesen-konsole": "/compliance/meldewesen-konsole",
    "annahme/qualitaets-check": "/annahme/qualitaets-check",
    "sales/kreditlimit-pruefung": "/sales/kreditlimit-pruefung",
    "futtermittel/futtermittel-qualitaetskontrolle": "/futtermittel/futtermittel-qualitaetskontrolle",
    "process/approval-density": "/workflows/approval",
    "process/background-jobs": "/admin/command-monitor",
    "strecke/nawaro-vertraege-pruefen": "/strecke/nawaro-vertraege-pruefen",
    "compliance/export-pruefprotokoll": "/compliance/export-pruefprotokoll",
    "lager/foreign-goods-queue": "/lager/fremdware",
}
