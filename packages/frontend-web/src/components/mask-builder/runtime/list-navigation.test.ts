import { describe, expect, it } from 'vitest'
import { listCSV, listNavigationTarget } from './list-navigation'
const resume = { resumeNodeId: 'complaint', businessStatus: 'in_progress', actionLabelPrefix: 'Open: ', createScreen: 'create', detailScreen: 'detail' }
describe('Studio list workflow and export', () => {
  it('binds the target and screen kind to the current workflow instance', () => {
    const query = new URLSearchParams('workflowProcess=process&workflowInstanceId=instance&workflowCase=CASE&subject=Weizen')
    const result = listNavigationTarget('/qualitaet/reklamation/one?tab=info', query, resume, false)
    expect(result.url).toContain('tab=info&workflowProcess=process')
    expect(result.checkpoint).toMatchObject({ process: 'process', instanceId: 'instance', payload: { resume_route: result.url, resume_payload: { screen: 'detail', workflowCase: 'CASE' } } })
  })
  it('does not invent a workflow instance for ordinary navigation', () => {
    expect(listNavigationTarget('/list', new URLSearchParams('q=a'), resume, true)).toEqual({ url: '/list', checkpoint: undefined })
  })
  it.each(['//outside.invalid', 'https://outside.invalid', '/path\\outside'])('refuses an external or ambiguous target %s', target => {
    expect(() => listNavigationTarget(target, new URLSearchParams(), resume, false)).toThrow()
  })
  it('exports declared columns with stable delimiter, quotes and safe spreadsheet values', () => {
    const csv = listCSV([{ name: '=BAD()', note: 'contains;"quotes"', amount: -5, secret: 'excluded' }], [
      { key: 'name', label: 'Name' }, { key: 'note', label: 'Note' }, { key: 'amount', label: 'Amount' },
    ])
    expect(csv).toContain('"Name";"Note";"Amount"')
    expect(csv).toContain('"\'=BAD()";"contains;""quotes""";"-5"')
    expect(csv).not.toContain('excluded')
  })
})
