---
title: PSM-Zulassungen - Pruefstand und Grenzen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-05
version: 1.2.0
---

# PSM-Zulassungen: Pruefstand und Grenzen (05.11.2026)

Die native Liste verwendet ausschliesslich den lokalen PSM-Stamm des angemeldeten Mandanten. Artikelnummer, Name, Wirkstoff, Mitteltyp, BVL-Nummer und Ablaufdatum kommen unveraendert aus dem Stamm. Der nullable Aktivwert bleibt bei unbekanntem Wert leer. Ablauf bedeutet nicht Widerruf oder Sperre. Die Ablaufzahl vergleicht den Kalendertag in der Betriebszeitzone und umfasst alle Seiten der gefilterten Ergebnismenge.

Nutzerentscheidung 04.11.2026: „vorhandene zeilen sin nur testdaten. tabelle kann entfernt werden, wenn nicht mehr passend“. Das ersetzte Register wird nach Verbraucherpruefung auch mit Zeilen unter Tabellensperre ohne CASCADE entfernt. Weiter genutzte Tabellen sind nicht umfasst. Die transaktionale Migrationspruefung ist im Nachlauf unten belegt; eine Abnahme mit gewachsenen Daten ist nicht erfolgt.

## Nachlauf 05.11.2026

Ein Alembic-Kopf; die vollstaendige noch ausstehende Kette wurde auf `valeo_probe` als `valeo_migrator` in einer Transaktion ausgefuehrt und vollstaendig zurueckgerollt. Ein Savepoint-Test belegte DROP der gefuellten ersetzten Tabelle und Wiederherstellung der Zeile durch Rollback. Zwei PostgreSQL-Tests bestanden: dieser Migrationstest und die SQL-Mandantenfilterung mit eigenen PSM-Zeilen. Letztere ist kein JWT- oder valeo_app-RLS-Nachweis.

Der bestehende PSM-Readvertrag bildet nullable ORM-Felder ab; `ist_aktiv` und `is_active` spiegeln denselben Wert. BVL-Felder ohne Quelle und ungueltige Ablaufdaten bleiben unbekannt. Create- und Updatevalidierung sind unveraendert. Neun reine PSM-/Parser-/Guard-/Routenvertragsfaelle bestanden (Exit 0). Der PSM-Zulassungsguard verweigert unbekannte, ungueltige und abgelaufene Daten; valide Zeitpunkte werden im Geschaeftstag verglichen. Die native Batch-11/12-Pruefung ergab 147 bestandene und einen erwarteten historischen Altlastfall; der Hook-Wrappertest bestand. Vollstaendige Frontend-Typpruefung bestanden. Die Komponenten-Sichtpruefung ist unten belegt; die authentifizierte Browserabnahme bleibt offen.

Maskenfeldvertrag nach Readschema-Anpassung: 5 bestanden. Der Dokumentgenerator-Gesamtcheck lief nach Schema- und Inventarnachzug erfolgreich; Pagination-, Godfile- und SQL-f-String-Gates bestanden, Doku-Drift 0. Pruefstandsrevision nach den Rollbacks unveraendert `ruestlisten_tabelle_20261103`, keine fremden aktiven Clients. Ein zunaechst versuchtes globales Batch-9-Testfixture scheiterte vor dem Test an fehlender `SET ROLE valeo_app`-Berechtigung; der isolierte SQL-Praedikat-Test bestand ohne Rollenaenderung.

## Visuelle Komponentenpruefung 05.11.2026

Die kanonische PSM-ScreenDefinition wurde unveraendert durch NativeListPage, RenderPlan und UniversalMaskRuntime in installiertem Headless-Chrome gerendert. Nur der HTTP-Adapter liefert drei ausdruecklich synthetische Datensaetze; Schreibmethoden und externe Netzwerkzugriffe sind gesperrt. Keine Sitzung, Datenbank oder Buchung wird verwendet.

**6 von 6 Ansichten bestanden:** 1366x768, 1440x900 und 1920x1080, jeweils Hell/Dunkel. Axe meldet fuer den Textkontrast null Verstoesse und null unbewertete Befunde; keine Laufzeitfehler, externen Anfragen oder Seitenueberbreite. Sechs unveraenderte Screenshots wurden gesichtet: lesbare Texte und Konturen, konsistente Themen. Die geteilte Ansicht zeigt eine reduzierte Tabellenbreite; weitere Spalten liegen im Tabellenbereich, nicht als Seitenueberlauf. Kein Nachweis der gesamten ERP-Shell oder aller Tabelleninteraktionen.

Die Pruefung fand stark abgeschwaechte Unicode-Sortierpfeile in der gemeinsamen Tabelle. Sie sind zentral durch SVG-Symbole mit Vordergrundfarbe ersetzt. Bestehende VirtualDataTable-Suite: **4 passed**, Exit 0. Der Test wurde nicht um Kontrast-Ausnahmen abgeschwaecht.

Nachweise: `evidence/psm-zulassungen-20261105/psm-rendernachweis.json` (Schema-Hash und sechs Ergebnisse), daneben sechs PNGs. Wiederholung: im Frontend `node tests/visual/psm-runtime-visual.mjs`. Die direkte Browser-Use-Verbindung scheiterte vor dem Start am Kernel-Assetpfad; der Komponentenlauf ersetzt keine Anmeldung, Rollen- oder RLS-Endabnahme. CI auf dem neuen Commit steht aus.

CI-Pfadpruefung: Der generische Dateiname `report.json` ist im Projekt gesperrt. Der ausschliesslich synthetische Renderer-Nachweis traegt jetzt den eindeutigen Namen `psm-rendernachweis.json`; keine Guard-Regel geaendert.
