---
title: Mandanten-Administration
type: how-to
audience: [tenant-admin]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Mandanten-Administration

Aufgaben des fachlichen Mandanten-Admins: Module, Rollen, Nummernkreise und
Stammdaten je Mandant verwalten.

## Mandantenkontext

Jeder Request trägt den Mandanten über den Header `X-Tenant-ID`. Fehlt er, greift
der Token-Claim bzw. der Default-Tenant. Daten sind über PostgreSQL-Schemata und
Tenant-Bezug strikt getrennt.

## Typische Aufgaben

- **Module aktivieren/deaktivieren** → siehe
  [Module & Feature-Flags](module-und-feature-flags.md).
- **Rollen & Berechtigungen** → siehe [RBAC & Rollen](rbac-und-rollen.md).
- **Nummernkreise** für Belege (Auftrag, Lieferschein, Rechnung) pflegen.
- **Stammdaten** (Kunden, Lieferanten, Artikel, Silozellen) pflegen.
- **Belegvorlagen & Übersetzungen** anpassen.

## Checkliste Neueinrichtung Mandant

1. Mandant anlegen und Default-Sprache setzen.
2. Benötigte Module aktivieren.
3. Rollen zuweisen.
4. Nummernkreise definieren.
5. Stammdaten importieren/pflegen.
6. Testbeleg je Kernprozess (Annahme, Verkauf) durchspielen.

## Häufige Fehler

- **Nutzer sieht Modul nicht:** Modul nicht aktiviert oder Rolle fehlt.
- **Belegnummer-Konflikt:** Nummernkreis falsch konfiguriert (GoBD: keine Lücken
  ohne Begründung, keine Doppelung).
