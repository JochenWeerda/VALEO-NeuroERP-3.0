"""Die Erklaerung weiss, ob sie uebermittelt ist — und der Zukauf, ob er geprueft ist.

Die EU betreibt fuer EUDR ein Informationssystem (Art. 33), an das sich ein
ERP anbinden kann. Es hat **zwei Richtungen**, und beide gehoeren in das Modell:

* **hinaus** — die eigene Sorgfaltserklaerung uebermitteln und dafuer Referenz-
  und Verifizierungsnummer zurueckbekommen. Das betrifft das Haus als
  Marktteilnehmer, der in Verkehr bringt (Art. 4).
* **herein** — eine **vorgelagerte** Erklaerung anhand von Referenz- und
  Verifizierungsnummer nachpruefen. Das betrifft das Haus als Haendler, der
  Ware mit fremder Erklaerung zukauft und die Nummern weitergibt (Art. 4/5).

Die zweite Richtung ist die, die ein Landhandel die meiste Zeit braucht: Er ist
oefter Zwischenhaendler als Erst-Inverkehrbringer. Bis hierhin trug das Register
die Nummern einer vorgelagerten Erklaerung, aber **nichts darueber, ob sie
jemand geprueft hat** — eine abgeschriebene Nummer sah aus wie ein Nachweis.

**Was diese Migration anlegt, und was ausdruecklich nicht:**

Sie legt die **Zustaende** beider Richtungen an. Sie legt **keinen** Transport
an: Der genaue Dienst, seine Fassung, seine Operationen und die
WS-Security-Zugangsdaten gehoeren in die Konfiguration und sind gegen die
Beschreibung der Kommission zu pruefen — eine erfundene Feldzuordnung waere hier
schlimmer als keine. Die Spalten sind deshalb transportneutral: Sie halten das
Ergebnis einer Uebermittlung oder Pruefung fest, unabhaengig davon, ob es ein
Dienst oder ein Mensch eingetragen hat.

**Zwei Umgebungen, nicht eine.** Das EU-Informationssystem wird ueber die
Kennung des Webdienst-Mandanten angesprochen, und die unterscheidet
Produktionsbetrieb von Annahmetest (``eudr-repository`` gegen ``eudr-test``).
Nur die erste hat rechtliche Wirkung. ``uebermittlung_umgebung`` haelt das fest,
und der Stand des Hauses zaehlt eine Probe **nicht** als Abgabe — sonst sieht
ein eingerichteter Testzugang wie Erfuellung aus.

Der Unterschied zwischen ``status`` und ``uebermittlung_status`` ist
beabsichtigt: ``status`` ist der fachliche Stand der Erklaerung (Entwurf,
eingereicht, zurueckgezogen), ``uebermittlung_status`` der Ausgang des
technischen Weges. Beide koennen auseinanderfallen — eine fachlich abgegebene
Erklaerung, deren Uebermittlung abgewiesen wurde, ist genau der Fall, den ein
Haus sehen muss.

Revision ID: eudr_uebermittlung_20261001
Revises: eudr_chargenkennzeichnung_20261001
"""

from __future__ import annotations

from alembic import op

revision = "eudr_uebermittlung_20261001"
down_revision = "eudr_chargenkennzeichnung_20261001"
branch_labels = None
depends_on = None

#: Ausgang des Weges hinaus.
UEBERMITTLUNG = (
    "NICHT_UEBERMITTELT",
    "UEBERMITTELT",
    "ABGEWIESEN",
    "ZURUECKGEZOGEN",
)

#: Ausgang des Weges herein.
PRUEFUNG = ("UNGEPRUEFT", "BESTAETIGT", "NICHT_GEFUNDEN", "ABGELAUFEN", "FEHLER")

#: Woher das Pruefergebnis kommt.
QUELLEN = ("EU_INFORMATIONSSYSTEM", "MANUELL")

#: Das EU-Informationssystem hat zwei Umgebungen. Die Kennung des
#: Webdienst-Mandanten unterscheidet sie (``eudr-repository`` gegen
#: ``eudr-test``), und nur die eine hat rechtliche Wirkung. Eine Uebermittlung
#: in den Annahmetest ist eine Probe, keine Abgabe — und darf im Stand des
#: Hauses nicht als erledigt zaehlen.
UMGEBUNGEN = ("PRODUKTION", "ANNAHMETEST")


def _in(spalte: str, werte: tuple[str, ...]) -> str:
    return f"{spalte} IN (" + ", ".join(f"'{w}'" for w in werte) + ")"


def upgrade() -> None:
    # ── hinaus: die eigene Erklaerung ───────────────────────────────────────
    op.execute(
        """
        ALTER TABLE domain_compliance.eudr_due_diligence
            ADD COLUMN IF NOT EXISTS uebermittlung_status VARCHAR(24)
                NOT NULL DEFAULT 'NICHT_UEBERMITTELT',
            ADD COLUMN IF NOT EXISTS eu_system_id        VARCHAR(64),
            ADD COLUMN IF NOT EXISTS uebermittelt_am     TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS uebermittlung_versuche INTEGER NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS uebermittlung_fehler TEXT,
            ADD COLUMN IF NOT EXISTS uebermittlung_dienst VARCHAR(128),
            ADD COLUMN IF NOT EXISTS uebermittlung_umgebung VARCHAR(16)
        """
    )
    op.execute(
        f"""
        ALTER TABLE domain_compliance.eudr_due_diligence
            ADD CONSTRAINT ck_eudr_uebermittlung_status
            CHECK ({_in('uebermittlung_status', UEBERMITTLUNG)})
        """
    )
    # Uebermittelt heisst: es gibt einen Zeitpunkt und eine Referenznummer.
    # Ohne beides ist es keine Uebermittlung, sondern ein Versuch.
    op.execute(
        """
        ALTER TABLE domain_compliance.eudr_due_diligence
            ADD CONSTRAINT ck_eudr_uebermittelt_belegt
            CHECK (
                uebermittlung_status <> 'UEBERMITTELT'
                OR (uebermittelt_am IS NOT NULL AND referenznummer IS NOT NULL)
            )
        """
    )
    op.execute(
        f"""
        ALTER TABLE domain_compliance.eudr_due_diligence
            ADD CONSTRAINT ck_eudr_uebermittlung_umgebung
            CHECK (
                uebermittlung_umgebung IS NULL
                OR {_in('uebermittlung_umgebung', UMGEBUNGEN)}
            )
        """
    )
    # Eine Uebermittlung ohne Umgebung ist nicht einzuordnen: Niemand koennte
    # sagen, ob sie rechtlich gilt oder eine Probe war.
    op.execute(
        """
        ALTER TABLE domain_compliance.eudr_due_diligence
            ADD CONSTRAINT ck_eudr_uebermittlung_umgebung_pflicht
            CHECK (
                uebermittlung_status <> 'UEBERMITTELT'
                OR uebermittlung_umgebung IS NOT NULL
            )
        """
    )
    # Ein Fehlschlag ohne Grund hilft niemandem beim naechsten Versuch.
    op.execute(
        """
        ALTER TABLE domain_compliance.eudr_due_diligence
            ADD CONSTRAINT ck_eudr_abgewiesen_begruendet
            CHECK (
                uebermittlung_status <> 'ABGEWIESEN'
                OR uebermittlung_fehler IS NOT NULL
            )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_eudr_eu_system_id "
        "ON domain_compliance.eudr_due_diligence (eu_system_id) "
        "WHERE eu_system_id IS NOT NULL"
    )
    # Gesucht wird "was ist fachlich abgegeben, aber technisch nicht draussen?".
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_eudr_uebermittlung_offen "
        "ON domain_compliance.eudr_due_diligence (tenant_id, uebermittlung_status) "
        "WHERE uebermittlung_status <> 'UEBERMITTELT'"
    )

    # ── herein: die zugekaufte Erklaerung ───────────────────────────────────
    op.execute(
        """
        ALTER TABLE domain_compliance.eudr_vorgelagerte_erklaerungen
            ADD COLUMN IF NOT EXISTS pruefung_status VARCHAR(24)
                NOT NULL DEFAULT 'UNGEPRUEFT',
            ADD COLUMN IF NOT EXISTS geprueft_am     TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS pruefung_quelle VARCHAR(32),
            ADD COLUMN IF NOT EXISTS pruefung_hinweis TEXT
        """
    )
    op.execute(
        f"""
        ALTER TABLE domain_compliance.eudr_vorgelagerte_erklaerungen
            ADD CONSTRAINT ck_eudr_vorgelagert_pruefstatus
            CHECK ({_in('pruefung_status', PRUEFUNG)})
        """
    )
    op.execute(
        f"""
        ALTER TABLE domain_compliance.eudr_vorgelagerte_erklaerungen
            ADD CONSTRAINT ck_eudr_vorgelagert_quelle
            CHECK (pruefung_quelle IS NULL OR {_in('pruefung_quelle', QUELLEN)})
        """
    )
    # Geprueft heisst: es gibt einen Zeitpunkt und eine Quelle.
    op.execute(
        """
        ALTER TABLE domain_compliance.eudr_vorgelagerte_erklaerungen
            ADD CONSTRAINT ck_eudr_vorgelagert_geprueft_belegt
            CHECK (
                pruefung_status = 'UNGEPRUEFT'
                OR (geprueft_am IS NOT NULL AND pruefung_quelle IS NOT NULL)
            )
        """
    )
    # Eine Bestaetigung aus dem EU-System setzt beide Nummern voraus: Abgefragt
    # wird eine Erklaerung ueber Referenz- **und** Verifizierungsnummer. Wer nur
    # die Referenznummer hat, kann sie nicht nachpruefen — und soll das nicht
    # als Bestaetigung eintragen koennen.
    op.execute(
        """
        ALTER TABLE domain_compliance.eudr_vorgelagerte_erklaerungen
            ADD CONSTRAINT ck_eudr_vorgelagert_bestaetigung
            CHECK (
                pruefung_status <> 'BESTAETIGT'
                OR pruefung_quelle <> 'EU_INFORMATIONSSYSTEM'
                OR verifizierungsnummer IS NOT NULL
            )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_eudr_vorgelagert_ungeprueft "
        "ON domain_compliance.eudr_vorgelagerte_erklaerungen (tenant_id, pruefung_status) "
        "WHERE pruefung_status <> 'BESTAETIGT'"
    )


def downgrade() -> None:
    for tabelle, bedingungen in (
        (
            "domain_compliance.eudr_due_diligence",
            (
                "ck_eudr_uebermittlung_status",
                "ck_eudr_uebermittelt_belegt",
                "ck_eudr_abgewiesen_begruendet",
                "ck_eudr_uebermittlung_umgebung",
                "ck_eudr_uebermittlung_umgebung_pflicht",
            ),
        ),
        (
            "domain_compliance.eudr_vorgelagerte_erklaerungen",
            (
                "ck_eudr_vorgelagert_pruefstatus",
                "ck_eudr_vorgelagert_quelle",
                "ck_eudr_vorgelagert_geprueft_belegt",
                "ck_eudr_vorgelagert_bestaetigung",
            ),
        ),
    ):
        for bedingung in bedingungen:
            op.execute(f"ALTER TABLE {tabelle} DROP CONSTRAINT IF EXISTS {bedingung}")

    op.execute("DROP INDEX IF EXISTS domain_compliance.ux_eudr_eu_system_id")
    op.execute("DROP INDEX IF EXISTS domain_compliance.ix_eudr_uebermittlung_offen")
    op.execute("DROP INDEX IF EXISTS domain_compliance.ix_eudr_vorgelagert_ungeprueft")

    # Die Spalten bleiben: Sie tragen, ob ein Nachweis uebermittelt und ein
    # Zukauf geprueft wurde. Das zurueckzunehmen hiesse, den Nachweis zu
    # verlieren, nicht eine Struktur.
