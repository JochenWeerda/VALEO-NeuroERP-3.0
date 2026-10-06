"""Vier Tabellen fuer drei Wege, die bisher nur quittiert haben.

`POST /schaeden/meldungen` antwortete `201` mit einer Meldungsnummer und
`status: "gemeldet"` — und schrieb **nichts**. `GET /schaeden/meldungen` lieferte
eine erfundene Hagelschadenmeldung ueber 12.500 EUR. `POST
/etiketten/druckauftrag` antwortete mit einer Auftragsnummer und `status:
"erstellt"`, ohne etwas zu speichern oder zu drucken. Drucker und
Versicherungsvertraege standen als Literale im Code.

Das ist nicht derselbe Fehler wie eine fehlende Tabelle: Dort antwortet der Weg
503 und jemand merkt es. Hier bekommt ein Haus eine Meldungsnummer in die Hand
und meldet deshalb nicht noch einmal — waehrend die Frist nach § 30 Abs. 1 VVG
laeuft.

Drei Entscheidungen stecken im Schema:

**Die Meldefrist steht am Vertrag.** `meldefrist_tage` an der Versicherung; die
Frist am einzelnen Schaden wird daraus **abgeleitet**. Eine Frist im Code gilt
fuer alle Policen gleich, und das ist sie nicht.

**`GEMELDET` braucht einen Zeitpunkt.** Ein Status "gemeldet" ohne Wann ist kein
Nachweis.

**Ein Druckauftrag hat einen Uebermittlungsstand.** Solange kein Spooler
angebunden ist, endet er bei `ANGELEGT` — die Tabelle laesst `GEDRUCKT` ohne
Zeitpunkt nicht zu.

Revision ID: quittung_ohne_vorgang_20261006
Revises: personal_organisation_zeitkonto_20261006
Create Date: 2026-10-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "quittung_ohne_vorgang_20261006"
down_revision = "personal_organisation_zeitkonto_20261006"
branch_labels = None
depends_on = None

#: Versicherungsarten, wie sie der Weg kennt.
VERSICHERUNGSARTEN = ("hagel", "haftpflicht", "feuer", "kasko", "inhalt", "transport", "sonstige")

#: Zustaende einer Schadenmeldung. `ENTWURF` ist der Eingangszustand: Das System
#: kann nicht behaupten, der Versicherer sei unterrichtet.
SCHADENSTAENDE = ("ENTWURF", "GEMELDET", "IN_BEARBEITUNG", "REGULIERT", "ABGELEHNT")

#: Zustaende eines Druckauftrags.
DRUCKSTAENDE = ("ANGELEGT", "UEBERMITTELT", "GEDRUCKT", "FEHLER", "ABGEBROCHEN")

#: Druckerzustaende.
DRUCKERSTAENDE = ("online", "offline", "fehler", "wartung")


def _liste(werte: tuple[str, ...]) -> str:
    return ", ".join(f"'{wert}'" for wert in werte)


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_erp")

    # ── Versicherungsvertraege ──────────────────────────────────────────────
    op.create_table(
        "versicherungen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("bezeichnung", sa.String(160), nullable=False),
        sa.Column("vertragsnummer", sa.String(80), nullable=False),
        sa.Column("typ", sa.String(30), nullable=False),
        sa.Column("versicherer", sa.String(200), nullable=False),
        sa.Column("gueltig_von", sa.Date(), nullable=True),
        sa.Column("gueltig_bis", sa.Date(), nullable=True),
        # Die Frist, innerhalb der ein Schaden anzuzeigen ist. Steht am Vertrag,
        # weil sie je Police verschieden ist (§ 30 Abs. 1 VVG verlangt
        # "unverzueglich"; Policen nennen regelmaessig konkrete Tage).
        sa.Column("meldefrist_tage", sa.Integer(), nullable=True),
        sa.Column("ansprechpartner", sa.String(160), nullable=True),
        sa.Column("kontakt", sa.String(200), nullable=True),
        sa.Column("aktiv", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.CheckConstraint(f"typ IN ({_liste(VERSICHERUNGSARTEN)})", name="ck_versicherung_typ"),
        sa.CheckConstraint(
            "meldefrist_tage IS NULL OR meldefrist_tage > 0", name="ck_versicherung_frist_positiv"
        ),
        sa.CheckConstraint(
            "gueltig_bis IS NULL OR gueltig_von IS NULL OR gueltig_bis >= gueltig_von",
            name="ck_versicherung_laufzeit",
        ),
        schema="domain_erp",
    )
    op.create_index(
        "ux_versicherung_vertragsnummer",
        "versicherungen",
        ["tenant_id", "vertragsnummer"],
        unique=True,
        schema="domain_erp",
    )

    # ── Schadenmeldungen ────────────────────────────────────────────────────
    op.create_table(
        "schaden_meldungen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("meldungsnummer", sa.String(40), nullable=False),
        sa.Column("art", sa.String(30), nullable=False),
        sa.Column("schadendatum", sa.Date(), nullable=False),
        sa.Column("ort", sa.String(160), nullable=True),
        sa.Column("beschreibung", sa.Text(), nullable=False),
        sa.Column("schadenhoehe", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("versicherung_id", sa.String(36), nullable=True),
        sa.Column("zeuge", sa.String(200), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="ENTWURF"),
        # Wann und durch wen der Versicherer unterrichtet wurde. Das System
        # uebermittelt nicht selbst; es haelt fest, dass es geschehen ist.
        sa.Column("gemeldet_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("gemeldet_durch", sa.String(120), nullable=True),
        sa.Column("meldeweg", sa.String(40), nullable=True),
        sa.Column("regulierungsbetrag", sa.Numeric(14, 2), nullable=True),
        sa.Column("abgelehnt_grund", sa.Text(), nullable=True),
        sa.Column("erfasst_durch", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["versicherung_id"], ["domain_erp.versicherungen.id"],
            name="fk_schaden_versicherung", ondelete="RESTRICT",
        ),
        sa.CheckConstraint(f"status IN ({_liste(SCHADENSTAENDE)})", name="ck_schaden_status"),
        sa.CheckConstraint("schadenhoehe >= 0", name="ck_schaden_hoehe_nicht_negativ"),
        sa.CheckConstraint("LENGTH(TRIM(beschreibung)) > 0", name="ck_schaden_beschrieben"),
        # Ein Status "gemeldet" ohne Wann ist kein Nachweis. Umgekehrt gibt es
        # keinen Meldezeitpunkt an einem Entwurf.
        sa.CheckConstraint(
            "(status = 'ENTWURF') = (gemeldet_am IS NULL)", name="ck_schaden_meldung_datiert"
        ),
        # Eine Ablehnung ohne Grund laesst sich nicht pruefen.
        sa.CheckConstraint(
            "status <> 'ABGELEHNT' OR (abgelehnt_grund IS NOT NULL "
            "AND LENGTH(TRIM(abgelehnt_grund)) > 0)",
            name="ck_schaden_ablehnung_begruendet",
        ),
        # Eine Regulierung ohne Betrag ist keine.
        sa.CheckConstraint(
            "status <> 'REGULIERT' OR regulierungsbetrag IS NOT NULL",
            name="ck_schaden_regulierung_beziffert",
        ),
        schema="domain_erp",
    )
    op.create_index(
        "ux_schaden_meldungsnummer",
        "schaden_meldungen",
        ["tenant_id", "meldungsnummer"],
        unique=True,
        schema="domain_erp",
    )
    op.create_index(
        "ix_schaden_mandant_status",
        "schaden_meldungen",
        ["tenant_id", "status", "schadendatum"],
        schema="domain_erp",
    )

    # ── Drucker ─────────────────────────────────────────────────────────────
    op.create_table(
        "drucker",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("standort", sa.String(160), nullable=True),
        sa.Column("typ", sa.String(30), nullable=True),
        sa.Column("modell", sa.String(80), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="offline"),
        sa.Column("ip", sa.String(60), nullable=True),
        sa.Column("aktiv", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.CheckConstraint(f"status IN ({_liste(DRUCKERSTAENDE)})", name="ck_drucker_status"),
        sa.CheckConstraint("LENGTH(TRIM(name)) > 0", name="ck_drucker_benannt"),
        schema="domain_erp",
    )
    op.create_index(
        "ux_drucker_name", "drucker", ["tenant_id", "name"], unique=True, schema="domain_erp"
    )

    # ── Druckauftraege ──────────────────────────────────────────────────────
    op.create_table(
        "druckauftraege",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("auftrags_nr", sa.String(40), nullable=False),
        sa.Column("chargen_id", sa.String(36), nullable=False),
        sa.Column("artikel", sa.String(200), nullable=True),
        sa.Column("menge", sa.Numeric(14, 3), nullable=True),
        sa.Column("lieferant", sa.String(200), nullable=True),
        sa.Column("eingang", sa.Date(), nullable=True),
        sa.Column("anzahl_etiketten", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("drucker_id", sa.String(36), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ANGELEGT"),
        # Wann der Auftrag tatsaechlich an einen Spooler gegangen und wann
        # gedruckt wurde. Solange nichts angebunden ist, bleiben beide leer — und
        # die Pruefbedingung laesst `GEDRUCKT` dann nicht zu.
        sa.Column("uebermittelt_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("gedruckt_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fehler", sa.Text(), nullable=True),
        sa.Column("erfasst_durch", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["drucker_id"], ["domain_erp.drucker.id"],
            name="fk_druckauftrag_drucker", ondelete="RESTRICT",
        ),
        sa.CheckConstraint(f"status IN ({_liste(DRUCKSTAENDE)})", name="ck_druckauftrag_status"),
        sa.CheckConstraint("anzahl_etiketten > 0", name="ck_druckauftrag_anzahl_positiv"),
        sa.CheckConstraint(
            "status <> 'UEBERMITTELT' OR uebermittelt_am IS NOT NULL",
            name="ck_druckauftrag_uebermittlung_datiert",
        ),
        sa.CheckConstraint(
            "status <> 'GEDRUCKT' OR gedruckt_am IS NOT NULL",
            name="ck_druckauftrag_druck_datiert",
        ),
        sa.CheckConstraint(
            "status <> 'FEHLER' OR (fehler IS NOT NULL AND LENGTH(TRIM(fehler)) > 0)",
            name="ck_druckauftrag_fehler_begruendet",
        ),
        schema="domain_erp",
    )
    op.create_index(
        "ux_druckauftrag_nr",
        "druckauftraege",
        ["tenant_id", "auftrags_nr"],
        unique=True,
        schema="domain_erp",
    )

    # ── Erinnerung zur Gelangensbestaetigung ────────────────────────────────
    # `erinnerung_gesendet: true` war eine Behauptung: "Stub: In production this
    # would send email/fax". Der Nachweis, dass jemand erinnern **wollte**, ist
    # etwas wert; die Behauptung, es sei versendet, ist es nicht.
    verbindung = op.get_bind()
    for spalte, typ in (
        ("erinnerung_angefordert_am", "TIMESTAMPTZ"),
        ("erinnerung_versuche", "INTEGER NOT NULL DEFAULT 0"),
        ("erinnerung_angefordert_durch", "VARCHAR(120)"),
    ):
        verbindung.execute(
            sa.text(
                "ALTER TABLE domain_compliance.gelangensbestaetigung "  # nosec B608  # reviewed-safe: Namen sind Code-Literale
                f"ADD COLUMN IF NOT EXISTS {spalte} {typ}"
            )
        )


def downgrade() -> None:
    verbindung = op.get_bind()
    for tabelle, was in (
        ("druckauftraege", "Druckauftraege"),
        ("drucker", "Drucker"),
        ("schaden_meldungen", "Schadenmeldungen"),
        ("versicherungen", "Versicherungsvertraege"),
    ):
        anzahl = verbindung.execute(
            sa.text(f"SELECT COUNT(*) FROM domain_erp.{tabelle}")  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        ).scalar()
        if anzahl:
            raise RuntimeError(
                f"domain_erp.{tabelle} fuehrt {anzahl} {was}. Eine Schadenmeldung ist "
                "fristgebunden und ein Etikett ein Rueckverfolgbarkeitsbeleg — beides "
                "wird nicht per Downgrade geloescht."
            )
    for spalte in (
        "erinnerung_angefordert_am",
        "erinnerung_versuche",
        "erinnerung_angefordert_durch",
    ):
        verbindung.execute(
            sa.text(
                "ALTER TABLE domain_compliance.gelangensbestaetigung "  # nosec B608  # reviewed-safe: Name ist ein Code-Literal
                f"DROP COLUMN IF EXISTS {spalte}"
            )
        )
    op.drop_index("ux_druckauftrag_nr", table_name="druckauftraege", schema="domain_erp")
    op.drop_table("druckauftraege", schema="domain_erp")
    op.drop_index("ux_drucker_name", table_name="drucker", schema="domain_erp")
    op.drop_table("drucker", schema="domain_erp")
    op.drop_index("ix_schaden_mandant_status", table_name="schaden_meldungen", schema="domain_erp")
    op.drop_index("ux_schaden_meldungsnummer", table_name="schaden_meldungen", schema="domain_erp")
    op.drop_table("schaden_meldungen", schema="domain_erp")
    op.drop_index("ux_versicherung_vertragsnummer", table_name="versicherungen", schema="domain_erp")
    op.drop_table("versicherungen", schema="domain_erp")
