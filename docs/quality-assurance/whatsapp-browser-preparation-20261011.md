---
title: Sichere WhatsApp-Benachrichtigungsvorbereitung
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-11
description: Veralteten automatischen Meta-Versand entfernen und vorbereitete Browsernachrichten ehrlich ausweisen.
---

# WhatsApp-Vorbereitung fuer Browserversand

## Befund und Reparatur

Die beiden Dev-Simulator-Endpunkte rufen denselben Benachrichtigungsdienst wie
die Lieferschein-Fachlogik auf. Mit WHATSAPP_PHONE_NUMBER_ID und
WHATSAPP_ACCESS_TOKEN versuchte der bisherige Dienst einen echten Meta-HTTP-
Versand, auch im Simulator. Fehler oder fehlende Credentials meldeten simulated.
Das widersprach dem vom Nutzer festgelegten WhatsApp-Web-/Computer-Use-Transport.

Der automatische Meta-Sender ist entfernt. Bestehende Funktionen, Textvorlagen
und Fachverbraucher bereiten jetzt ausschliesslich Nachrichten mit pending_browser
vor. Weder alte Zugangsdaten noch Simulatoraufrufe koennen durch diesen Dienst
eine externe Nachricht ausloesen. Kein sent oder simulated als Ergebnis dieses
Vorbereitungswegs. Die API-Responsefelder bleiben vorhanden; meta_msg_id ist
immer leer. Die bestehenden Dev-Pfade und Simulator-Summaries bleiben erhalten;
ihre Vorbereitungsmethode beschreibt den fehlenden Netzwerkversand ausdruecklich.

Zwei weitere Befunde sind behoben: Fehlender/leerer Mandant wird vor dem
Outbox-Zugriff abgewiesen. get_outbox gibt tiefe Kopien zurueck; ein Leser kann
Empfaenger oder Status des gespeicherten Entwurfs nicht veraendern. Logs enthalten
weder Telefonnummern noch Nachrichtentexte.

## Abnahme

Alle 16 neuen Gegenproben waren vor Reparatur rot. Der HTTP-Zugang ist in den
Tests explizit verboten; beide Vorbereitungsfunktionen werden auch mit alten
Meta-Credentials tatsaechlich ausgefuehrt. Weitere Gegenproben pruefen
Empfaenger-/Statusmutation, fehlende Mandanten und private Logwerte.

Final 33 gezielte Tests bestanden in 4,28 Sekunden: 16 neue Gegenproben, 13
bestehende Template-/Outboxvertraege und vier bestehende Service-Verbrauchertests.
Keine DB, Dockerinstanz, Browseranmeldung oder externe Nachricht.

Ein zusaetzlicher breiter Lauf der fremden Service-Wave lieferte 46 gruen und
drei Fehler beim Windows-Schluesselspeicherzugriff (Zugriff verweigert); diese
Tests betreffen secrets_vault, nicht WhatsApp. Sie gelten nicht als bestanden.
Der anschliessende gezielte Lauf enthaelt ausschliesslich betroffene Verbraucher.

## Offene Integration

Die Outbox ist weiterhin fluechtig. Ein Prozessneustart verliert Entwuerfe;
es gibt noch keinen dauerhaften Replay-/Versandnachweis oder Browserarbeiter.
Leerer Mandant ist eine Wertepruefung, keine verifizierte Mitgliedschaft.
Die alten Dev-Endpunkte nehmen den Mandanten weiterhin aus Requestdaten; sie
duerfen nicht als autorisierter Browser-Versandweg verwendet werden. Der
Meta-Webhook und parallele Bestellsimulator sind in diesem Slice nicht entfernt.

Weitere Schritte und Betriebsabnahme stehen im
[Browservertrag](../workflows/whatsapp-web-computer-use.md) und im offenen
WHATSAPP-WEB-INTEGRATION-20261011. Der Teilmeilenstein beansprucht weder
vollstaendige Mandantenisolation noch funktionsfaehigen Browserbetrieb.
