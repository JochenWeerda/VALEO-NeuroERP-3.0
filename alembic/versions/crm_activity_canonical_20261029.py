"""Unify the existing domain_crm.activities aggregate; preserve source provenance.

Revision ID: crm_activity_canon_20261029
Revises: rls_domain_shared_20261027
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision="crm_activity_canon_20261029"
down_revision="rls_domain_shared_20261027"
branch_labels=None
depends_on=None

_TYPES={"anruf":"call","besuch":"visit","e-mail":"email","aufgabe":"task","sonstiges":"note",
        "call":"call","visit":"visit","email":"email","task":"task","note":"note","meeting":"meeting"}
_STATUS={"offen":"planned","overdue":"planned","planned":"planned","completed":"completed","erledigt":"completed",
         "cancelled":"cancelled","abgesagt":"cancelled","storniert":"cancelled"}


def _normalized(value, choices):
    try:return choices[str(value).strip().casefold()]
    except KeyError as error:raise RuntimeError("Unknown legacy CRM activity classification; resolve before migration") from error


def _table(bind,schema,name):
    return sa.Table(name,sa.MetaData(),schema=schema,autoload_with=bind) if sa.inspect(bind).has_table(name,schema=schema) else None


def _name(bind,table,record_id,tenant,field):
    if not record_id:return ""
    if table is None:raise RuntimeError("Missing legacy CRM reference table")
    row=bind.execute(sa.select(table).where(table.c.id==record_id)).mappings().first()
    if row is None or ("tenant_id" in row and str(row["tenant_id"])!=tenant):
        raise RuntimeError("Invalid or foreign legacy CRM reference")
    if field=="full_name":return " ".join(str(row[k] or "") for k in ("first_name","last_name")).strip()
    return str(row[field] or "")


def upgrade():
    bind=op.get_bind()
    original_columns={item["name"] for item in sa.inspect(bind).get_columns("activities",schema="domain_crm")}
    for name,column in {
        "customer_id":sa.Column("customer_id",sa.String(64)),
        "contact_id":sa.Column("contact_id",sa.String(64)),
        "version":sa.Column("version",sa.Integer(),nullable=False,server_default="1"),
        "main_topics":sa.Column("main_topics",sa.JSON(),nullable=False,server_default=sa.text("'[]'::jsonb")),
        "orders_placed":sa.Column("orders_placed",sa.JSON(),nullable=False,server_default=sa.text("'[]'::jsonb")),
        "follow_up_actions":sa.Column("follow_up_actions",sa.JSON(),nullable=False,server_default=sa.text("'[]'::jsonb")),
        "origin":sa.Column("origin",sa.JSON(),nullable=False,server_default=sa.text("'{}'::jsonb")),
        "created_by":sa.Column("created_by",sa.String(120)),
        "updated_by":sa.Column("updated_by",sa.String(120)),
    }.items():
        # PostgreSQL JSONB is the canonical storage; JSON API values remain bounded arrays.
        if isinstance(column.type,sa.JSON):column.type=postgresql.JSONB()
        op.add_column("activities",column,schema="domain_crm")
    op.alter_column("activities","date",nullable=True,schema="domain_crm")
    target=_table(bind,"domain_crm","activities")
    tenants=_table(bind,"domain_shared","tenants")
    tenant_ids={str(value) for value in bind.execute(sa.select(tenants.c.id)).scalars()}
    for row in bind.execute(sa.select(target)).mappings():
        if str(row["tenant_id"]) not in tenant_ids or str(row["tenant_id"]) in {"","default","system"}:raise RuntimeError("CRM activity tenant must be resolved before migration")
        raw={key:row[key] for key in original_columns}
        origin={"source":"domain_crm.activities","record":json.loads(json.dumps(raw,default=str)),
                "sha256":hashlib.sha256(json.dumps(raw,sort_keys=True,default=str).encode()).hexdigest()}
        bind.execute(target.update().where(target.c.id==row["id"]).values(type=_normalized(row["type"],_TYPES),status=_normalized(row["status"],_STATUS),origin=origin))
    contacts=_table(bind,"public","crm_contacts")
    core_customers=_table(bind,"public","crm_core_customers")
    core_contacts=_table(bind,"public","crm_core_contacts")
    for schema,name in (("public","crm_activities"),("public","crm_core_activities"),("domain_crm","crm_activities")):
        source=_table(bind,schema,name)
        if source is None:continue
        # Existing source tables are kept intact until all retired consumers are removed.
        bind.execute(sa.text('LOCK TABLE "'+schema+'"."'+name+'" IN ACCESS EXCLUSIVE MODE'))
        for old in bind.execute(sa.select(source)).mappings():
            raw=dict(old);tenant=str(old["tenant_id"])
            if tenant not in tenant_ids or tenant in ("","default","system"):
                raise RuntimeError("Legacy CRM activity has no registered tenant")
            record_id=str(old["id"])
            if bind.execute(sa.select(target.c.id).where(target.c.id==record_id)).first():
                raise RuntimeError("CRM activity ID collision; no source row was overwritten")
            if name=="crm_core_activities":
                customer=_name(bind,core_customers,old["customer_id"],tenant,"display_name")
                person=_name(bind,core_contacts,old["contact_id"],tenant,"full_name")
                # Core contacts inherit their tenant from the core customer.
                if old["contact_id"]:
                    contact=bind.execute(sa.select(core_contacts).where(core_contacts.c.id==old["contact_id"])).mappings().one()
                    _name(bind,core_customers,contact["customer_id"],tenant,"display_name")
                title,date,description=old["title"],old["scheduled_at"],old["description"]
                assigned=old["assigned_to"] or ""
            elif schema=="public":
                person=_name(bind,contacts,old["contact_id"],tenant,"name")
                customer=_name(bind,contacts,old["contact_id"],tenant,"company")
                title,date,description=old["subject"] or "",old["date"],old["notes"]
                assigned=""  # An unverified creator is not an assignee or verified author.
            else:
                customer=person=""
                title,date,description=old["subject"],old["activity_date"],old["description"]
                assigned=old["assigned_to"] or ""
            if not title or len(title)>200 or len(customer)>100 or len(person)>100 or len(assigned)>100:
                raise RuntimeError("Legacy CRM activity exceeds canonical limits; no truncation allowed")
            origin={"source":schema+"."+name,"record":json.loads(json.dumps(raw,default=str)),
                    "sha256":hashlib.sha256(json.dumps(raw,sort_keys=True,default=str).encode()).hexdigest()}
            if isinstance(date,datetime) and date.tzinfo is None:date=date.replace(tzinfo=timezone.utc)
            bind.execute(target.insert().values(id=record_id,tenant_id=tenant,type=_normalized(old.get("type",old.get("activity_type")),_TYPES),
                title=title,customer=customer,contact_person=person,date=date,status=_normalized(old["status"],_STATUS),
                assigned_to=assigned,description=description,created_at=old["created_at"],updated_at=old.get("updated_at"),
                contact_id=str(old["contact_id"]) if schema=="public" and name=="crm_activities" and old["contact_id"] else None,
                origin=origin))
    op.alter_column("activities","tenant_id",nullable=False,schema="domain_crm")
    for parent_schema,parent_table,field,constraint in (("domain_crm","customers","customer_id","fk_activity_customer_tenant"),
                                                       ("public","crm_contacts","contact_id","fk_activity_contact_tenant")):
        unique=sa.inspect(bind).get_unique_constraints(parent_table,schema=parent_schema)
        if not any(item["column_names"]==["id","tenant_id"] for item in unique):
            op.create_unique_constraint("uq_activity_reference_"+parent_table,parent_table,["id","tenant_id"],schema=parent_schema)
        op.create_foreign_key(constraint,"activities",parent_table,[field,"tenant_id"],["id","tenant_id"],
                              source_schema="domain_crm",referent_schema=parent_schema,ondelete="RESTRICT")
    op.create_check_constraint("ck_activity_version_positive","activities","version >= 1",schema="domain_crm")
    op.create_check_constraint("ck_activity_status","activities","status IN ('planned','completed','cancelled')",schema="domain_crm")
    op.create_check_constraint("ck_activity_type","activities","type IN ('meeting','call','email','note','visit','task')",schema="domain_crm")
    op.create_index("ix_activities_tenant_date_id","activities",["tenant_id","date","id"],schema="domain_crm")


def downgrade():
    # Destructive data/model downgrades are not silent rollback procedures.
    raise RuntimeError("CRM activity unification requires restore from the pre-migration backup for downgrade")
