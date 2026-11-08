"""Studio-Listen auf ihrem eigenen Leseweg (Masken-Cluster Batch 6, 03.11.2026).

Diese Platzhalter lasen schon den richtigen Weg, zeigten aber nur id/name/status/updated_at. Spalten folgen dem
Response-Model. Datensparsam: personenbezogene Bankdaten (IBAN) der Mitglieder stehen nicht in der Liste.
"""
from __future__ import annotations

from typing import Any

from app.core.cluster_spalten import betrag, datum, janein, menge, status, text, zahl
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action

_EXPORT = stamm_list_export_action()


def _liste(**kwargs: Any) -> dict[str, Any]:
    return build_stamm_list_screen(actions=[_EXPORT], row_actions=[], row_route=None, **kwargs)


def build_etiketten_druckauftraege() -> dict[str, Any]:
    return _liste(
        screen_id="etiketten/drucken", domain="lager", bundle="lager", title="Etikettendruck",
        subtitle="Druckauftraege je Charge mit Drucker, Uebermittlung und Fehlern",
        endpoint="/api/v1/etiketten/druckauftrag",
        columns=[text("auftrags_nr", "Auftrag", "primary"), text("chargen_id", "Charge", "primary"),
                 text("artikel", "Artikel"), menge("menge", "Menge", prioritaet="secondary"),
                 zahl("anzahl_etiketten", "Etiketten"), text("drucker_name", "Drucker"), status(),
                 text("uebermittlung", "Übermittlung", "tertiary"), datum("gedruckt_am", "Gedruckt am"),
                 text("fehler", "Fehler", "tertiary")],
        purpose="Pruefen, welche Etiketten gedruckt sind und wo ein Druck haengt.",
        prompts=["Welche Druckauftraege sind fehlgeschlagen?", "Sind die Etiketten fuer Charge 4711 gedruckt?"],
        no_workflow="Auswertungsliste; Druck und Wiederholung in der Etikettenmaske.",
    )


def build_genossenschaft_mitglieder() -> dict[str, Any]:
    return _liste(
        screen_id="genossenschaft/mitglieder", domain="platform", bundle="genossenschaft", title="Mitglieder",
        subtitle="Genossenschaftsmitglieder mit Anteilen und Geschaeftsguthaben",
        endpoint="/api/v1/genossenschaft/mitglieder",
        columns=[text("mitglieds_nr", "Mitgliedsnr.", "primary"), text("name", "Name", "primary"),
                 datum("eintrittsdatum", "Eintritt"), datum("austrittsdatum", "Austritt"),
                 zahl("genossenschaftsanteile", "Anteile", "primary"), betrag("anteilswert_eur", "Anteilswert", summe=False),
                 betrag("geschaeftsguthaben_eur", "Geschäftsguthaben"), status()],
        purpose="Mitglieder, ihre Anteile und das Geschaeftsguthaben pruefen.",
        prompts=["Wie hoch ist das gesamte Geschaeftsguthaben?", "Welche Mitglieder sind zum Jahresende ausgetreten?"],
        no_workflow="Mitgliederliste; Ein- und Austritt in der Mitgliedermaske.",
    )


def build_kontrakte_kontraktklassen() -> dict[str, Any]:
    return _liste(
        screen_id="kontrakte/kontraktklassen", domain="agrar", bundle="kontrakte", title="Kontraktklassen",
        subtitle="Vorlagen fuer Kontrakte: Variante, Paritaet und Incoterm",
        endpoint="/api/v1/kontrakt-klassen",
        columns=[text("name", "Klasse", "primary"), text("variante", "Variante", "primary"),
                 text("incoterm_ort", "Incoterm-Ort"), text("beschreibung", "Beschreibung", "tertiary"),
                 datum("created_at", "Angelegt", "tertiary")],
        purpose="Kontraktklassen und ihre Lieferbedingungen pruefen.",
        prompts=["Welche Kontraktklassen gibt es fuer frei Haus?"],
        no_workflow="Stammdatenliste ohne eigenen Ablauf.",
    )


def build_logistik_frachtbriefe() -> dict[str, Any]:
    return _liste(
        screen_id="logistik/frachtbriefe", domain="logistics", bundle="logistik", title="Frachtbriefe",
        subtitle="Frachtbriefe mit Fahrzeug, Absender, Empfaenger und Tour",
        endpoint="/api/v1/logistik/frachtbriefe", table_profile="inventory",
        columns=[text("nummer", "Frachtbrief", "primary"), datum("datum", "Datum", "primary"),
                 text("kennzeichen", "Kennzeichen"), text("artikel", "Artikel"),
                 menge("menge", "Menge", prioritaet="secondary"), text("absender", "Absender"),
                 text("empfaenger", "Empfänger", "primary"), status(), text("lieferschein_ref", "Lieferschein", "tertiary")],
        purpose="Frachtbriefe finden und pruefen, welche zu einer Tour gehoeren.",
        prompts=["Welche Frachtbriefe sind heute offen?", "Zu welcher Tour gehoert Frachtbrief FB-1001?"],
        no_workflow="Belegliste; Erstellung in der Verladung.",
    )


def build_schaeden_meldungen() -> dict[str, Any]:
    return _liste(
        screen_id="schaeden/meldung", domain="qualitaet", bundle="schaeden", title="Schadensmeldungen",
        subtitle="Schaeden mit Meldefrist, Versicherung und Regulierung",
        endpoint="/api/v1/schaeden/meldungen",
        columns=[text("meldungsnummer", "Meldung", "primary"), text("art", "Art", "primary"),
                 datum("schadendatum", "Schadendatum"), text("ort", "Ort"), betrag("schadenhoehe", "Schadenhöhe"),
                 betrag("regulierungsbetrag", "Reguliert"), status(), datum("melden_bis", "Melden bis"),
                 janein("frist_ueberschritten", "Frist überschritten", "primary")],
        purpose="Schaeden mit ueberschrittener Meldefrist und offene Regulierungen finden.",
        prompts=["Welche Schaeden sind ueber der Meldefrist?", "Wie hoch ist die offene Schadenssumme?"],
        no_workflow="Meldeliste; Erfassung und Regulierung in der Schadensmaske.",
    )


def build_workflows_supervisor() -> dict[str, Any]:
    return _liste(
        screen_id="workflows/supervisor", domain="platform", bundle="workflows", title="Agentenlaeufe",
        subtitle="Laeufe der Assistenz-Agenten mit Faehigkeit, Status und Beginn",
        endpoint="/api/v1/agents/neuroassist/runs",
        columns=[text("capability_key", "Fähigkeit", "primary"), status(), datum("started_at", "Gestartet", "primary"),
                 text("run_id", "Lauf", "tertiary"), text("correlation_id", "Korrelation", "tertiary")],
        purpose="Pruefen, welche Agentenlaeufe haengen oder fehlgeschlagen sind.",
        prompts=["Welche Agentenlaeufe sind fehlgeschlagen?"],
        no_workflow="Beobachtungsliste; Agenten handeln nur ueber ihre Werkzeuge.",
    )


CLUSTER_EIGENE_WEGE_SCREEN_BUILDERS: dict[str, Any] = {
    "etiketten/drucken": build_etiketten_druckauftraege,
    "genossenschaft/mitglieder": build_genossenschaft_mitglieder,
    "kontrakte/kontraktklassen": build_kontrakte_kontraktklassen,
    "logistik/frachtbriefe": build_logistik_frachtbriefe,
    "schaeden/meldung": build_schaeden_meldungen,
    "workflows/supervisor": build_workflows_supervisor,
}
