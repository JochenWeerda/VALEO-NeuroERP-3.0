"""Belegartenregister fuer das Bestandshauptbuch (DOM-INV-006).

Revision ID: inv_movement_type_register_20260825
Revises: l3_runtime_hardening_20260822

Warum ein Register und keine Vereinheitlichung der bestehenden Werte:

HGB 239 Abs. 3 und die GoBD verlangen, dass der urspruengliche Inhalt einer
Buchung feststellbar bleibt. Ein UPDATE, das historische ``movement_type``-Werte
auf ein einheitliches Vokabular umschreibt, waere genau das, was diese Regel
verbietet - es wuerde die Vereinheitlichung erkaufen, indem es die Buchungen
faelscht. Stattdessen bekommt jede tatsaechlich verwendete Belegart einen
registrierten Eintrag mit Richtung und Begruendung, und ein Trigger sorgt dafuer,
dass keine unregistrierte Belegart mehr hinzukommt.

Diese Migration aendert daher keine einzige Zeile in
``inventory_stock_movements``.

Die Pruefung ist case-insensitiv, weil die Bestandsdaten dieselbe Belegart in
verschiedenen Schreibweisen fuehren (``EINLAGERUNG`` neben ``wareneingang``).
Auch das ist Bestand und wird nicht umgeschrieben.
"""

from alembic import op

revision = "inv_movement_type_register_20260825"
down_revision = "l3_runtime_hardening_20260822"
branch_labels = None
depends_on = None


# Muss deckungsgleich mit app.services.inventory_movement_direction sein.
# tests/test_inventory_movement_register.py prueft das gegen die Datenbank.
REGISTER = [
    ("abgang", -1, True, "Abgang aus den Korrekturdiensten (Storno einer Zugangsbuchung)."),
    ("adjustment", 1, True, "Bestandskorrektur, Menge vorzeichenbehaftet."),
    ("adjustment_in", 1, True, "Positive Bestandskorrektur."),
    ("adjustment_out", -1, True, "Negative Bestandskorrektur."),
    ("einlagerung", 1, True, "Zugang aus dem Wareneingang zum Lieferschein."),
    ("in", 1, True, "Allgemeiner Zugang aus den Artikel- und Compat-Pfaden."),
    (
        "inventory_count",
        0,
        False,
        "Altbestand: absoluter Zaehlwert der mobilen Inventur. Kein Delta und "
        "damit nicht bestandswirksam. Seit DOM-INV-006 bucht die mobile Zaehlung "
        "die Differenz; diese Belegart bleibt nur fuer Altzeilen im Register.",
    ),
    (
        "inventur",
        1,
        True,
        "Inventurbuchung aus der generischen Lagerbuchung, Menge vorzeichenbehaftet.",
    ),
    ("opening_balance", 1, True, "Freigegebener Bestandsvortrag; eroeffnet den Bestand."),
    ("out", -1, True, "Allgemeiner Abgang aus den Artikel- und Compat-Pfaden."),
    ("pick_out", -1, True, "Entnahme durch Kommissionierung."),
    ("reservation", 0, False, "Reservierung; bindet Ware, bewegt sie nicht."),
    ("retoure", 1, True, "Warenrueckgabe aus der Kasse."),
    ("return", 1, True, "Ruecklauf aus den Artikelpfaden."),
    (
        "umbuchung",
        1,
        True,
        "Umlagerung ohne getrennte Zu-/Abgangsseite, Menge vorzeichenbehaftet.",
    ),
    ("umbuchung_ausgang", -1, True, "Abgangsseite einer Umlagerung zwischen Lagerorten."),
    ("umbuchung_eingang", 1, True, "Zugangsseite einer Umlagerung zwischen Lagerorten."),
    (
        "wareneingang",
        1,
        True,
        "Zugang aus der generischen Lagerbuchung, Menge vorzeichenbehaftet.",
    ),
    ("warenausgang", -1, True, "Abgang aus der generischen Lagerbuchung."),
    ("zugang", 1, True, "Zugang aus den Korrekturdiensten (Storno einer Abgangsbuchung)."),
]


def _escape(value: str) -> str:
    return value.replace("'", "''")


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_inventory.inventory_movement_types (
            movement_type  VARCHAR(64) PRIMARY KEY,
            direction      SMALLINT    NOT NULL,
            is_delta       BOOLEAN     NOT NULL,
            note           TEXT        NOT NULL,
            created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT inventory_movement_types_direction_check
                CHECK (direction IN (-1, 0, 1)),
            CONSTRAINT inventory_movement_types_delta_check
                CHECK ((direction = 0) = (is_delta = false)),
            -- inventory_stock_movements.movement_type ist VARCHAR(20). Ohne
            -- diese Schranke koennte das Register eine Belegart fuehren, die
            -- sich nie buchen laesst.
            CONSTRAINT inventory_movement_types_laenge_check
                CHECK (length(movement_type) <= 20)
        );
        COMMENT ON TABLE domain_inventory.inventory_movement_types IS
            'Belegartenregister des Bestandshauptbuchs (DOM-INV-006). '
            'Richtung: 1 = bestandserhoehend, -1 = bestandsmindernd, '
            '0 = dokumentierend ohne Bestandswirkung.';
        """
    )

    werte = ", ".join(
        "('{}', {}, {}, '{}')".format(name, direction, str(is_delta).lower(), _escape(note))
        for name, direction, is_delta, note in REGISTER
    )
    op.execute(
        f"""
        INSERT INTO domain_inventory.inventory_movement_types
            (movement_type, direction, is_delta, note)
        VALUES {werte}
        ON CONFLICT (movement_type) DO UPDATE
            SET direction = EXCLUDED.direction,
                is_delta  = EXCLUDED.is_delta,
                note      = EXCLUDED.note;
        """  # nosec B608 - Werte aus der Modulkonstante REGISTER, keine Eingaben
    )

    # Schreibsperre. Bewusst als Trigger und nicht als Fremdschluessel: die
    # Bestandsdaten fuehren dieselbe Belegart in mehreren Schreibweisen, ein
    # Fremdschluessel waere case-sensitiv und wuerde entweder Altzeilen
    # blockieren oder das Register mit Schreibvarianten aufblaehen.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION domain_inventory.pruefe_belegart()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF NEW.movement_type IS NULL THEN
                RAISE EXCEPTION
                    'Bestandsbuchung ohne Belegart ist nicht zulaessig'
                    USING ERRCODE = 'check_violation';
            END IF;
            IF NOT EXISTS (
                SELECT 1 FROM domain_inventory.inventory_movement_types
                 WHERE movement_type = lower(NEW.movement_type)
            ) THEN
                RAISE EXCEPTION
                    'Unbekannte Belegart % - erst in domain_inventory.inventory_movement_types registrieren',
                    NEW.movement_type
                    USING ERRCODE = 'foreign_key_violation';
            END IF;
            RETURN NEW;
        END;
        $$;

        DROP TRIGGER IF EXISTS trg_pruefe_belegart
            ON domain_inventory.inventory_stock_movements;
        CREATE TRIGGER trg_pruefe_belegart
            BEFORE INSERT OR UPDATE OF movement_type
            ON domain_inventory.inventory_stock_movements
            FOR EACH ROW
            EXECUTE FUNCTION domain_inventory.pruefe_belegart();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_pruefe_belegart
            ON domain_inventory.inventory_stock_movements;
        DROP FUNCTION IF EXISTS domain_inventory.pruefe_belegart();
        DROP TABLE IF EXISTS domain_inventory.inventory_movement_types;
        """
    )
