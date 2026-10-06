"""Der Loeschlauf fuer Bewerberdaten — Frist, Einwilligung und Nachweis.

Art. 5 Abs. 1 lit. e DSGVO: personenbezogene Daten nicht laenger halten als fuer
den Zweck noetig. Fuer Bewerberdaten ist der Zweck mit dem Verfahren erledigt; die
ueblichen sechs Monate nach der Ablehnung leiten sich aus § 15 Abs. 4 AGG ab (zwei
Monate Geltendmachung) plus Zustellung und Klagefrist-Puffer.

Es gab einen Loeschweg je Bewerbung, aber keine Frist und keinen Lauf, der ihn
anstoesst. Was hier entsteht:

**Eine eigene Aufbewahrungsregel, nicht `gobd_aufbewahrungsrichtlinien`.** Die
GoBD-Richtlinie rechnet in **Jahren** und sagt "mindestens so lange"; hier gilt das
**Gegenteil** — "hoechstens so lange" — und die Einheit ist der Tag. Zwei
entgegengesetzte Pflichten gehoeren nicht in eine Tabelle: Wer sie zusammenlegt,
kann spaeter nicht mehr sagen, ob eine Zahl eine Untergrenze oder eine Obergrenze
ist.

**Ein Protokoll ohne Personenbezug.** Man muss beweisen koennen, **dass** geloescht
wurde, ohne zu behalten, **was** geloescht wurde. Deshalb traegt der Lauf nur
Zahlen: geprueft, geloescht, uebersprungen je Grund.

**Keine Vorbefuellung.** Ohne Regel loescht der Lauf nichts. Eine Frist, die
niemand beschlossen hat, ist keine Grundlage, um Daten zu vernichten.

Die **Loeschsperre** wird nicht neu erfunden: `public.gobd_loeschsperren` ist trotz
ihres Namens der allgemeine Begriff. Laeuft eine AGG-Klage, sind die Bewerberdaten
Beweismittel und duerfen nicht weg.

Revision ID: bewerbung_loeschlauf_20261006
Revises: bewerbung_statuswoerterbuch_20261006
Create Date: 2026-10-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "bewerbung_loeschlauf_20261006"
down_revision = "bewerbung_statuswoerterbuch_20261006"
branch_labels = None
depends_on = None

BEWERBUNGEN = "domain_hr.applications"


def upgrade() -> None:
    verbindung = op.get_bind()

    # ── Die Aufbewahrungsregel je Mandant ───────────────────────────────────
    op.create_table(
        "bewerbung_aufbewahrung",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        # In **Tagen**, nicht Jahren: Sechs Monate sind kein Jahr, und eine Frist,
        # die man aufrunden muss, haelt Daten laenger als noetig.
        sa.Column("aufbewahrung_tage", sa.Integer(), nullable=False),
        sa.Column("gesetzliche_grundlage", sa.String(200), nullable=False),
        sa.Column("beschluss_am", sa.Date(), nullable=True),
        sa.Column("beschluss_durch", sa.String(120), nullable=True),
        sa.Column("aktiv", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.CheckConstraint("aufbewahrung_tage > 0", name="ck_bewaufb_tage_positiv"),
        # Eine Frist von zehn Jahren fuer Bewerberdaten waere keine Aufbewahrung,
        # sondern ein Vorrat. Die Grenze ist weit gefasst und faengt nur den
        # Tippfehler — die fachliche Angemessenheit entscheidet das Haus.
        sa.CheckConstraint("aufbewahrung_tage <= 1095", name="ck_bewaufb_tage_obergrenze"),
        sa.CheckConstraint(
            "LENGTH(TRIM(gesetzliche_grundlage)) > 0", name="ck_bewaufb_grundlage_benannt"
        ),
        schema="domain_hr",
    )
    # Je Mandant gilt **eine** aktive Regel: Zwei waeren zwei Obergrenzen, und der
    # Lauf muesste raten, welche gilt.
    op.create_index(
        "ux_bewaufb_mandant",
        "bewerbung_aufbewahrung",
        ["tenant_id"],
        unique=True,
        postgresql_where=sa.text("aktiv"),
        schema="domain_hr",
    )

    # ── Die Einwilligung zur laengeren Aufbewahrung ──────────────────────────
    # Talentpool, Art. 6 Abs. 1 lit. a DSGVO. Wer eingewilligt hat, wird nicht
    # mitgeloescht — und die Einwilligung hat selbst ein Ende.
    verbindung.execute(
        sa.text(
            f"ALTER TABLE {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: Namen sind Code-Literale
            "ADD COLUMN IF NOT EXISTS aufbewahrung_einwilligung_bis DATE"
        )
    )
    verbindung.execute(
        sa.text(
            f"ALTER TABLE {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: Namen sind Code-Literale
            "ADD COLUMN IF NOT EXISTS aufbewahrung_einwilligung_am TIMESTAMPTZ"
        )
    )
    vorhanden = verbindung.execute(
        sa.text("SELECT 1 FROM pg_constraint WHERE conname = 'ck_bewerbung_einwilligung_datiert'")
    ).scalar()
    if not vorhanden:
        verbindung.execute(
            sa.text(
                f"ALTER TABLE {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: Namen sind Code-Literale
                "ADD CONSTRAINT ck_bewerbung_einwilligung_datiert CHECK ("
                "  (aufbewahrung_einwilligung_bis IS NULL) "
                "  = (aufbewahrung_einwilligung_am IS NULL))"
            )
        )

    # ── Der Nachweis: Zahlen, keine Namen ───────────────────────────────────
    op.create_table(
        "bewerbung_loeschlaeufe",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("gestartet_am", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("aufbewahrung_tage", sa.Integer(), nullable=False),
        # Der Stichtag, bis zu dem entschiedene Bewerbungen faellig waren.
        sa.Column("stichtag", sa.Date(), nullable=False),
        sa.Column("geprueft", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("geloescht", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("uebersprungen_sperre", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("uebersprungen_einwilligung", sa.Integer(), nullable=False,
                  server_default="0"),
        sa.Column("durchgefuehrt_durch", sa.String(120), nullable=True),
        sa.Column("hinweis", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "geprueft >= 0 AND geloescht >= 0 AND uebersprungen_sperre >= 0 "
            "AND uebersprungen_einwilligung >= 0",
            name="ck_bewloesch_zahlen_nicht_negativ",
        ),
        # Geloescht und uebersprungen koennen zusammen nicht mehr sein als geprueft.
        sa.CheckConstraint(
            "geloescht + uebersprungen_sperre + uebersprungen_einwilligung <= geprueft",
            name="ck_bewloesch_summe_stimmt",
        ),
        schema="domain_hr",
    )
    op.create_index(
        "ix_bewloesch_mandant",
        "bewerbung_loeschlaeufe",
        ["tenant_id", "gestartet_am"],
        schema="domain_hr",
    )


def downgrade() -> None:
    verbindung = op.get_bind()
    # Das Protokoll der Loeschlaeufe ist der Nachweis, dass geloescht wurde. Es
    # enthaelt keinen Personenbezug und steht einem Rueckbau nicht im Weg — aber
    # ein Haus, das es verliert, kann die Erfuellung nicht mehr belegen.
    anzahl = verbindung.execute(
        sa.text("SELECT COUNT(*) FROM domain_hr.bewerbung_loeschlaeufe")
    ).scalar()
    if anzahl:
        raise RuntimeError(
            f"domain_hr.bewerbung_loeschlaeufe fuehrt {anzahl} Laeufe. Sie sind der "
            "Nachweis der Loeschung nach Art. 5 Abs. 1 lit. e DSGVO und werden "
            "nicht per Downgrade geloescht."
        )
    op.drop_index("ix_bewloesch_mandant", table_name="bewerbung_loeschlaeufe", schema="domain_hr")
    op.drop_table("bewerbung_loeschlaeufe", schema="domain_hr")

    verbindung.execute(
        sa.text(
            f"ALTER TABLE {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: Namen sind Code-Literale
            "DROP CONSTRAINT IF EXISTS ck_bewerbung_einwilligung_datiert"
        )
    )
    einwilligungen = verbindung.execute(
        sa.text(
            f"SELECT COUNT(*) FROM {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE aufbewahrung_einwilligung_bis IS NOT NULL"
        )
    ).scalar()
    if einwilligungen:
        raise RuntimeError(
            f"{einwilligungen} Bewerbungen fuehren eine Einwilligung zur laengeren "
            "Aufbewahrung. Sie ist die Rechtsgrundlage dafuer, dass diese Daten "
            "noch da sind, und wird nicht per Downgrade geloescht."
        )
    for spalte in ("aufbewahrung_einwilligung_bis", "aufbewahrung_einwilligung_am"):
        verbindung.execute(
            sa.text(
                f"ALTER TABLE {BEWERBUNGEN} DROP COLUMN IF EXISTS {spalte}"  # nosec B608  # reviewed-safe: Namen sind Code-Literale
            )
        )

    op.drop_index("ux_bewaufb_mandant", table_name="bewerbung_aufbewahrung", schema="domain_hr")
    op.drop_table("bewerbung_aufbewahrung", schema="domain_hr")
