# Wave-20 Status

## Scope
Settlement-Audit-Hash-Kette + GoBD-Vollständigkeit + Optimistic-Lock-Contracts

## Zielbild

Wave 20 schliesst die drei verbleibenden P0-Luecken nach Wave-19-Settlement-Freigabe:
Gap 010 (Prozessjournalisierung mit Audit-Hash), Gap 041 (GoBD-Belegkette komplett)
und Gap 035 (Optimistic Locking gegen stille Überschreibungen).
Jeder Settlement-Freigabeschritt erhält einen verketteten SHA-256-Hash (GoBD §§ 146/147 AO).
Concurrent-Edit-Konflikte werden über unveränderliche Versions-Guards abgefangen.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/settlement_audit_chain.py` | GoBD-konforme Audit-Hash-Kette fuer Settlement-Lifecycle: SHA-256-Verkettung jedes Freigabeschritts; Ketten-Integritäts-Verifikation | abgeschlossen |
| AP2 | `app/core/optimistic_lock_contracts.py` | OCC-Contracts: `VersionedAggregate`, `OptimisticLockError`, `version_guard()`; verhindert stille Überschreibungen | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/settlement/audit-chain/{settlement_id}` — liefert vollständige Hash-Kette + Integritätsstatus | abgeschlossen |
| AP4 | `app/core/gobd_settlement_check.py` | GoBD-Pflicht-Check: 9 Pflichtfelder (Beleg-Nr, Datum, Betrag, Währung, Gegenkonto, Audit-Hash, Tenant, Kunde, Prozessreferenz) — maschinenlesbar | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/settlement/gobd-check/{settlement_id}` — GoBD-Vollständigkeitsprüfung mit Compliance-Status | abgeschlossen |
| AP6 | `app/core/settlement_audit_chain.py` | `verify_integrity()` erkennt Hash-Tampering und Kettenbrüche; `build_genesis_chain()` als Einstiegspunkt | abgeschlossen |

## Abnahmekriterien

- Jeder Freigabeschritt in der Settlement-Kette hat einen SHA-256-Hash des Vorgängers
- `verify_chain_integrity()` erkennt Tampering zuverlässig
- `version_guard()` wirft `OptimisticLockError` bei Versions-Konflikt
- GoBD-Check liefert `compliant=True/False` mit maschinenlesbaren Verstössen
- Alle neuen Contracts tragen `schema_version=1`
- Keine Schichtverletzungen: `app/core/` importiert keine API-Module

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave20_audit_chain.py` | 43 | AP1/AP6: Hash-Kette, Verkettung, Tampering-Erkennung; AP2: OCC-Contracts; AP4: GoBD-Check; AP3/AP5: API-Endpoints |

**Gesamt Wave 20: 43 Tests gruen**

## Gaps geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 010 | Betriebsprüfungsfeste Prozessjournalisierung | SHA-256-Hash-Kette in `settlement_audit_chain.py` |
| Gap 041 | GoBD Belegkette komplett durchgängig | 9-Felder-GoBD-Check in `gobd_settlement_check.py` |
| Gap 035 | Optimistic Locking gegen stille Überschreibungen | `version_guard()` + `OptimisticLockError` in `optimistic_lock_contracts.py` |

## Status
`abgeschlossen` — 2026-03-14 — 1068 Tests Gesamtsuite gruen
