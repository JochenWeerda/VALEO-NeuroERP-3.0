"""Ein Wiegeergebnis, eine Tabelle — und das Netto stimmt.

Der Doppelwiegungsweg schrieb `domain_agrar.wiegungen`, eine Tabelle, die keine
Migration anlegt und die in keiner Datenbank existiert. Daneben stehen drei
weitere Wiegetabellen. Diese Migration legt die fehlende **nicht** an: Das
kanonische Rueckgrat ist `domain_inventory.weighing_tickets` — die Tabelle, auf
die die Rueckverfolgbarkeit (`supply_chain_trace_service`) zeigt und die alle
Felder der Doppelwiegung schon hat. Sie bekommt die Spalten, die der Waage
eigen sind, und vier Pruefbedingungen.

**Warum `ck_wiegung_netto_stimmt`.** Der Weg rechnete
``netto = abs(wiegung1 - wiegung2)``. Der Absolutbetrag verdeckt den
Vorzeichenfehler: Eine Tara schwerer als das Brutto ist ein Messfehler oder eine
Verwechslung der Eingaben — und wurde zu einem plausiblen positiven Netto, auf
dem die Rechnung aufbaut. Das Nettogewicht ist die abgerechnete Menge; es muss
der Messung entsprechen, und das haelt die Datenbank nach.

**Warum `handwiegung` eine Spalte ist.** Nach MessEG ist eine von Hand
eingetragene Masse keine geeichte Messung. Der Beleg muss sagen, was er ist. In
einem JSONB-Klumpen ist das nicht auswertbar — und genau dort stand es.

Revision ID: wiegung_kanonisch_20261005
Revises: genossenschaft_mitgliederregister_20261005
Create Date: 2026-10-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "wiegung_kanonisch_20261005"
down_revision = "genossenschaft_mitgliederregister_20261005"
branch_labels = None
depends_on = None

TABELLE = "domain_inventory.weighing_tickets"

#: Richtungen eines Wiegevorgangs. Deckungsgleich mit dem Bestand (`in`, `out`)
#: und mit der Abbildung aus dem Zielscheintyp (EL -> in, VL -> out).
RICHTUNGEN = ("in", "out")

#: Spalten, die der Waage eigen sind und bisher im JSONB-Klumpen lagen.
SPALTEN = (
    ("gosse", "SMALLINT"),
    ("muster_nr", "VARCHAR(40)"),
    ("handwiegung", "BOOLEAN NOT NULL DEFAULT FALSE"),
    ("ident_nr", "VARCHAR(60)"),
    ("disposition_nr", "VARCHAR(40)"),
    ("charge_nr", "VARCHAR(60)"),
)

#: Die Pruefbedingungen. Vor dem Anlegen wird geprueft, ob der Bestand sie
#: traegt — eine Bedingung, die an echten Daten scheitert, wird nicht
#: stillschweigend uebersprungen, sondern gemeldet.
BEDINGUNGEN = (
    (
        "ck_wiegung_netto_stimmt",
        "gross_weight IS NULL OR tare_weight IS NULL OR net_weight IS NULL "
        "OR ABS(net_weight - (gross_weight - tare_weight)) < 0.001",
        "Das Nettogewicht ist die abgerechnete Menge und muss der Messung entsprechen.",
    ),
    (
        "ck_wiegung_tara_unter_brutto",
        "gross_weight IS NULL OR tare_weight IS NULL OR tare_weight < gross_weight",
        "Eine Tara schwerer als das Brutto ist ein Messfehler, kein Nettogewicht.",
    ),
    (
        "ck_wiegung_gewichte_nicht_negativ",
        "COALESCE(gross_weight, 0) >= 0 AND COALESCE(tare_weight, 0) >= 0 "
        "AND COALESCE(net_weight, 0) >= 0",
        "Eine Masse ist nicht negativ.",
    ),
    (
        "ck_wiegung_richtung",
        "direction IS NULL OR direction IN ('in', 'out')",
        "Eine Richtung, die der Rueckverfolgbarkeit unbekannt ist, laesst die "
        "Wiegung aus der Kette fallen.",
    ),
)


def upgrade() -> None:
    verbindung = op.get_bind()

    for name, typ in SPALTEN:
        verbindung.execute(
            sa.text(f"ALTER TABLE {TABELLE} ADD COLUMN IF NOT EXISTS {name} {typ}")  # nosec B608  # reviewed-safe: Namen und Typen sind Code-Literale
        )

    for name, bedingung, warum in BEDINGUNGEN:
        verstoesse = verbindung.execute(
            sa.text(f"SELECT COUNT(*) FROM {TABELLE} WHERE NOT ({bedingung})")  # nosec B608  # reviewed-safe: Bedingung ist ein Code-Literal
        ).scalar()
        if verstoesse:
            raise RuntimeError(
                f"{verstoesse} Wiegescheine verletzen {name}. {warum} "
                "Der Bestand ist zu klaeren, bevor die Bedingung gilt — sie zu "
                "ueberspringen wuerde den Fehler dauerhaft verdecken."
            )
        vorhanden = verbindung.execute(
            sa.text("SELECT 1 FROM pg_constraint WHERE conname = :n"), {"n": name}
        ).scalar()
        if not vorhanden:
            verbindung.execute(
                sa.text(f"ALTER TABLE {TABELLE} ADD CONSTRAINT {name} CHECK ({bedingung})")  # nosec B608  # reviewed-safe: Name und Bedingung sind Code-Literale
            )

    # Der Weg sucht die Wiegungen eines Hauses nach Kennzeichen und Zeitpunkt.
    verbindung.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS ix_wiegung_mandant_kennzeichen "
            f"ON {TABELLE} (tenant_id, vehicle_plate, weighing_date DESC)"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        )
    )


def downgrade() -> None:
    verbindung = op.get_bind()
    verbindung.execute(sa.text("DROP INDEX IF EXISTS domain_inventory.ix_wiegung_mandant_kennzeichen"))
    for name, _, _ in BEDINGUNGEN:
        verbindung.execute(sa.text(f"ALTER TABLE {TABELLE} DROP CONSTRAINT IF EXISTS {name}"))  # nosec B608  # reviewed-safe: Name ist ein Code-Literal
    # Die Spalten werden nur zurueckgebaut, wenn nichts darin steht: Eine
    # Handwiegung oder eine Gosse ist Teil des Belegs.
    belegt = verbindung.execute(
        sa.text(
            f"SELECT COUNT(*) FROM {TABELLE} WHERE gosse IS NOT NULL "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "OR muster_nr IS NOT NULL OR handwiegung OR ident_nr IS NOT NULL "
            "OR disposition_nr IS NOT NULL OR charge_nr IS NOT NULL"
        )
    ).scalar()
    if belegt:
        raise RuntimeError(
            f"{belegt} Wiegescheine fuehren Waagenangaben (Gosse, Muster, "
            "Handwiegung, Ident, Disposition, Charge). Diese Spalten sind Teil "
            "des Belegs und werden nicht per Downgrade geleert."
        )
    for name, _ in SPALTEN:
        verbindung.execute(sa.text(f"ALTER TABLE {TABELLE} DROP COLUMN IF EXISTS {name}"))  # nosec B608  # reviewed-safe: Name ist ein Code-Literal
