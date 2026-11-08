"""Tenant-bound domain commands and immutable harvest settlement evidence."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext
from hashlib import sha256
import json
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import text

from app.auth.deps import require_roles
from app.auth.finance_roles import beleg_read, beleg_write, finance_admin
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.infrastructure.models import (AgrarContract, Article, HarvestAcceptance,
    HarvestAcceptancePosition, QualityProtocol, WeighingTicket)
from modules.agrar.contracts.harvest_deductions_v1 import HarvestDeductionRuleV1

rule_approver = require_roles("EINKAUF_ADMIN", "FINANCE_ADMIN", "admin")
_TABLE = "domain_inventory.harvest_control_events"


def canonical(value):
    def encode(item):
        if isinstance(item, Decimal):
            if item == 0:
                return "0"
            with localcontext() as context:
                context.prec = max(context.prec, len(item.as_tuple().digits))
                return str(item.normalize())
        if hasattr(item, "isoformat"):
            return item.isoformat()
        if isinstance(item, UUID):
            return str(item)
        raise TypeError("Unsupported evidence value")
    return json.loads(json.dumps(value, default=encode, sort_keys=True, allow_nan=False))


def digest(value):
    return sha256(json.dumps(canonical(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def engine_hash():
    root = Path(__file__).resolve().parents[3]
    files = ["modules/agrar/services/harvest_rule_store.py", "app/services/harvest_acceptance_service.py",
             "modules/agrar/services/harvest_calculator.py", "modules/agrar/services/moisture_engine.py",
             "modules/agrar/contracts/harvest_deductions_v1.py", "modules/agrar/contracts/harvest_control_v1.py",
             "app/repositories/drying_rule_repository.py"]
    result = sha256()
    for name in files:
        result.update(name.encode()); result.update((root / name).read_bytes())
    return result.hexdigest()


class HarvestRuleStore:
    """A trusted server dependency; no command accepts a tenant/actor override."""
    def __init__(self, db, tenant_id, principal):
        self.db, self.tenant_id, self.principal = db, tenant_id, dict(principal)
        subject = self.principal.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise ValidationFailedError("Gepruefter Urheber fehlt.")
        self._subject = subject.strip()
        raw = self.principal.get("raw") or {}
        issuer = raw.get("iss")
        if not isinstance(issuer, str) or not issuer.strip():
            raise ValidationFailedError("Gepruefter Identitaetsaussteller fehlt.")
        self.identity = {"subject": self._subject, "issuer": issuer,
                         "agent_id": raw.get("agent_id"), "client_id": raw.get("azp"),
                         "identity_type": raw.get("identity_type")}
        self.identity_key = digest({"issuer": issuer, "subject": self._subject})

    @property
    def actor(self):
        return self._subject

    def _lock(self, key, *, shared=False):
        statement = ("SELECT pg_advisory_xact_lock_shared(hashtextextended(:key,0))" if shared
                     else "SELECT pg_advisory_xact_lock(hashtextextended(:key,0))")
        self.db.execute(text(statement), {"key": "harvest-control:" + self.tenant_id + ":" + key})

    def _event(self, event_id, kind=None):
        row = self.db.execute(text(f"SELECT * FROM {_TABLE} WHERE tenant_id=:tenant AND id=:id"),
                              {"tenant": self.tenant_id, "id": str(event_id)}).mappings().first()
        if row is None or (kind is not None and row["kind"] != kind):
            raise EntityNotFoundError("HarvestControlEvent", str(event_id))
        if row["payload"].get("schema_version") != 1:
            raise ValidationFailedError("Unbekannte Nachweisversion.")
        return row

    def _latest(self, aggregate, kinds, *, target=None):
        condition = " AND payload->'result'->>'rule_version_id'=:target" if target else ""
        return self.db.execute(text(f"SELECT * FROM {_TABLE} WHERE tenant_id=:tenant "
            f"AND aggregate_id=:aggregate AND kind=ANY(:kinds){condition} ORDER BY event_no DESC LIMIT 1"),
            {"tenant": self.tenant_id, "aggregate": aggregate, "kinds": list(kinds), "target": target}).mappings().first()

    def _run(self, kind, aggregate, body, operation):
        beleg_write(user=self.principal)
        actor = self.identity_key
        request_hash = digest({"kind": kind, "aggregate": aggregate, "body": body.model_dump(mode="json")})
        key = str(body.idempotency_key)
        with self.db.begin_nested():
            self._lock("request:" + key)
            existing = self.db.execute(text(f"SELECT * FROM {_TABLE} WHERE tenant_id=:tenant AND idempotency_key=:key"),
                                       {"tenant": self.tenant_id, "key": key}).mappings().first()
            if existing:
                if existing["actor"] != actor or existing["kind"] != kind or existing["request_hash"] != request_hash:
                    raise ConflictError("Idempotenzschluessel bereits fuer einen anderen Auftrag verwendet.")
                result = existing["payload"]["result"]
            else:
                self._lock(aggregate)
                event_id = str(uuid4())
                result = canonical(operation(event_id))
                self.db.execute(text(f"INSERT INTO {_TABLE} "
                    "(id,tenant_id,aggregate_id,kind,actor,idempotency_key,request_hash,payload) "
                    "VALUES (:id,:tenant,:aggregate,:kind,:actor,:key,:hash,CAST(:payload AS jsonb))"),
                    {"id": event_id, "tenant": self.tenant_id, "aggregate": aggregate, "kind": kind,
                     "actor": actor, "key": key, "hash": request_hash,
                     "payload": json.dumps({"schema_version": 1, "identity": self.identity,
                                            "authorized_roles": sorted(self.principal.get("roles") or []),
                                            "correlation_id": key, "result": result}, allow_nan=False)})
        self.db.commit()
        return result

    def _acceptance(self, acceptance_id, *, locked=True):
        query = self.db.query(HarvestAcceptance).filter(
            HarvestAcceptance.tenant_id == self.tenant_id, HarvestAcceptance.id == acceptance_id).populate_existing()
        if locked:
            query = query.with_for_update().populate_existing()
        obj = query.first()
        if obj is None:
            raise EntityNotFoundError("HarvestAcceptance", acceptance_id)
        return obj

    def _editable(self, obj):
        if obj.release_status not in {"draft", "provisional"} or obj.invoice_id:
            raise ConflictError("Festgeschriebene Annahme ist nicht mehr bearbeitbar.")

    def _reference(self, model, reference, *, locked=True):
        if not reference:
            return None
        query = self.db.query(model).filter(model.tenant_id == self.tenant_id, model.id == reference).populate_existing()
        if locked:
            query = query.with_for_update().populate_existing()
        row = query.first()
        if row is None:
            raise ValidationFailedError("Referenz liegt nicht im autorisierten Mandanten.")
        return row

    def _rule(self, version_id):
        event = self._event(version_id, "rule.created")
        rule = HarvestDeductionRuleV1.model_validate(event["payload"]["result"]["definition"])
        if rule.tenant_id != self.tenant_id or rule.content_hash != event["payload"]["result"]["content_hash"]:
            raise ValidationFailedError("Regelnachweis ist inkonsistent.")
        return event, rule

    def _approved_rule(self, version_id):
        event, rule = self._rule(version_id)
        self._lock("rule:" + rule.rule_id, shared=True)
        decision = self._latest("rule:" + rule.rule_id, ["rule.approved", "rule.revoked"], target=str(version_id))
        if (not decision or decision["kind"] != "rule.approved"
                or decision["actor"] == event["actor"]
                or decision["payload"]["result"]["content_hash"] != rule.content_hash
                or datetime.fromisoformat(decision["payload"]["result"]["expires_at"]) <= datetime.now(UTC)):
            raise ValidationFailedError("Aktuelle Vier-Augen-Genehmigung der Vertragsregel fehlt.")
        return rule, decision

    def _contract_scope(self, rule, delivery_date=None):
        from app.infrastructure.models import Customer
        customer = self._reference(Customer, rule.customer_id)
        contract = self._reference(AgrarContract, rule.contract_id)
        if contract and (contract.partner_id not in {customer.id, customer.business_partner_id}
                or contract.article_id != rule.article_id or contract.status == "cancelled"):
            raise ValidationFailedError("Kontrakt, Partner und Artikel widersprechen sich.")
        if contract and delivery_date and ((contract.valid_from and delivery_date < contract.valid_from.date())
                or (contract.valid_until and delivery_date > contract.valid_until.date())):
            raise ValidationFailedError("Lieferdatum liegt ausserhalb des Kontraktzeitraums.")

    def _match_rule(self, rule, obj):
        try:
            rule.require_scope(tenant_id=self.tenant_id, contract_id=obj.contract_id,
                customer_id=obj.customer_id, article_id=obj.article_id, delivery_date=obj.delivery_date)
        except ValueError as exc:
            raise ValidationFailedError("Vertragsregel passt nicht zur konkreten Annahme.") from exc
        self._contract_scope(rule, obj.delivery_date)

    def create_rule(self, body):
        def create(event_id):
            previous = self._latest("rule:" + body.rule_id, ["rule.created"])
            version = previous["payload"]["result"]["definition"]["rule_version"] if previous else 0
            if version != body.expected_version:
                raise ConflictError("Regelversion wurde zwischenzeitlich geaendert.")
            terms = body.terms.model_dump()
            for model, field in [(AgrarContract, "contract_id"), (Article, "article_id")]:
                self._reference(model, terms.get(field))
            from app.infrastructure.models import Customer
            self._reference(Customer, terms["customer_id"])
            rule = HarvestDeductionRuleV1(**terms, rule_id=body.rule_id,
                                         rule_version=version + 1, tenant_id=self.tenant_id)
            self._contract_scope(rule)
            return {"id": event_id, "definition": rule.model_dump(mode="json"), "content_hash": rule.content_hash,
                    "created_by": self.actor, "status": "draft"}
        return self._run("rule.created", "rule:" + body.rule_id, body, create)

    def decide_rule(self, version_id, body, *, revoke=False):
        rule_approver(user=self.principal)
        self._human_approver()
        original, rule = self._rule(version_id)
        def decide(event_id):
            if body.expected_hash != rule.content_hash:
                raise ConflictError("Regelinhalt entspricht nicht der geprueften Fassung.")
            if not revoke and original["actor"] == self.identity_key:
                raise ValidationFailedError("Regelautor darf die eigene Regel nicht genehmigen.")
            expires = None if revoke else self._expiry(body.expires_at, max_age=timedelta(days=366))
            if expires and expires.date() > rule.valid_until:
                raise ValidationFailedError("Genehmigung darf den Regelzeitraum nicht verlaengern.")
            return {"id": event_id, "rule_version_id": str(version_id), "content_hash": rule.content_hash,
                    "expires_at": expires, "reason": body.reason, "decision": "revoked" if revoke else "approved"}
        return self._run("rule.revoked" if revoke else "rule.approved", "rule:" + rule.rule_id, body, decide)

    @staticmethod
    def _expiry(value, *, max_age=timedelta(hours=24)):
        if value is None or value.tzinfo is None or value <= datetime.now(UTC):
            raise ValidationFailedError("Eine zukuenftige Genehmigungsfrist mit Zeitzone ist erforderlich.")
        if value > datetime.now(UTC) + max_age:
            raise ValidationFailedError("Genehmigungsfrist ueberschreitet die technische Freigaberichtlinie.")
        return value.astimezone(UTC)

    def _human_approver(self):
        if self.identity.get("identity_type") != "human":
            raise ValidationFailedError("Diese Genehmigung erfordert eine gepruefte menschliche Identitaet.")

    def list_rules(self, *, offset=0, limit=25):
        beleg_read(user=self.principal)
        if not 0 <= offset or not 1 <= limit <= 100:
            raise ValidationFailedError("Ungueltige Seitengroesse.")
        rows = self.db.execute(text(f"SELECT id, actor, recorded_at, payload FROM {_TABLE} "
            "WHERE tenant_id=:tenant AND kind='rule.created' ORDER BY event_no DESC LIMIT :limit OFFSET :offset"),
            {"tenant": self.tenant_id, "limit": limit, "offset": offset}).mappings().all()
        count = self.db.execute(text(f"SELECT count(*) FROM {_TABLE} WHERE tenant_id=:tenant AND kind='rule.created'"),
                                {"tenant": self.tenant_id}).scalar_one()
        decisions = self.db.execute(text(f"SELECT DISTINCT ON (payload->'result'->>'rule_version_id') "
            f"payload,kind FROM {_TABLE} WHERE tenant_id=:tenant AND kind=ANY(:kinds) "
            "AND payload->'result'->>'rule_version_id'=ANY(:ids) "
            "ORDER BY payload->'result'->>'rule_version_id',event_no DESC"),
            {"tenant": self.tenant_id, "kinds": ["rule.approved", "rule.revoked"],
             "ids": [row["id"] for row in rows]}).mappings().all() if rows else []
        statuses = {}
        for row in decisions:
            value = row["payload"]["result"]
            statuses[value["rule_version_id"]] = ("revoked" if row["kind"] == "rule.revoked" else
                "approved" if datetime.fromisoformat(value["expires_at"]) > datetime.now(UTC) else "expired")
        return {"items": [dict(row["payload"]["result"], status=statuses.get(row["id"], "draft"),
                               actor=row["payload"]["identity"]["subject"], recorded_at=row["recorded_at"]) for row in rows], "total": count}

    def choices(self, kind, query, limit):
        beleg_read(user=self.principal)
        from app.infrastructure.models import Customer
        sources = {"acceptance": (HarvestAcceptance, HarvestAcceptance.acceptance_number),
                   "customer": (Customer, Customer.company_name), "article": (Article, Article.name),
                   "contract": (AgrarContract, AgrarContract.contract_number)}
        if kind not in sources or len(query.strip()) < 2 or not 1 <= limit <= 25:
            raise ValidationFailedError("Suchbegriff oder Auswahlart ungueltig.")
        model, label = sources[kind]
        rows = self.db.query(model).filter(model.tenant_id == self.tenant_id,
            (label.ilike("%" + query.strip() + "%")) | (model.id == query.strip())).order_by(label, model.id).limit(limit).all()
        return {"items": [{"value": row.id, "label": getattr(row, label.key) or row.id} for row in rows]}

    def history(self, acceptance_id, *, offset=0, limit=25):
        beleg_read(user=self.principal)
        self._acceptance(acceptance_id, locked=False)
        if offset < 0 or not 1 <= limit <= 100:
            raise ValidationFailedError("Ungueltige Seitengroesse.")
        rows = self.db.execute(text(f"SELECT id,kind,actor,recorded_at,payload FROM {_TABLE} "
            "WHERE tenant_id=:tenant AND aggregate_id=:aggregate ORDER BY event_no DESC LIMIT :limit OFFSET :offset"),
            {"tenant": self.tenant_id, "aggregate": "acceptance:" + acceptance_id, "limit": limit, "offset": offset}).mappings().all()
        total = self.db.execute(text(f"SELECT count(*) FROM {_TABLE} WHERE tenant_id=:tenant AND aggregate_id=:aggregate"),
            {"tenant": self.tenant_id, "aggregate": "acceptance:" + acceptance_id}).scalar_one()
        return {"items": [{"id": row["id"], "action": row["kind"], "actor": row["payload"]["identity"]["subject"],
            "issuer": row["payload"]["identity"]["issuer"], "recorded_at": row["recorded_at"],
            "calculation_hash": row["payload"]["result"].get("calculation_hash"),
            "rule_version_id": row["payload"]["result"].get("rule_version_id")} for row in rows], "total": total}

    def _protocol(self, obj, *, locked=True):
        protocol = self._reference(QualityProtocol, obj.quality_protocol_id, locked=locked)
        if protocol and protocol.harvest_acceptance_id != obj.id:
            raise ValidationFailedError("Messprotokoll gehoert nicht zu dieser Annahme.")
        if protocol is None:
            return None, None
        keys = ["id", "tenant_id", "harvest_acceptance_id", "protocol_number", "version", "moisture_pct",
                "impurities_pct", "hl_weight_kg_per_hl", "protein_pct", "mycotoxin_ppb", "other_values",
                "source_type", "source_device_id", "source_file_name", "is_final", "approved_by", "approved_at"]
        snapshot = {key: getattr(protocol, key) for key in keys}
        snapshot["source_file_hash"] = sha256((protocol.source_file_content or "").encode()).hexdigest()
        return protocol, canonical(snapshot)

    def context(self, acceptance_id, *, locked=False):
        beleg_read(user=self.principal)
        if engine_hash() != _LOADED_ENGINE_HASH:
            raise ConflictError("Abrechnungsdienst muss nach Codeaenderung neu gestartet werden.")
        obj = self._acceptance(acceptance_id, locked=locked)
        acceptance = {key: getattr(obj, key) for key in ["id", "tenant_id", "customer_id", "contract_id",
            "article_id", "warehouse_id", "weighing_ticket_id", "quality_protocol_id", "delivery_date",
            "pricing_mode", "acceptance_mode", "ownership_type"]}
        sources = {}
        from app.infrastructure.models import Customer
        customer = self._reference(Customer, obj.customer_id, locked=locked)
        sources["customer"] = {"id": customer.id, "business_partner_id": customer.business_partner_id}
        for name, model, reference, keys in [
            ("ticket", WeighingTicket, obj.weighing_ticket_id, ["id", "gross_weight", "tare_weight", "net_weight", "moisture_pct", "impurities_pct", "hl_weight"]),
            ("article", Article, obj.article_id, ["id", "sales_price", "mehrwertsteuer_prozent", "warengruppe"]),
            ("contract", AgrarContract, obj.contract_id, ["id", "partner_id", "article_id", "pricing_model", "fixed_price", "valid_from", "valid_until", "status"]),
        ]:
            row = self._reference(model, reference, locked=locked)
            sources[name] = {key: getattr(row, key) for key in keys} if row else None
        protocol, snapshot = self._protocol(obj, locked=locked)
        sources["accounting"] = self._accounting_context(customer, locked=locked)
        binding = self._latest("acceptance:" + acceptance_id, ["rule.bound"])
        attestation = self._latest("acceptance:" + acceptance_id, ["measurement.attested"])
        decision = None
        if binding:
            _, rule = self._rule(binding["payload"]["result"]["rule_version_id"])
            decision = self._latest("rule:" + rule.rule_id, ["rule.approved", "rule.revoked"],
                                    target=binding["payload"]["result"]["rule_version_id"])
        positions = self.db.query(HarvestAcceptancePosition).filter(
            HarvestAcceptancePosition.harvest_acceptance_id == acceptance_id).order_by(HarvestAcceptancePosition.position_number).all()
        inputs = [{"position": p.position_number, "value": p.lab_value_pct if p.position_number in [15, 63] else p.amount_eur}
                  for p in positions if p.position_number in [15, 63, 75, 78, 80]]
        state = canonical({"acceptance": acceptance, "sources": sources, "protocol": snapshot, "inputs": inputs,
            "binding_id": binding["id"] if binding else None, "attestation_id": attestation["id"] if attestation else None,
            "rule_decision_id": decision["id"] if decision else None, "engine_hash": engine_hash()})
        calculation = self._latest("acceptance:" + acceptance_id, ["calculation.completed"])
        approval = self._latest("acceptance:" + acceptance_id, ["calculation.approved"])
        issues = []
        if not binding: issues.append("Genehmigte Regelversion an Annahme binden.")
        if binding and (not decision or decision["kind"] != "rule.approved" or
                       datetime.fromisoformat(decision["payload"]["result"]["expires_at"]) <= datetime.now(UTC)):
            issues.append("Aktuelle Regelgenehmigung fehlt oder ist abgelaufen.")
        if not attestation: issues.append("Messnachweis bestaetigen.")
        elif attestation["payload"]["result"]["protocol_hash"] != digest(snapshot):
            issues.append("Messprotokoll wurde nach Bestaetigung geaendert.")
        if binding:
            try:
                rule.require_scope(tenant_id=self.tenant_id, contract_id=obj.contract_id,
                    customer_id=obj.customer_id, article_id=obj.article_id, delivery_date=obj.delivery_date)
            except ValueError:
                issues.append("Regelbereich passt nicht mehr zur Annahme.")
            if attestation and ((attestation["payload"]["result"]["measurement_method"],
                                 attestation["payload"]["result"]["measurement_method_version"])
                                != (rule.measurement_method, rule.measurement_method_version)):
                issues.append("Untersuchungsmethode passt nicht zur Regel.")
        current_calculation = bool(calculation and calculation["payload"]["result"]["context_hash"] == digest(state)
            and calculation["payload"]["result"]["projection_hash"] == digest(self._projection(acceptance_id)))
        return {"context_hash": digest(state), "state": state, "protocol_hash": digest(snapshot) if snapshot else None,
                "release_status": obj.release_status, "issues": issues, "calculation_current": current_calculation,
                "rule_version_id": binding["payload"]["result"]["rule_version_id"] if binding else None,
                "calculation_hash": calculation["payload"]["result"]["calculation_hash"] if calculation else None,
                "calculation_result": calculation["payload"]["result"]["result"] if calculation else None,
                "calculation_id": calculation["id"] if calculation else None,
                "calculation_approval": approval["payload"]["result"] if approval else None}

    def _accounting_context(self, customer, *, locked):
        from app.finance.steuerschluessel import KONTENRAHMEN_SCHLUESSEL, KREDITORENKONTO
        suffix = " FOR SHARE" if locked else ""
        properties = self.db.execute(text("SELECT property_key,property_value FROM domain_shared.system_properties "
            "WHERE tenant_id=:tenant AND property_key=ANY(:keys) ORDER BY property_key" + suffix),
            {"tenant": self.tenant_id, "keys": ["agrar.self_billing.tax_code", KONTENRAHMEN_SCHLUESSEL]}).mappings().all()
        props = {row["property_key"]: row["property_value"] for row in properties}
        key = self.db.execute(text("SELECT code,steuersatz,debit_account,expense_account,reverse_charge,credit_account,"
            "active,gueltig_von,gueltig_bis FROM domain_erp.tax_keys WHERE tenant_id=:tenant AND code=:code" + suffix),
            {"tenant": self.tenant_id, "code": props.get("agrar.self_billing.tax_code")}).mappings().first()
        numbers = [KREDITORENKONTO.get(props.get(KONTENRAHMEN_SCHLUESSEL))]
        if key: numbers.extend([key["debit_account"], key["expense_account"]])
        accounts = self.db.execute(text("SELECT id,account_number,is_active,is_summary,deleted_at "
            "FROM domain_erp.chart_of_accounts WHERE tenant_id=:tenant AND account_number=ANY(:numbers) "
            "ORDER BY account_number" + suffix),
            {"tenant": self.tenant_id, "numbers": [n for n in numbers if n]}).mappings().all()
        profiles = self.db.execute(text("SELECT id,supplier_id,taxation_type,valid_from,valid_to "
            "FROM domain_crm.supplier_tax_profiles WHERE tenant_id=:tenant AND supplier_id=:supplier "
            "ORDER BY valid_from,id" + suffix),
            {"tenant": self.tenant_id, "supplier": customer.business_partner_id or customer.id}).mappings().all()
        return {"properties": props, "tax_key": dict(key) if key else None,
                "accounts": [dict(row) for row in accounts], "supplier_tax_profiles": [dict(row) for row in profiles]}

    def _expect_context(self, acceptance_id, expected):
        current = self.context(acceptance_id, locked=True)
        if current["context_hash"] != expected:
            raise ConflictError("Eingaben oder Nachweise wurden geaendert; aktuellen Stand neu laden.")
        return current

    def bind_rule(self, acceptance_id, body):
        def bind(event_id):
            obj = self._acceptance(acceptance_id); self._editable(obj)
            self._expect_context(acceptance_id, body.expected_context_hash)
            rule, _ = self._approved_rule(body.rule_version_id)
            self._match_rule(rule, obj)
            return {"id": event_id, "rule_version_id": str(body.rule_version_id), "rule_hash": rule.content_hash}
        return self._run("rule.bound", "acceptance:" + acceptance_id, body, bind)

    def attest(self, acceptance_id, body):
        def attest(event_id):
            obj = self._acceptance(acceptance_id); self._editable(obj)
            self._expect_context(acceptance_id, body.expected_context_hash)
            protocol, snapshot = self._protocol(obj)
            if (protocol is None or protocol.id != body.protocol_id or digest(snapshot) != body.expected_protocol_hash
                    or protocol.impurities_pct is None):
                raise ConflictError("Messprotokoll fehlt, wurde geaendert oder enthaelt keinen Besatzmesswert.")
            for key in ["impurities_pct", "moisture_pct", "hl_weight_kg_per_hl"]:
                value = getattr(protocol, key)
                if value is not None and (not value.is_finite() or value < 0 or (key.endswith("_pct") and value > 100)):
                    raise ValidationFailedError("Messwert ausserhalb des zulaessigen Wertebereichs.")
            return {"id": event_id, "protocol_id": protocol.id, "protocol_hash": digest(snapshot),
                    "snapshot": snapshot, "measurement_method": body.measurement_method,
                    "measurement_method_version": body.measurement_method_version, "source_reference": body.source_reference}
        return self._run("measurement.attested", "acceptance:" + acceptance_id, body, attest)

    def resolve(self, *, tenant_id, acceptance_id):
        if tenant_id != self.tenant_id:
            raise ValidationFailedError("Fremder Resolverkontext.")
        obj = self._acceptance(acceptance_id)
        binding = self._latest("acceptance:" + acceptance_id, ["rule.bound"])
        witness = self._latest("acceptance:" + acceptance_id, ["measurement.attested"])
        if not binding or not witness:
            raise ValidationFailedError("Genehmigte Regelbindung und bestaetigter Messnachweis erforderlich.")
        rule, _ = self._approved_rule(binding["payload"]["result"]["rule_version_id"])
        self._match_rule(rule, obj)
        _, snapshot = self._protocol(obj)
        measurement = witness["payload"]["result"]
        if (digest(snapshot) != measurement["protocol_hash"] or measurement["measurement_method"] != rule.measurement_method
                or measurement["measurement_method_version"] != rule.measurement_method_version):
            raise ValidationFailedError("Messnachweis ist veraltet oder die Untersuchungsmethode passt nicht zur Regel.")
        return rule

    def measurement_values(self, acceptance_id):
        self.resolve(tenant_id=self.tenant_id, acceptance_id=acceptance_id)
        obj = self._acceptance(acceptance_id)
        protocol, _ = self._protocol(obj)
        return {key: getattr(protocol, key) for key in ["impurities_pct", "moisture_pct", "hl_weight_kg_per_hl"]}

    def _projection(self, acceptance_id):
        obj = self._acceptance(acceptance_id)
        totals = {key: getattr(obj, key) for key in ["total_net_amount_eur", "total_vat_amount_eur", "total_gross_amount_eur", "vat_rate_percent"]}
        positions = self.db.query(HarvestAcceptancePosition).filter(
            HarvestAcceptancePosition.harvest_acceptance_id == acceptance_id).order_by(HarvestAcceptancePosition.position_number).all()
        return canonical({"totals": totals, "positions": [{key: getattr(p, key) for key in [
            "position_number", "description", "quantity_kg", "lab_value_pct", "amount_eur", "unit", "calculation_formula"]} for p in positions]})

    def calculate(self, service, acceptance_id, body):
        def calculate(event_id):
            obj = self._acceptance(acceptance_id); self._editable(obj)
            self._expect_context(acceptance_id, body.expected_context_hash)
            trace = {}
            result = service._calculate_settlement(acceptance_id, commit=False, trace=trace)
            self.db.flush()
            current = self.context(acceptance_id, locked=True)
            verify_trace = {}
            repeated = service._calculate_settlement(acceptance_id, persist=False, trace=verify_trace)
            if digest(result) != digest(repeated) or digest(trace) != digest(verify_trace):
                raise ConflictError("Berechnung ist mit ihren gespeicherten Eingaben nicht reproduzierbar.")
            evidence = {"id": event_id, "acceptance_id": acceptance_id, "context_hash": current["context_hash"],
                "state": current["state"], "trace": trace, "result": result, "result_hash": digest(result),
                "projection_hash": digest(self._projection(acceptance_id))}
            evidence["calculation_hash"] = digest(evidence)
            return evidence
        return self._run("calculation.completed", "acceptance:" + acceptance_id, body, calculate)

    def _verified_calculation(self, service, acceptance_id, expected):
        event = self._latest("acceptance:" + acceptance_id, ["calculation.completed"])
        if not event:
            raise ValidationFailedError("Unveraenderlicher Berechnungsnachweis fehlt.")
        proof = event["payload"]["result"]
        if expected != proof["calculation_hash"] or digest({k: v for k, v in proof.items() if k != "calculation_hash"}) != expected:
            raise ConflictError("Die angeforderte Berechnungsfassung ist nicht aktuell.")
        self._expect_context(acceptance_id, proof["context_hash"])
        trace = {}
        result = service._calculate_settlement(acceptance_id, persist=False, trace=trace)
        if (digest(result) != proof["result_hash"] or digest(trace) != digest(proof["trace"])
                or digest(self._projection(acceptance_id)) != proof["projection_hash"]):
            raise ConflictError("Berechnung, Messwerte, Preise oder gespeicherte Positionen wurden geaendert.")
        return event, proof

    def approve_calculation(self, service, acceptance_id, body):
        finance_admin(user=self.principal)
        self._human_approver()
        def approve(event_id):
            obj = self._acceptance(acceptance_id); self._editable(obj)
            original, proof = self._verified_calculation(service, acceptance_id, body.expected_calculation_hash)
            if proof["result"]["total_gross_amount_eur"] <= 0:
                raise ValidationFailedError("Finanzielle Gutschrift erfordert einen positiven Betrag; Korrekturen benoetigen ihren eigenen Prozess.")
            if original["actor"] == self.identity_key:
                raise ValidationFailedError("Berechnungsautor darf die eigene finanzielle Fassung nicht genehmigen.")
            if (any("Qualitaetsgrenze" in w for w in proof["result"]["warnings"])
                    and not body.acknowledge_quality_exception):
                raise ValidationFailedError("Qualitaetsabweichung muss fuer diese Berechnung ausdruecklich bestaetigt werden.")
            return {"id": event_id, "calculation_hash": proof["calculation_hash"],
                    "expires_at": self._expiry(body.expires_at), "reason": body.reason,
                    "acknowledge_quality_exception": body.acknowledge_quality_exception}
        return self._run("calculation.approved", "acceptance:" + acceptance_id, body, approve)

    def release(self, service, acceptance_id, body, *, create_stock_movement=True):
        def release(event_id):
            obj = self._acceptance(acceptance_id); self._editable(obj)
            original, proof = self._verified_calculation(service, acceptance_id, body.expected_calculation_hash)
            approval = self._latest("acceptance:" + acceptance_id, ["calculation.approved"])
            if (not approval or approval["actor"] == original["actor"]
                    or approval["payload"]["result"]["calculation_hash"] != proof["calculation_hash"]
                    or datetime.fromisoformat(approval["payload"]["result"]["expires_at"]) <= datetime.now(UTC)):
                raise ValidationFailedError("Aktionsgebundene finanzielle Vier-Augen-Freigabe fehlt oder ist abgelaufen.")
            result = service._release_acceptance(acceptance_id, "final", create_stock_movement, True,
                                                  self.actor, commit=False)
            return {"id": event_id, "calculation_hash": proof["calculation_hash"], "approval_id": approval["id"],
                    "create_stock_movement": create_stock_movement, "result": result}
        # Include all execution options in the idempotency request fingerprint.
        from pydantic import create_model
        request = create_model("BoundHarvestRelease", __base__=type(body), create_stock_movement=(bool, create_stock_movement))(
            **body.model_dump(), create_stock_movement=create_stock_movement)
        return self._run("release.completed", "acceptance:" + acceptance_id, request, release)


_LOADED_ENGINE_HASH = engine_hash()
