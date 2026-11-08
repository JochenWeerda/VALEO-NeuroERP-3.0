---
title: Agrar-Kontraktallokation - Wiegescheinreferenz
type: qa
audience: [entwickler, qa]
owner: agrar_allocation_guard
status: umgesetzt
last_reviewed: 2026-10-27
---

# AGRAR-ALLOCATION-REFERENCE-20261027

## Vertrag und Befund

ADR-077 bestimmt `domain_inventory.weighing_tickets` als fuehrenden Wiegeschein.
`AgrarContractAllocation.ticket_id` ist optional und referenziert dessen ID.
Der Agrar-Kontraktservice pruefte vor der Allokation nur den Mandanten des
Kontrakts. Eine ID eines fremden Wiegescheins konnte als Referenz gespeichert
werden; ohne Anwendungsschutz reicht die einfache Fremdschluesselbeziehung
nicht fuer Tenant-Isolation.

## Umsetzung

`AgrarContractService.allocate` sucht einen angegebenen Wiegeschein vor der
Restmengen- und Statusaenderung mit **ID und aktuellem Mandanten**. Fehlende
und fremde IDs erhalten denselben `EntityNotFoundError` (HTTP 404 im
bestehenden Router). Die optionale Referenz bleibt optional. Nichtpositive
Mengen werden nun auch bei direktem Serviceaufruf abgewiesen; der bestehende
HTTP-Vertrag fordert bereits `gt=0`. Rollen, Kontraktstatus und Obergrenze
bleiben unveraendert.

## Pruefung

`python -m pytest --noconftest -o addopts='' tests/test_agrar_contract_allocation_reference.py -q`
ergab **6 bestanden**. Geprueft: eigener, fremder und fehlender Wiegeschein,
optionale Referenz sowie Menge null/negativ. Bei abgewiesenen Aufrufen bleiben
Restmenge und Status unveraendert; es gibt kein Add und keinen Commit. Der
Test verwendet ausschliesslich Repository-Attrappen. `--noconftest` verhindert
die globale Fixture, die bei regularem Pytest den gemeinsamen Pruefstand
ansprechen kann. Der erste regulaere Pytest-Aufruf wurde nach dem Testbeginn
abgebrochen; kein erfolgreicher DB-Test wird daraus behauptet.

## Grenze

Keine PostgreSQL-, RLS- oder HTTP-End-to-End-Abnahme in diesem Slice. Das
exklusive Pruefstandfenster liegt beim Lead. Die Abnahme belegt den
Service-Guard und seine Wirkung bei isolierten Aufrufen.


## Lead-Nachlauf

Die direkte Servicegrenze weist nun auch nicht endliche Mengen (NaN und
positive/negative Unendlichkeit) vor jeder Mutation ab. Die isolierte
Fallgruppe umfasst damit neun statt sechs Faelle; sie ist Teil der
integrierten RLS-/Agrarabnahme. Ein optionaler Wiegeschein bleibt optional.
