import pytest
from app.services.studio_validation import validate_studio_draft
from app.core.screen_definitions_domain_batch15 import build_kontrakte_frmkontraktprotokoll_screen_definition

@pytest.mark.parametrize('metadata', [{'responseAdapter':'resource.v1'}, {'inputPrefill':'entity'}, {'resultNavigationRoute':'/crm/campaign-template/{result_id}'}])
def test_untrusted_studio_actions_cannot_acquire_native_resource_adapter(metadata):
    definition={'id':'tenant/synthetic/resource', 'actions':[{'key':'edit', 'label':'Edit', **metadata}]}
    assert 'nativer_ressourcenadapter_nicht_im_studio_katalog' in validate_studio_draft(definition,native_screen_ids=set())

def test_contract_audit_definition_has_real_context_and_exact_filters():
    definition=build_kontrakte_frmkontraktprotokoll_screen_definition()
    assert definition['dataSources'][0]['endpoint']=='/api/v1/kontrakte/{entity_id}/audit'
    table=definition['tables'][0]
    assert table['serverPagination'] is False
    assert {c['key'] for c in table['columns'] if c.get('filterable')}=={'field_name','changed_by'}
    assert [c['key'] for c in table['columns']]==['changed_at','changed_by','field_name','old_value','new_value','action']
    assert not definition['actions']


def test_native_registry_case_survives_bounded_read_contract():
    from app.api.v1.schemas.mask_data_contracts import MaskDataReadIn
    from pydantic import ValidationError
    request=MaskDataReadIn(screen_id='kontrakte/FrmKontraktProtokoll',source_key='list',entity_id='synthetic',table_key='list')
    assert request.screen_id=='kontrakte/FrmKontraktProtokoll'
    for value in ['../admin', 'kontrakte/%2e%2e/private', 'https://outside.invalid', 'a?tenant=other', 'a\\b', 'x'*122]:
        with pytest.raises(ValidationError): MaskDataReadIn(screen_id=value,source_key='list')


def test_audit_host_requires_visible_runtime_not_an_import_or_decoy():
    from app.core.mask_runtime_evidence import has_visible_runtime
    assert has_visible_runtime('return <NativeAuditListPage screenId="kontrakte/FrmKontraktProtokoll" />')
    assert not has_visible_runtime("import { NativeAuditListPage } from './NativeAuditListPage'")
    assert not has_visible_runtime('// return <NativeAuditListPage />')
    assert not has_visible_runtime('<span aria-hidden="true"><NativeAuditListPage /></span>')
    assert not has_visible_runtime('return createLegacyMaskPage(<NativeAuditListPage />)')
