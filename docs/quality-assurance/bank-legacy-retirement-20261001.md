---
title: Bankmodell-Retirement 2026-10-01
type: reference
audience: [entwickler, agent, qa]
owner: Codex-01a0f3fc
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
---

# Bankmodell-Retirement

## Entscheidung und Ist-Stand

Explizite User-Steuerung: Entwicklungsphase, saemtliche Altlasten duerfen
entfernt werden. Der anfangs erwogene Archivansatz wurde deshalb vollstaendig
verworfen. Keine neue Archivstruktur oder Kompatibilitaetsroute.

bank_import.py samt Montage in api.py, vier ausschliesslich dort konsumierte
DTOs und konkurrierende Bank-Vertraege in Wave3/Welle12 entfernt. Vor Edit
Aufrufer, Schema, ADR-003, Domain Pack, Workboard, Gaps und Handoffs gelesen.
Kein Frontend-Konsument der vier alten /api/v1/bank-Routen gefunden. Die echten
kanonischen Routen liegen unter /api/v1/finance; lokale Testrouter allein
haetten die reale Montage nicht bewiesen.

## Verifikation

Finaler gemeinsamer Lauf: **187 Tests bestanden**, darunter **9 neue**
Retirement-Vertraege, Wave3/Welle12, CAMT/MT940, echte Datei-Replays, Matching,
CSV-Import und Payment-Execution. Log: artifacts/bank-retirement-final-tests.log.
Ein erster echter Router-Vertrag scheiterte an fehlendem /finance im Test;
der Vertrag und alle API-Dokumentationspfade wurden an die reale Montage
angepasst. Keine Produkt-Route wurde fuer einen Test umbenannt.

Neue Migration auf einem eigenen kleinen Schema im bestehenden valeo_probe
geprueft: belegte und leere Altbestandsloeschung, kanonische Auszuege und
OP-Reste unveraendert, fehlendes Modell und unerwartete Fremdabhaengigkeit
brechen ab, beide DROPs rollen gemeinsam zurueck. Kein CASCADE. Downgrade
verweigert erfundene Historie explizit. Eigene Testschemata gezielt entfernt;
keine neue Datenbank/Dockerinstanz oder gemeinsamer Reset.

Ruff bestanden. Architektur-Drift strict bestanden: 932 Routen, 259 Services,
448 Endpointmodule zugeordnet. Vorhandenes webhook_service erhielt das
fehlende exakte Platform-Mapping, keine neue Funktion. Business-Time-Ratsche:
207 Stellen/116 Dateien; nur nachweislich entfernte Quellen abgesenkt.
Baselineintegritaet gegen Claim 1ede88778 bestanden. Agent-Handbuch unveraendert
aktuell. Inventare und OpenAPI regeneriert; vorher committete Inventardrift
wird damit ebenfalls nachgezogen. OpenAPI meldet weiterhin bestehende doppelte
Operation-IDs; keine Behauptung einer global widerspruchsfreien API.

## Datenbank und Integration

Read-only vor Migration: Entwicklungsdatenbank 8 alte Auszuege/8 Zeilen;
valeo_probe 0/0. Die Migration loescht nur diese zwei Alttabellen; die
kanonischen Auszuege und offenen Posten werden nicht veraendert oder neu bezahlt.

Ein erster Anwendungsversuch brach vor jeder DDL-Aenderung ab, weil
Entwicklung und Probe verschiedene Vorgaengerrevisionen hatten. Danach wurde
der Steuernachweis-Vorgaenger als ed0733300 committed. Zielgerichtete
Alembic-Anwendung/Verifikation auf beiden vorhandenen Datenbanken erfolgreich:
bank_legacy_retirement_20261001, beide Altbanktabellen absent, beide kanonischen
Banktabellen vorhanden. Log: artifacts/bank-retirement-migration.log.
Keine neue Datenbank oder Dockerinstanz, kein Reset, keine Zahlung/OP-Aenderung.
Tabellenkatalog nach realem Datenbankstand regeneriert. Die acht alten
Entwicklungsauszugdatensaetze entfallen nach expliziter User-Freigabe.

## Architektur-Impact und Uebergabe

Domain Finance; Entscheidungsstufe Significant; Proposed ADR-073 nach ADR-003.
Code, Domain Pack, Tests, Index, Inventare, OpenAPI und Workboard betroffen.
Keine neue Container-/Systemgrenze oder Eventform: C4-Quellen unveraendert,
generierte Sichten bestanden. Aktiver Speicher domain_erp; Alt-API entfernt.

GitHub-CI und Deployment bleiben externe Abnahmen. Weitere CAMT-Bankprofile,
semantische Duplikate im kanonischen Speicher, Reversal/GL und bestehende
Coverage-Luecken sind separate bekannte Gaps. Kein Gesamtabschluss behauptet.
