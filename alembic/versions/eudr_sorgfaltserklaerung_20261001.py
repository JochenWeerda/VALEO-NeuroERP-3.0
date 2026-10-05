"""Die EUDR-Sorgfaltserklaerung bekommt die Form, die die Verordnung vorgibt.

``domain_compliance.eudr_due_diligence`` legte keine Migration an. Der Code
kannte davon nur ein ``COUNT(*) WHERE tenant_id`` — zu wenig, um eine Tabelle
daraus abzuleiten, und deshalb blieb die Luecke im Vorgaenger-Slice bewusst
offen. Sie wird jetzt nach dem Verordnungstext geschlossen, nicht nach dem, was
der Code zufaellig anfasst.

**Grundlage:** Verordnung (EU) 2023/1115 (EUDR).

* **Anhang II** schreibt den Inhalt der Sorgfaltserklaerung vor: Marktteilnehmer
  mit Anschrift und EORI-Nummer, HS-Code mit Warenbeschreibung und Menge,
  Produktionsland mit Geolokation der Flurstuecke und Produktionszeitraum, die
  Referenznummern vorgelagerter Erklaerungen, die Erklaerung selbst sowie
  Unterschrift mit Name und Funktion.
* **Art. 9** verlangt die Informationen, auf die sich die Erklaerung stuetzt —
  darunter die **Geolokation aller Flurstuecke**, Angaben zu Lieferanten und
  belastbare, nachpruefbare Nachweise, dass das Erzeugnis abholzungsfrei ist und
  nach dem Recht des Erzeugerlandes hergestellt wurde. Fuer Flurstuecke ueber
  **vier Hektar** ist die Geolokation als **Polygon** anzugeben.
* **Art. 10/11** verlangen Risikobewertung und, bei mehr als
  vernachlaessigbarem Risiko, Minderungsmassnahmen.
* **Art. 3/4** verbieten das Inverkehrbringen, solange nicht hoechstens ein
  vernachlaessigbares Risiko festgestellt und die Erklaerung abgegeben ist.
* **Art. 33** regelt das EU-Informationssystem, aus dem Referenz- und
  Verifizierungsnummer stammen.
* **Art. 2** definiert "abholzungsfrei" mit dem Stichtag **31.12.2020**. Daraus
  folgt **keine** Datumsbedingung auf den Produktionszeitraum: Nicht die
  Herstellung muss vor dem Stichtag liegen, sondern die Flaeche darf nach ihm
  nicht abgeholzt worden sein. Deshalb traegt das ein Nachweisfeld, keine
  Pruefbedingung.

Drei Dinge haelt die Datenbank, und jedes steht im Verordnungstext:

1. **Eingereicht nur mit vernachlaessigbarem Risiko**, Referenznummer und
   abgegebener Erklaerung (Art. 3/4). Eine eingereichte Erklaerung ohne
   Risikobewertung ist keine Sorgfalt, sondern eine Behauptung.
2. **Flurstuecke ueber vier Hektar nur als Polygon** (Art. 9).
3. Die sieben **relevanten Rohstoffe** und die zwei **Risikostufen** als
   Wertemengen.

Der Feldsatz folgt dem Verordnungstext; die fachjuristische Abnahme gehoert dem
Compliance-Owner. Siehe ``docs/quality-assurance/eudr-sorgfaltserklaerung-20261001.md``.

Revision ID: eudr_sorgfaltserklaerung_20261001
Revises: bank_legacy_retirement_20261001
"""

from __future__ import annotations

from alembic import op

revision = "eudr_sorgfaltserklaerung_20261001"
down_revision = "bank_legacy_retirement_20261001"
branch_labels = None
depends_on = None

#: Die relevanten Rohstoffe nach Anhang I der Verordnung.
ROHSTOFFE = (
    "RIND",
    "KAKAO",
    "KAFFEE",
    "OELPALME",
    "KAUTSCHUK",
    "SOJA",
    "HOLZ",
)

#: Art. 10: Die Risikobewertung endet in einer dieser beiden Feststellungen.
RISIKOSTUFEN = ("VERNACHLAESSIGBAR", "NICHT_VERNACHLAESSIGBAR")

STAENDE = ("ENTWURF", "EINGEREICHT", "ZURUECKGEZOGEN")

#: Art. 9: Ab dieser Groesse ist die Geolokation als Polygon anzugeben.
POLYGONGRENZE_HA = 4


def _in(spalte: str, werte: tuple[str, ...]) -> str:
    return f"{spalte} IN (" + ", ".join(f"'{w}'" for w in werte) + ")"


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_compliance")

    op.execute(
        f"""
        CREATE TABLE IF NOT EXISTS domain_compliance.eudr_due_diligence (
            id                              VARCHAR(64)  PRIMARY KEY,
            tenant_id                       VARCHAR(80)  NOT NULL,

            -- Anhang II Nr. 1: Marktteilnehmer
            betreiber_name                  VARCHAR(255) NOT NULL,
            betreiber_adresse               TEXT         NOT NULL,
            eori_nummer                     VARCHAR(32),

            -- Anhang II Nr. 2: Erzeugnis
            rohstoff                        VARCHAR(16)  NOT NULL,
            hs_code                         VARCHAR(16)  NOT NULL,
            warenbeschreibung               TEXT         NOT NULL,
            menge_netto_kg                  NUMERIC(16, 3) NOT NULL,
            menge_volumen_m3                NUMERIC(16, 3),
            ergaenzende_einheit             VARCHAR(32),

            -- Anhang II Nr. 3 / Art. 9: Herstellung
            produktionsland                 VARCHAR(2)   NOT NULL,
            produktion_von                  DATE         NOT NULL,
            produktion_bis                  DATE         NOT NULL,

            -- Art. 9: Lieferkette
            lieferant_name                  VARCHAR(255) NOT NULL,
            lieferant_adresse               TEXT,
            lieferant_email                 VARCHAR(255),

            -- Art. 9: belastbare, nachpruefbare Nachweise. Der Stichtag
            -- 31.12.2020 (Art. 2) wird hier nachgewiesen, nicht gerechnet.
            nachweis_abholzungsfrei         BOOLEAN      NOT NULL DEFAULT FALSE,
            nachweis_abholzungsfrei_quelle  TEXT,
            nachweis_rechtskonform          BOOLEAN      NOT NULL DEFAULT FALSE,
            nachweis_rechtskonform_quelle   TEXT,

            -- Art. 10/11: Risikobewertung und Minderung
            risikostufe                     VARCHAR(32),
            risikobewertung_am              TIMESTAMPTZ,
            risikobewertung_durch           VARCHAR(255),
            minderungsmassnahmen            TEXT,

            -- Anhang II Nr. 5/6: die Erklaerung und ihre Unterzeichnung
            erklaerung_abgegeben_am         TIMESTAMPTZ,
            erklaerung_durch_name           VARCHAR(255),
            erklaerung_durch_funktion       VARCHAR(255),

            -- Art. 33: EU-Informationssystem
            referenznummer                  VARCHAR(64),
            verifizierungsnummer            VARCHAR(64),
            eingereicht_am                  TIMESTAMPTZ,

            status                          VARCHAR(16)  NOT NULL DEFAULT 'ENTWURF',
            created_at                      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at                      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

            CONSTRAINT ck_eudr_rohstoff CHECK ({_in('rohstoff', ROHSTOFFE)}),
            CONSTRAINT ck_eudr_status   CHECK ({_in('status', STAENDE)}),
            CONSTRAINT ck_eudr_risikostufe CHECK (
                risikostufe IS NULL OR {_in('risikostufe', RISIKOSTUFEN)}
            ),
            CONSTRAINT ck_eudr_zeitraum CHECK (produktion_bis >= produktion_von),
            CONSTRAINT ck_eudr_menge CHECK (menge_netto_kg > 0),

            -- Art. 3/4: Inverkehrbringen nur, wenn die Sorgfalt geleistet und
            -- hoechstens ein vernachlaessigbares Risiko festgestellt ist. Eine
            -- eingereichte Erklaerung ohne Risikobewertung, ohne Nachweise und
            -- ohne Unterzeichnung ist keine Sorgfalt, sondern eine Behauptung.
            CONSTRAINT ck_eudr_einreichung CHECK (
                status <> 'EINGEREICHT' OR (
                    risikostufe = 'VERNACHLAESSIGBAR'
                    AND risikobewertung_am IS NOT NULL
                    AND nachweis_abholzungsfrei
                    AND nachweis_rechtskonform
                    AND erklaerung_abgegeben_am IS NOT NULL
                    AND erklaerung_durch_name IS NOT NULL
                    AND erklaerung_durch_funktion IS NOT NULL
                    AND referenznummer IS NOT NULL
                    AND eingereicht_am IS NOT NULL
                )
            ),
            -- Art. 11: Bei mehr als vernachlaessigbarem Risiko sind
            -- Minderungsmassnahmen zu ergreifen — und zu dokumentieren.
            CONSTRAINT ck_eudr_minderung CHECK (
                risikostufe <> 'NICHT_VERNACHLAESSIGBAR'
                OR minderungsmassnahmen IS NOT NULL
            )
        )
        """
    )
    # Die Referenznummer stammt aus dem EU-Informationssystem und ist dort
    # eindeutig. Zwei Erklaerungen mit derselben Nummer waeren zwei Wahrheiten
    # ueber denselben Vorgang.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_eudr_referenznummer "
        "ON domain_compliance.eudr_due_diligence (referenznummer) "
        "WHERE referenznummer IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_eudr_tenant_status "
        "ON domain_compliance.eudr_due_diligence (tenant_id, status, created_at DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_eudr_tenant_rohstoff_land "
        "ON domain_compliance.eudr_due_diligence (tenant_id, rohstoff, produktionsland)"
    )

    # Art. 9: Geolokation **aller** Flurstuecke. Ein Erzeugnis kann von vielen
    # Flurstuecken stammen, deshalb eine eigene Tabelle.
    op.execute(
        f"""
        CREATE TABLE IF NOT EXISTS domain_compliance.eudr_geolokationen (
            id                 VARCHAR(64)  PRIMARY KEY,
            tenant_id          VARCHAR(80)  NOT NULL,
            erklaerung_id      VARCHAR(64)  NOT NULL
                REFERENCES domain_compliance.eudr_due_diligence (id) ON DELETE CASCADE,
            flurstueck_kennung VARCHAR(128),
            breitengrad        NUMERIC(9, 6)  NOT NULL,
            laengengrad        NUMERIC(9, 6)  NOT NULL,
            flaeche_ha         NUMERIC(12, 4),
            polygon            JSONB,
            erfasst_am         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

            CONSTRAINT ck_eudr_geo_breite CHECK (breitengrad BETWEEN -90 AND 90),
            CONSTRAINT ck_eudr_geo_laenge CHECK (laengengrad BETWEEN -180 AND 180),
            CONSTRAINT ck_eudr_geo_flaeche CHECK (flaeche_ha IS NULL OR flaeche_ha > 0),
            -- Art. 9: Ab vier Hektar ist die Geolokation als Polygon
            -- anzugeben. Ein Punkt genuegt dann nicht.
            CONSTRAINT ck_eudr_geo_polygonpflicht CHECK (
                flaeche_ha IS NULL
                OR flaeche_ha <= {POLYGONGRENZE_HA}
                OR polygon IS NOT NULL
            )
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_eudr_geo_erklaerung "
        "ON domain_compliance.eudr_geolokationen (erklaerung_id)"
    )

    # Anhang II Nr. 4 / Art. 4: Wer sich auf vorgelagerte Erklaerungen stuetzt,
    # fuehrt deren Referenznummern mit.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_compliance.eudr_vorgelagerte_erklaerungen (
            id                   VARCHAR(64)  PRIMARY KEY,
            tenant_id            VARCHAR(80)  NOT NULL,
            erklaerung_id        VARCHAR(64)  NOT NULL
                REFERENCES domain_compliance.eudr_due_diligence (id) ON DELETE CASCADE,
            referenznummer       VARCHAR(64)  NOT NULL,
            verifizierungsnummer VARCHAR(64),
            lieferant_name       VARCHAR(255),
            erfasst_am           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_eudr_vorgelagert_je_erklaerung "
        "ON domain_compliance.eudr_vorgelagerte_erklaerungen (erklaerung_id, referenznummer)"
    )


def downgrade() -> None:
    # Kein DROP TABLE auf der Erklaerung: Sie ist der Nachweis, mit dem ein
    # Erzeugnis in Verkehr gebracht wurde, und aufbewahrungspflichtig.
    # Zurueckgenommen werden nur die beiden Satellitentabellen, die diese
    # Migration neu angelegt hat, und die Indizes.
    op.execute("DROP TABLE IF EXISTS domain_compliance.eudr_vorgelagerte_erklaerungen")
    op.execute("DROP TABLE IF EXISTS domain_compliance.eudr_geolokationen")
    for index in (
        "ux_eudr_referenznummer",
        "ix_eudr_tenant_status",
        "ix_eudr_tenant_rohstoff_land",
    ):
        op.execute(f"DROP INDEX IF EXISTS domain_compliance.{index}")
