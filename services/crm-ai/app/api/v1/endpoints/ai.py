"""CRM AI API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....schemas.ai import (
    LeadScoringRequest, LeadScoringResponse, ChurnPredictionRequest, ChurnPredictionResponse,
    CLVPredictionRequest, CLVPredictionResponse, NextBestActionRequest, NextBestActionResponse,
    EmailAnalysisRequest, EmailAnalysisResponse, CaseClassificationRequest, CaseClassificationResponse,
    ModelListResponse, FeedbackSubmission, BatchPredictionRequest, BatchPredictionResponse,
    ModelTrainingRequest, ModelTrainingResponse
)
from ....schemas.base import PaginatedResponse

router = APIRouter()


@router.post("/lead-score", response_model=LeadScoringResponse, status_code=status.HTTP_200_OK)
async def score_lead(
    request: LeadScoringRequest,
    db: AsyncSession = get_db
):
    """Calculate lead scoring using ML models."""
    # Mock lead scoring - in production this would use trained ML models
    score = 0.85  # High-quality lead
    confidence = 0.92

    # Determine grade based on score
    if score >= 0.9:
        grade = "A"
    elif score >= 0.8:
        grade = "B"
    elif score >= 0.6:
        grade = "C"
    elif score >= 0.4:
        grade = "D"
    else:
        grade = "F"

    reasons = [
        "High company size indicates enterprise potential",
        "Strong industry match with our expertise",
        "Recent engagement shows active interest",
        "Good email domain reputation"
    ]

    recommendations = [
        "Schedule immediate demo call",
        "Send personalized product brochure",
        "Connect with technical decision maker",
        "Prepare custom pricing proposal"
    ]

    return LeadScoringResponse(
        lead_id=request.lead_id,
        score=score,
        confidence=confidence,
        grade=grade,
        reasons=reasons,
        recommendations=recommendations,
        model_version="v2.1.0",
        computed_at="2025-11-15T11:56:00Z"
    )


@router.post("/predict/churn", response_model=ChurnPredictionResponse, status_code=status.HTTP_200_OK)
async def predict_churn(
    request: ChurnPredictionRequest,
    db: AsyncSession = get_db
):
    """Predict customer churn probability."""
    # Mock churn prediction
    churn_probability = 0.15  # Low churn risk
    confidence = 0.88

    if churn_probability >= 0.8:
        risk_level = "Critical"
    elif churn_probability >= 0.6:
        risk_level = "High"
    elif churn_probability >= 0.4:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    risk_factors = [
        "Recent support ticket resolution time",
        "Contract renewal approaching",
        "Competitor mentions in recent calls"
    ]

    retention_recommendations = [
        "Schedule account review meeting",
        "Offer contract renewal discount",
        "Provide additional training resources",
        "Increase touchpoint frequency"
    ]

    return ChurnPredictionResponse(
        customer_id=request.customer_id,
        churn_probability=churn_probability,
        risk_level=risk_level,
        confidence=confidence,
        risk_factors=risk_factors,
        retention_recommendations=retention_recommendations,
        predicted_churn_date=None,
        model_version="v1.8.3",
        computed_at="2025-11-15T11:56:00Z"
    )


@router.post("/predict/clv", response_model=CLVPredictionResponse, status_code=status.HTTP_200_OK)
async def predict_clv(
    request: CLVPredictionRequest,
    db: AsyncSession = get_db
):
    """Predict customer lifetime value."""
    # Mock CLV prediction
    predicted_clv = 125000.0
    confidence_interval_lower = 95000.0
    confidence_interval_upper = 155000.0

    key_drivers = [
        "High contract value",
        "Long tenure (24 months)",
        "Consistent purchase history",
        "Enterprise segment classification"
    ]

    segments = [
        "Enterprise",
        "High-Value",
        "Long-Term",
        "Technology Sector"
    ]

    return CLVPredictionResponse(
        customer_id=request.customer_id,
        predicted_clv=predicted_clv,
        confidence_interval_lower=confidence_interval_lower,
        confidence_interval_upper=confidence_interval_upper,
        time_horizon_months=request.time_horizon_months,
        key_drivers=key_drivers,
        segments=segments,
        model_version="v3.2.1",
        computed_at="2025-11-15T11:56:00Z"
    )


@router.post("/recommend/actions", response_model=NextBestActionResponse, status_code=status.HTTP_200_OK)
async def recommend_next_action(
    request: NextBestActionRequest,
    db: AsyncSession = get_db
):
    """Recommend next best action for customer/lead engagement."""
    # Determine entity info
    if request.customer_id:
        entity_id = request.customer_id
        entity_type = "customer"
    elif request.lead_id:
        entity_id = request.lead_id
        entity_type = "lead"
    else:
        raise HTTPException(status_code=400, detail="Either customer_id or lead_id must be provided")

    # Mock recommendation logic
    recommended_action = "schedule_follow_up_call"
    confidence = 0.89
    expected_value = 2500.0
    reasoning = "Customer has shown high engagement but hasn't purchased in 30 days. Follow-up call has 35% conversion rate in similar cases."

    alternative_actions = [
        {"action": "send_personalized_email", "confidence": 0.76, "expected_value": 1800},
        {"action": "offer_discount", "confidence": 0.68, "expected_value": 3200},
        {"action": "schedule_demo", "confidence": 0.82, "expected_value": 4100}
    ]

    return NextBestActionResponse(
        entity_id=entity_id,
        entity_type=entity_type,
        recommended_action=recommended_action,
        confidence=confidence,
        expected_value=expected_value,
        reasoning=reasoning,
        alternative_actions=alternative_actions,
        model_version="v2.4.0",
        computed_at="2025-11-15T11:56:00Z"
    )


@router.post("/analyze/email", response_model=EmailAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_email(
    request: EmailAnalysisRequest,
    db: AsyncSession = get_db
):
    """Analyze email content for sentiment, intent, and routing."""
    # Mock email analysis
    sentiment = "neutral"
    sentiment_score = 0.1
    intent = "inquiry"
    intent_confidence = 0.87
    urgency = "medium"

    key_topics = [
        "Product pricing",
        "Contract terms",
        "Technical specifications"
    ]

    entities = {
        "PERSON": ["John Smith", "Sarah Johnson"],
        "ORG": ["ABC Corp", "Tech Solutions Inc"],
        "MONEY": ["$50,000", "€25,000"],
        "DATE": ["next quarter", "end of month"]
    }

    suggested_response = "Thank you for your inquiry about our pricing. I'll review the contract terms and get back to you within 24 hours with detailed information."

    routing_recommendation = "Sales Team - Enterprise Accounts"

    return EmailAnalysisResponse(
        email_id=request.email_id,
        sentiment=sentiment,
        sentiment_score=sentiment_score,
        intent=intent,
        intent_confidence=intent_confidence,
        urgency=urgency,
        key_topics=key_topics,
        entities=entities,
        suggested_response=suggested_response,
        routing_recommendation=routing_recommendation,
        model_version="v1.9.2",
        analyzed_at="2025-11-15T11:56:00Z"
    )


@router.post("/classify/case", response_model=CaseClassificationResponse, status_code=status.HTTP_200_OK)
async def classify_case(
    request: CaseClassificationRequest,
    db: AsyncSession = get_db
):
    """Automatically classify support cases for routing."""
    # Mock case classification
    predicted_category = "Technical Support"
    confidence = 0.91
    subcategories = ["Software Installation", "Configuration Issues"]
    priority_suggestion = "medium"
    routing_suggestion = "Technical Support Team"

    similar_cases = [
        {"case_id": "CASE-001", "similarity": 0.89, "resolution": "Configuration updated"},
        {"case_id": "CASE-015", "similarity": 0.76, "resolution": "Software reinstalled"}
    ]

    return CaseClassificationResponse(
        case_id=request.case_id,
        predicted_category=predicted_category,
        confidence=confidence,
        subcategories=subcategories,
        priority_suggestion=priority_suggestion,
        routing_suggestion=routing_suggestion,
        similar_cases=similar_cases,
        model_version="v2.1.5",
        classified_at="2025-11-15T11:56:00Z"
    )


@router.get("/models", response_model=ModelListResponse)
async def list_models(
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = get_db
):
    """List available AI models."""
    # Mock model list
    models = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Lead Scoring Model v2.1",
            "type": "lead_scoring",
            "algorithm": "gradient_boosting",
            "status": "ready",
            "version": "v2.1.0",
            "accuracy": 0.89,
            "precision": 0.91,
            "recall": 0.87,
            "f1_score": 0.89,
            "last_trained": "2025-11-10T08:00:00Z",
            "usage_count": 15420,
            "is_active": True
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "name": "Churn Prediction Model v1.8",
            "type": "churn_prediction",
            "algorithm": "random_forest",
            "status": "ready",
            "version": "v1.8.3",
            "accuracy": 0.92,
            "precision": 0.88,
            "recall": 0.91,
            "f1_score": 0.89,
            "last_trained": "2025-11-12T06:00:00Z",
            "usage_count": 8750,
            "is_active": True
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "name": "CLV Prediction Model v3.2",
            "type": "clv_prediction",
            "algorithm": "neural_network",
            "status": "ready",
            "version": "v3.2.1",
            "accuracy": 0.85,
            "precision": 0.83,
            "recall": 0.86,
            "f1_score": 0.84,
            "last_trained": "2025-11-08T10:00:00Z",
            "usage_count": 6230,
            "is_active": True
        }
    ]

    # Apply filters
    if model_type:
        models = [m for m in models if m["type"] == model_type]
    if status:
        models = [m for m in models if m["status"] == status]

    # Apply pagination
    total = len(models)
    models = models[skip:skip + limit]

    return ModelListResponse(models=models, total=total)


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackSubmission,
    db: AsyncSession = get_db
):
    """Submit feedback on AI predictions for model improvement."""
    # In production, this would store feedback for model retraining
    return {"message": "Feedback submitted successfully", "feedback_id": "fb-12345"}


@router.post("/batch/predict", response_model=BatchPredictionResponse, status_code=status.HTTP_200_OK)
async def batch_predict(
    request: BatchPredictionRequest,
    db: AsyncSession = get_db
):
    """Perform batch predictions for multiple entities."""
    # Mock batch prediction results
    predictions = []
    for entity_id in request.entity_ids:
        if request.prediction_type == "lead_scoring":
            predictions.append({
                "entity_id": str(entity_id),
                "score": 0.82,
                "confidence": 0.89,
                "grade": "B"
            })
        elif request.prediction_type == "churn_prediction":
            predictions.append({
                "entity_id": str(entity_id),
                "churn_probability": 0.23,
                "risk_level": "Low"
            })

    return BatchPredictionResponse(
        predictions=predictions,
        total_processed=len(request.entity_ids),
        total_successful=len(request.entity_ids),
        total_failed=0,
        model_version="v2.1.0-batch",
        batch_id="batch-12345",
        processed_at="2025-11-15T11:56:00Z"
    )


@router.post("/models/train", response_model=ModelTrainingResponse, status_code=status.HTTP_202_ACCEPTED)
async def train_model(
    request: ModelTrainingRequest,
    db: AsyncSession = get_db
):
    """Initiate model training job."""
    # In production, this would queue a training job
    return ModelTrainingResponse(
        model_id="model-12345",
        training_job_id="train-67890",
        status="queued",
        estimated_completion_time="2025-11-15T13:00:00Z",
        message="Training job queued successfully"
    )