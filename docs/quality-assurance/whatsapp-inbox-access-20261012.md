---
title: Mandantengebundener WhatsApp-Bestelleingang
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-12
description: Gepruefte OIDC-Inbox-Rechte, aktive Kunden-/Artikelreferenzen und Tokenurheber bei Kontaktbestaetigung.
---

# WhatsApp-Inbox Zugriffsschutz

## Befund und Umsetzung

Die fuenf Wege unter /api/v1/crm/bestell-inbox nutzten zuvor get_tenant_id
aus app/core/tenant.py mit Header-/Default-Kontext. Die Fuzzy-Kundensuche las
kunden_lookup ohne Mandantenpraedikat und waehlte ebenso wie die Artikelsuche
den ersten Treffer. Bestaetigungen uebernahmen Kunden- und Artikelreferenzen
aus parsed ohne eigene Fachreferenzpruefung; Kontakt-Bediener war der
ungepruefte Nachrichtenabsender.

Alle fuenf Wege verwenden jetzt den bestehenden get_verified_tenant_id und
require_scopes: Lesen crm:read, Erfassen/Bestaetigen/Verwerfen crm:write.
admin:all bleibt mandantengebunden; fehlende oder widerspruechliche Claims und
fremde Header werden vor dem Fachservice abgewiesen. Der Service besitzt
keinen Standardmandanten mehr. Request-Ruempfe akzeptieren keine unbekannten
Urheber-/Mandantenfelder. Belegtypen sind die bestehenden vier Werte.

Die Kunden-Bridge bleibt wegen vorhandener Foreign Keys auf public.kunden
erhalten. Auswahl ist nur ueber die tatsaechliche business_partner_id zu einem
aktiven Kunden-Business-Partner des geprueften Mandanten erlaubt. Eine gleiche
Kundennummer in einem anderen Kontext ist kein Berechtigungsnachweis.
Unverknuepfte, inaktive und fremde Kunden werden nicht ausgewertet. Mehrere
passende Kunden oder Artikel bleiben unaufgeloest; Ranking ist keine Freigabe.

Bestaetigung prueft Kunde und jede explizite Artikelreferenz erneut vor dem
ersten Write. Auswaehlbare Artikel gehoeren zum selben Mandanten und sind
aktiv. Autoritative Kunden-/Artikelnamen ersetzen gefaelschte Match-Metadaten;
explizite Mengen und Silos bleiben erhalten. Pruefungen sperren die beteiligten
Kunden-/Business-Partner-/Artikelzeilen mit FOR SHARE bis zum Transaktionsende,
damit ein gepruefter Bezug nicht waehrend des folgenden Writes umgewidmet wird.
Fehlerhafte Positionen und nicht verfuegbare Referenzen liefern 422 ohne
Fremdobjektwerte im Fehlertext. Fremde Inbox-IDs liefern 404, auch beim Verwerfen.
Manuelle Freitextpositionen ohne Artikelreferenz bleiben vorbelegbar.

Kontakt-Bediener ist jetzt ausschliesslich das gepruefte Token-sub. Das ist
eine Urheberverbesserung dieses Kontakts, kein unveraenderliches Eingangs- oder
Korrektur-Audit. Kunden-/Artikelmatch-Fehler verschlucken keine SQL-Fehler mehr
und rollen nicht still eine fremde laufende Session zurueck.

## Abnahme

Final **171 Tests bestanden**: 63 HTTP-/Service-Kontextvertraege der neuen
Inbox-Datei, 22 echte PostgreSQL-Referenz-/HTTP-Vertraege, 36 bestehende
LLM-JSON-Vertraege, 34 bestehende Benachrichtigungs-HTTP-Vertraege und 16
bestehende Benachrichtigungs-Persistenzvertraege.

HTTP-Guards laufen im echten FastAPI-Router. In der Guard-Datei ersetzt ein
Fachservice-Spy den Datenzugriff; das beweist Ablehnung vor Fachzugriff, keine
SQL-Isolation. Die Referenzdatei nutzt reale Inbox-/Kontakt-/Business-Partner-/
Kunden-/Artikelzeilen in zwei eigenen Probe-Mandanten. Nur externe Tokenpruefung
und im Eingangstest externe LLM-Extraktion werden ersetzt; Referenzpruefungen,
Fachmutationen und SQL sind echt. Fremde, fehlende, unverknuepfte, widerrufene
und widerspruechliche Bezuege lassen Inbox und Kontakte unveraendert. Erfolgreiche
HTTP-Bestaetigung schreibt den Tokenurheber statt des Nachrichtenabsenders.

Der vorhandene gemeinsame valeo_probe wurde mit --status als Revision
audit_urheber_20261011 geprueft. Keine Migration, keine neue Datenbank, kein
Container und kein Reset. Tests raeumen nur ihre eigenen Datensaetze auf.
Frisches CI-Schema, echte OIDC-Providerkonfiguration und Browserkonto sind mit
diesen lokalen Gegenproben nicht abgenommen. Vorhandene Starlette/httpx-
Deprecation-Warnung bleibt ausserhalb dieses Slices.

## Metadaten und Integration

Drei Code-Inventare, Architekturindex und Agent-Handbuch wurden in einem
isolierten Abbild des veroeffentlichten HEAD plus eigenen Codeaenderungen
erzeugt und geprueft. OpenAPI ist mit 3130 Pfaden aktuell; bestehende Duplicate-
Operation-ID-Warnungen des Gesamtsystems werden damit nicht als geloest
ausgewiesen. Claudes vier Kontenplan-Pfadobjekte aus fbc4aedb6 sind im neuen
Artefakt exakt erhalten. Der nachfolgende Routenwechsel d212dd3cf ist ebenfalls
im isolierten Architektur-/Agentenabgleich beruecksichtigt. Fremde OpenAPI-
und Generator-Arbeitsfassungen wurden nicht ueberschrieben oder mitcommittet.
Der Tabellenkatalog erhaelt nur den neuen lesenden Inbox-Service-Verbraucher
von domain_crm.business_partners; physische Tabellenvertraege unveraendert.

## Offene Fortsetzung

WHATSAPP-INBOX-TRUST-20261011 bleibt offen: Eingangs-Replay, atomarer Original-/
Korrektur-Nachweis, wiederholte Bestaetigung ohne zweiten Kontakt, verifizierte
Urheber fuer Erfassen/Verwerfen und konkurrierende Bearbeitung sind noch zu
schliessen. Dieser Schnitt ist WHATSAPP-INBOX-ACCESS-20261012, keine vollstaendige
Inbox-/Lernabnahme. Historienmodell, Silo-/Gebindevertrag, Lernkalibrierung,
Tourverfuegbarkeit und Browser-Versand bleiben im
[Bestell-Lernvertrag](../workflows/whatsapp-order-learning.md) getrennt offen.

Bestehende Frontend-Aufrufer nutzen apiClient; sie benoetigen nun crm:read /
crm:write im verifizierten Token. Bei zwei Kunden-/Artikeltreffern muessen sie
die bestehende manuelle Pruefung verwenden. Keine automatische Auftragsanlage
und keine Nachricht versandt.
