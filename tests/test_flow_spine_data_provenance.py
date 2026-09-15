"""FSX-003 — Gate: operative Registry-Konstanten duerfen im Instanzpfad nicht erscheinen.

Die drei Feldzustaende aus dem Masterplan
(`docs/design/flow-spine-entlastung-masterplan.md`):

1. Statisch und zulaessig  — Prozessdefinition: Phasenbezeichnung, Knotenlabel,
   Reihenfolge, Icon, Beschreibung, Zielrouten. Bleibt im Registry und wird hier
   ausdruecklich *nicht* beanstandet.
2. Operativ und vorhanden  — instanzbezogen, mit benannter Quelle (FSX-001).
3. Operativ und nicht ermittelbar — als fehlend sichtbar, nie durch einen
   Registry-Vorgabewert ersetzt.

Dieses Gate prueft genau den verbotenen Fall: ein operativer Wert aus dem
Registry im Kontext einer echten Instanz.
"""

from __future__ import annotations

import pytest

from app.core.flow_spine_registry import (
    CONTENT_MODE_CATALOG,
    CONTENT_MODE_INSTANCE,
    DEFINITION_NODE_FIELDS,
    OPERATIONAL_NODE_FIELDS,
    WORKSPACES,
    get_flow_spine_workspace,
    merge_instance_statuses,
)

pytestmark = pytest.mark.unit

ALL_PROCESS_KEYS = sorted(WORKSPACES.keys())


def _instance(process_key: str, **overrides: object) -> dict:
    base = {
        "instance_id": "11111111-1111-1111-1111-111111111111",
        "case_number": "WF-00042",
        "label": "Testvorgang",
        "node_statuses": {},
        "process_key": process_key,
    }
    base.update(overrides)
    return base


@pytest.mark.parametrize("process_key", ALL_PROCESS_KEYS)
def test_operative_registry_werte_erscheinen_nicht_im_instanzpfad(process_key: str) -> None:
    """Fall 3 darf nicht wie Fall 2 aussehen: keine Registry-Vorgabe als Vorgangswert."""
    catalog = get_flow_spine_workspace(process_key)
    registry_values = {
        node["id"]: {field: node.get(field) for field in OPERATIONAL_NODE_FIELDS}
        for node in catalog["nodes"]
    }

    merged = merge_instance_statuses(
        get_flow_spine_workspace(process_key), _instance(process_key)
    )

    for node in merged["nodes"]:
        node_id = node["id"]
        for field in OPERATIONAL_NODE_FIELDS:
            value = node.get(field)
            if not value:
                continue  # leer ist erlaubt — das ist der sichtbar fehlende Fall
            assert value != registry_values[node_id][field], (
                f"Prozess '{process_key}', Knoten '{node_id}': operatives Feld "
                f"'{field}' zeigt im Instanzpfad den Registry-Vorgabewert. "
                "Entweder an eine benannte Quelle binden (FSX-001) oder leer "
                "lassen, damit es als fehlend erkennbar bleibt."
            )


@pytest.mark.parametrize("process_key", ALL_PROCESS_KEYS)
def test_definitionsfelder_bleiben_im_instanzpfad_erhalten(process_key: str) -> None:
    """Fall 1 ist zulaessig: Phasenbezeichner duerfen und sollen statisch bleiben."""
    catalog = get_flow_spine_workspace(process_key)
    expected = {
        node["id"]: {
            field: node.get(field)
            for field in DEFINITION_NODE_FIELDS
            if field != "status"  # Status wird bewusst aus der Instanz ueberlagert
        }
        for node in catalog["nodes"]
    }

    merged = merge_instance_statuses(
        get_flow_spine_workspace(process_key), _instance(process_key)
    )

    for node in merged["nodes"]:
        for field, value in expected[node["id"]].items():
            assert node.get(field) == value, (
                f"Prozess '{process_key}', Knoten '{node['id']}': Definitionsfeld "
                f"'{field}' wurde im Instanzpfad veraendert. Phasenbezeichnungen, "
                "Labels, Icons, Beschreibungen und Zielrouten sind Prozess"
                "definition und bleiben statisch."
            )


@pytest.mark.parametrize("process_key", ALL_PROCESS_KEYS)
def test_knotenstatus_wird_weiterhin_aus_der_instanz_uebernommen(process_key: str) -> None:
    """Die Statusueberlagerung bleibt funktionsfaehig — das Gate darf sie nicht brechen."""
    catalog = get_flow_spine_workspace(process_key)
    first_node_id = catalog["nodes"][0]["id"]

    merged = merge_instance_statuses(
        get_flow_spine_workspace(process_key),
        _instance(process_key, node_statuses={first_node_id: "blocked"}),
    )

    assert merged["nodes"][0]["status"] == "blocked"


@pytest.mark.parametrize("process_key", ALL_PROCESS_KEYS)
def test_inhaltsmodus_wird_ausgewiesen(process_key: str) -> None:
    """Der Beispielinhalt des Katalogfalls wird gekennzeichnet, nicht verschwiegen."""
    catalog = get_flow_spine_workspace(process_key)
    assert catalog["content_mode"] == CONTENT_MODE_CATALOG
    assert all(node.get("data_state") == "example" for node in catalog["nodes"])

    merged = merge_instance_statuses(
        get_flow_spine_workspace(process_key), _instance(process_key)
    )
    assert merged["content_mode"] == CONTENT_MODE_INSTANCE
    for node in merged["nodes"]:
        assert node.get("metric") is None
        assert node.get("submetric") is None
        assert node.get("kpis") == []
        assert node.get("documents") == []
        assert node.get("agent") is None
        if node.get("timestamp") or node.get("detail_rows"):
            assert node.get("data_state") == "instance"
        else:
            assert node.get("data_state") == "not_determined"


def test_feldlisten_sind_ueberschneidungsfrei_und_vollstaendig() -> None:
    """Jedes Knotenfeld ist entweder Definition oder operativ — nichts dazwischen."""
    overlap = set(OPERATIONAL_NODE_FIELDS) & set(DEFINITION_NODE_FIELDS)
    assert not overlap, f"Feld in beiden Listen: {sorted(overlap)}"

    sample_node = get_flow_spine_workspace(ALL_PROCESS_KEYS[0])["nodes"][0]
    classified = set(OPERATIONAL_NODE_FIELDS) | set(DEFINITION_NODE_FIELDS) | {"data_state"}
    unclassified = set(sample_node.keys()) - classified
    assert not unclassified, (
        f"Nicht eingeordnete Knotenfelder: {sorted(unclassified)}. "
        "Jedes neue Feld muss als Definition oder als operativ deklariert werden."
    )
