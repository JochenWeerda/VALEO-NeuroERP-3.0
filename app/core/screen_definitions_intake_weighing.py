"""Declarative contracts for existing intake/weighing domain primitives.

The specialist owns wizard/scan/ticket state; Meridian still compiles its fields,
permissions, actions and shell. No legacy page is embedded by these definitions.
"""
from typing import Any


def _field(key: str, label: str, kind: str = "text", *, required: bool = False, read_only: bool = False) -> dict[str, Any]:
    return {"key": key, "label": label, "type": kind, "required": required, "readOnly": read_only}


def _action(key: str, label: str, endpoint: str | None = None, method: str = "POST", primary: bool = False) -> dict[str, Any]:
    action: dict[str, Any] = {"key": key, "label": label, "kind": "primary" if primary else "secondary", "dangerLevel": "safe", "forbiddenForAgents": True}
    if endpoint:
        action.update(permission=f"studio.{key}.intake-weighing", inputFlow={"kind": "humanForm", "submitEndpoint": endpoint, "method": method})
    else:
        action["localEffect"] = "view"
    return action


def _screen(screen_id: str, title: str, fields: list[dict[str, Any]], actions: list[dict[str, Any]], sources: list[tuple[str, str]]) -> dict[str, Any]:
    intake = screen_id.startswith("annahme/")
    # Registration/quality are guided forms, creation is a single-step form.
    # Tickets are a multi-object operator workspace, never a fetched object page.
    wizard = screen_id.endswith(("lkw-registrierung", "qualitaets-check", "/neu"))
    for action in actions:
        if action["key"] in {"upload", "start", "quality", "repair", "clarify", "harvest", "calibrate", "close", "import", "retryImport", "dismissImport"}:
            action["surfaceOnly"] = True
    return {
        "schemaVersion": 1, "id": screen_id, "domain": "agrar", "mode": "wizard" if wizard else "cockpit",
        "title": title, "subtitle": "Annahme, Qualität und Wiegen" if intake else "Waagen und Wiegescheine",
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "layout": {"floorplan": "wizard" if wizard else "cockpit", "density": "expertDense", "contextRail": "combined", "tableProfile": "inventory"},
        "fields": fields, "actions": actions,
        "dataSources": [{"key": key, "endpoint": endpoint, "staleTimeMs": 15000} for key, endpoint in sources],
        "specialized": {"type": "intake" if intake else "weighing", "id": screen_id},
        "workflow": {"processKey": "harvest-to-settlement", "status": "operator-workspace", "auditRequired": True},
        "performance": {"initialPayloadBudgetKb": 100, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "agrar"},
        "agentContract": {"businessPurpose": title + " über die vorhandenen Fachverträge bearbeiten.", "examplePrompts": ["Welche Eingaben und Aktionen sind verfügbar?"], "sensitiveFields": [field["key"] for field in fields], "forbiddenAgentTasks": ["Fachaktionen dieser Bedienoberfläche ausführen"], "testSelectors": {"screenRoot": f"[data-testid='native-cockpit-{screen_id.replace('/', '-')}']"}},
    }


def build_intake_registration() -> dict[str, Any]:
    fields = [_field("kennzeichen", "Kennzeichen", required=True), _field("lieferant", "Lieferant", required=True), _field("lieferscheinNr", "Lieferschein-Nr."), _field("articleId", "Artikel", required=True), _field("artikel", "Artikelbezeichnung"), _field("ankunftszeit", "Ankunftszeit", "datetime"), _field("prioritaet", "Priorität"), _field("attachmentIds", "Bildanhänge", "stringList")]
    return _screen("annahme/lkw-registrierung", "LKW-Registrierung", fields, [_action("register", "LKW registrieren", "/api/v1/annahme/lkw-registrierung", primary=True), _action("upload", "Bild hochladen", "/api/v1/annahme/upload"), _action("cancel", "Zur Warteschlange")], [("articles", "/api/v1/articles?limit=100")])


def build_intake_quality() -> dict[str, Any]:
    fields = [_field("lieferscheinNr", "Lieferschein-Nr.", read_only=True), _field("artikel", "Artikel", read_only=True), _field("feuchtigkeit", "Feuchtigkeit %", "number"), _field("protein", "Protein %", "number"), _field("verunreinigung", "Verunreinigung %", "number"), _field("fremdgeruch", "Fremdgeruch"), _field("schaedlinge", "Schädlinge / Schimmel"), _field("farbe", "Farbe"), _field("bemerkungen", "Bemerkungen", "textarea"), _field("ergebnis", "Ergebnis", read_only=True)]
    return _screen("annahme/qualitaets-check", "Qualitätsprüfung", fields, [_action("save", "Qualitätsprüfung speichern", "/api/v1/agrar/quality-protocols", primary=True), _action("start", "Prüfung beginnen", "/api/v1/annahme/warteschlange/{entity_id}", "PATCH"), _action("billing", "Zur Abrechnung"), _action("cancel", "Zur Warteschlange")], [("queue", "/api/v1/annahme/warteschlange")])


def build_intake_queue() -> dict[str, Any]:
    fields = [_field(key, label, read_only=True) for key, label in [("kennzeichen", "Kennzeichen"), ("lieferant", "Lieferant"), ("artikel", "Artikel"), ("status", "Status"), ("ankunft", "Ankunft"), ("wartezeit", "Wartezeit"), ("lieferschein_nr", "Lieferschein-Nr.")]]
    return _screen("annahme/warteschlange", "Annahme-Warteschlange", fields, [_action("new", "LKW anmelden", primary=True), _action("qr", "QR-Code (Handy)"), _action("refresh", "Aktualisieren"), _action("quality", "Qualitätsprüfung öffnen"), _action("repair", "Artikel reparieren", "/api/v1/annahme/warteschlange/{entity_id}/repair-article"), _action("clarify", "Klärung starten"), _action("harvest", "Ernte-Annahme öffnen")], [("queue", "/api/v1/annahme/warteschlange"), ("charges", "/api/v1/chargen"), ("freight", "/api/v1/logistik/frachtbriefe")])


def build_scale_list(screen_id: str = "waage/liste") -> dict[str, Any]:
    fields = [_field(key, label, read_only=True) for key, label in [("id", "ID"), ("standort", "Standort"), ("typ", "Typ"), ("maxKapazitaet", "Max. Kapazität (t)"), ("letzteEichung", "Letzte Eichung"), ("naechsteEichung", "Nächste Eichung"), ("status", "Status")]]
    fields += [_field("letztes_eichdatum", "Letztes Eichdatum", "date"), _field("naechste_eichfaelligkeit", "Nächste Eichfälligkeit", "date"), _field("eichamt", "Eichamt"), _field("zertifikat_nr", "Zertifikat-Nr.")]
    fields += [_field("importScaleId", "Importwaage", required=True), _field("importFile", "ASCII-Datei", "file", required=True), _field("fehlerToleranz", "Gültige Zeilen übernehmen und Fehler protokollieren", "boolean")]
    fields += [_field(key, label, read_only=True) for key, label in [("importRaw", "Rohdaten"), ("importError", "Importfehler"), ("importRetryCount", "Versuche")]]
    return _screen(screen_id, "Waagen", fields, [_action("new", "Neue Waage", primary=True), _action("yard", "Hofliste"), _action("export", "Export"), _action("refresh", "Aktualisieren"), _action("calibrate", "Eichdaten speichern", "/api/v1/waage/waagen/{entity_id}/kalibrierung", "PATCH"), _action("import", "Datei importieren", "/api/v1/waage/waagen/import/ascii"), _action("retryImport", "Erneut prüfen", "/api/v1/waage/waagen/import/fehlerqueue/{entity_id}/retry"), {**_action("dismissImport", "Verwerfen", "/api/v1/waage/waagen/import/fehlerqueue/{entity_id}", "DELETE"), "requiresConfirmation": True, "dangerLevel": "moderate"}], [("scales", "/api/v1/waage/waagen?limit=1000"), ("importQueue", "/api/v1/waage/waagen/import/fehlerqueue?limit=100"), ("charges", "/api/v1/chargen"), ("freight", "/api/v1/logistik/frachtbriefe")])


def build_scale_create() -> dict[str, Any]:
    return _screen("waage/neu", "Waage anlegen", [_field("standort", "Standort", required=True), _field("typ", "Waagentyp", required=True), _field("max_kapazitaet", "Kapazität in Tonnen", "number", required=True)], [_action("create", "Waage anlegen", "/api/v1/waage/waagen", primary=True)], [("scales", "/api/v1/waage/waagen")])


def build_weighing_tickets(screen_id: str = "waage/wiegungen") -> dict[str, Any]:
    fields = [_field(key, label, kind, required=key == "ticketNumber") for key, label, kind in [("ticketNumber", "Ticketnummer", "text"), ("scaleId", "Waage", "text"), ("vehiclePlate", "Kennzeichen", "text"), ("grossWeight", "Brutto", "number"), ("tareWeight", "Tara", "number"), ("moisturePct", "Feuchte %", "number"), ("impuritiesPct", "Besatz %", "number"), ("selectedTicketId", "Ticket", "text"), ("selectedContractId", "Offener Kontrakt", "text")]]
    return _screen(screen_id, "Wiegungen", fields, [_action("create", "Wiegeschein anlegen", "/api/v1/weighing-tickets", primary=True), _action("close", "Ticket schließen", "/api/v1/weighing-tickets/{entity_id}", "PUT"), _action("allocate", "Kontrakt zuordnen", "/api/v1/weighing-tickets/{entity_id}/allocate-contract"), _action("refresh", "Aktualisieren")], [("tickets", "/api/v1/weighing-tickets?limit=100"), ("contracts", "/api/v1/agrar/contracts?status=open&limit=100"), ("charges", "/api/v1/chargen"), ("freight", "/api/v1/logistik/frachtbriefe")])
