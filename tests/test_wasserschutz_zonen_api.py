"""
Contract-Tests für die Wasserschutz-Zonen-API (A2)

Testet:
- Zonen-Listing (alle Zonen)
- Nähe-Filterung mit Koordinaten + Radius
- BoundingBox-Validierung (Deutschland)
- Einzelzone abrufen
- TTL-Cache-Verhalten
"""

import time

import pytest

from app.domains.agrar.api.psm import (
    _bbox_valid,
    _get_wasserschutz_zonen_data,
    _haversine_km,
    _WSZ_CACHE,
)


# ── BoundingBox-Validierung ──────────────────────────────────────────────


class TestBBoxValidation:
    def test_halle_saale_inside(self):
        assert _bbox_valid(51.48, 11.97) is True

    def test_berlin_inside(self):
        assert _bbox_valid(52.52, 13.40) is True

    def test_munich_inside(self):
        assert _bbox_valid(48.14, 11.58) is True

    def test_flensburg_inside(self):
        assert _bbox_valid(54.78, 9.44) is True

    def test_paris_outside(self):
        assert _bbox_valid(48.86, 2.35) is False

    def test_oslo_outside(self):
        assert _bbox_valid(59.91, 10.75) is False

    def test_south_of_germany(self):
        assert _bbox_valid(46.0, 11.0) is False

    def test_east_of_germany(self):
        assert _bbox_valid(51.0, 16.0) is False


# ── Haversine-Distanz ────────────────────────────────────────────────────


class TestHaversine:
    def test_same_point(self):
        assert _haversine_km(51.0, 11.0, 51.0, 11.0) == pytest.approx(0.0, abs=0.01)

    def test_halle_to_dessau(self):
        dist = _haversine_km(51.48, 11.97, 51.83, 12.24)
        assert 30.0 < dist < 50.0

    def test_symmetric(self):
        d1 = _haversine_km(51.0, 11.0, 52.0, 12.0)
        d2 = _haversine_km(52.0, 12.0, 51.0, 11.0)
        assert d1 == pytest.approx(d2, abs=0.01)


# ── Zonen-Daten + Cache ─────────────────────────────────────────────────


class TestWasserschutzZonenData:
    def setup_method(self):
        _WSZ_CACHE.clear()

    def test_returns_list(self):
        zones = _get_wasserschutz_zonen_data()
        assert isinstance(zones, list)
        assert len(zones) > 0

    def test_zone_schema(self):
        zones = _get_wasserschutz_zonen_data()
        for z in zones:
            assert "id" in z
            assert "name" in z
            assert "typ" in z
            assert "zone" in z
            assert "restriktionsgrad" in z
            assert z["restriktionsgrad"] in ("hoch", "mittel", "niedrig")
            assert "koordinaten" in z
            assert "lat" in z["koordinaten"]
            assert "lng" in z["koordinaten"]
            assert "radius" in z

    def test_all_zones_inside_bbox(self):
        zones = _get_wasserschutz_zonen_data()
        for z in zones:
            lat = z["koordinaten"]["lat"]
            lng = z["koordinaten"]["lng"]
            assert _bbox_valid(lat, lng), f"Zone {z['id']} liegt außerhalb der BBox"

    def test_cache_hit(self):
        zones1 = _get_wasserschutz_zonen_data()
        zones2 = _get_wasserschutz_zonen_data()
        assert zones1 is zones2

    def test_unique_ids(self):
        zones = _get_wasserschutz_zonen_data()
        ids = [z["id"] for z in zones]
        assert len(ids) == len(set(ids))


# ── PSM-Compliance-Validierung ───────────────────────────────────────────


from modules.agrar.services.feldbuch_service import validate_psm_compliance
from datetime import datetime


class TestPSMCompliance:
    def test_non_psm_always_compliant(self):
        result = validate_psm_compliance(
            typ="duengung", datum=None, mittel=None, menge=None,
            einheit=None, flaeche=None, anwender=None, auflagen=None,
            wartezeit_tage=None, windgeschwindigkeit=None, temperatur=None,
        )
        assert result["compliant"] is True
        assert result["violations"] == []

    def test_complete_psm_is_compliant(self):
        result = validate_psm_compliance(
            typ="psm", datum=datetime.now(), mittel="Amistar Opti",
            menge=1.0, einheit="l/ha", flaeche=5.0, anwender="Max Müller",
            auflagen=["NW468", "NT102"], wartezeit_tage=35,
            windgeschwindigkeit=10.0, temperatur=18.0,
        )
        assert result["compliant"] is True
        assert result["violations"] == []

    def test_missing_datum_is_violation(self):
        result = validate_psm_compliance(
            typ="psm", datum=None, mittel="Amistar Opti",
            menge=1.0, einheit="l/ha", flaeche=5.0, anwender="Max Müller",
            auflagen=None, wartezeit_tage=None,
            windgeschwindigkeit=None, temperatur=None,
        )
        assert result["compliant"] is False
        assert any("Datum" in v for v in result["violations"])

    def test_missing_mittel_is_violation(self):
        result = validate_psm_compliance(
            typ="psm", datum=datetime.now(), mittel=None,
            menge=1.0, einheit="l/ha", flaeche=5.0, anwender="Max",
            auflagen=None, wartezeit_tage=None,
            windgeschwindigkeit=None, temperatur=None,
        )
        assert result["compliant"] is False
        assert any("PSM" in v for v in result["violations"])

    def test_missing_all_pflichtfelder(self):
        result = validate_psm_compliance(
            typ="psm", datum=None, mittel=None, menge=None,
            einheit=None, flaeche=None, anwender=None, auflagen=None,
            wartezeit_tage=None, windgeschwindigkeit=None, temperatur=None,
        )
        assert result["compliant"] is False
        assert len(result["violations"]) == 6

    def test_high_wind_warning(self):
        result = validate_psm_compliance(
            typ="psm", datum=datetime.now(), mittel="Folicur",
            menge=1.5, einheit="l/ha", flaeche=10.0, anwender="Hans",
            auflagen=None, wartezeit_tage=28,
            windgeschwindigkeit=30.0, temperatur=20.0,
        )
        assert result["compliant"] is True
        assert any("Wind" in w for w in result["warnings"])

    def test_high_temperature_warning(self):
        result = validate_psm_compliance(
            typ="psm", datum=datetime.now(), mittel="Folicur",
            menge=1.5, einheit="l/ha", flaeche=10.0, anwender="Hans",
            auflagen=None, wartezeit_tage=28,
            windgeschwindigkeit=5.0, temperatur=38.0,
        )
        assert result["compliant"] is True
        assert any("Verdunstung" in w for w in result["warnings"])

    def test_low_temperature_warning(self):
        result = validate_psm_compliance(
            typ="psm", datum=datetime.now(), mittel="Folicur",
            menge=1.5, einheit="l/ha", flaeche=10.0, anwender="Hans",
            auflagen=None, wartezeit_tage=28,
            windgeschwindigkeit=5.0, temperatur=2.0,
        )
        assert result["compliant"] is True
        assert any("eingeschr" in w for w in result["warnings"])

    def test_unknown_auflage_prefix_warning(self):
        result = validate_psm_compliance(
            typ="psm", datum=datetime.now(), mittel="Nativo",
            menge=0.8, einheit="l/ha", flaeche=3.0, anwender="Luise",
            auflagen=["NW468", "XX123"], wartezeit_tage=35,
            windgeschwindigkeit=None, temperatur=None,
        )
        assert result["compliant"] is True
        assert any("XX123" in w for w in result["warnings"])

    def test_negative_wartezeit_violation(self):
        result = validate_psm_compliance(
            typ="psm", datum=datetime.now(), mittel="Nativo",
            menge=0.8, einheit="l/ha", flaeche=3.0, anwender="Luise",
            auflagen=None, wartezeit_tage=-5,
            windgeschwindigkeit=None, temperatur=None,
        )
        assert result["compliant"] is False
        assert any("Wartezeit" in v for v in result["violations"])
