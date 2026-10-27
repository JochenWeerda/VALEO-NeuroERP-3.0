"""Service-Anfragen und ihre Rueckmeldungen liegen in der Datenbank.

Revision ID: service_anfragen_20261027
Revises: vat_return_bearbeiter_20261027

Bis 27.10.2026 hielt ``/service/anfragen`` alles in einem Woerterbuch des Prozesses, vorbelegt mit zwei erfundenen
Anfragen des Mandanten ``default``: Nach jedem Neustart waren angelegte Anfragen weg, jeder Worker hatte einen eigenen
Stand, und ohne Mandantenkopf galt ``default``.

Beide Tabellen gehoeren einem Mandanten (kein Platzhalter, Vorgabe aus dem Kontext) und stehen von Anfang an unter
getrennten Policies je Befehl. Die Rueckmeldung haengt ueber ``(anfrage_id, tenant_id)`` an ihrer Anfrage: FK-Pruefungen
umgehen RLS, nur der Verbundschluessel verhindert einen Verweis auf die Anfrage eines anderen Mandanten.
"""
from __future__ import annotations

from alembic import op

revision = "service_anfragen_20261027"
down_revision = "vat_return_bearbeiter_20261027"
branch_labels = None
depends_on = None

OWN = "tenant_id = public.rls_current_tenant()"
TABELLEN = ("domain_ops.service_anfragen", "domain_ops.service_anfrage_rueckmeldungen")


def _policies(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")
    op.execute(
        """
        CREATE TABLE domain_ops.service_anfragen (
            id               VARCHAR(36)  PRIMARY KEY,
            tenant_id        VARCHAR(120) NOT NULL DEFAULT public.rls_current_tenant()
                             CHECK (tenant_id NOT IN ('', 'default', 'system')),
            nummer           VARCHAR(40)  NOT NULL,
            kunde            VARCHAR(255) NOT NULL,
            betreff          VARCHAR(255) NOT NULL,
            beschreibung     TEXT,
            prioritaet       VARCHAR(10)  NOT NULL DEFAULT 'normal' CHECK (prioritaet IN ('hoch', 'normal', 'niedrig')),
            kategorie        VARCHAR(120),
            status           VARCHAR(20)  NOT NULL DEFAULT 'neu' CHECK (status IN ('neu', 'in-bearbeitung', 'erledigt')),
            datum            DATE         NOT NULL DEFAULT CURRENT_DATE,
            abschluss_grund  TEXT,
            abschluss_notiz  TEXT,
            abgeschlossen_am TIMESTAMPTZ,
            erstellt_von     VARCHAR(100) NOT NULL,
            created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_service_anfragen_nummer UNIQUE (tenant_id, nummer),
            CONSTRAINT uq_service_anfragen_id_tenant UNIQUE (id, tenant_id),
            CONSTRAINT ck_service_anfragen_abschluss CHECK ((status = 'erledigt') = (abgeschlossen_am IS NOT NULL))
        )
        """
    )
    op.execute(
        """
        CREATE TABLE domain_ops.service_anfrage_rueckmeldungen (
            id           VARCHAR(36)  PRIMARY KEY,
            tenant_id    VARCHAR(120) NOT NULL DEFAULT public.rls_current_tenant(),
            anfrage_id   VARCHAR(36)  NOT NULL,
            text         TEXT         NOT NULL,
            bewertet_von VARCHAR(255),
            bewertung    SMALLINT     CHECK (bewertung BETWEEN 1 AND 5),
            erstellt_von VARCHAR(100) NOT NULL,
            created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            CONSTRAINT fk_service_rueckmeldung_anfrage FOREIGN KEY (anfrage_id, tenant_id)
                REFERENCES domain_ops.service_anfragen (id, tenant_id) ON DELETE CASCADE
        )
        """
    )
    op.execute("CREATE INDEX ix_service_rueckmeldungen_anfrage ON domain_ops.service_anfrage_rueckmeldungen (anfrage_id)")
    for table in TABELLEN:
        _policies(table)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_ops.service_anfrage_rueckmeldungen")
    op.execute("DROP TABLE IF EXISTS domain_ops.service_anfragen")
