---
title: Uebergabe VVVO-Mandantenfilter
type: reference
audience: [agent, entwickler]
owner: Codex Lead
status: lokal abgenommen
last_reviewed: 2026-11-05
version: 1.0.0
---

# VVVO und Sachkunde: SQL-Mandantengrenze

Im eigenen Branch `codex/vvvo-mandantenfilter-20261105` filtern Einzelabfragen und VVVO-Update ID plus Mandant. UPDATE RETURNING verhindert Scheinwirkung, wenn der Datensatz inzwischen nicht mehr zugaenglich ist. Fremde und fehlende Datensaetze haben denselben Fehlervertrag.

21 Tests bestanden, Gegenprobe am alten Code drei gezielte Fehler. PostgreSQL-TEMP-Daten komplett zurueckgerollt, keine neue DB oder Migration; Revision unveraendert. Generator-Gesamtcheck, neun Integritaetsscanner und Doku-Drift gruen. [Nachweise und Grenzen](../../quality-assurance/vvvo-mandantenfilter-20261105.md).

Die fachliche VVVO-Registerzusammenfuehrung, fehlende Erfassungswege, Faelligkeitslogik und Audit-/Commandanbindung bleiben Folgeauftraege. Dieser Slice erteilt keine zusaetzlichen Rollen oder Schreibfreigaben und beansprucht keinen JWT-/RLS-Gesamtnachweis.
