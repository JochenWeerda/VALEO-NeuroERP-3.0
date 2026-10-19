import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { seg, useMaskRowCommands } from '@/components/mask-builder/runtime/useMaskRowCommands'

const SCREEN_ID = 'produktion/produktionsleitstand'
const operation = (key: string) => (row: Record<string, unknown>) =>
  `/api/v1/production-control/operations/${seg(row.id)}/actions/${key}`

/** Produktionsleitstand: Statuswechsel ueber dieselben Kommando-Wege wie CLI und MCP (MASK-COMMANDS-ROLLOUT). */
export default function ProduktionsleitstandPage(): JSX.Element {
  const handleAction = useMaskRowCommands({
    screenId: SCREEN_ID,
    commands: Object.fromEntries(['release', 'start', 'complete', 'mark_rework'].map(key => [key, operation(key)])),
    navigation: { open_source: row => row.source_route, print: () => '/produktion/produktions-dokumente-drucken' },
    reasonPrompt: 'Grund fuer den Statuswechsel (Audit):',
    successTitle: 'Produktionsvorgang aktualisiert',
  })
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="produktionsleitstand"
    permissions={['production.control.write']} onAction={handleAction} />
}
