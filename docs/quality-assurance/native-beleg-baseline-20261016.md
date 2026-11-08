---
title: Kanonische native Belegmasken als gepruefter Bestand
type: reference
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Bestehende Belegvarianten sicher verfuegbar halten

Neun native Belegvarianten kommen im bereits genehmigten synthetischen Sichtpruefungsmandanten ausschliesslich aus dem gemeinsamen Code-Builder. Andere Mandanten bekommen daraus keine Definition; der globale Maskenkatalog wird nicht um diese Testfreischaltung erweitert. Der reservierte Namensraum beleg/ wird nicht aus editierbaren Studio-Datensaetzen ueberlagert.

Das bisherige Veroeffentlichungsskript prueft jetzt nur die nativen Definitionen. Es erzeugt weder Entwuerfe noch Freigaben, Zweitpruefer oder Studio-Simulationsnachweise. Der alte --apply-Aufruf wird erklaert abgewiesen. Der vorhandene lesende --adressen-Aufruf bleibt fuer die bereits vorhandenen Referenzbelege erhalten und ist auf denselben genehmigten Mandanten begrenzt.

31 bestehende/neue Vertraege pruefen Belegform, alle neun Governance-Definitionen, fremde und fehlende Mandanten sowie wiederholte nebenwirkungsfreie Pruefung. Die normale Studio-Freigabe bleibt unveraendert gesperrt, wenn ihre fachlichen Nachweise fehlen. Dies sichert den bisherigen nativen Bestand; es ist keine vollstaendige Studio-Migration oder allgemeine Produktivfreigabe.
