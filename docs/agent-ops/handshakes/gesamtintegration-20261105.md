---
title: Gemeinsamer Integrationszweig der November-Slices
type: reference
audience: [agent, entwickler, qa]
owner: Codex Lead
status: lokal abgenommen
last_reviewed: 2026-11-05
version: 1.0.0
---

# Integration vor Uebernahme nach main

Im eigenen Arbeitsbaum artifacts/psm-zulassungen-20261104 liegt jetzt codex/gesamtintegration-20261105. Grundlage PSM 2a43fd5dc mit Stilllegungen 106/108; Omnibox 29c5e8ea0, Preis 059c7e744 und VVVO d991345d7 zusammengefuehrt. Alle sechs Einzel-PRs waren vor Beginn vollstaendig gruen. Die Stilllegungsmigrationen samt Tests/QA stimmen mit ihren Einzelzweigen ueberein. Hauptbaum und main unangetastet.

Workboard-Konflikte erhalten beide fachlich getrennten Nachweise. Alle zwoelf Projektionen regeneriert. Dabei Generatorfehler gefunden: Listenrouten hingen von Lazy-Initialisierung ab. Jetzt unveraenderliche urspruenglich kuratierte ID-Menge an der kanonischen Map, keine doppelte Registry. Wiederholte Erzeugung stabil; 447 Routen erhalten, 65 weiterhin offen.

46 gemeinsame Vertrags-/Feldtests bestanden; zwei Tests zum neuen Generator-/Omnibox-Vertrag bestanden, Gegenprobe alter Generator gezielt rot. Neun Verbesserungsscanner gruen. Abschliessender unabhaengiger Doc-Generator-Check gruen (Exit 0). Neue Gesamt-CI wird im [QA-Bericht](../../quality-assurance/gesamtintegration-20261105.md) nachgetragen. Keine neue DB, kein Container, keine Live-Migration oder Rechtevergabe.

Die authentifizierte PSM-Gesamtansicht, fehlende Registererfassung und vier RLS-Domain-Abnahmen bleiben eigene Folgeschritte. Einzelne gruene PRs beweisen nicht die gemeinsame Gesamt-CI. main verlangt weiterhin regulaere Review; keinen Schutz umgehen. Nach gemeinsamer Abnahme zuerst Integrations-PR, danach main nach develop. Einzel-PRs erst nach tatsaechlicher Uebernahme als enthalten schliessen.
