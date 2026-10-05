---
title: Wissensbasis und Kundenportal
type: how-to
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.2.0
---

# Wissensbasis und Kundenportal

Interne Wissensdatenbank und externes Kundenportal.

## Ziel

Sie arbeiten sicher in allen Masken des Bereichs **Wissensbasis und Kundenportal** — von der Navigation
bis zu Speichern, Freigabe und Folgebelegen.

## Voraussetzungen

- Gültige Anmeldung und Mandant (`X-Tenant-ID`).
- Modul für diesen Fachbereich ist installiert (siehe Administration → Module).
- Ihre Rolle hat Lese- bzw. Schreibberechtigung für die jeweilige Maske.

## Maskenregister

Vollständige Abdeckung: **20** App-Routen
(0 explizit in der Sidebar-Navigation).

| Maske | Route | Modul |
|-------|-------|-------|
| Portal | `/portal` | `@/pages/portal/index` |
| Anfragen | `/portal/anfragen` | `@/pages/portal/anfragen` |
| Bestellungen | `/portal/bestellungen` | `@/pages/portal/bestellungen` |
| Dokumente | `/portal/dokumente` | `@/pages/portal/dokumente` |
| Empfehlungen | `/portal/empfehlungen` | `@/pages/portal/empfehlungen` |
| Feldbuch | `/portal/feldbuch` | `@/pages/portal/feldbuch` |
| Lohndienste | `/portal/lohndienste` | `@/pages/portal/lohndienste` |
| Neu | `/portal/lohndienste/neu` | `@/pages/portal/lohndienste` |
| Naehrstoffbilanzen | `/portal/naehrstoffbilanzen` | `@/pages/portal/naehrstoffbilanzen` |
| Onboarding | `/portal/onboarding` | `@/pages/portal/onboarding` |
| Portal | `/portal/portal` | `@/pages/portal/index` |
| Preisspiegel | `/portal/preisspiegel` | `@/pages/portal/preisspiegel` |
| Profil | `/portal/profil` | `@/pages/portal/index` |
| Rationsoptimierung | `/portal/rationsoptimierung` | `@/pages/portal/rationsoptimierung` |
| Rechnungen | `/portal/rechnungen` | `@/pages/portal/rechnungen` |
| Shop | `/portal/shop` | `@/pages/portal/shop` |
| Vertraege | `/portal/vertraege` | `@/pages/portal/vertraege` |
| Whatsapp Simulator | `/portal/whatsapp-simulator` | `@/pages/portal/whatsapp-simulator` |
| Zertifikate | `/portal/zertifikate` | `@/pages/portal/zertifikate` |
| Wissensbasis | `/wissen/wissensbasis` | `@/pages/wissen/wissensbasis` |

## Masken im Detail

Für jede Route: Navigation, Bearbeitung, Ergebnis und typische Fehler.

### Portal

**Route:** `/portal` · **Modul:** `@/pages/portal/index`

**Ziel:** Portal in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Portal — Bedienoberfläche](img/portal.webp)


**Schritte:**

1. Sidebar oder Suche: **Portal** öffnen (`/portal`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Anfragen

**Route:** `/portal/anfragen` · **Modul:** `@/pages/portal/anfragen`

**Ziel:** Anfragen in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Anfragen — Bedienoberfläche](img/portal__anfragen.webp)


**Schritte:**

1. Sidebar oder Suche: **Anfragen** öffnen (`/portal/anfragen`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Bestellungen

**Route:** `/portal/bestellungen` · **Modul:** `@/pages/portal/bestellungen`

**Ziel:** Bestellungen in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Bestellungen — Bedienoberfläche](img/portal__bestellungen.webp)


**Schritte:**

1. Sidebar oder Suche: **Bestellungen** öffnen (`/portal/bestellungen`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Dokumente

**Route:** `/portal/dokumente` · **Modul:** `@/pages/portal/dokumente`

**Ziel:** Dokumente in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Dokumente — Bedienoberfläche](img/portal__dokumente.webp)


**Schritte:**

1. Sidebar oder Suche: **Dokumente** öffnen (`/portal/dokumente`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Empfehlungen

**Route:** `/portal/empfehlungen` · **Modul:** `@/pages/portal/empfehlungen`

**Ziel:** Empfehlungen in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Empfehlungen — Bedienoberfläche](img/portal__empfehlungen.webp)


**Schritte:**

1. Sidebar oder Suche: **Empfehlungen** öffnen (`/portal/empfehlungen`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Feldbuch / Ackerschlagkartei

**Route:** `/portal/feldbuch` · **Modul:** `@/pages/portal/feldbuch`
**Auswertungen:** `/portal/feldbuch-auswertungen`
**Agent-API:** siehe [`docs/specs/agrar/ackerschlagkartei-agent-crud-api.md`](../specs/agrar/ackerschlagkartei-agent-crud-api.md)

**Ziel:** Schläge und Maßnahmen im Kundenportal vollständig pflegen (Anlegen, Bearbeiten, Löschen), Sammeldüngung und Jahreswechsel ausführen, Schlaginfo drucken/exportieren, DüV-Auswertungen prüfen.

![Feldbuch — Übersicht](img/portal__feldbuch.png)

![Schlag angelegt](img/portal__feldbuch__schlag-angelegt.png)

![Schlag bearbeitet](img/portal__feldbuch__schlag-bearbeitet.png)

![Maßnahme angelegt](img/portal__feldbuch__massnahme-angelegt.png)

![Maßnahme bearbeitet](img/portal__feldbuch__massnahme-bearbeitet.png)

![Schlaginformation](img/portal__feldbuch__schlaginfo.png)

![Sammeldüngung](img/portal__feldbuch__sammelduengung.png)

![Export](img/portal__feldbuch__export.png)

![CSV-Import](img/portal__feldbuch__import.png)

![CSV-Import Ergebnis](img/portal__feldbuch__import-ergebnis.png)

![Jahreswechsel](img/portal__feldbuch__jahreswechsel.png)

![PSM ohne Sachkunde](img/portal__feldbuch__psm-ohne-sachkunde.png)

![PSM Prüfen-Badge](img/portal__feldbuch__psm-pruefen-badge.png)

![PSM mit Sachkunde](img/portal__feldbuch__psm-mit-sachkunde.png)

![DüV-Auswertungen](img/portal__feldbuch-auswertungen.png)

**Praxis-Nachweis:** Playwright-Simulation `packages/frontend-web/tests/e2e/portal-feldbuch-crud-praxis.spec.ts` schreibt Screenshots hierher und protokolliert nach `artifacts/portal-feldbuch-crud-praxis.json` (CRUD, Sammel, Export, **CSV-Import**, **Jahreswechsel**, **PSM-Sachkunde-Pflichtpfad**, Auswertungen).

**Schritte — Schläge (CRUD in der Zeile):**

1. Sidebar: **Feldbuch** öffnen (`/portal/feldbuch`).
2. Wirtschaftsjahr (WJ) oben wählen; Arbeitskontext prüfen.
3. Tab **Schläge** → **Schlag anlegen**: Name, Fläche (ha), Kultur, Gemeinde, FLIK → speichern.
4. In der Zeile: **Bearbeiten** (Stift), **Info** (Schlaginfo/DFL), **Löschen** (Papierkorb; Portal-Maßnahmen werden mitgelöscht; VALEO-Dienste blockieren mit Hinweis).
5. Optional: **Sammeldüngung**, **Jahreswechsel**, **Import/Export**.

**Schritte — Maßnahmen (CRUD in der Zeile):**

1. Tab **Maßnahmen** → **Maßnahme erfassen**.
2. Typ wählen (Düngung, PSM, Aussaat, Beregnung, AUM, Ernte, …); bei PSM Sachkunde/Begründung pflegen.
3. PSM ohne Sachkunde/Begründung speichern → Badge **Prüfen**; nach Ergänzung der Pflichtangaben verschwindet der Hinweis.
4. Zeile: **Bearbeiten** / **Löschen** — bei VALEO-Dienst (`erp_*`) ausgegraut.
5. **Import**: CSV mit Schlag/Datum/Maßnahme/Mittel…; **Jahreswechsel**: Schläge ins Folge-WJ übernehmen.
6. DüV-Auswertungen unter `/portal/feldbuch-auswertungen` (Bedarf, Bilanz, Stoffstrom, PSM, Ernte).

**Ergebnis:** Schläge/Maßnahmen persistiert, Liste aktualisiert, Auswertungen aktuell.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul/Backend/Migration | `alembic upgrade head`, API erreichbar prüfen |
| Speichern fehlgeschlagen | Pflichtfeld (z. B. Sorte bei Aussaat, AUM-Code) | Meldung lesen, Felder ergänzen |
| Löschen/Bearbeiten ausgegraut | VALEO-Dienstleistungs-Maßnahme | Nur Portal-Einträge ändern |
| Schlag löschen 409 | ERP-Maßnahmen am Schlag | Nachweis belassen, Schlag nicht löschen |

### Lohndienste

**Route:** `/portal/lohndienste` · **Modul:** `@/pages/portal/lohndienste`

**Ziel:** Lohndienste in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Lohndienste — Bedienoberfläche](img/portal__lohndienste.webp)


**Schritte:**

1. Sidebar oder Suche: **Lohndienste** öffnen (`/portal/lohndienste`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Neu

**Route:** `/portal/lohndienste/neu` · **Modul:** `@/pages/portal/lohndienste`

**Ziel:** Neu in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Neu — Bedienoberfläche](img/portal__lohndienste__neu.webp)


**Schritte:**

1. Sidebar oder Suche: **Neu** öffnen (`/portal/lohndienste/neu`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Naehrstoffbilanzen

**Route:** `/portal/naehrstoffbilanzen` · **Modul:** `@/pages/portal/naehrstoffbilanzen`

**Ziel:** Naehrstoffbilanzen in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Naehrstoffbilanzen — Bedienoberfläche](img/portal__naehrstoffbilanzen.webp)


**Schritte:**

1. Sidebar oder Suche: **Naehrstoffbilanzen** öffnen (`/portal/naehrstoffbilanzen`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Onboarding

**Route:** `/portal/onboarding` · **Modul:** `@/pages/portal/onboarding`

**Ziel:** Onboarding in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Onboarding — Bedienoberfläche](img/portal__onboarding.webp)


**Schritte:**

1. Sidebar oder Suche: **Onboarding** öffnen (`/portal/onboarding`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Portal

**Route:** `/portal/portal` · **Modul:** `@/pages/portal/index`

**Ziel:** Portal in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Portal — Bedienoberfläche](img/portal__portal.webp)


**Schritte:**

1. Sidebar oder Suche: **Portal** öffnen (`/portal/portal`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Preisspiegel

**Route:** `/portal/preisspiegel` · **Modul:** `@/pages/portal/preisspiegel`

**Ziel:** Preisspiegel in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Preisspiegel — Bedienoberfläche](img/portal__preisspiegel.webp)


**Schritte:**

1. Sidebar oder Suche: **Preisspiegel** öffnen (`/portal/preisspiegel`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Profil

**Route:** `/portal/profil` · **Modul:** `@/pages/portal/index`

**Ziel:** Profil in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Profil — Bedienoberfläche](img/portal__profil.webp)


**Schritte:**

1. Sidebar oder Suche: **Profil** öffnen (`/portal/profil`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Rationsoptimierung

**Route:** `/portal/rationsoptimierung` · **Modul:** `@/pages/portal/rationsoptimierung`

**Ziel:** Rationsoptimierung in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Rationsoptimierung — Bedienoberfläche](img/portal__rationsoptimierung.webp)


**Schritte:**

1. Sidebar oder Suche: **Rationsoptimierung** öffnen (`/portal/rationsoptimierung`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Rechnungen

**Route:** `/portal/rechnungen` · **Modul:** `@/pages/portal/rechnungen`

**Ziel:** Rechnungen in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Rechnungen — Bedienoberfläche](img/portal__rechnungen.webp)


**Schritte:**

1. Sidebar oder Suche: **Rechnungen** öffnen (`/portal/rechnungen`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Shop

**Route:** `/portal/shop` · **Modul:** `@/pages/portal/shop`

**Ziel:** Shop in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Shop — Bedienoberfläche](img/portal__shop.webp)


**Schritte:**

1. Sidebar oder Suche: **Shop** öffnen (`/portal/shop`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Vertraege

**Route:** `/portal/vertraege` · **Modul:** `@/pages/portal/vertraege`

**Ziel:** Vertraege in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Vertraege — Bedienoberfläche](img/portal__vertraege.webp)


**Schritte:**

1. Sidebar oder Suche: **Vertraege** öffnen (`/portal/vertraege`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Whatsapp Simulator

**Route:** `/portal/whatsapp-simulator` · **Modul:** `@/pages/portal/whatsapp-simulator`

**Ziel:** Whatsapp Simulator in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Whatsapp Simulator — Bedienoberfläche](img/portal__whatsapp-simulator.webp)


**Schritte:**

1. Sidebar oder Suche: **Whatsapp Simulator** öffnen (`/portal/whatsapp-simulator`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Zertifikate

**Route:** `/portal/zertifikate` · **Modul:** `@/pages/portal/zertifikate`

**Ziel:** Zertifikate in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Zertifikate — Bedienoberfläche](img/portal__zertifikate.webp)


**Schritte:**

1. Sidebar oder Suche: **Zertifikate** öffnen (`/portal/zertifikate`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

### Wissensbasis

**Route:** `/wissen/wissensbasis` · **Modul:** `@/pages/wissen/wissensbasis`

**Ziel:** Wissensbasis in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Wissensbasis — Bedienoberfläche](img/wissen__wissensbasis.webp)


**Schritte:**

1. Sidebar oder Suche: **Wissensbasis** öffnen (`/wissen/wissensbasis`).
2. Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.
3. Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.
4. Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.

**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.

**Häufige Fehler:**

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |
| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |
| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/*.tsx` — Sidebar-Navigation.
- `packages/frontend-web/src/app/routing/route-inventory.gen.json` — Routen-Inventar.
- `docs/MASKEN.md` — Layout-Standard (Gewohnheits-Prinzip).

Reverse-Pflege: Bei neuen Routen Generator `scripts/generate_benutzerhandbuch_full.py`
ausführen; `mkdocs.yml`, `index.md` und `generate_inapp_help_map.py` mitziehen.
