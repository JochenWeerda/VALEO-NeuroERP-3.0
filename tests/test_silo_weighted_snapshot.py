from app.api.v1.endpoints.silo import _weighted_quality_snapshot


class _Lot:
    def __init__(self, quantity_tons, moisture_pct=None, protein_pct=None, impurities_pct=None, hl_weight=None, status="active"):
        self.quantity_tons = quantity_tons
        self.moisture_pct = moisture_pct
        self.protein_pct = protein_pct
        self.impurities_pct = impurities_pct
        self.hl_weight = hl_weight
        self.status = status


def test_weighted_snapshot_empty():
    snapshot = _weighted_quality_snapshot([])
    assert snapshot["total_quantity_tons"] == 0.0
    assert snapshot["lot_count"] == 0
    assert snapshot["moisture_avg_pct"] is None


def test_weighted_snapshot_calculation():
    lots = [
        _Lot(quantity_tons=10, moisture_pct=13.0, protein_pct=11.0, impurities_pct=2.0, hl_weight=78.0),
        _Lot(quantity_tons=30, moisture_pct=15.0, protein_pct=12.0, impurities_pct=1.0, hl_weight=80.0),
        _Lot(quantity_tons=20, moisture_pct=None, protein_pct=13.0, impurities_pct=None, hl_weight=76.0),
    ]
    snapshot = _weighted_quality_snapshot(lots)
    assert snapshot["total_quantity_tons"] == 60.0
    assert snapshot["lot_count"] == 3
    assert snapshot["moisture_avg_pct"] == 14.5
    assert snapshot["protein_avg_pct"] == 12.17
    assert snapshot["impurities_avg_pct"] == 1.25
    assert snapshot["hl_weight_avg"] == 78.33


def test_weighted_snapshot_ignores_inactive_lots():
    lots = [
        _Lot(quantity_tons=10, moisture_pct=12.0, status="active"),
        _Lot(quantity_tons=20, moisture_pct=40.0, status="closed"),
    ]
    snapshot = _weighted_quality_snapshot(lots)
    assert snapshot["total_quantity_tons"] == 10.0
    assert snapshot["lot_count"] == 1
    assert snapshot["moisture_avg_pct"] == 12.0
