"""Postfaecher: Anbieter Microsoft 365.

Revision ID: postfach_microsoft_20261008
Revises: mailkonto_mandant_20261008

Microsoft 365 versendet ueber Microsoft Graph (``sendMail``) mit einer delegierten
OAuth-Anmeldung; das Geheimnis ist der Refresh-Token (verschluesselt wie alle).
"""

from alembic import op

revision = "postfach_microsoft_20261008"
down_revision = "mailkonto_mandant_20261008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_shared.mailkonten DROP CONSTRAINT IF EXISTS ck_mailkonto_anbieter")
    op.execute(
        "ALTER TABLE domain_shared.mailkonten ADD CONSTRAINT ck_mailkonto_anbieter "
        "CHECK (anbieter IN ('smtp', 'ionos', 'google', 'microsoft', 'alias'))"
    )
    # Microsoft 365 nur mit Anmeldung ueber Microsoft (kein Passwort-SMTP).
    op.execute("ALTER TABLE domain_shared.mailkonten DROP CONSTRAINT IF EXISTS ck_mailkonto_microsoft_oauth")
    op.execute(
        "ALTER TABLE domain_shared.mailkonten ADD CONSTRAINT ck_mailkonto_microsoft_oauth "
        "CHECK (anbieter <> 'microsoft' OR anmeldung = 'oauth2')"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE domain_shared.mailkonten DROP CONSTRAINT IF EXISTS ck_mailkonto_microsoft_oauth")
    op.execute("ALTER TABLE domain_shared.mailkonten DROP CONSTRAINT IF EXISTS ck_mailkonto_anbieter")
    op.execute(
        "ALTER TABLE domain_shared.mailkonten ADD CONSTRAINT ck_mailkonto_anbieter "
        "CHECK (anbieter IN ('smtp', 'ionos', 'google', 'alias'))"
    )
