"""SPEC-P0-03: kritische Finance-/Bestands-/Beleg-Datenpfade.

Bei DB-/Schemafehlern niemals still leere Listen liefern — RFC-7807 (503)
plus Alerting-Metrik `critical_data_path_errors_total`.
"""
from __future__ import annotations

from typing import NoReturn

from fastapi import HTTPException


def raise_critical_data_unavailable(
    *,
    endpoint: str,
    exc: BaseException,
    label: str,
) -> NoReturn:
    """Erhoeht die Metrik und wirft 503 mit Problem-Detail.

    Rueckgabetyp ``NoReturn``: die Funktion kehrt nie zurueck. Ohne das wuerden
    Typpruefer die aufrufenden Endpunkte mit ``response_model=list[...]`` als
    Pfad ohne Return melden.
    """
    from app.core.metrics import critical_data_path_errors_total

    critical_data_path_errors_total.labels(endpoint=endpoint, error_type="db_error").inc()
    raise HTTPException(
        status_code=503,
        detail=(
            f"{label} nicht verfuegbar — Datenbank-/Schemafehler: {exc.__class__.__name__}"
        ),
    ) from exc
