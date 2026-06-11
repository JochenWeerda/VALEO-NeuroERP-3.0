"""DOM-DOC-004.2 — Artefakt-Versionierung + Freigabe-Status.

Revision ID: doc_artifact_version_20260611
Revises: sales_delivery_storno_20260611

Ergänzt domain_docflow.document_artifacts um ``version`` (laufende Versionsnummer je
Header/Artefakttyp) und ``freigabe_status`` (entwurf→freigegeben→archiviert) inkl.
Freigabe-Audit. Idempotent (``ADD COLUMN IF NOT EXISTS``).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "doc_artifact_version_20260611"
down_revision: Union[str, Sequence[str], None] = "sales_delivery_storno_20260611"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE domain_docflow.document_artifacts "
        "ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1, "
        "ADD COLUMN IF NOT EXISTS freigabe_status VARCHAR(20) NOT NULL DEFAULT 'entwurf', "
        "ADD COLUMN IF NOT EXISTS freigegeben_at TIMESTAMPTZ, "
        "ADD COLUMN IF NOT EXISTS freigegeben_by VARCHAR(100);"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE domain_docflow.document_artifacts "
        "DROP COLUMN IF EXISTS freigegeben_by, "
        "DROP COLUMN IF EXISTS freigegeben_at, "
        "DROP COLUMN IF EXISTS freigabe_status, "
        "DROP COLUMN IF EXISTS version;"
    )
