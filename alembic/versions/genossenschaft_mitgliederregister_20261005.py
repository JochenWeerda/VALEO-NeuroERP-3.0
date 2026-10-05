"""Das Mitgliederregister einer eingetragenen Genossenschaft.

`domain_shared.genossenschaft_mitglieder` und
`genossenschaft_anteilsbewegungen` existierten in keiner Datenbank. Der
Endpunkt fing jeden Lesefehler: Die Mitgliederliste antwortete ``[]``, die
Kapitaluebersicht 0 Mitglieder und **0,00 EUR**. Fuer eine eG ist beides nie
wahr — § 30 GenG verpflichtet zur Mitgliederliste, und das Geschaeftsguthaben
der Mitglieder ist eine Bilanzposition (§ 337 HGB).

Zwei Entscheidungen stecken im Schema:

**Der Anteilsbestand ist keine Spalte.** Er wird aus den Bewegungen abgeleitet.
Eine fortgeschriebene Zahl neben dem Bewegungsjournal waere eine zweite
Wahrheit, die von der ersten abweichen kann — und abweichen wuerde, sobald eine
Bewegung fehlschlaegt oder korrigiert wird. GoBD Rz. 107 ff. verlangt, dass eine
Aenderung nachvollziehbar bleibt; eine Zahl ohne Bewegung dahinter ist das
Gegenteil.

**Eine Uebertragung hat zwei Seiten.** Der alte Code kannte einen Typ
``TRANSFER`` mit Vorzeichen ``+1`` — der haette Anteile aus nichts geschaffen.
Hier stehen zwei gerichtete Typen mit einer Gegenseite als Pflichtfeld.

Revision ID: genossenschaft_mitgliederregister_20261005
Revises: zusammenfuehrung_20261005
Create Date: 2026-10-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "genossenschaft_mitgliederregister_20261005"
down_revision = "zusammenfuehrung_20261005"
branch_labels = None
depends_on = None

#: Mitgliedsstaende. ``AUSGETRETEN`` ist kein Loeschen: § 30 Abs. 2 GenG will den
#: Austritt in der Liste sehen, und die Aufbewahrung laeuft weiter.
STAENDE = ("AKTIV", "RUHEND", "AUSGETRETEN")

#: Bewegungen, die Anteile **hinzufuegen**.
ZUGANG = ("ZEICHNUNG", "ERHOEHUNG", "UEBERTRAGUNG_AN")

#: Bewegungen, die Anteile **abziehen**.
ABGANG = ("TEILRUECKZAHLUNG", "VOLLRUECKZAHLUNG", "UEBERTRAGUNG_AB")

BEWEGUNGSTYPEN = ZUGANG + ABGANG


def _liste(werte: tuple[str, ...]) -> str:
    return ", ".join(f"'{wert}'" for wert in werte)


def _kontonummern_je_mandant(verbindung) -> None:
    """Die Kontonummer ist je Mandant eindeutig, nicht systemweit.

    ``001_initial_schema`` legte ``UniqueConstraint('account_number')`` ohne
    Mandanten an — systemweit. Damit kann genau **eine** Genossenschaft im ganzen
    System das Konto 1200 besitzen; jede zweite kann ihren Kontenrahmen nicht
    anlegen. Dass das nicht gemeint war, steht im Code daneben:
    ``FinanceTransactionService._bookable_account`` sucht ``WHERE tenant_id = :t
    AND account_number = :n``, also je Mandant.

    Ohne diese Korrektur koennte die Hauptbuchbuchung einer Anteilszeichnung fuer
    keinen echten Mandanten gelingen — und eine Buchung, die nie gelingt, waere
    hier besonders bitter, weil sie das gezeichnete Kapital traegt.

    Geprueft vor dem Umbau: Gibt es eine Nummer, die zwei Mandanten fuehren,
    bricht der Umbau ab. Dann ist die Lage zu klaeren und nicht zu ueberschreiben.
    """
    doppelt = verbindung.execute(
        sa.text(
            "SELECT account_number, COUNT(*) FROM domain_erp.chart_of_accounts "
            "GROUP BY tenant_id, account_number HAVING COUNT(*) > 1 LIMIT 1"
        )
    ).first()
    if doppelt:
        raise RuntimeError(
            f"Kontonummer {doppelt[0]} kommt je Mandant mehrfach vor. "
            "Der Umbau auf eine mandantenweite Eindeutigkeit wuerde die Lage "
            "verdecken — erst klaeren."
        )
    verbindung.execute(
        sa.text(
            "ALTER TABLE domain_erp.chart_of_accounts "
            "DROP CONSTRAINT IF EXISTS chart_of_accounts_account_number_key"
        )
    )
    vorhanden = verbindung.execute(
        sa.text("SELECT 1 FROM pg_constraint WHERE conname = 'uq_coa_mandant_kontonummer'")
    ).scalar()
    if not vorhanden:
        verbindung.execute(
            sa.text(
                "ALTER TABLE domain_erp.chart_of_accounts "
                "ADD CONSTRAINT uq_coa_mandant_kontonummer UNIQUE (tenant_id, account_number)"
            )
        )


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    _kontonummern_je_mandant(op.get_bind())

    op.create_table(
        "genossenschaft_mitglieder",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("mitglieds_nr", sa.String(40), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("adresse", sa.Text(), nullable=False),
        sa.Column("eintrittsdatum", sa.Date(), nullable=False),
        # § 30 Abs. 2 GenG nennt den Austritt als Inhalt der Liste. Ohne eigene
        # Spalte waere der Zeitpunkt nur noch im Status zu erraten.
        sa.Column("austrittsdatum", sa.Date(), nullable=True),
        sa.Column("anteilswert_eur", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="AKTIV"),
        sa.Column("iban", sa.String(34), nullable=False),
        sa.Column("bank_name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.CheckConstraint(f"status IN ({_liste(STAENDE)})", name="ck_geno_mitglied_status"),
        sa.CheckConstraint("anteilswert_eur > 0", name="ck_geno_anteilswert_positiv"),
        # Ein Austritt ohne Datum ist kein Austritt, ein Datum ohne Austritt ein
        # Widerspruch. Beides zusammen oder keins von beidem.
        sa.CheckConstraint(
            "(status = 'AUSGETRETEN') = (austrittsdatum IS NOT NULL)",
            name="ck_geno_austritt_datiert",
        ),
        sa.CheckConstraint(
            "austrittsdatum IS NULL OR austrittsdatum >= eintrittsdatum",
            name="ck_geno_austritt_nach_eintritt",
        ),
        schema="domain_shared",
    )

    # Die Mitgliedsnummer ist der fachliche Schluessel der Liste. Je Mandant
    # eindeutig — eine Doppelnummer macht die Liste nach § 30 GenG unbrauchbar,
    # und die Datenbank soll das laut sagen und nicht die Anwendung hoffen.
    op.create_index(
        "ux_geno_mitglied_nr",
        "genossenschaft_mitglieder",
        ["tenant_id", "mitglieds_nr"],
        unique=True,
        schema="domain_shared",
    )
    op.create_index(
        "ix_geno_mitglied_mandant",
        "genossenschaft_mitglieder",
        ["tenant_id", "status", "mitglieds_nr"],
        schema="domain_shared",
    )

    op.create_table(
        "genossenschaft_anteilsbewegungen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("mitglieds_id", sa.String(36), nullable=False),
        sa.Column("bewegungstyp", sa.String(30), nullable=False),
        sa.Column("anzahl_anteile", sa.Integer(), nullable=False),
        sa.Column("wert_eur", sa.Numeric(14, 2), nullable=False),
        sa.Column("datum", sa.Date(), nullable=False),
        sa.Column("bemerkung", sa.Text(), nullable=True),
        # Die Gegenseite einer Uebertragung. Ohne sie waere nicht nachvollziehbar,
        # wohin die Anteile gegangen sind.
        sa.Column("gegen_mitglieds_id", sa.String(36), nullable=True),
        # Belegbezug zur Hauptbuchbuchung. Eine Anteilszeichnung ohne Buchung
        # liesse das gezeichnete Kapital von der Mitgliederliste abweichen.
        sa.Column("journal_entry_id", sa.String(36), nullable=True),
        sa.Column("erfasst_durch", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        # ON DELETE RESTRICT: Ein Mitglied mit Bewegungen darf nicht verschwinden.
        # Die Bewegungen sind der Nachweis des Geschaeftsguthabens.
        sa.ForeignKeyConstraint(
            ["mitglieds_id"], ["domain_shared.genossenschaft_mitglieder.id"],
            name="fk_geno_bewegung_mitglied", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["gegen_mitglieds_id"], ["domain_shared.genossenschaft_mitglieder.id"],
            name="fk_geno_bewegung_gegenseite", ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            f"bewegungstyp IN ({_liste(BEWEGUNGSTYPEN)})", name="ck_geno_bewegungstyp"
        ),
        # Die Anzahl ist immer positiv; die Richtung steckt im Typ. Sonst gaebe es
        # zwei Wege, einen Abgang auszudruecken, und nur einer wuerde geprueft.
        sa.CheckConstraint("anzahl_anteile > 0", name="ck_geno_anzahl_positiv"),
        sa.CheckConstraint("wert_eur > 0", name="ck_geno_wert_positiv"),
        sa.CheckConstraint(
            "(bewegungstyp IN ('UEBERTRAGUNG_AB', 'UEBERTRAGUNG_AN')) "
            "= (gegen_mitglieds_id IS NOT NULL)",
            name="ck_geno_uebertragung_gegenseite",
        ),
        sa.CheckConstraint(
            "gegen_mitglieds_id IS NULL OR gegen_mitglieds_id <> mitglieds_id",
            name="ck_geno_uebertragung_nicht_an_sich",
        ),
        schema="domain_shared",
    )

    op.create_index(
        "ix_geno_bewegung_mitglied",
        "genossenschaft_anteilsbewegungen",
        ["tenant_id", "mitglieds_id", "datum"],
        schema="domain_shared",
    )


def downgrade() -> None:
    # Ein Mitgliederregister wird nicht aus Versehen zurueckgebaut: Die
    # Aufbewahrung laeuft nach § 30 GenG ueber den Austritt hinaus.
    verbindung = op.get_bind()
    for tabelle in ("genossenschaft_anteilsbewegungen", "genossenschaft_mitglieder"):
        anzahl = verbindung.execute(
            sa.text(f"SELECT COUNT(*) FROM domain_shared.{tabelle}")  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        ).scalar()
        if anzahl:
            raise RuntimeError(
                f"domain_shared.{tabelle} fuehrt {anzahl} Zeilen. Ein "
                "Mitgliederregister wird nicht per Downgrade geleert — § 30 GenG."
            )
    op.drop_index("ix_geno_bewegung_mitglied", table_name="genossenschaft_anteilsbewegungen",
                  schema="domain_shared")
    op.drop_table("genossenschaft_anteilsbewegungen", schema="domain_shared")
    op.drop_index("ix_geno_mitglied_mandant", table_name="genossenschaft_mitglieder",
                  schema="domain_shared")
    op.drop_index("ux_geno_mitglied_nr", table_name="genossenschaft_mitglieder",
                  schema="domain_shared")
    op.drop_table("genossenschaft_mitglieder", schema="domain_shared")
    # Die systemweite Eindeutigkeit wird nicht wiederhergestellt: Sie war ein
    # Fehler, und sie waere nach dem Anlegen zweiter Kontenrahmen nicht mehr
    # erfuellbar. Der Rueckbau wuerde an echten Daten scheitern.
    verbindung.execute(
        sa.text(
            "ALTER TABLE domain_erp.chart_of_accounts "
            "DROP CONSTRAINT IF EXISTS uq_coa_mandant_kontonummer"
        )
    )
