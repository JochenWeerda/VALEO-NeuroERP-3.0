"""Phase 2D Schritt 2: schlanke Domänentabellen für public.kunden (additiv, leer).

Revision ID: kunden_domain_tables_20260602
Revises: perf_indexes_apply_20260602
Create Date: 2026-06-02

Legt die in docs/kunden-konsolidierung.md §8 als NEU klassifizierten
Domänentabellen an, um public.kunden (83 Spalten) später zu verschlanken:

  - kunden_adressen        Haupt-/Liefer-/Postfach-/Rechnungsadressen (1:n)
  - kunden_zahlung         Zahl-/Mahn-/Abrechnungs-Flags (1:1)
  - kunden_external_refs   Fremdschlüssel/Altnummern (typ, wert) (1:n)
  - kunden_aggregates      abgeleitete Kennzahlen (Umsatz/letzter Auftrag/OP) (1:1)

Alle hängen über kunden_nr (PK von public.kunden, varchar(20)) mit
ON DELETE CASCADE. public.kunden hat kein tenant_id → die Satelliten ebenso
nicht (Identität/Mandant kommt perspektivisch über business_partner_id).

WICHTIG: rein additiv + idempotent (CREATE TABLE IF NOT EXISTS). KEIN
Datenumzug, KEIN Drop von Altspalten. Backfill aus public.kunden und das
Deprecaten der Altspalten erfolgen separat mit DB-Backup + Freigabe (Phase 2D
Schritt 3+). kunden_aggregates ist bewusst eine abgeleitete Performance-/
Temp-Tabelle (refresh aus Verkauf/FiBu), keine Stammdatenwahrheit.
"""

from alembic import op

revision = "kunden_domain_tables_20260602"
down_revision = "perf_indexes_apply_20260602"
branch_labels = None
depends_on = None

_TABLES = ["kunden_adressen", "kunden_zahlung", "kunden_external_refs", "kunden_aggregates"]


def upgrade() -> None:
    # Adressen (1:n, Typ haupt/liefer/postfach/rechnung)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_adressen (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            kunden_nr     VARCHAR(20) NOT NULL REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            adress_typ    VARCHAR(20) NOT NULL DEFAULT 'haupt',
            strasse       VARCHAR(200),
            plz           VARCHAR(10),
            ort           VARCHAR(120),
            land          VARCHAR(60),
            postfach      VARCHAR(60),
            postfach_plz  VARCHAR(10),
            postfach_ort  VARCHAR(120),
            ist_standard  BOOLEAN NOT NULL DEFAULT FALSE,
            created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_kunden_adressen_kunden_nr ON public.kunden_adressen (kunden_nr)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_kunden_adressen_plz_ort ON public.kunden_adressen (plz, ort)")

    # Zahlung/Abrechnung (1:1)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_zahlung (
            kunden_nr                     VARCHAR(20) PRIMARY KEY REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            -- Spaltentypen spiegeln die (inkonsistenten) Legacy-Typen von
            -- public.kunden für einen verlustfreien Lift-and-Shift; Normalisierung
            -- (z. B. lastschriftverfahren/einzel_abrechnung → boolean) später.
            zahlungsbedingungen_tage      INTEGER,
            skonto                        NUMERIC(6,3),
            netto_kasse                   BOOLEAN,
            mahnwesen                     BOOLEAN,
            lastschriftverfahren          VARCHAR(40),
            sepa_verfahren                BOOLEAN,
            mandat                        BOOLEAN,
            kontonutzung_rechnung         BOOLEAN,
            kontoauszug_gewuenscht        BOOLEAN,
            saldo_druck_rechnung          BOOLEAN,
            druck_verbot_rechnung         BOOLEAN,
            einzel_abrechnung             VARCHAR(40),
            sammel_abrechnung             BOOLEAN,
            sammel_abrechnungskennzeichen VARCHAR(20),
            bonus_berechtigung            BOOLEAN,
            bonus_rechnungsempfaenger_id  VARCHAR(20),
            selbstabrechnung_durch_kunden BOOLEAN,
            offene_posten_nicht_aufrufen  BOOLEAN,
            rabatt_verrechnung            VARCHAR(20),
            selbstabholer_rabatt          NUMERIC(6,3),
            created_at                    TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at                    TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    # External Refs / Altnummern (1:n, typ+wert)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_external_refs (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            kunden_nr   VARCHAR(20) NOT NULL REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            ref_typ     VARCHAR(40) NOT NULL,
            ref_wert    VARCHAR(100) NOT NULL,
            quelle      VARCHAR(40),
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_kunden_external_refs UNIQUE (kunden_nr, ref_typ, ref_wert)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_kunden_external_refs_lookup ON public.kunden_external_refs (ref_typ, ref_wert)")

    # Aggregate / abgeleitete Kennzahlen (1:1, Performance-/Temp-Schicht)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_aggregates (
            kunden_nr               VARCHAR(20) PRIMARY KEY REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            umsatz_ytd              NUMERIC(15,2),
            umsatz_vorjahr          NUMERIC(15,2),
            letzter_auftrag_am      DATE,
            letzter_auftrag_betrag  NUMERIC(15,2),
            offene_posten_summe     NUMERIC(15,2),
            offene_posten_anzahl    INTEGER,
            saldo                   NUMERIC(15,2),
            aktualisiert_am         TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )


def downgrade() -> None:
    for t in _TABLES:
        op.execute(f"DROP TABLE IF EXISTS public.{t} CASCADE")
