"""Studio-Listen FiBu/Finance aus vorhandenen Lesewegen (Masken-Cluster Batch 1, 02.11.2026).

Diese Masken waren batch15-Platzhalter (Spalten id/name/status/updated_at, oft fremde Quelle). Hier lesen sie
den typisierten Weg ihres Fachobjekts; Spalten folgen dem Response-Model. Shell, Finanzprofil, Export und
Lesegrenzen kommen aus ``build_stamm_list_screen`` (``StammListenParent``).
"""
from __future__ import annotations

from typing import Any

from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action

_EXPORT = stamm_list_export_action()
_KEIN_ABLAUF = "Stammdaten- bzw. Auswertungsliste ohne eigenen Ablauf; Aenderungen in der jeweiligen Fachmaske."


def _text(key: str, label: str, prioritaet: str = "secondary", **zusatz: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "sortable": True, "filterable": True, "priority": prioritaet, **zusatz}


def _betrag(key: str, label: str, summe: bool = True, prioritaet: str = "primary") -> dict[str, Any]:
    spalte = {"key": key, "label": label, "renderKind": "currency", "numeric": True, "sortable": True, "priority": prioritaet}
    return {**spalte, "aggregate": "sum"} if summe else spalte


def _datum(key: str, label: str, prioritaet: str = "secondary") -> dict[str, Any]:
    return {"key": key, "label": label, "renderKind": "date", "sortable": True, "priority": prioritaet}


def _janein(key: str, label: str) -> dict[str, Any]:
    return {"key": key, "label": label, "renderKind": "boolean", "filterable": True, "priority": "secondary"}


def _liste(**kwargs: Any) -> dict[str, Any]:
    return build_stamm_list_screen(bundle="finance", actions=[_EXPORT], row_actions=[], row_route=None,
                                   no_workflow=_KEIN_ABLAUF, **kwargs)


def build_fibu_erloeskennziffern() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/erloeskennziffern", domain="fibu", title="Erlöskennziffern",
        subtitle="Kennziffern, ueber die Artikel ihre Erloes- und Aufwandskonten finden",
        endpoint="/api/v1/fibu/erloeskennziffern",
        columns=[_text("ekz_nr", "EKZ-Nr.", "primary"), _text("bezeichnung", "Bezeichnung", "primary"),
                 _janein("aktiv", "Aktiv"), _datum("created_at", "Angelegt", "tertiary")],
        purpose="Erloeskennziffern finden und pruefen, welche aktiv sind.",
        prompts=["Welche Erloeskennziffern sind inaktiv?", "Zeige die Kennziffer 100."],
    )


def build_fibu_erloeskontenzuordnung() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/erloeskontenzuordnung", domain="fibu", title="Erlöskontenzuordnung",
        subtitle="Konten je Erloeskennziffer, Steuerschluessel und Gueltigkeit",
        endpoint="/api/v1/fibu/erloeskennziffern/zuordnungen",
        columns=[_datum("gueltig_ab", "Gültig ab", "primary"), _text("steuerschluessel", "Steuerschlüssel", "primary"),
                 _text("steuergruppe", "Steuergruppe"), _text("buchungsklasse", "Buchungsklasse"),
                 _text("konto_erloese", "Erlöskonto", "primary"), _text("konto_aufwand", "Aufwandskonto"),
                 _text("konto_umsatzsteuer", "USt-Konto", "tertiary"), _text("konto_vorsteuer", "VSt-Konto", "tertiary")],
        purpose="Pruefen, auf welche Konten eine Erloeskennziffer je Steuerschluessel bucht.",
        prompts=["Welche Zuordnungen gelten fuer Steuerschluessel 3?", "Welches Erloeskonto gilt ab 1.1.?"],
    )


def build_fibu_forderungsgruppen() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/forderungsgruppen", domain="fibu", title="Forderungsgruppen",
        subtitle="Sammelkonten fuer Forderungen und Verbindlichkeiten",
        endpoint="/api/v1/fibu/forderungsgruppen",
        columns=[_text("gruppe_nr", "Gruppe", "primary"), _text("bezeichnung", "Bezeichnung", "primary"),
                 _text("konto_forderungen", "Konto Forderungen"), _text("konto_verbindlichkeiten", "Konto Verbindlichkeiten"),
                 _text("konto_sammel_1", "Sammelkonto 1", "tertiary"), _janein("aktiv", "Aktiv")],
        purpose="Forderungsgruppen und ihre Sammelkonten pruefen.",
        prompts=["Welche Forderungsgruppe bucht auf 1400?", "Zeige inaktive Forderungsgruppen."],
    )


def build_fibu_periodische_buchungen() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/periodische-buchungen", domain="fibu", title="Periodische Buchungen",
        subtitle="Wiederkehrende Buchungen mit Turnus und Gueltigkeit",
        endpoint="/api/v1/fibu/periodische-buchungen",
        columns=[_text("bezeichnung", "Bezeichnung", "primary"), _text("konto", "Konto", "primary"),
                 _text("gegenkonto", "Gegenkonto", "primary"), _betrag("betrag", "Betrag"),
                 _text("turnus", "Turnus"), _datum("gueltig_ab", "Gültig ab"), _datum("gueltig_bis", "Gültig bis"),
                 _text("kostenstelle", "Kostenstelle", "tertiary"), _janein("gesperrt", "Gesperrt"), _janein("aktiv", "Aktiv")],
        purpose="Wiederkehrende Buchungen pruefen: Konten, Betrag, Turnus und Sperren.",
        prompts=["Welche periodischen Buchungen sind gesperrt?", "Wie hoch ist die monatliche Summe?"],
    )


def build_fibu_lohn_connector() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/lohn-connector", domain="fibu", title="Lohn-Übernahme",
        subtitle="Importlaeufe aus der Lohnbuchhaltung je Periode",
        endpoint="/api/v1/finance/lohn-connector/runs",
        columns=[_text("period", "Periode", "primary"), _text("source", "Quelle"),
                 {**_text("status", "Status", "primary"), "renderKind": "status"},
                 {"key": "journal_entry_count", "label": "Buchungen", "renderKind": "number", "numeric": True, "priority": "secondary"},
                 _betrag("total_debit", "Soll"), _betrag("total_credit", "Haben"),
                 _text("message", "Meldung", "tertiary"), _datum("created_at", "Gelaufen am")],
        purpose="Pruefen, ob die Lohnbuchungen einer Periode vollstaendig und ausgeglichen uebernommen wurden.",
        prompts=["Ist die Lohnuebernahme fuer Oktober gelaufen?", "Welche Laeufe sind fehlgeschlagen?"],
    )


def build_fibu_quadriga_connector() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/quadriga-connector", domain="fibu", title="Quadriga-Anbindung",
        subtitle="Konfigurationen der Quadriga-Schnittstelle",
        endpoint="/api/v1/finance/quadriga-connector/config",
        columns=[_text("connector_code", "Schnittstelle", "primary"), _text("name", "Name", "primary"),
                 _janein("is_active", "Aktiv"), _datum("updated_at", "Geändert")],
        purpose="Pruefen, welche Quadriga-Konfiguration aktiv ist.",
        prompts=["Ist die Quadriga-Anbindung aktiv?"],
    )


def build_fibu_kreditlinien() -> dict[str, Any]:
    return _liste(
        screen_id="fibu/kreditlinien", domain="fibu", title="Kreditlinien",
        subtitle="Kreditlimit und Inanspruchnahme je Geschaeftspartner",
        endpoint="/api/v1/finance/credit-limits",
        columns=[_text("partner_name", "Geschäftspartner", "primary"),
                 {**_betrag("credit_limit", "Kreditlimit"), "currencyField": "currency"},
                 {**_betrag("used_credit", "In Anspruch genommen"), "currencyField": "currency"},
                 {"key": "auslastung", "label": "Auslastung", "renderKind": "percentage", "priority": "primary",
                  "computed": {"op": "percentOf", "of": ["used_credit", "credit_limit"], "round": 1}},
                 _text("currency", "Währung", "tertiary")],
        purpose="Kreditlinien und ihre Auslastung je Partner pruefen.",
        prompts=["Welche Partner sind ueber 90 % ausgelastet?", "Wie hoch ist das gesamte Kreditlimit?"],
    )


def build_finance_nebenbuch_abstimmung() -> dict[str, Any]:
    return _liste(
        screen_id="finance/nebenbuch-abstimmung", domain="finance", title="Nebenbuch-Abstimmung",
        subtitle="Abstimmung Nebenbuch gegen Hauptbuch je Periode und Buchungskreis",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        columns=[_datum("abstimmungs_datum", "Abgestimmt am", "primary"), _text("periode", "Periode", "primary"),
                 _text("buchungskreis", "Buchungskreis"), {**_text("status", "Status", "primary"), "renderKind": "status"},
                 _betrag("nebenbuch_saldo", "Saldo Nebenbuch", summe=False), _betrag("hauptbuch_saldo", "Saldo Hauptbuch", summe=False),
                 _betrag("differenz", "Differenz"), _text("abgestimmt_durch", "Abgestimmt durch", "tertiary")],
        purpose="Differenzen zwischen Neben- und Hauptbuch je Periode finden.",
        prompts=["Welche Perioden haben eine Differenz?", "Wer hat die Abstimmung fuer Oktober gemacht?"],
    )


CLUSTER_FIBU_SCREEN_BUILDERS: dict[str, Any] = {
    "fibu/erloeskennziffern": build_fibu_erloeskennziffern,
    "fibu/erloeskontenzuordnung": build_fibu_erloeskontenzuordnung,
    "fibu/forderungsgruppen": build_fibu_forderungsgruppen,
    "fibu/periodische-buchungen": build_fibu_periodische_buchungen,
    "fibu/lohn-connector": build_fibu_lohn_connector,
    "fibu/quadriga-connector": build_fibu_quadriga_connector,
    "fibu/kreditlinien": build_fibu_kreditlinien,
    "finance/nebenbuch-abstimmung": build_finance_nebenbuch_abstimmung,
}
