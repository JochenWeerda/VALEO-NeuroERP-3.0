"""Maskenfamilien des Kontrakt-Vorgangs (Nutzerentscheidung 08.11.2026: Varianten statt Einzelmasken).

``kontrakt-liste`` (Worklist) — eine Liste, acht Varianten: Uebersicht, Erfuellungsstand, Fixierung, Abrechnung,
Mahnung, Alarme, Engagement je Artikel, Engagement je Partner. Die Varianten unterscheiden sich in Quelle, Spalten,
Zeilenziel und Zeilenaktion; Floorplan, Dichte, Export und Ansichtswechsel teilen sie.

``kontrakt`` (Objektseite je Kontrakt) — ein Kopf, drei Varianten: Erfuellung, Fixierung, Abrechnung. Alle lesen
denselben Kopf (``/api/v1/kontrakt-vorgang/{entity_id}``); je Variante wechseln Reiter, sichtbare Positionsspalten,
Kennzahlen und Aktionen — so wie bei der Belegfolge Preise nur auf der Rechnung stehen.

Versioniert werden die Varianten in ``config/mask_families/<familie>.json`` (``app/core/mask_family_versions.py``);
die Registry liefert die materialisierte, gehashte Fassung aus, nicht diese Builder.
"""
from __future__ import annotations

from typing import Any

from app.core.cluster_spalten import betrag, datum, janein, menge, status, text, zahl
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action

LISTE = "kontrakt-liste"
VORGANG = "kontrakt"
_WEG = "/api/v1/kontrakt-vorgang"
_RECHT_SCHREIBEN = "kontrakt.update"

# Landhandel rechnet Masse in dt (app/core/agrar_units.py); die Kontrakteinheit steht je Zeile.
_DT = "dt"


def _m(key: str, label: str, *, summe: bool = False, prioritaet: str = "primary") -> dict[str, Any]:
    return menge(key, label, einheit_feld="einheit", anzeige=_DT, summe=summe, prioritaet=prioritaet)


def _prozent(key: str, label: str, prioritaet: str = "primary") -> dict[str, Any]:
    return {"key": key, "label": label, "renderKind": "percentage", "numeric": True, "sortable": True,
            "priority": prioritaet}


# ── Familie kontrakt-liste ─────────────────────────────────────────────────────

_LISTEN_TITEL = {
    "uebersicht": "Kontrakte",
    "erfuellung": "Erfüllungsstand",
    "fixierung": "Fixierung",
    "abrechnung": "Abrechnung",
    "mahnung": "Kontraktmahnung",
    "alarme": "Kontrakt-Alarme",
    "engagement_artikel": "Engagement je Artikel",
    "engagement_partei": "Engagement je Partner",
}


def _ansichten(aktuell: str) -> list[dict[str, Any]]:
    """Wechsel zwischen den Varianten derselben Liste (reine Navigation)."""
    return [{"key": f"ansicht_{v}", "label": titel, "kind": "secondary", "dangerLevel": "safe", "zone": "header",
             "navigationRoute": f"/kontrakte/listen/{v.replace('_', '-')}", "localEffect": "navigation",
             "stubReason": f"Wechselt zur Variante {titel} derselben Kontraktliste."}
            for v, titel in _LISTEN_TITEL.items() if v != aktuell]


def _vorgang_route(variante: str, feld: str = "id") -> str:
    return f"/kontrakte/vorgang/{variante}/{{{feld}}}"


def _liste(variante: str, *, subtitle: str, endpoint: str, columns: list[dict[str, Any]], purpose: str,
           prompts: list[str], row_route: str | None, row_actions: list[dict[str, Any]] | None = None,
           table_profile: str = "inventory") -> dict[str, Any]:
    definition = build_stamm_list_screen(
        screen_id=f"{LISTE}/{variante.replace('_', '-')}", domain="agrar", bundle="kontrakte",
        title=_LISTEN_TITEL[variante], subtitle=subtitle, endpoint=endpoint, row_route=row_route, columns=columns,
        actions=[stamm_list_export_action(), *_ansichten(variante)], row_actions=row_actions or [],
        purpose=purpose, prompts=prompts, table_profile=table_profile, fetch_limit=500,
        no_workflow="Auswertungsliste der Kontraktfamilie; der Vorgang je Kontrakt laeuft in der Kontrakt-Objektseite.")
    definition["variant"] = {"family": LISTE, "id": variante}
    return definition


_MAHNEN = {
    "key": "mahnen", "label": "Mahnen", "kind": "secondary", "dangerLevel": "moderate", "permission": _RECHT_SCHREIBEN,
    "commandEndpoint": _WEG + "/{entity_id}/actions/mahnen", "method": "POST", "requiresConfirmation": True,
    "inputFields": [{"key": "text", "label": "Mahntext", "type": "textarea"}],
}


def kontrakt_liste_varianten() -> dict[str, dict[str, Any]]:
    return {
        "uebersicht": _liste(
            "uebersicht", subtitle="Einkaufs- und Verkaufskontrakte mit Restmenge und Alarmen",
            endpoint=_WEG + "/uebersicht", row_route=_vorgang_route("erfuellung"),
            columns=[text("contract_no", "Kontrakt", "primary"), status("contract_type", "Art"),
                     text("partner_name", "Partner", "primary"), text("artikel", "Artikel"),
                     menge("total_quantity", "Menge", einheit_feld="unit", anzeige=_DT),
                     menge("rest_quantity", "Rest", einheit_feld="unit", anzeige=_DT, summe=True),
                     betrag("preis", "Preis", summe=False, prioritaet="secondary"),
                     text("pricing_model", "Preismodell", "tertiary"), datum("valid_from", "Gültig ab", "tertiary"),
                     datum("valid_to", "Gültig bis", "primary"), status(), zahl("alarme", "Alarme", "primary")],
            purpose="Alle Kontrakte mit Restmenge, Laufzeit und offenen Alarmen finden und den Vorgang oeffnen.",
            prompts=["Welche Verkaufskontrakte laufen diesen Monat aus?", "Wie viel Restmenge Weizen ist offen?"]),
        "erfuellung": _liste(
            "erfuellung", subtitle="Kontrahiert gegen abgerufen, je Kontrakt",
            endpoint=_WEG + "/erfuellungsstand", row_route=_vorgang_route("erfuellung"),
            columns=[text("contract_no", "Kontrakt", "primary"), status("typ", "Art"),
                     text("partner_name", "Partner", "primary"), _m("menge_kontrakt", "Kontrahiert"),
                     _m("abgerufen", "Abgerufen", summe=True), _m("offen", "Offen", summe=True),
                     _prozent("erfuellung_pct", "Erfüllung"), status("erfuellung_status", "Erfüllungsstand"),
                     datum("valid_to", "Gültig bis"), janein("ueberfaellig", "Überfällig", "primary")],
            purpose="Erfuellungsgrad je Kontrakt pruefen und untererfuellte oder ueberfaellige Kontrakte finden.",
            prompts=["Welche Kontrakte sind ueberfaellig und noch offen?", "Wie weit ist Kontrakt K-1001 erfuellt?"]),
        "fixierung": _liste(
            "fixierung", subtitle="MATIF-bepreiste Kontrakte zum Fixieren",
            endpoint=_WEG + "/uebersicht?include_done=false&preismodell=matif", row_route=_vorgang_route("fixierung"),
            columns=[text("contract_no", "Kontrakt", "primary"), status("contract_type", "Art"),
                     text("partner_name", "Partner", "primary"), text("artikel", "Artikel"),
                     text("pricing_model", "Preismodell", "primary"),
                     menge("total_quantity", "Menge", einheit_feld="unit", anzeige=_DT),
                     menge("rest_quantity", "Rest", einheit_feld="unit", anzeige=_DT),
                     datum("valid_to", "Gültig bis"), zahl("alarme", "Alarme")],
            purpose="Offene Kontrakte waehlen, um Teilmengen gegen die MATIF-Notierung zu fixieren.",
            prompts=["Welche MATIF-Kontrakte sind noch nicht fixiert?"]),
        "abrechnung": _liste(
            "abrechnung", subtitle="Abgerufene Mengen, die an die Abrechnung gehen",
            endpoint=_WEG + "/erfuellungsstand", row_route=_vorgang_route("abrechnung"),
            columns=[text("contract_no", "Kontrakt", "primary"), status("typ", "Art"),
                     text("partner_name", "Partner", "primary"), _m("abgerufen", "Abgerufen", summe=True),
                     _m("offen", "Offen"), status("erfuellung_status", "Erfüllungsstand"), datum("valid_to", "Gültig bis")],
            purpose="Kontrakte mit Abrufen finden und ihre Bewegungen an die Abrechnung uebergeben.",
            prompts=["Welche Kontrakte haben noch nicht abgerechnete Abrufe?"]),
        "mahnung": _liste(
            "mahnung", subtitle="Ueberfaellige, untererfuellte Kontrakte",
            endpoint=_WEG + "/mahnkandidaten", row_route=_vorgang_route("erfuellung"), row_actions=[_MAHNEN],
            columns=[text("contract_no", "Kontrakt", "primary"), status("typ", "Art"),
                     text("partner_name", "Partner", "primary"), _m("offen", "Offen", summe=True),
                     datum("valid_to", "Gültig bis"), zahl("tage_ueberfaellig", "Tage überfällig", "primary"),
                     zahl("letzte_mahnstufe", "Letzte Stufe"), zahl("naechste_mahnstufe", "Nächste Stufe")],
            purpose="Ueberfaellige Kontrakte mit offener Menge mahnen; jede Mahnung haelt Stufe und offene Menge fest.",
            prompts=["Welche Kontrakte muessen gemahnt werden?", "Mahne Kontrakt K-1001."]),
        "alarme": _liste(
            "alarme", subtitle="Ablauf, Mahnung, Absicherung, Marktbewertung, Druck und Restmenge",
            endpoint=_WEG + "/alarme", row_route=_vorgang_route("erfuellung", "kontrakt_id"),
            columns=[text("contract_no", "Kontrakt", "primary"), text("partner_name", "Partner", "primary"),
                     status("alarm", "Alarm"), text("text", "Hinweis", "primary"),
                     zahl("tage_bis_ablauf", "Tage bis Ablauf"), datum("valid_to", "Gültig bis"),
                     menge("rest_quantity", "Rest", einheit_feld="unit", anzeige=_DT, prioritaet="secondary")],
            purpose="Kontrakte mit Handlungsbedarf nach Dringlichkeit abarbeiten.",
            prompts=["Welche Kontrakte laufen in den naechsten 30 Tagen aus?", "Wo fehlt die Absicherung?"]),
        "engagement_artikel": _liste(
            "engagement_artikel", subtitle="Offene Kontraktmenge je Artikel, Einkauf gegen Verkauf",
            endpoint=_WEG + "/engagement/artikel", row_route=None,
            columns=[text("artikel", "Artikel", "primary"), zahl("einkauf_offen", "Einkauf offen", "primary"),
                     zahl("verkauf_offen", "Verkauf offen", "primary"), zahl("netto", "Netto", "primary"),
                     zahl("kontrakte", "Kontrakte")],
            purpose="Die offene Netto-Position je Artikel pruefen (Long/Short aus Kontrakten).",
            prompts=["Wie hoch ist die Netto-Position bei Raps?"]),
        "engagement_partei": _liste(
            "engagement_partei", subtitle="Offene Kontraktmenge je Geschaeftspartner",
            endpoint=_WEG + "/engagement/partei", row_route=None,
            columns=[text("partner_name", "Partner", "primary"), text("party_id", "Partner-Nr.", "tertiary"),
                     zahl("offen", "Offen", "primary"), zahl("kontrakte", "Kontrakte")],
            purpose="Pruefen, bei welchen Partnern wie viel kontrahierte Menge offen ist.",
            prompts=["Bei welchem Partner ist am meisten offen?"]),
    }


# ── Familie kontrakt (Objektseite je Kontrakt) ─────────────────────────────────

_VORGANG_TITEL = {"erfuellung": "Kontrakterfüllung", "fixierung": "Kontraktfixierung",
                  "abrechnung": "Kontraktabrechnung"}


def _feld(key: str, label: str, typ: str = "text", **zusatz: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "type": typ, "readOnly": True, **zusatz}


def _mengenfeld(key: str, label: str) -> dict[str, Any]:
    return _feld(key, label, "number", unitField="einheit", displayUnit=_DT)


_KOPF_FELDER = [
    _feld("contract_no", "Kontrakt"), _feld("contract_type", "Art"), _feld("partner_name", "Partner"),
    _feld("status", "Status"), _feld("valid_from", "Gültig ab", "date"), _feld("valid_to", "Gültig bis", "date"),
    _feld("preismodell", "Preismodell"), _feld("basis", "Basis"), _feld("praemie_wert", "Prämie", "currency"),
    _mengenfeld("menge_kontrakt", "Kontrahiert"),
]

_KENNZAHLEN = {
    "erfuellung": [("abgerufen", "Abgerufen", "neutral"), ("offen", "Offen", "warning"),
                   ("erfuellung_pct", "Erfüllung %", "neutral"), ("offene_luecken", "Lücken", "warning")],
    "fixierung": [("fixiert", "Fixiert", "neutral"), ("offen_zu_fixieren", "Offen zu fixieren", "warning"),
                  ("fixierungsgrad_pct", "Fixierungsgrad %", "neutral"),
                  ("bewertung_fixiert_eur", "Bewertung fixiert (EUR)", "neutral")],
    "abrechnung": [("abgerufen", "Abgerufen", "neutral"), ("abgerechnet", "Abgerechnet", "neutral"),
                   ("offen_abruf", "Offen zur Abrechnung", "warning"), ("fixiert_aktiv", "Fixiert (aktiv)", "neutral")],
}

_VARIANT_FELDER = {
    "erfuellung": [_mengenfeld("abgerufen", "Abgerufen"), _mengenfeld("offen", "Offen"),
                   _feld("erfuellung_pct", "Erfüllung %", "number"), _feld("erfuellung_status", "Erfüllungsstand"),
                   _feld("ueberfaellig", "Überfällig", "checkbox")],
    "fixierung": [_mengenfeld("fixiert", "Fixiert"), _mengenfeld("offen_zu_fixieren", "Offen zu fixieren"),
                  _feld("fixierungsgrad_pct", "Fixierungsgrad %", "number"),
                  _feld("bewertung_fixiert_eur", "Bewertung fixiert", "currency"),
                  _feld("marktwert_offen_eur", "Marktwert offen", "currency")],
    "abrechnung": [_mengenfeld("abgerufen", "Abgerufen"), _mengenfeld("abgerechnet", "Abgerechnet"),
                   _mengenfeld("offen_abruf", "Offen zur Abrechnung"), _mengenfeld("fixiert_aktiv", "Fixiert (aktiv)")],
}

_POSITIONS_SPALTEN = {
    "erfuellung": [zahl("position_no", "Pos.", "primary"), text("artikel", "Artikel", "primary"),
                   text("bezeichnung", "Bezeichnung"), _m("menge_kontrakt", "Kontrahiert", summe=True),
                   _m("abgerufen", "Abgerufen", summe=True), _m("offen", "Offen", summe=True),
                   _prozent("erfuellung_pct", "Erfüllung"), status("erfuellung_status", "Stand"),
                   janein("abweichung", "Übermenge")],
    "fixierung": [zahl("position_no", "Pos.", "primary"), text("artikel", "Artikel", "primary"),
                  janein("is_matif", "MATIF"), _m("menge_kontrakt", "Kontrahiert", summe=True),
                  _m("fixiert", "Fixiert", summe=True), _m("offen_zu_fixieren", "Offen", summe=True),
                  _prozent("fixierungsgrad_pct", "Fixierungsgrad"),
                  betrag("avg_fixpreis_effektiv", "Ø Fixpreis", summe=False, je="t", anzeige_je=_DT),
                  text("symbol", "Symbol", "tertiary"),
                  betrag("markt_effektiv", "Markt effektiv", summe=False, je="t", anzeige_je=_DT),
                  betrag("bewertung_fixiert_eur", "Bewertung fixiert"), betrag("marktwert_offen_eur", "Marktwert offen")],
    "abrechnung": [zahl("position_no", "Pos.", "primary"), text("artikel", "Artikel", "primary"),
                   _m("menge_kontrakt", "Kontrahiert", summe=True), _m("abgerufen", "Abgerufen", summe=True),
                   _m("fixiert", "Fixiert", summe=True)],
}


def _quelle(key: str, rest: str) -> dict[str, Any]:
    return {"key": key, "endpoint": f"{_WEG}/{{entity_id}}/{rest}", "pageSize": 200}


def _tabelle(key: str, label: str, columns: list[dict[str, Any]], *,
             row_actions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    tabelle: dict[str, Any] = {"key": key, "label": label, "dataSourceKey": key, "serverPagination": False,
                               "pageSize": 50, "virtualized": True, "rowHeight": 40, "columns": columns}
    if row_actions:
        tabelle["rowActions"] = row_actions
    return {"key": key, "label": label, "lazy": True, "keepAlive": False, "tables": [tabelle]}


_STORNO_BEWEGUNG = {
    "key": "stornieren", "label": "Stornieren", "dangerLevel": "critical", "permission": _RECHT_SCHREIBEN,
    "commandEndpoint": _WEG + "/bewegungen/{entity_id}/actions/stornieren", "method": "POST",
    "requiresConfirmation": True, "auditReasonRequired": True, "forbiddenForAgents": True,
    "visibleWhen": {"field": "status", "values": ["offen"]},
}
_ABRECHNEN_BEWEGUNG = {
    "key": "abrechnen", "label": "Abrechnen", "dangerLevel": "moderate", "permission": _RECHT_SCHREIBEN,
    "commandEndpoint": _WEG + "/bewegungen/{entity_id}/actions/abrechnen", "method": "POST",
    "requiresConfirmation": True, "visibleWhen": {"field": "status", "values": ["offen"]},
    "inputFields": [{"key": "rechnung_nr", "label": "Abrechnungsnummer", "type": "text"}],
}
_STORNO_FIXIERUNG = {
    "key": "stornieren", "label": "Stornieren", "dangerLevel": "critical", "permission": _RECHT_SCHREIBEN,
    "commandEndpoint": _WEG + "/fixierungen/{entity_id}/actions/stornieren", "method": "POST",
    "requiresConfirmation": True, "auditReasonRequired": True, "forbiddenForAgents": True,
    "visibleWhen": {"field": "status", "values": ["aktiv"]},
}

_FIXIERUNG_SPALTEN = [zahl("fixing_no", "Nr.", "primary"), zahl("position_no", "Pos."),
                      _m("menge", "Menge", summe=True), betrag("matif_price", "MATIF", summe=False, je="t", anzeige_je=_DT),
                      betrag("praemie", "Prämie", summe=False, je="t", anzeige_je=_DT),
                      betrag("effektiv_preis", "Effektiv", summe=False, je="t", anzeige_je=_DT),
                      datum("datum", "Datum"), text("referenz", "Referenz", "tertiary"), status(),
                      text("bediener", "Bediener", "tertiary"), text("storno_grund", "Storno-Grund", "tertiary")]

_BEWEGUNG_SPALTEN = [datum("datum", "Datum", "primary"), _m("menge", "Menge", summe=True), status(),
                     text("invoice_no", "Abrechnung"), datum("settled_at", "Übergeben am"),
                     text("storno_grund", "Storno-Grund", "tertiary")]


def _reiter(variante: str) -> list[dict[str, Any]]:
    kopf = {"key": "kopf", "label": "Kontrakt", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
            "fields": [*_KOPF_FELDER, *_VARIANT_FELDER[variante]]}
    reiter = [kopf, _tabelle("positionen", "Positionen", _POSITIONS_SPALTEN[variante])]
    if variante == "erfuellung":
        reiter += [_tabelle("luecken", "Lücken", [status("schwere", "Schwere"), text("text", "Hinweis", "primary")]),
                   _tabelle("mahnungen", "Mahnungen", [zahl("mahnstufe", "Stufe", "primary"), _m("offen", "Offen"),
                                                       text("text", "Text"), text("bediener", "Bediener", "tertiary"),
                                                       datum("datum", "Datum", "primary")])]
    elif variante == "fixierung":
        reiter.append(_tabelle("fixierungen", "Fixierungen", _FIXIERUNG_SPALTEN, row_actions=[_STORNO_FIXIERUNG]))
    else:
        reiter += [_tabelle("bewegungen", "Bewegungen", _BEWEGUNG_SPALTEN,
                            row_actions=[_ABRECHNEN_BEWEGUNG, _STORNO_BEWEGUNG]),
                   _tabelle("fixierungen", "Fixierungen", _FIXIERUNG_SPALTEN, row_actions=[_STORNO_FIXIERUNG])]
    return reiter


def _quellen(variante: str) -> list[dict[str, Any]]:
    quellen = [{"key": "entity", "endpoint": _WEG + "/{entity_id}"}, _quelle("positionen", "positionen")]
    if variante == "erfuellung":
        quellen += [_quelle("luecken", "luecken"), _quelle("mahnungen", "mahnungen")]
    elif variante == "fixierung":
        quellen.append(_quelle("fixierungen", "fixierungen"))
    else:
        quellen += [_quelle("bewegungen", "bewegungen"), _quelle("fixierungen", "fixierungen")]
    return quellen


def _aktionen(variante: str) -> list[dict[str, Any]]:
    wechsel = [{"key": f"ansicht_{v}", "label": titel, "kind": "secondary", "dangerLevel": "safe", "zone": "header",
                "navigationRoute": _vorgang_route(v, "entity_id"), "localEffect": "navigation",
                "stubReason": f"Wechselt zur Variante {titel} desselben Kontrakts."}
               for v, titel in _VORGANG_TITEL.items() if v != variante]
    if variante == "erfuellung":
        haupt = [{**_MAHNEN, "kind": "primary", "zone": "header"}]
    elif variante == "fixierung":
        haupt = [
            {"key": "fixieren", "label": "Fixieren", "kind": "primary", "zone": "header", "dangerLevel": "moderate",
             "permission": _RECHT_SCHREIBEN, "commandEndpoint": _WEG + "/{entity_id}/actions/fixieren",
             "method": "POST", "requiresConfirmation": True,
             "inputFields": [
                 {"key": "position", "label": "Position (Nr.)", "type": "text",
                  "helpText": "Pflicht bei mehreren Positionen."},
                 {"key": "menge", "label": "Menge (Kontrakteinheit)", "type": "number", "required": True},
                 {"key": "matif_preis", "label": "MATIF-Preis je t", "type": "currency", "required": True},
                 {"key": "praemie", "label": "Prämie je t", "type": "currency",
                  "helpText": "Leer = Prämie des Kontrakts."},
                 {"key": "matif_referenz", "label": "MATIF-Referenz", "type": "text"},
                 {"key": "notiz", "label": "Notiz", "type": "textarea"}]},
            {"key": "notierung_erfassen", "label": "Notierung erfassen", "kind": "secondary", "zone": "header",
             "dangerLevel": "low", "permission": _RECHT_SCHREIBEN,
             "commandEndpoint": _WEG + "/{entity_id}/actions/notierung_erfassen", "method": "POST",
             "requiresConfirmation": False,
             "inputFields": [{"key": "symbol", "label": "Symbol", "type": "text", "required": True},
                             {"key": "preis", "label": "Preis je t", "type": "currency", "required": True},
                             {"key": "datum", "label": "Datum", "type": "date"}]},
        ]
    else:
        haupt = [{"key": "abrechnung_uebergeben", "label": "An Abrechnung übergeben", "kind": "primary",
                  "zone": "header", "dangerLevel": "moderate", "permission": _RECHT_SCHREIBEN,
                  "commandEndpoint": _WEG + "/{entity_id}/actions/abrechnung_uebergeben", "method": "POST",
                  "requiresConfirmation": True,
                  "inputFields": [{"key": "rechnung_nr", "label": "Abrechnungsnummer", "type": "text",
                                   "helpText": "Leer = je Bewegung ABR-<Kontrakt>-<lfd. Nr.>."}]}]
    return [*haupt, *wechsel]


def _vorgang(variante: str) -> dict[str, Any]:
    screen = f"{VORGANG}/{variante}"
    profil = "financial" if variante == "abrechnung" else "inventory"
    return {
        "schemaVersion": 1,
        "id": screen,
        "domain": "agrar",
        "mode": "detail",
        "title": _VORGANG_TITEL[variante],
        "subtitle": "Kontrakt-Vorgang",
        "adapter": {"type": "native", "sourceId": screen, "temporary": False},
        "identityField": "contract_no",
        "dataSources": _quellen(variante),
        "tabs": _reiter(variante),
        "actions": _aktionen(variante),
        "summary": [{"key": k, "label": label, "tone": ton} for k, label, ton in _KENNZAHLEN[variante]],
        "variant": {"family": VORGANG, "id": variante},
        "noWorkflowReason": ("Der Stand des Kontrakts (Erfuellung, Fixierung, Abrechnung) kommt je Kontrakt vom Server; "
                             "die Maske fuehrt keinen eigenen Ablauf."),
        "noProcessChainReason": "Kontrakt-Vorgang ohne Belegkette; Folgebelege entstehen in Annahme und Abrechnung.",
        "agentContract": {
            "businessPurpose": {
                "erfuellung": "Erfuellungsstand eines Kontrakts pruefen, Luecken sehen und ueberfaellige Kontrakte mahnen.",
                "fixierung": "Teilmengen eines MATIF-Kontrakts fixieren, Notierungen erfassen und Fixierungen stornieren.",
                "abrechnung": "Abrufbewegungen an die Abrechnung uebergeben und Bewegungen oder Fixierungen stornieren.",
            }[variante],
            "examplePrompts": {
                "erfuellung": ["Wie viel ist von Kontrakt K-1001 noch offen?", "Mahne Kontrakt K-1001."],
                "fixierung": ["Fixiere 50 t von K-1001 zu 215 EUR/t.", "Welche Fixierungen hat K-1001?"],
                "abrechnung": ["Uebergib die offenen Abrufe von K-1001 an die Abrechnung."],
            }[variante],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": f"[data-testid='kontrakt-{variante}']",
                              "primaryAction": f"[data-testid='action-{_aktionen(variante)[0]['key']}']",
                              "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44,
                   "floorplan": "objectPage", "columnNavigation": "single", "sectionNavigation": "anchors",
                   "density": "compact", "contextRail": "combined", "summaryPlacement": "header",
                   "stickyHeader": True, "stickyFooter": True, "tableProfile": profil},
        "performance": {"initialPayloadBudgetKb": 36, "requiresLazyTabs": True, "requiresVirtualTables": True,
                        "lookupMinChars": 2, "bundleGroup": "kontrakte"},
    }


def kontrakt_vorgang_varianten() -> dict[str, dict[str, Any]]:
    return {variante: _vorgang(variante) for variante in _VORGANG_TITEL}


#: Familie -> Builder aller Varianten (fuer Registry-Generator und Gleichlauf-Test).
FAMILIEN_BUILDER = {LISTE: kontrakt_liste_varianten, VORGANG: kontrakt_vorgang_varianten}
