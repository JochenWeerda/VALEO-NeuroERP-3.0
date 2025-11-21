from fastapi import APIRouter

from .endpoints import activities, contacts, customers, farm_profiles, leads

api_router = APIRouter()
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(farm_profiles.router, prefix="/farm-profiles", tags=["farm-profiles"])
