---
title: Hersteller-Recherche Agrar-Lager / Silo / Mischung
type: reference
audience: [entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Sammelliste offener Hersteller- und Schnittstellen-Recherche fuer Agrar-Lager, Silo und Mischungsanlagen (Stand 2026-06-12, WM-AGRI-SILO-001).
---

# Offene Recherche: Hersteller & Schnittstellen (Agrar-Lager / Silo / Mischung)

**Status:** Sammelliste â€” **keine** behaupteten Integrationen ohne belastbare Herstellerdokumentation im Projekt.

**Zweck:** Vorbereitung WM-AGRI-PLC-005 / WM-AGRI-MOBILE-004 / WM-AGRI-FLUSH-006.

## Kategorien

1. **Waagen** (Fahrzeugwaage, Durchfahrt, Bandwaage)
2. **Silo- und FÃ¶rdertechnik** (Elevatoren, Ketten, Schnecken, Weichen, Klappen)
3. **Mahl- und Mischanlagen / Feed-Mill**
4. **Mobile Mahl- und Mischanlagen (MMX)**

## MÃ¶gliche Schnittstellen-Typen (generisch)

| Typ | Eignung |
|-----|---------|
| OPC-UA | Industriestandard, viele SPS/Scada |
| Modbus/TCP | Einfache Register, Ã¤ltere Anlagen |
| MQTT | IoT-Gateways, Telemetrie |
| REST | Moderne Waagen-/Cloud-Dienste |
| CSV/XML/JSON-Export | Batch-Import in VALEO |
| ODBC/SQL-Export | InsellÃ¶sungen (Vorsicht: Sicherheit/Tenant) |
| PDF (Wiegeschein, Mischprotokoll) | Parsing/OCR nur als letzte Option |
| Tablet-/App-Erfassung | Operator-UI parallel zu Backend-Events |

## NÃ¤chste Schritte (nicht in diesem Slice)

- Pro Kategorie 2â€“3 MarktfÃ¼hrer anonymisieren oder mit **Ã¶ffentlicher** API-Doku verlinken.
- Abgleich mit Kundenstandort (welche Anlage wirklich im Einsatz).
- Proof-of-Concept getrennt vom Core-ERP (Adapter-Service, Outbox).
