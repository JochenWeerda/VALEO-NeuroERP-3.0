---
title: Fahrplan bis zum Verkaufsprodukt
type: reference
audience: [management, produkt, agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-15
version: 1.0.0
description: Verbindlicher Gesamtfahrplan der VALEO NeuroERP Suite - Meilensteine M0 bis M8 mit messbarer Abnahme, Arbeitsteilung der Agenten und Koordinationsregeln.
---

# Fahrplan VALEO NeuroERP 3.0 bis zum Verkaufsprodukt

Dieser Fahrplan ist die eine Stelle, an der Reihenfolge, Abnahmekriterien und Arbeitsteilung stehen.
Das [Workboard](../agent-ops/active-workboard.md) führt die einzelnen Arbeitsschritte; jeder Eintrag dort
nennt die Meilenstein-ID aus diesem Dokument.

## Entscheidungen des Nutzers (15.11.2026)

- **Umfang 1.0:** alle Domänen.
- **Betrieb in drei Stufen:** (1) eigener Server, praxisnaher Testbetrieb, Vorgänge aus L3 werden gespiegelt,
  um zu sehen, ob alle Prozesse 1:1 abgedeckt sind → (2) On-Premises beim Kunden → (3) gehostetes SaaS.
- **Termin:** kriteriengetrieben, keine Kalenderzusagen.
- **Finanzen:** vollständige Fibu (führendes Hauptbuch); DATEV ist Schnittstelle.

## Iststand (main `2338578d0`, 15.11.2026)

| Bereich | Messwert | Quelle |
|---|---|---|
| Backend-Suite | 28.497 bestanden; PR-Checks und Sonar grün | `docs/agent-ops/handshakes/` (Codex, 15.11.) |
| CI auf main | rot: CI/CD Pipeline, Quality Gate `qg:push:main`, E2E Full UAT, Runtime API Sweep | `gh run list --branch main` |
| Masken | handgebaut 3, Altmuster 15, Aktionen nicht deklariert 293, nicht verfügbar 24, ohne CLI 6; 98 `*-legacy.tsx` | `config/mask_studio_ratchet.json` |
| BELEG-052 | Auftrag, Lieferschein, Gutschrift in main; Kontrakt, Rechnung (2a/2b), Einkauf (3a/3b) auf Branches; 19 Leser der Übergangssicht | `tests/test_sicht_auftraege_ratsche.py` |
| Altlast Code | `compat.py` 3.312 Zeilen, 13 Godfiles | `config/godfile_baseline.json` |
| Domänenreife | hoch: Verkauf, CRM, Lager, Agrar, Logistik, Kontrakte; mittel: Fibu, Compliance, POS, Portal; dünn: KI/MCP | `docs/gap/executive-summary-20261007.md` |
| Fibu-Lücken | Journal, Periodensteuerung, Kassen-/Tagesabschluss, Bankabgleich, Mahnwesen dreifach, DATEV-Automatikkonten | `docs/project-context/open-gaps-and-known-issues.md` |
| Betrieb | Compose, Helm, Monitoring vorhanden; kein Restore-Nachweis, kein Mandanten-Anlageweg, Vorgabepasswörter in Staging | `GO-LIVE-CHECKLIST.md` |
| Produkt | kein Lizenz-/Preismodell, keine AVV/TOM/AGB/SLA, kein Demo-Mandant, kein L3-Importwerkzeug | Bestandsaufnahme 15.11. |
| Koordination | rund 125 Workboard-Einträge nicht abgeschlossen, viele veraltet; Workboard 2,3 MB | Workboard |

In M0 zu klären: Stand ZUGFeRD, tatsächlicher Schalter der Agent-Schreibfreigabe, Mandanten-Anlageweg.

## Meilensteine

Die Reihenfolge bildet die Abhängigkeit ab. Ein Meilenstein gilt erst mit seiner Abnahme als erreicht.

### M0 Ordnung und grüne Basis

- main vollständig grün: die vier roten Workflows diagnostizieren und beheben.
- Workboard: veraltete Claims schließen, erledigte Einträge nach `docs/agent-ops/archive/` auslagern,
  Statuswörter festlegen (`offen`, `reserviert`, `in Arbeit`, `abgeschlossen`, `verworfen`).
- Gemergte Arbeitsbäume und Branches entfernen.
- **Abnahme:** `gh run list --branch main` ohne rote Läufe; Workboard unter 300 KB; jeder offene Eintrag trägt eine Meilenstein-ID.

### M1 BELEG-052: DocFlow einziger Belegspeicher

- Pull Requests in fester Reihenfolge: Kontrakt → Rechnung 2a → 2b → Einkauf 3a → 3b.
- Alte Gutschrifttabellen entfernen; Übergangssichten abbauen; Alttabellen per Migration entfernen.
- Fachreste: Bestellung versenden, Rechnungsprüfung, ZUGFeRD aus DocFlow, DocFlow-Akteur als lokaler Nutzer.
- **Abnahme:** Ratsche der Sicht-Leser bei 0; Ratsche „Schreiber in Altspeicher“ bei 0; keine alten Belegrouter mehr.

### M2 Alle Masken in Studio-Qualität

- Ratschen auf null: handgebaut, Altmuster (Annahme und Waage als Familie mit Varianten), Aktionen nicht verfügbar,
  nicht deklariert, ohne CLI. Legacy-Seiten entfernen oder ersetzen. `compat.py` auflösen.
- **Abnahme:** `python scripts/mask_studio_inventory.py --check` mit leerer Baseline; je Maske Abnahme nach
  `docs/architecture/studio-release-standard.md`.

### M3 Vollständige Fibu

- Integrität: Journal, Periodensteuerung für alle Schreiber, echter Kassen-/Tagesabschluss, Bankabgleich mit Nachweis.
- Ein Mahnweg statt drei; offene Posten; Zahlungsverkehr.
- Hauptbuch: Saldenvortrag, Jahresabschluss (Bilanz, GuV), UStVA mit ELSTER, Anlagenbuchhaltung.
- DATEV-Export als Schnittstelle (Automatikkonten geprüft, keine doppelte Steuer).
- GoBD-Verfahrensdokumentation.
- **Abnahme:** ein Musterjahr mit Monats- und Jahresabschluss läuft durch; Summen- und Saldenliste stimmt mit dem
  Journal überein. Externe Tore: Abnahme durch den Steuerberater (GOBD-04), wahlweise Softwaretestat.

### M4 Domänenabnahme für alle Domänen

- Je Domäne ein Abnahmeblatt: Prozessliste aus der L3-Referenz, Maskenabnahme, keine Demo- oder Festwerte,
  Rollen geprüft.
- Reihenfolge: zuerst alles, was im L3-Betrieb genutzt wird (Verkauf, Einkauf, Lager, Annahme/Waage, Kontrakte,
  Strecke, Produktion/Mühle, Logistik, CRM), dann POS/TSE, Portal, Personal, Compliance/EUDR, Fütterung,
  Ackerschlagkartei, KI/MCP.
- **Abnahme:** Reifematrix unter `docs/gap/` neu erhoben, alle Zeilen „hoch“; Lückenliste ohne P0 und P1.

### M5 Betriebsreife Stufe 1 (eigener Server)

- Produktions-Compose ohne Vorgabepasswörter und ohne Dev-Token; Geheimnisse rotiert.
- Sicherung mit nachgewiesenem Restore; Überwachung und Alarme im Betrieb; Update-Verfahren mit Migration.
- Mandanten-Anlageweg (Mandant, Keycloak, RLS, Erstdaten) als ein Kommando.
- Übernahme aus L3: Kunden, Lieferanten, Artikel, Preise, Kontrakte, Bestände, offene Posten, Saldenvortrag.
- Agent-Schreibfreigabe: Entwicklungsschalter schließen; Autonomie nur über die Politik nach ADR-086 je Mandant.
- **Abnahme:** Neuinstallation aus dem Repo auf leerem Server nach Handbuch; Restore-Probe protokolliert.

### M6 Spiegelbetrieb (Stufe 1)

- Start, sobald M1, die Integritätspunkte aus M3, M5 und der im L3-Betrieb genutzte Teil von M4 stehen.
  Die übrigen Domänen laufen parallel weiter.
- Jeder L3-Vorgang wird in VALEO nachvollzogen. Abgleich täglich (Belege, Beträge, Bestände) und monatlich
  (offene Posten, Journal, UStVA-Werte). Jede Abweichung wird ein Workboard-Eintrag.
- Hardware-Tore: Waage, MDE, Tankanlage, TSE (KASSE-04).
- **Abnahme:** ein voller Monat einschließlich Monatsabschluss ohne ungeklärte Abweichung; Ernteannahme als Lastprobe.
  Danach Ablösung von L3.

### M7 Verkaufsprodukt On-Premises (Stufe 2)

- Installationspaket, Update-Verfahren, Fernwartungskonzept, Installations- und Betriebshandbuch.
- Modul- und Lizenzsteuerung auf `app/core/module_registry.py`; Preismodell.
- Unterlagen: AVV, TOM, Verarbeitungsverzeichnis, Löschkonzept, AGB, SLA, Supportprozess.
- Demo-Mandant, Schulungsunterlagen, In-App-Hilfe; Lasttest, Barrierefreiheitsbericht, SBOM, Penetrationstest.
- **Abnahme:** Installation bei einem fremden Betrieb durch eine Person, die nicht entwickelt hat.

### M8 SaaS (Stufe 3)

- Betrieb auf Helm/ArgoCD, Mandanten-Selbstanlage, Abo-Abrechnung, Rufbereitschaft, ISO-27001-Lücken geschlossen.
- **Abnahme:** zweiter Mandant produktiv auf derselben Instanz; Isolation durch Fremdtoken-Probe nachgewiesen.

### Strang A: Orchestrator und Trust & Autonomy (ab M2)

Ereignisgesteuerte Ausführung bestehender Fachprozesse und risikobasierte Agentenautonomie auf der vorhandenen
Freigabe-Engine, DocFlow und den vorhandenen Kommandowegen. Keine zweite ERP-Kernlogik. Der Strang blockiert M6 nicht.

## Arbeitsteilung

| Agent | Bahn |
|---|---|
| Claude | M1 vollständig; M3 Integrität und Hauptbuch; Migrationen und RLS; M5 Übernahme aus L3 |
| Codex | M0 CI; M2 Masken und Aktionsparität; Sicherheitsbefunde; M5 Laufzeit und Bereitstellung |
| Cursor (phasenweise) | abgeschlossene Pakete ohne Folgeabhängigkeit: M4-Abnahmeblätter, Benutzerhandbuch, UIX-Feinschliff, M7-Unterlagen |

Fällt ein Kontingent weg, darf kein anderer Strang stehen bleiben. Deshalb gilt:

- Jeder Workboard-Eintrag nennt Meilenstein-ID, Besitzer, Dateibesitz und Abnahme. Der Claim-Commit kommt zuerst.
- Bei Kontingentende: Resume-Paket nach `docs/agent-ops/resume-packet-template.md` unter
  `docs/agent-ops/handshakes/`, Eintrag zurück auf `offen`.
- Ein Claim ohne Commit seit sieben Tagen gilt als frei.
- Ein Ressourcenfenster: nur ein großer Testlauf oder Image-Bau gleichzeitig, im Workboard angemeldet.
- Ungemergte Migrationen kommen nie auf `valeo_neuro_erp` oder `valeo_probe`.
- Fortschritt wird an Ratschen und Abnahmen gemessen, nicht an Meldungen.

## Messung

| Meilenstein | Prüfung |
|---|---|
| M0 | `gh run list --branch main --limit 30`; `python scripts/check_baseline_integrity.py --base origin/main` |
| M1, M2 | Ratschentests; `python scripts/mask_studio_inventory.py --check`; `python scripts/generate_mask_family_versions.py --check`; `python scripts/generate_document_screen_versions.py --check` |
| Migrationen | Schema frisch (`python scripts/pruefstand_db.py`), Daten gewachsen in zurückgerollter Transaktion |
| M3 | Abschlusslauf des Musterjahrs als automatischer Test, dazu Sichtprüfung der Auswertungen |
| M5, M6 | Installations- und Restore-Protokoll; Abgleichsbericht L3 gegen VALEO je Tag und Monat |

## Risiken

- Alle Domänen plus vollständige Fibu ist der längste Weg. Der Spiegelbetrieb startet deshalb vor Abschluss von M4.
- Externe Tore liegen nicht in Agentenhand: Steuerberater, TSE, Waagen-Hardware, ELSTER-Zulassung, Penetrationstest.
- Die lokale Maschine ist der Engpass; schwere Läufe laufen strikt nacheinander.
