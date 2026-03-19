from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import List, Optional
from ...schemas.feed import FeedIngredient, FeedGroup
from ...services.feed_service import FeedService
from ...schemas.common import BaseResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
feed_service = FeedService()

def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> str:
    """Extract tenant ID from header, default to 'default'"""
    return x_tenant_id if x_tenant_id else "default"

@router.get("/feeds", response_model=List[FeedIngredient])
async def get_feeds(
    active_only: bool = Query(True, description="Return only active feeds"),
    group: Optional[FeedGroup] = Query(None, description="Filter by feed group"),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get all available feed ingredients for a tenant
    """
    logger.debug(f"Getting feeds for tenant {tenant_id} (active_only={active_only}, group={group})")
    
    if group:
        feeds = feed_service.get_feeds_by_group(group, tenant_id)
    else:
        feeds = feed_service.get_all_feeds(tenant_id, active_only=active_only)
    
    return feeds

@router.get("/feeds/{feed_id}", response_model=FeedIngredient)
async def get_feed(feed_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get a specific feed ingredient by ID for a tenant
    """
    logger.debug(f"Getting feed with ID: {feed_id} for tenant {tenant_id}")
    
    feed = feed_service.get_feed_by_id(feed_id, tenant_id)
    if not feed:
        raise HTTPException(status_code=404, detail=f"Feed with ID '{feed_id}' not found for tenant '{tenant_id}'")
    
    return feed

@router.post("/feeds/validate", response_model=BaseResponse)
async def validate_feeds(feeds: List[FeedIngredient]):
    """
    Validate a list of feed ingredients
    """
    logger.debug(f"Validating {len(feeds)} feed ingredients")
    
    errors = feed_service.validate_feeds(feeds)
    
    if errors:
        return BaseResponse(
            success=False,
            message="Validation failed",
            # In a real implementation, we'd include the errors in the response
            # but for simplicity we're just returning success=False
        )
    
    return BaseResponse(
        success=True,
        message="All feeds are valid"
    )

@router.post("/feeds", response_model=FeedIngredient)
async def create_feed(feed: FeedIngredient, tenant_id: str = Depends(get_tenant_id)):
    """
    Create a new feed ingredient
    """
    logger.debug(f"Creating feed: {feed.name}")
    
    try:
        return feed_service.add_feed(feed, tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/feeds/{feed_id}", response_model=FeedIngredient)
async def update_feed(feed_id: str, feed: FeedIngredient, tenant_id: str = Depends(get_tenant_id)):
    """
    Update an existing feed ingredient
    """
    logger.debug(f"Updating feed with ID: {feed_id}")
    
    if feed.id != feed_id:
        raise HTTPException(status_code=400, detail="Feed ID in path and body must match")
    
    try:
        return feed_service.update_feed(feed_id, feed, tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/feeds/{feed_id}", response_model=BaseResponse)
async def delete_feed(feed_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Delete a feed ingredient
    """
    logger.debug(f"Deleting feed with ID: {feed_id}")
    
    success = feed_service.delete_feed(feed_id, tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Feed with ID '{feed_id}' not found")
    
    return BaseResponse(
        success=True,
        message=f"Feed with ID '{feed_id}' deleted successfully"
    )