"""Fachliche Vertiefung Wave 5: Vermehrungsvertrag, Vertreterstamm, Geschäftsjahre, Periodische Buchungen

Revision ID: fachliche_vertiefung_wave5_20260521
Revises: fachliche_vertiefung_wave4_20260521
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave5_20260521"
down_revision = "fachliche_vertiefung_wave4_20260521"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Vertreterstamm: Außendienstmitarbeiter/Provisionsvertreter ---
    op.create_table(
        "crm_vertreter",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("vertreter_nr", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("vorname", sa.String(100), nullable=True),
        sa.Column("kuerzel", sa.String(10), nullable=True),
        sa.Column("telefon", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("vertretergruppe_nr", sa.String(20), nullable=True,
                  comment="Zuordnung zu Vertretergruppe"),
        sa.Column("provisionsgruppe_nr", sa.String(20), nullable=True,
                  comment="Standard-Provisionsgruppe"),
        sa.Column("gebiet", sa.String(100), nullable=True),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_vertreter_tenant_nr", "crm_vertreter",
                    ["tenant_id", "vertreter_nr"], unique=True, schema="domain_shared")

    op.create_table(
        "crm_vertretergruppen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("gruppe_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_vertretergruppe_tenant_nr", "crm_vertretergruppen",
                    ["tenant_id", "gruppe_nr"], unique=True, schema="domain_shared")

    # --- Vermehrungsvertrag [SAATV]: Saatgut-Anbauverträge ---
    op.create_table(
        "saatzucht_vermehrungsvertraege",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("vertrag_nr", sa.String(30), nullable=False),
        sa.Column("erntejahr", sa.Integer, nullable=False),
        sa.Column("vermehrer_kunden_nr", sa.String(50), nullable=False,
                  comment="Kundennummer aus Kundenstamm"),
        sa.Column("sorte_nr", sa.String(50), nullable=True,
                  comment="Sortennummer aus Saatgutstamm"),
        sa.Column("sorte_bezeichnung", sa.String(255), nullable=True),
        sa.Column("kategorie", sa.String(50), nullable=True,
                  comment="Saatkategorie z.B. Z1, Z2, SE"),
        sa.Column("vertragsart", sa.String(30), nullable=True),
        sa.Column("vertrags_menge_t", sa.Numeric(12, 3), nullable=True,
                  comment="Vertragliche Anbaumenge in Tonnen"),
        sa.Column("anbauflaeche_ha", sa.Numeric(10, 4), nullable=True),
        sa.Column("lwk_anerkennungsstelle", sa.String(100), nullable=True),
        sa.Column("vmkz", sa.String(50), nullable=True,
                  comment="Vermehrerkennziffer"),
        sa.Column("registriernummer", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), default="angelegt",
                  comment="angelegt, aktiv, beendet, storniert"),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_vermehrungsvertrag_tenant_nr", "saatzucht_vermehrungsvertraege",
                    ["tenant_id", "vertrag_nr"], unique=True, schema="domain_shared")
    op.create_index("ix_vermehrungsvertrag_erntejahr", "saatzucht_vermehrungsvertraege",
                    ["tenant_id", "erntejahr"], schema="domain_shared")

    # --- Geschäftsjahre / FiBu-Perioden [JAHR] ---
    op.create_table(
        "fibu_geschaeftsjahre",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("jahr_nr", sa.Integer, nullable=False,
                  comment="Geschäftsjahr z.B. 2024"),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("datum_beginn", sa.Date, nullable=False),
        sa.Column("datum_ende", sa.Date, nullable=False),
        sa.Column("kleinstes_datum", sa.Date, nullable=True,
                  comment="Untergrenze für Datumseingaben"),
        sa.Column("groesstes_datum", sa.Date, nullable=True,
                  comment="Obergrenze für Datumseingaben"),
        sa.Column("warndatum_von", sa.Date, nullable=True),
        sa.Column("warndatum_bis", sa.Date, nullable=True),
        sa.Column("anzahl_perioden_ware", sa.Integer, default=12),
        sa.Column("anzahl_perioden_fibu", sa.Integer, default=12),
        sa.Column("journal_nummernkreis", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), default="offen",
                  comment="offen, aktiv, abgeschlossen"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_fibu_gj_tenant_jahr", "fibu_geschaeftsjahre",
                    ["tenant_id", "jahr_nr"], unique=True, schema="domain_shared")

    op.create_table(
        "fibu_perioden",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("jahr_nr", sa.Integer, nullable=False),
        sa.Column("periode_nr", sa.Integer, nullable=False,
                  comment="1–12 = Normalperioden; 0=Eröffnung; 13=Abschluss"),
        sa.Column("bezeichnung", sa.String(100), nullable=True),
        sa.Column("datum_von", sa.Date, nullable=False),
        sa.Column("datum_bis", sa.Date, nullable=False),
        sa.Column("typ", sa.String(20), default="normal",
                  comment="normal, eroeffnung, abschluss"),
        sa.Column("gesperrt", sa.Boolean, default=False,
                  comment="Gebuchte Periode — keine weiteren Buchungen"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_fibu_periode_tenant_jahr_nr", "fibu_perioden",
                    ["tenant_id", "jahr_nr", "periode_nr"], unique=True, schema="domain_shared")

    # --- Periodische Buchungen [FIWIEBU]: Wiederkehrende FIBU-Buchungen ---
    op.create_table(
        "fibu_periodische_buchungen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("soll_konto", sa.String(20), nullable=False),
        sa.Column("haben_konto", sa.String(20), nullable=False),
        sa.Column("betrag_eur", sa.Numeric(18, 2), nullable=False),
        sa.Column("buchungstext", sa.String(255), nullable=True),
        sa.Column("intervall", sa.String(20), nullable=False,
                  comment="monatlich, quartalsweise, halbjaehrlich, jaehrlich"),
        sa.Column("naechste_buchung", sa.Date, nullable=True),
        sa.Column("buchung_bis", sa.Date, nullable=True,
                  comment="Abgrenzungsdatum — kein Beleg danach"),
        sa.Column("alle_belege_erzeugen", sa.Boolean, default=False,
                  comment="Alle ausstehenden Belege in einem Lauf erstellen (EPA FIWIEBU)"),
        sa.Column("anzahl_erzeugte_belege", sa.Integer, default=0),
        sa.Column("letzter_beleg_datum", sa.Date, nullable=True),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_fibu_periodb_tenant", "fibu_periodische_buchungen",
                    ["tenant_id"], schema="domain_shared")


def downgrade() -> None:
    op.drop_index("ix_fibu_periodb_tenant", "fibu_periodische_buchungen", schema="domain_shared")
    op.drop_table("fibu_periodische_buchungen", schema="domain_shared")
    op.drop_index("ix_fibu_periode_tenant_jahr_nr", "fibu_perioden", schema="domain_shared")
    op.drop_table("fibu_perioden", schema="domain_shared")
    op.drop_index("ix_fibu_gj_tenant_jahr", "fibu_geschaeftsjahre", schema="domain_shared")
    op.drop_table("fibu_geschaeftsjahre", schema="domain_shared")
    op.drop_index("ix_vermehrungsvertrag_erntejahr", "saatzucht_vermehrungsvertraege", schema="domain_shared")
    op.drop_index("ix_vermehrungsvertrag_tenant_nr", "saatzucht_vermehrungsvertraege", schema="domain_shared")
    op.drop_table("saatzucht_vermehrungsvertraege", schema="domain_shared")
    op.drop_index("ix_vertretergruppe_tenant_nr", "crm_vertretergruppen", schema="domain_shared")
    op.drop_table("crm_vertretergruppen", schema="domain_shared")
    op.drop_index("ix_vertreter_tenant_nr", "crm_vertreter", schema="domain_shared")
    op.drop_table("crm_vertreter", schema="domain_shared")
