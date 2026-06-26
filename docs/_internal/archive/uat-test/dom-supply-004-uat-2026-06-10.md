# DOM-SUPPLY-004 — UAT-Nachweispaket (Rückverfolgbarkeit & Lieferkette)

Abnahme-Grundlage für die durchgängige Lieferkette **Wiegung → Annahme → Lager →
Abrechnung** (Slices 004.1–004.4). Maßstab ist die 7-Punkte-Definition „fachliche
Tiefe erreicht". Dieses Paket bündelt Testfälle, erwartete Ergebnisse und die
bereits erbrachten technischen Nachweise.

## Testumgebung
- Frontend: `/lager/rueckverfolgbarkeit` (Nav „Rückverfolgbarkeit", Lager).
- Backend: `/api/v1/supply-chain/*` (siehe `app/api/v1/endpoints/supply_chain.py`).
- Seed: Wiegeschein `WG-2026-00001` → Annahme `EA-2026-0001` → Lot `LOT-2026-S001-001`.

## E2E (automatisiert)
- `playwright-tests/specs/inventory/rueckverfolgbarkeit-smoke.spec.ts` (@smoke):
  Seite lädt mit Picker; Kette eines Seed-Wiegescheins wird mit Timeline,
  Status und Ereignis-Log angezeigt.
- Backend-Logik: `tests/test_supply_chain_trace.py` (5), `tests/test_supply_chain_lot.py` (5).

## UAT-Testfälle

| # | Schritt | Erwartet | Standard-Punkt |
|---|---|---|---|
| 1 | Seite öffnen, Wiegeschein wählen | Genealogie Wiegung→Annahme→Lager(→Abrechnung) mit Status je Stufe | 1 Kernfall |
| 2 | Mengen-Konsistenz prüfen | kg-Differenz je Stufenübergang; >2 % rot als Schwund/Differenz | 2 Sonderfälle |
| 3 | Lücken prüfen | unallocated/fehlende/nicht-freigegebene Stufen werden gelistet | 2 Sonderfälle |
| 4 | Lot „Sperren" mit Grund | Status=gesperrt, Bewegung `sperre`, Ereignis `gesperrt` | 3 Storno/Korrektur |
| 5 | Lot „QS-Freigabe" mit Grund | Status=active, Ereignis `qs_freigabe`; nur aus gesperrt möglich | 3 |
| 6 | „Schwund" buchen (kg, Grund) | Bestand reduziert, Bewegung `schwund`, Ereignis; Übermenge → Fehler | 3 |
| 7 | „Ereignis erfassen" (Korrektur/Notiz) | Append-only Eintrag im Ereignis-Log mit Grund | 5 Audit |
| 8 | „Kette stornieren" mit Grund | kanon. Status=storniert, Lots→storniert/Bestand 0; Doppelstorno → Fehler | 3 + 5 |
| 9 | Erneut öffnen | Ereignis-Log persistent, Reihenfolge Wiegung→…→Abrechnung | 5 Audit |
| 10 | Anderer Tenant | keine fremden Lieferungen sichtbar | 5 Tenant |

## Erbrachte technische Nachweise (verifiziert 2026-06-10)
- `trace WG-2026-00001`: Kette korrekt, Mengen-Konsistenz 25.000 kg durchgängig (0 %),
  Lücken „unallocated"/„keine Abrechnung".
- `sync`: 3 Lifecycle-Ereignisse, 2. Lauf 0 (idempotent), Status „eingelagert".
- Lot-Aktionen: block→422 bei Doppel; release nur aus gesperrt; shrinkage 200 kg
  (25.000→24.800) + Ereignis; Übermenge→422.
- Storno: Lot→storniert/Bestand 0, kanon. Status storniert; Doppelstorno→422.

## Offene/Externe Abnahmepunkte (Punkt 7)
- Echte Waagenhardware/Eichnachweis, Drucker/Bon, Partie-Genealogie über Splits/Merges:
  Telefonie-/Hardware-Integration bzw. weitere Slices.
- Abrechnungs-Storno mit Finance-Wirkung (Gegenbuchung) → DOM-FIN-Schnittstelle.
- Fachliche Abnahme durch Betriebsleiter/Lagerleiter (Unterschrift) ausstehend.

## Status
004.1–004.4 umgesetzt + technisch verifiziert; E2E-Smoke + BE-Tests grün.
004.5 = dieses UAT-Paket + E2E-Spec. Verbleibend: externe/betriebliche Unterschrift.
