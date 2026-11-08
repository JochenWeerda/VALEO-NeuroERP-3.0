---
title: Gemeinsame Sitzungs- und Agentengrenze
type: explanation
audience: [architect, entwickler, agent]
owner: Codex
status: accepted
last_reviewed: 2026-10-12
description: Umsetzung der beauftragten Identitaetsarchitektur im bestehenden Backend und persistenten Redis.
---

# ADR-083: Gemeinsame Sitzungs- und Agentengrenze

**Status:** Accepted. **Datum:** 2026-10-12.

## Kontext

Die Umsetzung des zentralen Identitaetsentwurfs ist vom Auftraggeber beauftragt.
Die Annahme dieser Entscheidung bedeutet keine abgeschlossene Lieferabnahme.

## Entscheidung

Provideridentitaet und ERP-Mandant gelten auch fuer interne Werkzeugaufrufe.
Das Backend bindet einen verifizierten Kontext an die Anfrage und entfernt ihn
nach deren Ende. Urheber, Rollen und Ausfuehrungstoken stammen aus diesem Kontext.
Anfrageinhalte koennen ihn nicht erweitern. Interne HTTP-Aufrufe durchlaufen den
Produktionsdienst; die gesonderte Kompatibilitaets-App dient ausschliesslich Tests.

Sitzungsbeginn, Aktivitaet und Widerrufe liegen im vorhandenen Redis mit AOF.
Atomare Pruefungen verhindern das Wiederbeleben abgelaufener Sitzungen. Sid bzw.
Keycloaks session_state bindet auch erneuerte Zugriffstoken an denselben Widerruf.
Ausfall des gemeinsamen Speichers verweigert Zugriff. Keine Prozesslokal-Fallbacks.
Streams pruefen Widerruf erneut vor Fachausgabe und beim Warten. Ausgehende
Streamdaten erneuern keine Aktivitaet. Blockierende Speicher-/Providerzugriffe
laufen ausserhalb der Ereignisschleife; Verbindungspools werden wiederverwendet.

Agenten benoetigen eigene Provideridentitaeten und begrenzte serverseitige Mandate.
Rechte, Mandant, Auftrag, Inhaltsfassung und Ressourcenbudget werden vor Wirkung
geprueft. Menschliche Freigaben benoetigen einen anderen geprueften Urheber.
Diese Agentenvertraege werden in weiteren Teilschritten an die bestehenden
Ausfuehrungswege gebunden; Konfigurationsfelder allein sind kein Enforcement.

## Konsequenzen

Browserclients verwenden PKCE und entfernen Token-Rueckfaelle. Logout sperrt
lokal sofort, widerruft serverseitig und beim Provider und meldet einen nicht
bestaetigten Widerruf. Ein laufender Refresh darf den Logout nicht rueckgaengig
machen. Eine Rollen-Ablehnung beendet keine gueltige Sitzung.

Redis ist fuer die Sicherheitsgrenze eine notwendige Abhaengigkeit. AOF benoetigt
ein geschuetztes dauerhaftes Volume und eine getrennte Sicherungsstrategie.
Auditereignisse enthalten verifizierte Subjektkennungen, keine Roh-Token; ihre
Aufbewahrung und Integritaet sind eigenstaendige Betriebsvertraege.

Externe Providerrollenwechsel, zentrale Benutzerabschaltung, starke erneute
Authentifizierung und autonome Hintergrundmandate brauchen weitere konkrete
Integrationsnachweise. Die operative QA benennt den jeweils gelieferten Stand.
