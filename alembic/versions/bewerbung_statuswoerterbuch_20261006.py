"""Die Bewerbungspipeline bekommt ein Woerterbuch — in der Datenbank.

`domain_hr.applications.status` war freier Text, und `APPLICATION_STAGES` stand
als Python-`set` ohne Uebergaenge im Weg. Beides zusammen heisst: Eine
**abgelehnte** Bewerbung liess sich auf `EINGESTELLT` setzen, eine eingestellte
wieder auf `EINGANG`, und ein Importweg konnte jedes Wort schreiben.

Dass eine Ablehnung rueckgaengig zu machen ist, ist kein Komfort, sondern ein
fehlender Nachweis: Niemand kann spaeter sagen, ob die Ablehnung je galt. Und eine
Ablehnung ohne Grund laesst sich im Streitfall nicht verteidigen — die Beweislast
liegt nach § 22 AGG beim Arbeitgeber.

Der Bestand traegt nur `EINGANG` und `VORAUSWAHL`; die Pruefbedingung gilt also
ohne Datenarbeit. Gefunden wuerde das Gegenteil **vor** dem Umbau: Die Migration
bricht ab, statt die Lage zu ueberschreiben.

Revision ID: bewerbung_statuswoerterbuch_20261006
Revises: quittung_ohne_vorgang_20261006
Create Date: 2026-10-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "bewerbung_statuswoerterbuch_20261006"
down_revision = "quittung_ohne_vorgang_20261006"
branch_labels = None
depends_on = None

TABELLE = "domain_hr.applications"

#: Die Stufen der Pipeline. Deckungsgleich mit
#: ``bewerbung_service.STUFEN``.
STUFEN = (
    "EINGANG",
    "VORAUSWAHL",
    "ERSTGESPRAECH",
    "ENDGESPRAECH",
    "ANGEBOT",
    "EINGESTELLT",
    "ABGELEHNT",
)


def _liste(werte: tuple[str, ...]) -> str:
    return ", ".join(f"'{wert}'" for wert in werte)


def upgrade() -> None:
    verbindung = op.get_bind()

    # Ein Stand ausserhalb des Woerterbuchs ist ein Befund, keine Kleinigkeit:
    # Er wuerde beim Lesen als unbekannter Zustand auftauchen und jede
    # Uebergangspruefung aushebeln. Deshalb erst zaehlen, dann binden.
    fremd = verbindung.execute(
        sa.text(
            f"SELECT DISTINCT status FROM {TABELLE} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            f"WHERE status IS NULL OR status NOT IN ({_liste(STUFEN)})"
        )
    ).scalars().all()
    if fremd:
        raise RuntimeError(
            f"{TABELLE} fuehrt Staende ausserhalb des Woerterbuchs: {fremd!r}. "
            "Sie sind zuzuordnen, bevor die Pruefbedingung gilt — ein stilles "
            "Umschreiben wuerde verdecken, in welchem Stand eine Bewerbung war."
        )

    # Die Begruendung der Ablehnung. Getrennt von `notes`, weil `notes` ein
    # Verlaufsfeld ist, in das jeder Stufenwechsel schreibt — ein Grund, der
    # darin untergeht, ist kein Nachweis.
    verbindung.execute(
        sa.text(
            f"ALTER TABLE {TABELLE} "  # nosec B608  # reviewed-safe: Namen sind Code-Literale
            "ADD COLUMN IF NOT EXISTS ablehnungsgrund TEXT"
        )
    )
    verbindung.execute(
        sa.text(
            f"ALTER TABLE {TABELLE} "  # nosec B608  # reviewed-safe: Namen sind Code-Literale
            "ADD COLUMN IF NOT EXISTS entschieden_am TIMESTAMPTZ"
        )
    )
    verbindung.execute(
        sa.text(
            f"ALTER TABLE {TABELLE} "  # nosec B608  # reviewed-safe: Namen sind Code-Literale
            "ADD COLUMN IF NOT EXISTS entschieden_durch VARCHAR(120)"
        )
    )

    for name, bedingung in (
        ("ck_bewerbung_status", f"status IN ({_liste(STUFEN)})"),
        # Eine Ablehnung ohne Grund laesst sich nicht verteidigen (§ 22 AGG).
        (
            "ck_bewerbung_ablehnung_begruendet",
            "status <> 'ABGELEHNT' OR (ablehnungsgrund IS NOT NULL "
            "AND LENGTH(TRIM(ablehnungsgrund)) > 0)",
        ),
        # Ein endgueltiger Stand ohne Zeitpunkt ist kein Nachweis.
        (
            "ck_bewerbung_entscheidung_datiert",
            "status NOT IN ('EINGESTELLT', 'ABGELEHNT') OR entschieden_am IS NOT NULL",
        ),
        ("ck_bewerbung_name_gefuellt", "LENGTH(TRIM(applicant_name)) > 0"),
    ):
        vorhanden = verbindung.execute(
            sa.text("SELECT 1 FROM pg_constraint WHERE conname = :n"), {"n": name}
        ).scalar()
        if not vorhanden:
            verbindung.execute(
                sa.text(
                    f"ALTER TABLE {TABELLE} ADD CONSTRAINT {name} CHECK ({bedingung})"  # nosec B608  # reviewed-safe: Name und Bedingung sind Code-Literale
                )
            )

    # Die Liste wird je Mandant und Stand gelesen.
    verbindung.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS ix_bewerbung_mandant_status "
            f"ON {TABELLE} (tenant_id, status, applied_at DESC)"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        )
    )


def downgrade() -> None:
    verbindung = op.get_bind()
    verbindung.execute(sa.text("DROP INDEX IF EXISTS domain_hr.ix_bewerbung_mandant_status"))
    for name in (
        "ck_bewerbung_status",
        "ck_bewerbung_ablehnung_begruendet",
        "ck_bewerbung_entscheidung_datiert",
        "ck_bewerbung_name_gefuellt",
    ):
        verbindung.execute(
            sa.text(f"ALTER TABLE {TABELLE} DROP CONSTRAINT IF EXISTS {name}")  # nosec B608  # reviewed-safe: Name ist ein Code-Literal
        )
    # Die Begruendung einer Ablehnung wird nicht per Downgrade geloescht: Sie ist
    # der Nachweis, auf den es im Streitfall ankommt.
    belegt = verbindung.execute(
        sa.text(
            f"SELECT COUNT(*) FROM {TABELLE} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE ablehnungsgrund IS NOT NULL OR entschieden_am IS NOT NULL"
        )
    ).scalar()
    if belegt:
        raise RuntimeError(
            f"{belegt} Bewerbungen fuehren eine Entscheidung (Grund oder Zeitpunkt). "
            "Diese Spalten sind der Nachweis einer Ablehnung und werden nicht per "
            "Downgrade geleert."
        )
    for spalte in ("ablehnungsgrund", "entschieden_am", "entschieden_durch"):
        verbindung.execute(
            sa.text(f"ALTER TABLE {TABELLE} DROP COLUMN IF EXISTS {spalte}")  # nosec B608  # reviewed-safe: Name ist ein Code-Literal
        )
