from decimal import Decimal

import pytest

from app.services.kontrakte_service import (
    KontraktRestmengenService,
    KontraktSecurityService,
    KontraktValidationService,
)


def test_security_roles_intersection() -> None:
    assert KontraktSecurityService.has_any_role(["KONTRAKT_LESEN"], "KONTRAKT_LESEN") is True
    assert KontraktSecurityService.has_any_role(["OTHER"], "KONTRAKT_ADMIN") is False


def test_validation_contract_type_and_status() -> None:
    KontraktValidationService.validate_contract_type("VERKAUF")
    KontraktValidationService.validate_status("OFFEN")
    KontraktValidationService.validate_quantity_type("GESAMTKONTRAKT")
    with pytest.raises(ValueError):
        KontraktValidationService.validate_contract_type("INVALID")


def test_overdelivery_rule_enforcement() -> None:
    service = KontraktRestmengenService(db=None)  # type: ignore[arg-type]
    service.enforce_overdelivery(True, Decimal("10"), Decimal("11"))
    with pytest.raises(ValueError):
        service.enforce_overdelivery(False, Decimal("10"), Decimal("11"))


def test_determine_status_from_rest() -> None:
    assert KontraktRestmengenService.determine_status_from_rest(False, "OFFEN", Decimal("0")) == "ERLEDIGT"
    assert KontraktRestmengenService.determine_status_from_rest(False, "OFFEN", Decimal("1")) == "OFFEN"
    assert KontraktRestmengenService.determine_status_from_rest(True, "OFFEN", Decimal("-5")) == "OFFEN"
    assert KontraktRestmengenService.determine_status_from_rest(False, "STORNIERT", Decimal("-5")) == "STORNIERT"
