---
title: "Spezifikation Fütterungsberatung — Index"
type: reference
audience: [produkt, fachlich, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Single Source of Truth für das Fütterungsberatungs-Programm — Dokumentlandkarte mit Füllstand.
---

# Spezifikation Fütterungsberatung — Index

Zielstruktur folgt dem Fachkonzept-Vorschlag des Auftraggebers (00–17). Die
Dokumente wachsen **inkrementell mit den Inkrementen** (Entscheidung siehe unten),
damit Spezifikation und Code nicht auseinanderlaufen.

| Nr. | Dokument | Status | Heutiger Ort |
|---|---|---|---|
| 00 | Vision | ✅ enthalten | `lastenheft-fuetterungsberatung.md` Kap. 3 |
| 01 | Glossar | 🔜 mit Inkrement 1 | — (Begriffe derzeit im Lastenheft/Traceability) |
| 02 | Lastenheft | ✅ | `lastenheft-fuetterungsberatung.md` |
| 03 | Fachkonzept | ✅ Kern | `ist-audit.md` + `target-architecture.md` |
| 04 | Domänenmodell | ✅ Kern | `target-architecture.md` §2 (Aggregat-Tabelle); Detail-UML je Inkrement |
| 05 | Datenmodell | 🔜 je Inkrement | Migrationsdateien + `ist-audit.md` §1.4 |
| 06 | API | ✅ Zielbild | `target-architecture.md` §3; OpenAPI ist generiert (Repo-Gate) |
| 07 | Maskenkatalog | ✅ Landkarte | `target-architecture.md` §7; Detail je Editor-Slice |
| 08 | Workflows | ✅ Kern | Lastenheft Kap. 5/11; Lifecycle in `app/agrar/rations/lifecycle/domain.py` |
| 09 | Berechnungsregeln | ✅ im Code+Tests | `app/agrar/rations/constants/` + Golden-Tests (Single Source: Code, nicht Doku-Kopie) |
| 10 | UI/UX | ✅ | `docs/design/frontend-design-skill-audit.md` + ADR-041 |
| 11 | Agenten | 🔜 Release C | Leitplanken: Lastenheft Kap. 6.20 (verbindlich) |
| 12 | Integrationen | ✅ Kern | `target-architecture.md` §3–4; Connector-Verträge Slice 010 |
| 13 | Tests | ✅ Strategie | `target-architecture.md` §8; Bestand `ist-audit.md` §3 |
| 14 | Migration | ✅ Konzept | `target-architecture.md` §6 |
| 15 | Rollout | ✅ Konzept | `implementation-plan.md` (Flag `feeding_advisory`, Pilot) |
| 16 | Traceability | ✅ | `requirements-traceability.md` |
| 17 | Roadmap | ✅ | `implementation-plan.md` (Inkremente 1–6, Slices 015–036) |
| — | Fodjan-Abgleich | ⏳ blockiert | `fodjan-help-traceability.md` sobald Quelle abrufbar (Lastenheft Kap. 17) |

## Entscheidung zum Umfang (Empfehlung, umgesetzt)

Der Vorschlag eines 300–500-Seiten-Referenzwerks vorab wurde bewusst **nicht als
Big-Bang-Dokumentation** umgesetzt, sondern als wachsende Struktur:

1. **Doku-Drift ist das Hauptrisiko** dieses Repos (eigene Gates: docs-code-sync,
   Drift-Check). Ein vorab vollständig ausgeschriebener Masken-/Test-/Datenkatalog
   über 6 Inkremente veraltet vor seiner Umsetzung und verletzt dann die eigenen
   Governance-Regeln.
2. **Berechnungsregeln haben bereits eine Single Source:** den getesteten Code
   (~30 Golden-Test-Dateien gegen GfE 2023/DLG 01/2025). Eine Prosa-Kopie im
   Regelwerk-Dokument würde eine zweite, driftende Wahrheit schaffen.
3. **Verbindlichkeit entsteht hier über Slices:** jedes Inkrement liefert seinen
   Spezifikationsteil (Masken, Tabellen, Tests) mit dem Claim — die Struktur oben
   füllt sich, IDs und Kapitel bleiben stabil.

Damit arbeitet Claude Code mit derselben Single Source of Truth, ohne dass die
Spezifikation dem Code je 6 Inkremente vorauslaufen und veralten muss. Wünscht der
Auftraggeber dennoch das vollständige Vorab-Referenzwerk, ist das eine explizite
Entscheidung gegen die Drift-Gates und braucht einen eigenen Pflege-Prozess.
