---
title: Native Webhook-Maske und deklarative Leseansichten
type: reference
audience: [agent, entwickler, qa]
owner: Codex Lead
status: in Arbeit
last_reviewed: 2026-11-05
version: 1.0.0
---

# Studio-Webhooks

Eigener Worktree artifacts/psm-zulassungen-20261104, Zweig codex/studio-webhooks-native-20261105 auf Integrationsstand 6823018ae. Claim 2efc17153 vor Implementierung. Keine Datenbank, Container-, Rollen- oder Live-Migrationsaenderung.

Die Webhook-Seite verwendet NativeListPage und den StammListenParent. Registrierung deklariert Ereignis, Ziel-URL und Passwortfeld fuer das optionale Signiergeheimnis; Abmeldung verwendet die stabile Datensatzkennung statt einer veraenderlichen Listennummer. Beide Aktionen bleiben fuer Agenten gesperrt. Den vorhandenen menschlichen Fachendpunkten wird hier kein neuer serverseitiger Wiederholungsschutz bescheinigt.

readView bindet eine GET-Leseansicht an versionierte Maskenaktionen. Studio validiert lokale registrierte GET-Wege und echte Antwortspalten. Identitaetsplatzhalter, Fremd-URLs, Query-Strings, widerspruechliche Transporte und ungueltige Spalten werden abgewiesen. CLI und MCP verwenden denselben GET ohne Nutzlast. MCP reicht nur das Bearer-Token weiter, keine Mandantenwahl. Fachautorisierung bleibt beim Zielendpunkt.

Der Dialog nutzt den UniversalMaskRuntime mit echtem direkten Tabellenweg. Eine anfangs falsche Maskenprojektion wurde vor Abnahme korrigiert. Identitaetswechsel oder fehlendes Aktionsrecht blenden Daten aus; Cache-Schluessel trennen Benutzer und Mandant. Keine private Webhook-Historienseite.

## Nachweise

Erster Frontendlauf: 31 Tests bestanden (Leseansicht, Tabellenbindung, vorhandener Downloadvertrag). Erste Typpruefung bestanden. Backend-/CLI-/MCP-/Listenlauf: 84 Tests bestanden, ohne Datenbank. Registry-Paritaetshilfe initialisiert die Stammregistry vor der Iteration; der vorher beobachtete RuntimeError wird an seiner Ursache behoben, ohne Aktionen auszulassen. Der Cockpit-Ausnahmeeintrag fuer Webhooks ist entfernt: Der allgemeine Worklist-Vertrag prueft die Maske regulaer. Ein importierter, hashgebundener nativer Studio-Draft hat keine Validierungsverletzung (reine In-Memory-Pruefung; nichts aktiviert).

## Noch abzunehmen

Sicht-/Kontrastpruefung und authentifizierte Browserabnahme. Alte spezialisierte Oberflaeche und Tests bleiben bis zum Ersatznachweis erhalten. Keine komplette Studio-made- oder Gesamtfreigabe. Kein produktiver Studio-Entwurf aktiviert.

## Gepruefter Zwischenstand

Erweiterter Backend-/CLI-/MCP-/Studio-Baseline-/Feldvertragslauf: **108 passed, 4 warnings**. Vier fokussierte Frontenddateien: **35 passed**; sechs bestehende Listen-/Studio-/Verkaufsdateien: **19 passed**. Abschliessende volle Frontend-Typpruefung Exit 0. Neun Verbesserungsscanner bestanden, stabiler Snapshot. Anlage und Abmeldung sind im zentralen Dialog getestet, einschliesslich Pflichtfeldern, Passwortdarstellung, ausdruecklicher Bestaetigung, stabiler UUID und verweigertem Recht. Ein zuvor pauschal behauptetes Audit im allgemeinen Bestaetigungstext ist durch eine sachliche Ausfuehrungsbestaetigung ersetzt.

CLI-Register, Aktionskatalog, MCP-Zuordnung, Rollenprojektion, Studio-Versionen, Codeinventare, Architekturindex und Agent-Handbuch aus den Quellen neu erzeugt. Der Architekturcheck fand die fehlende Klassifikation des neuen internen Vertragsmoduls; Platform-Zuordnung und Domain-Impact-Note sind nachgetragen. Kein neuer Container, keine neue Route und keine Rechtefreischaltung. Bekannte OpenAPI-Warnungen sind kein Nachweis ihrer Behebung.

Die Komponentenabnahme ist synthetisch und enthaelt keine echten Webhook-Aussendungen. Kein authentifizierter Studio-CLI-Speichervorgang und keine Browser-Sichtabnahme behauptet. Die generische MCP-Aktionsliste liest Zeilenaktionen; der aeltere Sprach-Aktionskatalog erfasst weiterhin nur Kopfaktionen. Diese bestehende Katalogluecke ist nicht durch einen zweiten Registereintrag kaschiert.
