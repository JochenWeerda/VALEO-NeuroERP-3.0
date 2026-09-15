import { UniversalMaskRenderer } from './UniversalMaskRenderer'
import { useUniversalMaskRuntime } from './runtime/useUniversalMaskRuntime'
import type { ScreenDefinition } from './schema'
import type { SourceProposalContext } from './renderers/SourceProposalRenderer'

export const DOCUMENT_SOURCE_PROPOSAL_SCREEN: ScreenDefinition = {
  schemaVersion: 1, id: 'docflow/source-proposals', domain: 'sales', mode: 'detail',
  title: 'Belegquellen', sourceProposals: { contextKey: 'sourceContext' },
  layout: { floorplan: 'transaction', density: 'compact', contextRail: 'none', tableProfile: 'inventory' },
}

/** Legacy entry pages provide draft values only; layout and fetching remain in the Builder. */
export function DocumentSourceProposalRegion({ context }: { context: SourceProposalContext }): JSX.Element | null {
  const runtime = useUniversalMaskRuntime({
    screenId: DOCUMENT_SOURCE_PROPOSAL_SCREEN.id, schema: DOCUMENT_SOURCE_PROPOSAL_SCREEN, enabled: false,
  })
  return runtime.plan ? <UniversalMaskRenderer plan={runtime.plan} region="sourceProposals" data={{ sourceContext: context }} /> : null
}
