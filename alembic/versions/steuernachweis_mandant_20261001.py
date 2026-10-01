"""Steuerliche Nachweise bekommen eine Migration — und einen Mandanten.

Drei Tabellen legt keine Migration an:
``domain_compliance.gelangensbestaetigung``, ``.intrastat_meldungen`` und
``.lksg_supplier_risk_assessments``. Auf einer frischen Installation laufen die
Masken dort ins Leere.

Zwei von ihnen kennen ausserdem keinen Mandanten. Ihre Module nehmen
``get_tenant_id`` entgegen und **benutzen ihn nicht** — kein einziger Filter.
Deshalb traegt hier jede Tabelle ``tenant_id NOT NULL``:

* Die **Gelangensbestaetigung** ist der Nachweis, mit dem eine
  innergemeinschaftliche Lieferung steuerfrei bleibt (§ 6a UStG, § 17a UStDV).
  Sie enthaelt Kundennummer, Empfaengername und die **USt-IdNr.** des
  Empfaengers — Daten eines Dritten, die kein anderes Haus sehen darf.
* Die **Intrastat-Meldung** geht an das Statistische Bundesamt. Ein Export, der
  die Zeilen eines fremden Hauses enthaelt, ist eine falsche Meldung.

Die Form stammt aus den ``INSERT``-Spalten und den Pydantic-Modellen der beiden
Module. Ergaenzt sind ``tenant_id`` und drei Eindeutigkeiten, jede fuer einen
benannten Grund:

* **Ein Token je Bestaetigung, global eindeutig.** Der Empfaenger bestaetigt
  ueber einen Link; zwei gleiche Token waeren zwei Nachweise, die sich
  gegenseitig ueberschreiben.
* **Eine Meldenummer je Haus und Meldezeitraum.** Der Nummernkreis wurde vorher
  mit ``COUNT(*)`` ueber **alle** Haeuser gezogen.
* **Eine Gelangensbestaetigung je Haus und Lieferschein.** Zwei Nachweise zum
  selben Lieferschein sind kein Nachweis, sondern eine Frage.

``domain_compliance.eudr_due_diligence`` bleibt **offen**: Der Code kennt davon
nur ein ``COUNT(*) WHERE tenant_id``. Das genuegt nicht, um eine
EUDR-Sorgfaltserklaerung zu definieren, und sie zu erfinden waere hier
besonders falsch.

Revision ID: steuernachweis_mandant_20261001
Revises: periode_statuswoerterbuch_20261001
"""

from __future__ import annotations

from alembic import op

revision = "steuernachweis_mandant_20261001"
down_revision = "periode_statuswoerterbuch_20261001"
branch_labels = None
depends_on = None

#: Die Wertemengen, die die Module selbst pruefen.
GB_STAENDE = ("AUSSTEHEND", "ERHALTEN", "ABGELAUFEN")
INTRASTAT_STAENDE = ("ENTWURF", "GEMELDET", "STORNIERT")
INTRASTAT_ARTEN = ("EINGANG", "VERSAND")
LKSG_STUFEN = ("NIEDRIG", "MITTEL", "HOCH")


def _in(spalte: str, werte: tuple[str, ...]) -> str:
    return f"{spalte} IN (" + ", ".join(f"'{w}'" for w in werte) + ")"


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_compliance")

    op.execute(
        f"""
        CREATE TABLE IF NOT EXISTS domain_compliance.gelangensbestaetigung (
            id                   VARCHAR(64)  PRIMARY KEY,
            tenant_id            VARCHAR(80)  NOT NULL,
            lieferschein_nr      VARCHAR(64)  NOT NULL,
            rechnung_nr          VARCHAR(64),
            kunde_nr             VARCHAR(64)  NOT NULL,
            bestimmungsland_code VARCHAR(2)   NOT NULL,
            warenwert_eur        NUMERIC(14, 2) NOT NULL,
            versanddatum         DATE         NOT NULL,
            empfaenger_name      VARCHAR(255) NOT NULL,
            empfaenger_ust_id_nr VARCHAR(32),
            status               VARCHAR(16)  NOT NULL DEFAULT 'AUSSTEHEND',
            token                VARCHAR(64)  NOT NULL,
            erinnerung_am        DATE,
            erhalten_am          TIMESTAMPTZ,
            created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            CONSTRAINT ck_gelangensbestaetigung_status CHECK ({_in('status', GB_STAENDE)}),
            -- Ein erhaltener Nachweis braucht den Zeitpunkt, an dem er erhalten
            -- wurde; das ist das Beweisstueck, nicht der Status.
            CONSTRAINT ck_gelangensbestaetigung_erhalten CHECK (
                status <> 'ERHALTEN' OR erhalten_am IS NOT NULL
            )
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_gelangensbestaetigung_token "
        "ON domain_compliance.gelangensbestaetigung (token)"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_gelangensbestaetigung_tenant_lieferschein "
        "ON domain_compliance.gelangensbestaetigung (tenant_id, lieferschein_nr)"
    )
    # Gelesen wird "was ist in meinem Haus offen und faellig?".
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_gelangensbestaetigung_tenant_faellig "
        "ON domain_compliance.gelangensbestaetigung (tenant_id, status, erinnerung_am)"
    )

    op.execute(
        f"""
        CREATE TABLE IF NOT EXISTS domain_compliance.intrastat_meldungen (
            id                      VARCHAR(64)  PRIMARY KEY,
            tenant_id               VARCHAR(80)  NOT NULL,
            meldenummer             VARCHAR(64)  NOT NULL,
            meldezeitraum           VARCHAR(7)   NOT NULL,
            meldungsart             VARCHAR(16)  NOT NULL,
            cn8_warennummer         VARCHAR(8)   NOT NULL,
            ursprungsland           VARCHAR(2),
            bestimmungsland         VARCHAR(2),
            statistischer_wert_eur  NUMERIC(14, 2) NOT NULL,
            nettomasse_kg           NUMERIC(14, 3) NOT NULL,
            menge                   NUMERIC(14, 3),
            mengeneinheit           VARCHAR(16),
            geschaeftsvorgang_code  VARCHAR(8),
            status                  VARCHAR(16)  NOT NULL DEFAULT 'ENTWURF',
            created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMPTZ,
            CONSTRAINT ck_intrastat_status CHECK ({_in('status', INTRASTAT_STAENDE)}),
            CONSTRAINT ck_intrastat_art    CHECK ({_in('meldungsart', INTRASTAT_ARTEN)}),
            -- Der Meldezeitraum ist JJJJ-MM. Eine Meldung ohne erkennbaren
            -- Zeitraum kann nicht gemeldet werden.
            CONSTRAINT ck_intrastat_zeitraum CHECK (meldezeitraum ~ '^[0-9]{{4}}-[0-9]{{2}}$')
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_intrastat_tenant_zeitraum_nummer "
        "ON domain_compliance.intrastat_meldungen (tenant_id, meldezeitraum, meldenummer)"
    )
    # Gelesen wird "meine Meldungen dieses Zeitraums" — auch fuer den Export.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_intrastat_tenant_zeitraum "
        "ON domain_compliance.intrastat_meldungen (tenant_id, meldezeitraum, meldungsart)"
    )

    op.execute(
        f"""
        CREATE TABLE IF NOT EXISTS domain_compliance.lksg_supplier_risk_assessments (
            id                  VARCHAR(64)  PRIMARY KEY,
            tenant_id           VARCHAR(80)  NOT NULL,
            supplier_id         VARCHAR(80)  NOT NULL,
            country_code        VARCHAR(2)   NOT NULL,
            spend_eur           NUMERIC(14, 2),
            sector_risk         VARCHAR(32),
            human_rights_flags  JSONB        NOT NULL DEFAULT '[]'::jsonb,
            environmental_flags JSONB        NOT NULL DEFAULT '[]'::jsonb,
            mitigation_note     TEXT,
            risk_score          NUMERIC(6, 2),
            risk_level          VARCHAR(16),
            created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            CONSTRAINT ck_lksg_risk_level CHECK (
                risk_level IS NULL OR {_in('risk_level', LKSG_STUFEN)}
            )
        )
        """
    )
    # Gelesen wird "die Bewertungen meines Hauses, neueste zuerst" und die
    # Verteilung je Risikostufe.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lksg_tenant_erstellt "
        "ON domain_compliance.lksg_supplier_risk_assessments (tenant_id, created_at DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lksg_tenant_stufe "
        "ON domain_compliance.lksg_supplier_risk_assessments (tenant_id, risk_level)"
    )


def downgrade() -> None:
    # Kein DROP TABLE: Die Tabellen tragen steuerliche und
    # lieferkettenrechtliche Nachweise. Zurueckgenommen werden nur die Indizes
    # und Bedingungen, die diese Migration hinzugefuegt hat.
    for index in (
        "ux_gelangensbestaetigung_token",
        "ux_gelangensbestaetigung_tenant_lieferschein",
        "ix_gelangensbestaetigung_tenant_faellig",
        "ux_intrastat_tenant_zeitraum_nummer",
        "ix_intrastat_tenant_zeitraum",
        "ix_lksg_tenant_erstellt",
        "ix_lksg_tenant_stufe",
    ):
        op.execute(f"DROP INDEX IF EXISTS domain_compliance.{index}")
