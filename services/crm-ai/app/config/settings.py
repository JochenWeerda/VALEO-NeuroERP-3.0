"""
Settings for CRM AI Service.
"""

import os
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    ***REMOVED*** Database
    DATABASE_URL: str = "postgresql+asyncpg://valeo_dev:REDACTED_PASSWORD@postgres:5432/valeo_neuro_erp"

    ***REMOVED*** Redis
    REDIS_URL: str = "redis://localhost:6379/7"

    ***REMOVED*** Service
    SERVICE_NAME: str = "crm-ai"
    DEBUG: bool = False

    ***REMOVED*** CORS
    CORS_ORIGINS: list[str] = ["*"]

    ***REMOVED*** Tenant
    DEFAULT_TENANT_ID: str = "00000000-0000-0000-0000-000000000001"

    ***REMOVED*** CRM Service URLs (for data access and integration)
    CRM_CORE_BASE_URL: str = "http://localhost:5600"
    CRM_SALES_BASE_URL: str = "http://localhost:5700"
    CRM_SERVICE_BASE_URL: str = "http://localhost:5800"
    CRM_ANALYTICS_BASE_URL: str = "http://localhost:6000"
    CRM_COMMUNICATION_BASE_URL: str = "http://localhost:6100"

    ***REMOVED*** AI/ML Configuration
    MODEL_CACHE_TTL_SECONDS: int = 3600  ***REMOVED*** 1 hour
    PREDICTION_CACHE_TTL_SECONDS: int = 300  ***REMOVED*** 5 minutes
    MAX_TRAINING_DATA_SIZE: int = 100000
    DEFAULT_LEAD_SCORE_THRESHOLD: float = 0.7
    DEFAULT_CHURN_RISK_THRESHOLD: float = 0.6

    ***REMOVED*** ML Model Paths
    MODEL_STORAGE_PATH: str = "/app/models"
    LEAD_SCORING_MODEL_PATH: str = "/app/models/lead_scoring.pkl"
    CHURN_PREDICTION_MODEL_PATH: str = "/app/models/churn_prediction.pkl"
    CLV_MODEL_PATH: str = "/app/models/clv_prediction.pkl"

    ***REMOVED*** NLP Configuration
    SPACY_MODEL: str = "en_core_web_sm"
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    INTENT_MODEL: str = "facebook/bart-large-mnli"

    ***REMOVED*** Feature Engineering
    LEAD_FEATURES: list[str] = [
        "company_size", "industry", "region", "email_domain",
        "phone_presence", "website_presence", "social_presence",
        "engagement_score", "response_time", "interaction_count"
    ]

    CHURN_FEATURES: list[str] = [
        "tenure_months", "total_orders", "avg_order_value",
        "last_order_days", "support_tickets", "satisfaction_score",
        "engagement_score", "payment_delays", "contract_value"
    ]

    CLV_FEATURES: list[str] = [
        "tenure_months", "total_orders", "avg_order_value",
        "contract_value", "industry", "region", "satisfaction_score"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()