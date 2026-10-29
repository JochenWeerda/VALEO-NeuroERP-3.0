"""AP review before posting; every adapter uses the same locked transaction.

This review does not replace the central posting approval/consumption policy.
Existing requests without a verified content snapshot must be requested again.
"""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.auth.deps import effective_roles
from app.auth.finance_roles import FINANCE_APPROVAL_ROLES, FINANCE_WRITE_ROLES
from app.core.akteur import gepruefter_akteur, verlange_rolle
from app.core.tenant_binding import checked_tenant
from app.core.ap_approval_status import build_approval_status_response, APPROVAL_STATUS_TO_DOCUMENT_STATUS
from app.core.freigabe import GUELTIGKEIT_STUNDEN
from app.core.uuid7 import uuid7
from app.documents.repository import DocumentRepository
from app.infrastructure.models import AuditLog
from app.services.finance_freigabe import EingangsrechnungFreigabe, verlange_oder_409
from app.core import finance_periods
from app.core.fibu_audit import log_fibu_audit
from app.finance.steuerschluessel import Steuerklaerung
from app.services.finance_eingangsrechnung_buchung import buche_eingangsrechnung, summen
from app.services.freigabe_engine import Vorgang, technisches_konto


class APApprovalWorkflowService:
    def __init__(self, db, tenant_id):
        self.db, self.tenant_id = db, tenant_id
        self.repo = DocumentRepository(db)

    @contextmanager
    def boundary(self):
        try:
            yield
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(503, "AP-Freigabe derzeit nicht verfuegbar") from None

    def _invoice(self, invoice_id, *, lock=False):
        # Lock the shared document first, including requests with no existing row.
        query = """SELECT data FROM documents WHERE doc_type = 'ap_invoice'
            AND doc_number = :id
            AND COALESCE(CAST(data AS jsonb)->>'tenantId', CAST(data AS jsonb)->>'tenant_id') = :t"""
        if lock:
            query += " FOR UPDATE"
        row = self.db.execute(text(query), {"id": invoice_id, "t": self.tenant_id}).first()
        if not row:
            raise HTTPException(404, "AP Invoice not found")
        invoice = json.loads(row[0]) if isinstance(row[0], str) else dict(row[0])
        if invoice.get("tenant_id") not in (None, self.tenant_id):
            raise HTTPException(404, "AP Invoice not found")
        invoice["tenantId"] = self.tenant_id
        return invoice

    def _actor(self, user, *roles):
        actor = gepruefter_akteur(user)
        verlange_rolle(user, *roles)
        raw = user.get("raw")
        if raw is not None and (checked_tenant(raw) != self.tenant_id or raw.get("sub") != actor):
            raise HTTPException(403, "Widerspruechlicher Ausfuehrungskontext")
        if raw is not None:
            from app.auth.oidc import extract_roles
            if effective_roles(user.get("roles")) != effective_roles(extract_roles(raw)):
                raise HTTPException(403, "Widerspruechliche Rollenprojektion")
        return actor

    def editable_invoice(self, invoice_id, user, *, deleting=False):
        with self.boundary():
            self._actor(user, *(FINANCE_APPROVAL_ROLES if deleting else FINANCE_WRITE_ROLES))
            invoice = self._invoice(invoice_id, lock=True)
            allowed = {"ENTWURF", "ABGELEHNT"} if deleting else {
                "ENTWURF", "ZUR_FREIGABE", "TEILWEISE_FREIGEGEBEN", "FREIGEGEBEN", "ABGELEHNT"}
            if invoice.get("status") not in allowed:
                raise HTTPException(409, "Belegstatus erlaubt diese Aenderung nicht")
            return invoice

    def posting_invoice(self, invoice_id, user):
        with self.boundary():
            self._reviewer(user)
            invoice = self._invoice(invoice_id, lock=True)
            if invoice.get("status") != "FREIGEGEBEN":
                raise HTTPException(409, "Beleg ist nicht zur Buchung freigegeben")
            return invoice

    def _fingerprint(self, invoice_id, invoice):
        operational = {"status", "approvalRequestId", "approvedBy", "approvedAt", "semantic_status",
                       "postedBy", "postedAt", "journalEntryId", "steuerPruefgrund"}
        content = {k: v for k, v in invoice.items() if k not in operational and not k.startswith("approval_")}
        record = Vorgang(invoice_id, "purchase_invoice", Decimal("0"), False, inhalt=content)
        return EingangsrechnungFreigabe(self.db, self.tenant_id).abdruck(record, "ap_review")

    def _latest(self, invoice_id, *, lock=False):
        query = """SELECT id, invoice_id, requested_by, required_approvals, applicable_rule, status
            FROM domain_erp.ap_approval_requests WHERE invoice_id = :id AND tenant_id = :t
            ORDER BY created_at DESC, id DESC LIMIT 1"""
        if lock:
            query += " FOR UPDATE"
        return self.db.execute(text(query), {"id": invoice_id, "t": self.tenant_id}).mappings().first()

    @staticmethod
    def _policy(row):
        value = row["applicable_rule"] if row else None
        try:
            return json.loads(value) if isinstance(value, str) else value
        except ValueError:
            return None

    def _valid(self, row, invoice_id, invoice):
        policy = self._policy(row)
        if not isinstance(policy, dict) or policy.get("review_version") != 1:
            return False
        states = {"pending": {"ZUR_FREIGABE"}, "partially_approved": {"TEILWEISE_FREIGEGEBEN"},
                  "approved": {"FREIGEGEBEN", "VERBUCHT", "BEZAHLT"}, "rejected": {"ABGELEHNT"}}
        if invoice.get("status") not in states.get(row["status"], set()):
            return False
        try:
            expires = datetime.fromisoformat(policy["expires_at"])
            if expires.tzinfo is None or policy["fingerprint"] != self._fingerprint(invoice_id, invoice):
                return False
            if invoice.get("status") in {"VERBUCHT", "BEZAHLT"}:
                # An executed review is historical evidence; verify the actual own posting,
                # rather than disabling a legitimate payment when its review window expires.
                return bool(self.db.execute(text("""SELECT id FROM domain_erp.journal_entries
                    WHERE id=:journal AND tenant_id=:t AND reference=:invoice
                      AND source='ap_invoice' AND status='posted'"""),
                    {"journal": invoice.get("journalEntryId"), "t": self.tenant_id, "invoice": invoice_id}).scalar())
            return expires > datetime.now(timezone.utc)
        except (KeyError, TypeError, ValueError):
            return False

    def _response(self, invoice_id, row=None, invoice=None):
        if row is None:
            return build_approval_status_response(invoice_id=invoice_id, tenant_id=self.tenant_id,
                status="not_requested", required_approvals=0, approvals=[], rejections=[], applicable_rule=None)
        records = self.db.execute(text("""SELECT approved_by, action, created_at, comment
            FROM domain_erp.ap_approvals WHERE request_id = :id AND tenant_id = :t
            ORDER BY created_at, id"""), {"id": row["id"], "t": self.tenant_id}).mappings().all()
        decisions = {name: [{"approved_by": r["approved_by"],
            "approved_at": r["created_at"].isoformat(), "comment": r["comment"]}
            for r in records if r["action"] == name] for name in ("approve", "reject")}
        response = build_approval_status_response(invoice_id=invoice_id, tenant_id=self.tenant_id,
            approval_request_id=str(row["id"]), status=row["status"],
            required_approvals=row["required_approvals"], approvals=decisions["approve"],
            rejections=decisions["reject"], applicable_rule=self._policy(row))
        response.can_post = response.can_post and (invoice or {}).get("status") == "FREIGEGEBEN"
        response.can_pay = response.can_pay and (invoice or {}).get("status") == "VERBUCHT"
        return response

    def status(self, invoice_id, user=None):
        with self.boundary():
            invoice = self._invoice(invoice_id)
            row = self._latest(invoice_id)
            valid = self._valid(row, invoice_id, invoice)
            response = self._response(invoice_id, row if valid else None, invoice)
            if not isinstance(user, dict):
                from app.core.identity_context import current_identity
                try:
                    principal = current_identity()
                    user = {"sub": principal.subject, "roles": list(principal.roles), "raw": dict(principal.claims)}
                except HTTPException:
                    user = None
            if valid and row["status"] in {"pending", "partially_approved"} and user is not None:
                try:
                    actor = self._reviewer(user)
                    self._policy_actor(actor, user, row, invoice)
                    voted = response.approvals + response.rejections
                    response.can_decide = not any(vote["approved_by"] == actor for vote in voted)
                except HTTPException:
                    response.can_decide = False
            if invoice.get("status") in {"VERBUCHT", "BEZAHLT", "STORNIERT"}:
                response.can_post = False
            if invoice.get("status") in {"BEZAHLT", "STORNIERT"}:
                response.can_pay = False
            return response

    def _audit(self, invoice_id, actor, action, row, user):
        from app.core.logging import get_correlation_id
        correlation = get_correlation_id()
        raw = user.get("raw") or {}
        self.db.add(AuditLog(id=str(uuid7()), timestamp=datetime.now(timezone.utc), tenant_id=self.tenant_id,
            user_id=actor, user_email="", action=action, entity_type="ap_invoice_approval", entity_id=invoice_id,
            correlation_id=correlation if len(correlation) <= 50 else None,
            changes={"approval_request_id": str(row["id"]), "status": row["status"],
                     "review_policy": self._policy(row), "agent_id": raw.get("agent_id"),
                     "correlation_id": correlation}))

    @staticmethod
    def _matches(condition, invoice):
        field, op, value = condition["field"], condition["operator"], condition["value"]
        if field == "amount":
            actual = Decimal(str(invoice.get("totalGross", 0)))
            if not actual.is_finite() or actual < 0:
                raise HTTPException(409, "Rechnungsbetrag muss geprueft werden")
            value = [Decimal(str(v)) for v in value] if op == "in" else Decimal(str(value))
        else:
            actual = invoice.get("materialGroup", "") if field == "material_group" else (
                invoice.get("supplierId") or invoice.get("customerId", ""))
        if op == "in":
            return actual in value
        return {"gt": lambda: actual > value, "gte": lambda: actual >= value,
            "lt": lambda: actual < value, "lte": lambda: actual <= value,
            "eq": lambda: actual == value}[op]()

    def request(self, payload, user, rules):
        with self.boundary():
            actor = self._actor(user, *FINANCE_WRITE_ROLES)
            invoice = self._invoice(payload.invoice_id, lock=True)
            if invoice.get("status") not in {"ENTWURF", "ZUR_FREIGABE", "TEILWEISE_FREIGEGEBEN", "ABGELEHNT", "FREIGEGEBEN"}:
                raise HTTPException(409, "Belegstatus erlaubt keine neue Freigabeanfrage")
            try:
                amount = Decimal(str(invoice.get("totalGross", 0)))
                if not amount.is_finite() or amount < 0:
                    raise ValueError
            except (ArithmeticError, TypeError, ValueError):
                raise HTTPException(409, "Rechnungsbetrag muss geprueft werden") from None
            previous = self._latest(payload.invoice_id, lock=True)
            if self._valid(previous, payload.invoice_id, invoice):
                return self._response(payload.invoice_id, previous, invoice)
            from app.api.v1.schemas.ap_approval_workflow_schemas import ApprovalRuleCreate
            applicable = None
            for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
                # Old/invalid policies do not silently become a more permissive fallback.
                try:
                    checked = ApprovalRuleCreate.model_validate(rule.model_dump(exclude={"id", "created_at", "updated_at"}))
                except ValueError:
                    raise HTTPException(409, "Freigaberegel muss auf gueltige Fachrollen und Bedingungen umgestellt werden") from None
                if all(self._matches(c.model_dump(), invoice) for c in checked.conditions):
                    applicable = rule
                    break
            policy = {"id": applicable.id if applicable else "ap.review.default",
                "name": applicable.name if applicable else "Unabhaengige AP-Pruefung",
                "approval_roles": applicable.approval_roles if applicable else list(FINANCE_APPROVAL_ROLES),
                "required_approvals": applicable.required_approvals if applicable else 1,
                "review_version": 1, "fingerprint": self._fingerprint(payload.invoice_id, invoice),
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=GUELTIGKEIT_STUNDEN)).isoformat()}
            row = {"id": str(uuid7()), "invoice_id": payload.invoice_id, "requested_by": actor,
                   "required_approvals": policy["required_approvals"], "applicable_rule": policy, "status": "pending"}
            self.db.execute(text("""INSERT INTO domain_erp.ap_approval_requests
                (id, tenant_id, invoice_id, requested_by, required_approvals, applicable_rule, status, comment, created_at, updated_at)
                VALUES (:id, :t, :invoice_id, :requested_by, :required_approvals, CAST(:policy AS jsonb),
                        'pending', :comment, NOW(), NOW())"""),
                {**{k: row[k] for k in ("id", "invoice_id", "requested_by", "required_approvals")},
                 "t": self.tenant_id, "policy": json.dumps(policy), "comment": payload.comment})
            invoice.update(status="ZUR_FREIGABE", approvalRequestId=row["id"])
            invoice.pop("approvedBy", None)
            invoice.pop("approvedAt", None)
            self.repo.save_document("ap_invoice", payload.invoice_id, invoice, commit=False)
            self._audit(payload.invoice_id, actor, "ap_approval_request", row, user)
            response = self._response(payload.invoice_id, row, invoice)
            self.db.commit()
            return response

    def _reviewer(self, user):
        actor = self._actor(user, *FINANCE_APPROVAL_ROLES)
        if technisches_konto(user):
            raise HTTPException(403, "Eine Freigabe entscheidet nur eine angemeldete Person")
        return actor

    def _policy_actor(self, actor, user, row, invoice):
        if actor in {str(row["requested_by"]), str(invoice.get("createdBy") or ""), str(invoice.get("updatedBy") or "")}:
            raise HTTPException(403, "Wer angelegt, bearbeitet oder angefragt hat, entscheidet nicht selbst")
        policy = self._policy(row)
        roles = set(policy.get("approval_roles") or [])
        if not roles or not roles.issubset(FINANCE_APPROVAL_ROLES):
            raise HTTPException(409, "Freigaberegel enthaelt keine gueltigen Freigaberollen")
        if not effective_roles(user.get("roles")) & roles:
            raise HTTPException(403, "Keine Berechtigung fuer diese Freigaberegel")

    def _decision(self, payload, user, *, lock):
        actor = self._reviewer(user)
        invoice = self._invoice(payload.invoice_id, lock=lock)
        row = self._latest(payload.invoice_id, lock=lock)
        if not row or str(row["id"]) != payload.approval_request_id:
            raise HTTPException(409, "Freigabeanfrage ist nicht mehr aktuell")
        if not self._valid(row, payload.invoice_id, invoice):
            raise HTTPException(409, "Beleg geaendert oder Freigabeanfrage abgelaufen; erneut anfragen")
        self._policy_actor(actor, user, row, invoice)
        previous = self.db.execute(text("""SELECT action FROM domain_erp.ap_approvals
            WHERE request_id = :id AND tenant_id = :t AND approved_by = :actor"""),
            {"id": row["id"], "t": self.tenant_id, "actor": actor}).scalars().all()
        if previous and previous != [payload.action]:
            raise HTTPException(409, "Die Person hat bereits abweichend entschieden")
        if not previous and row["status"] not in {"pending", "partially_approved"}:
            raise HTTPException(409, "Freigabeanfrage ist bereits abgeschlossen")
        if invoice.get("status") in {"VERBUCHT", "BEZAHLT", "STORNIERT"}:
            raise HTTPException(409, "Abgeschlossener Beleg kann nicht freigegeben werden")
        return actor, invoice, dict(row), bool(previous)

    def validate_decision(self, payload, user):
        with self.boundary():
            self._decision(payload, user, lock=False)

    def decide(self, payload, user, *, commit=True):
        with self.boundary():
            actor, invoice, row, repeated = self._decision(payload, user, lock=True)
            if repeated:
                return self._response(payload.invoice_id, row, invoice)
            self.db.execute(text("""INSERT INTO domain_erp.ap_approvals
                (id, tenant_id, request_id, approved_by, action, comment, created_at)
                VALUES (:id, :t, :request_id, :actor, :action, :comment, NOW())"""),
                {"id": str(uuid7()), "t": self.tenant_id, "request_id": row["id"],
                 "actor": actor, "action": payload.action, "comment": payload.comment})
            count = self.db.execute(text("""SELECT count(DISTINCT approved_by) FROM domain_erp.ap_approvals
                WHERE request_id = :id AND tenant_id = :t AND action = 'approve'"""),
                {"id": row["id"], "t": self.tenant_id}).scalar_one()
            row["status"] = "rejected" if payload.action == "reject" else (
                "approved" if count >= row["required_approvals"] else "partially_approved")
            self.db.execute(text("""UPDATE domain_erp.ap_approval_requests SET status = :status, updated_at = NOW()
                WHERE id = :id AND tenant_id = :t"""),
                {"status": row["status"], "id": row["id"], "t": self.tenant_id})
            invoice["status"] = APPROVAL_STATUS_TO_DOCUMENT_STATUS[row["status"]]
            if row["status"] == "approved":
                invoice.update(approvedBy=actor, approvedAt=datetime.now(timezone.utc).isoformat())
            self.repo.save_document("ap_invoice", payload.invoice_id, invoice, commit=False)
            self._audit(payload.invoice_id, actor, "ap_approval_" + payload.action, row, user)
            response = self._response(payload.invoice_id, row, invoice)
            if commit:
                self.db.commit()
            return response

    def post_invoice(self, invoice_id, nutzer, *, commit=True):
        # Bis 13.10.2026 kam der Buchende aus der Anfrage: Jeder konnte unter fremdem Namen buchen.
        posted_by = self._actor(nutzer, *FINANCE_APPROVAL_ROLES)
        db, tenant_id, repo = self.db, self.tenant_id, self.repo
        # Ab hier ist invoice["tenantId"] der gepruefte Mandant.
        invoice = self.posting_invoice(invoice_id, nutzer)

        approval_status = self.status(invoice_id, nutzer)
        if not approval_status.can_post:
            raise HTTPException(status_code=409, detail="Gueltige AP-Freigabe fuer diesen Belegstand erforderlich")

        # FIBU-GL-05: block posting in closed periods
        invoice_date = invoice.get("date", datetime.now().isoformat()[:10])
        period = str(invoice_date)[:7]
        gesperrt = finance_periods.gesperrter_zustand(
            db, invoice.get("tenantId", "system"), period
        )
        if gesperrt:
            raise HTTPException(
                status_code=403,
                detail=finance_periods.meldung(period, gesperrt),
            )

        # Zentrale Freigabe (APPROVAL-001): Eine Finanzrechnung hat keinen Rechnungsabgleich und braucht deshalb die
        # Freigabe einer zweiten Person — zusaetzlich zum Freigabeablauf dieses Moduls.
        freigabe = EingangsrechnungFreigabe(db, tenant_id)
        akteur = str(nutzer.get("sub") or "") if isinstance(nutzer, dict) else None
        try:
            verlange_oder_409(freigabe, freigabe.vorgang_aus(invoice_id, invoice), "post", akteur)
        except HTTPException:
            db.rollback()
            raise
        # Journal, offener Posten und Beleg in einer Transaktion. Scheitert etwas, bleibt die Rechnung freigegeben.
        try:
            je_id, gruppen = buche_eingangsrechnung(
                db, tenant_id, invoice_id=invoice_id, invoice=invoice, posted_by=posted_by)
        except Steuerklaerung as klaerung:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail=f"Eingangsrechnung {invoice.get('number', invoice_id)} nicht gebucht, bitte prüfen: {klaerung}",
            ) from klaerung
        except Exception:
            db.rollback()
            raise
        netto, steuer, brutto = summen(gruppen)
        for key, amount in (("subtotalNet", netto), ("totalTax", steuer), ("totalGross", brutto)):
            if key in invoice and Decimal(str(invoice[key])) != amount:
                db.rollback()
                raise HTTPException(409, "Steuer- oder Betragsgrundlage geaendert; Beleg erneut pruefen und freigeben")
        invoice["subtotalNet"], invoice["totalTax"], invoice["totalGross"] = float(netto), float(steuer), float(brutto)
        invoice["steuerPruefgrund"] = None
        invoice["status"] = "VERBUCHT"
        invoice["postedBy"] = posted_by
        invoice["postedAt"] = datetime.now().isoformat()
        invoice["journalEntryId"] = je_id
        log_fibu_audit(
            db, tenant_id, "create", "journal_entry", je_id,
            {"source": "ap_invoice", "invoice_id": invoice_id},
            request=None, user_id=posted_by, user_email="", commit=False,
        )
        try:
            result = repo.save_document("ap_invoice", invoice_id, invoice, commit=False)
            self._post_event(
                db, tenant_id=tenant_id, invoice_id=invoice_id, posted_by=posted_by, journal_entry_id=je_id,
            )
            if commit:
                db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(503, "Eingangsrechnung nicht gebucht; Speicherung fehlgeschlagen") from None
        return {"status": "ok", "message": "AP Invoice posted", "data": result}

    @staticmethod
    def _post_event(db, *, tenant_id, invoice_id, posted_by, journal_entry_id):
        from dataclasses import asdict
        from app.domains.shared.process_events import APInvoicePosted
        from app.infrastructure.eventbus.outbox import OutboxEvent
        event = APInvoicePosted(aggregate_id=invoice_id, timestamp=datetime.now(timezone.utc),
            tenant_id=tenant_id, workflow_instance_id=f"wf-ap-{invoice_id}", invoice_id=invoice_id,
            posted_by=posted_by, journal_entry_id=journal_entry_id)
        db.add(OutboxEvent(id=event.event_id, event_type=event.__class__.__name__, aggregate_id=invoice_id,
            payload=json.dumps(asdict(event), default=str), timestamp=event.timestamp,
            published=False, tenant_id=tenant_id))
