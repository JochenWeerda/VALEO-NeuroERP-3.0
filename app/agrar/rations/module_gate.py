"""Router-Gate fuer das Modul-Flag `feeding_advisory` (FEED-REL-047).

Die Feeding-Subrouter (Prefix /feeding) haengen an diesem Gate: ist das Modul
fuer den Tenant nicht aktiviert (TENANT_MODULE_FLAGS), antworten alle Routen
mit 404 und klarer Meldung — Portal-Kacheln blenden ueber /modules aus.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException

from app.core.module_registry import registry
from app.core.tenant import get_tenant_id
from modules.bootstrap import initialize_module_registry

FEEDING_MODULE = "feeding_advisory"


async def require_feeding_advisory(tenant_id: str = Depends(get_tenant_id)) -> None:
    initialize_module_registry()
    if not registry.is_enabled(FEEDING_MODULE, tenant_id=tenant_id):
        raise HTTPException(
            status_code=404,
            detail=(f"Modul {FEEDING_MODULE} ist fuer diesen Mandanten nicht aktiviert. "
                    "Aktivierung erfolgt ueber die Modulverwaltung (TENANT_MODULE_FLAGS)."),
        )
