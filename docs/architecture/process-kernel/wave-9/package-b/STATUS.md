# Wave 9 Paket B Status

## Paket
- Name: `Ernte-Kampagne und Frontend-Process-Binding`
- Zugeordnete Aufgaben: `AP2`, `AP4`
- Status: `abgeschlossen`

## Gelieferte Artefakte

| Datei | Inhalt | Status |
|-------|--------|--------|
| `app/core/ernte_kampagne.py` | `ErnteKampagne`, `SchlagErnteziel`, `ErnteKampagneStore`, `fortschritt_pct()` | umgesetzt |
| `app/core/frontend_process_binding.py` | `MaskenCommandBinding`, `MaskenBindingRegistry`, `build_default_bindings()` | umgesetzt |
| `app/api/v1/endpoints/ernte_kampagne_api.py` | `POST /ernte-kampagnen`, `GET /tenant/{tenant_id}`, `POST /{id}/start|abschliessen` | umgesetzt |
| `tests/test_process_kernel_wave9_domain.py` | 22 Tests | umgesetzt |

## Testergebnis

```bash
pytest tests/test_process_kernel_wave9_domain.py -q --no-cov
# Ergebnis: 22 passed
```

## Abhaengigkeiten
- `app/core/business_commands.py` (Wave 5 AP1) -- Command-Katalog als Bindungsbasis
- `app/core/ui_mask_registry.py` (Wave 3 AP1) -- 18 Masken als Binding-Quelle
