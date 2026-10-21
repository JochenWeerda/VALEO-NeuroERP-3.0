import { describe, it, expect } from 'vitest'
import { tableSourceRequest } from '@/components/mask-builder/runtime/table-source-request'
describe('shared table request', () => {
  it('carries the same projection contract without identity overrides', () => {
    const url = tableSourceRequest('finance/list', 'record', {tableKey:'list', sourceKey:'rows', clientQuery:true, endpoint:'/unused', requiresServerQuery:true}, {page:2,pageSize:10,q:'Müller',sort:'name',sortDir:'desc',filterPlan:{name:{op:'contains',value:'A',label:'Name'}}})!
    const parsed = new URL(url, 'http://localhost')
    expect(parsed.pathname).toBe('/api/v1/masks/finance%2Flist/data/rows')
    expect(Object.fromEntries(parsed.searchParams)).toMatchObject({table_key:'list',entity_id:'record',page:'2',limit:'10',q:'Müller',sort:'name',sort_dir:'desc'})
    expect(parsed.searchParams.has('tenant_id')).toBe(false)
    expect(JSON.parse(parsed.searchParams.get('filter_plan')!)).toEqual({name:{op:'contains',value:'A',label:'Name'}})
  })
  it('retains legacy and server paging contracts', () => {
    for (const binding of [{tableKey:'x',endpoint:'/x',requiresServerQuery:true,clientQuery:true},{tableKey:'x',sourceKey:'rows',endpoint:'/x',requiresServerQuery:true,clientQuery:false}]) {
      expect(tableSourceRequest('s',undefined,binding,{page:1,pageSize:25})).toBeUndefined()
    }
  })
})
