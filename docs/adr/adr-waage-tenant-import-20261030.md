---
title: Waagenstamm, externe Waagenkennung und kanonischer ASCII-Import
type: adr
audience: [entwickler, architektur, qa]
owner: Codex
status: akzeptiert
last_reviewed: 2026-10-30
version: 1.0.0
description: Mandantengrenze des Waagenstamms und Wiederholungsnachweise fuer kanonische ASCII-Wiegescheine.
---

# Waagenstamm und Wiegescheinimport

**Status:** Akzeptiert. **Datum:** 2026-10-30.

## Kontext

Die bisherige Waagenliste las ohne Mandantengrenze; die Import- und Kalibrierungswege verwendeten nicht belegte Paralleltabellen und eine globale Fehlerliste. Fuehrend bleiben `domain_ops.ops_waagen` fuer registrierte Waagen und `domain_inventory.weighing_tickets` fuer Wiegescheine. Keine zweite Wiegequelle wird eingefuehrt.

## Entscheidung

Die additive Migration laesst vorhandene Waagen ohne belegte Herkunft mit NULL-Mandant erhalten und unsichtbar. Ein NOT-VALID-Check erlaubt keine neuen oder geaenderten NULL-/Leermandantenzeilen. Keine automatische Zuordnung, kein Reset und kein automatischer Downgrade. Eichtermine verwenden die vorhandenen Datumsspalten; Eichamt und Zertifikatnummer sind additive Metadaten derselben Waage. Datumspaare werden auch beim partiellen Aendern geprueft. Audit vor/nach und Outbox werden gemeinsam committed.

`scale_id` war bisher ein freier String ohne Fremdschluessel; insbesondere Fremdwaagen verwenden externe Kennungen. Das wird nicht nachtraeglich zu einer verpflichtenden Registrierungs-ID umgedeutet. Existiert der exakte Wert im Waagenstamm, muss er dem aktiven Mandanten gehoeren; fremde und unzugeordnete registrierte IDs werden abgewiesen. Unbekannte Werte bleiben ausschliesslich externe Quellenbezeichnungen und gewaehren keine Stammdatenrechte. Bestehende Wiegescheine werden nicht umgeschrieben.

Die eng begrenzte Datenbankfunktion `public.waage_reference_allowed(text)` liefert nur diese Berechtigung. Eine normale RLS-Abfrage koennte fremde IDs nicht von unbekannten externen Kennungen unterscheiden. Die Funktion verwendet festen Suchpfad, festes SQL, den bestehenden `rls_current_tenant()` und sperrt einen gefundenen Waagenstamm mit FOR SHARE gegen konkurrierendes Loeschen. PUBLIC hat kein Ausfuehrungsrecht. Die Migrationsrolle muss die Waagentabelle besitzen oder RLS autorisiert umgehen; andernfalls scheitert die Funktion geschlossen. Anwendungsrollen erhalten keinen direkten Bypass. Loeschen des registrierten Stamms sperrt gegen konkurrierende Referenzen und verweigert vorhandene kanonische Wiegescheine, Legacy-Kinder und Importnachweise.

ASCII-W-Saetze mit zugehoerigen Q-Saetzen werden gemeinsam validiert. Nur UTF-8, hoechstens 1 MB und 1000 Gruppen; keine erfundenen Nummern oder Messzeitpunkte. Die Quellzeit verwendet die Betriebszeitzone, falls kein Offset geliefert wird. Der Import ist ein Eingangsvorgang (`direction=in`). Artikelreferenzen werden auf den aktiven Mandanten geprueft. Lieferanten-, Partien- und Siloangaben bleiben ausdrueckliche Quellenmetadaten; sie erzeugen keine fremden Stammdatenverknuepfungen. Gewichts- und Abrechnungspruefungen verwenden die vorhandenen Domainfunktionen und kanonische Datenqualitaetspruefung.

`domain_ops.waage_import_entries` ist ein mandantengebundener Eingangs-/Fehlernachweis, keine Wiegetabelle. Deterministische Hashes aus Mandant, Waage und kompletter W/Q-Gruppe verhindern Doppelwirkungen bei erneutem Upload. Ein mandantenbezogenes Transaktionsschloss serialisiert Import und Retry; Waagensperren schuetzen gegen Loeschen. Strikte Verarbeitung rollt die gesamte Datei bei Fehler zurueck. Tolerante Verarbeitung speichert gueltige Wiegescheine und Fehlernachweise atomar. Retry verarbeitet denselben Nachweis erneut, etwa nach Bereitstellung fehlender eigener Artikel; ungueltige Rohdaten werden nicht still korrigiert. Eine korrigierte Datei wird neu hochgeladen. Verwerfen behaelt einen Tombstone, damit Wiederholung keinen erledigten Fehler wieder eroeffnet. Audit und Outbox sind atomar mit jeder Wirkung. Die Fehlerliste ist begrenzt und RLS-geschuetzt.

## Konsequenzen

Unmandantierte `ops_wiegungen`-CRUD-Wege bleiben 410: die aktive Anwendung verwendet den kanonischen Wiegescheinweg. Ihre Reaktivierung waere eine konkurrierende Fachquelle. Die neue Implementierung behauptet keine erfolgte Migration, Rollenbereitstellung, Hardwareeichung oder Live-UAT; diese werden getrennt nachgewiesen.
