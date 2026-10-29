---
title: UIX Mehrbereichsvertraege gegen zentrale Renderer
type: verification
owner: Codex frontend_ci_finish
status: in-arbeit
last_reviewed: 2026-10-27
---

# Abgegrenzte Testmigration

Claim `28503fa2165284f1060293f69f3f21f1e85606d6` betrifft ausschliesslich
`crm-fibu-logistik-uix.test.ts`, `fibu-portal-nawaro-uix.test.ts` und
`leitung-controlling-admin-uix.test.ts`, eigenen Helper/Fixtures/Paritaet und diese QA.
Keine Produktionsseite, Definition, API, Datenbank, Installation oder fremder Claim
wurde geaendert. Keine Resultcommits oder weiteren Workboard-Aenderungen waehrend
der seriellen Lead-Integration.

Alle **39 urspruenglichen Faelle bleiben erhalten**. Davon wurden **32** auf
wirkliche Page-Mounts umgestellt; **7** bleiben ausdruecklich statische
Quelltextpruefungen bzw. blockierte Migrationsvoraussetzungen. Ein zusaetzlicher
Dichtetest ergibt **40** Faelle. Es gibt keine Skip-/Todo-Markierung im Quelltext,
keine geloeschte Funktionsintention und keine abgesenkte Schwelle.

Der gemeinsame Helper ersetzt den HTTP-Transport, die Testsession, die Navigation
und Browsergrenzen (Viewport/geometrische Messung/Download-URL). NativeListPage,
ScreenDefinition-Kompiler, useUniversalMaskRuntime, UniversalMaskRenderer,
FastTableRenderer, NativeSelect und exportToCSV laufen unveraendert. Die 48 JSON-
Definitionen sind exakter Output registrierter Python-Builder; die
Paritaetsfunktion gegen alle 48 bestand. Vor der letzten Erweiterung bestand
auch pytest fuer alle damaligen 45 Definitionen (1/1).

Alle 48 direkt importierten Page-Module sind im aktuellen Routeninventar
registriert. Dieser Inventarabgleich und die Fixture-Paritaet sind statische
Nachweise; sie sind keine Browser-/Persistenz-/Funktionsfreigabe.

## Positive Teilabnahme

Zehn gezielt ausgewaehlte Faelle bestanden: Bankkonten-Suche und echter CSV-Blob,
Kampagnen-Suche und CSV, Warengruppen mit bestehender EINKAUF_BEARBEITEN-Rolle,
Verbindlichkeiten mit nativen SELECT-Elementen, Kreditoren, Anlieferavis, Journal,
FIBU-Schnittstelle, Lastschriften und Desktop-/Touch-Dichte. Die selektierten
19 uebrigen Faelle dieses einen Diagnoselaufs waren nur per CLI-Testfilter
nicht ausgewaehlt; keine dauerhaften Skips wurden eingefuehrt.

Der Dichtetest prueft reale Desktop-Gridzeilen von 40 px und den Wechsel auf die
Touch-Datensatzkarte mit Tastaturziel. Such-/Exportaktionen tragen min-h-touch;
der zentrale 44px-Token ist zusaetzlich statisch belegt. JSDOM ist keine visuelle
Pixelabnahme in einem Browser. Der CSV-Test ersetzt nicht exportToCSV, sondern
liest den tatsaechlich erzeugten Blob und prueft Kopf-/Datenzeilen.

## Vollstaendige abgegrenzte Ausfuehrung

Aktueller letzter Lauf: **13 bestanden / 27 fehlgeschlagen / 40 gesamt**.
Kein Gesamt-CI-Gruen. Rohbeleg: `artifacts/uix-multi-domain-results.json`;
Transportdiagnose: `artifacts/uix-multi-domain-all.log`.

## Echte Produktbefunde und offene Voraussetzungen

Die erhaltenen Erwartungen werden nicht durch ein generisches Export-Listenlayout
ersetzt. Fehlende Buttons werden nicht entfernt oder als bestandene Funktionen
klassifiziert. Mehrere urspruengliche UIX-Faelle enthalten mehr als einen Screen;
ein Fehler zaehlt deshalb nicht notwendig genau eine fehlende Capability.

| Bereich | Konkreter verbleibender Vertrag |
|---|---|
| Fuhrpark | Fahrzeuge-Builder hat nur CSV-Export, keine Fahrzeug-Neuanlage zum bestehenden Stamm. |
| Benachrichtigungen | Als gelesen markieren fehlt in der nativen Definition. |
| CRM | Kunden-E-Mail wird im montierten Renderer nicht als mailto-Link angeboten. |
| Zahlungsverkehr | Zahlungsvorschlaege ohne Zahlungslauf erstellen; Zahlungslaeufe ohne Wizard/Bezeichnung/Pflichtfeldfehler. |
| Offene Posten | OP-Verwaltung ohne Debitoren/Kreditoren-Einstieg; OP-Liste ohne Mahnlauf starten. |
| Hauptbuch | DATEV/FIBU-Schnittstellenaktion und Kontextnavigation fehlen. |
| Buchungsimport | Vorschau-/Schrittbedienung fehlt im generischen Listenvertrag. |
| Auswertungen | BWA ohne Aktualisieren; Bilanz/GuV/UStVA ohne die erwartete Periodenauswahl. |
| Journal | Storno fehlt; Checklisten-Details sind noch kein entitygebundener Mount in diesem Scope. |
| FIBU-Stamm | Periodische Buchungen ohne Sperren, Erloeskennziffern/Zuordnung ohne Bearbeiten, Forderungsgruppen/Lohnconnector ohne Loeschen. |
| Portal | Bestellungen/Vertraege/Anfragen ohne Details-Aktion; Rechnungen ohne dokumentgebundenen Download. CSV ist kein Rechnungsdownload. |
| Controlling | KPI-Verwaltung ohne Bearbeiten/Loeschen; Zeitreihenerfassung ohne Loeschen. |
| Quarantaene | Kein Erneut versuchen im nativen Builder (actions leer). |
| Einkauf | Die gerouteten AB-/Anfragen-Listen fordern nicht registrierte -liste-IDs statt der existierenden kanonischen IDs. Der echte Mount erreicht keinen RenderPlan. |
| Fahrer | Tourenplanung-Button sichtbar, aber nur command driver.openTours ohne navigationRoute/Handler; Klick navigiert nicht. |
| Rechnungserfassung | Alte Route liefert generische Liste ohne Speichern/Kostenstellensuche/Bedienerkontext. Der Lead hat die separate neue Inbox-/Belegkette anderweitig vergeben; hier nicht geaendert. |
| Nicht abgeschlossene Source-Migration | NaWaRo-Erfassung; Hausbanken/Betriebsstaetten/Mengeneinheiten/Partiestamm; Compliance/Docflow; Preis-/Konditions-Loeschen bleiben alte statische Pruefungen und liefern keine Runtime-Freigabe. |

Die letzten vier zusaetzlich migrierten urspruenglichen Faelle (AB, Anfragen,
OP-Mahnlauf, Fahrer) wurden unmittelbar vor der Stop-Scope-Nachricht begonnen.
Danach gab es keine weitere Umfangsausweitung. Die fehlenden Produktbindungen
gehoeren dem Lead und werden nicht durch Anpassung der Erwartungen kaschiert.

## Exakte verbliebene Fehler aus dem letzten Lauf

### crm-fibu-logistik-uix.test.ts

- oeffnet den Fuhrpark als Maske und legt ein Fahrzeug ueber den Stamm an
- stellt Benachrichtigungen lokal als gelesen
- stellt Kunden-mailto ohne Hover-Blau
- stellt Zahlungsvorschlaege Arbeit zuerst mit 44-px-Auswahl
- stellt Zahlungslaeufe Wizard zuerst mit 44-px-Auswahl
- stellt OP-Verwaltung Arbeit zuerst mit 44-px-Oeffnen
- stellt Auftragsbestaetigungen als Studio-Liste
- stellt Einkaufsanfragen als Studio-Liste mit echtem Export
- stellt FIBU Offene Posten Arbeit zuerst mit Mahnlauf
- stellt Hauptbuch Arbeit zuerst mit DATEV-Navigation
- stellt Buchungsimport Arbeit zuerst mit 44-px-Schritten
- stellt BWA Arbeit zuerst ohne Rohblau
- stellt Bilanz Arbeit zuerst mit CSV-Export
- stellt GuV Arbeit zuerst ohne Rohgruen
- stellt ELSTER Arbeit zuerst mit 44-px-Periode
- stellt Fahrer 44 px ohne Hover-Blau

### fibu-portal-nawaro-uix.test.ts

- stellt BWA-Aktualisieren auf 44 px
- stellt Journal-Storno und Abschluss-Details auf 44 px
- beschriftet FIBU-Stammaktionen 44 px
- stellt Portal-Self-Service 44 px mit beschrifteten Zeilen
- stellt NaWaRo-Erfassung 44 px
- beschriftet Einkauf-Stamm und Rechnungs-Toolbar 44 px
- beschriftet Stammdaten- und Partie-Aktionen 44 px

### leitung-controlling-admin-uix.test.ts

- stellt Controlling-Stammaktionen beschriftet 44 px
- stellt Leitungs-Admin und Vorfälle auf Deutsch 44 px
- stellt Compliance- und Docflow-Aktionen 44 px
- beschriftet Preis- und Konditions-Löschen 44 px
