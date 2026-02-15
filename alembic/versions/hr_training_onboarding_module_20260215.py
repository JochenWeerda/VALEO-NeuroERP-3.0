"""hr training/qualification/onboarding module

Revision ID: hr_training_onboarding_module_20260215
Revises: controlling_module_initial_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "hr_training_onboarding_module_20260215"
down_revision = "controlling_module_initial_20260215"
branch_labels = None
depends_on = None

DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_hr"))

    op.create_table(
        "training_courses",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("course_code", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("topic", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("mandatory", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("validity_months", sa.Integer(), nullable=True),
        sa.Column("provider", sa.String(length=120), nullable=True),
        sa.Column("delivery_mode", sa.String(length=30), nullable=False, server_default=sa.text("'classroom'")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "course_code", name="uq_hr_training_courses_tenant_course_code"),
        sa.CheckConstraint(
            "delivery_mode IN ('classroom','elearning','blended','external')",
            name="ck_hr_training_courses_delivery_mode",
        ),
        sa.CheckConstraint(
            "validity_months IS NULL OR validity_months >= 0",
            name="ck_hr_training_courses_validity_months_non_negative",
        ),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hr_training_courses_tenant_active",
        "training_courses",
        ["tenant_id", "is_active"],
        unique=False,
        schema="domain_hr",
    )

    op.create_table(
        "training_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("employee_ref", sa.String(length=80), nullable=False),
        sa.Column("assigned_by", sa.String(length=80), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'assigned'")),
        sa.Column("score_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_url", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["domain_hr.training_courses.id"],
            ondelete="CASCADE",
            name="fk_hr_training_assignments_course",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "course_id",
            "employee_ref",
            name="uq_hr_training_assignments_tenant_course_employee",
        ),
        sa.CheckConstraint(
            "status IN ('assigned','in_progress','completed','overdue','waived')",
            name="ck_hr_training_assignments_status",
        ),
        sa.CheckConstraint(
            "score_percent IS NULL OR (score_percent >= 0 AND score_percent <= 100)",
            name="ck_hr_training_assignments_score_range",
        ),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hr_training_assignments_tenant_employee",
        "training_assignments",
        ["tenant_id", "employee_ref", "status"],
        unique=False,
        schema="domain_hr",
    )

    op.create_table(
        "employee_certificates",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("employee_ref", sa.String(length=80), nullable=False),
        sa.Column("certificate_type", sa.String(length=80), nullable=False),
        sa.Column("certificate_name", sa.String(length=160), nullable=False),
        sa.Column("certificate_number", sa.String(length=120), nullable=True),
        sa.Column("issuer", sa.String(length=160), nullable=True),
        sa.Column("issued_at", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'valid'")),
        sa.Column("document_url", sa.String(length=255), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('valid','expired','revoked','pending_renewal')",
            name="ck_hr_employee_certificates_status",
        ),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hr_employee_certificates_tenant_employee",
        "employee_certificates",
        ["tenant_id", "employee_ref", "status"],
        unique=False,
        schema="domain_hr",
    )
    op.create_index(
        "idx_hr_employee_certificates_valid_until",
        "employee_certificates",
        ["tenant_id", "valid_until"],
        unique=False,
        schema="domain_hr",
    )

    op.create_table(
        "qualification_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("employee_ref", sa.String(length=80), nullable=False),
        sa.Column("role_code", sa.String(length=80), nullable=False),
        sa.Column("qualification_level", sa.String(length=40), nullable=False, server_default=sa.text("'basic'")),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "employee_ref",
            "role_code",
            name="uq_hr_qualification_profiles_tenant_employee_role",
        ),
        sa.CheckConstraint(
            "qualification_level IN ('basic','advanced','expert')",
            name="ck_hr_qualification_profiles_level",
        ),
        schema="domain_hr",
    )

    op.create_table(
        "onboarding_checklists",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("checklist_code", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("role_scope", sa.String(length=80), nullable=True),
        sa.Column("tasks", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "checklist_code", name="uq_hr_onboarding_checklists_tenant_code"),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hr_onboarding_checklists_tenant_active",
        "onboarding_checklists",
        ["tenant_id", "is_active"],
        unique=False,
        schema="domain_hr",
    )

    op.create_table(
        "onboarding_runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("checklist_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("employee_ref", sa.String(length=80), nullable=False),
        sa.Column("assigned_by", sa.String(length=80), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'not_started'")),
        sa.Column("progress_percent", sa.Numeric(5, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["checklist_id"],
            ["domain_hr.onboarding_checklists.id"],
            ondelete="CASCADE",
            name="fk_hr_onboarding_runs_checklist",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "checklist_id",
            "employee_ref",
            name="uq_hr_onboarding_runs_tenant_checklist_employee",
        ),
        sa.CheckConstraint(
            "status IN ('not_started','in_progress','completed','cancelled')",
            name="ck_hr_onboarding_runs_status",
        ),
        sa.CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="ck_hr_onboarding_runs_progress",
        ),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hr_onboarding_runs_tenant_employee",
        "onboarding_runs",
        ["tenant_id", "employee_ref", "status"],
        unique=False,
        schema="domain_hr",
    )

    op.execute(
        sa.text(
            f"""
            INSERT INTO domain_hr.training_courses
              (id, tenant_id, course_code, title, topic, description, mandatory, validity_months, provider, delivery_mode, metadata, is_active)
            VALUES
              ('f95d2f0d-2f6a-4d84-a004-cf8b84f62f3a', '{DEFAULT_TENANT_ID}', 'ONB-BASE-001', 'Onboarding Basis', 'onboarding', 'Pflicht-Onboarding fuer neue Mitarbeitende', TRUE, 0, 'Internal Academy', 'blended', '{{"scope":"all_new_hires"}}', TRUE),
              ('7ad22a61-5558-4f5e-a1ca-8d8f2c7f8b4f', '{DEFAULT_TENANT_ID}', 'QS-HACCP-001', 'QS/HACCP Grundschulung', 'quality', 'QS-Leitfaden und HACCP Grundlagen', TRUE, 12, 'QS Team', 'classroom', '{{"module":"agrar"}}', TRUE)
            ON CONFLICT (tenant_id, course_code) DO NOTHING;
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            INSERT INTO domain_hr.onboarding_checklists
              (id, tenant_id, checklist_code, title, description, role_scope, tasks, is_active)
            VALUES
              (
                '2ea75826-2e37-469b-81fa-cf2d02f4b50e',
                '{DEFAULT_TENANT_ID}',
                'ONB-SALES-STD',
                'Onboarding Vertrieb Standard',
                'Standard-Checkliste fuer Vertrieb und Kundenservice',
                'sales',
                jsonb_build_array(
                  jsonb_build_object('key', 'it_access', 'title', 'IT-Zugaenge bereitstellen', 'mandatory', true),
                  jsonb_build_object('key', 'product_training', 'title', 'Produktschulung abschliessen', 'mandatory', true),
                  jsonb_build_object('key', 'process_walkthrough', 'title', 'Order-to-Cash Prozesslauf', 'mandatory', true)
                ),
                TRUE
              )
            ON CONFLICT (tenant_id, checklist_code) DO NOTHING;
            """
        )
    )


def downgrade() -> None:
    op.drop_index("idx_hr_onboarding_runs_tenant_employee", table_name="onboarding_runs", schema="domain_hr")
    op.drop_table("onboarding_runs", schema="domain_hr")

    op.drop_index(
        "idx_hr_onboarding_checklists_tenant_active",
        table_name="onboarding_checklists",
        schema="domain_hr",
    )
    op.drop_table("onboarding_checklists", schema="domain_hr")

    op.drop_table("qualification_profiles", schema="domain_hr")

    op.drop_index(
        "idx_hr_employee_certificates_valid_until",
        table_name="employee_certificates",
        schema="domain_hr",
    )
    op.drop_index(
        "idx_hr_employee_certificates_tenant_employee",
        table_name="employee_certificates",
        schema="domain_hr",
    )
    op.drop_table("employee_certificates", schema="domain_hr")

    op.drop_index(
        "idx_hr_training_assignments_tenant_employee",
        table_name="training_assignments",
        schema="domain_hr",
    )
    op.drop_table("training_assignments", schema="domain_hr")

    op.drop_index(
        "idx_hr_training_courses_tenant_active",
        table_name="training_courses",
        schema="domain_hr",
    )
    op.drop_table("training_courses", schema="domain_hr")
