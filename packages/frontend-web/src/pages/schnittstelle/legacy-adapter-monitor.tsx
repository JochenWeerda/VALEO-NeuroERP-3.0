import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { seg, useMaskRowCommands } from '@/components/mask-builder/runtime/useMaskRowCommands'

const SCREEN_ID = 'schnittstelle/legacy-adapter-monitor'
const batch = (key: string) => (row: Record<string, unknown>) =>
  `/api/v1/legacy-interface-adapters/batches/${seg(row.id)}/actions/${key}`

/** Altsystem-Adapter: Staging, Abstimmung und Pilotfreigabe ueber dieselben Kommando-Wege wie CLI und MCP. */
export default function LegacyAdapterMonitorPage(): JSX.Element {
  const handleAction = useMaskRowCommands({
    screenId: SCREEN_ID,
    commands: { stage: batch('stage'), reconcile: batch('reconcile'), approve: batch('approve') },
    reasonPrompt: 'Begruendung (Audit):',
    successTitle: 'Adapter-Batch aktualisiert',
  })
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="legacy-adapter-monitor"
      permissions={['integration.legacy-adapter.read']}
      onAction={handleAction}
    />
  )
}
