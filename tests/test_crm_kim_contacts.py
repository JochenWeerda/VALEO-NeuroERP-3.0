"""KIM Ansprechpartner-Vertrag."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from app.api.v1.endpoints.crm_kim import ContactPersonCreate, create_contact, list_contacts

pytestmark = pytest.mark.unit


class _Mappings:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def all(self) -> list[dict]:
        return self._rows


class _Result:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def mappings(self) -> _Mappings:
        return _Mappings(self._rows)


def test_list_contacts_maps_contact_email() -> None:
    db = Mock()
    db.execute.return_value = _Result([{
        "id": 7,
        "anrede": "Herr",
        "nachname": "Mustermann",
        "vorname": "Max",
        "position": "Einkauf",
        "prioritaet": 1,
        "telefon1": "04941 111",
        "telefon2": None,
        "mobil": None,
        "email": "max.mustermann@example.test",
        "geburtsdatum": None,
    }])

    contacts = list_contacts("KD-1", db=db, tenant_id="tenant-1")

    assert contacts[0].email == "max.mustermann@example.test"
    assert "email" in str(db.execute.call_args.args[0])


def test_create_contact_persists_contact_email() -> None:
    db = Mock()
    body = ContactPersonCreate(
        name="Mustermann",
        firstName="Max",
        phone1="04941 111",
        email="max.mustermann@example.test",
    )

    result = create_contact("KD-1", body=body, db=db, tenant_id="tenant-1")

    assert result.status == "success"
    assert db.execute.call_args.args[1]["email"] == "max.mustermann@example.test"
    db.commit.assert_called_once()


def test_list_contacts_falls_back_when_legacy_table_has_no_email_column() -> None:
    db = Mock()
    db.execute.side_effect = [
        RuntimeError("column email does not exist"),
        _Result([{
            "id": 8,
            "anrede": "Frau",
            "nachname": "Beispiel",
            "vorname": "Eva",
            "position": "Disposition",
            "prioritaet": 2,
            "telefon1": "04941 333",
            "telefon2": None,
            "mobil": None,
            "geburtsdatum": None,
        }]),
    ]

    contacts = list_contacts("KD-2", db=db, tenant_id="tenant-1")

    assert contacts[0].name == "Beispiel"
    assert contacts[0].email is None
    db.rollback.assert_called_once()
