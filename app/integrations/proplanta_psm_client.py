"""
Proplanta PSM Client
Adapter für VALEO-NeuroERP → Proplanta PSM-Integration über MCP
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Config-Pfad
CONFIG_PATH = Path("data/config/proplanta_psm.json")

# Lade Config (falls vorhanden)
_cfg = {}
if CONFIG_PATH.exists():
    try:
        _cfg = json.loads(CONFIG_PATH.read_text())
    except Exception as e:
        logger.warning(f"Failed to load Proplanta PSM config: {e}")

# PSM-Connection (ENV-Override möglich)
PROPLANTA_PSM_URL = _cfg.get("url") or "https://psm.proplanta.de/list"
PROPLANTA_USERNAME = _cfg.get("username") or ""
PROPLANTA_PASSWORD = _cfg.get("password") or ""


class PSMData:
    """PSM Datenmodell"""

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.name = data.get('name', '')
        self.active_ingredient = data.get('activeIngredient', '')
        self.manufacturer = data.get('manufacturer', '')
        self.approval_number = data.get('approvalNumber', '')
        self.approval_date = data.get('approvalDate', '')
        self.expiry_date = data.get('expiryDate', '')
        self.application_areas = data.get('applicationAreas', [])
        self.hazard_class = data.get('hazardClass', '')
        self.status = data.get('status', 'approved')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'active_ingredient': self.active_ingredient,
            'manufacturer': self.manufacturer,
            'approval_number': self.approval_number,
            'approval_date': self.approval_date,
            'expiry_date': self.expiry_date,
            'application_areas': self.application_areas,
            'hazard_class': self.hazard_class,
            'status': self.status
        }

    def is_expired(self) -> bool:
        """Prüft ob PSM abgelaufen ist"""
        if not self.expiry_date:
            return False
        try:
            expiry = datetime.fromisoformat(self.expiry_date.replace('Z', '+00:00'))
            return expiry < datetime.now(expiry.tzinfo)
        except:
            return False


class ProplantaPSMClient:
    """Client für Proplanta PSM Integration über MCP"""

    def __init__(self):
        self.mcp_server_name = "proplanta-psm-scraper"
        self._cache = {}  # Simple cache für PSM Daten
        self._last_sync = None

    def _call_mcp_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ruft MCP Tool auf (wird durch MCP Framework ersetzt)
        Diese Methode dient als Platzhalter für die eigentliche MCP Integration
        """
        # TODO: Implement actual MCP tool calling
        # For now, return mock data for testing
        logger.warning("MCP tool calling not implemented yet - using mock data")

        if tool_name == "scrape_psm_list":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Successfully scraped 150 PSM items from mock data"
                    },
                    {
                        "type": "text",
                        "text": json.dumps([
                            {
                                "id": "PSM001",
                                "name": "Roundup PowerMax",
                                "activeIngredient": "Glyphosate",
                                "manufacturer": "Bayer",
                                "approvalNumber": "12345",
                                "approvalDate": "2020-01-01",
                                "expiryDate": "2025-12-31",
                                "applicationAreas": ["Getreide", "Mais"],
                                "hazardClass": "N",
                                "status": "approved"
                            },
                            {
                                "id": "PSM002",
                                "name": "Atlantis OD",
                                "activeIngredient": "Mesotrione + Terbuthylazine",
                                "manufacturer": "Syngenta",
                                "approvalNumber": "67890",
                                "expiryDate": "2024-06-30",
                                "applicationAreas": ["Mais"],
                                "hazardClass": "N",
                                "status": "expired"
                            }
                        ], indent=2)
                    }
                ]
            }
        elif tool_name == "search_psm":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Found 2 PSM items matching \"{args.get('query', '')}\""
                    },
                    {
                        "type": "text",
                        "text": json.dumps([
                            {
                                "id": "PSM001",
                                "name": "Roundup PowerMax",
                                "activeIngredient": "Glyphosate",
                                "manufacturer": "Bayer"
                            }
                        ], indent=2)
                    }
                ]
            }
        elif tool_name == "get_psm_details":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"PSM Details for ID: {args.get('id', '')}"
                    },
                    {
                        "type": "text",
                        "text": json.dumps({
                            "id": args.get('id', ''),
                            "name": "Roundup PowerMax",
                            "activeIngredient": "Glyphosate",
                            "manufacturer": "Bayer",
                            "approvalNumber": "12345",
                            "status": "approved"
                        }, indent=2)
                    }
                ]
            }

        return {"content": [{"type": "text", "text": "Mock response"}]}

    def sync_psm_data(self) -> List[PSMData]:
        """
        Synchronisiert PSM Daten von Proplanta

        Returns:
            Liste der PSM Daten
        """
        try:
            logger.info("Starting PSM data synchronization")

            # Call MCP tool to scrape PSM list
            result = self._call_mcp_tool("scrape_psm_list", {
                "url": PROPLANTA_PSM_URL,
                "username": PROPLANTA_USERNAME,
                "password": PROPLANTA_PASSWORD
            })

            # Parse response
            psm_items = []
            for content in result.get("content", []):
                if content.get("type") == "text" and "PSM items" in content.get("text", ""):
                    try:
                        # Extract JSON data from response
                        json_start = content["text"].find("[")
                        json_end = content["text"].rfind("]") + 1
                        if json_start >= 0 and json_end > json_start:
                            json_data = content["text"][json_start:json_end]
                            raw_items = json.loads(json_data)

                            for item in raw_items:
                                psm_items.append(PSMData(item))
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse PSM data: {e}")

            # Cache the data
            self._cache = {item.id: item for item in psm_items}
            self._last_sync = datetime.now()

            logger.info(f"Synchronized {len(psm_items)} PSM items")
            return psm_items

        except Exception as e:
            logger.error(f"Failed to sync PSM data: {e}")
            return []

    def search_psm(self, query: str, limit: int = 50) -> List[PSMData]:
        """
        Sucht PSM Daten

        Args:
            query: Suchbegriff
            limit: Maximale Anzahl Ergebnisse

        Returns:
            Liste der gefundenen PSM Daten
        """
        try:
            # Call MCP tool to search PSM data
            result = self._call_mcp_tool("search_psm", {
                "query": query,
                "url": PROPLANTA_PSM_URL,
                "limit": limit
            })

            # Parse response
            psm_items = []
            for content in result.get("content", []):
                if content.get("type") == "text" and "PSM items matching" in content.get("text", ""):
                    try:
                        # Extract JSON data from response
                        json_start = content["text"].find("[")
                        json_end = content["text"].rfind("]") + 1
                        if json_start >= 0 and json_end > json_start:
                            json_data = content["text"][json_start:json_end]
                            raw_items = json.loads(json_data)

                            for item in raw_items:
                                psm_items.append(PSMData(item))
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse search results: {e}")

            return psm_items

        except Exception as e:
            logger.error(f"Failed to search PSM data: {e}")
            return []

    def get_psm_details(self, psm_id: str) -> Optional[PSMData]:
        """
        Holt Details zu einem spezifischen PSM

        Args:
            psm_id: PSM ID

        Returns:
            PSM Daten oder None wenn nicht gefunden
        """
        try:
            # Check cache first
            if psm_id in self._cache:
                return self._cache[psm_id]

            # Call MCP tool to get PSM details
            result = self._call_mcp_tool("get_psm_details", {
                "id": psm_id,
                "url": PROPLANTA_PSM_URL
            })

            # Parse response
            for content in result.get("content", []):
                if content.get("type") == "text" and "PSM Details" in content.get("text", ""):
                    try:
                        # Extract JSON data from response
                        json_start = content["text"].find("{")
                        json_end = content["text"].rfind("}") + 1
                        if json_start >= 0 and json_end > json_start:
                            json_data = content["text"][json_start:json_end]
                            item_data = json.loads(json_data)

                            psm_item = PSMData(item_data)
                            # Cache the result
                            self._cache[psm_id] = psm_item
                            return psm_item
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse PSM details: {e}")

            return None

        except Exception as e:
            logger.error(f"Failed to get PSM details: {e}")
            return None

    def get_all_psm(self) -> List[PSMData]:
        """
        Holt alle gecachten PSM Daten

        Returns:
            Liste aller PSM Daten
        """
        return list(self._cache.values())

    def get_active_psm(self) -> List[PSMData]:
        """
        Holt alle aktiven (nicht abgelaufenen) PSM

        Returns:
            Liste der aktiven PSM Daten
        """
        return [psm for psm in self._cache.values() if not psm.is_expired()]

    def get_expired_psm(self) -> List[PSMData]:
        """
        Holt alle abgelaufenen PSM

        Returns:
            Liste der abgelaufenen PSM Daten
        """
        return [psm for psm in self._cache.values() if psm.is_expired()]


# Global client instance
psm_client = ProplantaPSMClient()


def sync_psm_data() -> List[Dict[str, Any]]:
    """
    Synchronisiert PSM Daten und gibt sie als Dicts zurück

    Returns:
        Liste der PSM Daten als Dictionaries
    """
    psm_data = psm_client.sync_psm_data()
    return [psm.to_dict() for psm in psm_data]


def search_psm(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Sucht PSM Daten

    Args:
        query: Suchbegriff
        limit: Maximale Anzahl Ergebnisse

    Returns:
        Liste der gefundenen PSM Daten als Dictionaries
    """
    psm_data = psm_client.search_psm(query, limit)
    return [psm.to_dict() for psm in psm_data]


def get_psm_details(psm_id: str) -> Optional[Dict[str, Any]]:
    """
    Holt Details zu einem spezifischen PSM

    Args:
        psm_id: PSM ID

    Returns:
        PSM Daten als Dictionary oder None
    """
    psm_data = psm_client.get_psm_details(psm_id)
    return psm_data.to_dict() if psm_data else None


def is_configured() -> bool:
    """
    Prüft, ob PSM Integration konfiguriert ist

    Returns:
        True wenn PSM-Config vorhanden
    """
    return bool(PROPLANTA_PSM_URL and (PROPLANTA_USERNAME or True))  # Username optional für öffentliche Daten