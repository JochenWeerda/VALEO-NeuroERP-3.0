# Response-Verträge HR-Löschung und Versandprofil

Stand 2026-11-07. Die drei HR-Löschkommandos deklarieren die tatsächlichen Erfolgsfelder einschließlich Audit, Outbox und Wiederholung; das Versandprofilkommando deklariert sein Ergebnis mit Audit und Wiederholung. Die gesperrten Legacy-DELETE-Wege dokumentieren ihre bestehenden Fehlerantworten: HR 409, Versandprofil 410. Fachverhalten und Schreibfreigaben bleiben unverändert.

Nachweis: `python -m pytest --noconftest --no-cov -q tests/test_hr_versand_response_contracts.py tests/test_hr_row_delete_routes.py tests/test_hr_row_delete_commands.py tests/test_versandprofil_commands.py`: 45 bestanden. `python scripts/check_response_models.py --verbose`: 3746/3746 Routen, 0 untypisiert, Schwelle 0. Kein Datenbankzugriff. OpenAPI-Gesamtprojektion wird vom Lead synchronisiert.
