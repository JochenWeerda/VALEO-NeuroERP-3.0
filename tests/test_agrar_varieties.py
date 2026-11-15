"""Canonical variety schema and HTTP boundaries, without dev tokens or a database.

Authentication and SQL are test boundaries. Domain roles and request validation
run through the actual FastAPI router. PostgreSQL/RLS remains a separate proof.
"""
import pytest
from pydantic import ValidationError
from app.auth.deps import get_current_user
from app.api.v1.endpoints.agrar_varieties import VarietyIn, VarietyOut
from test_agrar_variety_read_contract import client_with


class TestVarietySchemas:
    """Pydantic validation for VarietyIn / VarietyOut."""

    def test_valid_minimal(self):
        v = VarietyIn(variety_number="100", name="Mais")
        assert v.variety_number == "100"
        assert v.name == "Mais"
        assert v.description is None
        assert v.crop_type is None
        assert v.zuechter is None

    def test_valid_full(self):
        v = VarietyIn(
            variety_number="245",
            name="Weizen Elite",
            description="Hochleistungsweizen",
            crop_type="WHEAT",
            zuechter="Saatzucht GmbH",
            zulassungsjahr=2024,
            reifezahl="S240",
            qualitaetsgruppe="E",
        )
        assert v.zuechter == "Saatzucht GmbH"
        assert v.zulassungsjahr == 2024
        assert v.qualitaetsgruppe == "E"

    def test_empty_variety_number_rejected(self):
        with pytest.raises(ValidationError):
            VarietyIn(variety_number="", name="Test")

    def test_variety_number_too_long_rejected(self):
        with pytest.raises(ValidationError):
            VarietyIn(variety_number="x" * 21, name="Test")

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            VarietyIn(variety_number="100", name="")

    def test_name_too_long_rejected(self):
        with pytest.raises(ValidationError):
            VarietyIn(variety_number="100", name="n" * 256)

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            VarietyIn()

    def test_missing_variety_number(self):
        with pytest.raises(ValidationError):
            VarietyIn(name="Weizen")

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            VarietyIn(variety_number="100")

    def test_variety_out_requires_id(self):
        with pytest.raises(ValidationError):
            VarietyOut(variety_number="100", name="Mais")

    def test_variety_out_valid(self):
        v = VarietyOut(id="abc-123", variety_number="100", name="Mais")
        assert v.id == "abc-123"
        assert v.aktiv is True

@pytest.fixture
def route_client():
    client, db, query = client_with([])
    user = {"sub": "synthetic-variety-reader", "roles": ["AGRAR_LESEN"]}
    client.app.dependency_overrides[get_current_user] = lambda: user
    query.first.return_value = None
    with client:
        yield client, db, query, user


def test_list_returns_real_empty_inventory_without_creating_defaults(route_client):
    client, db, _, _ = route_client
    result = client.get("/api/v1/agrar/varieties/")
    assert result.status_code == 200 and result.json() == []
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_crop_filter_remains_bound_to_the_requested_tenant(route_client):
    client, db, query, _ = route_client
    response = client.get("/api/v1/agrar/varieties/?crop_type=WHEAT&aktiv=false")
    assert response.status_code == 200
    predicates = [call.args[0] for call in query.filter.call_args_list]
    assert len(predicates) == 2
    assert predicates[0].right.value == "tenant-contract"
    assert predicates[1].right.value == "WHEAT"
    db.commit.assert_not_called()


@pytest.mark.parametrize("method,path", [("post", "/"), ("put", "/v1"), ("delete", "/v1")])
def test_read_role_cannot_create_edit_or_deactivate(route_client, method, path):
    client, db, query, _ = route_client
    args = {"json": {"variety_number": "V1", "name": "Synthetic"}} if method != "delete" else {}
    response = getattr(client, method)("/api/v1/agrar/varieties" + path, **args)
    assert response.status_code == 403
    db.query.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize("method,path", [("get", "/foreign-id"), ("put", "/foreign-id"), ("delete", "/foreign-id")])
def test_missing_tenant_record_is_never_reported_as_success(route_client, method, path):
    client, db, query, user = route_client
    user["roles"] = ["AGRAR_BEARBEITEN"]
    args = {"json": {"variety_number": "V1", "name": "Synthetic"}} if method == "put" else {}
    response = getattr(client, method)("/api/v1/agrar/varieties" + path, **args)
    assert response.status_code == 404
    predicate = query.filter.call_args.args[0]
    assert [part.right.value for part in predicate.clauses] == ["foreign-id", "tenant-contract"]
    db.commit.assert_not_called()


@pytest.mark.parametrize("payload", [{}, {"variety_number": "V1"}, {"name": "Synthetic"}])
def test_authorized_create_still_validates_required_fields_before_sql(route_client, payload):
    client, db, _, user = route_client
    user["roles"] = ["AGRAR_BEARBEITEN"]
    response = client.post("/api/v1/agrar/varieties/", json=payload)
    assert response.status_code == 422
    db.query.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()
