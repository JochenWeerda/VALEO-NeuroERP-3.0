"""Das Verzeichnis der Aufbewahrungs-Einwilligungen — Nachweis und Widerruf.

Der Loeschlauf achtet seit `bewerbung_loeschlauf_20261006` eine Einwilligung zur
laengeren Aufbewahrung (Talentpool, Art. 6 Abs. 1 lit. a DSGVO), aber es gab keinen
Weg, sie zu erteilen oder zu widerrufen: Die Spalten waren da und niemand konnte sie
fuellen.

**Art. 7 Abs. 1 DSGVO** verlangt, die Einwilligung **nachweisen** zu koennen. Zwei
Spalten auf `applications` sagen *bis wann* und *seit wann* — nicht **wozu** und
nicht **wie** erteilt. Und nach einem Widerruf stehen sie leer: Dann ist nicht mehr
zu belegen, warum die Daten im abgelaufenen Zeitraum ueberhaupt noch da waren.

**Art. 7 Abs. 3 DSGVO** verlangt, dass der Widerruf jederzeit moeglich ist und nicht
schwerer als die Erteilung. Deshalb ist er hier eine **neue Zeile**, keine Aenderung:
Wer die Erteilung ueberschreibt, vernichtet genau den Nachweis, den Absatz 1
verlangt.

**Warum eine eigene Tabelle, obwohl es drei Einwilligungstabellen gibt.**
`domain_crm.crm_contact_consents` (+ `_history`) und `domain_crm.crm_consents`
haengen an einem CRM-Kontakt bzw. Partner und beschreiben eine **andere Erlaubnis**:
`channel`, `consent_type`, Double-Opt-In — die Erlaubnis, **angesprochen** zu
werden. Hier geht es um die Erlaubnis, Daten **aufzubewahren**. Wer beides
zusammenlegt, laesst einen widerrufenen Werbe-Opt-In wie einen widerrufenen
Aufbewahrungs-Opt-In aussehen. Fuer jeden Bewerber ausserdem einen CRM-Kontakt
anzulegen wuerde Bewerberdaten in den Vertrieb tragen — das Gegenteil von
Datenminimierung.

Das ist die Gegenprobe zur Loeschsperre im Vorslice: Dort war der Begriff
**derselbe** (ein Datensatz, der nicht geloescht werden darf) und
`public.gobd_loeschsperren` wurde wiederverwendet. Hier ist er ein anderer.

Revision ID: bewerbung_einwilligung_20261006
Revises: bewerbung_loeschlauf_20261006
Create Date: 2026-10-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "bewerbung_einwilligung_20261006"
down_revision = "bewerbung_loeschlauf_20261006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bewerbung_einwilligungen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        # Ist der Mensch geloescht, gibt es keine Aufbewahrung mehr zu
        # rechtfertigen — und ein Nachweis, der nur noch den Namen haelt, ist selbst
        # die Speicherung, die beendet werden sollte.
        sa.Column("bewerbung_id", sa.String(36), nullable=False),
        # ERTEILT | WIDERRUFEN. Ein Widerruf ist eine neue Zeile, keine Aenderung.
        sa.Column("vorgang", sa.String(20), nullable=False),
        sa.Column("erfolgt_am", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        # Nur bei der Erteilung: Bis wann die Erlaubnis reicht.
        sa.Column("gueltig_bis", sa.Date(), nullable=True),
        # Nur bei der Erteilung: auf welchem Weg sie einging (Art. 7 Abs. 1 — der
        # Nachweis muss sagen, **wie** eingewilligt wurde). Beim Widerruf bleibt die
        # Spalte leer: Ihn nach dem Weg zu fragen, waere eine Angabe, die die
        # Erteilung nicht verlangt, und damit ein hoeherer Aufwand als dort
        # (Art. 7 Abs. 3). Leer heisst hier "nicht erhoben" — nicht "WEB".
        sa.Column("kanal", sa.String(20), nullable=True),
        # Der Wortlaut, dem zugestimmt wurde. Ohne ihn ist nicht nachweisbar, **wozu**
        # eingewilligt wurde — und eine Einwilligung ohne bestimmten Zweck ist nach
        # Art. 6 Abs. 1 lit. a keine.
        sa.Column("einwilligungstext", sa.Text(), nullable=True),
        sa.Column("erfasst_durch", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["bewerbung_id"],
            ["domain_hr.applications.id"],
            name="fk_beweinw_bewerbung",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "vorgang IN ('ERTEILT', 'WIDERRUFEN')", name="ck_beweinw_vorgang"
        ),
        sa.CheckConstraint(
            "kanal IS NULL OR kanal IN ('WEB', 'E_MAIL', 'PAPIER', 'MUENDLICH')",
            name="ck_beweinw_kanal",
        ),
        sa.CheckConstraint(
            "(vorgang = 'ERTEILT') = (kanal IS NOT NULL)", name="ck_beweinw_kanal_bei_erteilung"
        ),
        # Eine Erteilung braucht ein Ende und einen Wortlaut; ein Widerruf hat
        # beides nicht — er braucht **keinen Grund**, sonst waere er schwerer als
        # die Erteilung (Art. 7 Abs. 3).
        sa.CheckConstraint(
            "(vorgang = 'ERTEILT') = (gueltig_bis IS NOT NULL)",
            name="ck_beweinw_erteilung_befristet",
        ),
        sa.CheckConstraint(
            "vorgang <> 'ERTEILT' OR LENGTH(TRIM(COALESCE(einwilligungstext, ''))) > 0",
            name="ck_beweinw_erteilung_mit_wortlaut",
        ),
        schema="domain_hr",
    )
    op.create_index(
        "ix_beweinw_bewerbung",
        "bewerbung_einwilligungen",
        ["tenant_id", "bewerbung_id", "erfolgt_am"],
        schema="domain_hr",
    )


def downgrade() -> None:
    verbindung = op.get_bind()
    # Das Verzeichnis ist der Nachweis nach Art. 7 Abs. 1 DSGVO. Wer es verliert,
    # kann nicht mehr belegen, dass die Aufbewahrung erlaubt war.
    anzahl = verbindung.execute(
        sa.text("SELECT COUNT(*) FROM domain_hr.bewerbung_einwilligungen")
    ).scalar()
    if anzahl:
        raise RuntimeError(
            f"domain_hr.bewerbung_einwilligungen fuehrt {anzahl} Vorgaenge. Sie sind "
            "der Nachweis der Einwilligung nach Art. 7 Abs. 1 DSGVO und werden nicht "
            "per Downgrade geloescht."
        )
    op.drop_index(
        "ix_beweinw_bewerbung", table_name="bewerbung_einwilligungen", schema="domain_hr"
    )
    op.drop_table("bewerbung_einwilligungen", schema="domain_hr")
