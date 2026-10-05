"""Eine Charge sagt, welche Sorgfaltserklaerung sie deckt.

Art. 4 der Verordnung (EU) 2023/1115 verbietet das Inverkehrbringen, solange
keine Sorgfaltserklaerung abgegeben ist. Dafuer muss eine Charge sagen koennen,
**welche** Erklaerung sie deckt — sonst ist die Erklaerung ein Dokument ohne
Ware und die Ware eine ohne Nachweis.

**Eine neue Spalte, und nur eine:** ``inventory_lots.eudr_relevant``. Ob eine
Charge einen relevanten Rohstoff traegt (Anhang I), ist eine Eigenschaft der
Ware und aus nichts anderem ableitbar.

**Die Verbindung ist keine Spalte, sondern eine Tabelle.** Im Landhandel wird
verschnitten: Eine Silocharge kann aus mehreren Partien stammen und damit von
**mehreren** Erklaerungen gedeckt sein. ``lot_eudr_erklaerungen`` traegt deshalb
je Charge und Erklaerung die Menge, fuer die die Erklaerung gilt.

**Was bewusst nicht entsteht:**

* **Keine Spalte fuer den Nachweisstand.** "Nachgewiesen" ergibt sich aus der
  gedeckten Menge und wird abgeleitet. Eine zweite, gespeicherte Wahrheit
  darueber waere genau das Muster, das diese Welle abbaut.
* **Keine Kopie der Referenznummer.** Sie steht an der Erklaerung; eine Kopie an
  der Charge koennte von ihr abweichen, und dann waere nicht entscheidbar,
  welche gilt.

``ON DELETE RESTRICT`` auf der Erklaerung: Eine Erklaerung, auf die sich eine
Charge stuetzt, darf nicht verschwinden. Das ist der Nachweis, mit dem die Ware
in Verkehr gebracht wurde.

Revision ID: eudr_chargenkennzeichnung_20261001
Revises: eudr_sorgfaltserklaerung_20261001
"""

from __future__ import annotations

from alembic import op

revision = "eudr_chargenkennzeichnung_20261001"
down_revision = "eudr_sorgfaltserklaerung_20261001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_inventory.inventory_lots
            ADD COLUMN IF NOT EXISTS eudr_relevant BOOLEAN NOT NULL DEFAULT FALSE
        """
    )
    # Gesucht wird "welche relevanten Chargen meines Hauses haben noch keinen
    # Nachweis?" — die Liste der Chargen, die nicht in Verkehr dürfen.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_inventory_lots_eudr_relevant "
        "ON domain_inventory.inventory_lots (tenant_id, eudr_relevant) "
        "WHERE eudr_relevant"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_inventory.lot_eudr_erklaerungen (
            id            VARCHAR(64)  PRIMARY KEY,
            tenant_id     VARCHAR(80)  NOT NULL,
            lot_id        VARCHAR(64)  NOT NULL
                REFERENCES domain_inventory.inventory_lots (id) ON DELETE CASCADE,
            erklaerung_id VARCHAR(64)  NOT NULL
                REFERENCES domain_compliance.eudr_due_diligence (id) ON DELETE RESTRICT,
            menge_kg      NUMERIC(16, 3) NOT NULL,
            verknuepft_am TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            verknuepft_durch VARCHAR(255),

            CONSTRAINT ck_lot_eudr_menge CHECK (menge_kg > 0)
        )
        """
    )
    # Eine Erklaerung deckt eine Charge einmal. Zwei Zeilen fuer dasselbe Paar
    # waeren zwei Aussagen ueber dieselbe Menge.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_lot_eudr_paar "
        "ON domain_inventory.lot_eudr_erklaerungen (lot_id, erklaerung_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lot_eudr_erklaerung "
        "ON domain_inventory.lot_eudr_erklaerungen (erklaerung_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lot_eudr_tenant_lot "
        "ON domain_inventory.lot_eudr_erklaerungen (tenant_id, lot_id)"
    )


def downgrade() -> None:
    # Die Verbindungstabelle traegt den Bezug zwischen Ware und Nachweis.
    # Zurueckgenommen wird sie nur, wenn sie leer ist — sonst bricht die
    # Migration ab, statt den Nachweis stillschweigend zu loesen.
    op.execute(
        """
        DO $$
        DECLARE bestand bigint;
        BEGIN
            IF to_regclass('domain_inventory.lot_eudr_erklaerungen') IS NULL THEN
                RETURN;
            END IF;
            SELECT count(*) INTO bestand FROM domain_inventory.lot_eudr_erklaerungen;
            IF bestand > 0 THEN
                RAISE EXCEPTION
                    'lot_eudr_erklaerungen traegt % Zeilen. Ruecknahme abgebrochen: '
                    'Das ist der Bezug zwischen Charge und Sorgfaltserklaerung '
                    '(Art. 4 Verordnung (EU) 2023/1115).', bestand;
            END IF;
        END $$;
        """
    )
    op.execute("DROP TABLE IF EXISTS domain_inventory.lot_eudr_erklaerungen")
    op.execute("DROP INDEX IF EXISTS domain_inventory.ix_inventory_lots_eudr_relevant")
    op.execute(
        "ALTER TABLE domain_inventory.inventory_lots DROP COLUMN IF EXISTS eudr_relevant"
    )
