"""Transformationslogik für InfraStat."""

from __future__ import annotations

from datetime import date
from typing import Iterable, List, Mapping, Tuple

from app.schemas.declaration import DeclarationBatchCreate, DeclarationLineCreate
from app.config import settings


class InfrastatTransformer:
    """Erzeugt deklarative Payloads aus Rohdaten."""

    DEFAULT_FLOW_TYPE = "dispatch"

    def __init__(self, reference_period: date, tenant_id: str, flow_type: str | None = None) -> None:
        self._reference_period = reference_period
        self._tenant_id = tenant_id
        self._flow_type = flow_type or self.DEFAULT_FLOW_TYPE

    def transform(
        self,
        records: Iterable[Mapping[str, object]],
    ) -> Tuple[DeclarationBatchCreate, List[str]]:
        lines: List[DeclarationLineCreate] = []
        warnings: List[str] = []
        seq = 1

        for record in records:
            try:
                line = DeclarationLineCreate(
                    sequence_no=seq,
                    commodity_code=str(record["commodity_code"]),
                    country_of_origin=str(record.get("country_of_origin", settings.DEFAULT_TENANT))[:2],
                    country_of_destination=str(record.get("country_of_destination", "DE"))[:2],
                    net_mass_kg=float(record.get("net_mass_kg", 0)),
                    supplementary_units=self._optional_float(record.get("supplementary_units")),
                    invoice_value_eur=float(record.get("invoice_value_eur", 0)),
                    statistical_value_eur=self._optional_float(record.get("statistical_value_eur")),
                    nature_of_transaction=str(record.get("nature_of_transaction", "11")),
                    transport_mode=str(record.get("transport_mode", "3")),
                    delivery_terms=str(record.get("delivery_terms", "DAP")) if record.get("delivery_terms") else None,
                    line_data={k: v for k, v in record.items() if k not in self._excluded_keys()},
                )
            except (TypeError, ValueError, KeyError) as exc:  # noqa: PERF203
                warnings.append(f"Datensatz {seq} übersprungen: {exc}")
                seq += 1
                continue

            lines.append(line)
            seq += 1

        batch = DeclarationBatchCreate(
            tenant_id=self._tenant_id,
            flow_type=self._flow_type,
            reference_period=self._reference_period,
            lines=lines,
            metadata={"source": "etl", "record_count": len(lines)},
        )
        return batch, warnings

    @staticmethod
    def _optional_float(value: object) -> float | None:
        if value in (None, "", "null"):
            return None
        return float(value)

    @staticmethod
    def _excluded_keys() -> set[str]:
        return {
            "commodity_code",
            "country_of_origin",
            "country_of_destination",
            "net_mass_kg",
            "supplementary_units",
            "invoice_value_eur",
            "statistical_value_eur",
            "nature_of_transaction",
            "transport_mode",
            "delivery_terms",
        }

