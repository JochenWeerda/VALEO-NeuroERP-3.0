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



def build_futtermittel_einzelfuttermittel_liste() -> dict[str, Any]:
    """Einzelfuttermittel aus dem Futterkatalog, derselben Quelle wie die Objektmaske."""
    return _liste(
        screen_id="futtermittel/einzelfuttermittel-liste", domain="futtermittel", title="Einzelfuttermittel",
        subtitle="Futterkatalog mit Freigabe und Revision",
        endpoint="/api/v1/agrar/rations-optimization/feed-catalog/feeds",
        row_route="/futtermittel/einzelfuttermittel/{id}", bundle="futtermittel",
        columns=[
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "artikel_nummer", "label": "Artikel-Nr.", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "art", "label": "Art", "filterable": True, "priority": "primary"},
            {"key": "approval_status", "label": "Freigabe", "renderKind": "status", "filterable": True,
             "priority": "secondary"},
            {"key": "trockensubstanz", "label": "TS g/kg", "numeric": True, "priority": "secondary"},
            {"key": "preis_pro_t", "label": "Preis/t", "numeric": True, "renderKind": "currency",
             "priority": "secondary"},
            {"key": "revision", "label": "Revision", "numeric": True, "priority": "tertiary"},
            {"key": "updated_at", "label": "Geaendert", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neues Einzelfuttermittel", "/futtermittel/einzelfuttermittel/stamm/new"), _EXPORT],
        row_actions=[
            {"key": "stilllegen", "label": "Stilllegen", "dangerLevel": "high",
             "permission": "futtermittel.einzelfutter.retire",
             "commandEndpoint": "/api/v1/futter/einzelfuttermittel/{entity_id}/actions/stilllegen", "method": "POST",
             "requiresConfirmation": True, "auditReasonRequired": True,
             "visibleWhen": {"field": "aktiv", "values": [True]}},
        ],
        purpose="Einzelfuttermittel des Futterkatalogs finden, oeffnen und nicht mehr gefuehrte stilllegen.",
        prompts=["Welche Einzelfuttermittel sind freigegeben?", "Welche Futtermittel haben keinen Preis?"],
        no_workflow="Freigabe und Revision stehen am Katalogeintrag; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_futtermittel_mischfuttermittel_liste() -> dict[str, Any]:
    """Mischfuttermittel; dieselbe Quelle wie die Objektmaske ``futtermittel/mischfuttermittel``."""
    return _liste(
        screen_id="futtermittel/mischfuttermittel-liste", domain="futtermittel", title="Mischfuttermittel",
        subtitle="Mischfutter je Tierart und Leistungsstufe", endpoint="/api/v1/futter/mischfuttermittel",
        row_route="/futtermittel/mischfuttermittel/{id}", bundle="futtermittel",
        columns=[
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "produkt_code", "label": "Produkt-Code", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "tierart", "label": "Tierart", "filterable": True, "priority": "primary"},
            {"key": "leistungsstufe", "label": "Leistungsstufe", "filterable": True, "priority": "secondary"},
            {"key": "protein", "label": "Protein %", "numeric": True, "priority": "secondary"},
            {"key": "energie", "label": "Energie MJ", "numeric": True, "priority": "secondary"},
        ],
        actions=[_neu("Neues Mischfuttermittel", "/futtermittel/mischfuttermittel/stamm/new"), _EXPORT],
        row_actions=[
            {"key": "deaktivieren", "label": "Deaktivieren", "dangerLevel": "high",
             "permission": "futtermittel.mischfutter.deactivate",
             "commandEndpoint": "/api/v1/futter/mischfuttermittel/{entity_id}/actions/deaktivieren", "method": "POST",
             "requiresConfirmation": True, "auditReasonRequired": True,
             "visibleWhen": {"field": "aktiv", "values": [True]}},
        ],
        purpose="Mischfuttermittel je Tierart finden, oeffnen und nicht mehr gefuehrte deaktivieren.",
        prompts=["Welche Mischfutter fuehren wir fuer Milchkuehe?", "Zeige Mischfutter mit ueber 18 % Protein."],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )



def build_finance_debitoren_liste() -> dict[str, Any]:
    """Debitoren mit offenem Betrag und Mahnstufe; dieselbe Quelle wie die Objektmaske ``finance/debitor``."""
    pfad = "/api/v1/finance/debitoren/{entity_id}/actions/"
    return _liste(
        screen_id="finance/debitoren-liste", domain="finance", title="Debitoren",
        subtitle="Kunden mit Forderungen, Kreditlimit und Mahnstufe", endpoint="/api/v1/finance/debitoren",
        row_route="/finance/debitor/{id}", bundle="finance",
        columns=[
            {"key": "name", "label": "Debitor", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "debitoren_nr", "label": "Debitoren-Nr.", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "offenerBetrag", "label": "Offen", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "primary"},
            {"key": "mahnstufe", "label": "Mahnstufe", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "faelligkeit", "label": "Faellig", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "kreditlimit", "label": "Kreditlimit", "numeric": True, "renderKind": "currency",
             "priority": "secondary"},
            {"key": "zahlungsbedingungen", "label": "Zahlungsbedingungen", "priority": "tertiary"},
            {"key": "is_active", "label": "Aktiv", "renderKind": "boolean", "filterable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neuer Debitor", "/finance/debitoren/new"), _EXPORT,
                 {"key": "mahnwesen", "label": "Mahnwesen", "kind": "secondary", "dangerLevel": "safe",
                  "zone": "header", "navigationRoute": "/finance/mahnwesen", "localEffect": "navigation",
                  "stubReason": "Oeffnet das Mahnwesen; Mahnlaeufe laufen dort mit Vorschau und Freigabe."}],
        row_actions=[
            {"key": "sperren", "label": "Sperren", "dangerLevel": "high", "permission": "finance.debitor.sperren",
             "commandEndpoint": pfad + "sperren", "method": "POST", "requiresConfirmation": True,
             "auditReasonRequired": True, "forbiddenForAgents": True,
             "visibleWhen": {"field": "is_active", "values": [True]}},
            {"key": "entsperren", "label": "Entsperren", "dangerLevel": "moderate",
             "permission": "finance.debitor.entsperren", "commandEndpoint": pfad + "entsperren", "method": "POST",
             "requiresConfirmation": True, "auditReasonRequired": True, "forbiddenForAgents": True,
             "visibleWhen": {"field": "is_active", "values": [False]}},
        ],
        dangerous=[{"key": "sperren", "reason": "Sperrt einen Kunden fuer Verkauf und Zahlung; nur Mensch."}],
        purpose="Debitoren mit offenen Forderungen und Mahnstufe finden, oeffnen und sperren.",
        prompts=["Welche Debitoren haben Mahnstufe 2 oder hoeher?", "Welche Kunden haben die hoechsten offenen Posten?"],
        no_workflow="Mahnungen laufen im Mahnwesen; die Liste fuehrt keinen eigenen Ablauf.",
    )



def build_finance_kreditoren_liste() -> dict[str, Any]:
    """Kreditoren (die Lieferanten des Einkaufs); dieselbe Quelle wie die Objektmaske ``finance/kreditor``."""
    return _liste(
        screen_id="finance/kreditoren-liste", domain="finance", title="Kreditoren",
        subtitle="Lieferanten als Kreditoren mit Steuer- und Zahlungsdaten", endpoint="/api/v1/finance/kreditoren",
        row_route="/finance/kreditor/{id}", bundle="finance",
        columns=[
            {"key": "name", "label": "Kreditor", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kreditoren_nr", "label": "Kreditoren-Nr.", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "city", "label": "Ort", "filterable": True, "priority": "secondary"},
            {"key": "ust_id", "label": "USt-IdNr.", "filterable": True, "priority": "secondary"},
            {"key": "zahlungsbedingungen", "label": "Zahlungsbedingungen", "priority": "tertiary"},
            {"key": "email", "label": "E-Mail", "priority": "tertiary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "secondary"},
        ],
        actions=[_neu("Neuer Kreditor", "/finance/kreditoren-stamm"), _EXPORT],
        row_actions=[],
        purpose="Kreditoren finden und ihre Stamm-, Steuer- und Bankdaten oeffnen.",
        prompts=["Welche Kreditoren haben keine USt-IdNr.?", "Finde den Kreditor Muehle Nord."],
        no_workflow="Stammdatenliste ohne eigenen Ablauf; Kreditoren sind die Lieferanten des Einkaufs.",
    )


def build_crm_kampagnen_liste() -> dict[str, Any]:
    """Marketing-Kampagnen mit Versand- und Oeffnungszahlen."""
    return _liste(
        screen_id="crm/kampagnen-liste", domain="crm", title="Kampagnen", subtitle="Marketing-Kampagnen und Reichweite",
        endpoint="/api/v1/crm/campaigns", row_route="/crm/campaign/{id}", bundle="crm",
        columns=[
            {"key": "name", "label": "Kampagne", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "type", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "sent_count", "label": "Versendet", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "open_count", "label": "Geoeffnet", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "click_count", "label": "Klicks", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "created_at", "label": "Erstellt", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neue Kampagne", "/crm/campaign/new"), _EXPORT],
        row_actions=[
            {"key": "loeschen", "label": "Loeschen", "dangerLevel": "high", "permission": "crm.kampagne.loeschen",
             "commandEndpoint": "/api/v1/crm/campaigns/{entity_id}", "method": "DELETE",
             "requiresConfirmation": True, "auditReasonRequired": True, "forbiddenForAgents": True},
        ],
        dangerous=[{"key": "loeschen", "reason": "Entfernt eine Kampagne; nur Mensch."}],
        purpose="Kampagnen mit Versand-, Oeffnungs- und Klickzahlen finden und oeffnen.",
        prompts=["Welche Kampagnen sind noch im Entwurf?", "Welche Kampagne hat die meisten Klicks?"],
        no_workflow="Der Status steht an der Kampagne; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_crm_kampagnenvorlagen_liste() -> dict[str, Any]:
    """Vorlagen fuer Kampagnen: aktivieren, deaktivieren, duplizieren, loeschen."""
    pfad = "/api/v1/crm/campaigns/templates/{entity_id}"
    return _liste(
        screen_id="crm/kampagnenvorlagen-liste", domain="crm", title="Kampagnenvorlagen",
        subtitle="Vorlagen fuer E-Mail-, Brief- und SMS-Kampagnen", endpoint="/api/v1/crm/campaigns/templates",
        row_route="/crm/campaign-template/{id}", bundle="crm",
        columns=[
            {"key": "name", "label": "Vorlage", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "type", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "subject", "label": "Betreff", "filterable": True, "priority": "secondary"},
            {"key": "is_active", "label": "Aktiv", "renderKind": "boolean", "filterable": True, "priority": "primary"},
            {"key": "usage_count", "label": "Verwendet", "numeric": True, "sortable": True, "priority": "tertiary"},
            {"key": "created_at", "label": "Erstellt", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neue Vorlage", "/crm/campaign-template/new"), _EXPORT],
        row_actions=[
            {"key": "aktivieren", "label": "Aktivieren", "dangerLevel": "safe", "permission": "crm.vorlage.aktivieren",
             "commandEndpoint": pfad + "/activate", "method": "POST", "requiresConfirmation": True,
             "visibleWhen": {"field": "is_active", "values": [False]}},
            {"key": "deaktivieren", "label": "Deaktivieren", "dangerLevel": "moderate",
             "permission": "crm.vorlage.deaktivieren", "commandEndpoint": pfad + "/deactivate", "method": "POST",
             "requiresConfirmation": True, "visibleWhen": {"field": "is_active", "values": [True]}},
            {"key": "duplizieren", "label": "Duplizieren", "dangerLevel": "safe", "permission": "crm.vorlage.duplizieren",
             "commandEndpoint": pfad + "/duplicate", "method": "POST", "requiresConfirmation": True},
            {"key": "loeschen", "label": "Loeschen", "dangerLevel": "high", "permission": "crm.vorlage.loeschen",
             "commandEndpoint": pfad, "method": "DELETE", "requiresConfirmation": True,
             "auditReasonRequired": True, "forbiddenForAgents": True},
        ],
        dangerous=[{"key": "loeschen", "reason": "Entfernt eine Vorlage; nur Mensch."}],
        purpose="Kampagnenvorlagen pflegen: aktivieren, deaktivieren, duplizieren.",
        prompts=["Welche Vorlagen sind aktiv?", "Welche Vorlage wird am haeufigsten verwendet?"],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


def build_crm_einwilligungen_liste() -> dict[str, Any]:
    """Einwilligungen (Art. 7 DSGVO): widerrufen mit Grund; Loeschen wird nicht angeboten (Nachweispflicht)."""
    return _liste(
        screen_id="crm/einwilligungen-liste", domain="crm", title="Einwilligungen",
        subtitle="Einwilligungen je Kontakt und Kanal mit Double-Opt-in", endpoint="/api/v1/crm/consents",
        row_route="/crm/consent/{id}", bundle="crm",
        columns=[
            {"key": "contact_id", "label": "Kontakt", "filterable": True, "priority": "primary"},
            {"key": "channel", "label": "Kanal", "filterable": True, "priority": "primary"},
            {"key": "consent_type", "label": "Zweck", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "granted_at", "label": "Erteilt", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "double_opt_in_confirmed_at", "label": "Double-Opt-in", "renderKind": "date",
             "priority": "secondary"},
            {"key": "source", "label": "Quelle", "filterable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Einwilligung erfassen", "/crm/consent/new"), _EXPORT],
        row_actions=[
            {"key": "widerrufen", "label": "Widerrufen", "dangerLevel": "high",
             "permission": "crm.einwilligung.widerrufen",
             "commandEndpoint": "/api/v1/crm/consents/{entity_id}/revoke", "method": "POST",
             "requiresConfirmation": True, "auditReasonRequired": True, "forbiddenForAgents": True,
             "visibleWhen": {"field": "status", "values": ["granted"]}},
        ],
        dangerous=[{"key": "widerrufen", "reason": "Widerruft eine Einwilligung; nur Mensch mit Begruendung."}],
        purpose="Einwilligungen je Kontakt und Kanal nachweisen und auf Wunsch widerrufen.",
        prompts=["Welche Einwilligungen warten auf Double-Opt-in?", "Welche Einwilligungen wurden widerrufen?"],
        no_workflow="Der Status steht an der Einwilligung; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_dsgvo_anfragen_liste() -> dict[str, Any]:
    """Betroffenenanfragen (Art. 15, 17, 20): pruefen, Auskunft, Daten loeschen, ablehnen."""
    pfad = "/api/v1/gdpr/requests/{entity_id}/"
    return _liste(
        screen_id="crm/dsgvo-anfragen-liste", domain="crm", title="DSGVO-Anfragen",
        subtitle="Auskunft, Loeschung und Datenuebertragung", endpoint="/api/v1/gdpr/requests",
        row_route="/crm/gdpr-request/{id}", bundle="crm",
        columns=[
            {"key": "subject_email", "label": "Betroffene Person", "filterable": True, "priority": "primary"},
            {"key": "request_type", "label": "Art", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "created_at", "label": "Eingegangen", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "verified_at", "label": "Geprueft", "renderKind": "date", "priority": "secondary"},
            {"key": "completed_at", "label": "Abgeschlossen", "renderKind": "date", "priority": "secondary"},
            {"key": "rejection_reason", "label": "Ablehnungsgrund", "priority": "tertiary"},
        ],
        actions=[_neu("Anfrage erfassen", "/crm/gdpr-request/new")],
        row_actions=[
            {"key": "pruefen", "label": "Identitaet bestaetigt", "dangerLevel": "moderate",
             "permission": "dsgvo.anfrage.pruefen", "commandEndpoint": pfad + "verify", "method": "POST",
             "requiresConfirmation": True, "forbiddenForAgents": True,
             "visibleWhen": {"field": "status", "values": ["PENDING"]}},
            {"key": "exportieren", "label": "Auskunft erstellen", "dangerLevel": "moderate",
             "permission": "dsgvo.anfrage.exportieren", "commandEndpoint": pfad + "export", "method": "POST",
             "requiresConfirmation": True, "forbiddenForAgents": True,
             "visibleWhen": {"field": "status", "values": ["VERIFIED"]}},
            {"key": "daten_loeschen", "label": "Daten loeschen (Art. 17)", "dangerLevel": "critical",
             "permission": "dsgvo.anfrage.loeschen", "commandEndpoint": pfad + "delete", "method": "POST",
             "requiresConfirmation": True, "auditReasonRequired": True, "humanApprovalRequired": True,
             "forbiddenForAgents": True, "visibleWhen": {"field": "status", "values": ["VERIFIED"]}},
            {"key": "ablehnen", "label": "Ablehnen", "dangerLevel": "high", "permission": "dsgvo.anfrage.ablehnen",
             "commandEndpoint": pfad + "reject", "method": "POST", "requiresConfirmation": True,
             "auditReasonRequired": True, "forbiddenForAgents": True,
             "visibleWhen": {"field": "status", "values": ["PENDING", "VERIFIED", "PROCESSING"]}},
        ],
        dangerous=[
            {"key": "daten_loeschen", "reason": "Loescht personenbezogene Daten unwiderruflich (Art. 17); nur Mensch."},
            {"key": "ablehnen", "reason": "Lehnt eine Betroffenenanfrage ab; nur Mensch mit Begruendung."},
        ],
        purpose="Betroffenenanfragen fristgerecht pruefen, beantworten, loeschen oder begruendet ablehnen.",
        prompts=["Welche DSGVO-Anfragen sind noch offen?", "Welche Loeschanfragen sind geprueft?"],
        no_workflow="Der Ablauf (eingegangen, geprueft, abgeschlossen) steht an der Anfrage selbst.",
    )


def build_crm_segmente_liste() -> dict[str, Any]:
    """Kundensegmente: Mitglieder neu berechnen, loeschen."""
    return _liste(
        screen_id="crm/segmente-liste", domain="crm", title="Segmente",
        subtitle="Kundensegmente mit Mitgliederzahl", endpoint="/api/v1/crm/segments",
        row_route="/crm/segment/{id}", bundle="crm",
        columns=[
            {"key": "name", "label": "Segment", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "type", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "member_count", "label": "Mitglieder", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "last_calculated_at", "label": "Berechnet", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "created_at", "label": "Erstellt", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neues Segment", "/crm/segment/new"), _EXPORT],
        row_actions=[
            {"key": "berechnen", "label": "Neu berechnen", "dangerLevel": "safe", "permission": "crm.segment.berechnen",
             "commandEndpoint": "/api/v1/crm/segments/{entity_id}/calculate", "method": "POST",
             "requiresConfirmation": True},
            {"key": "loeschen", "label": "Loeschen", "dangerLevel": "high", "permission": "crm.segment.loeschen",
             "commandEndpoint": "/api/v1/crm/segments/{entity_id}", "method": "DELETE",
             "requiresConfirmation": True, "auditReasonRequired": True, "forbiddenForAgents": True},
        ],
        dangerous=[{"key": "loeschen", "reason": "Entfernt ein Segment; nur Mensch."}],
        purpose="Kundensegmente finden, Mitglieder neu berechnen und nicht mehr genutzte entfernen.",
        prompts=["Wie viele Mitglieder hat jedes Segment?", "Welche Segmente sind lange nicht berechnet?"],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


def build_crm_opportunities_liste() -> dict[str, Any]:
    """Verkaufschancen; Zeile oeffnet die native Objektmaske ``crm/opportunity``."""
    pfad = "/api/v1/crm/opportunities/{entity_id}/actions/"
    return _liste(
        screen_id="crm/opportunities-liste", domain="crm", title="Verkaufschancen",
        subtitle="Pipeline mit Phase, Betrag und Wahrscheinlichkeit", endpoint="/api/v1/crm/opportunities/",
        row_route="/crm/opportunity/{id}", bundle="crm", fetch_limit=200,
        columns=[
            {"key": "name", "label": "Chance", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "stage", "label": "Phase", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "amount", "label": "Betrag", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "primary"},
            {"key": "probability", "label": "Wahrscheinlichkeit %", "numeric": True, "sortable": True,
             "priority": "secondary"},
            {"key": "expected_close_date", "label": "Abschluss geplant", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "assigned_to", "label": "Verantwortlich", "filterable": True, "priority": "tertiary"},
            {"key": "created_at", "label": "Erstellt", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neue Chance", "/crm/opportunity/new"), _EXPORT,
                 {"key": "kanban", "label": "Pipeline-Ansicht", "kind": "secondary", "dangerLevel": "safe",
                  "zone": "header", "navigationRoute": "/crm/opportunities-kanban", "localEffect": "navigation",
                  "stubReason": "Oeffnet die Pipeline als Kanban."}],
        row_actions=[
            {"key": "angebot", "label": "Angebot erstellen", "dangerLevel": "safe",
             "navigationRoute": "/sales/angebot-erstellen?opportunityId={id}", "localEffect": "navigation",
             "stubReason": "Oeffnet die Angebotserfassung mit dieser Chance."},
            {"key": "gewonnen", "label": "Gewonnen", "dangerLevel": "moderate", "permission": "crm.chance.gewonnen",
             "commandEndpoint": pfad + "gewonnen", "method": "POST", "requiresConfirmation": True,
             "forbiddenForAgents": True},
            {"key": "verloren", "label": "Verloren", "dangerLevel": "moderate", "permission": "crm.chance.verloren",
             "commandEndpoint": pfad + "verloren", "method": "POST", "requiresConfirmation": True,
             "auditReasonRequired": True, "forbiddenForAgents": True},
        ],
        purpose="Verkaufschancen nach Phase und Betrag steuern, Angebote erstellen und abschliessen.",
        prompts=["Welche Chancen schliessen diesen Monat?", "Welche Chancen haben ueber 70 % Wahrscheinlichkeit?"],
        no_workflow="Die Phase steht an der Chance; die Pipeline-Ansicht zeigt den Ablauf.",
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
    "futtermittel/einzelfuttermittel-liste": build_futtermittel_einzelfuttermittel_liste,
    "futtermittel/mischfuttermittel-liste": build_futtermittel_mischfuttermittel_liste,
    "finance/debitoren-liste": build_finance_debitoren_liste,
    "finance/kreditoren-liste": build_finance_kreditoren_liste,
    "crm/kampagnen-liste": build_crm_kampagnen_liste,
    "crm/kampagnenvorlagen-liste": build_crm_kampagnenvorlagen_liste,
    "crm/einwilligungen-liste": build_crm_einwilligungen_liste,
    "crm/dsgvo-anfragen-liste": build_dsgvo_anfragen_liste,
    "crm/segmente-liste": build_crm_segmente_liste,
    "crm/opportunities-liste": build_crm_opportunities_liste,
}
LISTEN_ROUTEN = {"einkauf/anfragen": "/einkauf/anfragen", "einkauf/angebote": "/einkauf/angebote",
                "einkauf/anlieferavis-liste": "/einkauf/anlieferavis",
                "einkauf/auftragsbestaetigungen": "/einkauf/auftragsbestaetigungen",
                "einkauf/lieferanten": "/einkauf/lieferanten",
                "einkauf/bestellungen": "/einkauf/bestellungen",
                "agrar/saatgut-liste": "/agrar/saatgut",
                "agrar/duenger-liste": "/agrar/duenger",
                "futtermittel/einzelfuttermittel-liste": "/futtermittel/einzelfuttermittel-liste",
                "futtermittel/mischfuttermittel-liste": "/futtermittel/mischfuttermittel-liste",
                "finance/debitoren-liste": "/finance/debitoren-liste",
                "finance/kreditoren-liste": "/finance/kreditoren",
                "crm/kampagnen-liste": "/crm/campaigns",
                "crm/kampagnenvorlagen-liste": "/crm/campaign-templates",
                "crm/einwilligungen-liste": "/crm/consents",
                "crm/dsgvo-anfragen-liste": "/crm/gdpr-requests",
                "crm/segmente-liste": "/crm/segments",
                "crm/opportunities-liste": "/crm/opportunities"}
LISTEN_SYNONYME = {"einkauf/anfragen": ["anfragen", "bedarfsanforderungen", "banf"],
                   "einkauf/angebote": ["angebote", "lieferantenangebote", "preisvergleich"],
                   "einkauf/anlieferavis-liste": ["avise", "lieferavise", "anlieferungen"],
                   "einkauf/auftragsbestaetigungen": ["auftragsbestaetigungen", "ab", "ordrsp"],
                   "einkauf/lieferanten": ["lieferanten", "lieferantenliste", "kreditoren einkauf"],
                   "einkauf/bestellungen": ["bestellungen", "einkaufsbestellungen", "po"],
                   "agrar/saatgut-liste": ["saatgut", "sorten", "saatgutliste"],
                   "agrar/duenger-liste": ["duenger", "duengemittel", "duengerliste"],
                   "futtermittel/einzelfuttermittel-liste": ["einzelfuttermittel", "futterkatalog", "futtermittel"],
                   "futtermittel/mischfuttermittel-liste": ["mischfuttermittel", "mischfutter", "kraftfutter"],
                   "finance/debitoren-liste": ["debitoren", "debitorenliste", "forderungen"],
                   "finance/kreditoren-liste": ["kreditoren", "kreditorenliste", "verbindlichkeiten stamm"],
                   "crm/kampagnen-liste": ["kampagnen", "marketing", "campaigns"],
                   "crm/kampagnenvorlagen-liste": ["kampagnenvorlagen", "vorlagen", "templates"],
                   "crm/einwilligungen-liste": ["einwilligungen", "consent", "opt-in"],
                   "crm/dsgvo-anfragen-liste": ["dsgvo-anfragen", "betroffenenanfragen", "gdpr"],
                   "crm/segmente-liste": ["segmente", "kundensegmente", "zielgruppen"],
                   "crm/opportunities-liste": ["verkaufschancen", "opportunities", "pipeline"]}
