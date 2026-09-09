"""SPEC-P1-06 Welle 8: Verankerung der Feldableitung gegen die reale DDL.

Welle 7 hat inventory_operations und agri_silo_material_flow bewusst
zurueckgestellt, weil beide ``SELECT *`` ueber Tabellen mit starker
Migrationsdrift lesen. Eine aus den Migrationen rekonstruierte Spaltenliste
waere dort nicht belastbar gewesen.

Dieser Test dreht die Richtung um: die Modelle in
``inventory_lot_bundle_schemas`` und ``silo_material_flow_schemas`` werden
gegen ``information_schema.columns`` einer laufenden, auf head migrierten
Datenbank geprueft. Faellt eine Spalte weg oder kommt eine dazu, ohne dass das
Modell nachgezogen wurde, schlaegt der Test an.

Ohne erreichbare Datenbank wird der Test uebersprungen - er ist ein
Drift-Waechter fuer Entwicklung und DB-fuehrende CI-Stufen, kein Unit-Test.
"""

import pytest
from sqlalchemy import text

from app.api.v1.schemas import inventory_lot_bundle_schemas as lots
from app.api.v1.schemas import silo_material_flow_schemas as flow

pytestmark = pytest.mark.integration

SCHEMA = "domain_inventory"

# Modell -> (Tabelle, Felder die das Modell zusaetzlich zur DDL fuehrt)
MODELL_ZU_TABELLE = [
    (lots.InventoryLotOut, "inventory_lots", set()),
    # idempotent ist ein Statusfeld der Antwort, keine Spalte.
    (lots.StornoKorrekturOut, "inventory_stock_movements", {"idempotent"}),
    (flow.SiloSystemOut, "silo_systems", set()),
    (flow.SiloCellOut, "silo_cells", set()),
    (flow.MaterialFlowNodeOut, "material_flow_nodes", set()),
    (flow.MaterialFlowEdgeOut, "material_flow_edges", set()),
]


# Felder, die je nach Datenbankgeneration Spalte sind oder nicht. Eine frisch
# migrierte Datenbank fuehrt die historischen Belegfelder, eine gewachsene
# Bestandsdatenbank kann sie ebenfalls fuehren — beide muessen mit demselben
# Antwortmodell auskommen. Deshalb werden sie auf beiden Seiten herausgerechnet:
# ihr Fehlen ist kein Modellfehler, ihr Vorhandensein kein Modellueberhang.
GENERATIONSABHAENGIGE_FELDER: dict[str, set[str]] = {
    "inventory_stock_movements": {
        "reference_type",
        "reference_id",
        "booked_at",
        "booked_by",
    },
}

@pytest.fixture(scope="module")
def db_session():
    from app.core.database import SessionLocal

    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - ohne DB ist der Waechter nicht anwendbar
        pytest.skip(f"keine Datenbank erreichbar: {exc.__class__.__name__}")
    try:
        yield session
    finally:
        session.close()


def _spalten(session, tabelle: str) -> set[str]:
    rows = session.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :tabelle"
        ),
        {"schema": SCHEMA, "tabelle": tabelle},
    ).scalars().all()
    return set(rows)


@pytest.mark.parametrize(
    "modell,tabelle,zusatzfelder",
    MODELL_ZU_TABELLE,
    ids=[eintrag[1] for eintrag in MODELL_ZU_TABELLE],
)
def test_modellfelder_decken_die_ddl_vollstaendig_ab(db_session, modell, tabelle, zusatzfelder):
    spalten = _spalten(db_session, tabelle)
    if not spalten:
        pytest.skip(f"{SCHEMA}.{tabelle} in dieser Datenbank nicht vorhanden")

    felder = set(modell.model_fields) - zusatzfelder

    generationsabhaengig = GENERATIONSABHAENGIGE_FELDER.get(tabelle, set())
    spalten = spalten - generationsabhaengig
    felder = felder - generationsabhaengig

    fehlend = spalten - felder
    assert not fehlend, (
        f"{modell.__name__} verliert Spalten von {SCHEMA}.{tabelle}: {sorted(fehlend)}"
    )

    ueberzaehlig = felder - spalten
    assert not ueberzaehlig, (
        f"{modell.__name__} fuehrt Felder ohne Spalte in {SCHEMA}.{tabelle}: "
        f"{sorted(ueberzaehlig)}"
    )


def test_bewegungstabelle_fuehrt_den_kanonischen_belegbezug(db_session):
    """Neue Buchungen tragen den kanonischen Belegbezug.

    Ersetzt die frueheren Abwesenheitstests fuer ``reference_type``/
    ``reference_id``. Die Altfelder bleiben erhalten — ein Bestandshauptbuch
    nach GoB muss den urspruenglichen Belegbezug waehrend der
    Aufbewahrungsfrist lesbar halten, und ein Spalten-Drop gaebe genau das auf.
    Geprueft wird deshalb der fachliche Vertrag, nicht die Spaltenmenge.
    """
    spalten = _spalten(db_session, "inventory_stock_movements")
    if not spalten:
        pytest.skip(f"{SCHEMA}.inventory_stock_movements nicht vorhanden")

    assert "source_document_type" in spalten
    assert "source_document_id" in spalten


def test_altfelder_bleiben_lesbar_wenn_die_datenbank_sie_fuehrt(db_session):
    """Wo Altfelder existieren, gibt das Antwortmodell sie auch heraus.

    Sonst waere der historische Belegbezug zwar gespeichert, aber ueber die
    API unsichtbar — gespeichert ist nicht dasselbe wie nachvollziehbar.
    """
    from app.api.v1.schemas.inventory_lot_bundle_schemas import StornoKorrekturOut

    spalten = _spalten(db_session, "inventory_stock_movements")
    if not spalten:
        pytest.skip(f"{SCHEMA}.inventory_stock_movements nicht vorhanden")

    for altfeld in ("reference_type", "reference_id"):
        if altfeld in spalten:
            assert altfeld in StornoKorrekturOut.model_fields, (
                f"{altfeld} liegt in der Datenbank, fehlt aber im Antwortmodell"
            )


def test_belegbezug_bevorzugt_kanonisch_und_bleibt_paarweise():
    """Der Bezug stammt immer aus genau einem Feldpaar."""
    from app.services.inventory_document_reference import belegbezug

    kanonisch = belegbezug(
        {
            "source_document_type": "WARENEINGANG",
            "source_document_id": "WE-1",
            "reference_type": None,
            "reference_id": None,
        }
    )
    assert (kanonisch.typ, kanonisch.id) == ("WARENEINGANG", "WE-1")
    assert kanonisch.herkunft == "kanonisch"
    assert kanonisch.konflikt is False

    # Historische Zeile: nur das Altpaar ist gefuellt und bleibt aufloesbar.
    historisch = belegbezug(
        {
            "source_document_type": None,
            "source_document_id": None,
            "reference_type": "KORREKTUR",
            "reference_id": "KO-7",
        }
    )
    assert (historisch.typ, historisch.id) == ("KORREKTUR", "KO-7")
    assert historisch.herkunft == "historisch"
    assert historisch.konflikt is False

    # Kein gemischtes Paar: kanonischer Typ plus historische Id ergibt nicht
    # ploetzlich eine Verknuepfung.
    gemischt = belegbezug(
        {
            "source_document_type": "STORNO",
            "source_document_id": None,
            "reference_type": None,
            "reference_id": "ALT-9",
        }
    )
    assert gemischt.konflikt is True
    assert gemischt.id != "ALT-9"


def test_widersprechende_belegbezuege_werden_ausgewiesen_nicht_umgedeutet():
    """Zwei gefuellte, widersprechende Paare sind ein Klaerfall."""
    from app.services.inventory_document_reference import belegbezug

    bezug = belegbezug(
        {
            "source_document_type": "WARENEINGANG",
            "source_document_id": "WE-1",
            "reference_type": "WARENAUSGANG",
            "reference_id": "WA-2",
        }
    )
    assert bezug.konflikt is True
    # Beide Paare bleiben sichtbar, damit die Klaerung nichts nachschlagen muss.
    assert bezug.kanonisch == ("WARENEINGANG", "WE-1")
    assert bezug.historisch == ("WARENAUSGANG", "WA-2")


def test_leere_zeile_behauptet_keinen_belegbezug():
    from app.services.inventory_document_reference import belegbezug

    bezug = belegbezug({})
    assert bezug.herkunft == "keiner"
    assert bezug.vorhanden is False


def test_keine_migration_entfernt_die_altfelder():
    """Der Bestand darf nicht durch eine spaetere Migration verschwinden.

    Punkt 5 der Festlegung: Buchungsanzahl, Mengen, Werte und Belegverknuepfung
    bleiben beim Upgrade erhalten. Fuer die Verknuepfung heisst das konkret:
    keine Migration wirft die Altspalten weg.
    """
    from pathlib import Path

    wurzel = Path(__file__).parents[1] / "alembic" / "versions"
    treffer: list[str] = []
    for datei in wurzel.glob("*.py"):
        text_inhalt = datei.read_text(encoding="utf-8", errors="replace").lower()
        if "inventory_stock_movements" not in text_inhalt:
            continue
        for altfeld in ("reference_type", "reference_id"):
            if f"drop column {altfeld}" in text_inhalt or f'drop_column("{altfeld}"' in text_inhalt:
                treffer.append(f"{datei.name}: {altfeld}")
    assert treffer == [], f"Migration entfernt historische Belegfelder: {treffer}"
