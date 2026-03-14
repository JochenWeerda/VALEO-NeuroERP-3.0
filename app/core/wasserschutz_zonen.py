from __future__ import annotations

import math
import time


WSZ_CACHE: dict[str, dict] = {}
WSZ_CACHE_TTL = 3600
DE_BBOX = {"min_lat": 47.27, "max_lat": 55.06, "min_lng": 5.87, "max_lng": 15.04}


def bbox_valid(lat: float, lng: float) -> bool:
    return DE_BBOX["min_lat"] <= lat <= DE_BBOX["max_lat"] and DE_BBOX["min_lng"] <= lng <= DE_BBOX["max_lng"]


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius_km = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_wasserschutz_zonen_data(*, from_api_enabled: bool, telemetry: dict[str, int], logger) -> list[dict]:
    cache_key = "wsz_all"
    entry = WSZ_CACHE.get(cache_key)
    if entry and (time.time() - entry["ts"]) < WSZ_CACHE_TTL:
        telemetry["hits"] += 1
        return entry["data"]

    telemetry["misses"] += 1

    if from_api_enabled:
        telemetry["api_calls"] += 1
        logger.info("AGRAR_ZONEN_FROM_API=True - WFS-Abfrage (Stub, nutzt Seed-Daten)")

    telemetry["seed_calls"] += 1

    zones = [
        {"id": "WSG-001", "name": "Wasserschutzgebiet Halle-Ost", "typ": "Trinkwasser", "zone": "III", "restriktionsgrad": "mittel", "koordinaten": {"lat": 51.48, "lng": 11.97}, "radius": 3.5},
        {"id": "WSG-002", "name": "WSG Elbaue Dessau", "typ": "Trinkwasser", "zone": "II", "restriktionsgrad": "hoch", "koordinaten": {"lat": 51.83, "lng": 12.24}, "radius": 2.0},
        {"id": "WSG-003", "name": "WSG Saale-Unstrut", "typ": "Grundwasser", "zone": "IIIA", "restriktionsgrad": "mittel", "koordinaten": {"lat": 51.21, "lng": 11.77}, "radius": 5.0},
        {"id": "WSG-004", "name": "WSG Mulde-Eilenburg", "typ": "Trinkwasser", "zone": "III", "restriktionsgrad": "niedrig", "koordinaten": {"lat": 51.46, "lng": 12.63}, "radius": 4.0},
        {"id": "WSG-005", "name": "WSG Thüringer Becken", "typ": "Grundwasser", "zone": "II", "restriktionsgrad": "hoch", "koordinaten": {"lat": 51.02, "lng": 11.03}, "radius": 3.0},
        {"id": "WSG-006", "name": "WSG Harz-Vorland", "typ": "Quellschutz", "zone": "I", "restriktionsgrad": "hoch", "koordinaten": {"lat": 51.75, "lng": 10.85}, "radius": 1.5},
        {"id": "WSG-007", "name": "WSG Magdeburger Börde", "typ": "Grundwasser", "zone": "III", "restriktionsgrad": "niedrig", "koordinaten": {"lat": 52.13, "lng": 11.62}, "radius": 6.0},
        {"id": "WSG-008", "name": "WSG Lausitz-Spreewald", "typ": "Trinkwasser", "zone": "IIIA", "restriktionsgrad": "mittel", "koordinaten": {"lat": 51.76, "lng": 14.33}, "radius": 4.5},
    ]
    WSZ_CACHE[cache_key] = {"ts": time.time(), "data": zones}
    return zones
