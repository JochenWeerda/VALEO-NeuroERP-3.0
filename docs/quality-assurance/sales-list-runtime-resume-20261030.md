# Verkaufslisten: Runtime-Fortsetzung 30.10.2026

Angebots- und Lieferlisten verwenden die native ScreenDefinition. Die bestehenden gemeinsamen Runtime-Wege bleiben fuer Lesen, vollstaendige gefilterte Tabellen, Suche, Statusauswahl und Navigation fuehrend. Die Lieferliste bietet nun denselben deklarierten lokalen Druckweg wie Angebote. Gedruckt und exportiert werden nur die geladenen gefilterten Zeilen mit den deklarierten Spalten; ein Wechsel der Screen-ID darf keine zuvor gespeicherten Zeilen ausgeben.

Der Arbeitsfokus ist eine Auswahl des Erklaerkontexts. Er aendert weder Datensaetze noch Filter oder Rechte. Die zentralen Kontextzeilen besitzen feste Schluessel; der gewaehlte Fokus zeigt nur die zugehoerigen Hinweise. Beim Wechsel der Maske gilt deren deklarierter Default.

Der Angebotsimport verwendet den bestehenden atomaren Backendcommand `/api/v1/sales/offers/actions/import-csv`. Der gemeinsame Dateifeldrenderer liest UTF-8-Inhalt; der Dialog zeigt eine Vorschau, der deklarierte Hilfetext nennt den CSV-Kopf. Vor dem Versand steht die Bestaetigung. Eine abgelehnte oder unterbrochene Anfrage haelt den Auftrag offen; derselbe Inhalt behaelt fuer einen erneuten Versuch denselben Wiederholungsschluessel. Berechtigungspruefung im Client ersetzt nicht die serverseitigen Human-/Mandanten-/Rollen- und Transaktionspruefungen.

Verifikation im koordinierten Lead-Lauf: 9/9 Tests in vier Dateien bestanden: `sales-list-runtime.test.tsx`, `list-role-focus.test.tsx` und die beiden bestehenden Sales-Listenseitentests. Die Seitentests verwenden echte Compiler, Runtime und Renderer sowie eine unveraenderte Projektion beider Python-Builder; nur Transport und Identitaet werden ersetzt. Dieser Nachweis ist keine Live-SSO-/Browser-/Drucker- oder Produktionsfreigabe. Gesamt-Reststatus und weitere gemeinsame Checks werden vom Lead ergaenzt.


## Kanonische Erfassungs-Fallbacks

Der CI-Synchronisationstest offenbarte neue Abweichungen in Kopfaktionen, Quellen, Tabellen und Registern der alten handkopierten Erfassungen. `scripts/generate_capture_screens.py` erzeugt jetzt alle 31 bestehenden TypeScript-Exporte aus derselben verfassten Python-Registry wie `generate_screen_registry_snapshot.py`. Kein Export oder Fachfeld wurde fuer einen Test ausgeblendet. Die 26 datierten Ausnahmeeintraege sind entfernt; der Frontendvergleich verlangt Gleichheit. Ein eigener Backend-Check weist veraltete generierte Fallbacks zurueck. Der Agentenvertrag bleibt wie bisher ausschliesslich serverseitig. Die regulierten Rollen-/Kommandowege der Registry ersetzen damit auch im Fallback die veralteten Aktionen ohne Rechtebindung.
