"""Client für fibu-core."""

from __future__ import annotations

from typing import Any, Dict, List

from app.clients.base import BaseServiceClient


class FibuCoreClient(BaseServiceClient):
    async def list_journal_entries(self, tenant: str) -> List[Dict[str, Any]]:
        data = await self._request(
            "GET",
            "/api/v1/journal-entries",
            headers={"X-Tenant-ID": tenant},
        )
        return self._extract_items(data)

    async def create_journal_entry(self, tenant: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request(
            "POST",
            "/api/v1/journal-entries",
            headers={"X-Tenant-ID": tenant},
            json=payload,
        )

