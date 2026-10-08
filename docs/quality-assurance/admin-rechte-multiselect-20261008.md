# Verwaltungsrechte und Mehrfachauswahl (Slice ADMIN-RECHTE-MULTISELECT-20261008)

Stand: 2026-10-08 · Folgeslice zu [Postfächer mit Microsoft 365](postfach-microsoft365-20261008.md)

## 1. Rechteausweitung unter `/api/v1/admin` geschlossen

**Befund:** `admin_core` (Prefix `/api/v1/admin`) hatte keine einzige Rollenprüfung. Jeder angemeldete Nutzer konnte Benutzer anlegen und löschen, sich selbst und anderen Rollen geben, Rollen definieren, API-Schlüssel anlegen, rotieren und widerrufen sowie Prozessvarianten und Policy-Overrides überschreiben. Gefunden wurde das beim Laden der Rollenliste für die Postfach-Maske.

**Behebung:** Die Rollen werden an den Routen geprüft, bevor irgendetwas die Datenbank erreicht.

| Wege | Rolle |
|---|---|
| Benutzer, Rollen und API-Schlüssel anlegen, ändern, löschen, rotieren, widerrufen; `PUT process-variants`, `PUT policy-overrides` | nur `admin` |
| Benutzer, Rollen, Audit-Log und API-Schlüssel lesen; Erntefenster aus Vorlage anlegen | `admin` oder `manager` |
| Agent-Manifest, Prozessvarianten und Policy-Overrides lesen, Erntefenster-Vorlagen und -Kampagnen, Workflow-Sandbox-Vorschau | unverändert: angemeldet; die Vorschau schreibt nichts |

**Vertrag** `tests/test_admin_rechte.py`:
- Jeder Schreibweg antwortet für Sachbearbeiter und Manager mit 403.
- Jeder geschützte Leseweg antwortet für Sachbearbeiter mit 403 und für Manager nicht.
- Ein Strukturtest stellt sicher, dass kein Schreibweg unter `/admin` ohne Abhängigkeit hinzukommt.

## 2. Mehrfachauswahl im Mask Builder

**Befund:** `multiselect` war im Schema erlaubt, wurde aber als Textfeld gezeichnet. In der Postfach-Maske waren Verwendung und Rollen deshalb kommagetrennter Text.

**Behebung:**
- `FieldRenderer` zeichnet ein `multiselect` mit Optionen als `fieldset`/`legend` mit einer Checkbox je Option, im 44-px-Touchraster.
- Der Wert ist eine Liste in der Reihenfolge der Optionen. Ein kommagetrennter Altwert wird gelesen.
- Ein Pflichtfeld blockiert bei leerer Liste; das übernimmt die vorhandene Regel im Form-State.
- Ohne Optionen bleibt das Feld ein Textfeld wie bisher; keine bestehende Maske ändert ihr Verhalten.

**Postfach-Maske:** Verwendung ist eine Mehrfachauswahl mit den Verwendungen des Dienstes (`VERWENDUNGEN`). Rollen ist eine Mehrfachauswahl mit den Rollen des Hauses aus `/api/v1/admin/rollen`. Eine bereits vergebene, unbekannte Rolle bleibt wählbar. Benutzerfreigabe und persönliches Postfach bleiben Text, weil die Benutzerkennung des Tokens nicht zwingend die lokale Benutzer-ID ist.

**Verträge:**
- Vitest `field-multiselect.test.tsx` (5 Tests): Gruppe, Liste, Reihenfolge, Altwert, nur lesend, Pflicht.
- Vitest `postfaecher.test.tsx`: Rollen und Verwendung als Checkboxen.
- `tests/test_postfaecher.py`: Optionen gleich dem Dienst; TS-Spiegel identisch.

## Nachweis

Backend: 55 grün (Postfächer, Admin-Rechte, Screen-Governance). Frontend: siehe Commit. Die Gates laufen im HEAD-Worktree.
