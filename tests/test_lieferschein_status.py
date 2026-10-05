import pytest

from app.domains.sales.lieferschein_status import pruefe_status


def test_entwurf_ist_zulaessig():
    pruefe_status("draft")


def test_offen_ist_kein_lieferschein_status():
    with pytest.raises(ValueError, match="offen"):
        pruefe_status("offen")
