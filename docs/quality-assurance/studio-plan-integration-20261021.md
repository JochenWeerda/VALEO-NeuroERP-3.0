# Studio: Pflichtplan, UI und MCP (2026-10-21)

Claim STUDIO-PLAN-INTEGRATION-20261021, Fortsetzung ADR-084 (Proposed).

Der gespeicherte Plan ist Pflicht im bestehenden Publikationsweg. Nach der
bisherigen Simulationspruefung werden Historienidentitaet, Revision, Definition,
Compiler-/Kataloghash und Bindung neu geprueft. Runtime verwirft veraltete oder
fehlende Planbelege. Vorgeschlagene, noch ungespeicherte Bindungen und jede
Schemaaenderung ohne Bereitstellungsnachweis bleiben gesperrt. Keine DDL.

Die bestehende Studio-Authoring-Oberflaeche bietet Aenderungsplan festhalten;
sie benutzt den vorhandenen Servercommand, bindet den Erfolg an Draft/Revision
und sperrt die Freigabe bei lokaler Aenderung oder fehlendem Plan. Bestehende
Theme-Tokens, keine neue handgeschriebene Geschaeftsmaske. Eindeutiger React-Key
fuer Plan und Historie verhindert mehrfach stehenbleibende Komponenten.

MCP studio.migration.plan / studio.migration_plan.prepare v1 leitet execute an
denselben HTTP-Command wie UI/CLI weiter. Explizit freigeschaltete R1-Capability,
bestehender Scope belege:write und bestehende Rollen beleg_write; keine neuen
Nutzerrechte. Kein SQL, DDL, Business-Write oder Freigabebefehl. Identitaet kommt
nur aus dem weitergeleiteten Bearer-Token. Die anderen drei Modi pruefen nur die
Syntax, speichern nichts und weisen auf die erst bei execute gepruefte
Zielautorisierung hin. Antwortgroesse begrenzt, keine Redirects, striktes JSON.

Abnahme:106 Serververtraege im breiten Lauf bestanden; danach16 Planvertraege
inklusive eines zusaetzlichen SQL-Publikationsvertrags bestanden (107 eindeutige
Tests insgesamt, Ueberlappung nicht doppelt zaehlen).14 Oberflaechen-/APIclienttests
bestanden, TypeScript ohne Fehler. Der SQL-Publikationsvertrag prueft reale
Historienabfrage, fehlenden Pflichtplan, anschliessende erfolgreiche Bindung und
Runtimeabruf innerhalb der bestehenden Rollback-Transaktion. Negativvertraege pruefen
fehlende/manipulierte/veraltete Plaene, Schemaausfuehrung ohne Nachweis, Rollen,
Scopes und fremde Mandanten. Reale signierte REST/CLI/MCP-Aufrufe benutzen den
bestehenden valeo_probe mit Ruecknahme eigener Daten. Nur externer Sitzungsdienst
und HTTP-Verbindung zum Testserver sind isoliert; Zielautorisierung bleibt real.
Lifecycle-Simulation verwendet explizite vorhandene Unitbelege, keine Behauptung
einer vollstaendigen Geschaeftskette. Kein weiterer Container/DB/Reset.

Grenzen: keine Browser-Sichtabnahme oder Live-Rollout dieses Standes; allgemeine
CRUD-/Capability-Generierung, Schemaeditor/-bereitstellung und alle kanalweisen
Fachketten sind weiterhin offen. not_verified wird nicht zu bestanden erklaert.
