---
title: Verbindliche Autorisierung geschaeftlicher Schreibwege
type: reference
audience: [entwickler, sicherheit, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-19
version: 1.0.0
description: Nutzerentscheidung zur Schliessung ungepruefter Schreibwege mit bestehenden Bereichsrollen und gleicher Durchsetzung an allen Adaptern.
---

# Entscheidung vom 19.10.2026

Der Nutzer hat die Entscheidung ueber das gemeldete Schreibrechte-Inventar beauftragt. Verbindlich ist die bestehende zentrale Identitaets- und Rollenarchitektur. Es entsteht kein zweites Rechtesystem. Fachrollen und bestehende Sonderrechte bleiben fuehrend; insbesondere [finance_roles.py](../../../app/auth/finance_roles.py) und die vorhandenen Bereichswaechter. [MCP-WRITE-001 bis015](../mcp-write-standard.md) gelten kanalgleich fuer REST, Maske, MCP und CLI.

## Verbindliche Regeln

1. **WRITE-AUTH-001: Keine implizite Schreiberlaubnis.** Ein geprueftes Token, ein passender Mandant, eine sichtbare Maske oder ein HTTP-Pfad gewaehrt noch kein Fachrecht. Jeder geschaeftsveraendernde Weg braucht eine explizite serverseitige Autorisierungsentscheidung vor Mutation und externer Wirkung. Fehlt eine belastbare Zuordnung, bleibt die Aktion gesperrt.
2. **WRITE-AUTH-002: Vorhandene Bereichsrollen.** Entwurf und regulaeres Bearbeiten verwenden die bestehenden jeweiligen BEARBEITEN-/ADMIN-Rollen oder ausdruecklich vorhandene Sonderrechte. Ein bereichsfremdes Bearbeitungsrecht erlaubt keine Mutation. Generische Rollen wie manager werden nicht automatisch in neue Freigaben aufgenommen. Bereichsuebergreifende Ausnahmen werden aus bereits beschlossenen Fachvertraegen uebernommen, etwa Belegbearbeitung und Kontenplanpflege.
3. **WRITE-AUTH-003: Administration zuerst.** Anlegen, Aendern, Loeschen und Deaktivieren administrativer Organisations-/Identitaetskonfiguration verlangt die bestehende administrative Berechtigung. Fuer die bestaetigte Niederlassungsloeschung ist das mindestens die vorhandene Rolle admin im autorisierten Mandanten. Globale Plattformoperationen brauchen ihr vorhandenes aktionsspezifisches Plattformrecht; eine lokale Fachadministration genuegt nicht. Auch Administratoren duerfen keine fremden Mandanten allein per Parameter auswaehlen.
4. **WRITE-AUTH-004: Fachfreigaben bleiben wirksam.** Buchen, Zahlung, Storno, Periodenabschluss, Bestandskorrektur und Rechte-/Kontingentvergabe verwenden ihre bestehenden aktionsgebundenen Rechte und Freigaben. Eine allgemeine Bereichsrolle ersetzt keine erforderliche Genehmigung, starke Autorisierung oder Vier-Augen-Regel. Bestehende explizite Admin-Zulaessigkeit wird nicht durch einen neuen globalen Bypass erweitert. Festgeschriebene Belege bleiben unveraenderlich; Korrektur und Storno folgen den Fachcommands.
5. **WRITE-AUTH-005: Objekt- und Mandantengrenze.** Rollenpruefung plus autorisierter Mandantenkontext plus Datensatz-/Beziehungspruefung sind gemeinsam erforderlich. Aufrufer-, Freigeber- und Agentenidentitaeten stammen ausschliesslich aus vertrauenswuerdigem Kontext. Payload und Clientkopfzeilen waehlen keine Rechte. Agentenrechte bleiben durch Mandat, Capability-Freischaltung und menschliche Freigabepflichten begrenzt.
6. **WRITE-AUTH-006: Gleichwertige Wege.** Direkter REST-Altweg, Domain-Command, Maske, CLI, MCP und Hintergrundauftrag muessen dieselbe Fachentscheidung durchsetzen. Einen abgesicherten neuen Storno-Command neben einem ungeschuetzten alten /cancel zu haben ist keine abgeschlossene Reparatur. Vorschau und Simulation pruefen dieselben Zugriffsvoraussetzungen; sie duerfen gesperrte Daten nicht indirekt offenlegen.
7. **WRITE-AUTH-007: Technische Ausnahmen sind eng.** OIDC-Anmeldung, Token-Erneuerung und ausschliesslich lesende POST-Abfragen sind nicht pauschal mit Geschaeftsmutationen gleichzusetzen. Provider-Webhooks brauchen ihren eigenen kryptografisch geprueften technischen Absender, feste Mandantenzuordnung und eng begrenzten Auftrag. Eine oeffentliche Ausnahme wird pro konkretem Vorgang begruendet und getestet; keine anonyme Fachschreiberlaubnis.
8. **WRITE-AUTH-008: Ratsche plus echte Abnahme.** Das gemeldete Inventar von rund1600 Wegen ist eine heuristische Pruefliste, keine bestaetigte Anzahl ausnutzbarer Luecken. Dekorator, Router-/Globale-Dependency und tatsaechlich aufgerufener Domain-Command werden gemeinsam verfolgt. Die Ratsche darf neue unbekannte Wege verhindern, aber bestehende Luecken nicht dauerhaft legitimieren. Geschlossen ist ein Weg erst mit negativem HTTP-Nachweis vor Mutation und positivem Fachnachweis.

## Umsetzung und Prioritaeten

1. Bestaetigte administrative Mutationen einschliesslich Niederlassungsloeschung sowie Benutzer-/Rollen-/Mandantenkonfiguration absichern.
2. Kritische Finanz-, Zahlungs-, Lager- und Belegaktionen samt direkten Altwegen schliessen; bestehende Freigabevertraege erhalten.
3. Bereichsweise alle uebrigen Mutationen auf bestehende Fachwaechter und Commands abbilden. Nicht klassifizierte Aktionen bleiben gesperrt; ueberholte Wege nach Verbraucherpruefung entfernen.
4. CI-Inventar kontinuierlich gegen die produktive Wurzelanwendung main:app fuehren. app/main.py bleibt eine ausdrueckliche Testgrenze und liefert keinen Produktionsnachweis.

Claudes laufender Rollen-Inventar-/Maskenrollout setzt diese Entscheidung innerhalb seines Workboard-Besitzes um. Codex behält den getrennten Audit-Identitaets-/Transaktionsslice. Keine pauschale Rollenvergabe an Test- oder echte Nutzer ist mit dieser Entscheidung verbunden.

## Abnahme je Fachgruppe

- Nicht angemeldet401; angemeldet ohne Fachrecht403; fremdes Objekt beziehungsweise fremder Mandant nach geltendem Objektvertrag404/403. Dabei keine Mutation, Outbox-Nachricht oder externe Wirkung.
- Berechtigter Aufruf erfolgreich; identischer Retry ohne Doppelwirkung; Freigabe-/Vier-Augen-Grenzen erhalten. Auch der direkte Altweg wird negativ geprueft.
- Tests verwenden die produktiven Guards, echte signierte Identitaeten und fuer Mutation die vorhandene gemeinsame Pruefdatenbank mit eigenen isolierten Daten. Keine neue Datenbank oder Container je Test/Agent.
- Gruppenuebergreifende Rechte werden positiv geprueft, damit Einkauf, Agrar und Kontrakt durch eine pauschale Finanzrolle nicht ausgesperrt werden. Fachliche Reads werden mit dieser Schreibentscheidung nicht pauschal eingeschraenkt.

Das Dokument ist die verbindliche Entscheidung, kein Nachweis bereits vollstaendig geschlossener Endpunkte.
