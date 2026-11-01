import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { validateScreenDefinition, type ScreenDefinition } from '@/components/mask-builder/schema'
import { tableSourceRequest } from '@/components/mask-builder/runtime/table-source-request'
import fixture from '../../fixtures/complaint-studio.json'

const state = vi.hoisted(() => ({ setTableQuery: vi.fn(), schema: {} as ScreenDefinition }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: state.schema }) }))
vi.mock('@/components/mask-builder', () => ({
  UniversalMaskRenderer: () => <div>Central mask</div>,
  useUniversalMaskRuntime: () => ({ plan: { ...state.schema, tablesByKey: {list:state.schema.tables?.[0]} },
    filteredTableRows:{list:[]}, tableQueryStates:{list:{page:3,pageSize:50,presetFilters:{owner:'mine'}}},
    setTableQuery: state.setTableQuery }),
}))

function definition(): ScreenDefinition {
  const d = structuredClone(fixture) as ScreenDefinition
  delete d.listExperience!.workflowResume
  d.tables![0].columns.push({key:'assigned_to',label:'Owner'})
  d.listExperience!.presets = [
    {key:'owner',label:'Zuständigkeit',field:'assigned_to',kind:'actor',options:[{value:'all',label:'Alle'},{value:'mine',label:'Meine Aktivitäten'}]},
    {key:'when',label:'Zeitraum',field:'datum',kind:'date',options:[{value:'all',label:'Alle'},{value:'today',label:'Heute'},{value:'week',label:'Diese Woche'},{value:'overdue',label:'Überfällig'}]},
  ]
  return d
}

beforeEach(() => { vi.clearAllMocks(); state.schema=definition() })

it('renders declared accessible selectors centrally and preserves other selections when resetting the page', () => {
  render(<UniversalNativeCockpitPage screenId="test/list" />)
  expect(screen.getByRole('combobox',{name:'Zuständigkeit'})).toHaveValue('mine')
  fireEvent.change(screen.getByRole('combobox',{name:'Zeitraum'}),{target:{value:'week'}})
  expect(state.setTableQuery).toHaveBeenCalledWith('list',{page:1,presetFilters:{owner:'mine',when:'week'}})
})

it('serializes exactly the same registered selectors and bounded complete-read flag as MCP/CLI', () => {
  const url=tableSourceRequest('test/list',undefined,{tableKey:'list',sourceKey:'rows',endpoint:'/source',clientQuery:true,requiresServerQuery:true},
    {page:1,pageSize:100,complete:true,presetFilters:{owner:'mine',when:'today'}})!
  const params=new URLSearchParams(url.split('?')[1])
  expect(params.get('complete')).toBe('true')
  expect(JSON.parse(params.get('preset_filters')!)).toEqual({owner:'mine',when:'today'})
  expect(params.has('tenant_id')).toBe(false)
})

it('accepts valid presets on a complete client table', () => {
  expect(validateScreenDefinition(definition())).not.toContain('listExperience is invalid')
})

it.each(['unknownField','duplicate','actorInjection','dateInjection','partial','executable'])('rejects invalid declaration %s', problem => {
  const d=definition()
  if(problem==='unknownField') d.listExperience!.presets![0].field='secret'
  if(problem==='duplicate') d.listExperience!.presets!.push(d.listExperience!.presets![0])
  if(problem==='actorInjection') d.listExperience!.presets![0].options[1].value='caller-supplied-user'
  if(problem==='dateInjection') d.listExperience!.presets![1].options[1].value='tomorrow'
  if(problem==='partial') d.tables![0].serverPagination=true
  if(problem==='executable') Object.assign(d.listExperience!.presets![0],{command:'/delete'})
  expect(validateScreenDefinition(d)).toContain('listExperience is invalid')
})


it('reports malformed null presets as validation errors without crashing', () => {
  const d=definition()
  Object.assign(d.listExperience!,{presets:[null]})
  expect(validateScreenDefinition(d)).toContain('listExperience is invalid')
})
