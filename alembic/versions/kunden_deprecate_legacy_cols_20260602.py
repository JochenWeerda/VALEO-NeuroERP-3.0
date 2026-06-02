"""Phase 2D Schritt 4: Altspalten in public.kunden deprecaten (nur Metadaten).

Revision ID: kunden_deprecate_legacy_cols_20260602
Revises: kunden_lookup_adressen_20260602
Create Date: 2026-06-02

Markiert die nach kunden_adressen / kunden_zahlung / kunden_external_refs
ausgelagerten Altspalten von public.kunden via COMMENT ON COLUMN als DEPRECATED
(Pointer auf den jeweiligen Satelliten). Voraussetzung erfuellt: Backfill ist
fuer alle nicht geloeschten Kunden vollstaendig (verifiziert vor dieser Revision).

Rein additiv/Metadaten — die Spalten bleiben funktional (Reader-Fallback in
BusinessPartnerService.get_customer_*). KEIN Drop. Das Entfernen des Fallbacks
und der DROP der Spalten erfolgen in Schritt 5 (separat), erst wenn die
Beobachtung 0 Fallback-Zugriffe zeigt.
"""

from alembic import op

revision = "kunden_deprecate_legacy_cols_20260602"
down_revision = "kunden_lookup_adressen_20260602"
branch_labels = None
depends_on = None

# Altspalte -> Ziel-Satellit. Nur Spalten, deren Daten tatsaechlich gebackfillt
# wurden. business_partner_id / legacy_kunden_nr (Bruecke), Kern- und noch nicht
# migrierte Felder (Bank, Profil, Versand, Genossenschaft) bleiben unberuehrt.
_COL_TO_SATELLITE = {
    # Adresse -> public.kunden_adressen
    "strasse": "public.kunden_adressen",
    "plz": "public.kunden_adressen",
    "ort": "public.kunden_adressen",
    "land": "public.kunden_adressen",
    "postfach": "public.kunden_adressen",
    "postfach_plz": "public.kunden_adressen",
    "postfach_ort": "public.kunden_adressen",
    # Zahlung/Abrechnung -> public.kunden_zahlung
    "zahlungsbedingungen_tage": "public.kunden_zahlung",
    "skonto": "public.kunden_zahlung",
    "netto_kasse": "public.kunden_zahlung",
    "mahnwesen": "public.kunden_zahlung",
    "lastschriftverfahren": "public.kunden_zahlung",
    "sepa_verfahren": "public.kunden_zahlung",
    "mandat": "public.kunden_zahlung",
    "kontonutzung_rechnung": "public.kunden_zahlung",
    "kontoauszug_gewuenscht": "public.kunden_zahlung",
    "saldo_druck_rechnung": "public.kunden_zahlung",
    "druck_verbot_rechnung": "public.kunden_zahlung",
    "einzel_abrechnung": "public.kunden_zahlung",
    "sammel_abrechnung": "public.kunden_zahlung",
    "sammel_abrechnungskennzeichen": "public.kunden_zahlung",
    "bonus_berechtigung": "public.kunden_zahlung",
    "bonus_rechnungsempfaenger_id": "public.kunden_zahlung",
    "selbstabrechnung_durch_kunden": "public.kunden_zahlung",
    "offene_posten_nicht_aufrufen": "public.kunden_zahlung",
    "rabatt_verrechnung": "public.kunden_zahlung",
    "selbstabholer_rabatt": "public.kunden_zahlung",
    # External Refs / Altnummern -> public.kunden_external_refs
    "webshop_kunden_nr": "public.kunden_external_refs",
    "tankkarte_ean_code": "public.kunden_external_refs",
    "kundenkarten_kennzeichen": "public.kunden_external_refs",
}

_NOTE = (
    "DEPRECATED 2026-06-02 (Kundenstamm-Konsolidierung Schritt 4): Wert wird aus "
    "{sat} gelesen (BusinessPartnerService.get_customer_*). Spalte bleibt vorerst "
    "als Fallback; Drop in Schritt 5 nach Entfernen des Reader-Fallbacks."
)


def upgrade() -> None:
    for col, sat in _COL_TO_SATELLITE.items():
        note = _NOTE.format(sat=sat)
        op.execute(f"COMMENT ON COLUMN public.kunden.{col} IS '{note}'")


def downgrade() -> None:
    for col in _COL_TO_SATELLITE:
        op.execute(f"COMMENT ON COLUMN public.kunden.{col} IS NULL")
