---
title: Studio Funktionsmigration Listen 20261028
type: handshake
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Uebergabe funktionale Reklamationsliste, zentrale Listenvertraege und naechste Maskenfamilien.
---

# Studio-Listen: integrierter Meilenstein

Akzeptierte Quelle bleibt artifacts/migration-repair-source. Lieferung auf
codex/migration-parity-repair-20261022; Root-Arbeitskopien nicht blind uebernehmen.
Reklamationsseite nennt nur noch die kanonische NativeListPage-Definition.
Die komplette Listenlogik liegt in ScreenDefinition/RenderPlan/Runtime und
geteilten Renderern. Details: [Abnahme](../../quality-assurance/studio-functional-lists-20261028.md).

108 gezielte Faelle gruen (46 Frontend,62 Backend inkl.Registry/Studiovertraegen).
REST/MCP/CLI wurden mit echten signierten Identitaeten und eigenen SQL-Zeilen
geprueft. Alle Zeilen zurueckgerollt. Nachkontrolle:valeo_probe auf
rls_domain_shared_20261027,0 Sitzungen; Fenster frei. Keine Migration/Liveaenderung.

Sechs Browseransichten(1366/1440/1920,Hell/Dunkel) der echten Komponente mit
synthetischem Transport aufgenommen,axe WCAG2A/AA ohne Befund,kein horizontaler
Ueberlauf. Gefilterter Download real im Browser geprueft. Dies ersetzt keine
angemeldete E2E-Abnahme oder globale Browserfreigabe. Eigener Vorschauprozess
und temporaere Einstiegdateien nach Abschluss entfernt.

Vier ungenutzte Batch15-IDs entfallen:finance/bankkonten-stamm,
finance/kreditoren-stamm,qualitaet/reklamation-detail,qualitaet/reklamationen.
Die aktiven URLs und kanonischen Detailseiten/Fallbacks bleiben unveraendert.
Keine kuenstliche Aliasverdrahtung. Generierter Stand853/A853/B853/C852/E801;
52 verbleibende Runtime-Punkte,844 native Eintraege,5 strukturell ready.

## Fortsetzung

- CRM-Aktivitaeten braucht deklarative Benutzer-/Datumsfilter und einen korrekten
  serverseitigen Gesamtbestand; alte SD hat unpassende Felder/Routen.
- Lieferliste braucht Mengen-/Statusprojektion, feste Statusfilter und die
  bisherigen rollenbezogenen Arbeitslinks. Kein blindes Umhaengen.
- Neun Prozessraeume brauchen gemeinsame Graph-/Instanz-/Lifecycle-Primitive;
  der Katalog ist separat zu migrieren. Die vorhandenen zehn generischen SDs
  zeigen auf Dead-Letter und sind kein Funktionsnachweis. Siehe
  [Familienplan](../../quality-assurance/studio-workflow-migration-plan-20261028.md).
- Fehlerkorrektur in FlowSpineWorkspace.handleAction integriert:fehlgeschlagener
  POST navigiert nicht weiter,Fehlertoast bleibt.4 Komponententests gruen.
- Waage,Annahme,Webhooks und Kundenstamm haben reale zusaetzliche Funktionen;
  vor Migration deren Daten-/Aktionsvertraege vollstaendig uebernehmen.

Nicht die unterbrochenen alten Reklamationsentwuerfe aus ignored artifacts blind
zurueckkopieren:der jetzige Vertrag ist integriert und serverseitig abgesichert.
Keine neue Testdatenbank/Container,kein Probe-Reset,keine persoenlichen Daten in Git.
