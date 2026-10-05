"""
Vertragstests fuer die Kunden-Id im Leseweg
(Slice SPEC-SOURCE-REALAPP-20260910).

Die Spalte ``domain_crm.customers.id`` ist ``character varying`` und traegt
neben UUIDs auch fachliche Schluessel aus Demo- und UAT-Bestaenden. Das
Antwortmodell ``Customer`` fuehrte ``id`` als ``UUID`` — dadurch brach
``GET /api/v1/crm/customers/`` mit HTTP 500 ab, sobald der CRM-Sidecar nicht
erreichbar war und der Degrade-Pfad lokale Daten las. Sichtbar wurde das erst
in einer Umgebung ohne Sidecar, also genau im CI-Runtime-Sweep.

Ohne Datenbank und ohne Netzwerk lauffaehig.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.v1.schemas.crm import Customer, CustomerCreate, CustomerUpdate

TENANT = "00000000-0000-0000-0000-000000000001"

# Ids, die am 2026-09-10 real in domain_crm.customers standen.
GESPEICHERTE_IDS = [
    "019c0008-0000-7000-8000-000000000001",
    "crm360-uat-customer-20260609042028",
    "DEMO-CUST-001",
]


def _zeile(kunden_id):
    return {
        "id": kunden_id,
        "tenant_id": TENANT,
        "customer_number": "KD-10001",
        "company_name": "Musterhof GmbH",
        "created_at": datetime(2026, 9, 10, 12, 0, 0),
        "updated_at": datetime(2026, 9, 10, 12, 0, 0),
    }


class TestLeseweg:
    @pytest.mark.parametrize("kunden_id", GESPEICHERTE_IDS)
    def test_gespeicherte_id_wird_unveraendert_gelesen(self, kunden_id):
        assert Customer.model_validate(_zeile(kunden_id)).id == kunden_id

    def test_regression_demo_cust_001(self):
        """Genau der Wert, an dem der Sweep unter CI-Bedingungen scheiterte."""
        assert Customer.model_validate(_zeile("DEMO-CUST-001")).id == "DEMO-CUST-001"

    def test_id_wird_nicht_in_uuid_umgedeutet(self):
        kunde = Customer.model_validate(_zeile("DEMO-CUST-001"))
        assert isinstance(kunde.id, str)

    def test_mandantengrenze_bleibt_streng(self):
        """Bewusst nicht mitgelockert: eine nicht auswertbare tenant_id ist ein
        Mandantenproblem und soll auffallen, nicht durchgereicht werden."""
        with pytest.raises(ValidationError):
            Customer.model_validate(_zeile("DEMO-CUST-001") | {"tenant_id": "kein-mandant"})


class TestSchreibweg:
    def test_create_nimmt_keine_id_entgegen(self):
        """Die Lockerung darf keinen Schreibweg oeffnen."""
        assert "id" not in CustomerCreate.model_fields
        assert "id" not in CustomerUpdate.model_fields

    def test_create_validiert_den_mandanten_weiterhin(self):
        with pytest.raises(ValidationError):
            CustomerCreate(company_name="Musterhof", customer_number="KD-1", tenant_id="kein-mandant")
