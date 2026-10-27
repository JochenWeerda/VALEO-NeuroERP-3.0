"""Listenmasken als ScreenDefinition (MASK-STUDIO-ROLLOUT-20261020, Welle 1).

Die Listen zu den nativen Objektmasken waren handgebaut oder Altmuster-Konfigurationen. Hier sind sie
ScreenDefinitions: Spalten, Zeilenroute zur nativen Objektmaske und alle Aktionen mit ihrem Kommando-Weg. Die Seite
ist ``NativeListPage`` und enthaelt keinen eigenen Code; Maske, CLI und MCP rufen dieselben Wege.

Shell: ``StammListenParent`` in ``app.core.stamm_list_parent`` (``build_stamm_list_screen``).
"""
from __future__ import annotations

from typing import Any

from app.core.stamm_list_parent import (
    build_stamm_list_screen,
    stamm_list_export_action,
    stamm_list_neu_action,
    stamm_list_status_visible,
)

_EXPORT = stamm_list_export_action()


def _neu(label: str, route: str) -> dict[str, Any]:
    return stamm_list_neu_action(label, route)


def _liste(**kwargs: Any) -> dict[str, Any]:
    return build_stamm_list_screen(**kwargs)


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
    return stamm_list_status_visible(*werte)


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
        row_route="/finance/debitor/{id}", bundle="finance", table_profile="financial",
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
        row_route="/finance/kreditor/{id}", bundle="finance", table_profile="financial",
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
        row_route="/crm/segment/{id}", bundle="crm", fetch_limit=200,
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


def build_agrar_psm_liste() -> dict[str, Any]:
    """Pflanzenschutzmittel aus dem BVL-Verzeichnis (wie die bisherige Seite)."""
    return _liste(
        screen_id="agrar/psm-liste", domain="agrar", title="Pflanzenschutzmittel",
        subtitle="Zugelassene Mittel mit Wirkstoff, Kulturen und Zulassungsende",
        endpoint="/api/v1/agrar/psm/?source=bvl", row_route="/agrar/psm/stamm/{id}", bundle="agrar", fetch_limit=200,
        columns=[
            {"key": "mittel", "label": "Mittel", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "wirkstoff", "label": "Wirkstoff", "filterable": True, "priority": "primary"},
            {"key": "kulturen", "label": "Kulturen", "filterable": True, "priority": "secondary"},
            {"key": "zulassungBis", "label": "Zulassung bis", "renderKind": "date", "sortable": True,
             "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "secondary"},
            {"key": "erklaerungLandwirtStatus", "label": "Erklaerung Landwirt", "priority": "tertiary"},
        ],
        actions=[_neu("Neues Mittel", "/agrar/psm/stamm/neu"), _EXPORT],
        row_actions=[],
        purpose="Pflanzenschutzmittel mit Zulassung und Wirkstoff finden und oeffnen.",
        prompts=["Welche Mittel laufen dieses Jahr aus?", "Welche Mittel enthalten Glyphosat?"],
        no_workflow="Verzeichnisliste ohne eigenen Ablauf.",
    )


def build_artikel_liste() -> dict[str, Any]:
    """Artikelstamm mit Warengruppe, Preis und Bestand."""
    return _liste(
        screen_id="artikel/liste", domain="lager", title="Artikel", subtitle="Artikelstamm mit Preis und Bestand",
        endpoint="/api/v1/articles/", row_route="/artikel/{id}", bundle="lager", fetch_limit=200,
        columns=[
            {"key": "article_number", "label": "Artikel-Nr.", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "category", "label": "Warengruppe", "filterable": True, "priority": "primary"},
            {"key": "sales_price", "label": "VK-Preis", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "secondary"},
            {"key": "current_stock", "label": "Bestand", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "unit", "label": "Einheit", "priority": "tertiary"},
            {"key": "is_active", "label": "Aktiv", "renderKind": "boolean", "filterable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neuer Artikel", "/artikel/neu"), _EXPORT],
        row_actions=[],
        purpose="Artikel mit Warengruppe, Preis und Bestand finden und oeffnen.",
        prompts=["Welche Artikel der Warengruppe Duenger fuehren wir?", "Welche Artikel haben keinen Bestand?"],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


def build_chargen_liste() -> dict[str, Any]:
    """Chargen mit Artikel, Menge, Lagerort und Status."""
    return _liste(
        screen_id="charge/liste", domain="lager", title="Chargen", subtitle="Chargen mit Lagerort und Freigabestatus",
        endpoint="/api/v1/chargen", row_route="/charge/stamm/{id}", bundle="lager",
        columns=[
            {"key": "chargenId", "label": "Charge", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "primary"},
            {"key": "menge", "label": "Menge (t)", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "lagerort", "label": "Lagerort", "filterable": True, "priority": "secondary"},
            {"key": "eingang", "label": "Eingang", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Wareneingang erfassen", "/charge/wareneingang"), _EXPORT],
        row_actions=[],
        purpose="Chargen nach Artikel, Lagerort und Status finden und ihre Spur oeffnen.",
        prompts=["Welche Chargen sind noch in Pruefung?", "Welche Chargen liegen in Silo 3?"],
        no_workflow="Der Status steht an der Charge; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_personal_mitarbeiter_liste() -> dict[str, Any]:
    """Mitarbeitende; Zugriff und Felder wie der Personalweg."""
    return _liste(
        screen_id="personal/mitarbeiter-liste", domain="personal", title="Mitarbeitende",
        subtitle="Mitarbeitende mit Abteilung und Position", endpoint="/api/v1/personal/mitarbeiter",
        row_route="/personal/mitarbeiter/{id}", bundle="personal",
        columns=[
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "abteilung", "label": "Abteilung", "filterable": True, "priority": "primary"},
            {"key": "position", "label": "Position", "filterable": True, "priority": "secondary"},
            {"key": "email", "label": "E-Mail", "priority": "tertiary"},
            {"key": "eintrittsdatum", "label": "Eintritt", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Neue Mitarbeiterin / neuer Mitarbeiter", "/personal/mitarbeiter/neu"), _EXPORT],
        row_actions=[],
        purpose="Mitarbeitende nach Abteilung und Status finden und ihre Personalakte oeffnen.",
        prompts=["Wer arbeitet im Lager?", "Wer ist seit diesem Jahr dabei?"],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


#: Diese Bereiche haben noch keine Detail- oder Anlageseite: Ihre Routen zeigten die Liste selbst. Die Listen
#: verlinken deshalb nichts, bis es eine Objektmaske gibt (MASK-STUDIO-ROLLOUT, keine toten Links).


def build_versicherungen_liste() -> dict[str, Any]:
    """Versicherungsvertraege mit Praemie und Ablauf."""
    return _liste(
        screen_id="versicherungen/liste", domain="finance", title="Versicherungen",
        subtitle="Vertraege mit Praemie, Summe und Ablauf", endpoint="/api/v1/versicherungen", row_route=None,
        bundle="finance", table_profile="financial",
        columns=[
            {"key": "art", "label": "Art", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "versicherer", "label": "Versicherer", "filterable": True, "priority": "primary"},
            {"key": "vertragsnummer", "label": "Vertrag", "filterable": True, "priority": "secondary"},
            {"key": "praemie", "label": "Praemie", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "primary"},
            {"key": "versicherungssumme", "label": "Summe", "numeric": True, "renderKind": "currency",
             "priority": "secondary"},
            {"key": "ablauf", "label": "Ablauf", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Versicherungsvertraege mit Praemie und Ablauf im Blick behalten.",
        prompts=["Welche Versicherungen laufen dieses Jahr aus?", "Was kosten alle Praemien zusammen?"],
        no_workflow="Vertragsliste ohne eigenen Ablauf.",
    )


def build_wartung_anlagen_liste() -> dict[str, Any]:
    """Anlagen mit letzter und naechster Wartung."""
    return _liste(
        screen_id="wartung/anlagen-liste", domain="lager", title="Wartung", subtitle="Anlagen und Wartungstermine",
        endpoint="/api/v1/wartung/anlagen", row_route=None, bundle="lager",
        columns=[
            {"key": "name", "label": "Anlage", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "standort", "label": "Standort", "filterable": True, "priority": "secondary"},
            {"key": "letzte_wartung", "label": "Letzte Wartung", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "naechste_wartung", "label": "Naechste Wartung", "renderKind": "date", "sortable": True,
             "priority": "primary"},
            {"key": "verantwortlicher", "label": "Verantwortlich", "filterable": True, "priority": "tertiary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Faellige Wartungen der Anlagen finden.",
        prompts=["Welche Anlagen sind diesen Monat zur Wartung faellig?", "Welche Anlagen sind defekt?"],
        no_workflow="Anlagenliste ohne eigenen Ablauf.",
    )


def build_projekte_liste() -> dict[str, Any]:
    """Projekte mit Fortschritt und Budget."""
    return _liste(
        screen_id="projekte/liste", domain="controlling", title="Projekte",
        subtitle="Projekte mit Fortschritt, Budget und Ausgaben", endpoint="/api/v1/projekte", row_route=None,
        bundle="controlling",
        columns=[
            {"key": "name", "label": "Projekt", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "projektleiter", "label": "Leitung", "filterable": True, "priority": "secondary"},
            {"key": "kunde", "label": "Kunde", "filterable": True, "priority": "secondary"},
            {"key": "fortschritt", "label": "Fortschritt %", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "budget", "label": "Budget", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "ausgaben", "label": "Ausgaben", "numeric": True, "renderKind": "currency", "priority": "secondary"},
            {"key": "enddatum", "label": "Ende", "renderKind": "date", "sortable": True, "priority": "tertiary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Projekte nach Fortschritt, Budget und Ausgaben steuern.",
        prompts=["Welche Projekte liegen ueber Budget?", "Welche Projekte enden diesen Monat?"],
        no_workflow="Projektliste ohne eigenen Ablauf.",
    )


def build_labor_proben_liste() -> dict[str, Any]:
    """Laborproben mit Typ, Artikel und Status."""
    return _liste(
        screen_id="labor/proben-liste", domain="qualitaet", title="Laborproben", subtitle="Proben und ihr Bearbeitungsstand",
        endpoint="/api/v1/labor/proben", row_route=None, bundle="qualitaet",
        columns=[
            {"key": "probennummer", "label": "Probe", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "secondary"},
            {"key": "labor", "label": "Labor", "filterable": True, "priority": "secondary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Laborproben und ihren Bearbeitungsstand verfolgen.",
        prompts=["Welche Proben sind noch ausstehend?", "Welche Proben gingen diese Woche ans Labor?"],
        no_workflow="Probenliste ohne eigenen Ablauf.",
    )


def build_foerder_antraege_liste() -> dict[str, Any]:
    """Foerderantraege; Zeile oeffnet den Antrag."""
    return _liste(
        screen_id="foerderung/liste", domain="agrar", title="Foerderantraege",
        subtitle="Antraege mit Programm, Flaeche und Betrag", endpoint="/api/v1/foerderung/antraege",
        row_route="/foerderung/antrag/{id}", bundle="agrar",
        columns=[
            {"key": "nummer", "label": "Antrag", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "programm", "label": "Programm", "filterable": True, "priority": "primary"},
            {"key": "antragsdatum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "flaeche", "label": "Flaeche (ha)", "numeric": True, "priority": "secondary"},
            {"key": "betrag", "label": "Betrag", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Neuer Antrag", "/foerderung/antrag"), _EXPORT],
        row_actions=[],
        purpose="Foerderantraege nach Programm und Stand verfolgen.",
        prompts=["Welche Antraege sind eingereicht?", "Welche Foerdersumme ist bewilligt?"],
        no_workflow="Der Stand steht am Antrag; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_schaeden_liste() -> dict[str, Any]:
    """Schadenmeldungen mit Frist; Zeile oeffnet die Meldung."""
    return _liste(
        screen_id="schaeden/liste", domain="finance", title="Schadenmeldungen",
        subtitle="Schaeden mit Meldefrist und Regulierung", endpoint="/api/v1/schaeden/meldungen",
        row_route="/schaeden/{id}", bundle="finance", table_profile="financial",
        columns=[
            {"key": "meldungsnummer", "label": "Meldung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "art", "label": "Art", "filterable": True, "priority": "primary"},
            {"key": "schadendatum", "label": "Schadendatum", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "melden_bis", "label": "Melden bis", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "schadenhoehe", "label": "Schadenhoehe", "numeric": True, "renderKind": "currency",
             "priority": "secondary"},
            {"key": "regulierungsbetrag", "label": "Reguliert", "numeric": True, "renderKind": "currency",
             "priority": "tertiary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Schaden melden", "/schaeden/meldung"), _EXPORT],
        row_actions=[],
        purpose="Schadenmeldungen mit Meldefrist und Regulierungsstand verfolgen.",
        prompts=["Welche Schaeden muessen diese Woche gemeldet werden?", "Welche Schaeden sind reguliert?"],
        no_workflow="Der Stand steht an der Meldung; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_admin_benutzer_liste() -> dict[str, Any]:
    """Benutzer des Mandanten; Detail- und Anlage-Route zeigten die Liste selbst, deshalb ohne Links."""
    return _liste(
        screen_id="admin/benutzer-liste", domain="admin", title="Benutzer", subtitle="Benutzer mit Rolle und letzter Anmeldung",
        endpoint="/api/v1/admin/benutzer", row_route=None, bundle="admin",
        columns=[
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "email", "label": "E-Mail", "filterable": True, "priority": "primary"},
            {"key": "rolle", "label": "Rolle", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "secondary"},
            {"key": "letzteAnmeldung", "label": "Letzte Anmeldung", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Benutzer mit Rolle und letzter Anmeldung pruefen.",
        prompts=["Wer hat sich seit drei Monaten nicht angemeldet?", "Welche Benutzer sind Administratoren?"],
        no_workflow="Benutzerliste ohne eigenen Ablauf.",
    )


def build_compliance_pcn_liste() -> dict[str, Any]:
    """PCN-Meldungen (Giftinformationszentren) mit UFI und Status."""
    return _liste(
        screen_id="compliance/pcn-liste", domain="compliance", title="PCN-Meldungen",
        subtitle="Meldungen an die Giftinformationszentren mit UFI", endpoint="/api/v1/compliance/pcn-meldungen",
        row_route=None, bundle="compliance", fetch_limit=200,
        columns=[
            {"key": "produktname", "label": "Produkt", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "ufi", "label": "UFI", "filterable": True, "priority": "primary"},
            {"key": "verwendungskategorie", "label": "Verwendung", "filterable": True, "priority": "secondary"},
            {"key": "cas_nummern", "label": "CAS-Nummern", "priority": "tertiary"},
            {"key": "pcnStatus", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "created_at", "label": "Erstellt", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_neu("Neue PCN-Meldung", "/compliance/pcn-ufi"), _EXPORT],
        row_actions=[],
        purpose="PCN-Meldungen mit UFI und Uebermittlungsstand nachweisen.",
        prompts=["Welche PCN-Meldungen sind noch Entwurf?", "Welche UFI hat Produkt X?"],
        no_workflow="Der Status steht an der Meldung; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_personal_stundenzettel_liste() -> dict[str, Any]:
    """Stundenzettel der Fahrer mit Arbeitszeit und Ueberstunden."""
    return _liste(
        screen_id="personal/stundenzettel-liste", domain="personal", title="Stundenzettel",
        subtitle="Fahrer-Stundenzettel mit Arbeitszeit und Ueberstunden", endpoint="/api/v1/personal/stundenzettel",
        row_route=None, bundle="personal",
        columns=[
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "fahrer", "label": "Fahrer", "filterable": True, "sortable": True, "priority": "primary"},
            {"key": "kennzeichen", "label": "Kennzeichen", "filterable": True, "priority": "secondary"},
            {"key": "gesamtArbeitszeit", "label": "Arbeitszeit (h)", "numeric": True, "sortable": True,
             "priority": "primary"},
            {"key": "ueberstunden", "label": "Ueberstunden (h)", "numeric": True, "sortable": True,
             "priority": "primary"},
            {"key": "erstelltAm", "label": "Erfasst", "renderKind": "date", "priority": "tertiary"},
        ],
        actions=[_neu("Stundenzettel erfassen", "/personal/stundenzettel"), _EXPORT],
        row_actions=[],
        purpose="Fahrer-Stundenzettel mit Arbeitszeit und Ueberstunden auswerten.",
        prompts=["Wer hatte diese Woche Ueberstunden?", "Wie viele Stunden fuhr Fahrer X im Monat?"],
        no_workflow="Erfassungsliste ohne eigenen Ablauf.",
    )


def build_finance_wechselkurse_liste() -> dict[str, Any]:
    """Wechselkurse je Waehrungspaar und Stichtag; anlegen, deaktivieren und aktivieren mit Begruendung."""
    pfad = "/api/v1/finance/exchange-rates/{entity_id}/actions/"
    aktiv = {"field": "active", "values": [True]}
    inaktiv = {"field": "active", "values": [False]}
    return _liste(
        screen_id="finance/wechselkurse", domain="finance", title="Wechselkurse",
        subtitle="Kurse je Waehrungspaar und Stichtag",         endpoint="/api/v1/finance/exchange-rates?active_only=false",
        row_route=None, bundle="finance", table_profile="financial",
        columns=[
            {"key": "from_currency", "label": "Von", "filterable": True, "sortable": True, "priority": "primary"},
            {"key": "to_currency", "label": "Nach", "filterable": True, "sortable": True, "priority": "primary"},
            {"key": "rate", "label": "Kurs", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "rate_date", "label": "Stichtag", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "rate_type", "label": "Kursart", "filterable": True, "priority": "secondary"},
            {"key": "source", "label": "Quelle", "filterable": True, "priority": "secondary"},
            {"key": "active", "label": "Aktiv", "renderKind": "boolean", "filterable": True, "priority": "secondary"},
        ],
        actions=[
            {"key": "neu", "label": "Kurs erfassen", "kind": "primary", "dangerLevel": "safe", "zone": "header",
             "permission": "finance.wechselkurs.create", "commandEndpoint": "/api/v1/finance/exchange-rates",
             "method": "POST", "inputFields": [
                 {"key": "from_currency", "label": "Von (ISO)", "type": "text", "required": True},
                 {"key": "to_currency", "label": "Nach (ISO)", "type": "text", "required": True},
                 {"key": "rate", "label": "Kurs", "type": "number", "required": True},
                 {"key": "rate_date", "label": "Stichtag", "type": "date", "required": True},
                 {"key": "rate_type", "label": "Kursart", "type": "select", "options": [
                     {"value": "SPOT", "label": "Tageskurs"}, {"value": "AVERAGE", "label": "Durchschnitt"},
                     {"value": "FORWARD", "label": "Terminkurs"}]},
                 {"key": "source", "label": "Quelle", "type": "text"},
             ]},
            _EXPORT,
        ],
        row_actions=[
            {"key": "deaktivieren", "label": "Deaktivieren", "dangerLevel": "moderate",
             "permission": "finance.wechselkurs.deaktivieren", "commandEndpoint": pfad + "deaktivieren",
             "method": "POST", "requiresConfirmation": True, "auditReasonRequired": True, "visibleWhen": aktiv},
            {"key": "aktivieren", "label": "Aktivieren", "dangerLevel": "safe",
             "permission": "finance.wechselkurs.aktivieren", "commandEndpoint": pfad + "aktivieren",
             "method": "POST", "requiresConfirmation": True, "auditReasonRequired": True, "visibleWhen": inaktiv},
        ],
        purpose="Wechselkurse fuer Fremdwaehrungsbelege pflegen und nachweisen.",
        prompts=["Welcher USD-Kurs galt am Monatsende?", "Welche Kurse sind deaktiviert?"],
        no_workflow="Kurse sind Referenzdaten ohne eigenen Ablauf.",
    )


def build_finance_buchungsvorlagen_liste() -> dict[str, Any]:
    """Buchungsvorlagen: anwenden (erzeugt einen Buchungsentwurf) und loeschen, wie die bisherige Seite."""
    return _liste(
        screen_id="finance/buchungsvorlagen", domain="finance", title="Buchungsvorlagen",
        subtitle="Wiederkehrende Buchungen als Vorlage",         endpoint="/api/v1/finance/booking-templates?active_only=false",
        row_route=None, bundle="finance", table_profile="financial",
        columns=[
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "category", "label": "Kategorie", "filterable": True, "priority": "primary"},
            {"key": "trigger_type", "label": "Ausloeser", "filterable": True, "priority": "secondary"},
            {"key": "default_amount", "label": "Standardbetrag", "numeric": True, "renderKind": "currency",
             "priority": "secondary"},
            {"key": "currency", "label": "Waehrung", "priority": "tertiary"},
            {"key": "active", "label": "Aktiv", "renderKind": "boolean", "filterable": True, "priority": "secondary"},
            {"key": "shared", "label": "Gemeinsam", "renderKind": "boolean", "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[
            {"key": "anwenden", "label": "Anwenden", "dangerLevel": "moderate", "permission": "finance.buchung.create",
             "commandEndpoint": "/api/v1/finance/booking-templates/{entity_id}/apply", "method": "POST",
             "requiresConfirmation": True, "visibleWhen": {"field": "active", "values": [True]},
             "inputFields": [
                 {"key": "entry_date", "label": "Belegdatum", "type": "date", "required": True},
                 {"key": "amount", "label": "Betrag (leer: Standardbetrag)", "type": "number"},
                 {"key": "reference", "label": "Referenz", "type": "text"},
                 {"key": "description", "label": "Buchungstext (leer: aus der Vorlage)", "type": "text"},
             ]},
            {"key": "loeschen", "label": "Loeschen", "dangerLevel": "high", "permission": "finance.buchungsvorlage.delete",
             "commandEndpoint": "/api/v1/finance/booking-templates/{entity_id}", "method": "DELETE",
             "requiresConfirmation": True, "visibleWhen": {"field": "shared", "values": [False]}},
        ],
        purpose="Wiederkehrende Buchungen als Entwurf erzeugen; der Entwurf geht durch die normale Buchungspruefung.",
        prompts=["Welche Buchungsvorlagen gibt es fuer Abschreibungen?", "Wende die Mietvorlage fuer Oktober an."],
        dangerous=[{"key": "loeschen", "reason": "Entfernt die Vorlage dauerhaft."}],
        no_workflow="Anwenden erzeugt einen Buchungsentwurf; Freigabe und Buchung laufen im Journal.",
    )


def build_einkauf_warengruppen_liste() -> dict[str, Any]:
    """Warengruppen (dritte Ebene unter Haupt- und Oberwarengruppe): anlegen, bearbeiten, deaktivieren."""
    pfad = "/api/v1/stammdaten/warengruppen/{entity_id}/actions/"
    ober = {"key": "ober_id", "label": "Oberwarengruppe", "type": "select", "required": True,
            "optionsSource": {"endpoint": "/api/v1/stammdaten/warengruppen/ober", "valueKey": "id",
                              "labelKey": "bezeichnung"}}
    return _liste(
        screen_id="einkauf/warengruppen", domain="einkauf", title="Warengruppen",
        subtitle="Warengruppen unter Haupt- und Oberwarengruppe", endpoint="/api/v1/stammdaten/warengruppen",
        row_route=None, bundle="einkauf",
        columns=[
            {"key": "gruppe_nr", "label": "Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "bezeichnung", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "ober_id", "label": "Oberwarengruppe", "filterable": True, "priority": "secondary"},
            {"key": "created_at", "label": "Angelegt", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[
            {"key": "neu", "label": "Warengruppe anlegen", "kind": "primary", "dangerLevel": "safe", "zone": "header",
             "permission": "stammdaten.warengruppe.create", "commandEndpoint": "/api/v1/stammdaten/warengruppen",
             "method": "POST", "inputFields": [
                 {"key": "gruppe_nr", "label": "Nr.", "type": "text", "required": True},
                 {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True}, ober]},
            _EXPORT,
        ],
        row_actions=[
            {"key": "bearbeiten", "label": "Bearbeiten", "dangerLevel": "safe",
             "permission": "stammdaten.warengruppe.update", "commandEndpoint": pfad + "bearbeiten", "method": "POST",
             "inputFields": [{"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True}, ober]},
            {"key": "deaktivieren", "label": "Deaktivieren", "dangerLevel": "moderate",
             "permission": "stammdaten.warengruppe.deaktivieren", "commandEndpoint": pfad + "deaktivieren",
             "method": "POST", "requiresConfirmation": True, "auditReasonRequired": True},
        ],
        purpose="Warengruppen fuer Artikel, Auswertungen und Einkauf pflegen.",
        prompts=["Welche Warengruppen gehoeren zu Saatgut?", "Lege die Warengruppe Biostimulanzien an."],
        no_workflow="Warengruppen sind Referenzdaten ohne eigenen Ablauf.",
    )


def build_einkauf_zahlungsbedingungen_liste() -> dict[str, Any]:
    """Zahlungsbedingungen mit Ziel und zwei Skontostufen: anlegen, bearbeiten, deaktivieren."""
    pfad = "/api/v1/fibu/zahlungsbedingungen/{entity_id}/actions/"
    art = {"key": "zahlungsart", "label": "Zahlungsart", "type": "select", "options": [
        {"value": "ueberweisung", "label": "Ueberweisung"}, {"value": "lastschrift", "label": "Lastschrift"},
        {"value": "scheck", "label": "Scheck"}, {"value": "kasse", "label": "Kasse"},
        {"value": "vorkasse", "label": "Vorkasse"}]}
    werte = [
        {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
        {"key": "zahlungsziel_tage", "label": "Zahlungsziel (Tage)", "type": "number", "required": True},
        {"key": "skonto1_tage", "label": "Skonto 1 Tage", "type": "number"},
        {"key": "skonto1_prozent", "label": "Skonto 1 %", "type": "number"},
        {"key": "skonto2_tage", "label": "Skonto 2 Tage", "type": "number"},
        {"key": "skonto2_prozent", "label": "Skonto 2 %", "type": "number"},
        {"key": "netto_tage", "label": "Netto (Tage)", "type": "number"},
        art,
    ]
    return _liste(
        screen_id="einkauf/zahlungsbedingungen", domain="finance", title="Zahlungsbedingungen",
        subtitle="Zahlungsziel und Skontostufen", endpoint="/api/v1/fibu/zahlungsbedingungen",
        row_route=None, bundle="finance", table_profile="financial",
        columns=[
            {"key": "zabd_nr", "label": "Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "bezeichnung", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "zahlungsziel_tage", "label": "Ziel (Tage)", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "skonto1_tage", "label": "Skonto 1 Tage", "numeric": True, "priority": "secondary"},
            {"key": "skonto1_prozent", "label": "Skonto 1 %", "numeric": True, "priority": "secondary"},
            {"key": "skonto2_tage", "label": "Skonto 2 Tage", "numeric": True, "priority": "tertiary"},
            {"key": "skonto2_prozent", "label": "Skonto 2 %", "numeric": True, "priority": "tertiary"},
            {"key": "zahlungsart", "label": "Zahlungsart", "filterable": True, "priority": "secondary"},
        ],
        actions=[
            {"key": "neu", "label": "Zahlungsbedingung anlegen", "kind": "primary", "dangerLevel": "safe",
             "zone": "header", "permission": "finance.zahlungsbedingung.create",
             "commandEndpoint": "/api/v1/fibu/zahlungsbedingungen", "method": "POST",
             "inputFields": [{"key": "zabd_nr", "label": "Nr.", "type": "text", "required": True}, *werte]},
            _EXPORT,
        ],
        row_actions=[
            {"key": "bearbeiten", "label": "Bearbeiten", "dangerLevel": "safe",
             "permission": "finance.zahlungsbedingung.update", "commandEndpoint": pfad + "bearbeiten",
             "method": "POST", "inputFields": werte},
            {"key": "deaktivieren", "label": "Deaktivieren", "dangerLevel": "moderate",
             "permission": "finance.zahlungsbedingung.deaktivieren", "commandEndpoint": pfad + "deaktivieren",
             "method": "POST", "requiresConfirmation": True, "auditReasonRequired": True},
        ],
        purpose="Zahlungsbedingungen fuer Kunden, Lieferanten und Belege pflegen.",
        prompts=["Welche Zahlungsbedingungen gewaehren 2 % Skonto?", "Lege 30 Tage netto, 10 Tage 2 % an."],
        no_workflow="Zahlungsbedingungen sind Referenzdaten ohne eigenen Ablauf.",
    )


def build_agrar_biostimulanzien_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/biostimulanzien-liste", domain="agrar", title="Biostimulanzien",
        subtitle="Agrarprodukte mit Zulassung und Bestand", endpoint="/api/v1/agrar/biostimulanzien",
        row_route="/agrar/biostimulanzien-stamm/{id}", bundle="agrar",
        columns=[
            {"key": "artikelnummer", "label": "Artikel-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "hersteller", "label": "Hersteller", "filterable": True, "priority": "secondary"},
            {"key": "vk_preis", "label": "VK-Preis", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "secondary"},
            {"key": "lagerbestand", "label": "Bestand", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "ist_aktiv", "label": "Aktiv", "renderKind": "boolean", "filterable": True, "priority": "tertiary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Biostimulanzien und Agrarprodukte mit Zulassung und Verfuegbarkeit finden.",
        prompts=["Welche Biostimulanzien sind aktiv?", "Welche Zulassungen laufen ab?"],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


def build_agrar_ernte_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/ernte-liste", domain="agrar", title="Ernte", subtitle="Ernten nach Schlag, Kultur und Menge",
        endpoint="/api/v1/agrar/ernte", row_route="/agrar/ernte/{id}", bundle="agrar",
        columns=[
            {"key": "schlag", "label": "Schlag", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kultur", "label": "Kultur", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "ertrag", "label": "Ertrag", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Ernte erfassen", "/agrar/ernte/neu"), _EXPORT],
        row_actions=[],
        purpose="Ernten nach Schlag und Kultur verfolgen.",
        prompts=["Welche Ernten laufen heute?", "Welche Schlaege sind abgeschlossen?"],
        no_workflow="Der Stand steht an der Ernte; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_agrar_kulturpflanzen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/kulturpflanzen-liste", domain="agrar", title="Kulturpflanzen",
        subtitle="Kulturen mit Flaeche, Ertrag und Deckungsbeitrag", endpoint="/api/v1/agrar/kulturen",
        row_route=None, bundle="agrar",
        columns=[
            {"key": "name", "label": "Kultur", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kategorie", "label": "Kategorie", "filterable": True, "priority": "primary"},
            {"key": "flaeche", "label": "Flaeche (ha)", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "ertrag", "label": "Ertrag", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "preis", "label": "Preis", "numeric": True, "renderKind": "currency", "priority": "secondary"},
            {"key": "deckungsbeitrag", "label": "DB", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Kulturen nach Flaeche und Deckungsbeitrag vergleichen.",
        prompts=["Welche Kulturen haben den hoechsten Deckungsbeitrag?", "Wie viel Flaeche ist Weizen?"],
        no_workflow="Auswertungsliste ohne eigenen Ablauf.",
    )


def build_zertifikate_liste() -> dict[str, Any]:
    return _liste(
        screen_id="zertifikate/liste", domain="qualitaet", title="Zertifikate",
        subtitle="Zertifikate mit Standard, Nummer und Gueltigkeit", endpoint="/api/v1/zertifikate", row_route=None,
        bundle="qualitaet",
        columns=[
            {"key": "art", "label": "Art", "filterable": True, "priority": "primary"},
            {"key": "standard", "label": "Standard", "filterable": True, "priority": "primary"},
            {"key": "nummer", "label": "Nummer", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "gueltigBis", "label": "Gueltig bis", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "audit", "label": "Audit", "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Zertifikate und ablaufende Nachweise im Blick behalten.",
        prompts=["Welche Zertifikate laufen dieses Quartal ab?", "Welche QS-Nachweise sind gueltig?"],
        no_workflow="Nachweisliste ohne eigenen Ablauf.",
    )


def build_benachrichtigungen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="benachrichtigungen/liste", domain="platform", title="Benachrichtigungen",
        subtitle="System- und Prozesshinweise — Lesestatus nur bis zum Verlassen dieser Ansicht", endpoint="/api/v1/benachrichtigungen", row_route=None,
        bundle="platform",
        columns=[
            {"key": "titel", "label": "Titel", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "nachricht", "label": "Nachricht", "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "secondary"},
            {"key": "zeitstempel", "label": "Zeit", "renderKind": "datetime", "sortable": True, "priority": "primary"},
            {"key": "gelesen", "label": "Gelesen", "renderKind": "boolean", "filterable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[{
            "key": "mark_read_local", "label": "Als gelesen markieren",
            "localEffect": "view", "readOnly": True, "dangerLevel": "safe",
            "visibleWhen": {"field": "gelesen", "values": [False]},
            "localRowPatch": {"identityField": "id", "field": "gelesen", "value": True},
        }],
        purpose="Offene Hinweise und Warnungen sichten.",
        prompts=["Welche Warnungen sind ungelesen?", "Was ist heute eingegangen?"],
        no_workflow="Posteingang ohne eigenen Ablauf.",
    )


def build_qualitaet_labor_liste() -> dict[str, Any]:
    return _liste(
        screen_id="qualitaet/labor-liste", domain="qualitaet", title="Laborauftraege",
        subtitle="Laborauftraege zu Chargen und Analysen", endpoint="/api/v1/qualitaet/labor-auftraege",
        row_route="/qualitaet/labor-auftrag/{id}", bundle="qualitaet",
        columns=[
            {"key": "id", "label": "Auftrag", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "chargenId", "label": "Charge", "filterable": True, "priority": "primary"},
            {"key": "labor", "label": "Labor", "filterable": True, "priority": "secondary"},
            {"key": "analysen", "label": "Analysen", "numeric": True, "priority": "secondary"},
            {"key": "auftragsdatum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Laborauftrag anlegen", "/qualitaet/labor-auftrag"), _EXPORT],
        row_actions=[],
        purpose="Laborauftraege und Befunde nachverfolgen.",
        prompts=["Welche Laborauftraege sind offen?", "Welche Charge wartet auf Befund?"],
        no_workflow="Der Stand steht am Laborauftrag; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_disposition_liste() -> dict[str, Any]:
    return _liste(
        screen_id="disposition/liste", domain="lager", title="Disposition",
        subtitle="Bestand, Mindestbestand und Beschaffungsempfehlung", endpoint="/api/v1/disposition",
        row_route=None, bundle="lager",
        columns=[
            {"key": "artikel", "label": "Artikel", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "bestand", "label": "Bestand", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "mindestbestand", "label": "Mindest", "numeric": True, "priority": "secondary"},
            {"key": "bedarf", "label": "Bedarf", "numeric": True, "priority": "secondary"},
            {"key": "empfehlung", "label": "Empfehlung", "filterable": True, "priority": "primary"},
            {"key": "prioritaet", "label": "Prioritaet", "renderKind": "status", "filterable": True,
             "priority": "primary"},
        ],
        actions=[_neu("Bestellvorschlaege", "/einkauf/bestellvorschlaege"), _EXPORT],
        row_actions=[],
        purpose="Unterdeckte Artikel finden und Bestellvorschlaege ausloesen.",
        prompts=["Welche Artikel liegen unter Mindestbestand?", "Wo ist Bedarf hoch?"],
        no_workflow="Empfehlungsliste ohne eigenen Ablauf.",
    )


def build_crm_kontakte_liste() -> dict[str, Any]:
    return _liste(
        screen_id="crm/kontakte-liste", domain="crm", title="Kontakte",
        subtitle="Kontakte zu Kunden, Lieferanten und Landwirten", endpoint="/api/v1/crm/contacts",
        row_route="/crm/kontakt/{id}", bundle="crm",
        columns=[
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "company", "label": "Unternehmen", "filterable": True, "priority": "primary"},
            {"key": "email", "label": "E-Mail", "filterable": True, "priority": "secondary"},
            {"key": "phone", "label": "Telefon", "priority": "tertiary"},
            {"key": "type", "label": "Typ", "filterable": True, "priority": "secondary"},
        ],
        actions=[_neu("Neuer Kontakt", "/crm/kontakt/neu"), _EXPORT],
        row_actions=[],
        purpose="Kontakte finden und die Kontaktakte oeffnen.",
        prompts=["Welche Kontakte gehoeren zu diesem Kunden?", "Zeige Lieferanten-Kontakte."],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


def build_crm_betriebsprofile_liste() -> dict[str, Any]:
    return _liste(
        screen_id="crm/betriebsprofile-liste", domain="crm", title="Betriebsprofile",
        subtitle="Landwirtschaftliche Betriebe mit Flaeche und Zertifizierung",
        endpoint="/api/v1/crm/betriebsprofile", row_route="/crm/betriebsprofile/{id}", bundle="crm",
        columns=[
            {"key": "farmName", "label": "Betrieb", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "owner", "label": "Inhaber", "filterable": True, "priority": "primary"},
            {"key": "totalArea", "label": "Flaeche (ha)", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "createdAt", "label": "Angelegt", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[_neu("Neues Betriebsprofil", "/crm/betriebsprofile/neu"), _EXPORT],
        row_actions=[],
        purpose="Betriebsprofile fuer Agrarberatung und CRM finden.",
        prompts=["Welche Betriebe haben mehr als 200 ha?", "Zeige Betriebe mit Bio-Zertifikat."],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


def build_sales_angebote_liste() -> dict[str, Any]:
    return _liste(
        screen_id="sales/angebote-liste", domain="sales", title="Verkaufsangebote",
        subtitle="Angebote mit Kunde, Betrag und Gueltigkeit", endpoint="/api/v1/sales/offers/",
        row_route="/sales/angebot/{id}", bundle="sales",
        columns=[
            {"key": "offer_number", "label": "Angebot-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "customer_name", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "subject", "label": "Betreff", "filterable": True, "priority": "secondary"},
            {"key": "total_amount", "label": "Betrag", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "primary"},
            {"key": "valid_until", "label": "Gueltig bis", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Neues Angebot", "/sales/angebot/neu"), _EXPORT],
        row_actions=[],
        purpose="Verkaufsangebote nach Kunde und Status verfolgen.",
        prompts=["Welche Angebote laufen diese Woche ab?", "Welche Angebote sind offen?"],
        no_workflow="Der Status steht am Angebot; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_sales_auftraege_liste() -> dict[str, Any]:
    return _liste(
        screen_id="sales/auftraege-liste", domain="sales", title="Verkaufsauftraege",
        subtitle="Auftraege mit Kunde, Betrag und Lieferstatus", endpoint="/api/v1/sales/orders/",
        row_route="/sales/sales-order/{id}", bundle="sales",
        columns=[
            {"key": "order_number", "label": "Auftrag-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "customer_name", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "subject", "label": "Betreff", "filterable": True, "priority": "secondary"},
            {"key": "total_amount", "label": "Betrag", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "primary"},
            {"key": "delivery_date", "label": "Liefertermin", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Neuer Auftrag", "/sales/order-editor"), _EXPORT],
        row_actions=[],
        purpose="Verkaufsauftraege nach Kunde und Lieferstatus steuern.",
        prompts=["Welche Auftraege sind noch offen?", "Welche Auftraege warten auf Lieferung?"],
        no_workflow="Der Status steht am Auftrag; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_sales_lieferungen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="sales/lieferungen-liste", domain="sales", title="Lieferscheine",
        subtitle="Ausgehende Lieferungen und Versandstatus", endpoint="/api/v1/sales/delivery-notes",
        row_route="/sales/delivery-note/{id}", bundle="sales",
        columns=[
            {"key": "delivery_number", "label": "Lieferschein-Nr.", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "customer_name", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "delivery_date", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "shipping_method", "label": "Versandart", "filterable": True, "priority": "tertiary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Lieferschein erfassen", "/sales/delivery-editor"), _EXPORT],
        row_actions=[],
        purpose="Lieferscheine und Versandstatus nachverfolgen.",
        prompts=["Welche Lieferscheine sind heute offen?", "Welche Lieferungen sind unterwegs?"],
        no_workflow="Der Status steht am Lieferschein; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_einkauf_rechnungseingaenge_liste() -> dict[str, Any]:
    pfad = "/api/v1/einkauf/rechnungseingaenge/{entity_id}/"
    return _liste(
        screen_id="einkauf/rechnungseingaenge-liste", domain="einkauf", title="Rechnungseingaenge",
        subtitle="Eingangsrechnungen vor Freigabe und Verbuchung", endpoint="/api/v1/einkauf/rechnungseingaenge",
        row_route="/belege/purchase_invoice/{id}", bundle="einkauf",
        columns=[
            {"key": "rechnungsNummer", "label": "Rechnung-Nr.", "sortable": True, "filterable": True,
             "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "rechnungsDatum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "bruttoBetrag", "label": "Betrag", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Rechnungseingang erfassen", "/einkauf/rechnungseingang/neu"), _EXPORT],
        row_actions=[
            {"key": "pruefen", "label": "Pruefen", "dangerLevel": "safe", "permission": "einkauf.rechnungseingang.pruefen",
             "commandEndpoint": pfad + "pruefen", "method": "POST", "requiresConfirmation": True,
             "visibleWhen": _status("OFFEN", "ERFASST", "ENTWURF")},
            {"key": "freigeben", "label": "Freigeben", "dangerLevel": "moderate",
             "permission": "einkauf.rechnungseingang.freigeben", "commandEndpoint": pfad + "freigeben", "method": "POST",
             "requiresConfirmation": True, "humanApprovalRequired": True, "forbiddenForAgents": True,
             "visibleWhen": _status("GEPRUEFT", "OFFEN")},
            {"key": "verbuchen", "label": "Verbuchen", "dangerLevel": "high", "permission": "einkauf.rechnungseingang.verbuchen",
             "commandEndpoint": pfad + "verbuchen", "method": "POST", "requiresConfirmation": True,
             "auditReasonRequired": True, "forbiddenForAgents": True,
             "visibleWhen": _status("FREIGEGEBEN", "GEPRUEFT")},
        ],
        dangerous=[
            {"key": "freigeben", "reason": "Gibt eine Eingangsrechnung zur Verbuchung frei; nur Mensch."},
            {"key": "verbuchen", "reason": "Verbucht eine Eingangsrechnung in der FIBU; nur Mensch mit Begruendung."},
        ],
        purpose="Eingangsrechnungen vor Pruefung und Verbuchung finden.",
        prompts=["Welche Rechnungen warten auf Freigabe?", "Welche Eingangsrechnungen sind offen?"],
        no_workflow="Der Status steht an der Rechnung; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_service_anfragen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="service/anfragen-liste", domain="service", title="Serviceanfragen",
        subtitle="Tickets mit Kunde, Prioritaet und Bearbeitungsstand", endpoint="/api/v1/service/anfragen",
        row_route="/service/anfrage/{id}", bundle="service",
        columns=[
            {"key": "nummer", "label": "Ticket-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kunde", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "betreff", "label": "Betreff", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "prioritaet", "label": "Prioritaet", "renderKind": "status", "filterable": True,
             "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Neue Anfrage", "/service/anfrage-neu"), _EXPORT],
        row_actions=[],
        purpose="Service-Tickets nach Prioritaet und Status abarbeiten.",
        prompts=["Welche Tickets sind hoch priorisiert?", "Was ist heute neu eingegangen?"],
        no_workflow="Der Stand steht an der Anfrage; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_compliance_enni_meldungen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/enni-meldungen-liste", domain="compliance", title="ENNI-Meldungen",
        subtitle="Duenge-Meldungen mit VVVO und Naehrstoffen",         endpoint="/api/v1/compliance/enni-meldungen",
        row_route=None, bundle="compliance",
        columns=[
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "betrieb", "label": "Betrieb", "filterable": True, "priority": "primary"},
            {"key": "vvvo", "label": "VVVO", "filterable": True, "priority": "secondary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Neue Meldung", "/compliance/enni-neu"), _EXPORT],
        row_actions=[],
        purpose="ENNI-Meldungen und offene Entwuerfe verfolgen.",
        prompts=["Welche Meldungen sind noch Entwurf?", "Welche VVVO-Meldungen sind faellig?"],
        no_workflow="Der Status steht an der Meldung; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_qualitaet_reklamationen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="qualitaet/reklamationen-liste", domain="qualitaet", title="Reklamationen",
        subtitle="Beanstandungen mit Kunde, Artikel und Prioritaet", endpoint="/api/v1/qualitaet/reklamationen",
        row_route="/qualitaet/reklamation/{id}", bundle="qualitaet",
        columns=[
            {"key": "nummer", "label": "Reklamation-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kunde", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "secondary"},
            {"key": "grund", "label": "Grund", "filterable": True, "priority": "secondary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "prioritaet", "label": "Prioritaet", "renderKind": "status", "filterable": True,
             "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Neue Reklamation", "/qualitaet/reklamation/neu"), _EXPORT],
        row_actions=[],
        purpose="Reklamationen nach Prioritaet und Bearbeitungsstand steuern.",
        prompts=["Welche Reklamationen sind offen?", "Welche Faelle sind hoch priorisiert?"],
        no_workflow="Der Stand steht an der Reklamation; die Liste fuehrt keinen eigenen Ablauf.",
    )


def build_crm_leads_liste() -> dict[str, Any]:
    return _liste(
        screen_id="crm/leads-liste", domain="crm", title="Leads", subtitle="Vertriebs-Leads und Qualifizierung",
        endpoint="/api/v1/crm/leads", row_route="/crm/leads/{id}", bundle="crm",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_neu("Neu", "/crm/leads/neu"), _EXPORT],
        row_actions=[],
        purpose="Leads: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Leads?", "Zeige aktuelle Leads."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_crm_aktivitaeten_liste() -> dict[str, Any]:
    return _liste(
        screen_id="crm/aktivitaeten-liste", domain="crm", title="Aktivitaeten", subtitle="Kontakte, Termine und Follow-ups",
        endpoint="/api/v1/crm/activities", row_route="/crm/aktivitaeten/{id}", bundle="crm",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Aktivitaeten: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Aktivitaeten?", "Zeige aktuelle Aktivitaeten."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_fibu_buchungsjournal_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/buchungsjournal-liste", domain="finance", title="Buchungsjournal", subtitle="Journalbuchungen und Belegnummern",
        endpoint="/api/v1/journal-entries/", row_route="/fibu/buchungsjournal/{id}", bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Buchungsjournal: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Buchungsjournal?", "Zeige aktuelle Buchungsjournal."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_fibu_offene_posten_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/offene-posten-liste", domain="finance", title="Offene Posten", subtitle="Forderungen und Verbindlichkeiten offen",
        endpoint="/api/v1/finance/open-items", row_route=None, bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Offene Posten: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Offene Posten?", "Zeige aktuelle Offene Posten."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_fibu_zahlungslaeufe_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/zahlungslaeufe-liste", domain="finance", title="Zahlungslaeufe", subtitle="SEPA-Laeufe und Freigaben",
        endpoint="/api/v1/finance/payment-runs", row_route="/fibu/zahlungslaeufe/{id}", bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Zahlungslaeufe: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Zahlungslaeufe?", "Zeige aktuelle Zahlungslaeufe."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_fibu_kostenstellen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/kostenstellen-liste", domain="finance", title="Kostenstellen", subtitle="Kostenstellen und Zuordnungen",
        endpoint="/api/v1/finance/kostenstellen", row_route=None, bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Kostenstellen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Kostenstellen?", "Zeige aktuelle Kostenstellen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_fibu_zahlungseingaenge_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/zahlungseingaenge-liste", domain="finance", title="Zahlungseingaenge", subtitle="Bankkonten und Eingaenge",
        endpoint="/api/v1/finance/bank-accounts", row_route=None, bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Zahlungseingaenge: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Zahlungseingaenge?", "Zeige aktuelle Zahlungseingaenge."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_fibu_kontenplan_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/kontenplan-liste", domain="finance", title="Kontenplan", subtitle="Sachkonten und Kontenklassen",
        endpoint="/api/v1/finance/chart-of-accounts/", row_route=None, bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Kontenplan: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Kontenplan?", "Zeige aktuelle Kontenplan."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_genossenschaft_mitglieder_liste() -> dict[str, Any]:
    return _liste(
        screen_id="genossenschaft/mitglieder-liste", domain="genossenschaft", title="Mitglieder", subtitle="Genossenschaftsmitglieder und Anteile",
        endpoint="/api/v1/genossenschaft/mitglieder", row_route="/genossenschaft/mitglieder/{id}", bundle="genossenschaft",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Mitglieder: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Mitglieder?", "Zeige aktuelle Mitglieder."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_kontrakte_kontraktklassen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="kontrakte/kontraktklassen-liste", domain="agrar", title="Kontraktklassen", subtitle="Klassen fuer Kontraktarten",
        endpoint="/api/v1/kontrakt-klassen", row_route=None, bundle="agrar",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Kontraktklassen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Kontraktklassen?", "Zeige aktuelle Kontraktklassen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_kontrakte_liste() -> dict[str, Any]:
    return _liste(
        screen_id="kontrakte/liste", domain="agrar", title="Kontrakte", subtitle="Einkaufs- und Verkaufskontrakte",
        endpoint="/api/v1/kontrakte", row_route="/kontrakte/{id}", bundle="agrar",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_neu("Neuer Kontrakt", "/kontrakte/neu"), _EXPORT],
        row_actions=[],
        purpose="Kontrakte: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Kontrakte?", "Zeige aktuelle Kontrakte."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_lager_lagerbewegungen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="lager/lagerbewegungen-liste", domain="lager", title="Lagerbewegungen", subtitle="Zugaenge, Abgaenge und Umbuchungen",
        endpoint="/api/v1/inventory/stock-movements/", row_route="/lager/lagerbewegungen/{id}", bundle="lager",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Lagerbewegungen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Lagerbewegungen?", "Zeige aktuelle Lagerbewegungen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_lager_inventur_liste() -> dict[str, Any]:
    return _liste(
        screen_id="lager/inventur-liste", domain="lager", title="Inventur", subtitle="Inventurpositionen und Differenzen",
        endpoint="/api/v1/inventory/inventur", row_route=None, bundle="lager",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Inventur: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Inventur?", "Zeige aktuelle Inventur."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_lager_partiestamm_liste() -> dict[str, Any]:
    return _liste(
        screen_id="lager/partiestamm-liste", domain="lager", title="Partiestamm", subtitle="Partien und Chargenstamm",
        endpoint="/api/v1/lager/partien", row_route="/lager/partiestamm/{id}", bundle="lager",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Partiestamm: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Partiestamm?", "Zeige aktuelle Partiestamm."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_lager_silo_uebersicht_liste() -> dict[str, Any]:
    return _liste(
        screen_id="lager/silo-uebersicht-liste", domain="lager", title="Silo-Uebersicht", subtitle="Silozellen und Fuellstaende",
        endpoint="/api/v1/lager/wms/agri/silo-cells", row_route=None, bundle="lager",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Silo-Uebersicht: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Silo-Uebersicht?", "Zeige aktuelle Silo-Uebersicht."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_qualitaet_ausnahmen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="qualitaet/ausnahmen-liste", domain="qualitaet", title="Betriebsausnahmen", subtitle="Prozess- und Systemausnahmen",
        endpoint="/api/v1/operations/exceptions", row_route=None, bundle="qualitaet",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Betriebsausnahmen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Betriebsausnahmen?", "Zeige aktuelle Betriebsausnahmen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_transporte_fahrer_liste() -> dict[str, Any]:
    return _liste(
        screen_id="transporte/fahrer-liste", domain="logistik", title="Fahrer", subtitle="Fahrerstamm fuer Transporte",
        endpoint="/api/v1/transporte/fahrer", row_route="/transporte/fahrer/{id}", bundle="logistik",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Fahrer: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Fahrer?", "Zeige aktuelle Fahrer."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_einkauf_bestellvorschlaege_liste() -> dict[str, Any]:
    return _liste(
        screen_id="einkauf/bestellvorschlaege-liste", domain="einkauf", title="Bestellvorschlaege", subtitle="Bedarf aus Lager und Verkauf",
        endpoint="/api/v1/einkauf/bestellvorschlaege", row_route=None, bundle="einkauf",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Bestellvorschlaege: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Bestellvorschlaege?", "Zeige aktuelle Bestellvorschlaege."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_einkauf_frachtauftraege_liste() -> dict[str, Any]:
    return _liste(
        screen_id="einkauf/frachtauftraege-liste", domain="einkauf", title="Frachtauftraege", subtitle="Fracht zu Einkaufslieferscheinen",
        endpoint="/api/v1/einkauf/frachtauftraege", row_route=None, bundle="einkauf",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Frachtauftraege: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Frachtauftraege?", "Zeige aktuelle Frachtauftraege."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_compliance_intrastat_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/intrastat-liste", domain="compliance", title="Intrastat", subtitle="Intrastat-Meldungen",
        endpoint="/api/v1/intrastat/meldungen", row_route=None, bundle="compliance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Intrastat: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Intrastat?", "Zeige aktuelle Intrastat."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_compliance_gelangensbestaetigung_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/gelangensbestaetigung-liste", domain="compliance", title="Gelangensbestaetigungen", subtitle="Gelangensnachweise fuer innergemeinschaftliche Lieferungen",
        endpoint="/api/v1/gelangensbestaetigung", row_route=None, bundle="compliance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Gelangensbestaetigungen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Gelangensbestaetigungen?", "Zeige aktuelle Gelangensbestaetigungen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_compliance_lksg_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/lksg-liste", domain="compliance", title="LKSG Lieferanten", subtitle="Lieferanten-Risikobewertungen LKSG",
        endpoint="/api/v1/compliance/lksg/supplier-risk-assessments", row_route=None, bundle="compliance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="LKSG Lieferanten: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen LKSG Lieferanten?", "Zeige aktuelle LKSG Lieferanten."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_compliance_qs_checkliste_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/qs-checkliste-liste", domain="compliance", title="QS-Checkliste", subtitle="QS-Pruefpunkte und Nachweise",
        endpoint="/api/v1/compliance/qs-checkliste", row_route=None, bundle="compliance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="QS-Checkliste: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen QS-Checkliste?", "Zeige aktuelle QS-Checkliste."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_admin_audit_log_liste() -> dict[str, Any]:
    return _liste(
        screen_id="admin/audit-log-liste", domain="admin", title="Audit-Log", subtitle="System-Aktivitaeten und Aenderungen",
        endpoint="/api/v1/admin/audit-log", row_route=None, bundle="admin",
        columns=[
            {"key": "zeitstempel", "label": "Zeitstempel", "sortable": True, "priority": "primary"},
            {"key": "benutzer", "label": "Benutzer", "filterable": True, "priority": "primary"},
            {"key": "aktion", "label": "Aktion", "filterable": True, "priority": "secondary"},
            {"key": "objekt", "label": "Objekt", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Audit-Ereignisse nachvollziehen und exportieren.",
        prompts=["Welche Aenderungen gab es heute?", "Wer hat den Datensatz geaendert?"],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_admin_webhooks_liste() -> dict[str, Any]:
    return _liste(
        screen_id="admin/webhooks-liste", domain="admin", title="Webhooks", subtitle="Webhook-Endpunkte und Bereiche",
        endpoint="/api/v1/webhooks", row_route=None, bundle="admin",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Webhooks: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Webhooks?", "Zeige aktuelle Webhooks."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_finance_audit_trail_liste() -> dict[str, Any]:
    return _liste(
        screen_id="finance/audit-trail-liste", domain="finance", title="Audit-Trail", subtitle="Pruefpfad fuer Finanzbelege",
        endpoint="/api/v1/audit/logs", row_route=None, bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Audit-Trail: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Audit-Trail?", "Zeige aktuelle Audit-Trail."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_finance_ap_invoices_liste() -> dict[str, Any]:
    return _liste(
        screen_id="finance/ap-invoices-liste", domain="finance", title="AP-Rechnungen", subtitle="Eingangsrechnungen zur Freigabe",
        endpoint="/api/v1/finance/ap/invoices/", row_route="/belege/purchase_invoice/{id}", bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="AP-Rechnungen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen AP-Rechnungen?", "Zeige aktuelle AP-Rechnungen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_finance_payment_matching_liste() -> dict[str, Any]:
    return _liste(
        screen_id="finance/payment-matching-liste", domain="finance", title="Zahlungsabgleich", subtitle="Unzugeordnete Zahlungen",
        endpoint="/api/v1/finance/payments/unmatched", row_route=None, bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Zahlungsabgleich: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Zahlungsabgleich?", "Zeige aktuelle Zahlungsabgleich."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_finance_periods_liste() -> dict[str, Any]:
    return _liste(
        screen_id="finance/periods-liste", domain="finance", title="Buchungsperioden", subtitle="Offene und geschlossene Perioden",
        endpoint="/api/v1/finance/periods/", row_route=None, bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Buchungsperioden: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Buchungsperioden?", "Zeige aktuelle Buchungsperioden."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_finance_skonto_optimizer_liste() -> dict[str, Any]:
    return _liste(
        screen_id="finance/skonto-optimizer-liste", domain="finance", title="Skonto-Optimierung", subtitle="Skontofaehige offene Posten",
        endpoint="/api/v1/finance/open-items", row_route=None, bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Skonto-Optimierung: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Skonto-Optimierung?", "Zeige aktuelle Skonto-Optimierung."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_agrar_saatzucht_partien_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/saatzucht-partien-liste", domain="agrar", title="Saatzucht-Partien", subtitle="Partien in der Saatzucht",
        endpoint="/api/v1/saatzucht/partien", row_route=None, bundle="agrar",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Saatzucht-Partien: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Saatzucht-Partien?", "Zeige aktuelle Saatzucht-Partien."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_agrar_vermehrungsvertraege_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/vermehrungsvertraege-liste", domain="agrar", title="Vermehrungsvertraege", subtitle="Saatzucht-Vermehrungsvertraege",
        endpoint="/api/v1/saatzucht/vermehrungsvertraege", row_route=None, bundle="agrar",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Vermehrungsvertraege: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Vermehrungsvertraege?", "Zeige aktuelle Vermehrungsvertraege."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_agrar_feldbuch_massnahmen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/feldbuch-massnahmen-liste", domain="agrar", title="Feldbuch-Massnahmen", subtitle="Massnahmen je Schlag",
        endpoint="/api/v1/agrar/feldbuch/massnahmen", row_route=None, bundle="agrar",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Feldbuch-Massnahmen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Feldbuch-Massnahmen?", "Zeige aktuelle Feldbuch-Massnahmen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_agrar_feldbuch_schlagkartei_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/feldbuch-schlagkartei-liste", domain="agrar", title="Schlagkartei", subtitle="Schlaege und Flaechen",
        endpoint="/api/v1/agrar/schlaege", row_route="/agrar/feldbuch/schlag/{id}", bundle="agrar",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Schlagkartei: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Schlagkartei?", "Zeige aktuelle Schlagkartei."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_banken_konten_liste() -> dict[str, Any]:
    return _liste(
        screen_id="banken/konten-liste", domain="finance", title="Bankkonten", subtitle="Hausbanken und Konten",
        endpoint="/api/v1/banken/konten", row_route=None, bundle="finance",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Bankkonten: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Bankkonten?", "Zeige aktuelle Bankkonten."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_personal_zeiterfassung_liste() -> dict[str, Any]:
    return _liste(
        screen_id="personal/zeiterfassung-liste", domain="personal", title="Zeiterfassung", subtitle="Erfasste Arbeitszeiten",
        endpoint="/api/v1/personal/zeiterfassung", row_route=None, bundle="personal",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Zeiterfassung: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Zeiterfassung?", "Zeige aktuelle Zeiterfassung."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_tankstelle_zapfungen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="tankstelle/zapfungen-liste", domain="lager", title="Zapfungen", subtitle="Tankstellen-Zapfvorgaenge",
        endpoint="/api/v1/tankstelle/zapfungen", row_route=None, bundle="lager",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Zapfungen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Zapfungen?", "Zeige aktuelle Zapfungen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_verladung_liste() -> dict[str, Any]:
    return _liste(
        screen_id="verladung/liste", domain="logistik", title="Verladungen", subtitle="Verladungen und Rampen",
        endpoint="/api/v1/verladung", row_route="/verladung/{id}", bundle="logistik",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Verladungen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Verladungen?", "Zeige aktuelle Verladungen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_waage_hofliste_liste() -> dict[str, Any]:
    return _liste(
        screen_id="waage/hofliste", domain="agrar", title="Hofliste Waage", subtitle="Warteschlange und Annahmen am Hof",
        endpoint="/api/v1/waage/hofliste", row_route=None, bundle="agrar",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Hofliste Waage: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Hofliste Waage?", "Zeige aktuelle Hofliste Waage."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_waage_waagen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="waage/waagen-liste", domain="agrar", title="Waagen", subtitle="Waagenstamm und Eichung",
        endpoint="/api/v1/waage/waagen", row_route="/waage/{id}", bundle="agrar",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Waagen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Waagen?", "Zeige aktuelle Waagen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_fuhrpark_rechnungen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fuhrpark/rechnungen-liste", domain="logistik", title="Fuhrpark-Rechnungen", subtitle="Rechnungen zum Fuhrpark",
        endpoint="/api/v1/fuhrpark/rechnungen", row_route=None, bundle="logistik",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Fuhrpark-Rechnungen: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Fuhrpark-Rechnungen?", "Zeige aktuelle Fuhrpark-Rechnungen."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_fuhrpark_fahrzeuge_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fuhrpark/fahrzeuge-liste", domain="logistik", title="Fuhrpark", subtitle="Fahrzeuge und Status",
        endpoint="/api/v1/fuhrpark/fahrzeuge", row_route="/fuhrpark/fahrzeug/{id}", bundle="logistik",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Fuhrpark: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Fuhrpark?", "Zeige aktuelle Fuhrpark."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_waage_wiegungen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="waage/wiegungen-liste", domain="agrar", title="Wiegescheine", subtitle="Waagen-Wiegescheine",
        endpoint="/api/v1/weighing-tickets/", row_route="/waage/wiegeschein/{id}", bundle="agrar",
        columns=[
            {"key": "id", "label": "ID", "filterable": True, "priority": "secondary"},
            {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Wiegescheine: Eintraege finden und Details oeffnen.",
        prompts=["Welche offenen Wiegescheine?", "Zeige aktuelle Wiegescheine."],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )

def build_marketing_kampagnen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="marketing/kampagnen-liste", domain="marketing", title="Marketingkampagnen",
        subtitle="Kampagnen mit Zielgruppe, Budget und Laufzeit",         endpoint="/api/v1/marketing/kampagnen",
        row_route="/marketing/kampagne/{id}", bundle="marketing",
        columns=[
            {"key": "name", "label": "Kampagne", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "zielgruppe", "label": "Zielgruppe", "filterable": True, "priority": "secondary"},
            {"key": "startdatum", "label": "Start", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "enddatum", "label": "Ende", "renderKind": "date", "sortable": True, "priority": "tertiary"},
            {"key": "budget", "label": "Budget", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Neue Kampagne", "/marketing/kampagne/neu"), _EXPORT],
        row_actions=[],
        purpose="Marketingkampagnen und Budgets verfolgen.",
        prompts=["Welche Kampagnen laufen gerade?", "Welches Budget ist fuer Q2 geplant?"],
        no_workflow="Kampagnenliste ohne eigenen Ablauf.",
    )


def build_crm_kunden_liste() -> dict[str, Any]:
    return _liste(
        screen_id="crm/kunden-liste", domain="crm", title="Kunden",
        subtitle="Operativer Kundenstamm mit Umsatz und Status",
        endpoint="/api/v1/crm/customers/lookup?q=&limit=1000", row_route="/crm/kunden/{id}", bundle="crm",
        columns=[
            {"key": "name", "label": "Firma / Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kunden_nr", "label": "Kunden-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "ort", "label": "Ort", "filterable": True, "priority": "secondary"},
            {"key": "plz", "label": "PLZ", "filterable": True, "priority": "tertiary"},
            {"key": "telefon", "label": "Telefon", "priority": "tertiary"},
            {"key": "email", "label": "E-Mail", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Neuer Kunde", "/verkauf/kunde/neu"), _EXPORT],
        row_actions=[],
        purpose="Kunden im operativen Stamm finden und die Kundenakte oeffnen.",
        prompts=["Welche Kunden sind in Hamburg?", "Zeige gesperrte Kunden."],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


def build_crm_lieferanten_liste() -> dict[str, Any]:
    return _liste(
        screen_id="crm/lieferanten-liste", domain="crm", title="Lieferanten",
        subtitle="Lieferanten und Einkaufskonditionen", endpoint="/api/v1/crm/suppliers",
        row_route="/crm/lieferanten/{id}", bundle="crm",
        columns=[
            {"key": "firma", "label": "Firma", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "ort", "label": "Ort", "filterable": True, "priority": "secondary"},
            {"key": "plz", "label": "PLZ", "filterable": True, "priority": "tertiary"},
            {"key": "email", "label": "E-Mail", "filterable": True, "priority": "secondary"},
            {"key": "zahlungsbedingungen", "label": "Zahlungsbedingungen", "priority": "tertiary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_neu("Neuer Lieferant", "/crm/lieferanten/stamm/new"), _EXPORT],
        row_actions=[],
        purpose="Lieferanten finden und Stammdaten oeffnen.",
        prompts=["Welche Lieferanten sind aktiv?", "Zeige Lieferanten mit Skonto."],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


def build_banken_konten_liste() -> dict[str, Any]:
    return _liste(
        screen_id="banken/konten-liste", domain="finance", title="Bankkonten",
        subtitle="Hausbankkonten mit Saldo und Status", endpoint="/api/v1/banken/konten",
        row_route="/finance/bankkonto/{id}", bundle="finance", table_profile="financial",
        columns=[
            {"key": "iban", "label": "IBAN", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "bank", "label": "Bank", "filterable": True, "priority": "primary"},
            {"key": "kontoart", "label": "Kontoart", "filterable": True, "priority": "secondary"},
            {"key": "saldo", "label": "Saldo", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Bankkonten und Salden im Blick behalten.",
        prompts=["Welches Konto hat den hoechsten Saldo?", "Welche Konten sind inaktiv?"],
        no_workflow="Kontenliste ohne eigenen Ablauf.",
    )


def build_dokumente_ablage_liste() -> dict[str, Any]:
    return _liste(
        screen_id="dokumente/ablage-liste", domain="dms", title="Dokumentenablage",
        subtitle="Dokumente nach Kategorie und Typ", endpoint="/api/v1/dokumente", row_route=None, bundle="dms",
        columns=[
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "kategorie", "label": "Kategorie", "filterable": True, "priority": "secondary"},
            {"key": "groesse", "label": "Groesse", "numeric": True, "priority": "tertiary"},
            {"key": "hochgeladen", "label": "Hochgeladen", "renderKind": "datetime", "sortable": True,
             "priority": "secondary"},
            {"key": "benutzer", "label": "Benutzer", "filterable": True, "priority": "tertiary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Dokumente in der Ablage finden und herunterladen.",
        prompts=["Welche Dokumente wurden heute hochgeladen?", "Zeige Vertraege in der Ablage."],
        no_workflow="DMS-Ablage ohne eigenen Ablauf.",
    )


def build_vertrag_rahmenvertraege_liste() -> dict[str, Any]:
    return _liste(
        screen_id="vertrag/rahmenvertraege-liste", domain="agrar", title="Rahmenvertraege",
        subtitle="Kontraktuelle Rahmen mit Restmenge und Laufzeit", endpoint="/api/v1/vertrag/rahmenvertraege",
        row_route=None, bundle="agrar",
        columns=[
            {"key": "nummer", "label": "Vertrag-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "partner", "label": "Partner", "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "secondary"},
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "secondary"},
            {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "restmenge", "label": "Restmenge", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "laufzeitBis", "label": "Laufzeit bis", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Rahmenvertraege mit Restmenge und Laufzeit verfolgen.",
        prompts=["Welche Rahmenvertraege laufen aus?", "Welche Restmengen sind kritisch?"],
        no_workflow="Vertragsliste ohne eigenen Ablauf.",
    )


def build_tankstelle_zapfungen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="tankstelle/zapfungen-liste", domain="logistik", title="Zapfungen",
        subtitle="Tankstellen-Zapfungen mit Fahrer und Menge", endpoint="/api/v1/tankstelle/zapfungen",
        row_route=None, bundle="logistik",
        columns=[
            {"key": "kennzeichen", "label": "Kennzeichen", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "primary"},
            {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "fahrer", "label": "Fahrer", "filterable": True, "priority": "secondary"},
            {"key": "zeitstempel", "label": "Zeit", "renderKind": "datetime", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Zapfungen der Tankstelle nachvollziehen.",
        prompts=["Welche Zapfungen gab es heute?", "Welches Fahrzeug tankte Diesel?"],
        no_workflow="Buchungsliste ohne eigenen Ablauf.",
    )


def build_waage_liste() -> dict[str, Any]:
    return _liste(
        screen_id="waage/liste", domain="logistik", title="Waagen",
        subtitle="Standorte, Kapazitaet und Eichung", endpoint="/api/v1/waage/waagen", row_route=None, bundle="logistik",
        columns=[
            {"key": "standort", "label": "Standort", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "maxKapazitaet", "label": "Max. Kapazitaet", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "letzteEichung", "label": "Letzte Eichung", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "naechsteEichung", "label": "Naechste Eichung", "renderKind": "date", "sortable": True,
             "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Waagenstandorte und Eichtermine im Blick behalten.",
        prompts=["Welche Waage muss als naechstes geeicht werden?", "Welche Waagen sind in Wartung?"],
        no_workflow="Geraeteliste ohne eigenen Ablauf.",
    )


def build_compliance_cross_compliance_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/cross-compliance-liste", domain="compliance", title="Cross-Compliance",
        subtitle="Anforderungen und Nachweise je Bereich", endpoint="/api/v1/compliance/cross-compliance",
        row_route=None, bundle="compliance",
        columns=[
            {"key": "bereich", "label": "Bereich", "filterable": True, "priority": "primary"},
            {"key": "anforderung", "label": "Anforderung", "filterable": True, "priority": "primary"},
            {"key": "erfuellt", "label": "Erfuellt", "renderKind": "boolean", "filterable": True, "priority": "primary"},
            {"key": "nachweis", "label": "Nachweis", "priority": "secondary"},
            {"key": "frist", "label": "Frist", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Cross-Compliance-Anforderungen und offene Nachweise pruefen.",
        prompts=["Welche Anforderungen sind nicht erfuellt?", "Was ist diese Woche faellig?"],
        no_workflow="Checklisten-Register ohne eigenen Ablauf.",
    )


def build_compliance_zulassungen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/zulassungen-liste", domain="compliance", title="Zulassungsregister",
        subtitle="Produktzulassungen mit Behoerde und Gueltigkeit",
        endpoint="/api/v1/compliance/zulassungen-register", row_route=None, bundle="compliance",
        columns=[
            {"key": "produkt", "label": "Produkt", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "secondary"},
            {"key": "nummer", "label": "Nummer", "filterable": True, "priority": "primary"},
            {"key": "behoerde", "label": "Behoerde", "filterable": True, "priority": "secondary"},
            {"key": "gueltigBis", "label": "Gueltig bis", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Produktzulassungen und Ablaufdaten im Blick behalten.",
        prompts=["Welche Zulassungen laufen ab?", "Welche Produkte sind widerrufen?"],
        no_workflow="Registerliste ohne eigenen Ablauf.",
    )


def build_compliance_vvvo_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/vvvo-liste", domain="compliance", title="VVVO-Register",
        subtitle="Betriebe mit VVVO-Nummer und Tierart", endpoint="/api/v1/compliance/vvvo-register",
        row_route=None, bundle="compliance",
        columns=[
            {"key": "betriebsname", "label": "Betrieb", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "vvvo", "label": "VVVO", "filterable": True, "priority": "primary"},
            {"key": "bundesland", "label": "Bundesland", "filterable": True, "priority": "secondary"},
            {"key": "tierart", "label": "Tierart", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "letzteAktualisierung", "label": "Aktualisiert", "renderKind": "date", "sortable": True,
             "priority": "tertiary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="VVVO-registrierte Betriebe finden und pruefen.",
        prompts=["Welche Betriebe sind inaktiv?", "Zeige Betriebe in Niedersachsen."],
        no_workflow="Registerliste ohne eigenen Ablauf.",
    )


def build_compliance_sachkunde_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/sachkunde-liste", domain="compliance", title="Sachkundenachweise",
        subtitle="Nachweise mit Gueltigkeit und ausstellender Stelle",
        endpoint="/api/v1/compliance/sachkunde-register", row_route=None, bundle="compliance",
        columns=[
            {"key": "kunde", "label": "Kunde", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kundennr", "label": "Kunden-Nr.", "filterable": True, "priority": "secondary"},
            {"key": "nachweisNr", "label": "Nachweis-Nr.", "filterable": True, "priority": "primary"},
            {"key": "ausstellungsdatum", "label": "Ausgestellt", "renderKind": "date", "sortable": True,
             "priority": "secondary"},
            {"key": "gueltigBis", "label": "Gueltig bis", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Sachkundenachweise und Ablaufdaten verfolgen.",
        prompts=["Welche Nachweise laufen ab?", "Welche Kunden haben gueltige Sachkunde?"],
        no_workflow="Registerliste ohne eigenen Ablauf.",
    )


def build_compliance_saatgut_nachbau_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/saatgut-nachbau-liste", domain="compliance", title="Saatgut-Nachbau",
        subtitle="Nachbauflaechen und Gebuehren je Betrieb", endpoint="/api/v1/compliance/saatgut-nachbau",
        row_route=None, bundle="compliance",
        columns=[
            {"key": "betrieb", "label": "Betrieb", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "sorte", "label": "Sorte", "filterable": True, "priority": "primary"},
            {"key": "kultur", "label": "Kultur", "filterable": True, "priority": "secondary"},
            {"key": "flaeche", "label": "Flaeche (ha)", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "erntejahr", "label": "Erntejahr", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "gebuehr", "label": "Gebuehr", "numeric": True, "renderKind": "currency", "sortable": True,
             "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Saatgut-Nachbauflaechen und offene Gebuehren verfolgen.",
        prompts=["Welche Nachbaugebuehren sind offen?", "Welche Sorten wurden nachgebaut?"],
        no_workflow="Meldeliste ohne eigenen Ablauf.",
    )


def build_crm_wiedervorlagen_liste() -> dict[str, Any]:
    """Offene Wiedervorlagen ueber alle Kunden; erledigen mit optionalem Ergebnis (haengt an die Kontaktnotiz)."""
    return _liste(
        screen_id="crm/wiedervorlagen", domain="crm", title="Wiedervorlagen",
        subtitle="Offene Wiedervorlagen und Aufgaben ueber alle Kunden",
        endpoint="/api/v1/crm/kunden-kontakte/wiedervorlagen?tage=365", row_route="/crm/kunden/{kunden_nr}",
        bundle="crm",
        columns=[
            {"key": "wiedervorlage", "label": "Faellig", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "ueberfaellig", "label": "Ueberfaellig", "renderKind": "boolean", "filterable": True,
             "priority": "primary"},
            {"key": "kunde", "label": "Kunde", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kunden_nr", "label": "Kunden-Nr.", "filterable": True, "priority": "secondary"},
            {"key": "art", "label": "Art", "filterable": True, "priority": "secondary"},
            {"key": "kurzinfo", "label": "Kurzinfo", "filterable": True, "priority": "primary"},
            {"key": "bediener", "label": "Bediener", "filterable": True, "priority": "tertiary"},
        ],
        actions=[_EXPORT],
        row_actions=[
            {"key": "erledigen", "label": "Erledigen", "dangerLevel": "safe", "permission": "crm.kontakt.erledigen",
             "commandEndpoint": "/api/v1/crm/kunden-kontakte/{entity_id}/erledigt", "method": "POST",
             "inputFields": [{"key": "ergebnis", "label": "Ergebnis (optional)", "type": "textarea"}]},
        ],
        purpose="Faellige Rueckrufe und Aufgaben abarbeiten; das Ergebnis wird an die Kontaktnotiz angehaengt.",
        prompts=["Welche Wiedervorlagen sind ueberfaellig?", "Was steht diese Woche fuer Kunde X an?"],
        no_workflow="Erledigen schliesst die Wiedervorlage am Kontakt; kein eigener Ablauf.",
    )


def build_agrar_bodenproben_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/bodenproben-liste", domain="agrar", title="Bodenproben",
        subtitle="Proben je Schlag und Labor", endpoint="/api/v1/labor/proben", row_route="/agrar/bodenprobe/{id}", bundle="agrar",
        columns=[
            {"key": "schlag", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "priority": "primary"},
            {"key": "labor", "label": "Labor", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Bodenproben finden und Ergebnisse oeffnen.",
        prompts=['Welche Proben warten auf Labor?', 'Zeige Proben fuer Schlag X.'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_ernte_annahme_energiemais_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/ernte-annahme-energiemais-liste", domain="agrar", title="Ernte Annahme Energiemais",
        subtitle="Annahmen Energiemais", endpoint="/api/v1/agrar/ernte", row_route="/agrar/ernte/{id}", bundle="agrar",
        columns=[
            {"key": "schlag", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "kultur", "label": "Kultur", "filterable": True, "priority": "primary"},
            {"key": "menge", "label": "Menge", "sortable": True, "numeric": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Energiemais-Ernten in der Annahme verfolgen.",
        prompts=['Welche Energiemais-Lieferungen sind offen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_feldbuch_flurstueck_kataster_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/feldbuch-flurstueck-kataster-liste", domain="agrar", title="Flurstueck-Kataster",
        subtitle="Flurstuecke und Geometrie", endpoint="/api/v1/agrar/schlaege", row_route=None, bundle="agrar",
        columns=[
            {"key": "flurstueck", "label": "Flurstueck", "filterable": True, "priority": "primary"},
            {"key": "schlag", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "flaeche", "label": "Flaeche", "numeric": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Flurstuecke im Kataster finden.",
        prompts=['Welche Flurstuecke gehoeren zu Schlag X?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_kultur_stamm_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/kultur-stamm-liste", domain="agrar", title="Kulturen",
        subtitle="Kultur-Stamm und Fruchtfolge", endpoint="/api/v1/agrar/kulturen", row_route="/agrar/kultur/{id}", bundle="agrar",
        columns=[
            {"key": "name", "label": "Kultur", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "code", "label": "Code", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Kulturen im Stamm finden.",
        prompts=['Welche Kulturen sind aktiv?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_maschinen_auslastung_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/maschinen-auslastung-liste", domain="agrar", title="Maschinenauslastung",
        subtitle="Maschinen und Stunden", endpoint="/api/v1/agrar/maschinen", row_route="/agrar/maschine/{id}", bundle="agrar",
        columns=[
            {"key": "name", "label": "Maschine", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Maschinenauslastung im Blick behalten.",
        prompts=['Welche Maschinen sind in Wartung?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_nachhaltigkeit_eudr_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/nachhaltigkeit-eudr-liste", domain="agrar", title="EUDR Nachhaltigkeit",
        subtitle="Sorgfaltserklaerungen und Risiko", endpoint="/api/v1/eudr/sorgfaltserklaerungen", row_route=None, bundle="agrar",
        columns=[
            {"key": "referenz", "label": "Referenz", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
            {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="EUDR-Sorgfaltserklaerungen verfolgen.",
        prompts=['Welche Erklaerungen sind offen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_pflanzenschutz_applikationen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/pflanzenschutz-applikationen-liste", domain="agrar", title="Pflanzenschutz-Applikationen",
        subtitle="Ausbringungen je Schlag", endpoint="/api/v1/agrar/feldbuch/massnahmen", row_route=None, bundle="agrar",
        columns=[
            {"key": "schlag", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "mittel", "label": "Mittel", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "priority": "secondary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Pflanzenschutz-Applikationen dokumentieren und finden.",
        prompts=['Welche Applikationen diese Woche?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_psm_abgabedokumentation_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/psm-abgabedokumentation-liste", domain="agrar", title="PSM Abgabedokumentation",
        subtitle="Abgaben und Nachweise", endpoint="/api/v1/agrar/psm/", row_route="/agrar/psm/abgabedokumentation/{id}", bundle="agrar",
        columns=[
            {"key": "name", "label": "Mittel", "filterable": True, "priority": "primary"},
            {"key": "kunde", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="PSM-Abgabedokumentation finden.",
        prompts=['Welche Abgaben fehlen noch?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_psm_beratung_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/psm-beratung-liste", domain="agrar", title="PSM Beratung",
        subtitle="Beratungsvorgaenge Pflanzenschutz", endpoint="/api/v1/agrar/psm/", row_route=None, bundle="agrar",
        columns=[
            {"key": "name", "label": "Mittel", "filterable": True, "priority": "primary"},
            {"key": "wirkstoff", "label": "Wirkstoff", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="PSM-Beratung mit Sortimentsdaten.",
        prompts=['Welche Mittel fuer Weizen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_psm_sachkunde_register_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/psm-sachkunde-register-liste", domain="agrar", title="PSM Sachkunde",
        subtitle="Sachkundenachweise Kunden", endpoint="/api/v1/compliance/sachkunde-register", row_route="/agrar/psm/sachkunde/{id}/edit", bundle="agrar",
        columns=[
            {"key": "kunde", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "nachweisNr", "label": "Nachweis-Nr.", "filterable": True, "priority": "primary"},
            {"key": "gueltigBis", "label": "Gueltig bis", "sortable": True, "renderKind": "date", "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Sachkundenachweise fuer PSM-Abgabe pruefen.",
        prompts=['Welche Nachweise laufen ab?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_psm_wasserschutz_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/psm-wasserschutz-liste", domain="agrar", title="Wasserschutz",
        subtitle="Wasserschutz-Zonen und Auflagen", endpoint="/api/v1/agrar/psm/wasserschutz-zonen", row_route=None, bundle="agrar",
        columns=[
            {"key": "zone", "label": "Zone", "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Wasserschutzzonen und PSM-Auflagen pruefen.",
        prompts=['Welche Zonen sind betroffen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_saatgut_bestellungen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/saatgut-bestellungen-liste", domain="agrar", title="Saatgut-Bestellungen",
        subtitle="Bestellungen Sorten und Mengen", endpoint="/api/v1/agrar/saatgut/", row_route="/agrar/saatgut/bestellung/{id}", bundle="agrar",
        columns=[
            {"key": "sorte", "label": "Sorte", "filterable": True, "priority": "primary"},
            {"key": "menge", "label": "Menge", "sortable": True, "numeric": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Saatgut-Bestellungen verfolgen.",
        prompts=['Welche Bestellungen sind offen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_saatgut_sortenregister_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/saatgut-sortenregister-liste", domain="agrar", title="Sortenregister",
        subtitle="Zugelassene Sorten", endpoint="/api/v1/agrar/varieties/", row_route="/agrar/saatgut/sorte/{id}", bundle="agrar",
        columns=[
            {"key": "name", "label": "Sorte", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "crop_type", "label": "Kultur", "filterable": True, "priority": "primary"},
            {"key": "zuechter", "label": "Zuechter", "filterable": True, "priority": "secondary"},
            {"key": "aktiv", "label": "Aktiv", "filterable": True, "renderKind": "boolean", "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Sortenregister durchsuchen.",
        prompts=['Welche Sorten sind aktiv?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_schlaege_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/schlaege-liste", domain="agrar", title="Schlaege",
        subtitle="Schlagstamm und Flaechen", endpoint="/api/v1/agrar/schlaege", row_route="/agrar/schlag/{id}", bundle="agrar",
        columns=[
            {"key": "name", "label": "Schlag", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "flaeche", "label": "Flaeche", "sortable": True, "numeric": True, "priority": "primary"},
            {"key": "kultur", "label": "Kultur", "filterable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Schlaege finden und oeffnen.",
        prompts=['Welche Schlaege haben Weizen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_schlaege_karte_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/schlaege-karte-liste", domain="agrar", title="Schlagkarte",
        subtitle="Schlaege auf der Karte", endpoint="/api/v1/agrar/schlaege", row_route="/agrar/schlag/{id}", bundle="agrar",
        columns=[
            {"key": "name", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "flaeche", "label": "Flaeche", "numeric": True, "priority": "secondary"},
            {"key": "kultur", "label": "Kultur", "filterable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Schlaege fuer die Kartenansicht laden.",
        prompts=['Zeige alle Schlaege mit Geometrie.'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_schlaege_kulturhistorie_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/schlaege-kulturhistorie-liste", domain="agrar", title="Kulturhistorie",
        subtitle="Fruchtfolge je Schlag", endpoint="/api/v1/agrar/schlaege", row_route="/agrar/schlag/{id}", bundle="agrar",
        columns=[
            {"key": "schlag", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "kultur", "label": "Kultur", "filterable": True, "priority": "primary"},
            {"key": "jahr", "label": "Jahr", "sortable": True, "numeric": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Kulturhistorie der Schlaege einsehen.",
        prompts=['Welche Kultur war letztes Jahr auf Schlag X?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_agrar_vertrag_kontingente_liste() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/vertrag-kontingente-liste", domain="agrar", title="Vertrag-Kontingente",
        subtitle="Restmengen und Kontingente", endpoint="/api/v1/kontrakte", row_route="/agrar/kontrakt/{id}", bundle="agrar",
        columns=[
            {"key": "nummer", "label": "Kontrakt", "filterable": True, "priority": "primary"},
            {"key": "partner", "label": "Partner", "filterable": True, "priority": "primary"},
            {"key": "restmenge", "label": "Restmenge", "sortable": True, "numeric": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Kontrakt-Kontingente und Restmengen pruefen.",
        prompts=['Welche Kontingente sind ausgeschoepft?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_charge_wareneingang_liste() -> dict[str, Any]:
    return _liste(
        screen_id="charge/wareneingang-liste", domain="lager", title="Wareneingang Chargen",
        subtitle="Chargen aus Wareneingaengen", endpoint="/api/v1/chargen", row_route="/charge/stamm/{id}", bundle="lager",
        columns=[
            {"key": "charge", "label": "Charge", "filterable": True, "priority": "primary"},
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "primary"},
            {"key": "menge", "label": "Menge", "sortable": True, "numeric": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Wareneingaenge als Chargen erfassen und finden.",
        prompts=['Welche Chargen kamen heute rein?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_compliance_bvl_umsatzmeldung_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/bvl-umsatzmeldung-liste", domain="compliance", title="BVL Umsatzmeldung",
        subtitle="Pflanzenschutz-Umsatzmeldungen", endpoint="/api/v1/compliance/bvl-umsaetze", row_route=None, bundle="compliance",
        columns=[
            {"key": "periode", "label": "Periode", "filterable": True, "priority": "primary"},
            {"key": "umsatz", "label": "Umsatz", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="BVL-Umsatzmeldungen verfolgen.",
        prompts=['Welche Meldungen sind faellig?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_compliance_eudr_compliance_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/eudr-compliance-liste", domain="compliance", title="EUDR Compliance",
        subtitle="Sorgfalt und Lieferketten", endpoint="/api/v1/eudr/sorgfaltserklaerungen", row_route=None, bundle="compliance",
        columns=[
            {"key": "referenz", "label": "Referenz", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="EUDR-Compliance-Faelle finden.",
        prompts=['Welche Lieferketten sind ungeprueft?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_compliance_export_pruefung_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/export-pruefung-liste", domain="compliance", title="Export-Pruefung",
        subtitle="Exportfaehigkeit pruefen", endpoint="/api/v1/export/entities", row_route=None, bundle="compliance",
        columns=[
            {"key": "entity", "label": "Entitaet", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Export-Pruefungen nachvollziehen.",
        prompts=['Welche Exporte sind blockiert?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_compliance_gefahrstoff_doku_liste() -> dict[str, Any]:
    return _liste(
        screen_id="compliance/gefahrstoff-doku-liste", domain="compliance", title="Gefahrstoff-Doku",
        subtitle="Gefahrstoffdokumentation", endpoint="/api/v1/compliance/exports/gefahrstoffdoku", row_route=None, bundle="compliance",
        columns=[
            {"key": "produkt", "label": "Produkt", "filterable": True, "priority": "primary"},
            {"key": "klasse", "label": "Klasse", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Gefahrstoffdokumentation einsehen.",
        prompts=['Welche Produkte brauchen Update?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_controlling_plan_ist_liste() -> dict[str, Any]:
    return _liste(
        screen_id="controlling/plan-ist-liste", domain="controlling", title="Plan-Ist",
        subtitle="KPIs Plan vs. Ist", endpoint="/api/v1/controlling/kpis", row_route=None, bundle="controlling",
        columns=[
            {"key": "name", "label": "KPI", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kpi_code", "label": "Code", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Plan-Ist-KPIs vergleichen.",
        prompts=['Wo weicht Ist vom Plan ab?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_crm_contact_detail_liste() -> dict[str, Any]:
    return _liste(
        screen_id="crm/contact-detail-liste", domain="crm", title="Kontakte",
        subtitle="Kontaktliste zur Detailansicht", endpoint="/api/v1/crm/contacts", row_route="/crm/kontakt/{id}", bundle="crm",
        columns=[
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "email", "label": "E-Mail", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Kontakte finden und Detail oeffnen.",
        prompts=['Welche Kontakte haben offene Aufgaben?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_crm_kontakt_management_liste() -> dict[str, Any]:
    return _liste(
        screen_id="crm/kontakt-management-liste", domain="crm", title="Kontakt-Management",
        subtitle="Kontakte und Follow-ups", endpoint="/api/v1/crm/contacts", row_route="/crm/kontakt/{id}", bundle="crm",
        columns=[
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "firma", "label": "Firma", "filterable": True, "priority": "primary"},
            {"key": "email", "label": "E-Mail", "filterable": True, "priority": "secondary"},
            {"key": "prioritaet", "label": "Prioritaet", "filterable": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Kontakte im Management finden.",
        prompts=['Welche Kontakte sind ueberfaellig?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_einkauf_anfragen_create_liste() -> dict[str, Any]:
    return _liste(
        screen_id="einkauf/anfragen-create-liste", domain="einkauf", title="Anfragen",
        subtitle="Bedarfsanforderungen anlegen", endpoint="/api/v1/einkauf/anfragen", row_route="/einkauf/anfrage/{id}", bundle="einkauf",
        columns=[
            {"key": "anfrageNummer", "label": "Anfrage-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Anfragen vor Anlage finden.",
        prompts=['Welche Anfragen sind Entwurf?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_einkauf_angebote_vergleich_liste() -> dict[str, Any]:
    return _liste(
        screen_id="einkauf/angebote-vergleich-liste", domain="einkauf", title="Angebotsvergleich",
        subtitle="Lieferantenangebote vergleichen", endpoint="/api/v1/einkauf/angebote", row_route="/einkauf/angebot/{id}", bundle="einkauf",
        columns=[
            {"key": "angebotNummer", "label": "Angebot-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "preis", "label": "Preis", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Angebote zum Vergleich finden.",
        prompts=['Welche Angebote zur Anfrage X?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_einkauf_dienstleistungen_haltung_liste() -> dict[str, Any]:
    return _liste(
        screen_id="einkauf/dienstleistungen-haltung-liste", domain="einkauf", title="Dienstleistungen Haltung",
        subtitle="DL-Bestellungen Tierhaltung", endpoint="/api/v1/einkauf/bestellungen", row_route="/einkauf/bestellung/{id}", bundle="einkauf",
        columns=[
            {"key": "bestellNummer", "label": "Bestell-Nr.", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Dienstleistungsbestellungen finden.",
        prompts=['Welche DL-Bestellungen sind offen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_einkauf_einkauf_vorgang_liste() -> dict[str, Any]:
    return _liste(
        screen_id="einkauf/einkauf-vorgang-liste", domain="einkauf", title="Einkaufsvorgaenge",
        subtitle="Vorgaenge im Einkauf", endpoint="/api/v1/einkauf/bestellungen", row_route="/einkauf/bestellung/{id}", bundle="einkauf",
        columns=[
            {"key": "nummer", "label": "Vorgang", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Einkaufsvorgaenge finden.",
        prompts=['Welche Vorgaenge warten auf Freigabe?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_einkauf_kontrakte_service_liste() -> dict[str, Any]:
    return _liste(
        screen_id="einkauf/kontrakte-service-liste", domain="einkauf", title="Kontrakte Service",
        subtitle="Einkaufskontrakte Service", endpoint="/api/v1/kontrakte", row_route="/einkauf/kontrakt/{id}", bundle="einkauf",
        columns=[
            {"key": "nummer", "label": "Kontrakt", "filterable": True, "priority": "primary"},
            {"key": "partner", "label": "Partner", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Service-Kontrakte im Einkauf finden.",
        prompts=['Welche Kontrakte laufen aus?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_einkauf_rechnung_abgleich_liste() -> dict[str, Any]:
    return _liste(
        screen_id="einkauf/rechnung-abgleich-liste", domain="einkauf", title="Rechnungsabgleich",
        subtitle="Eingangsrechnungen abgleichen", endpoint="/api/v1/einkauf/rechnungseingaenge", row_route="/belege/purchase_invoice/{id}", bundle="einkauf",
        columns=[
            {"key": "rechnungsNummer", "label": "Rechnung-Nr.", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Rechnungen zum Abgleich finden.",
        prompts=['Welche Rechnungen passen nicht zur Bestellung?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_einkauf_retouren_liste() -> dict[str, Any]:
    return _liste(
        screen_id="einkauf/retouren-liste", domain="einkauf", title="Retouren",
        subtitle="Einkaufsretouren", endpoint="/api/v1/einkauf/retouren", row_route="/einkauf/retouren/{id}", bundle="einkauf",
        columns=[
            {"key": "nummer", "label": "Retoure-Nr.", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Retouren verfolgen.",
        prompts=['Welche Retouren sind offen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_etiketten_druck_liste() -> dict[str, Any]:
    return _liste(
        screen_id="etiketten/druck-liste", domain="lager", title="Etikettendruck",
        subtitle="Druckauftraege Etiketten", endpoint="/api/v1/etiketten/druckauftrag", row_route=None, bundle="lager",
        columns=[
            {"key": "auftrag", "label": "Auftrag", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Etikettendruck-Auftraege finden.",
        prompts=['Welche Druckauftraege sind offen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_export_intrastat_meldung_liste() -> dict[str, Any]:
    return _liste(
        screen_id="export/intrastat-meldung-liste", domain="compliance", title="Intrastat-Meldung",
        subtitle="Intrastat Meldezeitraeume", endpoint="/api/v1/intrastat/meldungen", row_route=None, bundle="compliance",
        columns=[
            {"key": "periode", "label": "Periode", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Intrastat-Meldungen verfolgen.",
        prompts=['Welche Meldungen sind faellig?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_export_umsatzsteuer_voranmeldung_liste() -> dict[str, Any]:
    return _liste(
        screen_id="export/umsatzsteuer-voranmeldung-liste", domain="finance", title="USt-Voranmeldung",
        subtitle="Umsatzsteuer-Voranmeldungen", endpoint="/api/v1/compliance/ustva", row_route=None, bundle="finance",
        columns=[
            {"key": "periode", "label": "Periode", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="USt-Voranmeldungen einsehen.",
        prompts=['Welche Voranmeldung ist faellig?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_fibu_anlagen_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/anlagen-liste", domain="finance", title="Anlagen",
        subtitle="Anlagevermoegen", endpoint="/api/v1/finance/fixed-assets/detail", row_route="/fibu/anlage/{id}", bundle="finance",
        table_profile="financial",
        columns=[
            {"key": "anlagennr", "label": "Anlage-Nr.", "filterable": True, "priority": "primary"},
            {"key": "bezeichnung", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "buchwert", "label": "Buchwert", "numeric": True, "renderKind": "currency", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Anlagen finden und oeffnen.",
        prompts=['Welche Anlagen haben niedrigen Buchwert?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_fibu_debitoren_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/debitoren-liste", domain="finance", title="Debitoren OP",
        subtitle="Offene Posten Debitoren", endpoint="/api/v1/finance/open-items?typ=debitor", row_route="/sales/invoice/{id}", bundle="finance",
        table_profile="financial",
        columns=[
            {"key": "rechnungsnr", "label": "Rechnung", "filterable": True, "priority": "primary"},
            {"key": "kunde", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "offen", "label": "Offen", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "faelligkeit", "label": "Faellig", "sortable": True, "renderKind": "date", "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Offene Debitorenposten finden.",
        prompts=['Welche Posten sind ueberfaellig?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_fibu_hauptbuch_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/hauptbuch-liste", domain="finance", title="Hauptbuch",
        subtitle="Hauptbuch-Buchungen", endpoint="/api/v1/journal-entries/", row_route=None, bundle="finance",
        table_profile="financial",
        columns=[
            {"key": "belegnummer", "label": "Beleg", "filterable": True, "priority": "primary"},
            {"key": "konto", "label": "Konto", "filterable": True, "priority": "primary"},
            {"key": "soll", "label": "Soll", "numeric": True, "priority": "secondary"},
            {"key": "haben", "label": "Haben", "numeric": True, "priority": "secondary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Hauptbuch-Buchungen einsehen.",
        prompts=['Welche Buchungen auf Konto 1200?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_fibu_kassenbuch_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/kassenbuch-liste", domain="finance", title="Kassenbuch",
        subtitle="Kassenbuchungen", endpoint="/api/v1/kasse/tagesabschluss/aktuell", row_route=None, bundle="finance",
        table_profile="financial",
        columns=[
            {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "priority": "primary"},
            {"key": "saldo", "label": "Saldo", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Kassenbuch und Tagesabschluesse finden.",
        prompts=['Ist der heutige Abschluss offen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_fibu_kreditoren_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/kreditoren-liste", domain="finance", title="Kreditoren OP",
        subtitle="Offene Posten Kreditoren", endpoint="/api/v1/finance/open-items?typ=kreditor", row_route="/belege/purchase_invoice/{id}", bundle="finance",
        table_profile="financial",
        columns=[
            {"key": "rechnungsnr", "label": "Rechnung", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "offen", "label": "Offen", "numeric": True, "renderKind": "currency", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Offene Kreditorenposten finden.",
        prompts=['Welche Verbindlichkeiten sind faellig?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_fibu_schnittstelle_fibu_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/schnittstelle-fibu-liste", domain="finance", title="FIBU-Schnittstelle",
        subtitle="Buchungsuebergabe Exporte", endpoint="/api/v1/finance/connectors/profiles", row_route=None, bundle="finance",
        columns=[
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "filterable": True, "renderKind": "status", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="FIBU-Schnittstellen-Exporte verfolgen.",
        prompts=['Welcher Export ist fehlgeschlagen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
    )
def build_fibu_verbindlichkeiten_liste() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/verbindlichkeiten-liste", domain="finance", title="Verbindlichkeiten",
        subtitle="Offene Verbindlichkeiten", endpoint="/api/v1/finance/open-items?typ=kreditor", row_route="/fibu/verbindlichkeit/{id}", bundle="finance",
        table_profile="financial",
        columns=[
            {"key": "rechnungsNr", "label": "Rechnung", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "offen", "label": "Offen", "numeric": True, "renderKind": "currency", "priority": "primary"},
        ],
        actions=[_EXPORT],
        row_actions=[],
        purpose="Verbindlichkeiten finden.",
        prompts=['Welche Verbindlichkeiten sind offen?'],
        no_workflow="Listenmaske ohne eigenen Ablauf; Status steht am Datensatz.",
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
    "agrar/psm-liste": build_agrar_psm_liste,
    "artikel/liste": build_artikel_liste,
    "finance/wechselkurse": build_finance_wechselkurse_liste,
    "finance/buchungsvorlagen": build_finance_buchungsvorlagen_liste,
    "einkauf/warengruppen": build_einkauf_warengruppen_liste,
    "einkauf/zahlungsbedingungen": build_einkauf_zahlungsbedingungen_liste,
    "crm/wiedervorlagen": build_crm_wiedervorlagen_liste,
    "charge/liste": build_chargen_liste,
    "personal/mitarbeiter-liste": build_personal_mitarbeiter_liste,
    "versicherungen/liste": build_versicherungen_liste,
    "wartung/anlagen-liste": build_wartung_anlagen_liste,
    "projekte/liste": build_projekte_liste,
    "labor/proben-liste": build_labor_proben_liste,
    "foerderung/liste": build_foerder_antraege_liste,
    "schaeden/liste": build_schaeden_liste,
    "admin/benutzer-liste": build_admin_benutzer_liste,
    "compliance/pcn-liste": build_compliance_pcn_liste,
    "personal/stundenzettel-liste": build_personal_stundenzettel_liste,
    "agrar/biostimulanzien-liste": build_agrar_biostimulanzien_liste,
    "agrar/ernte-liste": build_agrar_ernte_liste,
    "agrar/kulturpflanzen-liste": build_agrar_kulturpflanzen_liste,
    "zertifikate/liste": build_zertifikate_liste,
    "benachrichtigungen/liste": build_benachrichtigungen_liste,
    "qualitaet/labor-liste": build_qualitaet_labor_liste,
    "disposition/liste": build_disposition_liste,
    "crm/kontakte-liste": build_crm_kontakte_liste,
    "crm/betriebsprofile-liste": build_crm_betriebsprofile_liste,
    "sales/angebote-liste": build_sales_angebote_liste,
    "sales/auftraege-liste": build_sales_auftraege_liste,
    "sales/lieferungen-liste": build_sales_lieferungen_liste,
    "einkauf/rechnungseingaenge-liste": build_einkauf_rechnungseingaenge_liste,
    "service/anfragen-liste": build_service_anfragen_liste,
    "compliance/enni-meldungen-liste": build_compliance_enni_meldungen_liste,
    "qualitaet/reklamationen-liste": build_qualitaet_reklamationen_liste,
    "marketing/kampagnen-liste": build_marketing_kampagnen_liste,
    "crm/kunden-liste": build_crm_kunden_liste,
    "crm/lieferanten-liste": build_crm_lieferanten_liste,
    "banken/konten-liste": build_banken_konten_liste,
    "dokumente/ablage-liste": build_dokumente_ablage_liste,
    "vertrag/rahmenvertraege-liste": build_vertrag_rahmenvertraege_liste,
    "tankstelle/zapfungen-liste": build_tankstelle_zapfungen_liste,
    "waage/liste": build_waage_liste,
    "compliance/cross-compliance-liste": build_compliance_cross_compliance_liste,
    "compliance/zulassungen-liste": build_compliance_zulassungen_liste,
    "compliance/vvvo-liste": build_compliance_vvvo_liste,
    "compliance/sachkunde-liste": build_compliance_sachkunde_liste,
    "compliance/saatgut-nachbau-liste": build_compliance_saatgut_nachbau_liste,
    "admin/audit-log-liste": build_admin_audit_log_liste,
    "admin/webhooks-liste": build_admin_webhooks_liste,
    "agrar/feldbuch-massnahmen-liste": build_agrar_feldbuch_massnahmen_liste,
    "agrar/feldbuch-schlagkartei-liste": build_agrar_feldbuch_schlagkartei_liste,
    "agrar/saatzucht-partien-liste": build_agrar_saatzucht_partien_liste,
    "agrar/vermehrungsvertraege-liste": build_agrar_vermehrungsvertraege_liste,
    "compliance/gelangensbestaetigung-liste": build_compliance_gelangensbestaetigung_liste,
    "compliance/intrastat-liste": build_compliance_intrastat_liste,
    "compliance/lksg-liste": build_compliance_lksg_liste,
    "compliance/qs-checkliste-liste": build_compliance_qs_checkliste_liste,
    "crm/aktivitaeten-liste": build_crm_aktivitaeten_liste,
    "crm/leads-liste": build_crm_leads_liste,
    "einkauf/bestellvorschlaege-liste": build_einkauf_bestellvorschlaege_liste,
    "einkauf/frachtauftraege-liste": build_einkauf_frachtauftraege_liste,
    "fibu/buchungsjournal-liste": build_fibu_buchungsjournal_liste,
    "fibu/kontenplan-liste": build_fibu_kontenplan_liste,
    "fibu/kostenstellen-liste": build_fibu_kostenstellen_liste,
    "fibu/offene-posten-liste": build_fibu_offene_posten_liste,
    "fibu/zahlungseingaenge-liste": build_fibu_zahlungseingaenge_liste,
    "fibu/zahlungslaeufe-liste": build_fibu_zahlungslaeufe_liste,
    "finance/ap-invoices-liste": build_finance_ap_invoices_liste,
    "finance/audit-trail-liste": build_finance_audit_trail_liste,
    "finance/payment-matching-liste": build_finance_payment_matching_liste,
    "finance/periods-liste": build_finance_periods_liste,
    "finance/skonto-optimizer-liste": build_finance_skonto_optimizer_liste,
    "fuhrpark/fahrzeuge-liste": build_fuhrpark_fahrzeuge_liste,
    "fuhrpark/rechnungen-liste": build_fuhrpark_rechnungen_liste,
    "genossenschaft/mitglieder-liste": build_genossenschaft_mitglieder_liste,
    "kontrakte/kontraktklassen-liste": build_kontrakte_kontraktklassen_liste,
    "kontrakte/liste": build_kontrakte_liste,
    "lager/inventur-liste": build_lager_inventur_liste,
    "lager/lagerbewegungen-liste": build_lager_lagerbewegungen_liste,
    "lager/partiestamm-liste": build_lager_partiestamm_liste,
    "lager/silo-uebersicht-liste": build_lager_silo_uebersicht_liste,
    "personal/zeiterfassung-liste": build_personal_zeiterfassung_liste,
    "qualitaet/ausnahmen-liste": build_qualitaet_ausnahmen_liste,
    "transporte/fahrer-liste": build_transporte_fahrer_liste,
    "verladung/liste": build_verladung_liste,
    "waage/hofliste": build_waage_hofliste_liste,
    "waage/waagen-liste": build_waage_waagen_liste,
    "waage/wiegungen-liste": build_waage_wiegungen_liste,    "agrar/bodenproben-liste": build_agrar_bodenproben_liste,    "agrar/ernte-annahme-energiemais-liste": build_agrar_ernte_annahme_energiemais_liste,    "agrar/feldbuch-flurstueck-kataster-liste": build_agrar_feldbuch_flurstueck_kataster_liste,    "agrar/kultur-stamm-liste": build_agrar_kultur_stamm_liste,    "agrar/maschinen-auslastung-liste": build_agrar_maschinen_auslastung_liste,    "agrar/nachhaltigkeit-eudr-liste": build_agrar_nachhaltigkeit_eudr_liste,    "agrar/pflanzenschutz-applikationen-liste": build_agrar_pflanzenschutz_applikationen_liste,    "agrar/psm-abgabedokumentation-liste": build_agrar_psm_abgabedokumentation_liste,    "agrar/psm-beratung-liste": build_agrar_psm_beratung_liste,    "agrar/psm-sachkunde-register-liste": build_agrar_psm_sachkunde_register_liste,    "agrar/psm-wasserschutz-liste": build_agrar_psm_wasserschutz_liste,    "agrar/saatgut-bestellungen-liste": build_agrar_saatgut_bestellungen_liste,    "agrar/saatgut-sortenregister-liste": build_agrar_saatgut_sortenregister_liste,    "agrar/schlaege-liste": build_agrar_schlaege_liste,    "agrar/schlaege-karte-liste": build_agrar_schlaege_karte_liste,    "agrar/schlaege-kulturhistorie-liste": build_agrar_schlaege_kulturhistorie_liste,    "agrar/vertrag-kontingente-liste": build_agrar_vertrag_kontingente_liste,    "charge/wareneingang-liste": build_charge_wareneingang_liste,    "compliance/bvl-umsatzmeldung-liste": build_compliance_bvl_umsatzmeldung_liste,    "compliance/eudr-compliance-liste": build_compliance_eudr_compliance_liste,    "compliance/export-pruefung-liste": build_compliance_export_pruefung_liste,    "compliance/gefahrstoff-doku-liste": build_compliance_gefahrstoff_doku_liste,    "controlling/plan-ist-liste": build_controlling_plan_ist_liste,    "crm/contact-detail-liste": build_crm_contact_detail_liste,    "crm/kontakt-management-liste": build_crm_kontakt_management_liste,    "einkauf/anfragen-create-liste": build_einkauf_anfragen_create_liste,    "einkauf/angebote-vergleich-liste": build_einkauf_angebote_vergleich_liste,    "einkauf/dienstleistungen-haltung-liste": build_einkauf_dienstleistungen_haltung_liste,    "einkauf/einkauf-vorgang-liste": build_einkauf_einkauf_vorgang_liste,    "einkauf/kontrakte-service-liste": build_einkauf_kontrakte_service_liste,    "einkauf/rechnung-abgleich-liste": build_einkauf_rechnung_abgleich_liste,    "einkauf/retouren-liste": build_einkauf_retouren_liste,    "etiketten/druck-liste": build_etiketten_druck_liste,    "export/intrastat-meldung-liste": build_export_intrastat_meldung_liste,    "export/umsatzsteuer-voranmeldung-liste": build_export_umsatzsteuer_voranmeldung_liste,    "fibu/anlagen-liste": build_fibu_anlagen_liste,    "fibu/debitoren-liste": build_fibu_debitoren_liste,    "fibu/hauptbuch-liste": build_fibu_hauptbuch_liste,    "fibu/kassenbuch-liste": build_fibu_kassenbuch_liste,    "fibu/kreditoren-liste": build_fibu_kreditoren_liste,    "fibu/schnittstelle-fibu-liste": build_fibu_schnittstelle_fibu_liste,    "fibu/verbindlichkeiten-liste": build_fibu_verbindlichkeiten_liste,
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
                "crm/opportunities-liste": "/crm/opportunities",
                "agrar/psm-liste": "/agrar/psm",
                "artikel/liste": "/artikel",
                "finance/wechselkurse": "/finance/wechselkurse",
                "finance/buchungsvorlagen": "/finance/buchungsvorlagen",
                "einkauf/warengruppen": "/einkauf/warengruppen",
                "einkauf/zahlungsbedingungen": "/einkauf/zahlungsbedingungen",
                "crm/wiedervorlagen": "/crm/wiedervorlagen",
                "charge/liste": "/charge/liste",
                "personal/mitarbeiter-liste": "/personal/mitarbeiter",
                "versicherungen/liste": "/versicherungen",
                "wartung/anlagen-liste": "/wartung/anlagen",
                "projekte/liste": "/projekte",
                "labor/proben-liste": "/labor/proben",
                "foerderung/liste": "/foerderung",
                "schaeden/liste": "/schaeden",
                "admin/benutzer-liste": "/admin/benutzer",
                "compliance/pcn-liste": "/compliance/pcn-liste",
                "personal/stundenzettel-liste": "/personal/stundenzettel-liste",
                "agrar/biostimulanzien-liste": "/agrar/biostimulanzien",
                "agrar/ernte-liste": "/agrar/ernte",
                "agrar/kulturpflanzen-liste": "/agrar/kulturpflanzen",
                "zertifikate/liste": "/zertifikate",
                "benachrichtigungen/liste": "/benachrichtigungen",
                "qualitaet/labor-liste": "/qualitaet/labor-liste",
                "disposition/liste": "/disposition",
                "crm/kontakte-liste": "/crm/kontakte-liste",
                "crm/betriebsprofile-liste": "/crm/betriebsprofile",
                "sales/angebote-liste": "/sales/angebote-liste",
                "sales/auftraege-liste": "/sales/auftraege-liste",
                "sales/lieferungen-liste": "/sales/lieferungen-liste",
                "einkauf/rechnungseingaenge-liste": "/einkauf/rechnungseingaenge-liste",
                "service/anfragen-liste": "/service/anfragen",
                "compliance/enni-meldungen-liste": "/compliance/enni-meldungen",
                "qualitaet/reklamationen-liste": "/qualitaet/reklamationen",
                "marketing/kampagnen-liste": "/marketing/kampagnen",
                "crm/kunden-liste": "/crm/kunden-liste",
                "crm/lieferanten-liste": "/crm/lieferanten-liste",
                "banken/konten-liste": "/banken/konten",
                "fuhrpark/rechnungen-liste": "/fuhrpark/fuhrpark-rechnungen",
                "agrar/feldbuch-massnahmen-liste": "/agrar/feldbuch/massnahmen",
                "agrar/saatzucht-partien-liste": "/agrar/saatzucht",
                "einkauf/frachtauftraege-liste": "/einkauf/frachtauftraege-eingang",
                "finance/ap-invoices-liste": "/finance/ap-invoices-list",
                "finance/payment-matching-liste": "/finance/payment-matching",
                "finance/bookings/new": "/finance/bookings/new",
                "kontrakte/liste": "/kontrakte/LstKontraktUebersicht",
                "dokumente/ablage-liste": "/dokumente/ablage",
                "vertrag/rahmenvertraege-liste": "/vertrag/rahmenvertraege",
                "tankstelle/zapfungen-liste": "/tankstelle/zapfungen",
                "waage/liste": "/waage/liste",
                "compliance/cross-compliance-liste": "/compliance/cross-compliance",
                "compliance/zulassungen-liste": "/compliance/zulassungen-register",
                "compliance/vvvo-liste": "/compliance/vvvo-register",
                "compliance/sachkunde-liste": "/compliance/sachkunde-register",
                "compliance/saatgut-nachbau-liste": "/compliance/saatgut-nachbau",
                "admin/audit-log-liste": "/admin/audit-log",
                "agrar/bodenproben-liste": "/agrar/bodenproben/liste",
                "agrar/ernte-annahme-energiemais-liste": "/agrar/ernte-annahme-energiemais",
                "agrar/feldbuch-schlagkartei-liste": "/agrar/feldbuch/ackerschlagkartei",
                "agrar/feldbuch-flurstueck-kataster-liste": "/agrar/feldbuch/flurstueck-kataster",
                "agrar/kultur-stamm-liste": "/agrar/kultur-stamm",
                "agrar/maschinen-auslastung-liste": "/agrar/maschinen-auslastung",
                "agrar/nachhaltigkeit-eudr-liste": "/agrar/nachhaltigkeit-eudr",
                "agrar/pflanzenschutz-applikationen-liste": "/agrar/pflanzenschutz-applikationen",
                "agrar/psm-abgabedokumentation-liste": "/agrar/psm/abgabedokumentation",
                "agrar/psm-beratung-liste": "/agrar/psm/beratung",
                "agrar/psm-sachkunde-register-liste": "/agrar/psm/sachkunde-register",
                "agrar/psm-wasserschutz-liste": "/agrar/psm/wasserschutz",
                "agrar/saatgut-bestellungen-liste": "/agrar/saatgut/bestellungen",
                "agrar/saatgut-sortenregister-liste": "/agrar/saatgut/sortenregister",
                "agrar/schlaege-liste": "/agrar/schlaege",
                "agrar/schlaege-karte-liste": "/agrar/schlaege/karte",
                "agrar/schlaege-kulturhistorie-liste": "/agrar/schlaege/kulturhistorie",
                "agrar/vertrag-kontingente-liste": "/agrar/vertrag-kontingente",
                "charge/wareneingang-liste": "/charge/wareneingang",
                "compliance/bvl-umsatzmeldung-liste": "/compliance/bvl-umsatzmeldung",
                "compliance/eudr-compliance-liste": "/compliance/eudr-compliance",
                "compliance/export-pruefung-liste": "/compliance/export-pruefung",
                "compliance/gefahrstoff-doku-liste": "/compliance/gefahrstoff-doku",
                "compliance/qs-checkliste-liste": "/compliance/qs-checkliste",
                "controlling/plan-ist-liste": "/controlling/plan-ist",
                "crm/contact-detail-liste": "/crm/contact-detail",
                "crm/kontakt-management-liste": "/crm/kontakt-management",
                "crm/leads-liste": "/crm/lead-detail",
                "einkauf/anfragen-create-liste": "/einkauf/anfragen-create",
                "einkauf/angebote-vergleich-liste": "/einkauf/angebote-vergleich",
                "einkauf/bestellvorschlaege-liste": "/einkauf/bestellvorschlaege",
                "einkauf/dienstleistungen-haltung-liste": "/einkauf/dienstleistungen-haltung",
                "einkauf/einkauf-vorgang-liste": "/einkauf/vorgang",
                "einkauf/kontrakte-service-liste": "/einkauf/kontrakte-service",
                "einkauf/rechnung-abgleich-liste": "/einkauf/rechnung-abgleich",
                "einkauf/retouren-liste": "/einkauf/retouren",
                "etiketten/druck-liste": "/etiketten/druck",
                "export/intrastat-meldung-liste": "/export/intrastat-meldung",
                "export/umsatzsteuer-voranmeldung-liste": "/export/umsatzsteuer-voranmeldung",
                "fibu/anlagen-liste": "/fibu/anlagen",
                "fibu/buchungsjournal-liste": "/fibu/buchungsjournal",
                "fibu/debitoren-liste": "/fibu/debitoren",
                "fibu/hauptbuch-liste": "/fibu/hauptbuch",
                "fibu/kassenbuch-liste": "/fibu/kassenbuch",
                "fibu/kostenstellen-liste": "/fibu/kostenstellenrechnung",
                "fibu/kreditoren-liste": "/fibu/kreditoren",
                "fibu/offene-posten-liste": "/fibu/offene-posten",
                "fibu/schnittstelle-fibu-liste": "/fibu/schnittstelle-fibu",
                "fibu/verbindlichkeiten-liste": "/fibu/verbindlichkeiten",
                "fibu/zahlungslaeufe-liste": "/fibu/zahlungslaeufe"}
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
                   "crm/opportunities-liste": ["verkaufschancen", "opportunities", "pipeline"],
                   "agrar/psm-liste": ["psm", "pflanzenschutzmittel", "pflanzenschutz"],
                   "artikel/liste": ["artikel", "artikelstamm", "produkte"],
                   "charge/liste": ["chargen", "partien", "lose"],
                   "personal/mitarbeiter-liste": ["mitarbeiter", "mitarbeitende", "personal"],
                   "versicherungen/liste": ["versicherungen", "policen", "versicherungsvertraege"],
                   "wartung/anlagen-liste": ["wartung", "anlagen", "instandhaltung"],
                   "projekte/liste": ["projekte", "projektliste", "vorhaben"],
                   "labor/proben-liste": ["laborproben", "proben", "labor"],
                   "foerderung/liste": ["foerderantraege", "foerderung", "antraege"],
                   "schaeden/liste": ["schaeden", "schadenmeldungen", "versicherungsschaeden"],
                   "admin/benutzer-liste": ["benutzer", "nutzer", "konten"],
                   "compliance/pcn-liste": ["pcn", "ufi", "giftinformation"],
                   "personal/stundenzettel-liste": ["stundenzettel", "fahrerzeiten", "arbeitszeit"],
                   "agrar/biostimulanzien-liste": ["biostimulanzien", "agrarprodukte", "stimulanzien"],
                   "agrar/ernte-liste": ["ernte", "ernten", "ernteliste"],
                   "agrar/kulturpflanzen-liste": ["kulturpflanzen", "kulturen", "fruchtfolge"],
                   "zertifikate/liste": ["zertifikate", "zertifizierung", "qs nachweis"],
                   "benachrichtigungen/liste": ["benachrichtigungen", "hinweise", "warnungen inbox"],
                   "qualitaet/labor-liste": ["laborauftraege", "labor liste", "analysenauftrag"],
                   "disposition/liste": ["disposition", "bestellvorschlag", "mindestbestand"],
                   "crm/kontakte-liste": ["kontakte", "ansprechpartner", "kontaktliste"],
                   "crm/betriebsprofile-liste": ["betriebsprofile", "landwirt", "farm profile"],
                   "sales/angebote-liste": ["verkaufsangebote", "kundenangebote", "sales offers"],
                   "sales/auftraege-liste": ["verkaufsauftraege", "kundenauftraege", "sales orders"],
                   "sales/lieferungen-liste": ["lieferscheine", "auslieferungen", "delivery notes"],
                   "einkauf/rechnungseingaenge-liste": ["rechnungseingang", "eingangsrechnungen", "ap liste"],
                   "service/anfragen-liste": ["service", "tickets", "serviceanfragen"],
                   "compliance/enni-meldungen-liste": ["enni", "duengemeldung", "naehrstoffmeldung"],
                   "qualitaet/reklamationen-liste": ["reklamationen", "beanstandungen", "maengel"],
                   "marketing/kampagnen-liste": ["marketing kampagnen", "werbekampagnen", "kampagne marketing"],
                   "crm/kunden-liste": ["kundenliste", "kundenstamm", "kunden"],
                   "crm/lieferanten-liste": ["lieferantenliste", "lieferanten crm", "einkaufspartner"],
                   "banken/konten-liste": ["bankkonten", "hausbank", "konten"],
                   "dokumente/ablage-liste": ["dokumentenablage", "dms ablage", "dokumente"],
                   "vertrag/rahmenvertraege-liste": ["rahmenvertraege", "kontrakt rahmen", "restmenge"],
                   "tankstelle/zapfungen-liste": ["tankstelle", "zapfungen", "diesel zapfung"],
                   "waage/liste": ["waagen", "eichung", "brueckenwaage"],
                   "compliance/cross-compliance-liste": ["cross compliance", "direktzahlungen", "gaep"],
                   "compliance/zulassungen-liste": ["zulassungsregister", "produktzulassung"],
                   "compliance/vvvo-liste": ["vvvo register", "tierhaltung register"],
                   "compliance/sachkunde-liste": ["sachkundenachweis", "psm sachkunde"],
                   "compliance/saatgut-nachbau-liste": ["saatgut nachbau", "nachbauflaeche"],
                   "admin/audit-log-liste": ['audit-log', 'audit-log'],
                   "agrar/bodenproben-liste": ['Bodenproben', 'bodenproben-liste'],
                   "agrar/ernte-annahme-energiemais-liste": ['Ernte Annahme Energiemais', 'ernte-annahme-energiemais-liste'],
                   "agrar/feldbuch-schlagkartei-liste": ['Ackerschlagkartei', 'feldbuch-schlagkartei-liste'],
                   "agrar/feldbuch-flurstueck-kataster-liste": ['Flurstueck-Kataster', 'feldbuch-flurstueck-kataster-liste'],
                   "agrar/kultur-stamm-liste": ['Kulturen', 'kultur-stamm-liste'],
                   "agrar/maschinen-auslastung-liste": ['Maschinenauslastung', 'maschinen-auslastung-liste'],
                   "agrar/nachhaltigkeit-eudr-liste": ['EUDR Nachhaltigkeit', 'nachhaltigkeit-eudr-liste'],
                   "agrar/pflanzenschutz-applikationen-liste": ['Pflanzenschutz-Applikationen', 'pflanzenschutz-applikationen-liste'],
                   "agrar/psm-abgabedokumentation-liste": ['PSM Abgabedokumentation', 'psm-abgabedokumentation-liste'],
                   "agrar/psm-beratung-liste": ['PSM Beratung', 'psm-beratung-liste'],
                   "agrar/psm-sachkunde-register-liste": ['PSM Sachkunde', 'psm-sachkunde-register-liste'],
                   "agrar/psm-wasserschutz-liste": ['Wasserschutz', 'psm-wasserschutz-liste'],
                   "agrar/saatgut-bestellungen-liste": ['Saatgut-Bestellungen', 'saatgut-bestellungen-liste'],
                   "agrar/saatgut-sortenregister-liste": ['Sortenregister', 'saatgut-sortenregister-liste'],
                   "agrar/schlaege-liste": ['Schlaege', 'schlaege-liste'],
                   "agrar/schlaege-karte-liste": ['Schlagkarte', 'schlaege-karte-liste'],
                   "agrar/schlaege-kulturhistorie-liste": ['Kulturhistorie', 'schlaege-kulturhistorie-liste'],
                   "agrar/vertrag-kontingente-liste": ['Vertrag-Kontingente', 'vertrag-kontingente-liste'],
                   "charge/wareneingang-liste": ['Wareneingang Chargen', 'wareneingang-liste'],
                   "compliance/bvl-umsatzmeldung-liste": ['BVL Umsatzmeldung', 'bvl-umsatzmeldung-liste'],
                   "compliance/eudr-compliance-liste": ['EUDR Compliance', 'eudr-compliance-liste'],
                   "compliance/export-pruefung-liste": ['Export-Pruefung', 'export-pruefung-liste'],
                   "compliance/gefahrstoff-doku-liste": ['Gefahrstoff-Doku', 'gefahrstoff-doku-liste'],
                   "compliance/qs-checkliste-liste": ['QS-Checkliste', 'qs-checkliste-liste'],
                   "controlling/plan-ist-liste": ['Plan-Ist', 'plan-ist-liste'],
                   "crm/contact-detail-liste": ['Kontakte', 'contact-detail-liste'],
                   "crm/kontakt-management-liste": ['Kontakt-Management', 'kontakt-management-liste'],
                   "crm/leads-liste": ['Leads', 'leads-liste'],
                   "einkauf/anfragen-create-liste": ['Anfragen', 'anfragen-create-liste'],
                   "einkauf/angebote-vergleich-liste": ['Angebotsvergleich', 'angebote-vergleich-liste'],
                   "einkauf/bestellvorschlaege-liste": ['Bestellvorschlaege', 'bestellvorschlaege-liste'],
                   "einkauf/dienstleistungen-haltung-liste": ['Dienstleistungen Haltung', 'dienstleistungen-haltung-liste'],
                   "einkauf/einkauf-vorgang-liste": ['Einkaufsvorgaenge', 'einkauf-vorgang-liste'],
                   "einkauf/kontrakte-service-liste": ['Kontrakte Service', 'kontrakte-service-liste'],
                   "einkauf/rechnung-abgleich-liste": ['Rechnungsabgleich', 'rechnung-abgleich-liste'],
                   "einkauf/retouren-liste": ['Retouren', 'retouren-liste'],
                   "etiketten/druck-liste": ['Etikettendruck', 'druck-liste'],
                   "export/intrastat-meldung-liste": ['Intrastat-Meldung', 'intrastat-meldung-liste'],
                   "export/umsatzsteuer-voranmeldung-liste": ['USt-Voranmeldung', 'umsatzsteuer-voranmeldung-liste'],
                   "fibu/anlagen-liste": ['Anlagen', 'anlagen-liste'],
                   "fibu/buchungsjournal-liste": ['Buchungsjournal', 'buchungsjournal-liste'],
                   "fibu/debitoren-liste": ['Debitoren OP', 'debitoren-liste'],
                   "fibu/hauptbuch-liste": ['Hauptbuch', 'hauptbuch-liste'],
                   "fibu/kassenbuch-liste": ['Kassenbuch', 'kassenbuch-liste'],
                   "fibu/kostenstellen-liste": ['Kostenstellen', 'kostenstellen-liste'],
                   "fibu/kreditoren-liste": ['Kreditoren OP', 'kreditoren-liste'],
                   "fibu/offene-posten-liste": ['Offene Posten', 'offene-posten-liste'],
                   "fibu/schnittstelle-fibu-liste": ['FIBU-Schnittstelle', 'schnittstelle-fibu-liste'],
                   "fibu/verbindlichkeiten-liste": ['Verbindlichkeiten', 'verbindlichkeiten-liste'],
                   "fibu/zahlungslaeufe-liste": ['Zahlungslaeufe', 'zahlungslaeufe-liste']}
