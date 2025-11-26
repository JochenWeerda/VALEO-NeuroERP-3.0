"""Pydantic schemas for AI Service."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class LeadScoringRequest(BaseModel):
    """Request schema for lead scoring."""
    lead_id: UUID
    features: Dict[str, Any] = Field(..., description="Lead features for scoring")
    tenant_id: Optional[str] = None


class LeadScoringResponse(BaseModel):
    """Response schema for lead scoring."""
    lead_id: UUID
    score: float = Field(..., ge=0, le=1, description="Lead quality score 0-1")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence 0-1")
    grade: str = Field(..., description="A, B, C, D, F grade")
    reasons: List[str] = Field(..., description="Reasons for the score")
    recommendations: List[str] = Field(..., description="Recommended next actions")
    model_version: str
    computed_at: datetime


class ChurnPredictionRequest(BaseModel):
    """Request schema for churn prediction."""
    customer_id: UUID
    features: Dict[str, Any] = Field(..., description="Customer features for prediction")
    tenant_id: Optional[str] = None


class ChurnPredictionResponse(BaseModel):
    """Response schema for churn prediction."""
    customer_id: UUID
    churn_probability: float = Field(..., ge=0, le=1, description="Churn probability 0-1")
    risk_level: str = Field(..., description="Low, Medium, High, Critical")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence 0-1")
    risk_factors: List[str] = Field(..., description="Key risk factors identified")
    retention_recommendations: List[str] = Field(..., description="Retention strategies")
    predicted_churn_date: Optional[datetime] = None
    model_version: str
    computed_at: datetime


class CLVPredictionRequest(BaseModel):
    """Request schema for CLV prediction."""
    customer_id: UUID
    features: Dict[str, Any] = Field(..., description="Customer features for CLV calculation")
    time_horizon_months: int = Field(12, ge=1, le=120, description="Prediction time horizon")
    tenant_id: Optional[str] = None


class CLVPredictionResponse(BaseModel):
    """Response schema for CLV prediction."""
    customer_id: UUID
    predicted_clv: float = Field(..., ge=0, description="Predicted customer lifetime value")
    confidence_interval_lower: float = Field(..., ge=0)
    confidence_interval_upper: float = Field(..., ge=0)
    time_horizon_months: int
    key_drivers: List[str] = Field(..., description="Key factors influencing CLV")
    segments: List[str] = Field(..., description="Customer segments")
    model_version: str
    computed_at: datetime


class NextBestActionRequest(BaseModel):
    """Request schema for next best action recommendations."""
    customer_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    context: Dict[str, Any] = Field(..., description="Current context and state")
    available_actions: List[str] = Field(..., description="Available actions to choose from")
    tenant_id: Optional[str] = None


class NextBestActionResponse(BaseModel):
    """Response schema for next best action recommendations."""
    entity_id: UUID
    entity_type: str = Field(..., description="customer, lead, case")
    recommended_action: str
    confidence: float = Field(..., ge=0, le=1)
    expected_value: Optional[float] = None
    reasoning: str
    alternative_actions: List[Dict[str, Any]] = Field(default_factory=list)
    model_version: str
    computed_at: datetime


class EmailAnalysisRequest(BaseModel):
    """Request schema for email analysis."""
    email_id: UUID
    content: str = Field(..., description="Email content to analyze")
    subject: Optional[str] = None
    tenant_id: Optional[str] = None


class EmailAnalysisResponse(BaseModel):
    """Response schema for email analysis."""
    email_id: UUID
    sentiment: str = Field(..., description="positive, negative, neutral")
    sentiment_score: float = Field(..., ge=-1, le=1)
    intent: str = Field(..., description="question, complaint, request, feedback, etc.")
    intent_confidence: float = Field(..., ge=0, le=1)
    urgency: str = Field(..., description="low, medium, high, critical")
    key_topics: List[str] = Field(..., description="Main topics discussed")
    entities: Dict[str, List[str]] = Field(..., description="Extracted entities")
    suggested_response: Optional[str] = None
    routing_recommendation: Optional[str] = None
    model_version: str
    analyzed_at: datetime


class CaseClassificationRequest(BaseModel):
    """Request schema for case classification."""
    case_id: UUID
    title: str
    description: str
    category_hints: Optional[List[str]] = None
    tenant_id: Optional[str] = None


class CaseClassificationResponse(BaseModel):
    """Response schema for case classification."""
    case_id: UUID
    predicted_category: str
    confidence: float = Field(..., ge=0, le=1)
    subcategories: List[str] = Field(default_factory=list)
    priority_suggestion: str = Field(..., description="low, medium, high, critical")
    routing_suggestion: str = Field(..., description="Suggested team/department")
    similar_cases: List[Dict[str, Any]] = Field(default_factory=list)
    model_version: str
    classified_at: datetime


class AIModelInfo(BaseModel):
    """Schema for AI model information."""
    id: UUID
    name: str
    type: str
    algorithm: str
    status: str
    version: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    last_trained: Optional[datetime] = None
    usage_count: int = 0
    is_active: bool = True


class ModelListResponse(BaseModel):
    """Response schema for listing AI models."""
    models: List[AIModelInfo]
    total: int


class FeedbackSubmission(BaseModel):
    """Schema for submitting AI model feedback."""
    prediction_id: UUID
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback_type: str = Field(..., description="accuracy, usefulness, relevance")
    comments: Optional[str] = None
    corrected_prediction: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None


class BatchPredictionRequest(BaseModel):
    """Request schema for batch predictions."""
    entity_ids: List[UUID] = Field(..., min_items=1, max_items=1000)
    entity_type: str = Field(..., description="customer, lead, case")
    prediction_type: str = Field(..., description="lead_scoring, churn_prediction, clv")
    tenant_id: Optional[str] = None


class BatchPredictionResponse(BaseModel):
    """Response schema for batch predictions."""
    predictions: List[Dict[str, Any]]
    total_processed: int
    total_successful: int
    total_failed: int
    model_version: str
    batch_id: UUID
    processed_at: datetime


class ModelTrainingRequest(BaseModel):
    """Request schema for model training."""
    model_type: str = Field(..., description="lead_scoring, churn_prediction, clv")
    algorithm: str = Field(..., description="random_forest, gradient_boosting, neural_network")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    training_data_query: Dict[str, Any] = Field(..., description="Query to get training data")
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None


class ModelTrainingResponse(BaseModel):
    """Response schema for model training."""
    model_id: UUID
    training_job_id: UUID
    status: str = "queued"
    estimated_completion_time: Optional[datetime] = None
    message: str