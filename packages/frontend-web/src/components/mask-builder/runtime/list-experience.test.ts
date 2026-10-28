import { describe, expect, it } from 'vitest'
import { compileRenderPlanFromScreenDefinition } from '../render-plan/schema-compiler'
import { applyClientTableQuery } from './client-table-query'
import { evaluateListExperience } from './list-experience'
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
