"""Der Abruf einer kontrahierten Menge — als Tabelle, nicht als Laufzeit-DDL.

`domain_agrar.kontrakt_dispositionen` existierte in keiner Datenbank. Angelegt
wurde sie vom Anwendungscode beim ersten Schreibzugriff
(`CREATE TABLE IF NOT EXISTS`), und der Fehlschlag dieses DDL lief in ein stilles
`except: rollback`. Vor dem ersten POST antwortete das Auflisten `[]`.

Drei Entscheidungen stecken im Schema:

**`freigabe` ist keine Spalte.** Die Freigabe stand als Boolean **und** als
`status = 'FREIGEGEBEN'`. Zwei Wahrheiten ueber denselben Umstand laufen
auseinander, sobald ein Weg nur eine von beiden setzt — und genau das tat der
Lieferweg. Die Freigabe ist jetzt der Zustand.

**Der Wiegeschein ist eine Beziehung.** `wiegeschein_nr` war freier Text. Eine
Lieferung, die sich auf einen Wiegeschein beruft, den es nicht gibt, ist nicht
belegt. Verwiesen wird auf `domain_inventory.weighing_tickets` — den kanonischen
Wiegeschein aus `wiegung_kanonisch_20261005`.

**Die Zustandsregeln stehen in Pruefbedingungen**, soweit sie eine einzelne Zeile
betreffen: Ein Lieferdatum gibt es nur bei `GELIEFERT`, und einen Wiegeschein
auch nur dort.

Revision ID: kontrakt_disposition_20261005
Revises: wiegung_kanonisch_20261005
Create Date: 2026-10-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "kontrakt_disposition_20261005"
down_revision = "wiegung_kanonisch_20261005"
branch_labels = None
depends_on = None

#: Zustaende eines Abrufs. `FREIGEGEBEN` ist das Tor zur Lieferung; `GELIEFERT`
#: und `STORNIERT` sind endgueltig.
ZUSTAENDE = ("OFFEN", "FREIGEGEBEN", "GELIEFERT", "STORNIERT")


def _liste(werte: tuple[str, ...]) -> str:
    return ", ".join(f"'{wert}'" for wert in werte)


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")

    op.create_table(
        "kontrakt_dispositionen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("kontrakt_id", sa.String(36), nullable=False),
        sa.Column("kontrakt_nr", sa.String(60), nullable=False),
        sa.Column("kontrakt_pos_nr", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("disposition_nr", sa.Integer(), nullable=False),
        sa.Column("geplantes_lieferdatum", sa.Date(), nullable=True),
        sa.Column("lieferdatum", sa.Date(), nullable=True),
        sa.Column("menge", sa.Numeric(18, 3), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="OFFEN"),
        # Der Beleg der Lieferung. ON DELETE RESTRICT: Der Wiegeschein darf nicht
        # verschwinden, solange eine Disposition sich auf ihn beruft.
        sa.Column("wiegeschein_id", sa.String(36), nullable=True),
        sa.Column("bemerkung", sa.Text(), nullable=True),
        sa.Column("erfasst_durch", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["wiegeschein_id"], ["domain_inventory.weighing_tickets.id"],
            name="fk_dispo_wiegeschein", ondelete="RESTRICT",
        ),
        sa.CheckConstraint(f"status IN ({_liste(ZUSTAENDE)})", name="ck_dispo_status"),
        # Eine Abrufmenge von null oder weniger ist kein Abruf.
        sa.CheckConstraint("menge > 0", name="ck_dispo_menge_positiv"),
        sa.CheckConstraint("disposition_nr > 0", name="ck_dispo_nummer_positiv"),
        # Ein Lieferdatum gibt es nur bei einer Lieferung — und dann immer.
        sa.CheckConstraint(
            "(status = 'GELIEFERT') = (lieferdatum IS NOT NULL)",
            name="ck_dispo_lieferdatum_bei_lieferung",
        ),
        # Ein Wiegeschein ohne Lieferung waere ein Beleg fuer etwas, das nicht
        # geschehen ist.
        sa.CheckConstraint(
            "wiegeschein_id IS NULL OR status = 'GELIEFERT'",
            name="ck_dispo_wiegeschein_nur_bei_lieferung",
        ),
        schema="domain_agrar",
    )

    # Die laufende Nummer ist je Mandant und Kontrakt eindeutig: Sie ist die
    # Bezeichnung, unter der im Haus ueber den Abruf gesprochen wird.
    op.create_index(
        "ux_dispo_nummer",
        "kontrakt_dispositionen",
        ["tenant_id", "kontrakt_id", "disposition_nr"],
        unique=True,
        schema="domain_agrar",
    )
    # Die Mengenpruefung summiert je Kontraktposition.
    op.create_index(
        "ix_dispo_position",
        "kontrakt_dispositionen",
        ["tenant_id", "kontrakt_id", "kontrakt_pos_nr", "status"],
        schema="domain_agrar",
    )


def downgrade() -> None:
    verbindung = op.get_bind()
    anzahl = verbindung.execute(
        sa.text("SELECT COUNT(*) FROM domain_agrar.kontrakt_dispositionen")
    ).scalar()
    if anzahl:
        raise RuntimeError(
            f"domain_agrar.kontrakt_dispositionen fuehrt {anzahl} Abrufe. Ein "
            "Abruf ist Teil der Kontraktabwicklung und wird nicht per Downgrade "
            "geloescht."
        )
    op.drop_index("ix_dispo_position", table_name="kontrakt_dispositionen", schema="domain_agrar")
    op.drop_index("ux_dispo_nummer", table_name="kontrakt_dispositionen", schema="domain_agrar")
    op.drop_table("kontrakt_dispositionen", schema="domain_agrar")
