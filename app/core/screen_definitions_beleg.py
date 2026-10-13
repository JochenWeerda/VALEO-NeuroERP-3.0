"""Eine Belegmaske, neun Varianten (BELEG-020).

Entscheidung des Auftraggebers vom 13.10.2026: Fuer jeden Schritt einer Belegfolge keine eigene Maske, sondern
die Variante einer Belegmaske — oft aendert sich nur die Bezeichnung, mal mit Preisen (Rechnung), mal nur mit
Mengen (Lieferschein).

``build_beleg_screen_definition(belegart)`` erzeugt aus einem Grundgeruest und der Variante des Belegvertrags
(``app/core/belegvertrag.py``) eine ScreenDefinition. Es gibt keine ausgeschriebene Definition je Belegart:

* Titel und Beschriftungen kommen aus der Variante (Bezeichnung, Partnerrolle).
* Preisspalten und Summenfelder gibt es nur in Varianten mit Preisen.
* Aktionen kommen aus dem Verzeichnis der Belegkommandos, Folgebelege aus der Variante.
* Gelesen wird ueber den Belegweg (``/api/v1/belege/…``); die Maske kennt keinen Speicher.

Die Definition beschreibt, was die Maske zeigen *kann*. Was der Leser sieht und darf, entscheidet der Server je
Beleg: ohne Preisrecht kommen die Preisfelder leer, und welche Aktion im Zustand des Belegs moeglich ist, sagt
``aktionen`` des Belegvertrags. Jede Aktion der Definition haengt ueber ``enabledWhen`` an einem Kopffeld
``aktion_<schluessel>``, das der Kopfweg aus ``aktionen`` setzt; die Sperrgruende stehen in ``aktionshinweis``.

Stand: Die Definitionen sind erzeugbar und geprueft, aber noch nicht in der Registry der Masken eingetragen —
der Eintrag folgt mit der Sichtpruefung im Browser (Entscheidung E4: keine Maskenmigration ohne sie).
"""
from __future__ import annotations

from typing import Any

from app.core.belegkommandos import BELEGKOMMANDOS, Belegkommando
from app.core.belegvertrag import BELEGARTEN, Belegvariante

REITER: tuple[str, ...] = ("kopf", "positionen", "kette", "dokumente", "historie")

_PARTNER = {"kunde": "Kunde", "lieferant": "Lieferant"}
_GEFAHR = {"R1": "safe", "R2": "low", "R3": "moderate", "R4": "critical"}


def screen_id(belegart: str) -> str:
    return f"beleg/{belegart.replace('_', '-')}"


def zustandsfeld(aktion_key: str) -> str:
    """Das Kopffeld, das sagt, ob eine Aktion fuer diesen Beleg und diesen Leser jetzt moeglich ist."""
    return "aktion_" + aktion_key.replace(":", "_")


def _pfad(belegart: str, rest: str = "") -> str:
    return f"/api/v1/belege/{belegart}/{{entity_id}}{rest}"


def _spalte(key: str, label: str, **mehr: Any) -> dict[str, Any]:
    return {"key": key, "label": label, **mehr}


def positionsspalten(variante: Belegvariante) -> list[dict[str, Any]]:
    """Die Spalten der Positionen — Mengen immer, Preise nur in Varianten mit Preisen."""
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


def kopffelder(variante: Belegvariante) -> list[dict[str, Any]]:
    def feld(key: str, label: str, typ: str = "text") -> dict[str, Any]:
        return {"key": key, "label": label, "type": typ, "readOnly": True}

    partner = _PARTNER[variante.partnerrolle]
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
        felder += [feld("buchungsstand", "Buchung"), feld("buchungsgrund", "Hinweis zur Buchung")]
    # Warum eine Aktion gerade nicht geht: der Sperrgrund vom Server, nicht eine Vermutung der Maske.
    felder.append(feld("aktionshinweis", "Hinweise zu Aktionen", "textarea"))
    return felder


def _aktion(key: str, label: str, kommando: Belegkommando, *, kind: str = "secondary", **mehr: Any) -> dict[str, Any]:
    return {
        "key": key, "label": label, "kind": kind,
        # Der Knopf ist nur aktiv, wenn der Server die Aktion fuer diesen Beleg und diesen Leser erlaubt
        # (Zustand, Recht, Freigabe). Fehlt das Feld, ist er gesperrt.
        "enabledWhen": zustandsfeld(key),
        "dangerLevel": _GEFAHR[kommando.risiko],
        # Ab R3 bestaetigt der Mensch die Aktion ausdruecklich.
        "requiresConfirmation": kommando.freigabe_noetig,
        "permission": f"belege.{kommando.recht}",
        "commandEndpoint": f"/api/v1{kommando.pfad}".replace("{doc_id}", "{entity_id}"),
        "method": kommando.methode,
        "kommando": kommando.name,
        **mehr,
    }


def aktionen(variante: Belegvariante) -> list[dict[str, Any]]:
    """Was die Maske anbieten kann. Genau eine Hauptaktion: der naechste Schritt der Belegfolge."""
    liste: list[dict[str, Any]] = [_aktion("freigeben", "Freigeben", BELEGKOMMANDOS["docflow.release"])]
    if variante.bucht:
        liste.append(_aktion("buchen", "Buchen", BELEGKOMMANDOS["docflow.post"]))
    for folgeart in variante.folgebelege:
        liste.append(_aktion(
            f"umwandeln:{folgeart}", f"{BELEGARTEN[folgeart].bezeichnung} erstellen", BELEGKOMMANDOS["docflow.convert"],
            folgebelegart=folgeart,
        ))
    liste.append(_aktion("stornieren", "Stornieren", BELEGKOMMANDOS["docflow.reverse"]))
    haupt = "buchen" if variante.bucht else (f"umwandeln:{variante.folgebelege[0]}" if variante.folgebelege else "freigeben")
    for aktion in liste:
        if aktion["key"] == haupt:
            aktion["kind"] = "primary"
    return liste


def _tabelle(key: str, label: str, spalten: list[dict[str, Any]], seite: int = 50) -> dict[str, Any]:
    return {"key": key, "label": label, "dataSourceKey": key, "serverPagination": True, "pageSize": seite,
            "virtualized": True, "rowHeight": 52, "columns": spalten}


def build_beleg_screen_definition(belegart: str) -> dict[str, Any]:
    variante = BELEGARTEN[belegart]
    kennung = screen_id(belegart)
    partner = _PARTNER[variante.partnerrolle]
    bereich = "einkauf" if variante.richtung == "einkauf" else "sales"
    return {
        "schemaVersion": 1,
        "id": kennung,
        "domain": bereich,
        "mode": "detail",
        "title": variante.bezeichnung,
        "subtitle": f"{partner} · {'mit Preisen' if variante.mit_preisen else 'nur Mengen'}",
        "identityField": "beleg_nr",
        "adapter": {"type": "native", "sourceId": kennung, "temporary": False},
        # Die Variante als Begriff der Definition: Belegart und was sie vom Grundgeruest unterscheidet.
        "variant": {
            "of": "beleg", "belegart": belegart, "partnerrolle": variante.partnerrolle,
            "mitPreisen": variante.mit_preisen, "bucht": variante.bucht, "folgebelege": list(variante.folgebelege),
        },
        "dataSources": [
            {"key": "entity", "endpoint": _pfad(belegart, "/kopf")},
            {"key": "positionen", "endpoint": _pfad(belegart, "/tabs/positionen"), "pageSize": 50},
            {"key": "kette", "endpoint": _pfad(belegart, "/tabs/kette"), "pageSize": 25},
            {"key": "dokumente", "endpoint": _pfad(belegart, "/tabs/dokumente"), "pageSize": 25},
            {"key": "historie", "endpoint": _pfad(belegart, "/tabs/historie"), "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": f"{variante.bezeichnung} – Kopf", "lazy": False, "keepAlive": True,
             "dataSourceKey": "entity", "fields": kopffelder(variante)},
            {"key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": False,
             "tables": [_tabelle("positionen", "Positionen", positionsspalten(variante))]},
            {"key": "kette", "label": "Belegkette", "lazy": True, "keepAlive": False,
             "tables": [_tabelle("kette", "Belegkette", [
                 _spalte("richtung", "Richtung", width=110, filterable=True),
                 _spalte("bezeichnung", "Belegart", width=160, filterable=True),
                 _spalte("beleg_nr", "Beleg-Nr.", width=160),
                 _spalte("status", "Status", width=110),
                 _spalte("menge", "Menge", numeric=True, renderKind="number"),
             ], 25)]},
            {"key": "dokumente", "label": "Dokumente", "lazy": True, "keepAlive": False,
             "tables": [_tabelle("dokumente", "Dokumente", [
                 _spalte("datum", "Datum", sortable=True, renderKind="date", width=110),
                 _spalte("art", "Art", width=90, filterable=True),
                 _spalte("bezeichnung", "Bezeichnung", width=240, filterable=True),
                 _spalte("version", "Version", numeric=True, width=80),
                 _spalte("stand", "Stand", width=120),
             ], 25)]},
            {"key": "historie", "label": "Verlauf", "lazy": True, "keepAlive": False,
             "tables": [_tabelle("historie", "Verlauf", [
                 _spalte("zeitpunkt", "Zeitpunkt", sortable=True, renderKind="datetime", width=160),
                 _spalte("von_status", "Von", width=110),
                 _spalte("nach_status", "Nach", width=110, filterable=True),
                 _spalte("kommando", "Aktion", width=130),
                 _spalte("akteur", "Durch", width=160),
                 _spalte("grund", "Grund", width=260),
             ], 25)]},
        ],
        "actions": aktionen(variante),
        "noWorkflowReason": "Der Stand des Belegs und die naechste moegliche Aktion kommen je Beleg vom Server "
                            "(aktionen des Belegvertrags); die Maske fuehrt keinen eigenen Ablauf.",
        "agentContract": {
            "businessPurpose": (
                f"{variante.bezeichnung} lesen: Kopf, {partner}, Positionen"
                f"{' mit Preisen und Summen' if variante.mit_preisen else ' (nur Mengen)'}, Belegkette, Dokumente und Verlauf. "
                "Dieselben Daten liefert das MCP-Werkzeug beleg.lesen."
            ),
            "examplePrompts": [
                f"Zeige die Positionen von {variante.bezeichnung} {{entity_id}}.",
                f"Aus welchem Beleg ist {variante.bezeichnung} {{entity_id}} entstanden?",
                f"Was ist der Stand von {variante.bezeichnung} {{entity_id}}, und was geht als Nächstes?",
            ],
            "sensitiveFields": ["netto", "steuer", "brutto", "einzelpreis", "rabatt_prozent"] if variante.mit_preisen else [],
            "testSelectors": {"screenRoot": f"[data-testid='beleg-{belegart.replace('_', '-')}']",
                              "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44,
                   "floorplan": "transaction", "sectionNavigation": "anchors", "summaryPlacement": "footer",
                   "stickyHeader": True, "stickyFooter": True},
        "interaction": {"enterMovesFocus": True},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True,
                        "lookupMinChars": 2, "bundleGroup": bereich},
    }


def alle_beleg_screen_definitions() -> dict[str, dict[str, Any]]:
    return {screen_id(art): build_beleg_screen_definition(art) for art in BELEGARTEN}
