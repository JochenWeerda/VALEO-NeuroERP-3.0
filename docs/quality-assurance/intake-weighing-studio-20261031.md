---
title: Annahme und Waage im Studio-Runtime-Vertrag
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-31
version: 1.0.0
description: Native Annahme-/Waagenoberflächen mit Feld-, Aktions-, Mandanten- und Transportnachweisen.
---

# Annahme und Waage

Die drei Annahmemasken und fünf Waagenverträge werden durch
`screen_definitions_intake_weighing.py` beschrieben. Bestehende Builder delegieren
nur ihre acht betroffenen IDs. Die fünf bisherigen Seiteneinstiege und die echte
Waagenneuanlage verwenden `IntakeWeighingPage` mit
`UniversalNativeCockpitPage`, `useUniversalMaskRuntime`, `RenderPlan` und
`UniversalMaskRenderer`. Der feste SpecializedComponentHost bindet ausschließlich
die drei intake- und fünf weighing-IDs. Keine alte Page wird eingebettet.

Registrierung, Qualitätsprüfung und Neuanlage sind geführte Formulare mit
Wizard-Semantik. Queue, Waagen und Wiegescheine sind Arbeitsräume für mehrere
Objekte. Es gibt keine erfundene Entity-Datenquelle, Identität oder Listenanlage.
Die Route `/waage/neu` bindet in der Aliasquelle die eigene Neuanlageseite.

## Bedienung und Schutz

- Registrierung erhält Wizard, Kennzeichen-/Lieferscheinübernahme, echte
  Artikel-ID, Bildanhänge, Priorität, Schrittvalidierung und Übergabe in die Queue.
- Queue erhält Suche, QR-Einstieg, Artikelkorrektur, Qualitätsprüfung, Klärung und
  Ernteannahmeübergabe einschließlich vorhandener Referenzparameter.
- Qualitätsprüfung erhält Messungen, Bewertung, Statusübergabe, Referenzanker und
  Abrechnungsnavigation. Numerische Nullwerte werden nicht in `null` umgeschrieben.
- Wiegescheine verwenden weiter `/api/v1/weighing-tickets`, die bestehenden
  Anlage-/Update-/Allokationshooks und Kontrakte. Legacy-Wiegungen werden nicht
  als zweite Quelle aktiviert.
- Waagen lesen die echten snake_case-Antworten und projizieren Kapazität/Eichdaten
  ausdrücklich. Eine fehlende Eichung wird nicht als Datum erfunden.
- Die Eichdatenpflege verwendet ausschließlich die ausgewählte Waagen-ID und den
  kanonischen GET/PATCH-Kalibrierungsvertrag. Datumsreihenfolge, API-Fehler,
  schreibgeschützte Felder und nicht erlaubte Aktionen sind berücksichtigt.
- ASCII-Import verlangt eine ausdrücklich ausgewählte eigene Waage und eine
  UTF-8-Datei bis 1 MB. Ohne ausdrückliche Fehlertoleranz ist der Import strikt.
  Fehler lassen die Datei und Auswahl für den Retry erhalten. Erfolgsanzeigen
  unterscheiden Import, Fehler und Wiederholungsbeleg. Fehlerqueue, erneute Prüfung
  und bestätigtes Verwerfen verwenden die vorhandenen mandantengebundenen APIs.

Fachaktionen werden aus dem kompilierten Plan geprüft, auch bei direktem Aufruf
oder Tastaturbedienung. Verdeckte notwendige Feldbereiche verhindern das Mounten
der Datenoberfläche; nicht unterstützte dynamische Aktionsbedingungen werden
nicht als erlaubt angenommen. Schreibschutz gilt auch für Upload und Entfernen
von Anhängen. Kontextaktionen behalten ihre Berechtigungsprüfung im Plan, werden
mit dem auf diese festen Oberflächen begrenzten `surfaceOnly` aber nicht zusätzlich
als kontextlose Headerknöpfe gezeichnet. Dieses Merkmal ist Teil des Plancaches.

Neue Datenabfragen verwenden den eindeutigen Mandanten des angemeldeten Tokens
und den Akteur im Cacheschlüssel, ohne Standardmandanten. Ein Identitätswechsel
mountet die Oberfläche neu und verwirft vorherige Formularzustände. Die Signatur-
und Objektprüfung bleibt serverseitig; diese Clientprojektion ersetzt sie nicht.
Studio-Kopien verwenden die serverseitig validierte `baseScreenId` und den festen
kanonischen Specialized-Vertrag. Eine falsche Basis wird abgewiesen.

## Prüfung

Am 31.10.2026 bestanden 54 Frontendfälle in zwölf Dateien zusammen: die bisherigen
Interaktionstests für Registrierung, Qualität, Queue und Wiegescheine sowie neue
Verträge, Wizard-, Kalibrierungs-, Import-/Fehlerqueue- und Neuanlagefälle.
Die vorhandenen Seitentests behalten ihre Scan-, Artikel-ID-, Handover-, Such-
und Aktionsassertionen und durchlaufen jetzt den echten Studio-Compiler, die
Runtime und den Renderer mit ausdrücklich ausgewiesenen Testidentitäten und
Fachleseattrappen.

Danach bestanden 17 Fälle im gezielten Nachlauf für Registrierung und den
erweiterten Vertrag. Dieser ergänzt drei neue Upload-/Schreibschutzfälle und
einen Plancachefall. Zusammen sind das **58 unterschiedliche Frontendfälle**;
die elf wiederholten Fälle werden nicht erneut gezählt. Fünf Backend-
Definitionsverträge bestanden nach der Floorplan-Korrektur ebenfalls.

Betroffene Frontendtests liegen unter `src/__tests__/components/workflow/`:
`intake-weighing-contract`, `intake-wizard`, `intake-registration-guards`,
`weighing-calibration`, `weighing-import` und `waage-scale-create-plan`.
Zusätzlich wurden die sieben bestehenden Annahme-/Waage-Seiten-/UIX-Dateien
ausgeführt. Backend: `tests/test_intake_weighing_screen_contracts.py`.

UTF-8 wurde für die eigenen neuen Quellen und geänderten Annahmetests geprüft;
keine Ersatzzeichen verbleiben. Diese Bedienabnahme ist keine Live-SSO-,
Hardware-, Browserbild- oder Produktionsfreigabe. Der echte SQL-/RLS-/Audit-
Nachweis der Waagenmigration gehört zur getrennten Backend-Abnahme des Leads.
Keine neue Datenbank, kein Container und kein Datenreset wurden angelegt.
