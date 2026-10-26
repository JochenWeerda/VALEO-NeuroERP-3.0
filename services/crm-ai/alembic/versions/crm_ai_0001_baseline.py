"""Basis des CRM AI-Schemas aus app.db.models.

Ersetzt die nie angewendeten Vorgaengerrevisionen: sie wichen von den Modellen ab (IDs
varchar statt uuid, Enum-Spalten als varchar, abweichende Tabellen). Indizes, die nur die
Altkette kannte, sind in die Modelle uebernommen. Eigene Versionstabelle siehe env.py.

Revision ID: crm_ai_0001
Revises:
Create Date: 2026-10-26
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "crm_ai_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('crm_ai_experiments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('model_type', sa.Enum('lead_scoring', 'churn_prediction', 'clv_prediction', 'sentiment_analysis', 'intent_classification', 'recommendation', name='crm_ai_experiment_model_type'), nullable=False),
    sa.Column('control_variant', sa.JSON(), nullable=False),
    sa.Column('test_variants', sa.JSON(), nullable=False),
    sa.Column('target_metric', sa.String(length=64), nullable=False),
    sa.Column('minimum_sample_size', sa.Integer(), nullable=False),
    sa.Column('confidence_level', sa.Float(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('winner_variant', sa.String(length=64), nullable=True),
    sa.Column('statistical_significance', sa.Float(), nullable=True),
    sa.Column('effect_size', sa.Float(), nullable=True),
    sa.Column('results_summary', sa.JSON(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_ai_features',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('entity_type', sa.String(length=64), nullable=False),
    sa.Column('data_type', sa.String(length=32), nullable=False),
    sa.Column('source_field', sa.String(length=255), nullable=True),
    sa.Column('transformation', sa.String(length=64), nullable=True),
    sa.Column('parameters', sa.JSON(), nullable=False),
    sa.Column('min_value', sa.Float(), nullable=True),
    sa.Column('max_value', sa.Float(), nullable=True),
    sa.Column('mean_value', sa.Float(), nullable=True),
    sa.Column('std_deviation', sa.Float(), nullable=True),
    sa.Column('categories', sa.JSON(), nullable=False),
    sa.Column('usage_count', sa.Integer(), nullable=False),
    sa.Column('last_used', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_ai_models',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.Enum('lead_scoring', 'churn_prediction', 'clv_prediction', 'sentiment_analysis', 'intent_classification', 'recommendation', name='crm_ai_model_type'), nullable=False),
    sa.Column('algorithm', sa.Enum('random_forest', 'gradient_boosting', 'neural_network', 'logistic_regression', 'svm', 'transformer', name='crm_ai_algorithm_type'), nullable=False),
    sa.Column('status', sa.Enum('training', 'ready', 'failed', 'deprecated', name='crm_ai_model_status'), nullable=False),
    sa.Column('version', sa.String(length=32), nullable=False),
    sa.Column('accuracy', sa.Float(), nullable=True),
    sa.Column('precision', sa.Float(), nullable=True),
    sa.Column('recall', sa.Float(), nullable=True),
    sa.Column('f1_score', sa.Float(), nullable=True),
    sa.Column('hyperparameters', sa.JSON(), nullable=False),
    sa.Column('feature_importance', sa.JSON(), nullable=False),
    sa.Column('training_data_info', sa.JSON(), nullable=False),
    sa.Column('model_path', sa.String(length=500), nullable=True),
    sa.Column('model_size_bytes', sa.Integer(), nullable=True),
    sa.Column('last_used', sa.DateTime(), nullable=True),
    sa.Column('usage_count', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_ai_predictions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('model_id', sa.UUID(), nullable=False),
    sa.Column('entity_id', sa.UUID(), nullable=False),
    sa.Column('entity_type', sa.String(length=64), nullable=False),
    sa.Column('score', sa.Float(), nullable=False),
    sa.Column('prediction_class', sa.String(length=64), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=False),
    sa.Column('features', sa.JSON(), nullable=False),
    sa.Column('feature_importance', sa.JSON(), nullable=False),
    sa.Column('model_version', sa.String(length=32), nullable=False),
    sa.Column('prediction_type', sa.String(length=64), nullable=False),
    sa.Column('cached_until', sa.DateTime(), nullable=True),
    sa.Column('computation_time_ms', sa.Integer(), nullable=True),
    sa.Column('actual_outcome', sa.String(length=64), nullable=True),
    sa.Column('feedback_score', sa.Float(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['model_id'], ['crm_ai_models.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_ai_feedback',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('prediction_id', sa.UUID(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('feedback_type', sa.String(length=32), nullable=False),
    sa.Column('user_id', sa.String(length=64), nullable=True),
    sa.Column('context_data', sa.JSON(), nullable=False),
    sa.Column('corrected_prediction', sa.String(length=255), nullable=True),
    sa.Column('feature_adjustments', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['prediction_id'], ['crm_ai_predictions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('crm_ai_feedback')
    op.drop_table('crm_ai_predictions')
    op.drop_table('crm_ai_models')
    op.drop_table('crm_ai_features')
    op.drop_table('crm_ai_experiments')
    sa.Enum(name='crm_ai_algorithm_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_ai_experiment_model_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_ai_model_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_ai_model_type').drop(op.get_bind(), checkfirst=True)
