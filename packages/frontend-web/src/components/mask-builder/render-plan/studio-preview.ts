import type { RenderPlan, RenderTablePlan } from './types'

/** A preview never mounts live transports or reuses a modified live-plan cache entry. */
export function createStudioPreviewPlan(source: RenderPlan): { plan: RenderPlan; suppressedWidgets: string[] } {
  const suppressedWidgets = [
    ...(source.calendar ? ['Kalender'] : []),
    ...(source.twin ? ['Twin-Ansicht'] : []),
    ...(source.sourceProposals ? ['Quellenvorschläge'] : []),
    ...(source.tiles.length ? ['Kachelnavigation'] : []),
  ]
  const table = (original: RenderTablePlan): RenderTablePlan => ({
    ...original, rowActions: undefined, bulkActions: undefined, rowRouteTemplate: undefined,
  })
  const tablesByKey = Object.fromEntries(Object.entries(source.tablesByKey).map(([key, value]) => [key, table(value)]))
  const tablesByTab = Object.fromEntries(Object.entries(source.tablesByTab).map(([key, values]) => [
    key, values.map(value => tablesByKey[value.key] ?? table(value)),
  ]))
  return {
    suppressedWidgets,
    plan: {
      ...source, cacheKey: `${source.cacheKey}::studio-preview`,
      shell: { ...source.shell, voice: { enabled: false, provider: source.shell.voice?.provider ?? 'webspeech' } },
      calendar: undefined, twin: undefined, sourceProposals: undefined, tiles: [],
      actions: source.actions.map(action => ({ ...action, disabled: true })),
      tablesByKey, tablesByTab,
    },
  }
}
