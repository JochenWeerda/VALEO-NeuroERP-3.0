"""Explicit tenant administration; preserve every journal entry before deletion."""
from __future__ import annotations
import json
from app.core.uuid7 import uuid7
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.identity_context import current_identity
from app.core.identity_session import block_tenant
from app.infrastructure.models import Tenant
from app.infrastructure.models.journal import JournalEntry
from app.infrastructure.eventbus.outbox import OutboxEvent


class TenantLifecycleService:
    def __init__(self, db: Session):
        self.db=db
        self.principal=current_identity()

    def authorize(self,target_id: str | None=None,*,write: bool=False,platform: bool=False):
        p=self.principal
        elevated=p.claims.get('identity_type')=='human' and 'platform:tenants:manage' in p.scopes
        if platform or (target_id is not None and target_id!=p.tenant_id):
            if not elevated: raise HTTPException(403,'Ausdrückliche Plattformberechtigung erforderlich')
        if write and not elevated and (p.claims.get('identity_type')!='human' or 'admin' not in p.roles):
            raise HTTPException(403,'Mandantenadministration erforderlich')
        return elevated

    def get(self,target_id: str,*,write: bool=False) -> Tenant:
        self.authorize(target_id,write=True)
        query=self.db.query(Tenant).filter(Tenant.id==target_id)
        if write: query=query.with_for_update()
        row=query.first()
        if row is None: raise HTTPException(404,'Mandant nicht gefunden')
        return row

    def list(self,skip: int,limit: int):
        elevated=self.authorize(write=True)
        query=self.db.query(Tenant)
        if not elevated: query=query.filter(Tenant.id==self.principal.tenant_id)
        return query.order_by(Tenant.id).offset(skip).limit(limit).all(),query.count()

    def record(self,row: Tenant,event: str,reason: str=''):
        self.db.add(OutboxEvent(id=uuid7(),event_type='identity.tenant.'+event,
            aggregate_id=row.id,tenant_id=row.id,payload=json.dumps(dict(
                actor=self.principal.subject,actor_tenant=self.principal.tenant_id,
                target_id=row.id,reason=reason,event=event))))

    def commit(self):
        try: self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(409,'Mandant besitzt referenzierte Daten oder widersprüchliche Stammdaten') from exc
        except Exception:
            self.db.rollback()
            raise

    def create(self,values: dict) -> Tenant:
        self.authorize(write=True,platform=True)
        row=Tenant(id=uuid7(),**values,is_active=True)
        self.db.add(row)
        self.record(row,'created')
        self.commit()
        self.db.refresh(row)
        return row

    def update(self,target_id: str,values: dict) -> Tenant:
        row=self.get(target_id,write=True)
        for field in ('name','domain','settings'):
            if field in values:
                if values[field] is None: raise HTTPException(422,'Pflichtwert darf nicht gelöscht werden')
                setattr(row,field,values[field])
        self.record(row,'updated')
        self.commit()
        self.db.refresh(row)
        return row

    def block(self,target_id: str,reason: str) -> Tenant:
        row=self.get(target_id,write=True)
        block_tenant(target_id,actor=self.principal.subject)
        row.is_active=False
        self.record(row,'blocked',reason)
        self.commit()
        self.db.refresh(row)
        return row

    def delete(self,target_id: str,reason: str) -> None:
        row=self.get(target_id,write=True)
        # FOR UPDATE conflicts with the FK key-share lock of concurrent journal
        # inserts. All entries (including drafts and reversals) prevent deletion.
        if self.db.query(JournalEntry.id).filter(JournalEntry.tenant_id==target_id).first() is not None:
            raise HTTPException(409,'Mandant besitzt Buchungen. Nur Sperren ist möglich.')
        self.record(row,'deleted',reason)
        self.db.delete(row)
        # Validate protected references before emitting a persistent deny marker.
        # The delete remains uncommitted and the tenant row lock remains held.
        try:
            self.db.flush()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(409,'Mandant besitzt geschützte Referenzen. Nur Sperren ist möglich.') from exc
        try:
            block_tenant(target_id,actor=self.principal.subject)
        except Exception:
            self.db.rollback()
            raise
        self.commit()
