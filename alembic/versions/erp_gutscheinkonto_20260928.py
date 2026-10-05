"""Gutscheine bekommen ein eigenes Konto.

Der Kassendienst buchte ausgegebene und eingeloeste Gutscheine auf 1600 —
dort liegen die Verbindlichkeiten aus Lieferungen und Leistungen, also das,
was wir Lieferanten schulden. Ein ausgegebener Gutschein ist etwas anderes:
eine Leistungsverpflichtung gegenueber einem Kunden.

Beides auf einem Konto heisst, dass weder der Lieferantensaldo noch der
Gutscheinbestand stimmt, und dass keiner von beiden aus dem Konto heraus zu
erklaeren ist. Die GoBD verlangen Klarheit und Nachvollziehbarkeit (Rz. 30
ff.): Ein sachverstaendiger Dritter muss die Geschaeftsvorfaelle in
angemessener Zeit nachvollziehen koennen. Bei einem Mischkonto kann er das
nicht.

1700 liegt im SKR03-Bereich der sonstigen Verbindlichkeiten (1700-1799). Die
genaue Nummer ist eine Verabredung mit der Buchhaltung; die Trennung ist es
nicht.

**Bereits gebuchte Saetze bleiben, wo sie sind.** Die GoBD fordern
Unveraenderbarkeit (Rz. 107 ff.) — eine Umbuchung ist ein Buchungsvorgang mit
eigenem Beleg, kein Datenbankupdate. Diese Migration legt nur das Konto an.

Revision ID: erp_gutscheinkonto_20260928
Revises: erp_kontenrahmen_skr03_20260927
Create Date: 2026-09-28
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op

revision = "erp_gutscheinkonto_20260928"
down_revision = "erp_kontenrahmen_skr03_20260927"
branch_labels = None
depends_on = None

KONTO = "1700"
NAME = "Verbindlichkeiten aus ausgegebenen Gutscheinen"


def upgrade() -> None:
    verbindung = op.get_bind()
    schon_da = verbindung.execute(
        sa.text(
            "SELECT 1 FROM domain_erp.chart_of_accounts "
            "WHERE account_number = :nr AND is_active = TRUE"
        ),
        {"nr": KONTO},
    ).first()
    if schon_da:
        return

    verbindung.execute(
        sa.text(
            "INSERT INTO domain_erp.chart_of_accounts "
            "(id, tenant_id, account_number, account_name, account_type, "
            " category, is_active, description) "
            "VALUES (:id, 'system', :nr, :name, 'liability', "
            "        'current_liabilities', TRUE, :beschreibung)"
        ),
        {
            "id": str(uuid.uuid4()),
            "nr": KONTO,
            "name": NAME,
            "beschreibung": (
                "Getrennt von 1600 (Verbindlichkeiten aus Lieferungen und Leistungen), "
                "weil ein Gutschein eine Leistungsverpflichtung gegenueber dem Kunden ist "
                "und keine Lieferantenschuld. GoBD Rz. 30 ff. (Klarheit). "
                "Nummer von der Buchhaltung zu bestaetigen."
            ),
        },
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa.text(
            "DELETE FROM domain_erp.chart_of_accounts "
            "WHERE account_number = :nr AND tenant_id = 'system'"
        ),
        {"nr": KONTO},
    )
