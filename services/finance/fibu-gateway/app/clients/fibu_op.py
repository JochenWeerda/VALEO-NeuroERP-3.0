"""Client für fibu-op."""

from __future__ import annotations

from typing import Any, Dict, List

from app.clients.base import BaseServiceClient


class FibuOpClient(BaseServiceClient):
    async def list_open_items(self, tenant: str, debtor: str | None = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if debtor:
            params["debtor"] = debtor
        data = await self._request(
            "GET",
            "/api/v1/open-items",
            headers={"X-Tenant-ID": tenant},
            params=params,
        )
        return self._extract_items(data)

