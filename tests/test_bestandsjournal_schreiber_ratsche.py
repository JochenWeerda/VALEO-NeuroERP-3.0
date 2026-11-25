"""Ratsche: kein neuer Direktschreiber ins Bestandsjournal (24.11.2026).

Zielbild (docs/design/bestandsbuchung-wege-konsolidierung.md): ein Buchungsdienst
(``InventoryService.process_stock_movement``) ist der einzige Weg in ``domain_inventory.inventory_stock_movements``.
Heute schreiben 13 Stellen eigenes SQL; sie bilden die Baseline. Neue Stellen schlagen fehl; wer eine Stelle auf den
Dienst umstellt, senkt die Baseline hier (sie darf nur sinken).
"""
from __future__ import annotations

import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"
DIREKT = re.compile(r"INSERT\s+INTO\s+domain_inventory\.inventory_stock_movements\b", re.IGNORECASE)

#: Datei -> Anzahl direkter INSERTs (Stand 24.11.2026). Nur senken.
BASELINE = {
    "app/api/v1/endpoints/compat.py": 2,
    "app/api/v1/endpoints/inventory_operations.py": 1,
    "app/api/v1/endpoints/pos_retoure.py": 1,
    "app/api/v1/endpoints/warehouse_transfers.py": 2,
    "app/services/agri_flush_booking.py": 1,
    "app/services/agri_lot_link_booking_service.py": 1,
    "app/services/agri_silo_material_flow_service.py": 2,
    "app/services/docflow_lagerzugang.py": 1,
    "app/services/inventory_correction_service.py": 1,
    "app/services/inventory_count_close_service.py": 1,
    "app/services/mobile_sync_service.py": 1,
    "app/services/warehouse_service.py": 1,
}


def _fundstellen() -> dict[str, int]:
    gefunden: dict[str, int] = {}
    for pfad in APP.rglob("*.py"):
        anzahl = len(DIREKT.findall(pfad.read_text(encoding="utf-8", errors="ignore")))
        if anzahl:
            gefunden[pfad.relative_to(APP.parent).as_posix()] = anzahl
    return gefunden


def test_kein_neuer_direktschreiber_ins_bestandsjournal():
    neu = {datei: n for datei, n in _fundstellen().items() if n > BASELINE.get(datei, 0)}
    assert not neu, ("Bestandsbewegungen nur ueber InventoryService.process_stock_movement "
                     f"(docs/design/bestandsbuchung-wege-konsolidierung.md): {neu}")


def test_baseline_sinkt_mit():
    veraltet = {datei: (soll, _fundstellen().get(datei, 0)) for datei, soll in BASELINE.items()
                if _fundstellen().get(datei, 0) < soll}
    assert not veraltet, f"Direktschreiber abgebaut - BASELINE senken: {veraltet}"


def test_muster_trifft_den_direktschreiber():
    assert DIREKT.search("INSERT INTO domain_inventory.inventory_stock_movements (id, tenant_id)")
    assert not DIREKT.search("SELECT * FROM domain_inventory.inventory_stock_movements")
