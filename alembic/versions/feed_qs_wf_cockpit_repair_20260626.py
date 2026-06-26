"""FEED-QS-001 + WF-COCKPIT-002: Futtermittel-QS-Tabellen + domain_workflow sicherstellen.

  domain_shared — futtermittel_haccp_plaene, futtermittel_vlog_meldungen,
                  futtermittel_qs_pruefpunkte

  domain_workflow — wf_cockpit_instances, wf_cockpit_events, wf_cockpit_blockers
                    (ADD COLUMN IF NOT EXISTS fuer bereits angelegte Varianten)

Revision ID: feed_qs_wf_cockpit_repair_20260626
Revises: final_single_head_merge_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text


revision = "feed_qs_wf_cockpit_repair_20260626"
down_revision = "final_single_head_merge_20260626"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_shared"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_workflow"))

    # ── Futtermittel HACCP-Plaene ─────────────────────────────────────────────

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.futtermittel_haccp_plaene (
            id              TEXT        PRIMARY KEY,
            tenant_id       TEXT        NOT NULL,
            bezeichnung     TEXT        NOT NULL,
            gueltigkeit_von DATE        NOT NULL,
            gueltigkeit_bis DATE,
            gefahrenanalyse JSONB       NOT NULL DEFAULT '[]'::jsonb,
            ccp_liste       JSONB       NOT NULL DEFAULT '[]'::jsonb,
            ueberwachung    JSONB       NOT NULL DEFAULT '[]'::jsonb,
            korrekturen     JSONB       NOT NULL DEFAULT '[]'::jsonb,
            verifizierung   JSONB       NOT NULL DEFAULT '{}'::jsonb,
            aktiv           BOOLEAN     NOT NULL DEFAULT TRUE,
            erstellt_am     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            geaendert_am    TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_futtermittel_haccp_plaene_tenant
            ON domain_shared.futtermittel_haccp_plaene (tenant_id, aktiv)
    """))

    # ── Futtermittel VLOG-Meldungen ───────────────────────────────────────────

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.futtermittel_vlog_meldungen (
            id              TEXT        PRIMARY KEY,
            tenant_id       TEXT        NOT NULL,
            rezeptur_id     TEXT,
            meldedatum      DATE        NOT NULL,
            menge_kg        NUMERIC(14,3) NOT NULL DEFAULT 0,
            rohstoff_liste  JSONB       NOT NULL DEFAULT '[]'::jsonb,
            gvo_frei        BOOLEAN     NOT NULL DEFAULT TRUE,
            zertifikat_nr   TEXT,
            status          TEXT        NOT NULL DEFAULT 'erstellt',
            notiz           TEXT,
            erstellt_am     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            geaendert_am    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT futtermittel_vlog_status_ck
                CHECK (status IN ('erstellt','gesendet','bestaetigt','abgelehnt'))
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_futtermittel_vlog_tenant_datum
            ON domain_shared.futtermittel_vlog_meldungen (tenant_id, meldedatum)
    """))

    # ── Futtermittel QS-Leitfaden-Pruefpunkte ────────────────────────────────

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.futtermittel_qs_pruefpunkte (
            id              TEXT        PRIMARY KEY,
            tenant_id       TEXT        NOT NULL,
            periode         TEXT        NOT NULL,
            kategorie       TEXT        NOT NULL DEFAULT 'allgemein',
            punkt_nr        TEXT        NOT NULL,
            bezeichnung     TEXT        NOT NULL,
            anforderung     TEXT        NOT NULL DEFAULT '',
            bestaetigt      BOOLEAN     NOT NULL DEFAULT FALSE,
            abweichung      TEXT,
            massnahme       TEXT,
            bestaetigt_am   TIMESTAMPTZ,
            bestaetigt_von  TEXT,
            erstellt_am     TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_futtermittel_qs_pruefpunkte_tenant_periode
            ON domain_shared.futtermittel_qs_pruefpunkte (tenant_id, periode, kategorie)
    """))

    # ── domain_workflow — Cockpit-Tabellen sicherstellen ──────────────────────
    # (wf_cockpit_persist_service.py erwartet diese; Parallel-Branch moeglicherweise
    #  noch nicht auf allen Instanzen gelaufen)

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_workflow.wf_cockpit_instances (
            id                      TEXT        NOT NULL PRIMARY KEY,
            tenant_id               TEXT        NOT NULL,
            process_key             TEXT        NOT NULL,
            status                  TEXT        NOT NULL DEFAULT 'running',
            correlation_id          TEXT        NOT NULL,
            idempotency_key         TEXT,
            business_object_ref     TEXT,
            current_step            TEXT,
            audit_ref               TEXT,
            active_blocker_count    INTEGER     NOT NULL DEFAULT 0,
            replayable              BOOLEAN     NOT NULL DEFAULT FALSE,
            started_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            finished_at             TIMESTAMPTZ
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_wf_cockpit_instances_tenant_status
            ON domain_workflow.wf_cockpit_instances (tenant_id, status)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_wf_cockpit_instances_process_key
            ON domain_workflow.wf_cockpit_instances (tenant_id, process_key, started_at)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_workflow.wf_cockpit_events (
            id                      TEXT        NOT NULL PRIMARY KEY,
            tenant_id               TEXT        NOT NULL,
            process_instance_id     TEXT        NOT NULL,
            kind                    TEXT        NOT NULL DEFAULT 'domain_event',
            message                 TEXT        NOT NULL DEFAULT '',
            source                  TEXT,
            payload                 JSONB,
            occurred_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_wf_cockpit_events_instance
            ON domain_workflow.wf_cockpit_events (process_instance_id, occurred_at)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_wf_cockpit_events_tenant_kind
            ON domain_workflow.wf_cockpit_events (tenant_id, kind, occurred_at)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_workflow.wf_cockpit_blockers (
            id                      TEXT        NOT NULL PRIMARY KEY,
            tenant_id               TEXT        NOT NULL,
            process_instance_id     TEXT        NOT NULL,
            blocker_type            TEXT        NOT NULL DEFAULT 'BLOCKED_EXTERNAL_GATE',
            reason                  TEXT        NOT NULL DEFAULT '',
            context                 JSONB,
            resolved                BOOLEAN     NOT NULL DEFAULT FALSE,
            resolved_at             TIMESTAMPTZ,
            resolved_by             TEXT,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_wf_cockpit_blockers_instance
            ON domain_workflow.wf_cockpit_blockers (process_instance_id, resolved)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_wf_cockpit_blockers_tenant_unresolved
            ON domain_workflow.wf_cockpit_blockers (tenant_id, resolved, created_at)
    """))


def downgrade() -> None:
    pass
