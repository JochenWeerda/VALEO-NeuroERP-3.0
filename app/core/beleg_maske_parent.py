"""BelegMaskeParent — gemeinsame Schablone fuer alle Belege (BELEG-020 + Vererbung).

Taxonomie: ``docs/architecture/uix/beleg-maskenfamilie-vererbung.md`` §2.
Alle 9 kanonischen Belegvarianten (sales/purchase + offer/order/delivery/invoice/credit_memo)
erben von dieser Parent-Schablone:

* Layout: ``transaction`` mit sticky Header/Footer, Register-Tabs (kopf/positionen/kette/dokumente/historie).
* Kopf: Beleg-Nr., Status, Belegdatum, Partner (Kunde/Lieferant je Variante).
* Positionen: Mengen immer; Preisspalten nur wenn Variante.mit_preisen.
* Summen: nur in preisenden Varianten.
* Belegkette: Navigation zu Vorgängern/Nachfolgern aus Variante.folgebelege.
* ProcessBand: Stand eines Vorgangs (Phasen, eine nächste Aktion, Blocker) — getrennt von ProcessRibbon.
* ProcessRibbon: Navigation der Belegfolge (DocFlow-Konvertierung) — nur in ProcessRibbon-Renderer, nicht im Band-Label.
* Aktionen: aus Belegkommandos, ``enabledWhen`` am Server-Feld aktion_<key>.

Strikte Trennung:
  - ProcessBand: Vorgangsstand anzeigen (welche Phasen, was ist nächste Aktion, was blockt).
    Label zeigt nur Phasennamen, nicht interne Prozessschlüssel.
  - ProcessRibbon: Belegketten-Navigation (über folgebelege-Liste und ConvertAction).
    Ribbons navigieren zu Zielmasken; Phasen und Blocker sind nicht Navigationsziele.

Kinder müssen nicht überschreiben:
  - Floorplan, Density, contextRail.
  - Reiter-Gerüst und deren Reihenfolge.
  - Kopf-/Positions-Basis (Layout-Parität/Gewohnheits-Prinzip).
  - DocFlow Create/Update (centralisiert).
  - Theme / Meridian (global).

Kinder können/müssen überschreiben:
  - Bezeichner (Partner-Label, Kopf-Feldtexte, Reiter-Labels).
  - Preisspalten wenn mit_preisen.
  - Summenblock wenn bucht.
  - Erlaubte Aktionen / Folgebelege.
  - testId/agentContract-Texte je Belegart.

Kandidaten (noch nicht in BELEGARTEN):
  - purchase_rfq (Anfrage), purchase_offer (Lieferantenangebot), debit_memo (Belastungsanzeige).
  Definition sauberer erst nach Variantenvertrag + Kettenprofil.
"""
from __future__ import annotations

from typing import Any

from app.core.belegkommandos import BELEGKOMMANDOS, Belegkommando
from app.core.belegvertrag import BELEGARTEN, Belegvariante


# ── Konstanten ──────────────────────────────────────────────────────────────

REITER: tuple[str, ...] = ("kopf", "positionen", "kette", "dokumente", "historie")
"""Unveraenderliche Register-Tabs in der Belegmaske (Vererbung)."""

_PARTNER_LABEL = {"kunde": "Kunde", "lieferant": "Lieferant"}
_RISIKO_MAPPING = {"R1": "safe", "R2": "safe", "R3": "moderate", "R4": "critical"}


# ── Hilfsfunktionen ────────────────────────────────────────────────────────

def screen_id(belegart: str) -> str:
    """Screen-ID (Familie) fuer eine Belegart: 'sales_invoice' -> 'beleg/sales-invoice'."""
    return f"beleg/{belegart.replace('_', '-')}"


def zustandsfeld(aktion_key: str) -> str:
    """Das Kopffeld, das der Server setzt, um zu sagen, ob eine Aktion gerade moeglich ist.
    Maske prueft ``enabledWhen: zustandsfeld(key)`` - der Server liefert true/false."""
    return "aktion_" + aktion_key.replace(":", "_")


def _pfad(belegart: str, rest: str = "") -> str:
    """API-Endpoint-Template fuer einen Belegart-Pfad."""
    return f"/api/v1/belege/{belegart}/{{entity_id}}{rest}"


def _spalte(key: str, label: str, **mehr: Any) -> dict[str, Any]:
    """Helper fuer Spaltendeklaration (Positionen/Kette/Dokumente/Historie)."""
    return {"key": key, "label": label, **mehr}


# ── Positions-Spalten-Builder ──────────────────────────────────────────────

def beleg_positionsspalten(variante: Belegvariante) -> list[dict[str, Any]]:
    """Spalten der Positionen-Tabelle.

    Mengen-Spalten (pos_nr, artikel_nr, bezeichnung, menge, einheit, charge)
    sind immer enthalten. Preisspalten (einzelpreis, rabatt, steuerschluessel, netto)
    nur wenn variante.mit_preisen. Offen-Spalte nur wenn Folgebelege.
    """
    spalten = [
        _spalte("pos_nr", "Pos.", width=50, sortable=True),
        _spalte("artikel_nr", "Artikel-Nr.", width=120, filterable=True),
        _spalte("bezeichnung", "Bezeichnung", width=220, filterable=True),
        _spalte("menge", "Menge", numeric=True, sortable=True, renderKind="number"),
        _spalte("einheit", "Einheit", width=70),
        _spalte("charge", "Charge", width=120),
    ]
    if variante.folgebelege:
        spalten.append(_spalte("menge_offen", "Offen", numeric=True, renderKind="number"))
    if variante.mit_preisen:
        spalten += [
            _spalte("einzelpreis", "Einzelpreis", numeric=True, renderKind="currency"),
            _spalte("rabatt_prozent", "Rabatt %", numeric=True, renderKind="number"),
            _spalte("steuerschluessel", "Steuerschlüssel", width=110),
            _spalte("netto", "Netto", numeric=True, renderKind="currency"),
        ]
        if variante.richtung == "einkauf":
            spalten.append(_spalte("aufwandskonto", "Aufwandskonto", width=110))
    return spalten


# ── Kopf-Felder-Builder ────────────────────────────────────────────────────

def beleg_kopffelder(variante: Belegvariante) -> list[dict[str, Any]]:
    """Kopf-Felder: Beleg-Nr., Status, Datum, Partner, Preissummen, Buchungsstand, Aktionshinweise.

    Child kann diese Liste erweitern oder anpassen, aber die Basis ist vertragsgerecht.
    """
    def feld(key: str, label: str, typ: str = "text") -> dict[str, Any]:
        return {"key": key, "label": label, "type": typ, "readOnly": True}

    partner = _PARTNER_LABEL[variante.partnerrolle]
    felder = [
        feld("beleg_nr", f"{variante.bezeichnung} Nr."),
        feld("status", "Status"),
        feld("belegdatum", "Belegdatum", "date"),
        feld("partner_nummer", f"{partner}-Nr."),
        feld("partner_name", partner),
    ]
    if variante.mit_preisen:
        felder += [
            feld("waehrung", "Währung"),
            feld("netto", "Netto", "currency"),
            feld("steuer", "Vorsteuer" if variante.richtung == "einkauf" else "Umsatzsteuer", "currency"),
            feld("brutto", "Brutto", "currency"),
        ]
    if variante.bucht:
        felder += [
            feld("buchungsstand", "Buchung"),
            feld("buchungsgrund", "Hinweis zur Buchung"),
        ]
    felder.append(feld("aktionshinweis", "Hinweise zu Aktionen", "textarea"))
    return felder


# ── Tabellen-Helper (Kette, Dokumente, Historie) ───────────────────────────

def beleg_kette_tab() -> dict[str, Any]:
    """Belegketten-Register: Vorgaenger und Nachfolger (Read-only)."""
    return {
        "key": "kette",
        "label": "Belegkette",
        "lazy": True,
        "keepAlive": False,
        "tables": [{
            "key": "kette",
            "label": "Belegkette",
            "dataSourceKey": "kette",
            "serverPagination": True,
            "pageSize": 25,
            "virtualized": True,
            "rowHeight": 52,
            "columns": [
                _spalte("richtung", "Richtung", width=110, filterable=True),
                _spalte("bezeichnung", "Belegart", width=160, filterable=True),
                _spalte("beleg_nr", "Beleg-Nr.", width=160),
                _spalte("status", "Status", width=110),
                _spalte("menge", "Menge", numeric=True, renderKind="number"),
            ],
        }],
    }


def beleg_dokumente_tab() -> dict[str, Any]:
    """Dokumente-Register: eingescannte/hochgeladene Belege."""
    return {
        "key": "dokumente",
        "label": "Dokumente",
        "lazy": True,
        "keepAlive": False,
        "tables": [{
            "key": "dokumente",
            "label": "Dokumente",
            "dataSourceKey": "dokumente",
            "serverPagination": True,
            "pageSize": 25,
            "virtualized": True,
            "rowHeight": 52,
            "columns": [
                _spalte("datum", "Datum", sortable=True, renderKind="date", width=110),
                _spalte("art", "Art", width=90, filterable=True),
                _spalte("bezeichnung", "Bezeichnung", width=240, filterable=True),
                _spalte("version", "Version", numeric=True, width=80),
                _spalte("stand", "Stand", width=120),
            ],
        }],
    }


def beleg_historie_tab() -> dict[str, Any]:
    """Historie-Register: Statusuebergaenge und Auditpfad."""
    return {
        "key": "historie",
        "label": "Verlauf",
        "lazy": True,
        "keepAlive": False,
        "tables": [{
            "key": "historie",
            "label": "Verlauf",
            "dataSourceKey": "historie",
            "serverPagination": True,
            "pageSize": 25,
            "virtualized": True,
            "rowHeight": 52,
            "columns": [
                _spalte("zeitpunkt", "Zeitpunkt", sortable=True, renderKind="datetime", width=160),
                _spalte("von_status", "Von", width=110),
                _spalte("nach_status", "Nach", width=110, filterable=True),
                _spalte("kommando", "Aktion", width=130),
                _spalte("akteur", "Durch", width=160),
                _spalte("grund", "Grund", width=260),
            ],
        }],
    }


# ── Datensquellen-Builder ──────────────────────────────────────────────────

def beleg_data_sources(belegart: str) -> list[dict[str, Any]]:
    """Zentrale Datensquellen fuer einen Beleg (alle Kinder gleich)."""
    return [
        {"key": "entity", "endpoint": _pfad(belegart, "/kopf")},
        {"key": "positionen", "endpoint": _pfad(belegart, "/tabs/positionen"), "pageSize": 50},
        {"key": "kette", "endpoint": _pfad(belegart, "/tabs/kette"), "pageSize": 25},
        {"key": "dokumente", "endpoint": _pfad(belegart, "/tabs/dokumente"), "pageSize": 25},
        {"key": "historie", "endpoint": _pfad(belegart, "/tabs/historie"), "pageSize": 25},
    ]


# ── Aktionen-Builder ────────────────────────────────────────────────────────

def _aktion(
    key: str,
    label: str,
    kommando: Belegkommando,
    *,
    kind: str = "secondary",
    **mehr: Any,
) -> dict[str, Any]:
    """Einzelne Belegaktion aus Kommando, mit enabledWhen, Permission, Bestätigung."""
    return {
        "key": key,
        "label": label,
        "kind": kind,
        "enabledWhen": zustandsfeld(key),
        "dangerLevel": _RISIKO_MAPPING[kommando.risiko],
        "requiresConfirmation": kommando.freigabe_noetig,
        "permission": f"belege.{kommando.recht}",
        "commandEndpoint": f"/api/v1{kommando.pfad}".replace("{doc_id}", "{entity_id}"),
        "method": kommando.methode,
        "kommando": kommando.name,
        "commandBinding": {
            "adapter": "docflow.v1",
            "command": kommando.name.removeprefix("docflow."),
            "preview": kommando.name == "docflow.convert",
        },
        "forbiddenForAgents": True,  # MCP-WRITE-014: keine schreibende Freischaltung per SD
        "auditReasonRequired": kommando.name == "docflow.reverse",
        **mehr,
    }


def beleg_aktionen(variante: Belegvariante) -> list[dict[str, Any]]:
    """Alle erlaubten Aktionen fuer eine Belegvariante.

    Basis: Bearbeiten, Freigeben, Buchen (wenn bucht), Umwandeln (wenn Folgebelege),
    Stornieren, Freigabe-Anfragen und -Entscheidungen.
    """
    zeilenfelder = [
        {"key": "article_number", "label": "Artikel-Nr.", "type": "text", "required": True},
        {"key": "description", "label": "Bezeichnung", "type": "text"},
        {"key": "quantity", "label": "Menge", "type": "number", "required": True},
        {"key": "unit", "label": "Einheit", "type": "text"},
        {"key": "charge", "label": "Charge", "type": "text"},
    ]
    if variante.mit_preisen:
        zeilenfelder += [
            {"key": "unit_price", "label": "Einzelpreis", "type": "currency", "required": True},
            {"key": "discount_percent", "label": "Rabatt %", "type": "number"},
            {"key": "tax_code", "label": "Steuerschluessel", "type": "text"},
            {"key": "tax_rate", "label": "Steuersatz %", "type": "number"},
        ]
        if variante.richtung == "einkauf":
            zeilenfelder.append({"key": "expense_account", "label": "Aufwandskonto", "type": "text"})

    liste: list[dict[str, Any]] = [
        _aktion(
            "bearbeiten",
            "Beleg bearbeiten",
            BELEGKOMMANDOS["docflow.update"],
            inputFields=[
                {"key": "document_date", "label": "Belegdatum", "type": "date", "required": True},
                {"key": "currency", "label": "Waehrung", "type": "text", "required": True},
                {"key": "source_ref", "label": "Externe Referenz", "type": "text"},
                {
                    "key": "items",
                    "label": "Positionen",
                    "type": "table",
                    "required": True,
                    "rowFields": zeilenfelder,
                    "tableEditing": {"allowAdd": True, "allowDelete": True, "maxRows": 200},
                },
            ],
        ),
        _aktion("freigeben", "Freigeben", BELEGKOMMANDOS["docflow.release"]),
    ]
    if variante.bucht:
        liste.append(_aktion("buchen", "Buchen", BELEGKOMMANDOS["docflow.post"]))
    for folgeart in variante.folgebelege:
        liste.append(
            _aktion(
                f"umwandeln:{folgeart}",
                f"{BELEGARTEN[folgeart].bezeichnung} erstellen",
                BELEGKOMMANDOS["docflow.convert"],
                folgebelegart=folgeart,
                commandBinding={
                    "adapter": "docflow.v1",
                    "command": "convert",
                    "preview": True,
                    "defaults": {"target_doc_type": folgeart},
                },
            )
        )
    liste.append(_aktion("stornieren", "Stornieren", BELEGKOMMANDOS["docflow.reverse"]))

    for fachaktion in (("post", "reverse") if variante.bucht else ("reverse",)):
        recht = "buchen" if fachaktion == "post" else "stornieren"
        freigaberecht = "freigeben" if fachaktion == "post" else "freigeben_erhoeht"
        bezug = "Buchung" if fachaktion == "post" else "Storno"
        liste.append(
            _aktion(
                f"freigabe_anfordern:{fachaktion}",
                f"{bezug}: Freigabe anfragen",
                BELEGKOMMANDOS["docflow.approval_request"],
                permission=f"belege.{recht}",
                commandBinding={
                    "adapter": "docflow.v1",
                    "command": "approval_request",
                    "preview": False,
                    "defaults": {"action": fachaktion},
                },
                inputFields=[{"key": "reason", "label": "Grund der Anfrage", "type": "textarea"}],
            )
        )
        for erteilt, verb in ((True, "erteilen"), (False, "ablehnen")):
            state_action = f"freigabe_erteilen:{fachaktion}"
            liste.append(
                _aktion(
                    f"freigabe_{verb}:{fachaktion}",
                    f"{bezug}: Freigabe {verb}",
                    BELEGKOMMANDOS["docflow.approval_decide"],
                    permission=f"belege.{freigaberecht}",
                    enabledWhen=zustandsfeld(state_action),
                    requiresConfirmation=True,
                    commandBinding={
                        "adapter": "docflow.v1",
                        "command": "approval_decide",
                        "preview": False,
                        "stateAction": state_action,
                        "defaults": {"granted": erteilt, "action": fachaktion},
                    },
                    inputFields=[{"key": "note", "label": "Pruefvermerk", "type": "textarea", "required": True}],
                )
            )

    haupt = "buchen" if variante.bucht else (f"umwandeln:{variante.folgebelege[0]}" if variante.folgebelege else "freigeben")
    for aktion in liste:
        if aktion["key"] == haupt:
            aktion["kind"] = "primary"
    return liste


# ── Layout (Meridian + Floorplan) ───────────────────────────────────────────

_DEFAULT_NO_WORKFLOW_REASON = (
    "Der Stand des Belegs wird vom Server-Status Kopf:status gespeist."
)

_PRODUCTION_NO_WORKFLOW_REASON = (
    "Der Stand des Belegs und die naechste moegliche Aktion kommen je Beleg vom Server "
    "(aktionen des Belegvertrags); die Maske fuehrt keinen eigenen Ablauf."
)


def beleg_meridian_layout_extras(variante: Belegvariante) -> dict[str, Any]:
    """Meridian-Profil fuer Belegmasken (density, contextRail, tableProfile).

    Wird erst mit dem naechsten ``document_screen_versions``-Release materialisiert;
    der produktive Builder nutzt ``meridian_profile=False``, bis die Registry nachzieht.
    """
    return {
        "density": "compact",
        "contextRail": "workflow",
        "tableProfile": "financial" if variante.mit_preisen else "standard",
    }


def beleg_layout(
    variante: Belegvariante,
    *,
    meridian_profile: bool = False,
    register_tabs: bool = False,
) -> dict[str, Any]:
    """Floorplan und Meridian-Metadaten fuer Beleg-Detailmasken."""
    layout: dict[str, Any] = {
        "preferredMode": "desktopDense",
        "mobileMode": "mobileStack",
        "touchTargetPx": 44,
        "floorplan": "transaction",
        "sectionNavigation": "anchors",
        "summaryPlacement": "footer",
        "stickyHeader": True,
        "stickyFooter": True,
    }
    if register_tabs:
        layout["registerTabs"] = True
    if meridian_profile:
        layout.update(beleg_meridian_layout_extras(variante))
    return layout


def beleg_interaction() -> dict[str, Any]:
    return {"enterMovesFocus": True}


def beleg_performance(bereich: str) -> dict[str, Any]:
    return {
        "initialPayloadBudgetKb": 48,
        "requiresLazyTabs": True,
        "requiresVirtualTables": True,
        "lookupMinChars": 2,
        "bundleGroup": bereich,
    }


# ── Parent-Konstruktor ──────────────────────────────────────────────────────

def build_beleg_maske_parent(
    belegart: str,
    *,
    business_purpose: str,
    example_prompts: list[str],
    test_id: str,
    sensitive_fields: list[str] | None = None,
    extra_kopffelder: list[dict[str, Any]] | None = None,
    extra_aktionen: list[dict[str, Any]] | None = None,
    creation: dict[str, Any] | None = None,
    workflow: dict[str, Any] | None = None,
    meridian_profile: bool = False,
    register_tabs: bool = False,
    test_selectors: dict[str, str] | None = None,
    no_workflow_reason: str | None = None,
    no_process_chain_reason: str | None = None,
) -> dict[str, Any]:
    """BelegMaskeParent: ScreenDefinition fuer eine Belegart.

    Belegart muss in BELEGARTEN registriert sein. Die Maske erbt:
    - Floorplan transaction, sticky Header/Footer.
    - Register-Tabs (kopf/positionen/kette/dokumente/historie) — Reihenfolge unveraendert.
    - Kopf-Basis (Beleg-Nr., Status, Partner, Summen wenn mit_preisen, Buchungsstand wenn bucht).
    - Aktionen (Bearbeiten, Freigeben, Buchen, Umwandeln, Stornieren, Freigaben).
    - DataSources fuer alle Tabs.
    - Theme/Meridian (global).

    Child kann:
    - extra_kopffelder: zusaetzliche Felder hinzufuegen (muessen NACH den Basis-Feldern kommen).
    - extra_aktionen: weitere Fachaktionen ergaenzen.
    - business_purpose, example_prompts, test_id, sensitive_fields: Belegart-spezifisch.
    - creation: abweichender Create-Flow (aber Default ist DocFlow).
    - workflow: Prozess-Definition (BELEG-020 Entscheidung: ProcessBand koennte hier kommen,
                aber aktuell ist noWorkflowReason Standard).

    ProcessBand-Invariante: Das Band zeigt den Stand eines *Vorgangs* (Phasen, eine naechste
    Aktion, Blocker). Es erbt von Parent; Child darf nicht eigene Phasendefinition in die
    Maske schreiben. Die Phasen kommen aus workflow.phases (noch nicht konfiguriert als
    Standard-Override; Erweiterung geplant).

    ProcessRibbon-Invariante: Das Ribbon navigiert die *Belegkette* (Schritt -> Zielmaske).
    Es ist **nicht** Teil des ProcessBand-Labels. Das Ribbon wird vom Renderer aus
    folgebelege + ConvertAction aufgebaut; Phasen-Chevrons sind eine reine Visualisierungssache,
    keine Navigation.
    """
    if belegart not in BELEGARTEN:
        raise ValueError(f"Belegart {belegart!r} hat keine Variante in BELEGARTEN")

    variante = BELEGARTEN[belegart]
    kennung = screen_id(belegart)
    partner = _PARTNER_LABEL[variante.partnerrolle]
    bereich = "einkauf" if variante.richtung == "einkauf" else "sales"

    # Tabs zusammenstellen: kopf, positionen, kette, dokumente, historie.
    kopf_felder = beleg_kopffelder(variante)
    if extra_kopffelder:
        kopf_felder.extend(extra_kopffelder)

    tabs = [
        {
            "key": "kopf",
            "label": f"{variante.bezeichnung} – Kopf",
            "lazy": False,
            "keepAlive": True,
            "dataSourceKey": "entity",
            "fields": kopf_felder,
        },
        {
            "key": "positionen",
            "label": "Positionen",
            "lazy": True,
            "keepAlive": False,
            "tables": [{
                "key": "positionen",
                "label": "Positionen",
                "dataSourceKey": "positionen",
                "serverPagination": True,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 52,
                "columns": beleg_positionsspalten(variante),
            }],
        },
        beleg_kette_tab(),
        beleg_dokumente_tab(),
        beleg_historie_tab(),
    ]

    # Aktionen zusammenstellen: Basis + extra.
    aktionen = beleg_aktionen(variante)
    if extra_aktionen:
        aktionen.extend(extra_aktionen)

    # Definition zusammenstellen.
    definition: dict[str, Any] = {
        "schemaVersion": 1,
        "id": kennung,
        "domain": bereich,
        "mode": "detail",
        "title": variante.bezeichnung,
        "subtitle": f"{partner} · {'mit Preisen' if variante.mit_preisen else 'nur Mengen'}",
        "identityField": "beleg_nr",
        "adapter": {"type": "native", "sourceId": kennung, "temporary": False},
        "variant": {
            "of": "beleg",
            "belegart": belegart,
            "partnerrolle": variante.partnerrolle,
            "mitPreisen": variante.mit_preisen,
            "bucht": variante.bucht,
            "folgebelege": list(variante.folgebelege),
        },
        "dataSources": beleg_data_sources(belegart),
        "tabs": tabs,
        "actions": aktionen,
        "agentContract": {
            "businessPurpose": business_purpose,
            "examplePrompts": example_prompts,
            "sensitiveFields": list(sensitive_fields or []),
            "testSelectors": test_selectors
            or {
                "screenRoot": f"[data-testid='{test_id}']",
                "primaryAction": "[data-testid='action-umwandeln' i]",
                "summaryArea": "[data-testid='beleg-kopf']",
            },
        },
        "layout": beleg_layout(variante, meridian_profile=meridian_profile, register_tabs=register_tabs),
        "interaction": beleg_interaction(),
        "performance": beleg_performance(bereich),
    }

    if creation is not None:
        definition["creation"] = creation
    else:
        # Default: DocFlow Create.
        definition["creation"] = {
            "adapter": "docflow.create.v1",
            "endpoint": "/api/v1/docflow/",
            "permission": "belege.bearbeiten",
            "detailRoute": f"/belege/{belegart}/{{entity_id}}",
            "defaults": {"currency": "EUR", "items": []},
            "dataSources": [
                {"key": "partner", "endpoint": f"/api/v1/belege/{belegart}/partner-auswahl"}
            ],
            "fields": [
                {
                    "key": "doc_number",
                    "label": "Entwurfsbezeichnung",
                    "type": "text",
                    "required": True,
                },
                {
                    "key": "supplier_id" if variante.partnerrolle == "lieferant" else "customer_id",
                    "label": partner,
                    "type": "lookup",
                    "dataSourceKey": "partner",
                    "required": True,
                },
                *next(
                    (action["inputFields"] for action in aktionen if action["key"] == "bearbeiten"),
                    [],
                ),
            ],
        }

    if workflow is not None:
        definition["workflow"] = workflow
    else:
        definition["noWorkflowReason"] = no_workflow_reason or _DEFAULT_NO_WORKFLOW_REASON

    if no_process_chain_reason:
        definition["noProcessChainReason"] = no_process_chain_reason

    return definition
