"""Die Statusbedingung des Lieferscheins kennt die Zustaende, die es gibt.

``ck_delivery_notes_status`` stammt aus der Tabellenanlage
(``sales_delivery_notes_branches_audit_20260216``) und erlaubt fuenf Werte:
draft, printed, delivered, invoiced, cancelled.

Der Code schreibt aber neun. Vier davon kennt die Bedingung nicht:

- ``posted``    — ``POST /sales/delivery-notes/{id}/post`` (Buchen)
- ``shipped``   — ``POST /sales/delivery-notes/{id}/ship`` (Versenden)
- ``BERECHNET`` — die Sammelrechnung (``collective_documents.py``)
- ``storniert`` — ``sales_storno_service``

Auf einer gewachsenen Entwicklungsdatenbank faellt das nicht auf: Dort fehlt
die Bedingung. Auf einer frischen laufen Buchen, Versenden, Sammelrechnung
und Storno jeweils in einen 500er — der Lieferschein kommt ueber den Entwurf
nicht hinaus.

Diese Migration macht die Bedingung wahrheitsgemaess. Sie raeumt den
Widerspruch **nicht** auf, den sie dabei sichtbar macht: In einer Spalte
stehen drei Schreibweisen nebeneinander (englisch klein, deutsch klein,
deutsch gross). Das ist eine Entscheidung ueber das Fachmodell und gehoert
nicht in eine Migration, die nur eine Bedingung nachzieht. Festgehalten in
``docs/project-context/lieferschein-statuswerte-2026-09-29.md``.

Bestehende Zeilen werden nicht angefasst.

Revision ID: lieferschein_status_bedingung_20260929
Revises: erp_gutscheinkonto_20260928
"""

from __future__ import annotations

from alembic import op

revision = "lieferschein_status_bedingung_20260929"
down_revision = "erp_gutscheinkonto_20260928"
branch_labels = None
depends_on = None


# Die Werte, die der Code heute schreibt — und einer, den er nicht mehr
# schreibt, der aber im Bestand steht.
#
# ``geliefert`` liegt auf gebuchten Lieferscheinen aus einem aelteren
# Codepfad. Eine Bedingung, die Bestandszeilen abweist, laesst sich nicht
# anlegen; und Gebuchtes umzuschreiben, damit die Bedingung passt, waere
# genau das, was die GoBD verbieten (Rz. 107 ff.). Der Wert bleibt also
# zulaessig und ist als Altbestand vermerkt.
ZUSTAENDE = (
    "draft",
    "printed",
    "posted",
    "shipped",
    "delivered",
    "invoiced",
    "BERECHNET",
    "storniert",
    "cancelled",
    "geliefert",  # Altbestand, wird nicht mehr geschrieben
)

ALT = ("draft", "printed", "delivered", "invoiced", "cancelled")


def _setzen(werte: tuple[str, ...]) -> None:
    liste = ", ".join(f"'{w}'" for w in werte)
    op.execute(
        f"""
        ALTER TABLE domain_sales.delivery_notes
            DROP CONSTRAINT IF EXISTS ck_delivery_notes_status,
            ADD CONSTRAINT ck_delivery_notes_status
                CHECK (status IN ({liste}));
        """
        # Die Werteliste steht fest im Modul; es geht keine Eingabe ein.
    )


def upgrade() -> None:
    _setzen(ZUSTAENDE)


def downgrade() -> None:
    # Zurueck auf den alten Stand geht nur, solange keine Zeile einen der
    # vier neuen Zustaende traegt. Deshalb wird die Bedingung hier nur
    # entfernt, nicht verengt — ein Rueckbau soll keine Daten verlieren.
    op.execute(
        """
        ALTER TABLE domain_sales.delivery_notes
            DROP CONSTRAINT IF EXISTS ck_delivery_notes_status;
        """
    )
