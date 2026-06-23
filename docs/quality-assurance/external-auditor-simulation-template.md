# External Auditor Simulation Template

## Zweck

Dieses Template definiert interne Vorabnahmen nach gleichen oder hoeheren
Standards als externe Pruefer. Eine Simulation ersetzt keine reale
Zertifizierung oder externe Abnahme.

## Simulationskopf

| Feld | Inhalt |
|------|--------|
| Domain | POS, FiBu, Payroll, HR, DMS, QS, WMS, Security |
| Prueferprofil | z. B. Steuerberater, TSE-/Kassenpruefer, Datenschutz, ISO/Security |
| Rechts-/Normbezug | GoBD, DSFinV-K, DSGVO, DATEV, GMP+, VLOG, interne Policy |
| Testdaten | Fiktive, reproduzierbare Daten mit Tenant-Kontext |
| Pruefdatum | YYYY-MM-DD |
| Ergebnis | bestanden, bestanden_mit_auflagen, nicht_bestanden, extern_offen |

## Mindestpruefung

- Fachlicher Prozess ist vollstaendig.
- Belege sind unveraenderbar oder korrekt versioniert.
- Buchungssaetze sind balanciert und nachvollziehbar.
- Tenant-Isolation ist nachgewiesen.
- Rollenrechte und Vier-Augen-Pflichten sind geprueft.
- Audit Trail enthaelt User, Zeit, Grund, Entity und Vorher/Nachher-Kontext.
- Exporte haben Checksummen oder reproduzierbare Dateiinhalte.
- Storno/Korrektur ist fachlich und technisch abbildbar.
- Fehlerpfade sind fail-closed.
- Externe Abnahme ist als offen markiert, wenn sie nicht real erfolgt ist.

## Beispiel POS/TSE

```yaml
domain: POS
auditor_profile: Kassenpruefer
legal_reference:
  - GoBD
  - DSFinV-K
  - KassenSichV
test_cases:
  - bon_barzahlung
  - bon_ec_cash
  - barentnahme
  - gutschein_ausgabe
  - gutschein_annahme
  - tagesabschluss_z_report
evidence:
  - pdf_receipt
  - tse_mock_certificate
  - fiscal_journal
  - fibu_transfer
result: extern_offen
```

## Beispiel FiBu/Payroll

```yaml
domain: Payroll
auditor_profile: Steuerberater
legal_reference:
  - DATEV-ASCII
  - GoBD
  - DSGVO
test_cases:
  - monatsabschluss
  - arbeitgeberanteile
  - lohnarten_mapping
  - fibu_buchungssaetze
  - korrekturlauf
evidence:
  - export_file
  - checksum
  - booking_batch
  - audit_log
result: extern_offen
```

## Ergebnisregeln

`bestanden` darf nur gesetzt werden, wenn alle internen Pruefpunkte erfuellt
sind und kein reales externes Gate behauptet wird. Bei realer Zertifizierung
wird die externe Evidenz als eigener Nachweis verlinkt.

