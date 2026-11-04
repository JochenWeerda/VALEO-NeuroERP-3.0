"""Portal-Listen auf ihrem eigenen Weg (Masken-Cluster Batch 7, 03.11.2026).

Die batch15-Platzhalter lasen fast alle ``/portal/anfragen`` und zeigten id/name/status/updated_at: Bestellungen,
Rechnungen, Feldbuch und Shop waren im Portal Anfragen. Jede Liste liest jetzt den Weg ihres Registers aus
``portal_kundenwege.py`` (Kundenkonto und Rolle serverseitig, TENANT-DOC-001/PORTAL-CONTEXT-001) mit den Spalten
seiner Zeilenform (``app/api/v1/schemas/portal_listen_schemas.py``).
"""
from __future__ import annotations

from typing import Any

from app.core.cluster_spalten import betrag, datum, janein, menge, status, text, zahl
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action

_EXPORT = stamm_list_export_action()


def _portal_liste(**kwargs: Any) -> dict[str, Any]:
    return build_stamm_list_screen(domain="portal", bundle="portal", actions=[_EXPORT], row_actions=[],
                                   row_route=None, **kwargs)


def build_portal_anfragen() -> dict[str, Any]:
    return _portal_liste(
        screen_id="portal/anfragen", title="Anfragen", subtitle="Anfragen des Kundenkontos",
        endpoint="/api/v1/portal/anfragen",
        columns=[text("nummer", "Anfrage", "primary"), text("betreff", "Betreff", "primary"),
                 datum("datum", "Datum", "primary"), status()],
        purpose="Eigene Anfragen und ihren Bearbeitungsstand sehen.",
        prompts=["Welche meiner Anfragen sind noch offen?"],
        no_workflow="Portalliste; die Anfrage bearbeitet der Innendienst.",
    )


def build_portal_bestellungen() -> dict[str, Any]:
    return _portal_liste(
        screen_id="portal/bestellungen", title="Bestellungen", subtitle="Auftraege des Kundenkontos",
        endpoint="/api/v1/portal/bestellungen",
        columns=[text("nummer", "Bestellung", "primary"), datum("datum", "Datum", "primary"),
                 text("artikel", "Erster Artikel"), menge("menge", "Menge", prioritaet="secondary"),
                 betrag("betrag", "Betrag (brutto)"), status()],
        purpose="Eigene Bestellungen, ihren Stand und die Summe sehen.",
        prompts=["Welche Bestellungen sind noch nicht geliefert?", "Wie viel habe ich dieses Jahr bestellt?"],
        no_workflow="Portalliste; Bestellen im Shop, Bearbeitung im Verkauf.",
    )


def build_portal_dokumente() -> dict[str, Any]:
    return _portal_liste(
        screen_id="portal/dokumente", title="Dokumente", subtitle="Dem Kundenkonto zugeordnete Unterlagen",
        endpoint="/api/v1/portal/dokumente",
        columns=[text("name", "Dokument", "primary"), text("kategorie", "Kategorie", "primary"), text("typ", "Typ"),
                 datum("datum", "Hochgeladen", "primary"), zahl("groesse", "Größe (Byte)", "tertiary")],
        purpose="Unterlagen finden, die dem eigenen Kundenkonto zugeordnet sind.",
        prompts=["Welche Dokumente sind neu?"],
        no_workflow="Portalliste; nur gesichert zugeordnete Unterlagen (TENANT-DOC-001), sonst leer.",
    )


def build_portal_feldbuch() -> dict[str, Any]:
    return _portal_liste(
        screen_id="portal/feldbuch", title="Feldbuch", subtitle="Schlaege des Betriebs mit Kultur und Flaeche",
        endpoint="/api/v1/portal/feldbuch",
        columns=[text("schlag", "Schlag", "primary"), text("kultur", "Kultur", "primary"),
                 menge("flaeche", "Fläche", einheit="ha", summe=True),
                 datum("letzteMassnahme", "Letzte Maßnahme"), datum("naechsteMassnahme", "Nächste Maßnahme")],
        purpose="Schlaege, Kulturen und die bewirtschaftete Flaeche sehen.",
        prompts=["Wie viel Hektar Weizen habe ich?", "Welche Schlaege haben keine Kultur?"],
        no_workflow="Portalliste; Massnahmen im Feldbuch des Portals.",
    )


def build_portal_naehrstoffbilanzen() -> dict[str, Any]:
    # Die Zeilen sind Naehrstoffe je Lieferung, kein Saldo je Schlag; die Spalte ``bewertung`` (170 kg N je
    # Lieferung statt je Hektar und Betrieb) bleibt bewusst weg, sie waere eine falsche DueV-Aussage.
    return _portal_liste(
        screen_id="portal/naehrstoffbilanzen", title="Nährstoffzufuhr",
        subtitle="Naehrstoffe der gelieferten Duengemittel je Lieferung",
        endpoint="/api/v1/portal/naehrstoffbilanzen",
        columns=[text("id", "Lieferung", "primary"), text("schlag", "Schlag", "primary"), text("kultur", "Kultur"),
                 menge("n_saldo", "N", einheit="kg", summe=True), menge("p_saldo", "P₂O₅", einheit="kg", summe=True),
                 menge("k_saldo", "K₂O", einheit="kg", summe=True)],
        purpose="Sehen, wie viel Stickstoff, Phosphat und Kali mit den Lieferungen auf den Betrieb kamen.",
        prompts=["Wie viel Stickstoff wurde dieses Jahr geliefert?"],
        no_workflow="Auswertungsliste; die Duengebilanz nach DueV steht im Feldbuch.",
    )


def build_portal_rechnungen() -> dict[str, Any]:
    return _portal_liste(
        screen_id="portal/rechnungen", title="Rechnungen", subtitle="Rechnungen des Kundenkontos",
        endpoint="/api/v1/portal/rechnungen",
        columns=[text("nummer", "Rechnung", "primary"), datum("datum", "Datum", "primary"),
                 betrag("betrag", "Betrag (brutto)"), status()],
        purpose="Eigene Rechnungen und offene Betraege sehen.",
        prompts=["Welche Rechnungen sind offen?", "Wie hoch ist die Summe der offenen Rechnungen?"],
        no_workflow="Portalliste; Zahlung und Mahnung laufen in der Buchhaltung.",
    )


def build_portal_shop() -> dict[str, Any]:
    return _portal_liste(
        screen_id="portal/shop", title="Shop", subtitle="Artikel mit Preis, Einheit und Verfuegbarkeit",
        endpoint="/api/v1/portal/shop",
        columns=[text("name", "Artikel", "primary"), text("kategorie", "Kategorie", "primary"),
                 betrag("preis", "Preis", summe=False), text("einheit", "Einheit"),
                 janein("verfuegbar", "Verfügbar", "primary")],
        purpose="Artikel finden und pruefen, ob sie verfuegbar sind.",
        prompts=["Welche Duenger sind verfuegbar?"],
        no_workflow="Katalogliste; Bestellen ueber den Shop-Warenkorb.",
    )


def build_portal_vertraege() -> dict[str, Any]:
    return _portal_liste(
        screen_id="portal/vertraege", title="Verträge", subtitle="Dem Kundenkonto zugeordnete Vertraege",
        endpoint="/api/v1/portal/vertraege",
        columns=[text("nummer", "Vertrag", "primary"), text("typ", "Typ", "primary"), text("partner", "Partner"),
                 datum("laufzeitBis", "Laufzeit bis", "primary"), status()],
        purpose="Eigene Vertraege und ihre Laufzeit sehen.",
        prompts=["Welche Vertraege laufen dieses Jahr aus?"],
        no_workflow="Portalliste; nur gesichert zugeordnete Vertraege (TENANT-DOC-001), sonst leer.",
    )


def build_portal_empfehlungen() -> dict[str, Any]:
    return _portal_liste(
        screen_id="portal/empfehlungen", title="Empfehlungen", subtitle="Vorschlaege fuer das Kundenkonto",
        endpoint="/api/v1/portal/empfehlungen",
        columns=[text("titel", "Empfehlung", "primary"), text("typ", "Typ", "primary"), text("prioritaet", "Priorität"),
                 betrag("betrag_indikativ", "Richtbetrag", summe=False, prioritaet="secondary"),
                 datum("gueltig_bis", "Gültig bis"), janein("gesehen", "Gesehen"),
                 text("herkunft", "Herkunft", "tertiary"), text("beschreibung", "Beschreibung", "tertiary")],
        purpose="Vorschlaege sehen; eine Empfehlung ist ein Vorschlag, kein Auftrag.",
        prompts=["Welche neuen Empfehlungen habe ich?"],
        no_workflow="Vorschlagsliste; Bestellen nur ueber den Shop.",
    )


CLUSTER_PORTAL_SCREEN_BUILDERS: dict[str, Any] = {
    "portal/anfragen": build_portal_anfragen,
    "portal/bestellungen": build_portal_bestellungen,
    "portal/dokumente": build_portal_dokumente,
    "portal/empfehlungen": build_portal_empfehlungen,
    "portal/feldbuch": build_portal_feldbuch,
    "portal/naehrstoffbilanzen": build_portal_naehrstoffbilanzen,
    "portal/rechnungen": build_portal_rechnungen,
    "portal/shop": build_portal_shop,
    "portal/vertraege": build_portal_vertraege,
}
