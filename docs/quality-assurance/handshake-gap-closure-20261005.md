---
title: Handshake-Luecken Bank, Journalnummer und Wiegemodell
type: reference
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-05
version: 1.0.0
---

# Handshake-Luecken 2026-10-05

## Bank-Fixture und Paginierung

Das migrierte Shared-Probe-Schema enthaelt die Bank-GL-Spalte bereits.
LIKE INCLUDING ALL kopiert Spalten, Checks und Indizes; ein erneuter
bank_gl_binding_upgrade erzeugte DuplicateColumn und 31 Setup-Fehler.
Das Fixture kopiert jetzt den aktuellen Stand und ergaenzt nur den von
PostgreSQL nicht kopierten Fremdschluessel auf seine eigene CoA-Tabelle.
Keine Migration gegen gemeinsame Tabellen, kein stilles IF NOT EXISTS.
32 echte Bankvertraege bestanden. Der neue Seitentest prueft stabile,
lueckenlose und fremdtenantfreie Seiten sowie ungueltige Grenzen.
Ledger-Optionen behalten SQL LIMIT/OFFSET und verwenden fetchmany(limit).
Paginierungsratsche: 285 Abfragen in 258 Funktionen, Exit 0.

## Journalnummer je Mandant

Im Pruefstand war journal_entries_entry_number_key global. Die neue
Migration journal_number_tenant_20261005 folgt dem committed
kontrakt_disposition_20261005. Sie installiert UNIQUE(tenant_id,entry_number),
setzt tenant_id auf NOT NULL und entfernt die globale Nummern-Eindeutigkeit.
Keine Nummernaenderung, kein Datenloeschen und kein erfundener Mandant.
Fehlender Mandant oder bestehende Tenant-Dubletten stoppen die Migration
atomar. Downgrade kollidierender Cross-Tenant-Nummern stoppt statt Belege
umzunummerieren. ORM und Datenbank haben denselben Vertrag.
Sechs neue Vertraege bestanden: ORM, erlaubte Cross-Tenant-Nummer,
abgewiesene Tenant-Dublette, fehlender Mandant, erneute Anwendung und
atomarer Migrationsabbruch mit erhaltener Altzeile.
Die Tests verwenden private Schemas im vorhandenen valeo_probe.

## Fuehrendes Wiegemodell

[ADR-077](../adr/adr-077-leading-weighing-ticket.md) entscheidet den
kanonischen Inventory-Wiegeschein anhand realer Verbraucher und FK-Beziehungen.
Entscheidungs-Handshake geschlossen. Die technische Umstellung von
waage_mobile.py und Operations-Wiegung-CRUD bleibt als eigener Folge-Slice
offen; kein bereits vollzogener Tabellenrueckbau behauptet.
Agrar- und Operations-Alttabellen sind im geprueften Probe jeweils leer.

## Betrieb und Grenzen

Keine weitere Datenbank, Dockerinstanz oder Ruecksetzung. Vor einer
Integration erneut Head und aktive Nutzung pruefen; eigener Wartungsclaim
steht im Workboard. Gemeinsame Journalmigration und Betriebsnachweis werden
nach der privaten Abnahme separat dokumentiert. Die Entwicklungsdatenbank
ist nicht Bestandteil dieses Wartungsclaims. Kein Gesamt-GoBD-/UI-Nachweis.

## Regression

380 Bank-/Journal-/Perioden-/Finance-Vertraege bestanden, einschliesslich
der 38 gezielten Checks. Log: artifacts/handshake-regression.log.
