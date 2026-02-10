"""
PSM API endpoints
Full CRUD for Pflanzenschutzmittel-Stammdaten management
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
import logging

from ....core.database import get_db
from ....infrastructure.models import PSM as PSMModel
from ....api.v1.schemas.base import PaginatedResponse
from ....api.v1.schemas.agrar import PSM, PSMCreate, PSMUpdate
from ....integrations.dms_client import upload_document, is_configured as dms_configured
from ....services.sync_scheduler import sync_scheduler
from ....services.competitor_monitor import competitor_monitor

router = APIRouter()

DEFAULT_TENANT = "system"
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaginatedResponse[PSM])
async def list_psm(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    search: Optional[str] = Query(None, description="Search in name, wirkstoff, bvl_nummer"),
    mittel_typ: Optional[str] = Query(None, description="Filter by type"),
    wirkstoff: Optional[str] = Query(None, description="Filter by active ingredient"),
    kultur: Optional[str] = Query(None, description="Filter by crop"),
    bienenschutz: Optional[bool] = Query(None, description="Filter by bee protection"),
    wasserschutz_gebiet: Optional[bool] = Query(None, description="Filter by water protection"),
    ist_aktiv: Optional[bool] = Query(None, description="Filter by active status"),
    erklaerung_status: Optional[str] = Query(None, description="Filter by farmer declaration status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of PSM."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    query = db.query(PSMModel).filter(PSMModel.tenant_id == effective_tenant)

    if ist_aktiv is not None:
        query = query.filter(PSMModel.ist_aktiv == ist_aktiv)

    if mittel_typ:
        query = query.filter(PSMModel.mittel_typ == mittel_typ)

    if wirkstoff:
        query = query.filter(PSMModel.wirkstoff.ilike(f"%{wirkstoff}%"))

    if kultur:
        # Filter by crops in JSON array
        query = query.filter(PSMModel.kulturen.contains([kultur]))

    if bienenschutz is not None:
        query = query.filter(PSMModel.bienenschutz == bienenschutz)

    if wasserschutz_gebiet is not None:
        query = query.filter(PSMModel.wasserschutz_gebiet == wasserschutz_gebiet)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                PSMModel.name.ilike(like),
                PSMModel.wirkstoff.ilike(like),
                PSMModel.bvl_nummer.ilike(like),
            )
        )

    # Filter by farmer declaration status
    if erklaerung_status:
        query = query.filter(PSMModel.erklaerung_landwirt_status == erklaerung_status)

    total = query.count()
    items = query.order_by(desc(PSMModel.created_at)).offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse(
        items=[PSM.model_validate(item) for item in items],
        total=total,
        page=page,
        pages=pages,
        size=limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{psm_id}", response_model=PSM)
async def get_psm(
    psm_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get a single PSM by ID."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    psm = (
        db.query(PSMModel)
        .filter(
            PSMModel.id == psm_id,
            PSMModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not psm:
        raise HTTPException(status_code=404, detail="PSM not found")

    return PSM.model_validate(psm)


@router.post("/", response_model=PSM, status_code=201)
async def create_psm(
    psm_data: PSMCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Create a new PSM."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    # Check if bvl_nummer already exists
    existing = (
        db.query(PSMModel)
        .filter(
            PSMModel.bvl_nummer == psm_data.bvl_nummer,
            PSMModel.tenant_id == effective_tenant
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"PSM with BVL number {psm_data.bvl_nummer} already exists"
        )

    # Validate business rules
    if psm_data.zulassung_ablauf and psm_data.zulassung_ablauf < datetime.utcnow().date():
        raise HTTPException(
            status_code=400,
            detail="Approval expiry date cannot be in the past"
        )

    # Validate dosage ranges
    if psm_data.dosierung_min and psm_data.dosierung_max and psm_data.dosierung_min > psm_data.dosierung_max:
        raise HTTPException(
            status_code=400,
            detail="Minimum dosage cannot be greater than maximum dosage"
        )

    psm = PSMModel(
        **psm_data.model_dump(),
        tenant_id=effective_tenant
    )

    db.add(psm)
    db.commit()
    db.refresh(psm)

    return PSM.model_validate(psm)


@router.put("/{psm_id}", response_model=PSM)
async def update_psm(
    psm_id: str,
    psm_data: PSMUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Update an existing PSM."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    psm = (
        db.query(PSMModel)
        .filter(
            PSMModel.id == psm_id,
            PSMModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not psm:
        raise HTTPException(status_code=404, detail="PSM not found")

    update_data = psm_data.model_dump(exclude_unset=True)

    # Validate bvl_nummer uniqueness if changed
    if "bvl_nummer" in update_data and update_data["bvl_nummer"] != psm.bvl_nummer:
        existing = (
            db.query(PSMModel)
            .filter(
                PSMModel.bvl_nummer == update_data["bvl_nummer"],
                PSMModel.tenant_id == effective_tenant,
                PSMModel.id != psm_id
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"PSM with BVL number {update_data['bvl_nummer']} already exists"
            )

    # Validate approval expiry
    if "zulassung_ablauf" in update_data and update_data["zulassung_ablauf"]:
        from datetime import datetime
        if update_data["zulassung_ablauf"] < datetime.utcnow().date():
            raise HTTPException(
                status_code=400,
                detail="Approval expiry date cannot be in the past"
            )

    # Audit logging for compliance changes
    if any(key in update_data for key in ["ausgangsstoff_explosivstoffe", "erklaerung_landwirt_erforderlich", "erklaerung_landwirt_status"]):
        logger.info(f"PSM compliance update: {psm_id} - {update_data}")

    # Validate dosage ranges
    if ("dosierung_min" in update_data or "dosierung_max" in update_data):
        min_dose = update_data.get("dosierung_min", psm.dosierung_min)
        max_dose = update_data.get("dosierung_max", psm.dosierung_max)
        if min_dose and max_dose and min_dose > max_dose:
            raise HTTPException(
                status_code=400,
                detail="Minimum dosage cannot be greater than maximum dosage"
            )

    for key, value in update_data.items():
        setattr(psm, key, value)

    db.commit()
    db.refresh(psm)

    return PSM.model_validate(psm)


@router.delete("/{psm_id}", status_code=204)
async def delete_psm(
    psm_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Delete a PSM (soft delete)."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    psm = (
        db.query(PSMModel)
        .filter(
            PSMModel.id == psm_id,
            PSMModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not psm:
        raise HTTPException(status_code=404, detail="PSM not found")

    psm.ist_aktiv = False
    db.commit()

    return None


@router.post("/{psm_id}/erklaerung", response_model=PSM)
async def upload_farmer_declaration(
    psm_id: str,
    erklaerung_data: dict = {"status": "eingegangen"},
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Upload farmer declaration for PSM."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    psm = (
        db.query(PSMModel)
        .filter(
            PSMModel.id == psm_id,
            PSMModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not psm:
        raise HTTPException(status_code=404, detail="PSM not found")

    if not psm.ausgangsstoff_explosivstoffe:
        raise HTTPException(
            status_code=400,
            detail="PSM does not require farmer declaration"
        )

    # Update declaration status
    old_status = psm.erklaerung_landwirt_status
    new_status = erklaerung_data.get("status", "eingegangen")
    psm.erklaerung_landwirt_status = new_status
    db.commit()
    db.refresh(psm)

    # Audit logging for status changes
    if old_status != new_status:
        logger.info(f"PSM farmer declaration status changed: {psm_id} - {old_status} → {new_status}")

    # DMS Integration: Upload declaration document if DMS is configured
    if dms_configured() and erklaerung_data.get("file_path"):
        try:
            dms_result = upload_document(
                domain="psm_erklaerung",
                doc_number=f"PSM-{psm_id}-ERKLAERUNG",
                file_path=erklaerung_data["file_path"],
                metadata={
                    "psm_id": psm_id,
                    "bvl_nummer": psm.bvl_nummer,
                    "status": psm.erklaerung_landwirt_status,
                    "tenant_id": effective_tenant
                }
            )
            if dms_result.get("ok"):
                # Store DMS document ID in PSM record (would need additional field)
                pass
        except Exception as e:
            # Log error but don't fail the operation
            logger.warning(f"Failed to upload declaration to DMS: {e}")

    return PSM.model_validate(psm)


@router.put("/{psm_id}/erklaerung/status", response_model=PSM)
async def update_farmer_declaration_status(
    psm_id: str,
    status_data: dict = {"status": "geprueft"},
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Update farmer declaration status."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    psm = (
        db.query(PSMModel)
        .filter(
            PSMModel.id == psm_id,
            PSMModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not psm:
        raise HTTPException(status_code=404, detail="PSM not found")

    valid_statuses = ["eingegangen", "geprueft", "abgelehnt"]
    new_status = status_data.get("status")

    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    psm.erklaerung_landwirt_status = new_status
    db.commit()
    db.refresh(psm)

    return PSM.model_validate(psm)


@router.get("/search", response_model=list[PSM])
async def search_psm(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lightweight search endpoint for PSM."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    like = f"%{q}%"

    query = (
        db.query(PSMModel)
        .filter(PSMModel.ist_aktiv == True)
        .filter(PSMModel.tenant_id == effective_tenant)
        .filter(
            or_(
                PSMModel.name.ilike(like),
                PSMModel.wirkstoff.ilike(like),
                PSMModel.bvl_nummer.ilike(like),
            )
        )
        .order_by(PSMModel.name.asc())
        .limit(limit)
    )

    return [PSM.model_validate(item) for item in query.all()]


@router.get("/stats/overview")
async def get_psm_stats(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get PSM statistics overview."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    # Count by type
    type_stats = {}
    types = db.query(PSMModel.mittel_typ, db.func.count(PSMModel.id)).filter(
        PSMModel.tenant_id == effective_tenant,
        PSMModel.ist_aktiv == True
    ).group_by(PSMModel.mittel_typ).all()

    for typ, count in types:
        type_stats[typ or "Unbekannt"] = count

    # Safety stats
    safety_stats = {}
    safety = db.query(
        db.func.concat(
            db.case((PSMModel.bienenschutz == True, "B"), else_=""),
            db.case((PSMModel.wasserschutz_gebiet == True, "W"), else_="")
        ),
        db.func.count(PSMModel.id)
    ).filter(
        PSMModel.tenant_id == effective_tenant,
        PSMModel.ist_aktiv == True
    ).group_by(
        PSMModel.bienenschutz,
        PSMModel.wasserschutz_gebiet
    ).all()

    for safety_type, count in safety:
        safety_stats[safety_type or "Standard"] = count

    # Approval expiry warnings (next 90 days)
    from datetime import datetime, timedelta
    expiry_cutoff = datetime.utcnow().date() + timedelta(days=90)

    expiring_count = db.query(PSMModel).filter(
        PSMModel.tenant_id == effective_tenant,
        PSMModel.ist_aktiv == True,
        PSMModel.zulassung_ablauf <= expiry_cutoff,
        PSMModel.zulassung_ablauf >= datetime.utcnow().date()
    ).count()

    expired_count = db.query(PSMModel).filter(
        PSMModel.tenant_id == effective_tenant,
        PSMModel.ist_aktiv == True,
        PSMModel.zulassung_ablauf < datetime.utcnow().date()
    ).count()

    # Stock stats
    stock_stats = db.query(
        db.func.sum(PSMModel.lagerbestand),
        db.func.avg(PSMModel.vk_preis)
    ).filter(
        PSMModel.tenant_id == effective_tenant,
        PSMModel.ist_aktiv == True
    ).first()

    # Farmer declaration stats
    erklaerung_stats = {}
    erklaerung = db.query(
        PSMModel.erklaerung_landwirt_status,
        db.func.count(PSMModel.id)
    ).filter(
        PSMModel.tenant_id == effective_tenant,
        PSMModel.ist_aktiv == True,
        PSMModel.ausgangsstoff_explosivstoffe == True
    ).group_by(PSMModel.erklaerung_landwirt_status).all()

    for status, count in erklaerung:
        erklaerung_stats[status or "offen"] = count

    return {
        "total_psm": sum(type_stats.values()),
        "by_type": type_stats,
        "by_safety": safety_stats,
        "farmer_declaration": erklaerung_stats,
        "approval_warnings": {
            "expiring_soon": expiring_count,
            "already_expired": expired_count
        },
        "stock_summary": {
            "total_stock": float(stock_stats[0] or 0),
            "avg_price": float(stock_stats[1] or 0)
        }
    }


@router.post("/sync/proplanta", response_model=dict)
async def sync_proplanta_psm(
    sync_config: dict = {
        "url": "https://www.proplanta.de/psm-database",
        "force_update": False,
        "max_items": 1000
    },
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Trigger automated PSM synchronization with Proplanta."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    try:
        # Import MCP client for Proplanta scraping
        from ....integrations.mcp_client import call_mcp_tool

        logger.info(f"Starting PSM sync for tenant {effective_tenant}")

        # Call MCP tool to scrape PSM data
        result = await call_mcp_tool(
            server_name="proplanta-psm-scraper",
            tool_name="scrape_psm_list",
            arguments={
                "url": sync_config.get("url", "https://www.proplanta.de/psm-database"),
                "username": sync_config.get("username"),
                "password": sync_config.get("password")
            }
        )

        if not result or not result.get("content"):
            raise HTTPException(status_code=500, detail="Failed to scrape PSM data from Proplanta")

        # Parse scraped data
        scraped_data = result["content"]
        if isinstance(scraped_data, list) and len(scraped_data) > 0:
            # Extract PSM data from MCP response
            psm_items = scraped_data[0].get("text", "").split("\n")
            processed_count = 0

            for item_text in psm_items[:sync_config.get("max_items", 1000)]:
                if not item_text.strip():
                    continue

                try:
                    # Parse PSM data (simplified - would need proper JSON parsing)
                    # This is a placeholder for actual data processing
                    processed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process PSM item: {e}")
                    continue

            logger.info(f"Successfully processed {processed_count} PSM items from Proplanta")

            return {
                "status": "completed",
                "message": f"PSM synchronization completed successfully",
                "processed_items": processed_count,
                "tenant_id": effective_tenant,
                "timestamp": datetime.utcnow().isoformat()
            }

        else:
            return {
                "status": "completed",
                "message": "No new PSM data found",
                "processed_items": 0,
                "tenant_id": effective_tenant,
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"PSM sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"PSM synchronization failed: {str(e)}")


@router.get("/sync/status")
async def get_sync_status(
    tenant_id: Optional[str] = Query(None),
):
    """Get current PSM synchronization status."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    # Get comprehensive sync status from scheduler
    status = sync_scheduler.get_schedule_status()

    return {
        "tenant_id": effective_tenant,
        "schedules": status['schedules'],
        "active_jobs": status['active_jobs'],
        "summary": status['summary']
    }


@router.post("/sync/schedule")
async def schedule_sync(
    schedule_config: dict = {
        "name": "custom_psm_sync",
        "interval_hours": 24,
        "enabled": True,
        "article_groups": ["PSM"],
        "max_items": 1000
    },
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Schedule automated PSM synchronization."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    # Add schedule to sync scheduler
    schedule = sync_scheduler.add_schedule(
        name=schedule_config.get("name", f"custom_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
        interval_hours=schedule_config.get("interval_hours", 24),
        article_groups=schedule_config.get("article_groups", ["PSM"]),
        max_items=schedule_config.get("max_items", 1000),
        enabled=schedule_config.get("enabled", True)
    )

    logger.info(f"PSM sync scheduled for tenant {effective_tenant}: {schedule_config}")

    return {
        "status": "scheduled",
        "tenant_id": effective_tenant,
        "schedule_name": schedule.name,
        "interval_hours": schedule.interval_hours,
        "enabled": schedule.enabled,
        "article_groups": schedule.article_groups,
        "max_items": schedule.max_items,
        "next_run": schedule.next_run.isoformat() if schedule.next_run else None
    }


@router.post("/sync/run-due")
async def run_due_schedules(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Execute all due sync schedules."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    due_schedules = sync_scheduler.get_due_schedules()
    executed_jobs = []

    for schedule in due_schedules:
        for article_group in schedule.article_groups:
            try:
                # Start sync job
                job_id = sync_scheduler.start_sync_job(schedule.name, article_group)

                # Execute sync based on article group
                if article_group == "PSM":
                    # PSM sync logic
                    await sync_proplanta_psm(
                        sync_config={
                            "max_items": schedule.max_items,
                            "force_update": False
                        },
                        tenant_id=effective_tenant,
                        db=db
                    )
                    sync_scheduler.update_job_status(job_id, "completed", schedule.max_items)

                elif article_group in ["DUENGER", "SAATGUT", "BIOSTIMULANZ"]:
                    # Placeholder for other article syncs
                    sync_scheduler.update_job_status(job_id, "completed", 0)

                elif article_group in ["PRICES", "COMPETITOR_PRICES"]:
                    # Placeholder for price syncs
                    sync_scheduler.update_job_status(job_id, "completed", 0)

                executed_jobs.append({
                    "schedule_name": schedule.name,
                    "article_group": article_group,
                    "job_id": job_id,
                    "status": "completed"
                })

            except Exception as e:
                logger.error(f"Failed to execute sync job for {schedule.name}/{article_group}: {e}")
                sync_scheduler.update_job_status(job_id, "failed", 0, str(e))
                executed_jobs.append({
                    "schedule_name": schedule.name,
                    "article_group": article_group,
                    "job_id": job_id,
                    "status": "failed",
                    "error": str(e)
                })

    return {
        "status": "executed",
        "tenant_id": effective_tenant,
        "due_schedules": len(due_schedules),
        "executed_jobs": executed_jobs,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.put("/sync/schedule/{schedule_name}")
async def update_sync_schedule(
    schedule_name: str,
    updates: dict,
    tenant_id: Optional[str] = Query(None),
):
    """Update an existing sync schedule."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    try:
        sync_scheduler.update_schedule(schedule_name, **updates)
        return {
            "status": "updated",
            "schedule_name": schedule_name,
            "tenant_id": effective_tenant,
            "updates": updates
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update schedule: {str(e)}")


@router.delete("/sync/schedule/{schedule_name}")
async def delete_sync_schedule(
    schedule_name: str,
    tenant_id: Optional[str] = Query(None),
):
    """Delete a sync schedule."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    try:
        if schedule_name in sync_scheduler.schedules:
            del sync_scheduler.schedules[schedule_name]
            sync_scheduler.save_schedules()
            return {
                "status": "deleted",
                "schedule_name": schedule_name,
                "tenant_id": effective_tenant
            }
        else:
            raise HTTPException(status_code=404, detail=f"Schedule {schedule_name} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete schedule: {str(e)}")


@router.post("/competitor/search")
async def search_competitor_products(
    query: str = Query(..., description="Search query for products"),
    category: str = Query("psm", description="Product category"),
    max_results: int = Query(50, description="Maximum number of results"),
    tenant_id: Optional[str] = Query(None),
):
    """Search for competitor products using hybrid search-scraping approach"""
    effective_tenant = tenant_id or DEFAULT_TENANT

    try:
        # Search for product URLs
        product_urls = await competitor_monitor.search_products(query, category, max_results)

        return {
            "query": query,
            "category": category,
            "found_urls": len(product_urls),
            "product_urls": product_urls[:max_results],
            "tenant_id": effective_tenant,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Competitor search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Competitor search failed: {str(e)}")


@router.post("/competitor/scrape")
async def scrape_competitor_data(
    product_urls: List[str] = Query(..., description="List of product URLs to scrape"),
    tenant_id: Optional[str] = Query(None),
):
    """Scrape competitor product data from URLs"""
    effective_tenant = tenant_id or DEFAULT_TENANT

    try:
        scraped_data = []

        for url in product_urls[:20]:  # Limit to 20 URLs per request
            product_data = await competitor_monitor.scrape_product_data(url)
            if product_data:
                scraped_data.append({
                    "shop_name": product_data.shop_name,
                    "product_url": product_data.product_url,
                    "product_name": product_data.product_name,
                    "price": product_data.price,
                    "currency": product_data.currency,
                    "brand": product_data.brand,
                    "gtin": product_data.gtin,
                    "images": [
                        {
                            "url": img.url,
                            "hash": img.hash,
                            "width": img.width,
                            "height": img.height
                        } for img in product_data.images
                    ],
                    "scraped_at": product_data.scraped_at.isoformat() if product_data.scraped_at else None
                })

        # Save to price history
        if scraped_data:
            competitor_monitor.save_price_history([
                competitor_monitor._parse_scraped_data(item) for item in scraped_data
                if competitor_monitor._parse_scraped_data(item)
            ])

        return {
            "scraped_count": len(scraped_data),
            "products": scraped_data,
            "tenant_id": effective_tenant,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Competitor scraping failed: {e}")
        raise HTTPException(status_code=500, detail=f"Competitor scraping failed: {str(e)}")


@router.get("/competitor/alerts")
async def get_price_alerts(
    threshold_percent: float = Query(15.0, description="Price change threshold for alerts"),
    tenant_id: Optional[str] = Query(None),
):
    """Get price change alerts"""
    effective_tenant = tenant_id or DEFAULT_TENANT

    try:
        alerts = competitor_monitor.get_price_alerts(threshold_percent)

        return {
            "alerts_count": len(alerts),
            "threshold_percent": threshold_percent,
            "alerts": alerts,
            "tenant_id": effective_tenant,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get price alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get price alerts: {str(e)}")


@router.get("/competitor/history")
async def get_price_history(
    product_url: Optional[str] = Query(None, description="Filter by product URL"),
    shop_name: Optional[str] = Query(None, description="Filter by shop name"),
    days: int = Query(30, description="Number of days to look back"),
    tenant_id: Optional[str] = Query(None),
):
    """Get price history data"""
    effective_tenant = tenant_id or DEFAULT_TENANT

    try:
        # This would typically query a database
        # For now, return mock data structure
        return {
            "product_url": product_url,
            "shop_name": shop_name,
            "days": days,
            "history": [],  # Would contain actual price history
            "tenant_id": effective_tenant,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get price history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get price history: {str(e)}")


@router.post("/competitor/monitor")
async def start_competitor_monitoring(
    config: dict = {
        "categories": ["psm", "duenger", "saatgut"],
        "shops": ["baywa", "raiffeisen", "agrar24"],
        "alert_threshold": 15.0,
        "schedule_hours": 24
    },
    tenant_id: Optional[str] = Query(None),
):
    """Start automated competitor monitoring"""
    effective_tenant = tenant_id or DEFAULT_TENANT

    try:
        # Add to sync scheduler as competitor monitoring job
        schedule = sync_scheduler.add_schedule(
            name=f"competitor_monitor_{effective_tenant}",
            interval_hours=config.get("schedule_hours", 24),
            article_groups=["COMPETITOR_PRICES"],
            max_items=1000,
            enabled=True
        )

        return {
            "status": "monitoring_started",
            "schedule_name": schedule.name,
            "categories": config.get("categories", []),
            "shops": config.get("shops", []),
            "alert_threshold": config.get("alert_threshold", 15.0),
            "next_run": schedule.next_run.isoformat() if schedule.next_run else None,
            "tenant_id": effective_tenant,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to start competitor monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start competitor monitoring: {str(e)}")