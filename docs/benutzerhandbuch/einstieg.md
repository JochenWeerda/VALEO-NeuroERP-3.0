---
title: Einstieg – Anmeldung, Mandant, Navigation
type: tutorial
audience: [endnutzer]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-29
version: 3.1.0
---

# Einstieg – Anmeldung, Mandant, Navigation

Dieser Einstieg führt durch die ersten Schritte: Anmelden, Mandant wählen und in
der Oberfläche navigieren.

## Anmelden

1. Rufen Sie die Anwendung im Browser auf.
2. Sie werden zur **Anmeldung** (OIDC) weitergeleitet.
3. Geben Sie Benutzername und Passwort ein (bzw. nutzen Sie Single Sign-on).
4. Nach erfolgreicher Anmeldung landen Sie auf dem **Dashboard**.

**Ergebnis:** Sie sind angemeldet und sehen die für Ihre Rolle freigeschalteten
Bereiche.

![Dashboard nach der Anmeldung mit Kennzahlen und Flow-Spine-Prozessen](img/einstieg-dashboard.webp)

## Mandant wählen

Wenn Sie Zugriff auf mehrere Mandanten haben:

1. Öffnen Sie oben rechts die **Mandantenauswahl**.
2. Wählen Sie den gewünschten Mandanten.
3. Die Oberfläche lädt die Daten und Module dieses Mandanten neu.

!!! warning "Mandantentrennung"
    Sie sehen ausschließlich Daten des aktiven Mandanten. Ein Wechsel ändert den
    gesamten Datenkontext.

## Navigation

- **Seitenleiste:** Fachbereiche (Annahme, Verkauf, Einkauf, Lager, FiBu, CRM …).
- **Kopfzeile:** Mandant, Benutzer, Benachrichtigungen, Hilfe.
- **Globale Suche:** schnell zu Belegen, Kunden oder Masken springen.
- **Omnibox / Kommandoleiste (Strg+K):** natuerlichsprachig „sagen statt suchen"
  (z. B. `offene posten folkerts`) und in einem Schritt zur gefilterten Liste
  springen. Ausfuehrlich in [Moderne Bedienung](moderne-bedienung.md).
- **Rollen-Workspaces:** aufgabenbezogene Startseiten (Einkauf/Verkauf/Lager/
  FIBU/Leitung) mit Kacheln in die wichtigsten Arbeitsvorraete.

## Tastatur & Shortcuts

Häufige Aktionen sind über Funktionstasten erreichbar (z. B. Speichern, Neu,
Folgebeleg). Die belegspezifischen Shortcuts stehen jeweils in der Fußzeile der
Maske.

## Gemeinsame Masken-Funktionen (ab Version 3.1)

Diese Funktionen stehen in allen modernen Detailmasken (Universal Mask) zur Verfügung:

### Sortieren und Filtern in Tabellen

In Tab-Tabellen (z. B. Aufträge, Aktivitäten, Positionen):

- **Sortieren:** Klick auf einen Spalten-Header sortiert aufsteigend, zweiter Klick
  absteigend. Ein kleiner Pfeil zeigt die aktive Richtung an.
- **Filter-Chips:** Oberhalb der Tabelle erscheinen vordefinierte Filter (z. B. nach
  Status oder Typ). Aktive Filter sind farbig hervorgehoben; × entfernt den Filter.
- **Freitextsuche:** Das Suchfeld oben in der Tabelle filtert alle sichtbaren Spalten.
- **Blättern:** Die Seitennavigation am Tabellenrand lädt die Daten serverseitig —
  auch bei sehr vielen Datensätzen bleibt die Anzeige flüssig.

### Bearbeiten mit Sticky Submit Bar

Beim Bearbeiten von Stammdaten-Feldern erscheint am unteren Bildschirmrand eine
**klebrige Aktionsleiste**:

| Element | Bedeutung |
|---------|-----------|
| „Ungespeicherte Änderungen" | Es gibt nicht gespeicherte Felder |
| **Zurücksetzen** | Alle Änderungen verwerfen (wird aktiv sobald etwas geändert wurde) |
| **Speichern** | Änderungen sichern (deaktiviert bei leeren Pflichtfeldern oder laufendem Speichern) |
| „Speichern…" | Speichervorgang läuft — Button deaktiviert, Doppelklick-Schutz aktiv |

Pflichtfelder werden beim Verlassen mit einem roten Hinweistext markiert.

### Workflow-Panel

In Masken mit Prozessstatus (z. B. Aufträge, Kunden-Cockpit) erscheint ein
**Workflow-Panel** unterhalb der Aktionsleiste:

- **Grün:** Objekt ist im Normalzustand, alle Aktionen erlaubt.
- **Gelb:** Hinweis oder weiche Sperre; Aktionen möglich, aber Klärung empfohlen.
- **Rot:** Harte Sperre; Aktionen sind blockiert bis der genannte Klärungsschritt
  durchgeführt wurde. Details aufklappen für Sperrgrund und Nächste Schritte.

### Allgemeine Fehler-Tabelle

| Symptom | Ursache | Maßnahme |
|---------|---------|----------|
| Speichern-Button grau | Pflichtfeld leer oder Speichervorgang läuft | Fehlende Felder ausfüllen oder kurz warten |
| Tabelle lädt nicht | Fehler beim API-Aufruf oder kein Netz | Seite neu laden; Administrator informieren |
| Filter zeigt keine Ergebnisse | Kombination zu restriktiv | Einen oder mehrere Filter entfernen |
| Workflow-Panel rot | Aktive Sperre am Objekt | Sperrgrund lesen, Klärungsschritte ausführen |
| Aktion ausgegraut | Berechtigung fehlt oder falscher Status | Vorbeleg freigeben oder Berechtigung klären |

## Maskenregister

Vollständige Abdeckung: **17** App-Routen
(0 explizit in der Sidebar-Navigation).

| Maske | Route | Modul |
|-------|-------|-------|
| Alerts | `/alerts` | `@/pages/workflow/workflow-monitoring` |
| Callback | `/auth/Callback` | `@/pages/auth/Callback` |
| Login | `/auth/Login` | `@/pages/auth/Login` |
| Callback | `/auth/callback` | `@/pages/auth/Callback` |
| Login | `/auth/login` | `@/pages/auth/Login` |
| Benachrichtigungen | `/benachrichtigungen` | `@/pages/benachrichtigungen/liste` |
| Liste | `/benachrichtigungen/liste` | `@/pages/benachrichtigungen/liste` |
| Einstellungen | `/einstellungen` | `@/pages/einstellungen/system` |
| System | `/einstellungen/system` | `@/pages/einstellungen/system` |
| Notfound | `/errors/NotFound` | `@/pages/errors/NotFound` |
| Hilfe | `/hilfe` | `@/pages/hilfe` |
| Login | `/login` | `@/pages/auth/Login` |
| Verify | `/public/verify` | `@/pages/public/verify` |
| Firma | `/setup/firma` | `@/pages/setup/firma` |
| Start Dashboard | `/start-dashboard` | `@/pages/start-dashboard` |
| :Number | `/verify/:domain/:number` | `@/pages/public/verify` |
| :Hash | `/verify/:domain/:number/:hash` | `@/pages/public/verify` |

## Masken im Detail

Für jede Route: Navigation, Bearbeitung, Ergebnis und typische Fehler.

### Alerts

**Route:** `/alerts` · **Modul:** `@/pages/workflow/workflow-monitoring`

**Ziel:** Alerts in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Alerts — Bedienoberfläche](img/alerts.webp)


**Schritte:**

1. Sidebar oder Suche: **Alerts** öffnen (`/alerts`).
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

### Callback

**Route:** `/auth/Callback` · **Modul:** `@/pages/auth/Callback`

**Ziel:** Callback in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

**Schritte:**

1. Sidebar oder Suche: **Callback** öffnen (`/auth/Callback`).
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

### Login

**Route:** `/auth/Login` · **Modul:** `@/pages/auth/Login`

**Ziel:** Login in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

**Schritte:**

1. Sidebar oder Suche: **Login** öffnen (`/auth/Login`).
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

### Callback

**Route:** `/auth/callback` · **Modul:** `@/pages/auth/Callback`

**Ziel:** Callback in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

**Schritte:**

1. Sidebar oder Suche: **Callback** öffnen (`/auth/callback`).
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

### Login

**Route:** `/auth/login` · **Modul:** `@/pages/auth/Login`

**Ziel:** Login in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

**Schritte:**

1. Sidebar oder Suche: **Login** öffnen (`/auth/login`).
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

### Benachrichtigungen

**Route:** `/benachrichtigungen` · **Modul:** `@/pages/benachrichtigungen/liste`

**Ziel:** Benachrichtigungen in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Benachrichtigungen — Bedienoberfläche](img/benachrichtigungen.webp)


**Schritte:**

1. Sidebar oder Suche: **Benachrichtigungen** öffnen (`/benachrichtigungen`).
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

### Liste

**Route:** `/benachrichtigungen/liste` · **Modul:** `@/pages/benachrichtigungen/liste`

**Ziel:** Liste in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Liste — Bedienoberfläche](img/benachrichtigungen__liste.webp)


**Schritte:**

1. Sidebar oder Suche: **Liste** öffnen (`/benachrichtigungen/liste`).
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

### Einstellungen

**Route:** `/einstellungen` · **Modul:** `@/pages/einstellungen/system`

**Ziel:** Einstellungen in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Einstellungen — Bedienoberfläche](img/einstellungen.webp)


**Schritte:**

1. Sidebar oder Suche: **Einstellungen** öffnen (`/einstellungen`).
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

### System

**Route:** `/einstellungen/system` · **Modul:** `@/pages/einstellungen/system`

**Ziel:** System in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![System — Bedienoberfläche](img/einstellungen__system.webp)


**Schritte:**

1. Sidebar oder Suche: **System** öffnen (`/einstellungen/system`).
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

### Notfound

**Route:** `/errors/NotFound` · **Modul:** `@/pages/errors/NotFound`

**Ziel:** Notfound in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Notfound — Bedienoberfläche](img/errors__notfound.webp)


**Schritte:**

1. Sidebar oder Suche: **Notfound** öffnen (`/errors/NotFound`).
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

### Hilfe

**Route:** `/hilfe` · **Modul:** `@/pages/hilfe`

**Ziel:** Hilfe in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Hilfe — Bedienoberfläche](img/hilfe.webp)


**Schritte:**

1. Sidebar oder Suche: **Hilfe** öffnen (`/hilfe`).
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

### Login

**Route:** `/login` · **Modul:** `@/pages/auth/Login`

**Ziel:** Login in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Login — Bedienoberfläche](img/login.webp)


**Schritte:**

1. Sidebar oder Suche: **Login** öffnen (`/login`).
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

### Verify

**Route:** `/public/verify` · **Modul:** `@/pages/public/verify`

**Ziel:** Verify in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Verify — Bedienoberfläche](img/public__verify.webp)


**Schritte:**

1. Sidebar oder Suche: **Verify** öffnen (`/public/verify`).
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

### Firma

**Route:** `/setup/firma` · **Modul:** `@/pages/setup/firma`

**Ziel:** Firma in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Firma — Bedienoberfläche](img/setup__firma.webp)


**Schritte:**

1. Sidebar oder Suche: **Firma** öffnen (`/setup/firma`).
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

### Start Dashboard

**Route:** `/start-dashboard` · **Modul:** `@/pages/start-dashboard`

**Ziel:** Start Dashboard in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![Start Dashboard — Bedienoberfläche](img/start-dashboard.webp)


**Schritte:**

1. Sidebar oder Suche: **Start Dashboard** öffnen (`/start-dashboard`).
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

### :Number

**Route:** `/verify/:domain/:number` · **Modul:** `@/pages/public/verify`

**Ziel:** :Number in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![:Number — Bedienoberfläche](img/verify__demo-1__demo-1.webp)


**Schritte:**

1. Sidebar oder Suche: **:Number** öffnen (`/verify/:domain/:number`).
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

### :Hash

**Route:** `/verify/:domain/:number/:hash` · **Modul:** `@/pages/public/verify`

**Ziel:** :Hash in VALEO NeuroERP öffnen, Daten prüfen oder erfassen und das Ergebnis in Liste bzw. Folgebeleg kontrollieren.

![:Hash — Bedienoberfläche](img/verify__demo-1__demo-1__demo-1.webp)


**Schritte:**

1. Sidebar oder Suche: **:Hash** öffnen (`/verify/:domain/:number/:hash`).
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
