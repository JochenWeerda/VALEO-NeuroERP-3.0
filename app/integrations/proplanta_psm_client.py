"""
Proplanta PSM Client
Adapter fuer VALEO-NeuroERP -> Proplanta PSM-Integration ueber einen expliziten Tool-Contract.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("data/config/proplanta_psm.json")


class ProplantaPSMContractError(RuntimeError):
    pass


ToolCaller = Callable[[str, Dict[str, Any]], Dict[str, Any]]


def _load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProplantaPSMContractError(f"Proplanta-Config enthaelt ungueltiges JSON: {CONFIG_PATH}") from exc
    if not isinstance(data, dict):
        raise ProplantaPSMContractError(f"Proplanta-Config muss ein JSON-Objekt sein: {CONFIG_PATH}")
    return data


_cfg = _load_config()

PROPLANTA_PSM_URL = os.getenv("PROPLANTA_PSM_URL") or _cfg.get("url") or ""
PROPLANTA_USERNAME = os.getenv("PROPLANTA_PSM_USERNAME") or _cfg.get("username") or ""
PROPLANTA_PASSWORD = os.getenv("PROPLANTA_PSM_PASSWORD") or _cfg.get("password") or ""
PROPLANTA_MCP_SERVER_NAME = os.getenv("PROPLANTA_PSM_MCP_SERVER") or _cfg.get("mcp_server_name") or ""


class PSMData:
    """PSM Datenmodell."""

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.active_ingredient = data.get("activeIngredient", "")
        self.manufacturer = data.get("manufacturer", "")
        self.approval_number = data.get("approvalNumber", "")
        self.approval_date = data.get("approvalDate", "")
        self.expiry_date = data.get("expiryDate", "")
        self.application_areas = data.get("applicationAreas", [])
        self.hazard_class = data.get("hazardClass", "")
        self.status = data.get("status", "approved")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "active_ingredient": self.active_ingredient,
            "manufacturer": self.manufacturer,
            "approval_number": self.approval_number,
            "approval_date": self.approval_date,
            "expiry_date": self.expiry_date,
            "application_areas": self.application_areas,
            "hazard_class": self.hazard_class,
            "status": self.status,
        }

    def is_expired(self) -> bool:
        if not self.expiry_date:
            return False
        try:
            expiry = datetime.fromisoformat(self.expiry_date.replace("Z", "+00:00"))
            return expiry < datetime.now(expiry.tzinfo)
        except ValueError:
            return False


class ProplantaPSMClient:
    """Client fuer Proplanta PSM Integration ueber einen injizierten Tool-Caller."""

    def __init__(self, tool_caller: ToolCaller | None = None):
        self.mcp_server_name = PROPLANTA_MCP_SERVER_NAME
        self._tool_caller = tool_caller
        self._cache: dict[str, PSMData] = {}
        self._last_sync: datetime | None = None

    def is_ready(self) -> bool:
        return bool(PROPLANTA_PSM_URL and self.mcp_server_name and self._tool_caller)

    def set_tool_caller(self, tool_caller: ToolCaller) -> None:
        self._tool_caller = tool_caller

    def _call_mcp_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self._tool_caller:
            raise ProplantaPSMContractError(
                "Proplanta-MCP-Transport ist nicht angebunden. Tool-Aufrufe duerfen nicht auf Mock-Daten fallen."
            )
        try:
            response = self._tool_caller(tool_name, args)
        except Exception as exc:  # pragma: no cover - defensive transport boundary
            raise ProplantaPSMContractError(f"MCP-Tool-Aufruf fehlgeschlagen: {tool_name}") from exc
        if not isinstance(response, dict):
            raise ProplantaPSMContractError(f"MCP-Tool-Antwort muss ein Objekt sein: {tool_name}")
        return response

    @staticmethod
    def _extract_text_entries(result: Dict[str, Any]) -> list[str]:
        content = result.get("content")
        if not isinstance(content, list):
            raise ProplantaPSMContractError("MCP-Tool-Antwort verletzt Contract: 'content' muss eine Liste sein.")
        return [entry.get("text", "") for entry in content if isinstance(entry, dict) and entry.get("type") == "text"]

    def _parse_item_list(self, result: Dict[str, Any]) -> list[PSMData]:
        for text in self._extract_text_entries(result):
            json_start = text.find("[")
            json_end = text.rfind("]") + 1
            if json_start < 0 or json_end <= json_start:
                continue
            try:
                raw_items = json.loads(text[json_start:json_end])
            except json.JSONDecodeError as exc:
                raise ProplantaPSMContractError("MCP-Tool-Antwort enthaelt ungueltige PSM-JSON-Liste.") from exc
            if not isinstance(raw_items, list):
                raise ProplantaPSMContractError("PSM-JSON-Liste muss eine Liste enthalten.")
            return [PSMData(item) for item in raw_items if isinstance(item, dict)]
        return []

    def _parse_item_details(self, result: Dict[str, Any]) -> Optional[PSMData]:
        for text in self._extract_text_entries(result):
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            if json_start < 0 or json_end <= json_start:
                continue
            try:
                item_data = json.loads(text[json_start:json_end])
            except json.JSONDecodeError as exc:
                raise ProplantaPSMContractError("MCP-Tool-Antwort enthaelt ungueltige PSM-Details.") from exc
            if not isinstance(item_data, dict):
                raise ProplantaPSMContractError("PSM-Details muessen ein Objekt sein.")
            return PSMData(item_data)
        return None

    def sync_psm_data(self) -> List[PSMData]:
        if not self.is_ready():
            raise ProplantaPSMContractError("Proplanta-PSM-Integration ist nicht vollstaendig konfiguriert.")
        logger.info("Starting PSM data synchronization")
        result = self._call_mcp_tool(
            "scrape_psm_list",
            {
                "url": PROPLANTA_PSM_URL,
                "username": PROPLANTA_USERNAME,
                "password": PROPLANTA_PASSWORD,
            },
        )
        psm_items = self._parse_item_list(result)
        self._cache = {item.id: item for item in psm_items if item.id}
        self._last_sync = datetime.now()
        logger.info("Synchronized %s PSM items", len(psm_items))
        return psm_items

    def search_psm(self, query: str, limit: int = 50) -> List[PSMData]:
        if not self.is_ready():
            raise ProplantaPSMContractError("Proplanta-PSM-Integration ist nicht vollstaendig konfiguriert.")
        result = self._call_mcp_tool(
            "search_psm",
            {
                "query": query,
                "url": PROPLANTA_PSM_URL,
                "limit": limit,
            },
        )
        return self._parse_item_list(result)

    def get_psm_details(self, psm_id: str) -> Optional[PSMData]:
        if psm_id in self._cache:
            return self._cache[psm_id]
        if not self.is_ready():
            raise ProplantaPSMContractError("Proplanta-PSM-Integration ist nicht vollstaendig konfiguriert.")
        result = self._call_mcp_tool(
            "get_psm_details",
            {
                "id": psm_id,
                "url": PROPLANTA_PSM_URL,
            },
        )
        item = self._parse_item_details(result)
        if item and item.id:
            self._cache[item.id] = item
        return item

    def get_all_psm(self) -> List[PSMData]:
        return list(self._cache.values())

    def get_active_psm(self) -> List[PSMData]:
        return [psm for psm in self._cache.values() if not psm.is_expired()]

    def get_expired_psm(self) -> List[PSMData]:
        return [psm for psm in self._cache.values() if psm.is_expired()]


psm_client = ProplantaPSMClient()


def sync_psm_data() -> List[Dict[str, Any]]:
    return [psm.to_dict() for psm in psm_client.sync_psm_data()]


def search_psm(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    return [psm.to_dict() for psm in psm_client.search_psm(query, limit)]


def get_psm_details(psm_id: str) -> Optional[Dict[str, Any]]:
    psm_data = psm_client.get_psm_details(psm_id)
    return psm_data.to_dict() if psm_data else None


def is_configured() -> bool:
    return psm_client.is_ready()
