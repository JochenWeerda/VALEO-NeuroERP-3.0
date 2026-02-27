"""einkauf domain tables — Lieferanten, Kontrakte, Bestellungen, Bestellvorschlaege, ArtikelLagerParameter, LagerKonten, PalettenKonto, PfandKonto, FremdwarenEinlagerung

Revision ID: einkauf_domain_tables_20260227
Revises: feldbuch_schlag_massnahme_20260226
Create Date: 2026-02-27

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

revision = "einkauf_domain_tables_20260227"
down_revision = "feldbuch_schlag_massnahme_20260226"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Schema anlegen ──────────────────────────────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_einkauf")

    # ── Lieferanten ─────────────────────────────────────────────────────────
    op.create_table(
        "lieferanten",
        sa.Column("id",                  PGUUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id",           sa.String,   nullable=False),
        sa.Column("lieferantennummer",   sa.String(50), nullable=False),
        sa.Column("partner_id",          sa.String),
        sa.Column("firmenname",          sa.String(255), nullable=False),
        sa.Column("ansprechpartner",     sa.String(255)),
        sa.Column("email",               sa.String(255)),
        sa.Column("telefon",             sa.String(50)),
        sa.Column("fax",                 sa.String(50)),
        sa.Column("strasse",             sa.String(255)),
        sa.Column("plz",                 sa.String(20)),
        sa.Column("ort",                 sa.String(100)),
        sa.Column("land",                sa.String(100), server_default="Deutschland"),
        sa.Column("steuernummer",        sa.String(50)),
        sa.Column("ust_id",              sa.String(30)),
        sa.Column("zahlungsbedingungen", sa.String(50)),
        sa.Column("zahlungsziel_tage",   sa.Integer),
        sa.Column("skonto_prozent",      sa.Numeric(5, 2)),
        sa.Column("lieferzeit_tage",     sa.Integer),
        sa.Column("mindestbestellwert",  sa.Numeric(12, 2)),
        sa.Column("bewertung",           sa.Integer),
        sa.Column("aktiv",               sa.Boolean, server_default=sa.true()),
        sa.Column("notiz",               sa.Text),
        sa.Column("edi_kennung",         sa.String(50)),
        sa.Column("edi_format",          sa.String(20)),
        sa.Column("email_bestellung",    sa.String(255)),
        sa.Column("fax_bestellung",      sa.String(50)),
        sa.Column("created_at",          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",          sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("created_by",          sa.String(200)),
        schema="domain_einkauf",
    )
    op.create_index("ix_ek_lieferant_tenant_nr", "lieferanten",
                    ["tenant_id", "lieferantennummer"], schema="domain_einkauf")
    op.create_index("ix_ek_lieferant_firmenname", "lieferanten",
                    ["firmenname"], schema="domain_einkauf")

    # ── Kontrakte ────────────────────────────────────────────────────────────
    op.create_table(
        "kontrakte",
        sa.Column("id",              PGUUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id",       sa.String,   nullable=False),
        sa.Column("kontraktnummer",  sa.String(50), nullable=False),
        sa.Column("lieferant_id",    PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.lieferanten.id"), nullable=False),
        sa.Column("bezeichnung",     sa.String(300)),
        sa.Column("gueltig_von",     sa.Date),
        sa.Column("gueltig_bis",     sa.Date),
        sa.Column("status",          sa.String(20), server_default="aktiv"),
        sa.Column("kontrakt_typ",    sa.String(30), server_default="rahmen"),
        sa.Column("waehrung",        sa.String(3),  server_default="EUR"),
        sa.Column("gesamtwert",      sa.Numeric(14, 2)),
        sa.Column("gesamtmenge",     sa.Numeric(14, 3)),
        sa.Column("offene_menge",    sa.Numeric(14, 3)),
        sa.Column("niederlassung_id", sa.String),
        sa.Column("notiz",           sa.Text),
        sa.Column("anhang_ids",      JSONB),
        sa.Column("created_at",      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",      sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("created_by",      sa.String(200)),
        schema="domain_einkauf",
    )
    op.create_index("ix_ek_kontrakt_tenant_nr", "kontrakte",
                    ["tenant_id", "kontraktnummer"], schema="domain_einkauf")
    op.create_index("ix_ek_kontrakt_lieferant", "kontrakte",
                    ["lieferant_id"], schema="domain_einkauf")
    op.create_index("ix_ek_kontrakt_status", "kontrakte",
                    ["tenant_id", "status"], schema="domain_einkauf")

    # ── Kontrakt-Positionen ─────────────────────────────────────────────────
    op.create_table(
        "kontrakt_positionen",
        sa.Column("id",                  PGUUID(as_uuid=False), primary_key=True),
        sa.Column("kontrakt_id",         PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.kontrakte.id"), nullable=False),
        sa.Column("pos_nr",              sa.Integer, nullable=False),
        sa.Column("article_id",          sa.String),
        sa.Column("artikel_bezeichnung", sa.String(300)),
        sa.Column("menge",               sa.Numeric(14, 3), nullable=False),
        sa.Column("offene_menge",        sa.Numeric(14, 3)),
        sa.Column("einheit",             sa.String(20)),
        sa.Column("preis",               sa.Numeric(14, 4)),
        sa.Column("preis_einheit",       sa.String(20), server_default="100kg"),
        sa.Column("preisbindung",        sa.String(20), server_default="fix"),
        sa.Column("gueltig_von",         sa.Date),
        sa.Column("gueltig_bis",         sa.Date),
        sa.Column("notiz",               sa.Text),
        schema="domain_einkauf",
    )
    op.create_index("ix_ek_kontrakt_pos_kontrakt", "kontrakt_positionen",
                    ["kontrakt_id"], schema="domain_einkauf")

    # ── ArtikelLagerParameter ───────────────────────────────────────────────
    op.create_table(
        "artikel_lager_parameter",
        sa.Column("id",               PGUUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id",        sa.String, nullable=False),
        sa.Column("article_id",       sa.String, nullable=False),
        sa.Column("warehouse_id",     sa.String),
        sa.Column("niederlassung_id", sa.String),
        sa.Column("mindestbestand",   sa.Numeric(14, 3), server_default="0"),
        sa.Column("maximalbestand",   sa.Numeric(14, 3)),
        sa.Column("meldebestand",     sa.Numeric(14, 3), server_default="0"),
        sa.Column("soll_bestand",     sa.Numeric(14, 3)),
        sa.Column("std_lieferant_id", PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.lieferanten.id")),
        sa.Column("std_bestellmenge", sa.Numeric(14, 3)),
        sa.Column("std_einheit",      sa.String(20)),
        sa.Column("wiederbeschaffungs_tage", sa.Integer, server_default="3"),
        sa.Column("durchschnitt_verbrauch_tag", sa.Numeric(14, 4)),
        sa.Column("reichweite_tage",  sa.Numeric(10, 1)),
        sa.Column("aktiv",            sa.Boolean, server_default=sa.true()),
        sa.Column("notiz",            sa.Text),
        sa.Column("created_at",       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",       sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("updated_by",       sa.String(200)),
        sa.UniqueConstraint("tenant_id", "article_id", "warehouse_id",
                            name="uq_alp_tenant_article_warehouse"),
        schema="domain_einkauf",
    )
    op.create_index("ix_alp_tenant_article", "artikel_lager_parameter",
                    ["tenant_id", "article_id"], schema="domain_einkauf")

    # ── Bestellvorschläge ───────────────────────────────────────────────────
    op.create_table(
        "bestellvorschlaege",
        sa.Column("id",              PGUUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id",       sa.String, nullable=False),
        sa.Column("vorschlag_typ",   sa.String(20), nullable=False),
        sa.Column("bezeichnung",     sa.String(300)),
        sa.Column("datum",           sa.Date, nullable=False),
        sa.Column("niederlassung_id", sa.String),
        sa.Column("parameter",       JSONB, server_default="{}"),
        sa.Column("status",          sa.String(20), server_default="entwurf"),
        sa.Column("erstellt_von",    sa.String(200)),
        sa.Column("freigegeben_von", sa.String(200)),
        sa.Column("freigegeben_am",  sa.DateTime(timezone=True)),
        sa.Column("notiz",           sa.Text),
        sa.Column("created_at",      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",      sa.DateTime(timezone=True), onupdate=sa.func.now()),
        schema="domain_einkauf",
    )
    op.create_index("ix_ek_bv_tenant_typ", "bestellvorschlaege",
                    ["tenant_id", "vorschlag_typ"], schema="domain_einkauf")
    op.create_index("ix_ek_bv_tenant_status", "bestellvorschlaege",
                    ["tenant_id", "status"], schema="domain_einkauf")

    # ── Bestellvorschlag-Positionen ─────────────────────────────────────────
    op.create_table(
        "bestellvorschlag_positionen",
        sa.Column("id",                  PGUUID(as_uuid=False), primary_key=True),
        sa.Column("vorschlag_id",        PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.bestellvorschlaege.id"), nullable=False),
        sa.Column("pos_nr",              sa.Integer, nullable=False),
        sa.Column("article_id",          sa.String, nullable=False),
        sa.Column("artikel_nr",          sa.String(50)),
        sa.Column("artikel_bezeichnung", sa.String(300)),
        sa.Column("artikel_gruppe",      sa.String(80)),
        sa.Column("einheit",             sa.String(20)),
        sa.Column("ist_bestand",         sa.Numeric(14, 3), server_default="0"),
        sa.Column("offene_auftraege",    sa.Numeric(14, 3), server_default="0"),
        sa.Column("bedarf",              sa.Numeric(14, 3), server_default="0"),
        sa.Column("vorschlag_menge",     sa.Numeric(14, 3), nullable=False),
        sa.Column("bestell_menge",       sa.Numeric(14, 3)),
        sa.Column("lieferant_id",        PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.lieferanten.id")),
        sa.Column("lieferant_name",      sa.String(255)),
        sa.Column("kontrakt_id",         PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.kontrakte.id")),
        sa.Column("letzter_preis",       sa.Numeric(14, 4)),
        sa.Column("preis_einheit",       sa.String(20)),
        sa.Column("letzter_kauf_datum",  sa.Date),
        sa.Column("status",              sa.String(20), server_default="offen"),
        schema="domain_einkauf",
    )
    op.create_index("ix_ek_bvp_vorschlag", "bestellvorschlag_positionen",
                    ["vorschlag_id"], schema="domain_einkauf")

    # ── Bestellungen ────────────────────────────────────────────────────────
    op.create_table(
        "bestellungen",
        sa.Column("id",               PGUUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id",        sa.String, nullable=False),
        sa.Column("bestellnummer",    sa.String(50), nullable=False),
        sa.Column("lieferant_id",     PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.lieferanten.id"), nullable=False),
        sa.Column("vorschlag_id",     PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.bestellvorschlaege.id")),
        sa.Column("niederlassung_id", sa.String),
        sa.Column("bestelldatum",     sa.Date, nullable=False),
        sa.Column("lieferdatum_wunsch",    sa.Date),
        sa.Column("lieferdatum_zugesagt",  sa.Date),
        sa.Column("lieferdatum_ist",       sa.Date),
        sa.Column("status",           sa.String(30), server_default="entwurf"),
        sa.Column("versand_art",      sa.String(20), server_default="email"),
        sa.Column("versandt_am",      sa.DateTime(timezone=True)),
        sa.Column("versandt_von",     sa.String(200)),
        sa.Column("netto_summe",      sa.Numeric(14, 2)),
        sa.Column("mwst_betrag",      sa.Numeric(14, 2)),
        sa.Column("brutto_summe",     sa.Numeric(14, 2)),
        sa.Column("waehrung",         sa.String(3), server_default="EUR"),
        sa.Column("zahlungsziel_tage", sa.Integer),
        sa.Column("skonto_prozent",   sa.Numeric(5, 2)),
        sa.Column("skonto_frist_tage", sa.Integer),
        sa.Column("unsere_referenz",  sa.String(100)),
        sa.Column("ihre_referenz",    sa.String(100)),
        sa.Column("kontrakt_id",      PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.kontrakte.id")),
        sa.Column("freitext_kopf",    sa.Text),
        sa.Column("freitext_fuss",    sa.Text),
        sa.Column("notiz",            sa.Text),
        sa.Column("anhang_ids",       JSONB),
        sa.Column("erstellt_von",     sa.String(200)),
        sa.Column("created_at",       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",       sa.DateTime(timezone=True), onupdate=sa.func.now()),
        schema="domain_einkauf",
    )
    op.create_index("ix_ek_bestellung_tenant_nr", "bestellungen",
                    ["tenant_id", "bestellnummer"], schema="domain_einkauf")
    op.create_index("ix_ek_bestellung_tenant_status", "bestellungen",
                    ["tenant_id", "status"], schema="domain_einkauf")
    op.create_index("ix_ek_bestellung_lieferant", "bestellungen",
                    ["lieferant_id"], schema="domain_einkauf")

    # ── Bestell-Positionen ──────────────────────────────────────────────────
    op.create_table(
        "bestellung_positionen",
        sa.Column("id",                  PGUUID(as_uuid=False), primary_key=True),
        sa.Column("bestellung_id",       PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.bestellungen.id"), nullable=False),
        sa.Column("pos_nr",              sa.Integer, nullable=False),
        sa.Column("article_id",          sa.String),
        sa.Column("artikel_nr",          sa.String(50), nullable=False),
        sa.Column("artikel_bezeichnung", sa.String(300), nullable=False),
        sa.Column("lieferanten_artnr",   sa.String(50)),
        sa.Column("menge",               sa.Numeric(14, 3), nullable=False),
        sa.Column("menge_geliefert",     sa.Numeric(14, 3), server_default="0"),
        sa.Column("menge_offen",         sa.Numeric(14, 3)),
        sa.Column("einheit",             sa.String(20), nullable=False),
        sa.Column("einzelpreis",         sa.Numeric(14, 4)),
        sa.Column("preis_einheit",       sa.String(20), server_default="100kg"),
        sa.Column("rabatt_prozent",      sa.Numeric(5, 2), server_default="0"),
        sa.Column("netto_betrag",        sa.Numeric(14, 2)),
        sa.Column("mwst_satz",           sa.Numeric(5, 2)),
        sa.Column("mwst_betrag",         sa.Numeric(14, 2)),
        sa.Column("brutto_betrag",       sa.Numeric(14, 2)),
        sa.Column("kontrakt_pos_id",     PGUUID(as_uuid=False),
                  sa.ForeignKey("domain_einkauf.kontrakt_positionen.id")),
        sa.Column("lieferdatum",         sa.Date),
        sa.Column("lagerort",            sa.String(100)),
        sa.Column("notiz",               sa.Text),
        sa.Column("status",              sa.String(20), server_default="offen"),
        schema="domain_einkauf",
    )
    op.create_index("ix_ek_bp_bestellung", "bestellung_positionen",
                    ["bestellung_id"], schema="domain_einkauf")

    # ── Lager-Konten-Zuordnung ──────────────────────────────────────────────
    op.create_table(
        "lager_kontenzuordnung",
        sa.Column("id",                  PGUUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id",           sa.String, nullable=False),
        sa.Column("artikelgruppe",       sa.String(80), nullable=False),
        sa.Column("niederlassung_id",    sa.String),
        sa.Column("bestandskonto",       sa.String(20), nullable=False),
        sa.Column("gegenkonto_zugang",   sa.String(20)),
        sa.Column("gegenkonto_abgang",   sa.String(20)),
        sa.Column("paletten_konto",      sa.String(20)),
        sa.Column("pfand_konto",         sa.String(20)),
        sa.Column("fremdwaren_konto",    sa.String(20)),
        sa.Column("einlagerung_konto",   sa.String(20)),
        sa.Column("chargen_konto",       sa.String(20)),
        sa.Column("ust_schluessel",      sa.String(10)),
        sa.Column("aktiv",               sa.Boolean, server_default=sa.true()),
        sa.Column("notiz",               sa.Text),
        sa.Column("created_at",          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",          sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("updated_by",          sa.String(200)),
        sa.UniqueConstraint("tenant_id", "artikelgruppe", "niederlassung_id",
                            name="uq_lkz_tenant_gruppe_nl"),
        schema="domain_einkauf",
    )
    op.create_index("ix_lkz_tenant", "lager_kontenzuordnung",
                    ["tenant_id"], schema="domain_einkauf")

    # ── Paletten-Konto ──────────────────────────────────────────────────────
    op.create_table(
        "paletten_konto_buchungen",
        sa.Column("id",               PGUUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id",        sa.String, nullable=False),
        sa.Column("partner_id",       sa.String, nullable=False),
        sa.Column("partner_typ",      sa.String(10), nullable=False),
        sa.Column("niederlassung_id", sa.String),
        sa.Column("buchungsdatum",    sa.Date, nullable=False),
        sa.Column("buchungsart",      sa.String(20), nullable=False),
        sa.Column("paletten_typ",     sa.String(30), server_default="EUR-Palette"),
        sa.Column("menge",            sa.Integer, nullable=False),
        sa.Column("saldo_vorher",     sa.Integer),
        sa.Column("saldo_nachher",    sa.Integer),
        sa.Column("referenz_typ",     sa.String(30)),
        sa.Column("referenz_id",      sa.String),
        sa.Column("referenz_nr",      sa.String(100)),
        sa.Column("notiz",            sa.Text),
        sa.Column("created_at",       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by",       sa.String(200)),
        schema="domain_einkauf",
    )
    op.create_index("ix_pkl_tenant_partner", "paletten_konto_buchungen",
                    ["tenant_id", "partner_id"], schema="domain_einkauf")
    op.create_index("ix_pkl_tenant_datum", "paletten_konto_buchungen",
                    ["tenant_id", "buchungsdatum"], schema="domain_einkauf")

    # ── Pfand-Konto ─────────────────────────────────────────────────────────
    op.create_table(
        "pfand_konto_buchungen",
        sa.Column("id",                    PGUUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id",             sa.String, nullable=False),
        sa.Column("partner_id",            sa.String, nullable=False),
        sa.Column("partner_typ",           sa.String(10), nullable=False),
        sa.Column("niederlassung_id",      sa.String),
        sa.Column("buchungsdatum",         sa.Date, nullable=False),
        sa.Column("buchungsart",           sa.String(20), nullable=False),
        sa.Column("gebinde_typ",           sa.String(50), nullable=False),
        sa.Column("menge",                 sa.Numeric(10, 0), nullable=False),
        sa.Column("pfandwert_je_einheit",  sa.Numeric(10, 2)),
        sa.Column("gesamtpfandwert",       sa.Numeric(12, 2)),
        sa.Column("saldo_menge",           sa.Numeric(10, 0)),
        sa.Column("saldo_wert",            sa.Numeric(12, 2)),
        sa.Column("referenz_typ",          sa.String(30)),
        sa.Column("referenz_id",           sa.String),
        sa.Column("referenz_nr",           sa.String(100)),
        sa.Column("notiz",                 sa.Text),
        sa.Column("created_at",            sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by",            sa.String(200)),
        schema="domain_einkauf",
    )
    op.create_index("ix_pfk_tenant_partner", "pfand_konto_buchungen",
                    ["tenant_id", "partner_id"], schema="domain_einkauf")
    op.create_index("ix_pfk_tenant_datum", "pfand_konto_buchungen",
                    ["tenant_id", "buchungsdatum"], schema="domain_einkauf")

    # ── Fremdwaren-Einlagerung ──────────────────────────────────────────────
    op.create_table(
        "fremdwaren_einlagerung",
        sa.Column("id",                    PGUUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id",             sa.String, nullable=False),
        sa.Column("einlagerungs_nr",       sa.String(50), nullable=False),
        sa.Column("eigentuemer_id",        sa.String, nullable=False),
        sa.Column("eigentuemer_name",      sa.String(255)),
        sa.Column("niederlassung_id",      sa.String),
        sa.Column("warehouse_id",          sa.String),
        sa.Column("lagerort",              sa.String(100)),
        sa.Column("article_id",            sa.String),
        sa.Column("artikel_nr",            sa.String(50)),
        sa.Column("artikel_bezeichnung",   sa.String(300)),
        sa.Column("charge",                sa.String(64)),
        sa.Column("einlagerungstyp",       sa.String(20), server_default="fremdware"),
        sa.Column("menge_eingelagert",     sa.Numeric(14, 3), nullable=False),
        sa.Column("menge_aktuell",         sa.Numeric(14, 3), nullable=False),
        sa.Column("einheit",               sa.String(20)),
        sa.Column("einlagerungsdatum",     sa.Date, nullable=False),
        sa.Column("auslagerungsdatum",     sa.Date),
        sa.Column("geplante_auslagerung",  sa.Date),
        sa.Column("gebuehr_pro_tag",       sa.Numeric(10, 4)),
        sa.Column("gebuehr_einheit",       sa.String(20), server_default="t"),
        sa.Column("letzte_abrechnung",     sa.Date),
        sa.Column("status",                sa.String(20), server_default="eingelagert"),
        sa.Column("notiz",                 sa.Text),
        sa.Column("created_at",            sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",            sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("created_by",            sa.String(200)),
        schema="domain_einkauf",
    )
    op.create_index("ix_fwe_tenant_partner", "fremdwaren_einlagerung",
                    ["tenant_id", "eigentuemer_id"], schema="domain_einkauf")
    op.create_index("ix_fwe_tenant_status", "fremdwaren_einlagerung",
                    ["tenant_id", "status"], schema="domain_einkauf")


def downgrade() -> None:
    op.drop_table("fremdwaren_einlagerung",      schema="domain_einkauf")
    op.drop_table("pfand_konto_buchungen",        schema="domain_einkauf")
    op.drop_table("paletten_konto_buchungen",     schema="domain_einkauf")
    op.drop_table("lager_kontenzuordnung",        schema="domain_einkauf")
    op.drop_table("bestellung_positionen",        schema="domain_einkauf")
    op.drop_table("bestellungen",                 schema="domain_einkauf")
    op.drop_table("bestellvorschlag_positionen",  schema="domain_einkauf")
    op.drop_table("bestellvorschlaege",           schema="domain_einkauf")
    op.drop_table("artikel_lager_parameter",      schema="domain_einkauf")
    op.drop_table("kontrakt_positionen",          schema="domain_einkauf")
    op.drop_table("kontrakte",                    schema="domain_einkauf")
    op.drop_table("lieferanten",                  schema="domain_einkauf")
    op.execute("DROP SCHEMA IF EXISTS domain_einkauf CASCADE")
