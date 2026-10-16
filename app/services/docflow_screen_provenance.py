"""Verified screen provenance stored in the existing immutable document command log."""
from copy import deepcopy
from sqlalchemy import text
from app.core.exceptions import ConflictError, ValidationFailedError


def resolve_screen_context(context, doc_type, tenant_id):
    if context is None:
        return None
    from app.core.screen_definitions import get_screen_definition
    from app.core.studio_release import definition_hash
    definition = get_screen_definition(context.screen_id, tenant_id=tenant_id)
    if not definition or definition.get('variant', {}).get('belegart') != doc_type:
        raise ValidationFailedError('Belegmaske ist fuer diesen Mandanten und Belegtyp nicht aktiv.')
    if definition_hash(definition) != context.definition_hash:
        raise ConflictError('Maskenfassung wurde geaendert. Bitte die Maske neu laden.')
    return {'screen_id': context.screen_id, 'definition_hash': context.definition_hash,
            'document_variant': deepcopy(definition.get('documentVariant')),
            'studio_release': deepcopy(definition.get('studioRelease'))}


def read_screen_context(service, doc_id):
    row = service.db.execute(text(
        "SELECT payload FROM domain_docflow.document_command_log "
        "WHERE tenant_id=:t AND header_id=:id AND command='create' ORDER BY logged_at,id LIMIT 1"),
        {'t': service.tenant_id, 'id': doc_id}).mappings().first()
    return (row['payload'] or {}).get('screen_context') if row else None
