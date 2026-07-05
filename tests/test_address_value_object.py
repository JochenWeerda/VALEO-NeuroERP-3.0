"""Tests fuer das kanonische Adress-Value-Object (app/core/address.py)."""
from __future__ import annotations

import pytest

from app.core.address import Address, flat_to_address, parse_address


def test_parse_none_and_empty():
    assert parse_address(None).is_empty()
    assert parse_address("").is_empty()
    assert parse_address({}).is_empty()


@pytest.mark.parametrize("zip_key", ["postal_code", "postalCode", "zip", "zipCode", "plz"])
def test_parse_jsonb_zip_aliases(zip_key):
    a = parse_address({zip_key: "48143", "city": "Muenster"})
    assert a.postal_code == "48143"
    assert a.city == "Muenster"


@pytest.mark.parametrize("country_key", ["country", "countryCode", "country_code", "land"])
def test_parse_jsonb_country_aliases(country_key):
    assert parse_address({country_key: "DE"}).country == "DE"


@pytest.mark.parametrize("city_key", ["city", "ort", "town"])
def test_parse_jsonb_city_aliases(city_key):
    assert parse_address({city_key: "Krummhoern"}).city == "Krummhoern"


def test_parse_freitext_street_zip_city():
    a = parse_address("Hauptstrasse 123, 48143 Muenster")
    assert a.postal_code == "48143"
    assert a.city == "Muenster"
    assert a.street and "Hauptstrasse 123" in a.street


def test_parse_freitext_zip_city_only():
    a = parse_address("26736 Krummhoern")
    assert a.postal_code == "26736"
    assert a.city == "Krummhoern"


def test_parse_freitext_plain_street():
    a = parse_address("Musterweg 5")
    assert a.street == "Musterweg 5"
    assert a.postal_code is None


def test_geo_aliases():
    a = parse_address({"latitude": "53.1", "longitude": "7.2", "city": "X"})
    assert a.lat == pytest.approx(53.1)
    assert a.lon == pytest.approx(7.2)


def test_flat_to_address_adapter():
    a = flat_to_address(address="Teststrasse 1", city="Teststadt", postal_code="00000", country="DE")
    assert a.city == "Teststadt"
    assert a.postal_code == "00000"
    assert a.country == "DE"


def test_roundtrip_to_jsonb_and_back():
    original = Address(street="Weg 1", postal_code="12345", city="Ort", country="DE")
    restored = parse_address(original.to_jsonb())
    assert restored == original


def test_format_oneline():
    a = Address(street="Hauptstr.", house_no="7", postal_code="48143", city="Muenster", country="DE")
    line = a.format_oneline()
    assert "Hauptstr. 7" in line
    assert "48143 Muenster" in line
    assert "DE" not in line  # DE wird nicht angehaengt

    a2 = Address(street="Main St", postal_code="10001", city="NYC", country="US")
    assert "US" in a2.format_oneline()


def test_idempotent_parse_of_address():
    a = Address(city="X", postal_code="1")
    assert parse_address(a) is a
