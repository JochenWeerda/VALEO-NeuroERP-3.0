---
title: Geerbte CI-Testgrenzen gezielt korrigieren
type: qa
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Begrenzter erster Integrationsmeilenstein

Nach ausdruecklicher Nutzerfreigabe wurde CI-GRUEN-20261014 von Claude an Codex uebernommen. Dieser Meilenstein umfasst ausschliesslich sieben bestehende Testdateien und zwei Kennungszuweisungen im CI-Bootstrap. Kein Fuhrpark-, Finanz- oder sonstiger Fachcode wird damit veraendert; generierte Gesamtartefakte gehoeren nicht zu diesem Paket.

PCN-Mini-App und direkte Ernte-DQ-Aufrufe benennen ihre synthetische Testidentitaet ausdruecklich. Ernte-Query-Stubs unterstuetzen die produktiv verlangte Sperrschnittstelle. Der Aktionsmontagevertrag vergleicht den URL-Pfad ohne feste Queryparameter. Finanz- und Journalfixtures erlauben die erklaerte gemeinsame Probe beziehungsweise CI-Job-Datenbank und verbieten weiterhin Entwicklungsdatenbanken.

206 gezielte Finanz-, Ernte-, DQ-, PCN- und Katalogvertraege bestanden. Die CI-Bootstrapkennung wurde in genau zwei Zuweisungen durch eine synthetische Kennung ersetzt; alle anderen Skriptteile bleiben erhalten. Datenschutzguard und Shellsyntaxpruefung bestanden. Kennwoerter und Tokens wurden weder ausgegeben noch neu gespeichert. Keine neue Datenbank, Container oder Schemaaenderung.

Die automatische Freigabepruefung lehnte zuvor ein wesentlich breiteres gemischtes Integrationspaket wegen moeglicher fremder Arbeitsstaende ab. Dieser separat abgegrenzte Test-/Bootstrap-Meilenstein enthaelt keine jener Fachcode- oder Gesamtartefaktintegrationen. Die weitere Quellenintegration erfordert eigene Nachweise und einen neuen CI-Nachlauf.
