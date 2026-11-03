"""Studio-Listen Lager aus vorhandenen Lesewegen (Masken-Cluster Batch 2, 03.11.2026).

Vorher batch15-Platzhalter auf ``/lager/bestaende`` mit id/name/status/updated_at bzw. eine Seite ohne Maske
(``lager/bestandsuebersicht``). Die Kommissionierung liest die Ruestlisten (Tabelle seit ruestlisten_tabelle_20261103). Inventarprofil, Export und Lesegrenzen kommen aus ``build_stamm_list_screen``.
"""
from __future__ import annotations

from typing import Any

from app.core.cluster_spalten import betrag, datum, janein, menge, status, text
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action

_EXPORT = stamm_list_export_action()
_KEIN_ABLAUF = "Auswertungsliste ohne eigenen Ablauf; Buchungen und Bewegungen in der jeweiligen Fachmaske."


def _liste(**kwargs: Any) -> dict[str, Any]:
    return build_stamm_list_screen(domain="lager", bundle="lager", actions=[_EXPORT], row_actions=[],
                                   no_workflow=_KEIN_ABLAUF, **kwargs)


def _bestand(screen_id: str, title: str, subtitle: str, *, mit_wert: bool, purpose: str, prompts: list[str]) -> dict[str, Any]:
    spalten = [text("article_number", "Artikelnr.", "primary"), text("article_name", "Artikel", "primary"),
               text("warehouse_name", "Lager", "primary"), text("charge", "Charge"),
               menge("menge", "Bestand", einheit_feld="einheit", summe=True), text("einheit", "Einheit", "tertiary")]
    if mit_wert:
        spalten.append(betrag("bestandswert", "Bestandswert"))
    return _liste(screen_id=screen_id, title=title, subtitle=subtitle, endpoint="/api/v1/lager/bestaende",
                  row_route="/lager/article-stock/{article_id}", columns=spalten, purpose=purpose, prompts=prompts)


def build_lager_bestandsuebersicht() -> dict[str, Any]:
    return _bestand("lager/bestandsuebersicht", "Bestandsübersicht", "Bestand je Artikel, Lager und Charge",
                    mit_wert=False, purpose="Den aktuellen Bestand eines Artikels in allen Lagern finden.",
                    prompts=["Wie viel Weizen liegt im Lager Nord?", "Welche Chargen hat Artikel 4711?"])


def build_lager_bestandsbewertung() -> dict[str, Any]:
    return _bestand("lager/bestandsbewertung", "Bestandsbewertung", "Bestand mit Wert je Artikel, Lager und Charge",
                    mit_wert=True, purpose="Den Bestandswert je Lager und Artikel pruefen, etwa zum Monatsabschluss.",
                    prompts=["Wie hoch ist der Bestandswert im Lager Sued?", "Welche Artikel binden das meiste Kapital?"])


def build_lager_kommissionierung() -> dict[str, Any]:
    return _liste(
        screen_id="lager/kommissionierung", title="Kommissionierung", subtitle="Rüstlisten je Auftrag mit Status und Priorität",
        endpoint="/api/v1/lager/ruestliste", row_route=None,
        columns=[text("ruestlisten_nr", "Rüstliste", "primary"), text("auftrag_nr", "Auftrag", "primary"), status(),
                 text("prioritaet", "Priorität"), text("erstellt_fuer", "Erstellt für"),
                 datum("erstellt_am", "Erstellt am"), datum("verarbeitet_am", "Verarbeitet am", "tertiary")],
        purpose="Offene Ruestlisten nach Prioritaet abarbeiten und erledigte nachvollziehen.",
        prompts=["Welche Ruestlisten sind noch offen?", "Welche Auftraege sind eilig?"],
    )


def build_lager_rueckverfolgbarkeit() -> dict[str, Any]:
    return _liste(
        screen_id="lager/rueckverfolgbarkeit", title="Rückverfolgbarkeit",
        subtitle="Wiegescheine und der Stand ihrer Kette: Annahme, Lager, Abrechnung",
        endpoint="/api/v1/supply-chain/traceability/tickets", row_route=None,
        columns=[text("ticket_nr", "Wiegeschein", "primary"), datum("datum", "Datum", "primary"),
                 menge("menge_kg", "Menge", einheit="kg", anzeige="dt", summe=True), status(), text("allokation", "Zuordnung"),
                 janein("hat_annahme", "Annahme"), janein("hat_lager", "Lager"), janein("hat_abrechnung", "Abrechnung"),
                 janein("vollstaendig", "Kette vollständig", "primary")],
        purpose="Wiegescheine finden, deren Kette von der Annahme bis zur Abrechnung noch Luecken hat.",
        prompts=["Welche Wiegescheine haben keine Abrechnung?", "Ist die Kette von WG-2026-00001 vollstaendig?"],
    )


CLUSTER_LAGER_SCREEN_BUILDERS: dict[str, Any] = {
    "lager/bestandsuebersicht": build_lager_bestandsuebersicht,
    "lager/bestandsbewertung": build_lager_bestandsbewertung,
    "lager/kommissionierung": build_lager_kommissionierung,
    "lager/rueckverfolgbarkeit": build_lager_rueckverfolgbarkeit,
}
