---
title: Studio-Freigabestandard
status: verbindlich
type: reference
owner: Codex
last_reviewed: 2026-10-15
---

# STUDIO-RELEASE-001

Eine Studio-Definition darf erst produktiv aktiviert werden, wenn ihre Schnittstellenartefakte synchronisiert, ihre Änderungen nachvollziehbar versioniert, ihre fachlichen Invarianten erfolgreich getestet und alle verpflichtenden Prozesssimulationen bestanden sind. Die menschliche Freigabe bezieht sich ausschließlich auf die geprüfte unveränderliche Version.

## Verbindliche Nachweise

- Registry, REST/OpenAPI, MCP und CLI müssen dieselbe freigegebene Capability-Version, Eingabe, Berechtigung und Wirkung verwenden. Advisory-Auswertungen erteilen keine Ausführungsgenehmigung.
- Die Historie enthält überprüften Urheber, Zeitpunkt, Aktion, Status, Revision und Ausgangsrevision. Vergleiche lesen unveränderliche Snapshots ausschließlich im authentifizierten Mandanten.
- Eine Simulation verwendet reale Domain-Commands und Fachdienste, kontrollierte Testdaten und den gemeinsamen Prüfstand. Produktive Daten und externe Systeme dürfen keine Wirkung erfahren. Eine bloße Szenariobeschreibung ist kein Nachweis.
- Der Nachweis muss an Mandant, Entwurf, exakte Revision, Profil und die geprüften Fach-/Vertragsartefakte gebunden sein. Änderung, unbekanntes Profil, unvollständige Kette oder ein fehlgeschlagener Pflichtcheck verhindern Veröffentlichung.
- Die Freigabeprüfung muss am gemeinsamen Statuswechsel gelten, auch für andere Adapter. Vier Augen und menschliche Administrationsrolle bleiben erforderlich.

## Implementierungsstand 2026-10-15

Der gemeinsame Statuswechsel verlangt einen serverseitig gespeicherten, erfolgreichen Nachweis fuer die exakte Kandidatenrevision. Mandant, Entwurf, Definitionshash und Fach-/Vertragsartefakthash muessen uebereinstimmen. Aktuelle REST-, MCP- und Agentenprojektionen werden vor Simulation und Freigabe abgeglichen. Alte Entwicklungsveroeffentlichungen ohne Nachweis sind nicht als aktive Definition ladbar.

grain.v1 prueft die echte Annahme-, Qualitaets-, Vorsteuer-, Self-Billing-, Hauptbuch-, Bestands- und Stornokette, Mandanten- und Rollengrenzen, Unveraenderbarkeit festgeschriebener Annahmen, Wiederholung, Nummernvergabe und Rollback. Der gemeinsame Pruefstand wird transaktional verwendet; eine globale transaktionale Sperre verhindert konkurrierende Simulationslaeufe (HTTP 429, kein falscher Fehlernachweis). Quellcodeaenderungen erfordern einen kohärenten Neustart der Simulation.

Das Profil deckt den festen Agrar-Basispfad ab. Unmodellierte Fachaktionen, editierbare Agentenfelder und fachliche Workflow-/Kontierungsvarianten sind gesperrt. Ein erfolgreicher Basispfad bescheinigt keine beliebige Prozessvariante oder systemweite CLI-Schreibgleichwertigkeit. Die Korrekturpruefung weist die Abweisung verbotener Aenderungen nach; sie ersetzt keinen vollstaendigen fachlichen Korrekturbelegprozess.

Studio-Entwurfsaktionen verwenden die vorhandene beleg_write-Rollenregel. Menschliche Admin-Freigabe und Vier Augen bleiben erforderlich. Die Oberflaeche erhaelt diese Rechteprojektion vom Server. Native Historienmasken zeigen Revision, Actor, Zeit, Status, Differenz und Simulationsergebnis. Nach Aenderungen wird ihr Cache gezielt invalidiert.

Abnahmen einschliesslich positiver Vier-Augen-Browserfreigabe und nachgewiesenem Rechteentzug: [Studio-Abschluss](../quality-assurance/studio-closure-20261015.md). Bedienung mit echten Screenshots: [Studio-Freigabe](../benutzerhandbuch/studio-freigabe.md). Weitere Profile bleiben deaktiviert, bis ihre eigene vollstaendige Kette nachgewiesen ist.
