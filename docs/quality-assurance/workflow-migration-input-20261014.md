---
title: Expliziter Workflow-Migrationsvergleich ohne Demorueckfall
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-14
---

# Vergleich tatsaechlicher Definitionen

POST /process/workflow-migration/check verlangt nun den typisierten WorkflowMigrationCheckIn-Vertrag: Prozess, Quell-/Zielversion, mindestens einen alten Schritt und eine explizite Liste neuer Schritte. Eine leere Zielliste bedeutet Loeschung, keine Demoersetzung. Schritt-IDs sind eindeutig und nicht leer; Bool/Integer strikt, Zusatzfelder verboten. Alte/neue Schema-Versionen werden mitgeprueft. Der bisherige Rueckfall auf identische Agrar-Demoschritte wurde entfernt. Dies korrigiert den bestehenden Vertrag ohne neue Route, Container oder Datenbank.

Das vorhandene Migrationsregelwerk bewertet Pflichtschritte, Terminalzustaende, Rollen, Reihenfolge und Schema-Downgrades. comparison_revision ist SHA-256 des kanonischen validierten Vergleichsinhalts inklusive Versionen und Rollen. Dieser Fingerprint beweist Inhaltsbindung, ist weder elektronische Genehmigung noch Nachweis einer vollstaendigen Fachprozesssimulation oder der aktiven Produktionsversion.

Das MCP-Werkzeug migration_check traegt Version 2 und verwendet direkt das REST-Validierungsschema als inputSchema, inklusive verschachtelter Schritte. Der Transport validiert vor HTTP und gibt bei unvollstaendigem Inhalt ein sanitisiertes 422 ohne Eingabewerte zurueck. Die neue optionale kanonische input_schema-Projektion kopiert Schemas, sodass externe Veraenderung einer Ausgabe den Quellvertrag nicht aendert.

Das bestehende REST-Bindungsgate wurde um exakte JSON-Schema-Vergleiche fuer solche kanonischen Eingaben erweitert. Es expandiert lokale Referenzen und ignoriert beschreibende Titel, bewahrt aber echte Felder namens title. Gegen die frisch erzeugte Produktions-OpenAPI bestehen elf Lesebindungen und ein kanonischer POST-Vertrag. Andere POST-Werkzeuge sind damit nicht abgenommen. Die zwei neuen Schema-Komponenten und nur Eingabe/Beschreibung des Migrationspfads werden auf den aktuellen committeten OpenAPI-Stand projiziert; die fremde Arbeitskopie bleibt erhalten.

Abnahme: 89 Payload-/Migrations-/Manifest-/Transportfaelle bestanden; anschliessend 30 gezielte Schema-/Bindungs-/Transportfaelle bestanden (mit Ueberschneidung). Ein breiterer Lauf scheiterte vor Testausfuehrung kurzzeitig an UniqueConstraint im parallel geaenderten Portalmodell; der Import wurde vom parallelen Arbeitsstand korrigiert, nicht in diesem Slice. Kein Fachdatensatz und kein Reset erforderlich.

Offen: weitere POST-Transformationen und ERP-Katalog, freigegebene Capability-Version, CLI-/Berechtigungsgleichwertigkeit, Studio-Historienanzeige, vollstaendige Prozesssimulation und technische STUDIO-RELEASE-001-Sperre. Der Vergleich ist eine Voraussetzung der Releasepruefung und darf diese nicht ersetzen.
