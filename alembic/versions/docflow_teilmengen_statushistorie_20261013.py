"""DocFlow: mehrere Folgebelege je Quelle, Statushistorie aus der Datenbank.

Revision ID: docflow_teilmengen_statushistorie_20261013
Revises: docflow_steuerschluessel_20261013

**Teilmengen.** ``uq_docflow_header_link_source_relation`` liess je Quellbeleg und Folgeart genau einen
Folgebeleg zu: Aus einem Auftrag entstand ein Lieferschein, nie ein zweiter. Eindeutig ist jetzt das Paar
Quelle/Ziel; wie viel einer Position schon umgewandelt ist, rechnet der Dienst aus ``document_links``.

**Statushistorie.** Der Status stand nur im Kopf und wurde ueberschrieben; das Protokoll war ein
„best effort“-Eintrag ohne Benutzer, dessen Fehler verschluckt wurden. ``document_status_history`` wird von
einem Trigger auf ``document_headers`` geschrieben — in derselben Transaktion wie der Wechsel. Kein Weg, auch
kein rohes SQL, kann den Status aendern, ohne dass der Eintrag entsteht; scheitert der Eintrag, scheitert
der Wechsel. Die Historie laesst sich nicht aendern; loeschen geht nur mit ausdruecklichem Wartungsschalter
(``valeo.docflow_wartung = 'loeschen'``), etwa beim Entfernen eines Mandanten.

Wer und warum: ``actor`` ist ``updated_by`` bzw. ``created_by`` des Kopfs; Kommando und Grund gibt der Dienst
je Transaktion mit (``valeo.docflow_command``, ``valeo.docflow_reason``).

Bestehende Belege bekommen einen Anfangseintrag ``bestand``.

**Kommandoprotokoll.** ``document_command_log`` haelt jedes Kommando fest (anlegen, aendern, freigeben,
umwandeln, buchen, stornieren, loeschen, Druck, Ausgabe) — in derselben Transaktion, nicht „best effort“.
Das zentrale ``infrastructure.audit_log`` fehlt in gewachsenen Datenbanken; darauf kann sich ein Beleg nicht
verlassen. Auch dieses Protokoll ist unveraenderlich.

**Idempotenz mit Inhalt.** ``command_idempotency_keys.request_hash``: Derselbe Schluessel mit anderem Inhalt
wird abgewiesen, statt die alte Antwort fuer eine andere Anfrage auszugeben.
"""

from alembic import op

revision = "docflow_teilmengen_statushistorie_20261013"
down_revision = "docflow_steuerschluessel_20261013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE domain_docflow.document_header_links "
        "DROP CONSTRAINT IF EXISTS uq_docflow_header_link_source_relation"
    )
    # Derselbe Schutz bestand ein zweites Mal als eindeutiger Index; er bleibt als gewoehnlicher Index.
    op.execute("DROP INDEX IF EXISTS domain_docflow.ix_docflow_header_links_from_relation")
    op.execute(
        "CREATE INDEX ix_docflow_header_links_from_relation "
        "ON domain_docflow.document_header_links (tenant_id, from_header_id, relation_type)"
    )
    op.execute(
        "ALTER TABLE domain_docflow.document_header_links "
        "ADD CONSTRAINT uq_docflow_header_link_pair UNIQUE (tenant_id, from_header_id, to_header_id, relation_type)"
    )
    op.execute(
        """
        CREATE TABLE domain_docflow.document_status_history (
            id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            tenant_id VARCHAR(64) NOT NULL,
            header_id VARCHAR(36) NOT NULL,
            from_status VARCHAR(20),
            to_status VARCHAR(20) NOT NULL,
            command VARCHAR(40),
            actor VARCHAR(100),
            reason TEXT,
            changed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_docflow_status_history_header "
        "ON domain_docflow.document_status_history (tenant_id, header_id, changed_at)"
    )
    op.execute(
        """
        CREATE FUNCTION domain_docflow.protokolliere_status() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE
            kommando TEXT := NULLIF(current_setting('valeo.docflow_command', true), '');
            grund TEXT := NULLIF(current_setting('valeo.docflow_reason', true), '');
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO domain_docflow.document_status_history
                    (tenant_id, header_id, from_status, to_status, command, actor, reason)
                VALUES (NEW.tenant_id, NEW.id, NULL, NEW.status, kommando, COALESCE(NEW.updated_by, NEW.created_by), grund);
            ELSIF OLD.status IS DISTINCT FROM NEW.status THEN
                INSERT INTO domain_docflow.document_status_history
                    (tenant_id, header_id, from_status, to_status, command, actor, reason)
                VALUES (NEW.tenant_id, NEW.id, OLD.status, NEW.status, kommando, COALESCE(NEW.updated_by, NEW.created_by), grund);
            ELSIF OLD.deleted_at IS NULL AND NEW.deleted_at IS NOT NULL THEN
                INSERT INTO domain_docflow.document_status_history
                    (tenant_id, header_id, from_status, to_status, command, actor, reason)
                VALUES (NEW.tenant_id, NEW.id, OLD.status, 'geloescht', kommando, COALESCE(NEW.updated_by, NEW.created_by), grund);
            END IF;
            RETURN NEW;
        END $$
        """
    )
    op.execute(
        "CREATE TRIGGER docflow_statushistorie AFTER INSERT OR UPDATE ON domain_docflow.document_headers "
        "FOR EACH ROW EXECUTE FUNCTION domain_docflow.protokolliere_status()"
    )
    op.execute(
        """
        CREATE FUNCTION domain_docflow.statushistorie_unveraenderlich() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' AND current_setting('valeo.docflow_wartung', true) = 'loeschen' THEN
                RETURN OLD;
            END IF;
            RAISE EXCEPTION 'Die Statushistorie eines Belegs wird nicht geaendert oder geloescht.'
                USING ERRCODE = 'restrict_violation';
        END $$
        """
    )
    op.execute(
        "CREATE TRIGGER docflow_statushistorie_unveraenderlich BEFORE UPDATE OR DELETE "
        "ON domain_docflow.document_status_history "
        "FOR EACH ROW EXECUTE FUNCTION domain_docflow.statushistorie_unveraenderlich()"
    )
    op.execute(
        """
        CREATE TABLE domain_docflow.document_command_log (
            id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            tenant_id VARCHAR(64) NOT NULL,
            header_id VARCHAR(36) NOT NULL,
            command VARCHAR(40) NOT NULL,
            actor VARCHAR(100),
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            logged_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_docflow_command_log_header "
        "ON domain_docflow.document_command_log (tenant_id, header_id, logged_at)"
    )
    op.execute(
        "CREATE TRIGGER docflow_kommandoprotokoll_unveraenderlich BEFORE UPDATE OR DELETE "
        "ON domain_docflow.document_command_log "
        "FOR EACH ROW EXECUTE FUNCTION domain_docflow.statushistorie_unveraenderlich()"
    )
    op.execute(
        "ALTER TABLE domain_docflow.command_idempotency_keys ADD COLUMN IF NOT EXISTS request_hash VARCHAR(64)"
    )
    op.execute(
        "INSERT INTO domain_docflow.document_status_history (tenant_id, header_id, from_status, to_status, command, actor) "
        "SELECT tenant_id, id, NULL, status, 'bestand', COALESCE(updated_by, created_by) FROM domain_docflow.document_headers"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS docflow_statushistorie ON domain_docflow.document_headers")
    op.execute("DROP FUNCTION IF EXISTS domain_docflow.protokolliere_status()")
    op.execute("DROP TABLE IF EXISTS domain_docflow.document_status_history")
    op.execute("DROP TABLE IF EXISTS domain_docflow.document_command_log")
    op.execute("ALTER TABLE domain_docflow.command_idempotency_keys DROP COLUMN IF EXISTS request_hash")
    op.execute("DROP FUNCTION IF EXISTS domain_docflow.statushistorie_unveraenderlich()")
    op.execute(
        "ALTER TABLE domain_docflow.document_header_links DROP CONSTRAINT IF EXISTS uq_docflow_header_link_pair"
    )
    # Der alte Schutz laesst je Quelle und Folgeart nur einen Folgebeleg zu; mit Teilbelegen im Bestand
    # liesse er sich nicht wieder anlegen. Der Rueckweg stellt ihn deshalb nur her, wenn es keine gibt.
    op.execute(
        """
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM domain_docflow.document_header_links
                GROUP BY tenant_id, from_header_id, relation_type HAVING count(*) > 1
            ) THEN
                ALTER TABLE domain_docflow.document_header_links
                    ADD CONSTRAINT uq_docflow_header_link_source_relation UNIQUE (tenant_id, from_header_id, relation_type);
                DROP INDEX IF EXISTS domain_docflow.ix_docflow_header_links_from_relation;
                CREATE UNIQUE INDEX ix_docflow_header_links_from_relation
                    ON domain_docflow.document_header_links (tenant_id, from_header_id, relation_type);
            END IF;
        END $$
        """
    )
