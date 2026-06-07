"""KIM 360°-CRM Satellit: kunden_crm360 (L3-Vertriebsfelder).

Folgt dem Satelliten-Muster der Kundenstamm-Konsolidierung (KUNDENSTAMM-KONSOLIDIERUNG-001):
die L3-spezifischen 360°-Felder (KV-Limit, Vertreter, Disponent, ABC-/Umsatzstatus,
Chef-Anweisung, Alarmbanner) kommen NICHT in den kunden-Monolithen, sondern in eine
schlanke Satellitentabelle.

Die Kontaktpersonen-Tabelle `public.kunden_ansprechpartner` existiert bereits aus dem
L3-Import (Spalten vorname/nachname/telefon1/anrede/…); KIM nutzt diese unverändert
weiter (kein Neuanlegen — siehe crm_kim.py). kunden_kontakte führt separat die
Kontakthistorie/Wiedervorlage.

Revision ID: kunden_crm360_20260607
Revises: kunden_geo_20260604
"""
from __future__ import annotations

from alembic import op

revision = "kunden_crm360_20260607"
down_revision = "kunden_geo_20260604"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1:1-Satellit von public.kunden — exakt dem etablierten Muster (kunden_zahlung,
    # kunden_aggregates) folgend: kunden_nr VARCHAR(20) als PK + FK ON DELETE CASCADE,
    # KEIN tenant_id (Satelliten haben bewusst keins; Mandant kommt über
    # business_partner_id am Stamm). Siehe kunden_domain_tables_20260602.py.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_crm360 (
            kunden_nr        VARCHAR(20) PRIMARY KEY
                                 REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            kv_limit         NUMERIC(14,2),
            sales_rep_vb     TEXT,
            dispatcher_disp  TEXT,
            abc_status       TEXT,
            revenue_status   TEXT,
            chef_anweisung   TEXT,
            alert_messages   JSONB NOT NULL DEFAULT '[]'::jsonb,
            profile_summary  TEXT,
            cust_group       TEXT,
            co_affiliation   TEXT,
            updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    # kunden_ansprechpartner existiert bereits (L3-Import, ORM-Modell app/verkauf/models.py)
    # und wird unverändert weitergenutzt.


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.kunden_crm360")
