"""Phase 2D Schritt 3: kunden_lookup liest Adresse aus kunden_adressen.

Revision ID: kunden_lookup_adressen_20260602
Revises: kunden_domain_tables_20260602
Create Date: 2026-06-02

Nach dem Backfill (public.kunden -> kunden_adressen) wird die View
public.kunden_lookup so umgestellt, dass plz/ort/strasse aus der Haupt-Adresse
(kunden_adressen, adress_typ='haupt') kommen. COALESCE-Fallback auf public.kunden
hält die View während der Übergangszeit robust für Kunden ohne Adresszeile.
Spaltenliste/-typen unverändert -> CREATE OR REPLACE VIEW genügt.
"""

from alembic import op

revision = "kunden_lookup_adressen_20260602"
down_revision = "kunden_domain_tables_20260602"
branch_labels = None
depends_on = None

_MATCHCODE = "lower(regexp_replace(coalesce(k.name1, ''), '[^a-zA-Z0-9]', '', 'g'))"


def upgrade() -> None:
    # DROP+CREATE statt REPLACE: COALESCE über unterschiedlich lange varchar
    # (kunden_adressen vs. public.kunden) ergibt längenloses varchar -> REPLACE
    # verweigert die Spaltentyp-Änderung. An der View hängt DB-seitig nichts
    # (nur Laufzeit-SELECTs via BusinessPartnerService.search_lookup).
    op.execute("DROP VIEW IF EXISTS public.kunden_lookup")
    op.execute(
        f"""
        CREATE VIEW public.kunden_lookup AS
        SELECT
            k.business_partner_id,
            k.kunden_nr,
            k.name1                                AS name,
            {_MATCHCODE}                           AS matchcode,
            (NOT coalesce(k.geloescht, FALSE))     AS aktiv,
            coalesce(a.plz, k.plz)                 AS plz,
            coalesce(a.ort, k.ort)                 AS ort,
            coalesce(a.strasse, k.strasse)         AS strasse,
            ae.ust_id_nr,
            ae.kundengruppe,
            ae.vertriebsbeauftragter               AS betreuer,
            ae.sperrgrund
        FROM public.kunden k
        LEFT JOIN public.kunden_adressen a
               ON a.kunden_nr = k.kunden_nr AND a.adress_typ = 'haupt'
        LEFT JOIN public.kunden_allgemein_erweitert ae ON ae.kunden_nr = k.kunden_nr
        WHERE coalesce(k.geloescht, FALSE) = FALSE
        """
    )


def downgrade() -> None:
    # Übergangsvariante wiederherstellen: Adresse direkt aus public.kunden.
    op.execute("DROP VIEW IF EXISTS public.kunden_lookup")
    op.execute(
        f"""
        CREATE VIEW public.kunden_lookup AS
        SELECT
            k.business_partner_id,
            k.kunden_nr,
            k.name1                                AS name,
            {_MATCHCODE}                           AS matchcode,
            (NOT coalesce(k.geloescht, FALSE))     AS aktiv,
            k.plz, k.ort, k.strasse,
            ae.ust_id_nr,
            ae.kundengruppe,
            ae.vertriebsbeauftragter               AS betreuer,
            ae.sperrgrund
        FROM public.kunden k
        LEFT JOIN public.kunden_allgemein_erweitert ae ON ae.kunden_nr = k.kunden_nr
        WHERE coalesce(k.geloescht, FALSE) = FALSE
        """
    )
