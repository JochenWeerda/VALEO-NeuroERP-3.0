import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { seg, useMaskRowCommands } from '@/components/mask-builder/runtime/useMaskRowCommands'

const command = (key: string) => (row: Record<string, unknown>) =>
  `/api/v1/document-control/exceptions/${seg(row.id)}/actions/${key}`

/**
 * Belegkontrolle und ihre gespeicherten L3-Sichten. Die Seite fragt nur die Begruendung ab; Bearbeiter,
 * Zustaendiger, Statusregeln, Audit und Wiederholungsschutz liegen beim Kommando-Endpunkt, den auch CLI
 * und MCP rufen (MASK-COMMANDS-ROLLOUT).
 */
export function DocumentControlScopePage({ screenId, testId }: { screenId: string; testId?: string }): JSX.Element {
  const handleAction = useMaskRowCommands({
    screenId,
    commands: Object.fromEntries(['assign_me', 'start_work', 'resolve', 'waive'].map(key => [key, command(key)])),
    navigation: { open_source: row => row.source_route },
    successTitle: 'Belegkontrolle aktualisiert',
  })

  return (
    <UniversalNativeCockpitPage
      screenId={screenId}
      testId={testId ?? screenId.replace('/', '-')}
      permissions={['document_control.write']}
      onAction={handleAction}
    />
  )
}
