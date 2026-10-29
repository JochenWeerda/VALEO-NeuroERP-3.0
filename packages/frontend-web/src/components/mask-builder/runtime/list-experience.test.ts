import { describe, expect, it } from 'vitest'
import { compileRenderPlanFromScreenDefinition } from '../render-plan/schema-compiler'
import { applyClientTableQuery } from './client-table-query'
import { evaluateListExperience, formatListAggregate } from './list-experience'
import { validateScreenDefinition, type ListExperience, type ScreenDefinition } from '../schema'
const experience: ListExperience = { searchFields:['name'], aggregates:[{key:'open',label:'Offen',conditions:[{field:'status',op:'eq',value:'open'}]}], export:{filenamePrefix:'test',delimiter:';',columns:[{key:'name',label:'Name'}]}, workflowResume:{resumeNodeId:'node',businessStatus:'open',actionLabelPrefix:'Go ',createScreen:'create',detailScreen:'detail'}, notice:{aggregate:'open',text:'{open} offen'}, insightLines:[{label:'Status',variants:[{when:{aggregate:'open',op:'gt',value:0},text:'{open} offen'},{text:'Keine'}]}] }
const rows = [{name:'A',status:'open',secret:'needle'},{name:'B',status:'open',secret:'x'},{name:'C',status:'done',secret:'x'}]
describe('list experience', () => {
 it('counts filtered rows before pagination', () => { const q = applyClientTableQuery(rows,{page:2,pageSize:1},experience.searchFields); expect(q.rows).toHaveLength(1); expect(evaluateListExperience(experience,q.filteredRows)).toEqual({counts:{open:2},notice:'2 offen',insights:[{label:'Status',text:'2 offen'}]}) })
 it('restricts search and preserves behavior without metadata', () => { expect(applyClientTableQuery(rows,{page:1,pageSize:10,q:'needle'},experience.searchFields).total).toBe(0); expect(applyClientTableQuery(rows,{page:1,pageSize:10,q:'needle'}).total).toBe(1) })
})

describe('list experience validation', () => {
 const screen = {schemaVersion:1,id:'test/list',domain:'sales',mode:'list',title:'Test',tables:[{key:'list',label:'List',columns:[{key:'name',label:'Name'},{key:'status',label:'Status'}]}]} as ScreenDefinition
 it('does not require metadata for existing screens', () => {
   expect(validateScreenDefinition(screen)).not.toContain('listExperience is invalid')
 })
 it('allows list metadata without workflow', () => {
   expect(validateScreenDefinition({...screen,listExperience:{...experience, workflowResume:undefined}})).not.toContain('listExperience is invalid')
 })
 it('rejects dangerous keys, missing workflow fields and oversized metadata', () => {
   for (const bad of [
     {...experience, aggregates:[{key:'__proto__',label:'x',conditions:[]}]},
     {...experience, searchFields:['constructor']},
     {...experience, workflowResume:{resumeNodeId:'node',businessStatus:'open',actionLabelPrefix:'Go ',createScreen:'create',detailScreen:''}},
     {...experience, export:{...experience.export, columns:Array.from({length:101},()=>({key:'id',label:'ID'}))}},
   ]) expect(validateScreenDefinition({...screen,listExperience:bad} as ScreenDefinition)).toContain('listExperience is invalid')
 })
})

it('compiler rejects invalid list metadata before returning a cached plan', () => {
  const screen = {schemaVersion:1,id:'test/cached-list',domain:'sales',mode:'list',title:'Test',tables:[{key:'list',label:'List',columns:[{key:'name',label:'Name'},{key:'status',label:'Status'}]}],listExperience:experience} as ScreenDefinition
  expect(compileRenderPlanFromScreenDefinition(screen).listExperience).toEqual(experience)
  expect(() => compileRenderPlanFromScreenDefinition({...screen,listExperience:{...experience,export:{...experience.export,columns:[{key:'hidden',label:'Secret'}]}}})).toThrow('Invalid declarative list experience')
})


describe('declared money summaries', () => {
 const money: ListExperience = { searchFields: ['name'], aggregates: [{ key: 'balance', label: 'Saldo', kind: 'sum', field: 'amount', format: 'currency', conditions: [] }], export: { filenamePrefix: 'money', delimiter: ';', columns: [{ key: 'amount', label: 'Betrag' }] } }
 it('sums exact cents including credits before rendering', () => {
  const result = evaluateListExperience(money, [{ amount: '0.10' }, { amount: 0.2 }, { amount: '-0.01' }])
  expect(result.counts.balance).toBe(0.29)
  expect(formatListAggregate(money.aggregates[0], result.counts.balance)).toMatch(/0,29.*€/)
 })
 it.each([undefined, null, true, 'not-a-number', '0.001', Number.NaN, Number.POSITIVE_INFINITY, '900719925474.01'])('rejects unsafe money %s rather than manufacturing zero', value => {
  expect(() => evaluateListExperience(money, [{ amount: value }])).toThrow()
 })
 it('retains the filtered full set before summing', () => {
  const page = applyClientTableQuery([{ name: 'A', amount: '1.01' }, { name: 'A', amount: '2.02' }, { name: 'B', amount: '9.99' }], { page: 1, pageSize: 1, q: 'A' }, money.searchFields)
  expect(evaluateListExperience(money, page.filteredRows).counts.balance).toBe(3.03)
 })
})
