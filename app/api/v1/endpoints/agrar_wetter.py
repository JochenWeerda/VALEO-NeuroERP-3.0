"""
Agrar Wetter — Wetter-Proxy für BrightSky (DWD) + Open-Meteo (ICON-D2)

Endpoints:
  GET /agrar/wetter/aktuell      → BrightSky current_weather (DWD Stationsdaten)
  GET /agrar/wetter/prognose     → Open-Meteo DWD ICON-D2 7-Tage-Vorhersage
  GET /agrar/wetter/stunden      → BrightSky stündliche Wetterdaten
  GET /agrar/wetter/warnungen    → BrightSky DWD-Wetterwarnungen
  GET /agrar/wetter/boden        → Open-Meteo Bodenfeuchte + Bodentemperatur

Keine API-Keys erforderlich. Quellen:
  BrightSky: https://api.brightsky.dev  (DWD-Daten, Open Source)
  Open-Meteo: https://api.open-meteo.com (ICON-D2, kostenlos nicht-kommerziell)
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class AgrarWetterOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(tags=["agrar", "wetter"])

BRIGHTSKY_BASE = "https://api.brightsky.dev"
OPEN_METEO_BASE = "https://api.open-meteo.com/v1"

# Timeout für externe API-Calls (Sek.)
_TIMEOUT = 10.0

timezone_utc = timezone.utc


_http_client: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=_TIMEOUT)
    return _http_client


async def _get(url: str, params: dict) -> dict:
    """HTTP-GET mit Timeout-Handling und Connection-Pooling."""
    client = _get_http_client()
    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Wetter-API Timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Wetter-API Fehler: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Wetter-API nicht erreichbar: {str(e)}")


_weather_cache: dict = {}
_WEATHER_CACHE_TTL = 300  # 5 minutes


async def _cached_get(url: str, params: dict, cache_ttl: int = _WEATHER_CACHE_TTL) -> dict:
    """HTTP-GET with TTL caching for weather data."""
    import hashlib
    import json
    import time
    cache_key = hashlib.sha256(f"{url}:{json.dumps(params, sort_keys=True)}".encode()).hexdigest()
    now = time.time()
    if cache_key in _weather_cache and (now - _weather_cache[cache_key]["ts"]) < cache_ttl:
        return _weather_cache[cache_key]["data"]
    data = await _get(url, params)
    _weather_cache[cache_key] = {"data": data, "ts": now}
    return data


# ────────────────────────────────────────────────────────────────────────────
# Response Schemas
# ────────────────────────────────────────────────────────────────────────────

class WetterAktuell(BaseModel):
    timestamp: Optional[str] = None
    temperatur: Optional[float] = None           # °C
    taupunkt: Optional[float] = None             # °C
    relative_feuchte: Optional[int] = None       # %
    niederschlag: Optional[float] = None         # mm/h
    windgeschwindigkeit: Optional[float] = None  # km/h
    windrichtung: Optional[int] = None           # Grad
    windboee: Optional[float] = None             # km/h
    bedeckungsgrad: Optional[int] = None         # %
    sonnenscheindauer: Optional[int] = None      # min/h
    strahlung: Optional[float] = None            # Wh/m²
    luftdruck: Optional[float] = None            # hPa
    sichtweite: Optional[int] = None             # m
    bedingung: Optional[str] = None              # DWD icon code
    station_id: Optional[str] = None
    station_name: Optional[str] = None
    station_lat: Optional[float] = None
    station_lon: Optional[float] = None


class WetterWarnung(BaseModel):
    id: str
    event: str
    headline: str
    description: Optional[str] = None
    instruction: Optional[str] = None
    severity: str    # Minor | Moderate | Severe | Extreme
    urgency: Optional[str] = None
    certainty: Optional[str] = None
    gueltig_von: Optional[str] = None
    gueltig_bis: Optional[str] = None
    ausgabezeit: Optional[str] = None


class PrognoseTag(BaseModel):
    datum: str
    temperatur_max: Optional[float] = None
    temperatur_min: Optional[float] = None
    niederschlag_summe: Optional[float] = None   # mm
    niederschlag_stunden: Optional[int] = None
    et0_fao: Optional[float] = None              # mm (FAO Grasreferenz-ET₀)
    wachstumsgradtage: Optional[float] = None    # GDD base 0°C
    sonnenscheindauer: Optional[float] = None    # Stunden
    windgeschwindigkeit_max: Optional[float] = None  # km/h
    uv_index_max: Optional[float] = None


class BodenDaten(BaseModel):
    timestamp: str
    bodenfeuchte_0_1cm: Optional[float] = None   # m³/m³
    bodenfeuchte_1_3cm: Optional[float] = None
    bodenfeuchte_3_9cm: Optional[float] = None
    bodenfeuchte_9_27cm: Optional[float] = None
    bodenfeuchte_27_81cm: Optional[float] = None
    bodentemp_0cm: Optional[float] = None        # °C
    bodentemp_6cm: Optional[float] = None
    bodentemp_18cm: Optional[float] = None
    bodentemp_54cm: Optional[float] = None
    evapotranspiration: Optional[float] = None   # mm/h
    et0_fao: Optional[float] = None              # mm/h


# ────────────────────────────────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────────────────────────────────

@router.get("/wetter/aktuell", response_model=WetterAktuell, summary="Wetter aktuell abrufen")
async def get_wetter_aktuell(
    lat: float = Query(..., description="Breitengrad (WGS84)"),
    lon: float = Query(..., description="Längengrad (WGS84)"),
):
    """Aktuelles Wetter vom nächsten DWD-Messgerät (via BrightSky)."""
    data = await _cached_get(
        f"{BRIGHTSKY_BASE}/current_weather",
        {"lat": lat, "lon": lon, "units": "dwd"},
    )
    w = data.get("weather", {})
    src = data.get("sources", [{}])[0] if data.get("sources") else {}

    return WetterAktuell(
        timestamp=w.get("timestamp"),
        temperatur=w.get("temperature"),
        taupunkt=w.get("dew_point"),
        relative_feuchte=w.get("relative_humidity"),
        niederschlag=w.get("precipitation"),
        windgeschwindigkeit=w.get("wind_speed"),
        windrichtung=w.get("wind_direction"),
        windboee=w.get("wind_gust_speed"),
        bedeckungsgrad=w.get("cloud_cover"),
        sonnenscheindauer=w.get("sunshine"),
        strahlung=w.get("solar"),
        luftdruck=w.get("pressure_msl"),
        sichtweite=w.get("visibility"),
        bedingung=w.get("icon"),
        station_id=str(src.get("dwd_station_id", "")),
        station_name=src.get("station_name"),
        station_lat=src.get("lat"),
        station_lon=src.get("lon"),
    )


@router.get("/wetter/warnungen", response_model=list[WetterWarnung], summary="Wetter warnungen abrufen")
async def get_wetter_warnungen(
    lat: float = Query(..., description="Breitengrad"),
    lon: float = Query(..., description="Längengrad"),
):
    """DWD-Wetterwarnungen für eine Geokoordinate (via BrightSky)."""
    data = await _cached_get(
        f"{BRIGHTSKY_BASE}/alerts",
        {"lat": lat, "lon": lon},
    )
    result: list[WetterWarnung] = []
    for a in data.get("alerts", []):
        result.append(WetterWarnung(
            id=str(a.get("id", "")),
            event=a.get("event", ""),
            headline=a.get("headline", ""),
            description=a.get("description"),
            instruction=a.get("instruction"),
            severity=a.get("severity", "Minor"),
            urgency=a.get("urgency"),
            certainty=a.get("certainty"),
            gueltig_von=a.get("onset"),
            gueltig_bis=a.get("expires"),
            ausgabezeit=a.get("sent"),
        ))
    return result


@router.get("/wetter/stunden", response_model=list[AgrarWetterOut], summary="Wetter stunden abrufen")
async def get_wetter_stunden(
    lat: float = Query(..., description="Breitengrad"),
    lon: float = Query(..., description="Längengrad"),
    datum: str = Query(default=None, description="ISO-Datum (YYYY-MM-DD), Standard: heute"),
    bis: str = Query(default=None, description="End-Datum (YYYY-MM-DD), Standard: datum+1"),
):
    """Stündliche Wetterdaten (DWD-Stationsdaten via BrightSky)."""
    if not datum:
        datum = date.today().isoformat()
    if not bis:
        bis = (date.today() + timedelta(days=1)).isoformat()

    data = await _cached_get(
        f"{BRIGHTSKY_BASE}/weather",
        {"lat": lat, "lon": lon, "date": datum, "last_date": bis, "units": "dwd"},
    )

    records = []
    for w in data.get("weather", []):
        records.append({
            "timestamp": w.get("timestamp"),
            "temperatur": w.get("temperature"),
            "niederschlag": w.get("precipitation"),
            "windgeschwindigkeit": w.get("wind_speed"),
            "windrichtung": w.get("wind_direction"),
            "relative_feuchte": w.get("relative_humidity"),
            "bedeckungsgrad": w.get("cloud_cover"),
            "sonnenscheindauer": w.get("sunshine"),
            "bedingung": w.get("icon"),
        })
    return records


@router.get("/wetter/prognose", response_model=list[PrognoseTag], summary="Wetter prognose abrufen")
async def get_wetter_prognose(
    lat: float = Query(..., description="Breitengrad"),
    lon: float = Query(..., description="Längengrad"),
    tage: int = Query(default=7, ge=1, le=16, description="Prognosezeitraum in Tagen"),
    timezone: str = Query(default="Europe/Berlin"),
):
    """7-Tage-Wetterprognose mit Agrar-Variablen (Open-Meteo DWD ICON-D2)."""
    start = date.today().isoformat()
    end = (date.today() + timedelta(days=tage - 1)).isoformat()

    data = await _cached_get(
        f"{OPEN_METEO_BASE}/dwd-icon",
        {
            "latitude": lat,
            "longitude": lon,
            "daily": ",".join([
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_hours",
                "et0_fao_evapotranspiration",
                "growing_degree_days_base_0_limit_50",
                "sunshine_duration",
                "windspeed_10m_max",
                "uv_index_max",
            ]),
            "timezone": timezone,
            "start_date": start,
            "end_date": end,
            "models": "icon_seamless",
        },
    )

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    result: list[PrognoseTag] = []

    for i, d in enumerate(dates):
        def _v(key: str) -> Any:
            vals = daily.get(key, [])
            return vals[i] if i < len(vals) else None

        result.append(PrognoseTag(
            datum=d,
            temperatur_max=_v("temperature_2m_max"),
            temperatur_min=_v("temperature_2m_min"),
            niederschlag_summe=_v("precipitation_sum"),
            niederschlag_stunden=int(_v("precipitation_hours") or 0),
            et0_fao=_v("et0_fao_evapotranspiration"),
            wachstumsgradtage=_v("growing_degree_days_base_0_limit_50"),
            sonnenscheindauer=round((_v("sunshine_duration") or 0) / 3600, 1),  # s → h
            windgeschwindigkeit_max=_v("windspeed_10m_max"),
            uv_index_max=_v("uv_index_max"),
        ))

    return result


@router.get("/wetter/boden", response_model=list[BodenDaten], summary="Wetter boden abrufen")
async def get_wetter_boden(
    lat: float = Query(..., description="Breitengrad"),
    lon: float = Query(..., description="Längengrad"),
    stunden: int = Query(default=48, ge=1, le=240, description="Stunden Vorhersagezeitraum"),
    timezone: str = Query(default="Europe/Berlin"),
):
    """Bodenfeuchte, Bodentemperatur und Evapotranspiration (Open-Meteo ICON-D2)."""
    start = datetime.now(tz=timezone_utc).strftime("%Y-%m-%d")
    end = (datetime.now(tz=timezone_utc) + timedelta(hours=stunden)).strftime("%Y-%m-%d")

    data = await _cached_get(
        f"{OPEN_METEO_BASE}/dwd-icon",
        {
            "latitude": lat,
            "longitude": lon,
            "hourly": ",".join([
                "soil_moisture_0_to_1cm",
                "soil_moisture_1_to_3cm",
                "soil_moisture_3_to_9cm",
                "soil_moisture_9_to_27cm",
                "soil_moisture_27_to_81cm",
                "soil_temperature_0cm",
                "soil_temperature_6cm",
                "soil_temperature_18cm",
                "soil_temperature_54cm",
                "evapotranspiration",
                "et0_fao_evapotranspiration",
            ]),
            "timezone": timezone,
            "start_date": start,
            "end_date": end,
            "models": "icon_seamless",
        },
    )

    hourly = data.get("hourly", {})
    timestamps = hourly.get("time", [])
    result: list[BodenDaten] = []

    for i, ts in enumerate(timestamps[:stunden]):
        def _v(key: str) -> Any:
            vals = hourly.get(key, [])
            return vals[i] if i < len(vals) else None

        result.append(BodenDaten(
            timestamp=ts,
            bodenfeuchte_0_1cm=_v("soil_moisture_0_to_1cm"),
            bodenfeuchte_1_3cm=_v("soil_moisture_1_to_3cm"),
            bodenfeuchte_3_9cm=_v("soil_moisture_3_to_9cm"),
            bodenfeuchte_9_27cm=_v("soil_moisture_9_to_27cm"),
            bodenfeuchte_27_81cm=_v("soil_moisture_27_to_81cm"),
            bodentemp_0cm=_v("soil_temperature_0cm"),
            bodentemp_6cm=_v("soil_temperature_6cm"),
            bodentemp_18cm=_v("soil_temperature_18cm"),
            bodentemp_54cm=_v("soil_temperature_54cm"),
            evapotranspiration=_v("evapotranspiration"),
            et0_fao=_v("et0_fao_evapotranspiration"),
        ))

    return result
