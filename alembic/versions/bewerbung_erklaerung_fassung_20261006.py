"""Die Einwilligungserklaerung in Fassungen — welchem Wortlaut zugestimmt wurde.

Seit `bewerbung_einwilligung_20261006` traegt jede Erteilung ihren Wortlaut als
**freien Text**. Jede Erteilung kann einen anderen Text haben, und niemand merkt es;
ein Tippfehler im Personalbuero erzeugt still eine neue "Erklaerung". Nachweisbar
(Art. 7 Abs. 1 DSGVO) ist eine Einwilligung erst, wenn feststeht, **welcher Fassung**
zugestimmt wurde — und dass diese Fassung sich seitdem nicht geaendert hat.

* `domain_hr.bewerbung_einwilligungserklaerungen` — je Mandant fortlaufende
  `fassung` mit `wortlaut`. **Unveraenderlich** (Trigger gegen jedes UPDATE): Wer
  eine Fassung aendert, aendert rueckwirkend, wozu alle frueheren Bewerber
  eingewilligt haben. Loeschbar nur, solange keine Erteilung darauf verweist — eine
  nie benutzte Fassung belegt nichts. Derselbe Wortlaut ist **eine** Fassung.
  Kein Personenbezug: Die Fassung bleibt, wenn eine Bewerbung geloescht wird, denn
  andere koennen demselben Text zugestimmt haben.
* `bewerbung_einwilligungen.erklaerung_id` ersetzt `einwilligungstext`. Bestandszeilen
  werden in Fassungen ueberfuehrt (je Mandant in der Reihenfolge ihrer ersten
  Verwendung), dann entfaellt die freie Spalte: Der Wortlaut steht an **einer**
  Stelle. Der Fremdschluessel ist zusammengesetzt (`tenant_id`, `erklaerung_id`) —
  eine Erteilung kann nicht auf die Fassung eines anderen Mandanten zeigen, auch
  nicht per direktem SQL.

Keine vorhandene Tabelle passt: `business_partners.privacy_policy_version` ist ein
Etikett ohne Text, und die CRM-Einwilligungen beschreiben die Erlaubnis,
angesprochen zu werden (siehe Vormigration).

Revision ID: bewerbung_erklaerung_fassung_20261006
Revises: bewerbung_einwilligung_20261006
Create Date: 2026-10-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "bewerbung_erklaerung_fassung_20261006"
down_revision = "bewerbung_einwilligung_20261006"
branch_labels = None
depends_on = None

#: Wer die Bestandszeilen ueberfuehrt hat — kein Mensch, und das soll man sehen.
UEBERNOMMEN_DURCH = "Migration: aus freiem Text uebernommen"


def upgrade() -> None:
    op.create_table(
        "bewerbung_einwilligungserklaerungen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        # 1, 2, 3 … je Mandant. Die Nummer steht auf dem Formular, das der Bewerber
        # unterschreibt; deshalb ist sie fachlich und nicht die technische Kennung.
        sa.Column("fassung", sa.Integer(), nullable=False),
        sa.Column("wortlaut", sa.Text(), nullable=False),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("erstellt_durch", sa.String(120), nullable=True),
        sa.UniqueConstraint("tenant_id", "fassung", name="uq_beweinwerk_fassung"),
        # Ziel des zusammengesetzten Fremdschluessels aus dem Verzeichnis.
        sa.UniqueConstraint("tenant_id", "id", name="uq_beweinwerk_tenant_id"),
        sa.CheckConstraint("fassung > 0", name="ck_beweinwerk_fassung_positiv"),
        # Randleerzeichen machen keinen anderen Text — gespeichert wird getrimmt,
        # damit "derselbe Wortlaut" in der Datenbank dasselbe heisst wie im Dienst.
        sa.CheckConstraint(
            "wortlaut = BTRIM(wortlaut, E' \\t\\r\\n') AND LENGTH(wortlaut) > 0",
            name="ck_beweinwerk_wortlaut",
        ),
        schema="domain_hr",
    )
    # Derselbe Wortlaut ist eine Fassung. md5 statt des Textes selbst: Ein B-Baum
    # nimmt keine beliebig langen Werte auf.
    op.execute(
        "CREATE UNIQUE INDEX uq_beweinwerk_wortlaut "
        "ON domain_hr.bewerbung_einwilligungserklaerungen (tenant_id, md5(wortlaut))"
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION domain_hr.bewerbung_erklaerung_unveraenderlich()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION
                'Fassung % der Einwilligungserklaerung ist unveraenderlich: Wer sie '
                'aendert, aendert rueckwirkend, wozu fruehere Bewerber eingewilligt '
                'haben. Ein neuer Wortlaut ist eine neue Fassung.', OLD.fassung
                USING ERRCODE = 'integrity_constraint_violation';
        END;
        $$
        """
    )
    op.execute(
        "CREATE TRIGGER trg_bewerbung_erklaerung_unveraenderlich "
        "BEFORE UPDATE ON domain_hr.bewerbung_einwilligungserklaerungen "
        "FOR EACH ROW EXECUTE FUNCTION domain_hr.bewerbung_erklaerung_unveraenderlich()"
    )

    op.add_column(
        "bewerbung_einwilligungen",
        sa.Column("erklaerung_id", sa.String(36), nullable=True),
        schema="domain_hr",
    )

    # Bestand ueberfuehren: je Mandant ein Wortlaut, eine Fassung, nummeriert in der
    # Reihenfolge der ersten Verwendung. Nichts wird erfunden — der Text ist der,
    # der schon dastand.
    op.execute(
        sa.text(
            """
            INSERT INTO domain_hr.bewerbung_einwilligungserklaerungen
                (id, tenant_id, fassung, wortlaut, erstellt_am, erstellt_durch)
            SELECT gen_random_uuid()::text, tenant_id,
                   ROW_NUMBER() OVER (PARTITION BY tenant_id ORDER BY zuerst, wortlaut),
                   wortlaut, zuerst, :durch
            FROM (
                SELECT tenant_id,
                       BTRIM(einwilligungstext, E' \\t\\r\\n') AS wortlaut,
                       MIN(erfolgt_am) AS zuerst
                FROM domain_hr.bewerbung_einwilligungen
                WHERE vorgang = 'ERTEILT'
                GROUP BY tenant_id, BTRIM(einwilligungstext, E' \\t\\r\\n')
            ) bestand
            """
        ).bindparams(durch=UEBERNOMMEN_DURCH)
    )
    op.execute(
        """
        UPDATE domain_hr.bewerbung_einwilligungen v
        SET erklaerung_id = e.id
        FROM domain_hr.bewerbung_einwilligungserklaerungen e
        WHERE v.vorgang = 'ERTEILT'
          AND e.tenant_id = v.tenant_id
          AND e.wortlaut = BTRIM(v.einwilligungstext, E' \\t\\r\\n')
        """
    )

    op.drop_constraint(
        "ck_beweinw_erteilung_mit_wortlaut", "bewerbung_einwilligungen", schema="domain_hr"
    )
    op.drop_column("bewerbung_einwilligungen", "einwilligungstext", schema="domain_hr")
    op.create_foreign_key(
        "fk_beweinw_erklaerung",
        "bewerbung_einwilligungen",
        "bewerbung_einwilligungserklaerungen",
        ["tenant_id", "erklaerung_id"],
        ["tenant_id", "id"],
        source_schema="domain_hr",
        referent_schema="domain_hr",
        ondelete="RESTRICT",
    )
    # Eine Erteilung genau dann mit Fassung; ein Widerruf braucht keine — er
    # braucht **nichts** (Art. 7 Abs. 3).
    op.create_check_constraint(
        "ck_beweinw_erteilung_mit_fassung",
        "bewerbung_einwilligungen",
        "(vorgang = 'ERTEILT') = (erklaerung_id IS NOT NULL)",
        schema="domain_hr",
    )
    op.create_index(
        "ix_beweinw_erklaerung",
        "bewerbung_einwilligungen",
        ["tenant_id", "erklaerung_id"],
        schema="domain_hr",
    )


def downgrade() -> None:
    # Der Wortlaut geht nicht verloren: Er wandert aus der Fassung zurueck in jede
    # Erteilung, die auf sie verwies.
    op.add_column(
        "bewerbung_einwilligungen",
        sa.Column("einwilligungstext", sa.Text(), nullable=True),
        schema="domain_hr",
    )
    op.execute(
        """
        UPDATE domain_hr.bewerbung_einwilligungen v
        SET einwilligungstext = e.wortlaut
        FROM domain_hr.bewerbung_einwilligungserklaerungen e
        WHERE e.id = v.erklaerung_id AND e.tenant_id = v.tenant_id
        """
    )
    op.drop_index(
        "ix_beweinw_erklaerung", table_name="bewerbung_einwilligungen", schema="domain_hr"
    )
    op.drop_constraint(
        "ck_beweinw_erteilung_mit_fassung", "bewerbung_einwilligungen", schema="domain_hr"
    )
    op.drop_constraint(
        "fk_beweinw_erklaerung", "bewerbung_einwilligungen", schema="domain_hr"
    )
    op.drop_column("bewerbung_einwilligungen", "erklaerung_id", schema="domain_hr")
    op.create_check_constraint(
        "ck_beweinw_erteilung_mit_wortlaut",
        "bewerbung_einwilligungen",
        "vorgang <> 'ERTEILT' OR LENGTH(TRIM(COALESCE(einwilligungstext, ''))) > 0",
        schema="domain_hr",
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trg_bewerbung_erklaerung_unveraenderlich "
        "ON domain_hr.bewerbung_einwilligungserklaerungen"
    )
    op.execute("DROP FUNCTION IF EXISTS domain_hr.bewerbung_erklaerung_unveraenderlich()")
    op.drop_table("bewerbung_einwilligungserklaerungen", schema="domain_hr")
