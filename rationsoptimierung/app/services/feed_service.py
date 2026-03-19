"""
Feed service for managing feed ingredients
"""
from typing import List, Dict, Optional
import os
from ..schemas.feed import FeedIngredient, FeedGroup
from ..domain.enums import FeedGroup as DomainFeedGroup
from ..optimization.solver import OptimizationService
from ..utils.dlg_merged_csv import load_merged_feed_ingredients
import logging

logger = logging.getLogger(__name__)

class FeedService:
    """Service for managing feed ingredients"""
    
    def __init__(self):
        # In-memory storage for feeds (would be replaced with database in production)
        # Structure: {tenant_id: {feed_id: FeedIngredient}}
        self._feeds: Dict[str, Dict[str, FeedIngredient]] = {}
        self._initialize_sample_feeds()
        self._initialize_dlg_merged_feeds_optional()
    
    def _initialize_sample_feeds(self):
        """Initialize with sample feed data for MVP"""
        # For simplicity, we'll store sample data under a "default" tenant
        # In a real implementation, this would come from a database or configuration service
        sample_feeds = [
            FeedIngredient(
                id="grassilage",
                name="Grassilage",
                group=FeedGroup.FORAGE,
                dm_frac=0.35,
                price_eur_kgdm=0.15,
                me_mj_kgdm=10.5,
                sidp_g_kgdm=180,
                andfom_g_kgdm=450,
                starch_g_kgdm=20,
                sugar_g_kgdm=15,
                fat_g_kgdm=30,
                ca_g_kgdm=6,
                p_g_kgdm=3,
                na_g_kgdm=1,
                min_kgdm=0.0,
                max_kgdm=15.0,
                active=True
            ),
            FeedIngredient(
                id="maissilage",
                name="Maissilage",
                group=FeedGroup.FORAGE,
                dm_frac=0.35,
                price_eur_kgdm=0.12,
                me_mj_kgdm=11.0,
                sidp_g_kgdm=80,
                andfom_g_kgdm=220,
                starch_g_kgdm=350,
                sugar_g_kgdm=20,
                fat_g_kgdm=25,
                ca_g_kgdm=2,
                p_g_kgdm=2,
                na_g_kgdm=1,
                min_kgdm=0.0,
                max_kgdm=10.0,
                active=True
            ),
            FeedIngredient(
                id="kartoffelpulpe",
                name="Kartoffelpülpe",
                group=FeedGroup.CONCENTRATE,
                dm_frac=0.12,
                price_eur_kgdm=0.08,
                me_mj_kgdm=12.5,
                sidp_g_kgdm=60,
                andfom_g_kgdm=100,
                starch_g_kgdm=200,
                sugar_g_kgdm=300,
                fat_g_kgdm=10,
                ca_g_kgdm=1,
                p_g_kgdm=1,
                na_g_kgdm=1,
                min_kgdm=0.0,
                max_kgdm=5.0,
                active=True
            ),
            FeedIngredient(
                id="weizen",
                name="Weizen",
                group=FeedGroup.CONCENTRATE,
                dm_frac=0.88,
                price_eur_kgdm=0.20,
                me_mj_kgdm=13.0,
                sidp_g_kgdm=110,
                andfom_g_kgdm=25,
                starch_g_kgdm=600,
                sugar_g_kgdm=20,
                fat_g_kgdm=20,
                ca_g_kgdm=0.5,
                p_g_kgdm=3.5,
                na_g_kgdm=0.5,
                min_kgdm=0.0,
                max_kgdm=3.0,
                active=True
            ),
            FeedIngredient(
                id="sojaschrot",
                name="Sojaschrot NON GMO",
                group=FeedGroup.PROTEIN,
                dm_frac=0.88,
                price_eur_kgdm=0.45,
                me_mj_kgdm=12.0,
                sidp_g_kgdm=380,
                andfom_g_kgdm=120,
                starch_g_kgdm=30,
                sugar_g_kgdm=10,
                fat_g_kgdm=20,
                ca_g_kgdm=3,
                p_g_kgdm=6,
                na_g_kgdm=0.5,
                min_kgdm=0.0,
                max_kgdm=4.0,
                active=True
            ),
            FeedIngredient(
                id="mineralfutter",
                name="Mineralfutter",
                group=FeedGroup.MINERAL,
                dm_frac=0.90,
                price_eur_kgdm=0.50,
                me_mj_kgdm=0.0,
                sidp_g_kgdm=0,
                andfom_g_kgdm=0,
                starch_g_kgdm=0,
                sugar_g_kgdm=0,
                fat_g_kgdm=0,
                ca_g_kgdm=250,
                p_g_kgdm=120,
                na_g_kgdm=100,
                min_kgdm=0.1,
                max_kgdm=0.5,
                active=True
            ),
            FeedIngredient(
                id="futterkalk",
                name="Futterkalk",
                group=FeedGroup.MINERAL,
                dm_frac=0.95,
                price_eur_kgdm=0.10,
                me_mj_kgdm=0.0,
                sidp_g_kgdm=0,
                andfom_g_kgdm=0,
                starch_g_kgdm=0,
                sugar_g_kgdm=0,
                fat_g_kgdm=0,
                ca_g_kgdm=380,
                p_g_kgdm=0,
                na_g_kgdm=0,
                min_kgdm=0.0,
                max_kgdm=0.3,
                active=True
            ),
            FeedIngredient(
                id="nacl",
                name="NaCl",
                group=FeedGroup.MINERAL,
                dm_frac=1.00,
                price_eur_kgdm=0.15,
                me_mj_kgdm=0.0,
                sidp_g_kgdm=0,
                andfom_g_kgdm=0,
                starch_g_kgdm=0,
                sugar_g_kgdm=0,
                fat_g_kgdm=0,
                ca_g_kgdm=0,
                p_g_kgdm=0,
                na_g_kgdm=393,
                min_kgdm=0.0,
                max_kgdm=0.1,
                active=True
            )
        ]
        
        # Initialize with default tenant
        default_tenant = "default"
        self._feeds[default_tenant] = {}
        for feed in sample_feeds:
            self._feeds[default_tenant][feed.id] = feed
        
        logger.info(f"Initialized {len(self._feeds[default_tenant])} sample feed ingredients for tenant '{default_tenant}'")

    def _initialize_dlg_merged_feeds_optional(self) -> None:
        """
        Optional: load DLG/LKV-merged feeds from `data/reference/dlg_merged_feeds_lp.csv`
        into a dedicated tenant (default: `dlg`), so the normal demo tenant stays stable.

        Env:
          - RATIONS_DLG_MERGED_TENANT_ID (default: "dlg")
          - RATIONS_DLG_MERGED_ENABLE ("1"/"true"/"yes" to enable; default disabled)
        """
        enable = os.getenv("RATIONS_DLG_MERGED_ENABLE", "").strip().lower() in ("1", "true", "yes")
        if not enable:
            return

        tenant_id = os.getenv("RATIONS_DLG_MERGED_TENANT_ID", "dlg").strip() or "dlg"
        try:
            feeds = load_merged_feed_ingredients()
        except FileNotFoundError:
            logger.warning(
                "DLG merged feeds enabled but merged CSV missing; skipping tenant '%s'",
                tenant_id,
            )
            return
        except Exception as e:
            logger.exception(
                "Failed to load DLG merged feeds for tenant '%s': %s",
                tenant_id,
                str(e),
            )
            return

        self._feeds[tenant_id] = {f.id: f for f in feeds}
        logger.info(
            "Initialized %s merged feed ingredients for tenant '%s'",
            len(self._feeds[tenant_id]),
            tenant_id,
        )

    def _ensure_tenant_loaded(self, tenant_id: str) -> None:
        """
        Lazy-load optional tenants after app import.

        This enables test/ops scenarios where env vars are set after the module-level
        FeedService instance has already been constructed.
        """
        if tenant_id in self._feeds:
            return
        enable = os.getenv("RATIONS_DLG_MERGED_ENABLE", "").strip().lower() in ("1", "true", "yes")
        if not enable:
            return
        configured = os.getenv("RATIONS_DLG_MERGED_TENANT_ID", "dlg").strip() or "dlg"
        if tenant_id != configured:
            return
        try:
            feeds = load_merged_feed_ingredients()
        except Exception as e:
            logger.exception("Lazy load failed for tenant '%s': %s", tenant_id, str(e))
            return
        self._feeds[tenant_id] = {f.id: f for f in feeds}
        logger.info("Lazy-loaded %s merged feeds for tenant '%s'", len(feeds), tenant_id)
    
    def get_all_feeds(self, tenant_id: str = "default", active_only: bool = True) -> List[FeedIngredient]:
        """
        Get all feed ingredients for a tenant
        
        Args:
            tenant_id: Tenant identifier
            active_only: If True, return only active feeds
            
        Returns:
            List of feed ingredients
        """
        self._ensure_tenant_loaded(tenant_id)
        feeds = list(self._feeds.get(tenant_id, {}).values())
        if active_only:
            feeds = [f for f in feeds if f.active]
        return feeds
    
    def get_feed_by_id(self, feed_id: str, tenant_id: str = "default") -> Optional[FeedIngredient]:
        """
        Get a feed ingredient by ID for a specific tenant
        
        Args:
            feed_id: ID of the feed ingredient
            tenant_id: Tenant identifier
            
        Returns:
            Feed ingredient if found, None otherwise
        """
        self._ensure_tenant_loaded(tenant_id)
        return self._feeds.get(tenant_id, {}).get(feed_id)
    
    def get_feeds_by_group(self, group: FeedGroup, tenant_id: str = "default") -> List[FeedIngredient]:
        """
        Get feed ingredients by group for a specific tenant
        
        Args:
            group: Feed group to filter by
            tenant_id: Tenant identifier
            
        Returns:
            List of feed ingredients in the specified group
        """
        self._ensure_tenant_loaded(tenant_id)
        feeds = self._feeds.get(tenant_id, {}).values()
        return [f for f in feeds if f.group == group and f.active]
    
    def add_feed(self, feed: FeedIngredient, tenant_id: str = "default") -> FeedIngredient:
        """
        Add a new feed ingredient
        
        Args:
            feed: Feed ingredient to add
            tenant_id: Tenant identifier (default: "default")
            
        Returns:
            The added feed ingredient
            
        Raises:
            ValueError: If a feed with the same ID already exists
        """
        if tenant_id not in self._feeds:
            self._feeds[tenant_id] = {}
        if feed.id in self._feeds[tenant_id]:
            raise ValueError(f"Feed with ID '{feed.id}' already exists")
        
        self._feeds[tenant_id][feed.id] = feed
        logger.info(f"Added feed: {feed.name} (ID: {feed.id})")
        return feed
    
    def update_feed(self, feed_id: str, feed: FeedIngredient, tenant_id: str = "default") -> FeedIngredient:
        """
        Update an existing feed ingredient
        
        Args:
            feed_id: ID of the feed to update
            feed: Updated feed ingredient data
            tenant_id: Tenant identifier (default: "default")
            
        Returns:
            The updated feed ingredient
            
        Raises:
            ValueError: If no feed with the given ID exists
        """
        if feed_id not in self._feeds.get(tenant_id, {}):
            raise ValueError(f"No feed found with ID '{feed_id}'")
        
        # Ensure the ID matches
        if feed.id != feed_id:
            raise ValueError("Feed ID cannot be changed")
        
        self._feeds[tenant_id][feed_id] = feed
        logger.info(f"Updated feed: {feed.name} (ID: {feed.id})")
        return feed
    
    def delete_feed(self, feed_id: str, tenant_id: str = "default") -> bool:
        """
        Delete a feed ingredient
        
        Args:
            feed_id: ID of the feed to delete
            tenant_id: Tenant identifier (default: "default")
            
        Returns:
            True if deleted, False if not found
        """
        tenant_feeds = self._feeds.get(tenant_id, {})
        if feed_id in tenant_feeds:
            del tenant_feeds[feed_id]
            logger.info(f"Deleted feed with ID: {feed_id}")
            return True
        return False
    
    def validate_feeds(self, feeds: List[FeedIngredient]) -> List[str]:
        """
        Validate a list of feed ingredients
        
        Args:
            feeds: List of feed ingredients to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        # Use the optimization service for validation
        optimization_service = OptimizationService()
        return optimization_service.validate_feeds(feeds)