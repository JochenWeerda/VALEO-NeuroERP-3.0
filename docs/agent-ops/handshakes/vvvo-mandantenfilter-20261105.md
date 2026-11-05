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

Die fachliche VVVO-Registerzusammenfuehrung, fehlende Erfassungswege, Audit-/Commandanbindung bleiben Folgeauftraege. Dieser Slice erteilt keine zusaetzlichen Rollen oder Schreibfreigaben und beansprucht keinen JWT-/RLS-Gesamtnachweis.

Nachlauf Faelligkeit: jetzt 23 Tests gruen; Ueberfaellige und offene Termine im eigenen Mandanten enthalten, Geschaeftstag verwendet. Zwei Gegenproben am alten Faelligkeitsfilter rot. Neun Scanner und Doku-Governance gruen. Nutzerrecherche zur VVVO-Nummer dokumentiert: [Fachgrundlagen](../../quality-assurance/vvvo-nummer-fachgrundlagen-20261105.md). Die 365 Tage bleiben interne Wiedervorlage, kein gesetzlicher Nummernablauf und keine automatische Liefersperre.
