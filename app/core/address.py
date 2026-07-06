"""Kanonisches Adress-Value-Object für VALEO NeuroERP.

Vereinheitlicht die historisch uneinheitlichen Adress-Darstellungen:
- JSONB-Objekt mit Alias-Keys (country/countryCode/country_code,
  postal_code/postalCode/zip/zipCode/plz, city/ort, street/strasse …)
- flache Spalten (Warehouse: address/city/postal_code/country)
- Freitext-String ("Hauptstrasse 123, 48143 Muenster")

Neuer Code sollte `Address` als Repraesentation nutzen. `parse_address()`
akzeptiert alle drei Eingabeformen und normalisiert auf kanonische Felder;
`to_jsonb()`/`format_oneline()` serialisieren zurueck. So koennen bestehende
Entitaeten schrittweise auf das gemeinsame Value-Object migriert werden, ohne
ihre Speicherform sofort zu aendern (Adapter an der Schema-Grenze).

Siehe docs/architecture/adr/adr-039-address-value-object.md.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

# Alias-Mengen aus dem Bestand (add_customer_address_generated_columns_20260217,
# customer_service.py, diverse JSONB-Schreiber).
_STREET_KEYS = ("street", "strasse", "straße", "line1", "address_line1", "anschrift")
_HOUSE_KEYS = ("house_no", "house_number", "hausnummer", "hausnr", "number")
_ZIP_KEYS = ("postal_code", "postalCode", "zip", "zipCode", "plz")
_CITY_KEYS = ("city", "ort", "town")
_COUNTRY_KEYS = ("country", "countryCode", "country_code", "land")
_REGION_KEYS = ("region", "state", "bundesland", "province")

# "Hauptstrasse 123, 48143 Muenster" bzw. "48143 Muenster"
_STR_PLZ_CITY = re.compile(r"^\s*(?P<street>.*?)(?:,\s*)?(?P<zip>\b\d{4,5}\b)\s+(?P<city>[^,]+?)\s*$")


class Address(BaseModel):
    """Strukturierte Adresse (kanonisch). Alle Felder optional (Bestandstoleranz)."""

    model_config = ConfigDict(extra="ignore")

    street: Optional[str] = None
    house_no: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = Field(default=None, description="ISO-3166-alpha-2, z. B. 'DE'")
    lat: Optional[float] = None
    lon: Optional[float] = None

    def is_empty(self) -> bool:
        return not any((self.street, self.postal_code, self.city, self.country))

    def to_jsonb(self) -> dict[str, Any]:
        """Kanonische dict-Form fuer JSONB-Spalten."""
        return {
            k: v
            for k, v in {
                "street": self.street,
                "house_no": self.house_no,
                "postal_code": self.postal_code,
                "city": self.city,
                "region": self.region,
                "country": self.country,
                "lat": self.lat,
                "lon": self.lon,
            }.items()
            if v is not None
        }

    def format_oneline(self) -> str:
        """Einzeilige Freitext-Darstellung (fuer flache String-Spalten/Anzeige)."""
        line1 = " ".join(p for p in (self.street, self.house_no) if p)
        line2 = " ".join(p for p in (self.postal_code, self.city) if p)
        parts = [p for p in (line1, line2, self.country if self.country and self.country != "DE" else None) if p]
        return ", ".join(parts)


def _first(d: dict[str, Any], keys: tuple[str, ...]) -> Optional[Any]:
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def parse_address(value: Any) -> Address:
    """Best-effort-Normalisierung beliebiger Bestandsformen auf `Address`.

    Akzeptiert dict (JSONB mit Alias-Keys), Freitext-String, `Address` oder None.
    """
    if value is None:
        return Address()
    if isinstance(value, Address):
        return value
    if isinstance(value, dict):
        lat = value.get("lat") or value.get("latitude")
        lon = value.get("lon") or value.get("lng") or value.get("longitude")
        return Address(
            street=_first(value, _STREET_KEYS),
            house_no=_first(value, _HOUSE_KEYS),
            postal_code=_str_or_none(_first(value, _ZIP_KEYS)),
            city=_first(value, _CITY_KEYS),
            region=_first(value, _REGION_KEYS),
            country=_first(value, _COUNTRY_KEYS),
            lat=_float_or_none(lat),
            lon=_float_or_none(lon),
        )
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return Address()
        # JSONB-Spalten liefern teils den JSON-String statt eines dict.
        if s[0] in "{[":
            import json as _json
            try:
                parsed = _json.loads(s)
                if isinstance(parsed, dict):
                    return parse_address(parsed)
            except (ValueError, TypeError):
                pass
        m = _STR_PLZ_CITY.match(s)
        if m:
            street = m.group("street").strip().rstrip(",").strip() or None
            return Address(street=street, postal_code=m.group("zip"), city=m.group("city").strip())
        return Address(street=s)
    return Address()


def flat_to_address(
    address: Optional[str] = None,
    city: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None,
) -> Address:
    """Adapter fuer Entitaeten mit flachen Spalten (z. B. Warehouse)."""
    base = parse_address(address) if address else Address()
    return base.model_copy(update={
        "city": city or base.city,
        "postal_code": postal_code or base.postal_code,
        "country": country or base.country,
    })


def _str_or_none(v: Any) -> Optional[str]:
    return str(v) if v not in (None, "") else None


def _float_or_none(v: Any) -> Optional[float]:
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None
