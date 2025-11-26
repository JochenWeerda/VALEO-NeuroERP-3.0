"""Validierungsregeln für InfraStat."""

from __future__ import annotations

from typing import Iterable, List, Tuple

from app.schemas.declaration import DeclarationLineCreate


class InfrastatValidator:
    """Führt semantische Validierungen durch (TARIC, Mengeneinheiten etc.)."""

    def __init__(self, valid_commodity_codes: set[str] | None = None, valid_country_codes: set[str] | None = None) -> None:
        self._commodity_codes = valid_commodity_codes or set()
        self._country_codes = valid_country_codes or set()

    def validate_lines(self, lines: Iterable[DeclarationLineCreate]) -> Tuple[List[dict], List[DeclarationLineCreate]]:
        errors: List[dict] = []
        valid_lines: List[DeclarationLineCreate] = []

        for line in lines:
            line_errors = []

            if self._commodity_codes and line.commodity_code not in self._commodity_codes:
                line_errors.append(
                    {
                        "code": "INVALID_TARIC",
                        "severity": "error",
                        "message": f"Unbekannte Warennummer {line.commodity_code}",
                        "details": {"commodity_code": line.commodity_code},
                    }
                )

            if self._country_codes:
                if line.country_of_origin not in self._country_codes:
                    line_errors.append(
                        {
                            "code": "INVALID_COUNTRY_ORIGIN",
                            "severity": "error",
                            "message": f"Ungültiges Ursprungsland {line.country_of_origin}",
                            "details": {"country": line.country_of_origin},
                        }
                    )
                if line.country_of_destination not in self._country_codes:
                    line_errors.append(
                        {
                            "code": "INVALID_COUNTRY_DESTINATION",
                            "severity": "error",
                            "message": f"Ungültiges Bestimmungsland {line.country_of_destination}",
                            "details": {"country": line.country_of_destination},
                        }
                    )

            if line.net_mass_kg <= 0:
                line_errors.append(
                    {
                        "code": "NEGATIVE_WEIGHT",
                        "severity": "error",
                        "message": "Netto-Masse muss größer 0 sein.",
                        "details": {"net_mass_kg": line.net_mass_kg},
                    }
                )

            if line.invoice_value_eur <= 0:
                line_errors.append(
                    {
                        "code": "NEGATIVE_VALUE",
                        "severity": "error",
                        "message": "Rechnungswert muss größer 0 sein.",
                        "details": {"invoice_value_eur": line.invoice_value_eur},
                    }
                )

            if line_errors:
                for error in line_errors:
                    error["line_id"] = None
                    error["sequence_no"] = line.sequence_no
                errors.extend(line_errors)
            else:
                valid_lines.append(line)

        return errors, valid_lines

