from __future__ import annotations

from datetime import date
from types import SimpleNamespace

from app.xml import DatMLRawBuilder


def test_datml_raw_builder_generates_xml():
    batch = SimpleNamespace(
        reference_period=date(2025, 9, 1),
        metadata={
            "sender": {"name": "VALERO"},
            "receiver": {"name": "Destatis"},
        },
        lines=[
            SimpleNamespace(
                sequence_no=1,
                commodity_code="12099190",
                country_of_origin="DE",
                country_of_destination="FR",
                net_mass_kg=100.0,
                invoice_value_eur=15000.0,
                statistical_value_eur=None,
                delivery_terms=None,
            )
        ],
    )

    xml_output = DatMLRawBuilder(batch).build()

    assert "DatML-RAW-D" in xml_output
    assert "VALERO" in xml_output
    assert "Destatis" in xml_output
    assert "12099190" in xml_output
