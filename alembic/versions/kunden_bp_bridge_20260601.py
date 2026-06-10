"""Kunden→BusinessPartner Identitäts-Brücke (Phase 1 Stammdaten-Konsolidierung).

Revision ID: kunden_bp_bridge_20260601
Revises: ustva_voranmeldungen_20260527
Create Date: 2026-06-01

Additive Brücke: public.kunden erhält die technische BP-Identität
``business_partner_id`` (UUID → domain_crm.business_partners.partner_id) sowie
``legacy_kunden_nr`` für Alt-/Importnummern. ``kunden_nr`` bleibt fachlicher
Primärschlüssel. Rein additiv, idempotent, ohne Datenbewegung — der FK-Constraint
und das Backfill erfolgen in Phase 2 (nach Merge), hier nur Spalten + Index.
"""

from alembic import op

revision = "kunden_bp_bridge_20260601"
down_revision = "ustva_voranmeldungen_20260527"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden (
            kunden_nr VARCHAR(20) PRIMARY KEY,
            name1 VARCHAR(100) NOT NULL,
            name2 VARCHAR(100),
            name3 VARCHAR(100),
            strasse VARCHAR(100),
            plz VARCHAR(10),
            ort VARCHAR(100),
            land VARCHAR(100),
            postfach VARCHAR(10),
            postfach_plz VARCHAR(10),
            postfach_ort VARCHAR(100),
            tel VARCHAR(50),
            fax VARCHAR(50),
            email VARCHAR(100),
            homepage VARCHAR(200),
            kontonutzung_rechnung BOOLEAN DEFAULT FALSE,
            kontoauszug_gewuenscht BOOLEAN DEFAULT FALSE,
            saldo_druck_rechnung BOOLEAN DEFAULT FALSE,
            druck_verbot_rechnung BOOLEAN DEFAULT FALSE,
            druck_werbetext BOOLEAN DEFAULT FALSE,
            versandpauschalen_berechnen BOOLEAN DEFAULT FALSE,
            einzel_abrechnung VARCHAR(20),
            sammel_abrechnung BOOLEAN DEFAULT FALSE,
            sammel_abrechnung_ohne_einzel BOOLEAN DEFAULT FALSE,
            sammel_abrechnungskennzeichen VARCHAR(50),
            bonus_berechtigung BOOLEAN DEFAULT FALSE,
            bonus_rechnungsempfaenger_id VARCHAR(20)
                REFERENCES public.kunden(kunden_nr),
            bemerkenswerte_forderung BOOLEAN DEFAULT FALSE,
            selbstabrechnung_durch_kunden BOOLEAN DEFAULT FALSE,
            selbstabrechner_verkauf_zukauf VARCHAR(50),
            kunden_zusatz TEXT,
            direktes_konto BOOLEAN DEFAULT FALSE,
            rabatt_verrechnung VARCHAR(20),
            selbstabholer_rabatt NUMERIC(5,2) DEFAULT 0,
            preisermittlung_sorten BOOLEAN DEFAULT FALSE,
            direktabzug BOOLEAN DEFAULT FALSE,
            wochenpreis_ec_basis BOOLEAN DEFAULT FALSE,
            gueltig_ab DATE,
            gueltig_bis DATE,
            zahlungsbedingungen_tage INTEGER,
            skonto NUMERIC(5,2) DEFAULT 0,
            netto_kasse BOOLEAN DEFAULT FALSE,
            mahnwesen BOOLEAN DEFAULT FALSE,
            lastschriftverfahren VARCHAR(20),
            sepa_verfahren BOOLEAN DEFAULT FALSE,
            mandat BOOLEAN DEFAULT FALSE,
            bank VARCHAR(200),
            iban VARCHAR(34),
            bic VARCHAR(11),
            umrechnung_euro BOOLEAN DEFAULT FALSE,
            umrechnungskurs NUMERIC(10,4),
            waehrung VARCHAR(3) DEFAULT 'EUR',
            zinstabelle_id INTEGER,
            letzter_zinstermin DATE,
            saldo_letzte_zinsabrechnung NUMERIC(12,2) DEFAULT 0,
            verrechnung_automatisch BOOLEAN DEFAULT FALSE,
            lade_information TEXT,
            allgemeine_angaben TEXT,
            nachkalkulation BOOLEAN DEFAULT FALSE,
            formular_id INTEGER,
            offene_posten_nicht_aufrufen BOOLEAN DEFAULT FALSE,
            versicherung BOOLEAN DEFAULT FALSE,
            sprachschluessel VARCHAR(2) DEFAULT 'DE',
            statistik_kennzeichen VARCHAR(50),
            landwirtschaftsamt_betriebsnummer VARCHAR(50),
            marktpreis_auswertung BOOLEAN DEFAULT FALSE,
            schwellenwert NUMERIC(12,2) DEFAULT 0,
            webshop_kunde BOOLEAN DEFAULT FALSE,
            selektion_schluessel VARCHAR(50),
            selektion_berechnung TEXT,
            tankkarte_ean_code VARCHAR(50),
            kundenkarten_kennzeichen VARCHAR(50),
            edifact_invoic BOOLEAN DEFAULT FALSE,
            edifact_orders BOOLEAN DEFAULT FALSE,
            edifact_desadv BOOLEAN DEFAULT FALSE,
            rechnungs_sammeldruck BOOLEAN DEFAULT FALSE,
            webshop_kunden_nr VARCHAR(50),
            webshop_bezeichnung VARCHAR(200),
            erstellt_am TIMESTAMP,
            geaendert_am TIMESTAMP,
            geloescht BOOLEAN DEFAULT FALSE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_allgemein_erweitert (
            kunden_nr VARCHAR(20) PRIMARY KEY
                REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            staat VARCHAR(100),
            bundesland VARCHAR(100),
            kunde_seit DATE,
            debitoren_konto VARCHAR(50),
            deb_kto_hauptkonto VARCHAR(50),
            disponent VARCHAR(100),
            vertriebsbeauftragter VARCHAR(100),
            abc_umsatzstatus VARCHAR(50),
            betriebsnummer VARCHAR(50),
            ust_id_nr VARCHAR(50),
            steuernummer VARCHAR(50),
            sperrgrund TEXT,
            kundengruppe VARCHAR(100),
            fax_sperre BOOLEAN DEFAULT FALSE,
            infofeld4 TEXT,
            infofeld5 TEXT,
            infofeld6 TEXT,
            erstellt_am TIMESTAMP,
            geaendert_am TIMESTAMP
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_ansprechpartner (
            id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            kunden_nr VARCHAR(20) NOT NULL
                REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            prioritaet INTEGER DEFAULT 0,
            vorname VARCHAR(100),
            nachname VARCHAR(100),
            position VARCHAR(100),
            abteilung VARCHAR(100),
            telefon1 VARCHAR(50),
            telefon2 VARCHAR(50),
            mobil VARCHAR(50),
            email VARCHAR(100),
            strasse VARCHAR(100),
            plz VARCHAR(10),
            ort VARCHAR(100),
            anrede VARCHAR(20),
            briefanrede VARCHAR(50),
            geburtsdatum DATE,
            hobbys TEXT,
            info1 TEXT,
            info2 TEXT,
            empfanger_rechnung_email BOOLEAN DEFAULT FALSE,
            empfanger_mahnung_email BOOLEAN DEFAULT FALSE,
            kontaktart VARCHAR(50),
            erstanlage DATE,
            cad_system VARCHAR(100),
            softwaresysteme VARCHAR(200),
            datenschutzbeauftragter BOOLEAN DEFAULT FALSE,
            erstellt_am TIMESTAMP,
            geaendert_am TIMESTAMP
        )
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('public.kunden') IS NOT NULL THEN
                ALTER TABLE public.kunden
                    ADD COLUMN IF NOT EXISTS business_partner_id UUID;
                ALTER TABLE public.kunden
                    ADD COLUMN IF NOT EXISTS legacy_kunden_nr VARCHAR(64);
                CREATE INDEX IF NOT EXISTS idx_kunden_business_partner_id
                    ON public.kunden (business_partner_id);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('public.kunden') IS NOT NULL THEN
                DROP INDEX IF EXISTS public.idx_kunden_business_partner_id;
                ALTER TABLE public.kunden DROP COLUMN IF EXISTS legacy_kunden_nr;
                ALTER TABLE public.kunden DROP COLUMN IF EXISTS business_partner_id;
            END IF;
        END $$;
        """
    )
