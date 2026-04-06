# INT-SG-049 - Superglue CRM Masterdata

## Ziel

Den CRM-/Masterdata-Connector auf den produktiven tenant-gebundenen Laufzeitpfad ziehen.

## Umgesetzt

- `customer_profile_adapter.py` bietet jetzt `get_customer_profile()` als produktiven Read-Pfad.
- `CustomerProfilePreview` wurde um produktive Stammfelder erweitert.
- Tenant-gebundene Tool-IDs und Runtime-Credentials bleiben der einzige Ausfuehrungspfad.

## Verifikation

- `pytest tests/test_superglue_customer_profile_adapter.py -q --no-cov`

