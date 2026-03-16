# Wave-46 Status

## Scope
Process Quarantine Contracts + Workflow ACL Contracts

## Zielbild

Wave 46 ergänzt den Process-Kernel um zwei Stabilitäts- und Sicherheitsthemen:

1. **Process Quarantine Contracts**: Quarantäne-Mechanismus für fehlgeschlagene/suspekte
   Prozessinstanzen mit Retry-Strategien (SOFORT/FESTER_INTERVALL/EXPONENTIELL/KEIN_RETRY),
   Dead-Letter-Management und aggregierter Statistik.
   `QuarantaeneEintrag.berechne_naechsten_versuch()`: SOFORT→jetzt,
   FESTER_INTERVALL→jetzt+basis, EXPONENTIELL→jetzt+basis×2^versuch_anzahl, KEIN_RETRY→None.
   `kann_wiederholt_werden`: IN_QUARANTAENE + versuch_anzahl < max_versuche + kein KEIN_RETRY.
   `ist_dead_letter`: Status==DEAD_LETTER OR versuch_anzahl >= max_versuche.
   5 Standard-Einträge: QE-001 (IN_QUARANTAENE/EXPONENTIELL), QE-002 (IN_QUARANTAENE/FESTER_INTERVALL),
   QE-003 (DEAD_LETTER, Max-Versuche), QE-004 (FREIGEGEBEN/SOFORT), QE-005 (ABGEBROCHEN/KEIN_RETRY).

2. **Workflow ACL Contracts**: Feingranulare Zugangskontrolle auf Workflow-Ressourcen-Ebene
   mit `AclRegel` (Erlauben/Verweigern je Subjekt+Ressource+Aktion), Deny-Override-Prinzip
   und Default-Deny bei keinem Match.
   `pruefe_acl()`: Sort nach (prioritaet, 0=VERWEIGERN/1=ERLAUBEN), erste Regel gewinnt,
   kein Match → Default-Deny (VERWEIGERN, angewandte_regel_id="").
   6 Standardregeln: AR-001 (admin/\* ADMINISTRIEREN ERLAUBEN p=1), AR-002 (sachbearbeiter
   kontrakt AUSFUEHREN ERLAUBEN p=10), AR-003 (sachbearbeiter settlement FREIGEBEN VERWEIGERN p=5),
   AR-004 (leiter settlement FREIGEBEN ERLAUBEN p=5), AR-005 (\*/\* LESEN ERLAUBEN p=100),
   AR-006 (extern compliance SCHREIBEN VERWEIGERN p=1).

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/process_quarantine_contracts.py` | `QuarantaeneEintrag` (kann_wiederholt_werden, ist_dead_letter, berechne_naechsten_versuch), `QuarantaeneStatistik` (dead_letter_rate_pct) | abgeschlossen |
| AP2 | `app/core/process_quarantine_contracts.py` | `berechne_quarantaene_statistik()`, `get_default_quarantaene_eintraege()` (5) | abgeschlossen |
| AP3 | `app/core/workflow_acl_contracts.py` | `AclRegel` (_trifft_zu, ist_erlaubnis, ist_verweigerung), `AclEntscheidung` (ist_erlaubt) | abgeschlossen |
| AP4 | `app/core/workflow_acl_contracts.py` | `pruefe_acl()` (Deny-Override, Default-Deny), `get_default_acl_regeln()` (6) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/quarantine/eintraege`, `POST /process/quarantine/retry-zeitpunkt` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/acl/regeln`, `POST /process/acl/pruefe` | abgeschlossen |

## Abnahmekriterien

- `kann_wiederholt_werden`: False wenn KEIN_RETRY, False wenn versuch_anzahl >= max_versuche, False wenn nicht IN_QUARANTAENE
- `ist_dead_letter`: True wenn Status==DEAD_LETTER ODER versuch_anzahl >= max_versuche
- `berechne_naechsten_versuch(KEIN_RETRY)` → None
- `berechne_naechsten_versuch(EXPONENTIELL, versuch=3, basis=60)` → jetzt + 480s (60×2³)
- `pruefe_acl()`: VERWEIGERN gewinnt bei gleicher Priorität (Deny-Override)
- `pruefe_acl()`: Kein Match → Default-Deny (angewandte_regel_id="")
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave46_quarantine_acl.py` — 68 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave46_quarantine_acl.py -q --no-cov
# Ergebnis: 68 passed
```

## Status
`abgeschlossen`
