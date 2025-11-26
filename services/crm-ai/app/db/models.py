"""SQLAlchemy models for CRM AI Service."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, Text, Integer, Float, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ModelType(str, Enum):
    LEAD_SCORING = "lead_scoring"
    CHURN_PREDICTION = "churn_prediction"
    CLV_PREDICTION = "clv_prediction"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    INTENT_CLASSIFICATION = "intent_classification"
    RECOMMENDATION = "recommendation"


class ModelStatus(str, Enum):
    TRAINING = "training"
    READY = "ready"
    FAILED = "failed"
    DEPRECATED = "deprecated"


class AlgorithmType(str, Enum):
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    LOGISTIC_REGRESSION = "logistic_regression"
    SVM = "svm"
    TRANSFORMER = "transformer"


enum_values = lambda enum_cls: [member.value for member in enum_cls]  # noqa: E731


class AIModel(Base):
    __tablename__ = "crm_ai_models"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    type: Mapped[ModelType] = mapped_column(
        SQLEnum(
            ModelType,
            name="crm_ai_model_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    algorithm: Mapped[AlgorithmType] = mapped_column(
        SQLEnum(
            AlgorithmType,
            name="crm_ai_algorithm_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    status: Mapped[ModelStatus] = mapped_column(
        SQLEnum(
            ModelStatus,
            name="crm_ai_model_status",
            values_callable=enum_values,
        ),
        default=ModelStatus.TRAINING,
        nullable=False,
    )

    # Model metadata
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    accuracy: Mapped[float | None] = mapped_column(Float)
    precision: Mapped[float | None] = mapped_column(Float)
    recall: Mapped[float | None] = mapped_column(Float)
    f1_score: Mapped[float | None] = mapped_column(Float)

    # Training parameters
    hyperparameters: Mapped[dict] = mapped_column(JSON, default=dict)
    feature_importance: Mapped[dict] = mapped_column(JSON, default=dict)
    training_data_info: Mapped[dict] = mapped_column(JSON, default=dict)

    # Model storage
    model_path: Mapped[str | None] = mapped_column(String(500))
    model_size_bytes: Mapped[int | None] = mapped_column(Integer)

    # Performance tracking
    last_used: Mapped[datetime | None] = mapped_column(DateTime)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "crm_ai_predictions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    model_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_ai_models.id"), nullable=False)

    # Prediction target
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)  # customer, lead, case, etc.

    # Prediction results
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-1 probability/confidence
    prediction_class: Mapped[str | None] = mapped_column(String(64))  # categorical prediction
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # 0-1 confidence level

    # Input features used
    features: Mapped[dict] = mapped_column(JSON, nullable=False)
    feature_importance: Mapped[dict] = mapped_column(JSON, default=dict)

    # Prediction metadata
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    prediction_type: Mapped[str] = mapped_column(String(64), nullable=False)

    # Caching and performance
    cached_until: Mapped[datetime | None] = mapped_column(DateTime)
    computation_time_ms: Mapped[int | None] = mapped_column(Integer)

    # Validation and feedback
    actual_outcome: Mapped[str | None] = mapped_column(String(64))  # For supervised learning validation
    feedback_score: Mapped[float | None] = mapped_column(Float)  # User feedback on prediction quality

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    model: Mapped[AIModel] = relationship("AIModel")


class Feature(Base):
    __tablename__ = "crm_ai_features"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)  # customer, lead, case, etc.
    data_type: Mapped[str] = mapped_column(String(32), nullable=False)  # numeric, categorical, text, boolean

    # Feature engineering
    source_field: Mapped[str | None] = mapped_column(String(255))  # Original field name
    transformation: Mapped[str | None] = mapped_column(String(64))  # log, sqrt, normalize, etc.
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)

    # Statistics for numeric features
    min_value: Mapped[float | None] = mapped_column(Float)
    max_value: Mapped[float | None] = mapped_column(Float)
    mean_value: Mapped[float | None] = mapped_column(Float)
    std_deviation: Mapped[float | None] = mapped_column(Float)

    # Categories for categorical features
    categories: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used: Mapped[datetime | None] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Experiment(Base):
    __tablename__ = "crm_ai_experiments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    model_type: Mapped[ModelType] = mapped_column(
        SQLEnum(
            ModelType,
            name="crm_ai_experiment_model_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    # Experiment variants
    control_variant: Mapped[dict] = mapped_column(JSON, nullable=False)
    test_variants: Mapped[list[dict]] = mapped_column(JSON, nullable=False)

    # Experiment parameters
    target_metric: Mapped[str] = mapped_column(String(64), nullable=False)
    minimum_sample_size: Mapped[int] = mapped_column(Integer, default=1000)
    confidence_level: Mapped[float] = mapped_column(Float, default=0.95)

    # Status and results
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")  # running, completed, stopped
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime)

    # Results
    winner_variant: Mapped[str | None] = mapped_column(String(64))
    statistical_significance: Mapped[float | None] = mapped_column(Float)
    effect_size: Mapped[float | None] = mapped_column(Float)
    results_summary: Mapped[dict] = mapped_column(JSON, default=dict)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "crm_ai_feedback"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    prediction_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_ai_predictions.id"), nullable=False)

    # Feedback data
    rating: Mapped[int] = mapped_column(Integer)  # 1-5 scale
    comments: Mapped[str | None] = mapped_column(Text)
    feedback_type: Mapped[str] = mapped_column(String(32), nullable=False)  # accuracy, usefulness, relevance

    # Context
    user_id: Mapped[str | None] = mapped_column(String(64))
    context_data: Mapped[dict] = mapped_column(JSON, default=dict)

    # For model improvement
    corrected_prediction: Mapped[str | None] = mapped_column(String(255))
    feature_adjustments: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    prediction: Mapped[Prediction] = relationship("Prediction")