"""Metadata-only provider role reconciliation, preserving effective grants."""
import copy
import json
import unittest
from pathlib import Path
import httpx
from scripts.provision_identity_provider import ROOT, prepared_realm, reconcile_realm_roles


class ProviderDescriptionContracts(unittest.TestCase):
    def test_prepared_roles_use_catalog_without_new_historical_manager(self):
        source={'realm':'fixture','roles':{'realm':[{'name':'manager','description':'old','composite':False}]}}
        snapshot=copy.deepcopy(source)
        desired=prepared_realm(source)
        catalog=json.loads((ROOT/'config/keycloak/fachrollen.json').read_text(encoding='utf8'))
        descriptions={r['name']:r['beschreibung'] for r in catalog['rollen']+catalog['grundrollen']}
        self.assertEqual(source,snapshot)
        self.assertEqual(prepared_realm(desired),desired)
        for role in desired['roles']['realm']:
            self.assertEqual(role['description'],descriptions[role['name']])
        clean=prepared_realm({'realm':'fixture','roles':{'realm':[]}})
        self.assertNotIn('manager',{r['name'] for r in clean['roles']['realm']})

    def test_metadata_update_preserves_role_and_never_assigns_users_or_composites(self):
        for failure in (None,'update_failed','not_persisted','metadata_changed','wrong_name','missing_id'):
            with self.subTest(failure=failure):
                record={'id':'role-fixture','name':'FINANCE_ADMIN','description':'old',
                        'composite':True,'clientRole':False,'attributes':{'retained':['value']}}
                if failure=='wrong_name':record['name']='wrong'
                if failure=='missing_id':record.pop('id')
                original=copy.deepcopy(record);writes=[]
                def handler(request):
                    if request.method=='GET':return httpx.Response(200,json=record)
                    self.assertEqual(request.method,'PUT')
                    self.assertTrue(request.url.path.endswith('/roles/FINANCE_ADMIN'))
                    desired=json.loads(request.content)
                    self.assertEqual(desired,{**original,'description':'canonical'})
                    writes.append(desired)
                    if failure=='update_failed':return httpx.Response(403)
                    if failure!='not_persisted':record.update(desired)
                    if failure=='metadata_changed':record['composite']=False
                    return httpx.Response(204)
                with httpx.Client(base_url='https://identity.invalid',transport=httpx.MockTransport(handler)) as client:
                    if failure:
                        with self.assertRaises(RuntimeError):
                            reconcile_realm_roles(client,{},'fixture',[{'name':'FINANCE_ADMIN','description':'canonical'}])
                        if failure in {'wrong_name','missing_id'}:self.assertEqual(writes,[])
                    else:
                        for _ in range(2):reconcile_realm_roles(client,{},'fixture',[{'name':'FINANCE_ADMIN','description':'canonical'}])
                        self.assertEqual(record,{**original,'description':'canonical'})
                        self.assertEqual(len(writes),1)
