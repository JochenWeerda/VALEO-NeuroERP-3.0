---
title: Sicherheitspatches und CI – Handoff
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-29
version: 1.0.0
description: Gepatchte Node-Abhaengigkeiten, unveraenderte Source-Repair-Grenzen und belegte Runtime-Vertraege.
---

# Sicherheitspatches

Der Security-Scan40833492184 auf9d09356b6 blockierte sieben neue Findings in
seroval1.6.3 undi18next-http-backend4.0.2. Root-Overrides und direkte Frontend-
Abhaengigkeit verwenden nun seroval1.6.11 beziehungsweise i18next-http-backend4.0.4.
Die offiziellen Advisories bestaetigen die korrigierten Versionen:
[Serializer](https://github.com/advisories/GHSA-f86p-h4j2-7qgj),
[Sprach-Queryparameter](https://github.com/advisories/GHSA-3cmx-xjww-583x).

Die Aufloesung erfolgte in einer eigenen Installation unter dem ignorierten
artifacts/security-fix-runtime-20261029. Im Paketbestand des Lockfiles sind
exakt die beiden betroffenen Versionen ersetzt; keine weiteren Paketversionen
hinzugefuegt/entfernt. Frozen-Install erfolgreich. Bestehende node_modules-
Junctions und fremde Installationen wurden nicht veraendert.

Die installierten braces/deepmerge-Reparaturdateien, Lizenz und Patchhashes
stimmen mit dem geprueften Bestand ueberein. Nur Manifest-/Lock-Bindungen der
bestehenden Reviews sind neu berechnet. Reviewdatum, Ablauf30.10., Zielversion,
Patch und installierte Sourcehashes bleiben unveraendert. Keine neue VEX-/
Allowlist-Regel und keine abgesenkte Schwere-/Releasegrenze.

Produktionsaudit und unveraendertes Gate bestaetigen0Advisories,0Findings,
0blocked und release_allowed=true.76 Security-/Source-Repair-Verhaltenstests
bestehen. Zwei neue harmlose Gegenproben scheitern an den frueher installierten
Paketen und bestehen an den Patchversionen: manipulierter Typed-Array-
Konstruktorname sowie Sprachwerte mit &/= im Query-loadPath. Keine echten
Netzrequests in diesen Tests, kein ausfuehrbarer Angriffscode notwendig.

# CI-Nachlauf

Die kanonische OP-Projektion nutzt business_today statt direktem Systemdatum.
Ein Zeitzonen-/Monatsgrenzfall und due-today-/settled-Grenzen sind geprueft.
Dynamische OP-Relationsbezeichner akzeptieren nurpublic/domain_erp; fremde
Schemanamen werden vor Folge-SQL abgewiesen. SQL-fstring-Guard gruen, enge
Reviewmarker begruenden Code-Konstanten/Allowlist und gebundene Werte.
Die Business-Time-Ratsche ist ausschliesslich um zwei bestehende Fundstellen
abgesenkt:191 verbleibende direkte Kalenderstellen projektweit. Baseline-
Integritaet und Toolchain-Pins bestehen; kein Schwellenanstieg.

Die beiden Dispositionsfehleranzeigen erhalten ul/li-Semantik und haben den
Alert auf einem inneren Absatz.20 Rendererfaelle inklusive des gezielten
axe-list/listitem/aria-required-children-Fehlerfalls bestehen. Debitorentests
verwenden nun echte Builder-/Transport-/Runtimevertraege statt eines nicht mehr
aufgerufenen Legacyhooks. Batch11/alte und neue OP-Renderertests bestehen.

Mit der neuen Patchinstallation:90Frontendfaelle gruen; hinzu kommen16enge
Backend-Lesewegfaelle sowie die76Sicherheitstests. Vollstaendige Typpruefung
und Produktionsbuild dieser Installation sind gruen. Der echte Produktions-
Browsercheck zeigt den bedienbaren SSO-Knopf auf/login ohne PageError. Siehe
[Bild und Messergebnisse](screenshots/security-prod-patches-20261029/result.json).
Eigener Preview3012 beendet. Keine DB-/Container-/Rollenveraenderung.

# Verbleibende Gesamtarbeit

Die gezielten Slices sind abgenommen, keine Gesamtfreigabe aller ERP-Fachmasken.
47Runtimepunkte sowie weitere eigenstaendige fachliche UI-/Seitenregistrierungs-
und Schemafehlstellen bleiben im Arbeitsinventar. Der aktuelleSmoke-Bootstrap
ist in allenfuenfCI-Domaenen gruen; nachfolgende Fach-Smokes zeigen fehlende
Maskeninhalte und werden nicht durch Readiness-Lockerungen verdeckt.
Drei fehlende Live-Tabellen sind gesondert auditiert; Tabellen allein wuerden
unsichere Abschreibungs-/Abgangs-/Rahmenabruf-Schreibpfade freischalten.
Vor deren DDL muessen Atomaritaet, Fachrechnung, Referenzen und RLS nachgewiesen
sein. In diesem Slice wurde keine Migration oder Live-Aktivierung vorgenommen.

Nachfolgende Nodepruefungen gegen die neuen Pakete in der eigenen Installation
laufen lassen; akzeptierter Lieferquellbaum bleibt artifacts/migration-repair-source.
Python-/Schemaaenderungen dort pruefen und Nodequellenaenderungen vor neuen
Checks gezielt in die private Installation uebertragen. Bestehende gemeinsame
Junctions nicht als neue Patchinstallation ausgeben oder veraendern.

Exakte Dateimanifeste/privateIndex-Lieferung, GitHub-Zweig
codex/migration-parity-repair-20261022. KeineRohtraces/Audit-Umgebung/Secretsliefern.
