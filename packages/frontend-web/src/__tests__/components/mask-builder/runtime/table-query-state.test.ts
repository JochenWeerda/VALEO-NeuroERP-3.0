import { describe, it, expect } from 'vitest'
import { toQueryParams, defaultTableQueryState } from '@/components/mask-builder/runtime/table-query-state'

describe('toQueryParams', () => {
  it('serializes basic page/limit', () => {
    const params = toQueryParams(defaultTableQueryState(25))
    expect(params).toEqual({ page: '1', limit: '25' })
  })

  it('serializes sort and sort_dir', () => {
    const params = toQueryParams({ page: 1, pageSize: 25, sort: 'name', sortDir: 'desc' })
    expect(params['sort']).toBe('name')
    expect(params['sort_dir']).toBe('desc')
  })

  it('defaults sort_dir to asc when omitted', () => {
    const params = toQueryParams({ page: 1, pageSize: 25, sort: 'name' })
    expect(params['sort_dir']).toBe('asc')
  })

  it('serializes q', () => {
    const params = toQueryParams({ page: 1, pageSize: 25, q: 'Müller' })
    expect(params['q']).toBe('Müller')
  })

  it('serializes filterPlan as JSON string', () => {
    const filterPlan = { amount: { op: 'gt', value: 100 } }
    const params = toQueryParams({ page: 1, pageSize: 25, filterPlan })
    expect(params['filterPlan']).toBe(JSON.stringify(filterPlan))
  })

  it('omits filterPlan when empty', () => {
    const params = toQueryParams({ page: 1, pageSize: 25, filterPlan: {} })
    expect(params['filterPlan']).toBeUndefined()
  })

  it('omits sort when not set', () => {
    const params = toQueryParams({ page: 1, pageSize: 25 })
    expect(params['sort']).toBeUndefined()
    expect(params['sort_dir']).toBeUndefined()
  })
})
