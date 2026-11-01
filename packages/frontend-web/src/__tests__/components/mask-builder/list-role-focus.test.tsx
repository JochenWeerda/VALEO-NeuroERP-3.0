import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, expect, it, vi } from 'vitest'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { evaluateListExperience, focusListInsights } from '@/components/mask-builder/runtime/list-experience'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
const state=vi.hoisted(() => ({ setQuery:vi.fn(), rows:[{id:'A-1',status:'offen'},{id:'A-2',status:'angenommen'}], definition:{} as ScreenDefinition }))
vi.mock('@/lib/api/masks', () => ({useScreenDefinition:() => ({data:state.definition})}))
vi.mock('@/components/mask-builder', () => ({
  UniversalMaskRenderer: ({tables}:{tables:{list:unknown[]}}) => <p>{tables.list.length} unveränderte Datensätze</p>,
  useUniversalMaskRuntime:() => ({plan:{...state.definition,tablesByKey:{list:{}}},filteredTableRows:{list:state.rows},tableRows:{list:state.rows},tableQueryStates:{list:{page:1}},setTableQuery:state.setQuery}),
}))
beforeEach(() => {
  vi.clearAllMocks()
  state.definition={schemaVersion:1,id:'sales/angebote-liste',domain:'sales',mode:'list',title:'Angebote',listExperience:{searchFields:['id'],export:{filenamePrefix:'Angebote_',delimiter:';',columns:[{key:'id',label:'ID'}]},aggregates:[{key:'total',label:'Angebote',conditions:[]},{key:'open',label:'Offen',conditions:[{field:'status',op:'eq',value:'offen'}]}],insightLines:[{key:'sales',label:'Vertriebshinweis',variants:[{text:'{open} offene Angebote'}]},{key:'management',label:'Leitungshinweis',variants:[{text:'{total} Angebote insgesamt'}]}],roleFocus:{defaultKey:'all',options:[{key:'all',label:'Alle Rollen'},{key:'sales',label:'Vertrieb',insightLineKeys:['sales']},{key:'management',label:'Leitung',insightLineKeys:['management']}]}}} as ScreenDefinition
})
it('changes only the explanatory focus while keeping rows, counts and filters', () => {
  render(<UniversalNativeCockpitPage screenId="sales/angebote-liste" />)
  expect(screen.getByText('1 offene Angebote')).toBeInTheDocument()
  expect(screen.getByText('2 Angebote insgesamt')).toBeInTheDocument()
  fireEvent.change(screen.getByRole('combobox',{name:'Arbeitsfokus'}),{target:{value:'sales'}})
  expect(screen.getByText('1 offene Angebote')).toBeInTheDocument()
  expect(screen.queryByText('2 Angebote insgesamt')).not.toBeInTheDocument()
  expect(screen.getByText('2 unveränderte Datensätze')).toBeInTheDocument()
  expect(state.setQuery).not.toHaveBeenCalled()
  fireEvent.change(screen.getByRole('combobox',{name:'Arbeitsfokus'}),{target:{value:'management'}})
  expect(screen.queryByText('1 offene Angebote')).not.toBeInTheDocument()
  expect(screen.getByText('2 Angebote insgesamt')).toBeInTheDocument()
})
it('resets an old focus when navigating to another list', () => {
  const view=render(<UniversalNativeCockpitPage screenId="sales/angebote-liste" />)
  fireEvent.change(screen.getByRole('combobox',{name:'Arbeitsfokus'}),{target:{value:'sales'}})
  view.rerender(<UniversalNativeCockpitPage screenId="sales/lieferungen-liste" />)
  expect(screen.getByRole('combobox',{name:'Arbeitsfokus'})).toHaveValue('all')
  expect(screen.getByText('2 Angebote insgesamt')).toBeInTheDocument()
})
it('does not mutate business rows when selecting insights', () => {
  const rows=structuredClone(state.rows)
  const experience=state.definition.listExperience!
  const result=evaluateListExperience(experience,rows)
  expect(focusListInsights(experience,result.insights,'sales')).toEqual([{key:'sales',label:'Vertriebshinweis',text:'1 offene Angebote'}])
  expect(rows).toEqual(state.rows)
  expect(result.counts).toEqual({total:2,open:1})
})
