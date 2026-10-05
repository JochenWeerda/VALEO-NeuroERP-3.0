"""Organisationseinheiten und Zeitkontokorrekturen — zwei fehlende Tabellen.

`domain_hr.org_units` und `domain_hr.time_account_adjustments` existierten in
keiner Datenbank. Das Organigramm antwortete auf allen vier Wegen 503, und jede
Saldokorrektur ebenso. Beide Faecher sind nachweispflichtig: Das Organigramm
traegt die Kostenstellenzuordnung, das Zeitkonto die Grundlage der
Ueberstundenabrechnung (§ 16 Abs. 2 ArbZG).

Drei Entscheidungen stecken im Schema:

**Der Zyklenschutz.** Die Lesewege des Organigramms sind rekursive CTEs; ein
Zyklus im Baum laeuft endlos. ``CHECK (parent_id <> id)`` deckt den trivialen
Fall. Tiefere Zyklen kann eine Pruefbedingung nicht sehen — dort greift eine
Tiefengrenze im Leseweg, und wird sie erreicht, ist das ein Fehler mit
Begruendung und kein stillschweigend gekuerzter Baum.

**Die Kostenstelle ist eine Beziehung**, kein Textfeld: `ON DELETE RESTRICT` auf
`domain_finance.kostenstellen`. Dass sie dem **eigenen** Mandanten gehoeren muss,
kann ein Fremdschluessel allein nicht sagen; das prueft der Schreibweg.

**Eine Korrektur ohne Grund gibt es nicht.** ``delta_hours <> 0`` (eine Korrektur
um null ist keine) und ein nicht leerer Grund. Eine Aenderung am Zeitkonto ohne
Begruendung ist nicht nachvollziehbar.

Revision ID: personal_organisation_zeitkonto_20261006
Revises: zusammenfuehrung_20261005_preis_journal
Create Date: 2026-10-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "personal_organisation_zeitkonto_20261006"
down_revision = "zusammenfuehrung_20261005_preis_journal"
branch_labels = None
depends_on = None

#: Arten einer Organisationseinheit. Deckungsgleich mit dem Schema des Weges.
EINHEITSARTEN = ("ABTEILUNG", "TEAM", "STANDORT", "KOSTENSTELLE", "GESCHAEFTSBEREICH")


def _liste(werte: tuple[str, ...]) -> str:
    return ", ".join(f"'{wert}'" for wert in werte)


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_hr")

    op.create_table(
        "org_units",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("unit_code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("unit_type", sa.String(30), nullable=False, server_default="ABTEILUNG"),
        sa.Column("parent_id", sa.String(36), nullable=True),
        sa.Column("cost_center_id", sa.String(36), nullable=True),
        sa.Column("manager_ref", sa.String(80), nullable=True),
        sa.Column("aktiv", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        # Eine Einheit mit Untereinheiten verschwindet nicht einfach.
        sa.ForeignKeyConstraint(
            ["parent_id"], ["domain_hr.org_units.id"],
            name="fk_orgeinheit_eltern", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["cost_center_id"], ["domain_finance.kostenstellen.id"],
            name="fk_orgeinheit_kostenstelle", ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            f"unit_type IN ({_liste(EINHEITSARTEN)})", name="ck_orgeinheit_art"
        ),
        # Der triviale Zyklus. Tiefere sieht keine Pruefbedingung — dafuer hat der
        # Leseweg eine Tiefengrenze.
        sa.CheckConstraint("parent_id IS NULL OR parent_id <> id", name="ck_orgeinheit_nicht_sich"),
        sa.CheckConstraint("LENGTH(TRIM(name)) > 0", name="ck_orgeinheit_name_gefuellt"),
        schema="domain_hr",
    )

    # Der Einheitenschluessel ist die Bezeichnung, unter der im Haus ueber die
    # Einheit gesprochen wird — je Mandant eindeutig.
    op.create_index(
        "ux_orgeinheit_code",
        "org_units",
        ["tenant_id", "unit_code"],
        unique=True,
        schema="domain_hr",
    )
    op.create_index(
        "ix_orgeinheit_eltern",
        "org_units",
        ["tenant_id", "parent_id"],
        schema="domain_hr",
    )

    op.create_table(
        "time_account_adjustments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("employee_ref", sa.String(80), nullable=False),
        sa.Column("delta_hours", sa.Numeric(8, 2), nullable=False),
        sa.Column("reason", sa.String(400), nullable=False),
        sa.Column("adjustment_date", sa.Date(), nullable=False),
        sa.Column("erfasst_durch", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        # Eine Korrektur um null Stunden ist keine Korrektur.
        sa.CheckConstraint("delta_hours <> 0", name="ck_zeitkorrektur_wirksam"),
        # Eine Aenderung am Zeitkonto ohne Begruendung ist nicht nachvollziehbar
        # (§ 16 Abs. 2 ArbZG, GoBD Rz. 30 ff.).
        sa.CheckConstraint("LENGTH(TRIM(reason)) > 0", name="ck_zeitkorrektur_begruendet"),
        schema="domain_hr",
    )

    op.create_index(
        "ix_zeitkorrektur_mitarbeiter",
        "time_account_adjustments",
        ["tenant_id", "employee_ref", "adjustment_date"],
        schema="domain_hr",
    )


def downgrade() -> None:
    verbindung = op.get_bind()
    for tabelle, was in (
        ("time_account_adjustments", "Zeitkontokorrekturen"),
        ("org_units", "Organisationseinheiten"),
    ):
        anzahl = verbindung.execute(
            sa.text(f"SELECT COUNT(*) FROM domain_hr.{tabelle}")  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        ).scalar()
        if anzahl:
            raise RuntimeError(
                f"domain_hr.{tabelle} fuehrt {anzahl} {was}. Zeitkonto und "
                "Organigramm sind nachweispflichtig und werden nicht per "
                "Downgrade geleert."
            )
    op.drop_index("ix_zeitkorrektur_mitarbeiter", table_name="time_account_adjustments",
                  schema="domain_hr")
    op.drop_table("time_account_adjustments", schema="domain_hr")
    op.drop_index("ix_orgeinheit_eltern", table_name="org_units", schema="domain_hr")
    op.drop_index("ux_orgeinheit_code", table_name="org_units", schema="domain_hr")
    op.drop_table("org_units", schema="domain_hr")
