"""CRM Multi-Channel API v1 router."""

from fastapi import APIRouter

from .endpoints.multichannel import router as multichannel_router

api_router = APIRouter()
api_router.include_router(multichannel_router, prefix="/multichannel", tags=["multichannel"])

# TODO: Add dedicated routers for specific platforms when implemented
# api_router.include_router(facebook_router, prefix="/facebook", tags=["facebook"])
# api_router.include_router(twitter_router, prefix="/twitter", tags=["twitter"])
# api_router.include_router(shopify_router, prefix="/shopify", tags=["shopify"])