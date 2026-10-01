"""Neue Lagerbuchung: kanonische Spaltennamen, Altname nur als Adapter."""

from app.services.inventory_document_reference import Belegkonflikt, buchungsbeleg
import pytest


def test_altname_fuellt_die_kanonischen_spalten() -> None:
    beleg = buchungsbeleg(reference_type="lieferschein", reference_id="LS-19")
    assert beleg.source_document_type == "lieferschein"
    assert beleg.reference_number == "LS-19"


def test_kanonischer_name_hat_vorrang_bei_demselben_wert() -> None:
    beleg = buchungsbeleg(
        source_document_type="lieferschein",
        reference_number="LS-19",
        reference_type="lieferschein",
        reference_id="LS-19",
    )
    assert beleg.source_document_type == "lieferschein"
    assert beleg.reference_number == "LS-19"


def test_widerspruch_zwischen_namen_ist_ein_fehler() -> None:
    with pytest.raises(Belegkonflikt, match="Belegart"):
        buchungsbeleg(source_document_type="bestellung", reference_type="lieferschein")


def test_belegnummer_wird_nicht_zur_beleg_id() -> None:
    beleg = buchungsbeleg(reference_id="LS-19")
    assert beleg.reference_number == "LS-19"
    assert not hasattr(beleg, "source_document_id")
