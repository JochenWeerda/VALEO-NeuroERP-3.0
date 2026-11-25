"""KIM Ansprechpartner-Vertrag."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from app.api.v1.endpoints.crm_kim import ContactPersonCreate, create_contact, list_contacts

pytestmark = pytest.mark.unit

_EIGENER = {
    "kunden_nr": "KD-1",
    "name1": "Mustermann",
    "geloescht": False,
    "business_partner_id": "bp-1",
}


class _Mappings:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def all(self) -> list[dict]:
        return self._rows

    def first(self) -> dict | None:
        return self._rows[0] if self._rows else None


class _Result:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def mappings(self) -> _Mappings:
        return _Mappings(self._rows)


@patch("app.api.v1.endpoints.crm_kim.public_kunde_im_mandanten", return_value=_EIGENER)
def test_list_contacts_maps_contact_email(_kunde) -> None:
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


@patch("app.api.v1.endpoints.crm_kim.public_kunde_im_mandanten", return_value=_EIGENER)
def test_create_contact_persists_contact_email(_kunde) -> None:
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


@patch("app.api.v1.endpoints.crm_kim.public_kunde_im_mandanten", return_value={**_EIGENER, "kunden_nr": "KD-2"})
def test_list_contacts_falls_back_when_legacy_table_has_no_email_column(_kunde) -> None:
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


@patch("app.api.v1.endpoints.crm_kim.public_kunde_im_mandanten", return_value=None)
def test_list_contacts_fremder_mandant_404(_kunde) -> None:
    from fastapi import HTTPException

    db = Mock()
    with pytest.raises(HTTPException) as exc:
        list_contacts("KD-fremd", db=db, tenant_id="tenant-1")
    assert exc.value.status_code == 404
    db.execute.assert_not_called()
