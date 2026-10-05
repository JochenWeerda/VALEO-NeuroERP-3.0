"""Jedes Konto traegt genau eine Sache — und Gebuchtes bleibt stehen.

Drei Konten wurden im Code doppelt belegt. Das ist kein Schoenheitsfehler:
Die GoBD verlangen Nachvollziehbarkeit und Klarheit (Rz. 30 ff.) — ein
sachverstaendiger Dritter muss die Geschaeftsvorfaelle in angemessener Zeit
nachvollziehen koennen. Bei einem Konto, das zwei Dinge traegt, kann er das
nicht, und keiner der beiden Salden stimmt.

- **1200** ist die Bank. Der Verkauf buchte Forderungen darauf und behauptete
  damit Geld, das noch nicht da war. Forderungen sind 1400.
- **6000** ist Loehne und Gehaelter. Der Einkauf buchte Wareneinkauf darauf
  und vermischte Personal- mit Materialaufwand. Handelsware gehoert auf 5100.
- **1600** sind Verbindlichkeiten aus Lieferungen und Leistungen. Die Kasse
  buchte Gutscheine darauf — eine Leistungsverpflichtung gegenueber dem
  Kunden, keine Lieferantenschuld. Gutscheine stehen auf 1700.

Die Aenderungen wirken **nur nach vorn**. Die GoBD fordern Unveraenderbarkeit
(Rz. 107 ff.): Was gebucht ist, bleibt gebucht. Eine Umbuchung ist ein
Buchungsvorgang mit eigenem Beleg, kein Datenbankupdate — und damit eine
Entscheidung der Buchhaltung, nicht einer Migration.
"""

from __future__ import annotations

import os
import pathlib
import re

import pytest

pytestmark = pytest.mark.unit

WURZEL = pathlib.Path(__file__).resolve().parents[1]


def test_forderungen_stehen_nicht_auf_dem_bankkonto() -> None:
    from app.services.sales_posting_service import SalesPostingService

    assert SalesPostingService.ACCOUNT_RECEIVABLES == "1400"
    # Die Bank bleibt die Bank.
    assert SalesPostingService.ACCOUNT_RECEIVABLES != "1200"


def test_wareneinkauf_steht_nicht_auf_dem_lohnkonto() -> None:
    """6000 ist Loehne und Gehaelter — dort hat Handelsware nichts zu suchen."""
    quelle = (WURZEL / "app" / "services" / "procurement_service.py").read_text(
        encoding="utf-8"
    )
    obligo = quelle[quelle.index("OBLIGO-") : quelle.index("OBLIGO-") + 1500]

    assert 'fin.account_id_for_number("5100")' in obligo, "Das Bestellobligo bucht nicht auf 5100"
    assert 'fin.account_id_for_number("6000")' not in obligo, "Das Bestellobligo bucht noch auf 6000"


def test_gutscheine_stehen_nicht_bei_den_lieferantenschulden() -> None:
    from app.services.pos_accounting_service import ACCOUNT_DEFINITIONS

    assert "1700" in ACCOUNT_DEFINITIONS
    assert "Gutschein" in ACCOUNT_DEFINITIONS["1700"].name

    quelle = (WURZEL / "app" / "services" / "pos_accounting_service.py").read_text(
        encoding="utf-8"
    )
    # 1600 darf im Kassendienst gar nicht mehr vorkommen.
    assert '"1600"' not in quelle, "Der Kassendienst bucht noch auf 1600"


def test_keine_migration_schreibt_gebuchte_werte_um() -> None:
    """Unveraenderbarkeit: Gebuchtes wird nicht nachtraeglich umgeschrieben.

    Eine Migration, die einen gebuchten Betrag, ein Konto oder ein Datum
    aendert, tut das unsichtbar — ohne Beleg, ohne Gegenbuchung, ohne Spur.
    Das ist der Kern dessen, was die GoBD verbieten (Rz. 107 ff.).

    Eine **Nachfuellung** ist etwas anderes und bleibt erlaubt: Wird eine neue
    Spalte eingefuehrt und aus dem vorhandenen Wert gefuellt (``WHERE ... IS
    NULL``), aendert sich am Geschaeftsvorfall nichts — er wird nur
    vollstaendiger abgebildet. Genau das tut
    ``add_missing_domain_erp_finance_tables_20260304``, als es debit_amount
    aus debit und period aus entry_date ableitet.

    Geprueft wird deshalb die Unterscheidung, nicht das blosse Vorkommen:
    ein UPDATE ohne ``IS NULL``-Bedingung schreibt Bestehendes um, ein DELETE
    ohnehin.
    """
    verstoesse: list[str] = []
    # Bis zum Zeilenende lesen, nicht bis zum naechsten Anfuehrungszeichen:
    # In `SET period = TO_CHAR(entry_date, 'YYYY-MM') WHERE period IS NULL`
    # steht die entscheidende Bedingung hinter einem Hochkomma.
    anweisung = re.compile(
        r"(?P<art>UPDATE|DELETE\s+FROM)\s+[a-z_\.]*journal_entr\w*(?P<rest>.*)",
        re.IGNORECASE,
    )
    for datei in sorted((WURZEL / "alembic" / "versions").glob("*.py")):
        text = datei.read_text(encoding="utf-8", errors="ignore")
        for treffer in anweisung.finditer(text):
            art = treffer.group("art").upper()
            rest = treffer.group("rest")
            if art.startswith("DELETE"):
                verstoesse.append(f"{datei.name}: DELETE auf gebuchten Saetzen")
            elif "IS NULL" not in rest.upper():
                verstoesse.append(f"{datei.name}: UPDATE ohne IS-NULL-Bedingung")

    assert not verstoesse, (
        "Diese Migrationen schreiben Gebuchtes um: " + "; ".join(verstoesse)
    )


@pytest.mark.integration
def test_die_getrennten_konten_stehen_im_kontenrahmen() -> None:
    """Ohne Konto keine Buchung — die Trennung muss im Rahmen ankommen."""
    from sqlalchemy import create_engine, text

    url = os.environ.get(
        "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
    )
    try:
        engine = create_engine(url)
        with engine.connect() as verbindung:
            vorhanden = {
                r[0]
                for r in verbindung.execute(
                    text(
                        "SELECT account_number FROM domain_erp.chart_of_accounts "
                        "WHERE is_active = TRUE"
                    )
                )
            }
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")

    for konto, zweck in (
        ("1400", "Forderungen aus Lieferungen und Leistungen"),
        ("5100", "Einkauf Handelswaren"),
        ("1700", "Verbindlichkeiten aus ausgegebenen Gutscheinen"),
    ):
        assert konto in vorhanden, f"Konto {konto} ({zweck}) fehlt im Kontenrahmen"
