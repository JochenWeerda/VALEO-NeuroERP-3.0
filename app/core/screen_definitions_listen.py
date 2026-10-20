"""Listenmasken als ScreenDefinition (MASK-STUDIO-ROLLOUT-20261020, Welle 1).

Die Listen zu den nativen Objektmasken waren handgebaut oder Altmuster-Konfigurationen. Hier sind sie
ScreenDefinitions: Spalten, Zeilenroute zur nativen Objektmaske und alle Aktionen mit ihrem Kommando-Weg. Die Seite
ist ``NativeListPage`` und enthaelt keinen eigenen Code; Maske, CLI und MCP rufen dieselben Wege.
"""
from __future__ import annotations

from typing import Any


def _liste(*, screen_id: str, domain: str, title: str, subtitle: str, endpoint: str, row_route: str,
           columns: list[dict[str, Any]], actions: list[dict[str, Any]], row_actions: list[dict[str, Any]],
           purpose: str, prompts: list[str], dangerous: list[dict[str, str]] | None = None,
           bundle: str, no_workflow: str, fetch_limit: int = 500) -> dict[str, Any]:
    agent: dict[str, Any] = {
        "businessPurpose": purpose,
        "examplePrompts": prompts,
        "sensitiveFields": [],
        "testSelectors": {"screenRoot": f"[data-testid='screen-{screen_id}']"},
    }
    if dangerous:
        agent["dangerousActions"] = dangerous
    return {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "list",
        "title": title,
        "subtitle": subtitle,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        # Ohne Serverblaetterung laedt die Laufzeit einmal bis pageSize (Grenze des Dienstes beachten).
        "dataSources": [{"key": "list", "endpoint": endpoint, "pageSize": fetch_limit}],
        "actions": actions,
        "tables": [{
            "key": "list", "label": title, "dataSourceKey": "list", "serverPagination": False, "pageSize": 50,
            "virtualized": True, "rowHeight": 40, "rowRouteTemplate": row_route,
            "columns": columns, "rowActions": row_actions,
        }],
        "noWorkflowReason": no_workflow,
        "agentContract": agent,
        "layout": {"floorplan": "worklist", "preferredMode": "desktopDense", "mobileMode": "mobileStack",
                   "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 60, "requiresLazyTabs": False, "requiresVirtualTables": True,
                        "lookupMinChars": 2, "bundleGroup": bundle},
    }


#: CSV-Export der Liste mit ihren Spalten (NativeListPage, ohne Serverwirkung).
_EXPORT = {"key": "export", "label": "CSV-Export", "kind": "secondary", "dangerLevel": "safe", "zone": "header",
           "command": "list.exportCsv", "localEffect": "download", "stubReason": "Exportiert die Liste mit ihren Spalten; keine Serverwirkung."}


def _neu(label: str, route: str) -> dict[str, Any]:
    """Anlage oeffnen; Rechte prueft der Anlageweg der Zielmaske."""
    return {"key": "neu", "label": label, "kind": "primary", "dangerLevel": "safe", "zone": "header",
            "navigationRoute": route, "localEffect": "navigation",
            "stubReason": "Oeffnet die Anlage; Rechte prueft deren Anlageweg."}


def build_einkauf_anfragen_liste() -> dict[str, Any]:
    """Bedarfsanforderungen: senden, in Bestellung ueberfuehren, Entwurf loeschen."""
    return _liste(
        screen_id="einkauf/anfragen", domain="einkauf", title="Anfragen", subtitle="Bedarfsanforderungen an Lieferanten",
        endpoint="/api/v1/einkauf/anfragen", row_route="/einkauf/anfrage/{id}", bundle="einkauf",
        columns=[
            {"key": "anfrageNummer", "label": "Anfrage-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "primary"},
            {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "anforderer", "label": "Anforderer", "filterable": True, "priority": "secondary"},
            {"key": "prioritaet", "label": "Prioritaet", "filterable": True, "priority": "secondary"},
            {"key": "faelligkeit", "label": "Faellig", "renderKind": "date", "sortable": True, "priority": "tertiary"},
            {"key": "createdAt", "label": "Erstellt", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neue Anfrage", "/einkauf/anfrage-erfassung"),
                 _EXPORT],
        row_actions=[
            {"key": "senden", "label": "Senden", "dangerLevel": "moderate", "permission": "einkauf.anfrage.senden",
             "commandEndpoint": "/api/v1/einkauf/anfragen/{entity_id}/actions/senden", "method": "POST",
             "requiresConfirmation": True, "humanApprovalRequired": True, "forbiddenForAgents": True,
             "visibleWhen": {"field": "status", "values": ["ENTWURF", "OFFEN", "FREIGEGEBEN", "offen", "entwurf"]},
             "inputFields": [{"key": "lieferanten", "label": "Lieferanten", "type": "multiselect", "required": True,
                              "optionsSource": {"endpoint": "/api/v1/einkauf/lieferanten", "valueKey": "id",
                                                "labelKey": "firmenname"}}]},
            {"key": "in_bestellung", "label": "In Bestellung", "dangerLevel": "moderate",
             "permission": "einkauf.anfrage.bestellen", "requiresConfirmation": True,
             "commandEndpoint": "/api/v1/einkauf/anfragen/{entity_id}/actions/in_bestellung", "method": "POST",
             "visibleWhen": {"field": "status", "values": ["FREIGEGEBEN", "ANGEBOTSPHASE"]}},
            {"key": "loeschen", "label": "Loeschen", "dangerLevel": "high", "permission": "einkauf.anfrage.loeschen",
             "commandEndpoint": "/api/v1/einkauf/anfragen/{entity_id}/actions/loeschen", "method": "POST",
             "requiresConfirmation": True, "auditReasonRequired": True, "forbiddenForAgents": True,
             "visibleWhen": {"field": "status", "values": ["ENTWURF", "OFFEN", "offen", "entwurf"]}},
        ],
        dangerous=[
            {"key": "senden", "reason": "Versendet E-Mails an Lieferanten im Namen des Hauses; nur Mensch."},
            {"key": "loeschen", "reason": "Entfernt eine Anfrage endgueltig; nur Mensch mit Begruendung."},
        ],
        purpose="Bedarfsanforderungen des Einkaufs finden, an Lieferanten senden und in Bestellungen ueberfuehren.",
        prompts=["Welche Anfragen sind noch im Entwurf?", "Zeige dringende Anfragen."],
        no_workflow="Der Status steht an der Anfrage; die Liste fuehrt keinen eigenen Ablauf.",
    )



def _status(*werte: str) -> dict[str, Any]:
    """Sichtbarkeit nach Status; die Altdaten fuehren Status teils klein geschrieben."""
    return {"field": "status", "values": [*werte, *(w.lower() for w in werte)]}


def build_einkauf_angebote_liste() -> dict[str, Any]:
    """Lieferantenangebote: pruefen, genehmigen, ablehnen, in Bestellung ueberfuehren."""
    pfad = "/api/v1/einkauf/angebote/{entity_id}/actions/"
    return _liste(
        screen_id="einkauf/angebote", domain="einkauf", title="Angebote", subtitle="Lieferantenangebote zu Anfragen",
        endpoint="/api/v1/einkauf/angebote", row_route="/einkauf/angebot/{id}", bundle="einkauf",
        columns=[
            {"key": "angebotNummer", "label": "Angebot-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "sortable": True, "priority": "primary"},
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "secondary"},
            {"key": "preis", "label": "Betrag", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "secondary"},
            {"key": "gueltigBis", "label": "Gueltig bis", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "lieferzeit", "label": "Lieferzeit (Tage)", "numeric": True, "priority": "tertiary"},
            {"key": "createdAt", "label": "Erstellt", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neues Angebot", "/einkauf/angebot"),
                 _EXPORT],
        row_actions=[
            {"key": "pruefen", "label": "Pruefen", "dangerLevel": "safe", "permission": "einkauf.angebot.review",
             "commandEndpoint": pfad + "pruefen", "method": "POST", "requiresConfirmation": True,
             "visibleWhen": _status("ERFASST", "OFFEN", "ENTWURF")},
            {"key": "genehmigen", "label": "Genehmigen", "dangerLevel": "moderate",
             "permission": "einkauf.angebot.approve", "commandEndpoint": pfad + "genehmigen", "method": "POST",
             "requiresConfirmation": True, "humanApprovalRequired": True, "forbiddenForAgents": True,
             "visibleWhen": _status("GEPRUEFT")},
            {"key": "bestellen", "label": "In Bestellung", "dangerLevel": "moderate",
             "permission": "einkauf.angebot.order", "commandEndpoint": pfad + "bestellen", "method": "POST",
             "requiresConfirmation": True, "visibleWhen": _status("GEPRUEFT", "GENEHMIGT")},
            {"key": "ablehnen", "label": "Ablehnen", "dangerLevel": "high", "permission": "einkauf.angebot.reject",
             "commandEndpoint": pfad + "ablehnen", "method": "POST", "requiresConfirmation": True,
             "auditReasonRequired": True, "visibleWhen": _status("ERFASST", "OFFEN", "ENTWURF", "GEPRUEFT", "GENEHMIGT")},
        ],
        dangerous=[{"key": "genehmigen", "reason": "Gibt ein Angebot zur Bestellung frei; nur Mensch."}],
        purpose="Lieferantenangebote vergleichen, pruefen, genehmigen und in Bestellungen ueberfuehren.",
        prompts=["Welche Angebote warten auf Pruefung?", "Welche Angebote laufen diese Woche ab?"],
        no_workflow="Der Status steht am Angebot; die Liste fuehrt keinen eigenen Ablauf.",
    )



def build_einkauf_anlieferavis_liste() -> dict[str, Any]:
    """Lieferavise: senden, bestaetigen, stornieren, Wareneingang buchen."""
    pfad = "/api/v1/einkauf/anlieferavis/{entity_id}/actions/"
    return _liste(
        screen_id="einkauf/anlieferavis-liste", domain="einkauf", title="Anlieferavis",
        subtitle="Lieferavise fuer die Wareneingangsvorbereitung", endpoint="/api/v1/einkauf/anlieferavis",
        row_route="/einkauf/anlieferavis/{id}", bundle="einkauf",
        columns=[
            {"key": "avisNummer", "label": "Avis-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "sortable": True, "priority": "primary"},
            {"key": "bestellung", "label": "Bestellung", "filterable": True, "priority": "secondary"},
            {"key": "geplantesAnlieferDatum", "label": "Geplant", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "createdAt", "label": "Erstellt", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[_EXPORT],
        row_actions=[
            {"key": "senden", "label": "Senden", "dangerLevel": "safe", "permission": "einkauf.avis.senden",
             "commandEndpoint": pfad + "senden", "method": "POST", "requiresConfirmation": True,
             "visibleWhen": _status("OFFEN", "ANGEKUENDIGT")},
            {"key": "bestaetigen", "label": "Bestaetigen", "dangerLevel": "safe",
             "permission": "einkauf.avis.bestaetigen", "commandEndpoint": pfad + "bestaetigen", "method": "POST",
             "requiresConfirmation": True, "visibleWhen": _status("OFFEN", "ANGEKUENDIGT", "GESENDET")},
            {"key": "wareneingang", "label": "Wareneingang buchen", "dangerLevel": "moderate",
             "permission": "lager.wareneingang.create", "commandEndpoint": pfad + "wareneingang", "method": "POST",
             "requiresConfirmation": True, "visibleWhen": _status("BESTAETIGT", "GESENDET", "OFFEN"),
             "inputFields": [
                 {"key": "lieferschein_nr", "label": "Lieferschein-Nr.", "type": "text", "required": True},
                 {"key": "lager_id", "label": "Lager", "type": "select", "required": True,
                  "optionsSource": {"endpoint": "/api/v1/inventory/warehouses/", "valueKey": "id",
                                    "labelKey": "name"}}]},
            {"key": "stornieren", "label": "Stornieren", "dangerLevel": "high",
             "permission": "einkauf.avis.stornieren", "commandEndpoint": pfad + "stornieren", "method": "POST",
             "requiresConfirmation": True, "auditReasonRequired": True,
             "visibleWhen": _status("OFFEN", "ANGEKUENDIGT", "GESENDET", "BESTAETIGT")},
        ],
        purpose="Angekuendigte Lieferungen verfolgen, bestaetigen und als Wareneingang buchen.",
        prompts=["Welche Lieferungen sind fuer diese Woche angekuendigt?", "Welche Avise sind noch offen?"],
        no_workflow="Der Status steht am Avis; die Liste fuehrt keinen eigenen Ablauf.",
    )



def build_einkauf_auftragsbestaetigungen_liste() -> dict[str, Any]:
    """Auftragsbestaetigungen der Lieferanten: erfassen, pruefen, bestaetigen (Wege der Objektmaske)."""
    pfad = "/api/v1/einkauf/auftragsbestaetigungen/{entity_id}/actions/"
    return _liste(
        screen_id="einkauf/auftragsbestaetigungen", domain="einkauf", title="Auftragsbestaetigungen",
        subtitle="Bestaetigungen der Lieferanten zu Bestellungen", endpoint="/api/v1/einkauf/auftragsbestaetigungen",
        row_route="/einkauf/auftragsbestaetigung/{id}", bundle="einkauf",
        columns=[
            {"key": "bestaetigungsNummer", "label": "AB-Nr.", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "bestellung", "label": "Bestellung", "filterable": True, "sortable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "sortable": True, "priority": "secondary"},
            {"key": "createdAt", "label": "Erfasst", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[_neu("AB erfassen", "/einkauf/auftragsbestaetigung/neu"),
                 _EXPORT],
        row_actions=[
            {"key": "pruefen", "label": "Pruefen", "dangerLevel": "safe",
             "permission": "einkauf.auftragsbestaetigung.review", "commandEndpoint": pfad + "pruefen",
             "method": "POST", "requiresConfirmation": True,
             "visibleWhen": _status("OFFEN")},
            {"key": "bestaetigen", "label": "Bestaetigen", "dangerLevel": "moderate",
             "permission": "einkauf.auftragsbestaetigung.confirm", "commandEndpoint": pfad + "bestaetigen",
             "method": "POST", "requiresConfirmation": True,
             "visibleWhen": _status("OFFEN", "GEPRUEFT")},
        ],
        purpose="Lieferanten-Bestaetigungen gegen Bestellungen pruefen und bestaetigen.",
        prompts=["Welche Auftragsbestaetigungen sind noch ungeprueft?", "Zeige Bestaetigungen mit Abweichung."],
        no_workflow="Der Status steht an der Auftragsbestaetigung; die Liste fuehrt keinen eigenen Ablauf.",
    )



def build_einkauf_lieferanten_liste() -> dict[str, Any]:
    """Lieferanten aus derselben Quelle wie die Objektmaske ``einkauf/supplier``."""
    return _liste(
        screen_id="einkauf/lieferanten", domain="einkauf", title="Lieferanten", subtitle="Lieferanten suchen und oeffnen",
        endpoint="/api/v1/einkauf/lieferanten", row_route="/einkauf/lieferanten/{id}", bundle="einkauf",
        columns=[
            {"key": "firmenname", "label": "Lieferant", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "lieferantennummer", "label": "Lieferantennr.", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "ort", "label": "Ort", "filterable": True, "sortable": True, "priority": "secondary"},
            {"key": "telefon", "label": "Telefon", "priority": "tertiary"},
            {"key": "email", "label": "E-Mail", "priority": "tertiary"},
            {"key": "lieferzeit_tage", "label": "Lieferzeit (Tage)", "numeric": True, "priority": "tertiary"},
            {"key": "bewertung", "label": "Bewertung", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "aktiv", "label": "Aktiv", "renderKind": "boolean", "filterable": True, "priority": "secondary"},
        ],
        actions=[_neu("Neuer Lieferant", "/einkauf/lieferant/neu"),
                 _EXPORT],
        row_actions=[],
        purpose="Lieferanten finden und ihre Stammdaten, Bestellungen und Kontakte oeffnen.",
        prompts=["Finde den Lieferanten Muehle Nord.", "Welche Lieferanten sind inaktiv?"],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )



def build_einkauf_bestellungen_liste() -> dict[str, Any]:
    """Bestellungen aus derselben Quelle wie die Objektmaske ``einkauf/purchase-order``."""
    pfad = "/api/v1/einkauf/bestellungen/{entity_id}/actions/"
    return _liste(
        screen_id="einkauf/bestellungen", domain="einkauf", title="Bestellungen", subtitle="Bestellungen an Lieferanten",
        endpoint="/api/v1/einkauf/bestellungen", row_route="/einkauf/bestellung/{id}", bundle="einkauf",
        columns=[
            {"key": "bestellnummer", "label": "Bestellnr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "lieferant_name", "label": "Lieferant", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "bestelldatum", "label": "Bestellt am", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "lieferdatum_wunsch", "label": "Liefertermin", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "netto_summe", "label": "Netto", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "secondary"},
            {"key": "positionen_anz", "label": "Positionen", "numeric": True, "priority": "tertiary"},
            {"key": "versandt_am", "label": "Versandt am", "renderKind": "date", "sortable": True,
             "priority": "tertiary"},
        ],
        actions=[_neu("Neue Bestellung", "/einkauf/bestellungen/neu"), _EXPORT],
        row_actions=[
            {"key": "freigeben", "label": "Freigeben", "dangerLevel": "moderate",
             "permission": "einkauf.bestellung.approve", "commandEndpoint": pfad + "freigeben", "method": "POST",
             "requiresConfirmation": True, "humanApprovalRequired": True, "forbiddenForAgents": True,
             "visibleWhen": _status("ENTWURF", "DRAFT")},
            {"key": "versenden", "label": "Versenden", "dangerLevel": "moderate",
             "permission": "einkauf.bestellung.send", "commandEndpoint": pfad + "versenden", "method": "POST",
             "requiresConfirmation": True, "humanApprovalRequired": True, "forbiddenForAgents": True,
             "visibleWhen": _status("ENTWURF", "FREIGEGEBEN", "VERSANDT")},
            {"key": "stornieren", "label": "Stornieren", "dangerLevel": "high",
             "permission": "einkauf.bestellung.cancel", "commandEndpoint": pfad + "stornieren", "method": "POST",
             "requiresConfirmation": True, "auditReasonRequired": True, "forbiddenForAgents": True,
             "visibleWhen": _status("ENTWURF", "DRAFT", "FREIGEGEBEN", "VERSANDT", "TEILGELIEFERT")},
        ],
        dangerous=[
            {"key": "freigeben", "reason": "Gibt die Bestellung frei und bucht das Obligo; nur Mensch."},
            {"key": "versenden", "reason": "Sendet die Bestellung an den Lieferanten; nur Mensch."},
            {"key": "stornieren", "reason": "Storniert eine Bestellung; nur Mensch mit Begruendung."},
        ],
        purpose="Bestellungen an Lieferanten finden, freigeben, versenden und stornieren.",
        prompts=["Welche Bestellungen sind noch Entwurf?", "Welche Liefertermine sind ueberfaellig?"],
        no_workflow="Der Status steht an der Bestellung; die Liste fuehrt keinen eigenen Ablauf.",
    )



def build_agrar_saatgut_liste() -> dict[str, Any]:
    """Saatgut-Stammdaten; Zeile oeffnet die native Objektmaske ``agrar/saatgut``."""
    return _liste(
        screen_id="agrar/saatgut-liste", domain="agrar", title="Saatgut", subtitle="Sorten, Zulassungen und Bestand",
        endpoint="/api/v1/agrar/saatgut/", row_route="/agrar/saatgut/{id}", bundle="agrar", fetch_limit=200,
        columns=[
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "artikelnummer", "label": "Artikel-Nr.", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "sorte", "label": "Sorte", "filterable": True, "sortable": True, "priority": "primary"},
            {"key": "art", "label": "Kultur", "filterable": True, "priority": "secondary"},
            {"key": "zuechter", "label": "Zuechter", "filterable": True, "priority": "secondary"},
            {"key": "bsa_zulassung", "label": "BSA", "renderKind": "boolean", "priority": "tertiary"},
            {"key": "eu_zulassung", "label": "EU", "renderKind": "boolean", "priority": "tertiary"},
            {"key": "vk_preis", "label": "VK-Preis", "numeric": True, "renderKind": "currency", "priority": "secondary"},
            {"key": "verfuegbar", "label": "Verfuegbar", "numeric": True, "sortable": True, "priority": "secondary"},
        ],
        actions=[_neu("Neues Saatgut", "/agrar/saatgut-stamm"), _EXPORT],
        row_actions=[],
        purpose="Saatgut-Sorten mit Zulassung, Preis und verfuegbarem Bestand finden.",
        prompts=["Welche Weizensorten haben BSA-Zulassung?", "Welches Saatgut ist knapp?"],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )



def build_agrar_duenger_liste() -> dict[str, Any]:
    """Duenger-Stammdaten; Zeile oeffnet die native Objektmaske ``agrar/duenger``."""
    return _liste(
        screen_id="agrar/duenger-liste", domain="agrar", title="Duenger", subtitle="Duengemittel mit Naehrstoffen",
        endpoint="/api/v1/agrar/duenger/", row_route="/agrar/duenger/{id}", bundle="agrar", fetch_limit=200,
        columns=[
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "artikelnummer", "label": "Artikel-Nr.", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "hersteller", "label": "Hersteller", "filterable": True, "priority": "secondary"},
            {"key": "n_gehalt", "label": "N %", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "p_gehalt", "label": "P %", "numeric": True, "priority": "secondary"},
            {"key": "k_gehalt", "label": "K %", "numeric": True, "priority": "secondary"},
            {"key": "wassergefaehrdend", "label": "Wassergefaehrdend", "renderKind": "boolean", "priority": "tertiary"},
            {"key": "ist_aktiv", "label": "Aktiv", "renderKind": "boolean", "filterable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neuer Duenger", "/agrar/duenger-stamm"), _EXPORT],
        row_actions=[
            {"key": "deaktivieren", "label": "Deaktivieren", "dangerLevel": "high",
             "permission": "agrar.duenger.deactivate",
             "commandEndpoint": "/api/v1/agrar/duenger/{entity_id}/actions/deaktivieren", "method": "POST",
             "requiresConfirmation": True, "auditReasonRequired": True,
             "visibleWhen": {"field": "ist_aktiv", "values": [True]}},
        ],
        purpose="Duengemittel mit Naehrstoffgehalten finden, oeffnen und nicht mehr gefuehrte deaktivieren.",
        prompts=["Welche Stickstoffduenger fuehren wir?", "Welche Duenger sind wassergefaehrdend?"],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


LISTEN_SCREEN_BUILDERS = {
    "einkauf/anfragen": build_einkauf_anfragen_liste,
    "einkauf/angebote": build_einkauf_angebote_liste,
    "einkauf/anlieferavis-liste": build_einkauf_anlieferavis_liste,
    "einkauf/auftragsbestaetigungen": build_einkauf_auftragsbestaetigungen_liste,
    "einkauf/lieferanten": build_einkauf_lieferanten_liste,
    "einkauf/bestellungen": build_einkauf_bestellungen_liste,
    "agrar/saatgut-liste": build_agrar_saatgut_liste,
    "agrar/duenger-liste": build_agrar_duenger_liste,
}
LISTEN_ROUTEN = {"einkauf/anfragen": "/einkauf/anfragen", "einkauf/angebote": "/einkauf/angebote",
                "einkauf/anlieferavis-liste": "/einkauf/anlieferavis",
                "einkauf/auftragsbestaetigungen": "/einkauf/auftragsbestaetigungen",
                "einkauf/lieferanten": "/einkauf/lieferanten",
                "einkauf/bestellungen": "/einkauf/bestellungen",
                "agrar/saatgut-liste": "/agrar/saatgut",
                "agrar/duenger-liste": "/agrar/duenger"}
LISTEN_SYNONYME = {"einkauf/anfragen": ["anfragen", "bedarfsanforderungen", "banf"],
                   "einkauf/angebote": ["angebote", "lieferantenangebote", "preisvergleich"],
                   "einkauf/anlieferavis-liste": ["avise", "lieferavise", "anlieferungen"],
                   "einkauf/auftragsbestaetigungen": ["auftragsbestaetigungen", "ab", "ordrsp"],
                   "einkauf/lieferanten": ["lieferanten", "lieferantenliste", "kreditoren einkauf"],
                   "einkauf/bestellungen": ["bestellungen", "einkaufsbestellungen", "po"],
                   "agrar/saatgut-liste": ["saatgut", "sorten", "saatgutliste"],
                   "agrar/duenger-liste": ["duenger", "duengemittel", "duengerliste"]}
