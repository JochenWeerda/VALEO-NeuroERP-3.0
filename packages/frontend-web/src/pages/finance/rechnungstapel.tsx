import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { seg, useMaskRowCommands } from '@/components/mask-builder/runtime/useMaskRowCommands'

const SCREEN_ID = 'finance/rechnungstapel'
const batch = (key: string) => (row: Record<string, unknown>) => `/api/v1/billing-batches/${seg(row.id)}/actions/${key}`

/** Rechnungstapel: Pruefen, Freigeben (Vier-Augen) und Ausfuehren ueber dieselben Kommando-Wege wie CLI und MCP. */
export default function RechnungstapelPage(): JSX.Element {
  const handleAction = useMaskRowCommands({
    screenId: SCREEN_ID,
    commands: {
      validate: batch('validate'),
      release: batch('release'),
      execute: batch('execute'),
      retry: row => `/api/v1/billing-batches/lines/${seg(row.id)}/actions/retry`,
    },
    navigation: { open_source: row => row.source_route, open_evidence: row => row.evidence_route },
    reasonPrompt: 'Grund (Audit):',
    successTitle: 'Rechnungstapel aktualisiert',
  })
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="rechnungstapel"
    permissions={['billing.batch.write']} onAction={handleAction} />
}
