# Wave 9 Status

## Wave
- Name: `EDI/API-Integration, Ernte-Kampagnen und Frontend-Prozessanbindung`
- Epics: `Epic 3 Tenant, Security and Integration Governance`, `Epic 4 Specialized Domain Enablers`
- Status: `abgeschlossen`
- Startbedingung: Wave 8 abgeschlossen

## Ziel

Externe Integrationen (EDI-Import/Export, API-Partner) werden als formale
Integrations-Klassen modelliert. Ernte-Kampagnen schliessen die letzte grosse
Agrar-Luecke. Frontend-Masken binden sich an Process-Kernel-Commands (Wave 5) an.

## Arbeitspakete

| AP | Thema | Status |
|----|-------|--------|
| AP1 | EDI-Integrations-Klassen: EDIFACT ORDERS/INVOIC, SEPA XML | umgesetzt |
| AP2 | Ernte-Kampagne: Saison-Aggregat, Schlag-Cluster, Ernteziel | umgesetzt |
| AP3 | API-Gateway-Manifest: externe API-Partner mit Rate-Limits und Scopes | umgesetzt |
| AP4 | Frontend-Process-Binding: Command-Dispatch statt CRUD aus Masken | umgesetzt |
| AP5 | Zertifikate und Qualitaetsnachweise: QS-GAP, ISO 22000 Lebenszyklus | umgesetzt |

## Pakete

### Paket A: EDI + API-Gateway + Zertifikate
- Enthaelt: AP1, AP3, AP5
- Tests: `tests/test_process_kernel_wave9_integration.py` (>= 22)

### Paket B: Ernte-Kampagne + Frontend-Binding
- Enthaelt: AP2, AP4
- Tests: `tests/test_process_kernel_wave9_domain.py` (>= 20)

## Exit-Kriterien

- [x] EdiNachricht kann geparst und validiert werden
- [x] ErnteKampagne.fortschritt_pct() berechnet korrekt, Zustandsmaschine vollstaendig
- [x] ApiGatewayRegistry.pruefe_api_zugriff() prueft Scopes und Rate-Limits
- [x] MaskenBindingRegistry deckt die vorgesehenen Wave-9-Frontend-Bindings ab
- [x] Zertifikat.tage_bis_ablauf() warnt korrekt vor Ablauf
- [x] Alle >= 42 Wave-9-Tests gruen

## Verifikation

```bash
pytest tests/test_process_kernel_wave9_integration.py -q --no-cov
# Ergebnis: 28 passed

pytest tests/test_process_kernel_wave9_domain.py -q --no-cov
# Ergebnis: 22 passed
```

## Startpunkte

- `app/core/business_commands.py` (Wave 5) -- Command-Katalog als Bindungsbasis
- `app/core/ui_mask_registry.py` (Wave 3 AP1) -- 18 Masken als Binding-Quelle
- `modules/einkauf/services/versand_service.py` -- EDIFACT-Referenz
- `app/core/tenant_isolation_guard.py` (Wave 8) -- Isolation fuer API-Partner-Check
