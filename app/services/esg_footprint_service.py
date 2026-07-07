"""ESG-CO2e-Fussabdruck je Charge (UIX-082) — auditierbarer Berechnungskern.

Reine, deterministische Berechnung: gleiche Inputs + gleiche Faktor-Version
ergeben ein identisches Ergebnis (Decimal, 3 Dezimalen). Jede Komponente traegt
einen `source_ref` (Beleg-Verweis) — Auditierbarkeit ist Abnahmekriterium.
Fehlender Input → Komponente fehlt (KEINE 0-Schaetzung). Keine DB, keine Secrets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "esg_factors.yaml"
_Q = Decimal("0.001")


class EsgConfigError(RuntimeError):
    pass


@lru_cache(maxsize=4)
def _load_config() -> dict[str, Any]:
    if not _CONFIG_PATH.exists():
        raise EsgConfigError(f"ESG-Faktor-Konfiguration fehlt: {_CONFIG_PATH}")
    data = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    if "version" not in data or "factors" not in data:
        raise EsgConfigError("esg_factors.yaml braucht 'version' und 'factors'")
    return data


def current_factor_version() -> str:
    return str(_load_config()["version"])


def get_factor(factor_key: str) -> dict[str, Any] | None:
    return _load_config()["factors"].get(factor_key)


@dataclass(frozen=True)
class EsgInput:
    """Ein Mess-/Beleg-Input je Emissionsfaktor."""
    factor_key: str
    value: float
    source_ref: str


@dataclass
class FootprintComponent:
    key: str
    input: dict[str, float]
    factor_version: str
    co2e_kg: float
    source_ref: str
    source: str


@dataclass
class Footprint:
    charge_id: str
    tenant_id: str | None
    factor_version: str
    co2e_kg: float
    components: list[FootprintComponent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "charge_id": self.charge_id,
            "tenant_id": self.tenant_id,
            "factor_version": self.factor_version,
            "co2e_kg": self.co2e_kg,
            "components": [
                {
                    "key": c.key,
                    "input": c.input,
                    "factor_version": c.factor_version,
                    "co2e_kg": c.co2e_kg,
                    "source_ref": c.source_ref,
                    "source": c.source,
                }
                for c in self.components
            ],
        }


def _round3(value: Decimal) -> float:
    return float(value.quantize(_Q, rounding=ROUND_HALF_UP))


def compute_footprint(
    charge_id: str,
    inputs: list[EsgInput],
    *,
    tenant_id: str | None = None,
    factor_version: str | None = None,
) -> Footprint:
    """Berechnet den CO2e-Fussabdruck einer Charge aus Belegen.

    Nur Inputs mit bekanntem Faktor erzeugen eine Komponente; unbekannte oder
    fehlende Inputs werden uebersprungen (keine Schaetzung). Deterministisch.
    """
    config = _load_config()
    version = str(factor_version or config["version"])
    factors = config["factors"]

    components: list[FootprintComponent] = []
    total = Decimal("0")
    # Stabile Reihenfolge (nach Faktor-Schluessel) fuer reproduzierbare Ausgabe.
    for item in sorted(inputs, key=lambda i: i.factor_key):
        factor = factors.get(item.factor_key)
        if factor is None:
            continue  # unbekannter Faktor → keine Schaetzung
        co2e = (Decimal(str(item.value)) * Decimal(str(factor["co2e_kg"])))
        total += co2e
        components.append(
            FootprintComponent(
                key=item.factor_key,
                input={factor.get("unit", "unit"): item.value},
                factor_version=version,
                co2e_kg=_round3(co2e),
                source_ref=item.source_ref,
                source=str(factor.get("source", "")),
            )
        )

    return Footprint(
        charge_id=charge_id,
        tenant_id=tenant_id,
        factor_version=version,
        co2e_kg=_round3(total),
        components=components,
    )
