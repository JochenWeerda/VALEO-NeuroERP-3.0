"""Client für fibu-master-data."""

from __future__ import annotations

from typing import Any, Dict, List

from app.clients.base import BaseServiceClient


class FibuMasterDataClient(BaseServiceClient):
    async def list_chart_of_accounts(self, tenant: str) -> List[Dict[str, Any]]:
        data = await self._request(
            "GET",
            "/api/v1/chart-of-accounts",
            headers={"X-Tenant-ID": tenant},
        )
        return self._extract_items(data)

