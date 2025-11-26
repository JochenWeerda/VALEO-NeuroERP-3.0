"""Initial CRM AI schema.

Revision ID: 001_initial_crm_ai_schema
Revises:
Create Date: 2025-11-15 11:58:00.000000

"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001_initial_crm_ai_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create CRM AI tables."""
    # Create enums
    op.execute("CREATE TYPE crm_ai_model_type AS ENUM ('lead_scoring', 'churn_prediction', 'clv_prediction', 'sentiment_analysis', 'intent_classification', 'recommendation')")
    op.execute("CREATE TYPE crm_ai_model_status AS ENUM ('training', 'ready', 'failed', 'deprecated')")
    op.execute("CREATE TYPE crm_ai_algorithm_type AS ENUM ('random_forest', 'gradient_boosting', 'neural_network', 'logistic_regression', 'svm', 'transformer')")

    # AI Models table
    op.create_table(
        "crm_ai_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("type", postgresql.ENUM('lead_scoring', 'churn_prediction', 'clv_prediction', 'sentiment_analysis', 'intent_classification', 'recommendation', name='crm_ai_model_type'), nullable=False),
        sa.Column("algorithm", postgresql.ENUM('random_forest', 'gradient_boosting', 'neural_network', 'logistic_regression', 'svm', 'transformer', name='crm_ai_algorithm_type'), nullable=False),
        sa.Column("status", postgresql.ENUM('training', 'ready', 'failed', 'deprecated', name='crm_ai_model_status'), nullable=False, server_default='training'),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("accuracy", sa.Float),
        sa.Column("precision", sa.Float),
        sa.Column("recall", sa.Float),
        sa.Column("f1_score", sa.Float),
        sa.Column("hyperparameters", postgresql.JSONB, default=dict),
        sa.Column("feature_importance", postgresql.JSONB, default=dict),
        sa.Column("training_data_info", postgresql.JSONB, default=dict),
        sa.Column("model_path", sa.String(500)),
        sa.Column("model_size_bytes", sa.Integer),
        sa.Column("last_used", sa.DateTime),
        sa.Column("usage_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Predictions table
    op.create_table(
        "crm_ai_predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_ai_models.id"), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("prediction_class", sa.String(64)),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("features", postgresql.JSONB, nullable=False),
        sa.Column("feature_importance", postgresql.JSONB, default=dict),
        sa.Column("model_version", sa.String(32), nullable=False),
        sa.Column("prediction_type", sa.String(64), nullable=False),
        sa.Column("cached_until", sa.DateTime),
        sa.Column("computation_time_ms", sa.Integer),
        sa.Column("actual_outcome", sa.String(64)),
        sa.Column("feedback_score", sa.Float),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Features table
    op.create_table(
        "crm_ai_features",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("data_type", sa.String(32), nullable=False),
        sa.Column("source_field", sa.String(255)),
        sa.Column("transformation", sa.String(64)),
        sa.Column("parameters", postgresql.JSONB, default=dict),
        sa.Column("min_value", sa.Float),
        sa.Column("max_value", sa.Float),
        sa.Column("mean_value", sa.Float),
        sa.Column("std_deviation", sa.Float),
        sa.Column("categories", postgresql.JSONB, default=list),
        sa.Column("usage_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("last_used", sa.DateTime),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Experiments table
    op.create_table(
        "crm_ai_experiments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("model_type", postgresql.ENUM('lead_scoring', 'churn_prediction', 'clv_prediction', 'sentiment_analysis', 'intent_classification', 'recommendation', name='crm_ai_experiment_model_type'), nullable=False),
        sa.Column("control_variant", postgresql.JSONB, nullable=False),
        sa.Column("test_variants", postgresql.JSONB, nullable=False),
        sa.Column("target_metric", sa.String(64), nullable=False),
        sa.Column("minimum_sample_size", sa.Integer, nullable=False, server_default='1000'),
        sa.Column("confidence_level", sa.Float, nullable=False, server_default='0.95'),
        sa.Column("status", sa.String(32), nullable=False, server_default='running'),
        sa.Column("start_date", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("end_date", sa.DateTime),
        sa.Column("winner_variant", sa.String(64)),
        sa.Column("statistical_significance", sa.Float),
        sa.Column("effect_size", sa.Float),
        sa.Column("results_summary", postgresql.JSONB, default=dict),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Feedback table
    op.create_table(
        "crm_ai_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("prediction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_ai_predictions.id"), nullable=False),
        sa.Column("rating", sa.Integer),
        sa.Column("comments", sa.Text),
        sa.Column("feedback_type", sa.String(32), nullable=False),
        sa.Column("user_id", sa.String(64)),
        sa.Column("context_data", postgresql.JSONB, default=dict),
        sa.Column("corrected_prediction", sa.String(255)),
        sa.Column("feature_adjustments", postgresql.JSONB, default=dict),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Seed initial data
    _seed_initial_data()


def downgrade() -> None:
    """Drop CRM AI tables."""
    op.drop_table("crm_ai_feedback")
    op.drop_table("crm_ai_experiments")
    op.drop_table("crm_ai_features")
    op.drop_table("crm_ai_predictions")
    op.drop_table("crm_ai_models")

    op.execute("DROP TYPE crm_ai_algorithm_type")
    op.execute("DROP TYPE crm_ai_model_status")
    op.execute("DROP TYPE crm_ai_model_type")
    op.execute("DROP TYPE crm_ai_experiment_model_type")


def _seed_initial_data():
    """Seed initial demo AI data."""
    # This will be populated when the service starts and finds existing data
    pass