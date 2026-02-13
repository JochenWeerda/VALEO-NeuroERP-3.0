from fastapi import HTTPException

from app.api.v1.endpoints.weighing_tickets import _resolve_ticket_allocation_quantity


class _Ticket:
    def __init__(self, billing_weight=None, net_weight=None):
        self.billing_weight = billing_weight
        self.net_weight = net_weight


def test_resolve_allocation_uses_requested_quantity():
    ticket = _Ticket(billing_weight=100.0, net_weight=90.0)
    quantity = _resolve_ticket_allocation_quantity(ticket, 42.0)
    assert float(quantity) == 42.0


def test_resolve_allocation_falls_back_to_billing_weight():
    ticket = _Ticket(billing_weight=88.5, net_weight=90.0)
    quantity = _resolve_ticket_allocation_quantity(ticket, None)
    assert float(quantity) == 88.5


def test_resolve_allocation_falls_back_to_net_weight():
    ticket = _Ticket(billing_weight=None, net_weight=90.0)
    quantity = _resolve_ticket_allocation_quantity(ticket, None)
    assert float(quantity) == 90.0


def test_resolve_allocation_raises_if_no_weight_available():
    ticket = _Ticket(billing_weight=None, net_weight=None)
    try:
        _resolve_ticket_allocation_quantity(ticket, None)
        assert False, "expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 400

