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

    fehlend = spalten - felder
    assert not fehlend, (
        f"{modell.__name__} verliert Spalten von {SCHEMA}.{tabelle}: {sorted(fehlend)}"
    )

    ueberzaehlig = felder - spalten
    assert not ueberzaehlig, (
        f"{modell.__name__} fuehrt Felder ohne Spalte in {SCHEMA}.{tabelle}: "
        f"{sorted(ueberzaehlig)}"
    )


def test_bewegungstabelle_hat_kein_reference_type(db_session):
    """Regression zum Welle-8-Befund.

    ``storno_korrektur`` und ``differenz_buchen`` haben auf
    ``reference_type``/``reference_id`` geschrieben und gefiltert. Diese
    Spalten existieren nicht; kanonisch sind ``source_document_type`` und
    ``source_document_id``. Kommen sie eines Tages doch dazu, soll dieser Test
    auffallen, damit die Dienste bewusst nachgezogen werden.
    """
    spalten = _spalten(db_session, "inventory_stock_movements")
    if not spalten:
        pytest.skip(f"{SCHEMA}.inventory_stock_movements nicht vorhanden")

    assert "source_document_type" in spalten
    assert "source_document_id" in spalten
    assert "reference_type" not in spalten
    assert "reference_id" not in spalten
