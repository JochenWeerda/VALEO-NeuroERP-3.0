---
title: Amtlicher eBilanz-Konzeptkatalog und explizite XML-Entwuerfe
type: explanation
audience: [architect, entwickler, qa]
owner: domain/finance
status: proposed
last_reviewed: 2026-10-08
---

# ADR-079: eBilanz-Entwurf und externe Bestaetigung

**Status:** Proposed
**Datum:** 2026-10-08

## Kontext

Der historische Teilkatalog enthielt unzutreffende GCD-Pfade. Der entfernte
ERIC-Simulator darf durch einen neuen lokalen XML-Erfolg nicht wieder entstehen.

## Entscheidung

Taxonomie 6.9 wird aus dem amtlichen XBRL-Paket hashgebunden in einen
deterministischen GCD-/Kernkonzeptkatalog ueberfuehrt. Generierung ist ein
Wartungsschritt; Requests verwenden den lokalen Katalog ohne Netzabruf.
Kein neuer Container, Kontext, Auth-Modell oder Datenbankschema.

Der Finance-Service erzeugt ausschliesslich einfache explizite Fakten in einer
XBRL-Instanz mit den amtlichen Namespaces, Schema-Referenzen, Periodenkontexten
und EUR-/pure-/shares-Einheiten. Zahlen werden dezimal und ohne Rundung
serialisiert; XML-Zeichen werden escaped. Unbekannte/abstrakte/Tupel-Konzepte,
unabgenommene Typen oder widerspruechliche Perioden werden abgewiesen.
Kontenzuordnung, Tupel, Dimensionen, Pflichtfeld-/Rechenregeln und Hersteller-
Validierung sind weitere Fachvertraege, die dieser Entwurf nicht ersetzt.

## Konsequenzen

Download am vorhandenen tenantgebundenen Export verlangt Finance-Schreibrechte.
Neue Entwurfsmetadaten verwenden 6.9 fuer Periodenbeginn 2025/2026; IFRS- oder
historische andere Taxonomie-Exporte sind in diesem Download nicht abgenommen.
Bestehende Datensaetze bleiben erhalten. Die XML-Bytes werden heruntergeladen,
nicht archiviert oder als uebertragen markiert. Kein Status-/Ticket-Update.
Antwort `DRAFT_UNVALIDATED` und Readiness `repo_contract_ready=false` bleiben
sichtbar. Amtliche Validierung/Arelle und ERiC-Empfang brauchen eigene Abnahmen.

Quelle: [amtliche eSteuer-Taxonomien](https://www.esteuer.de/).
6.10 ist veroeffentlicht, die Echtuebermittlung wird dort erst fuer Mai 2027
angekuendigt; das aktuelle Entwicklungsdatum wird nicht als Freigabe ausgegeben.
Details und Betrieb: [QA](../quality-assurance/ebilanz-xbrl-draft-20261008.md).
