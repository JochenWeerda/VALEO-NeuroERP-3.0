import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.weighing_tickets import _validate_and_compute_weights


def test_validate_and_compute_weights_success():
    value = _validate_and_compute_weights(42000.0, 12000.0, None)
    assert value == 30000.0


def test_validate_and_compute_weights_rejects_negative_values():
    with pytest.raises(HTTPException):
        _validate_and_compute_weights(-1.0, 0.0, None)


def test_validate_and_compute_weights_rejects_inconsistent_net():
    with pytest.raises(HTTPException):
        _validate_and_compute_weights(100.0, 20.0, 70.0)

