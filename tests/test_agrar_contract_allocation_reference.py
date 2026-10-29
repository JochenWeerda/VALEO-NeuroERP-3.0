"""Tenant and mutation guards for optional Agrar allocation ticket references."""

from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.infrastructure.models import AgrarContract, WeighingTicket
from app.services.agrar_contract_service import AgrarContractService


class _Query:
    def __init__(self, rows):
        self.rows = rows
        self.clauses = []

    def filter(self, *clauses):
        self.clauses.extend(clauses)
        return self

    def first(self):
        for row in self.rows:
            if all(getattr(row, clause.left.name) == clause.right.value for clause in self.clauses):
                return row
        return None


class _Db:
    def __init__(self, contract, tickets=()):
        self.rows = {AgrarContract: [contract], WeighingTicket: list(tickets)}
        self.queries = []
        self.added = []
        self.commits = 0

    def query(self, model):
        query = _Query(self.rows[model])
        self.queries.append((model, query))
        return query

    def add(self, row):
        self.added.append(row)

    def commit(self):
        self.commits += 1

    def refresh(self, _row):
        pass


def _service(tickets=()):
    contract = SimpleNamespace(
        id="contract-1", tenant_id="tenant-a", status="open",
        total_quantity_kg=Decimal("100"), remaining_quantity_kg=Decimal("100"),
    )
    db = _Db(contract, tickets)
    return AgrarContractService(db, "tenant-a"), db, contract


@pytest.mark.parametrize("tickets", [
    (),
    (SimpleNamespace(id="ticket-1", tenant_id="tenant-b"),),
])
def test_missing_or_foreign_ticket_rejected_before_mutation(tickets):
    service, db, contract = _service(tickets)

    with pytest.raises(EntityNotFoundError) as exc:
        service.allocate("contract-1", 10, "ticket-1", None)

    assert exc.value.detail == "WeighingTicket 'ticket-1' not found"
    assert contract.remaining_quantity_kg == Decimal("100")
    assert contract.status == "open"
    assert db.added == []
    assert db.commits == 0
    ticket_queries = [query for model, query in db.queries if model is WeighingTicket]
    assert len(ticket_queries) == 1
    assert {clause.left.name for clause in ticket_queries[0].clauses} == {"id", "tenant_id"}


def test_own_ticket_is_accepted():
    ticket = SimpleNamespace(id="ticket-1", tenant_id="tenant-a")
    service, db, contract = _service((ticket,))

    allocation = service.allocate("contract-1", 10, ticket.id, "note")

    assert allocation.ticket_id == ticket.id
    assert allocation.tenant_id == "tenant-a"
    assert contract.remaining_quantity_kg == Decimal("90")
    assert contract.status == "partially_allocated"
    assert db.added == [allocation]
    assert db.commits == 1


def test_allocation_without_ticket_remains_supported():
    service, db, contract = _service()

    allocation = service.allocate("contract-1", 10, None, None)

    assert allocation.ticket_id is None
    assert contract.remaining_quantity_kg == Decimal("90")
    assert all(model is not WeighingTicket for model, _ in db.queries)
    assert db.commits == 1


@pytest.mark.parametrize("quantity", [0, -10, float("nan"), float("inf"), float("-inf")])
def test_nonpositive_quantity_rejected_before_mutation(quantity):
    service, db, contract = _service()

    with pytest.raises(ValidationFailedError):
        service.allocate("contract-1", quantity, None, None)

    assert contract.remaining_quantity_kg == Decimal("100")
    assert contract.status == "open"
    assert db.added == []
    assert db.commits == 0
