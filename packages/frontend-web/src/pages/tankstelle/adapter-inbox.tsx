import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { seg, useMaskRowCommands } from '@/components/mask-builder/runtime/useMaskRowCommands'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'tankstelle/adapter-inbox'
const intake = (key: string) => (row: Record<string, unknown>) => `/api/v1/tank-adapter/intake/${seg(row.id)}/actions/${key}`

/** Tankanlagen-Eingang: Pruefen, Uebernehmen und Wiederholen ueber dieselben Kommando-Wege wie CLI und MCP. */
export default function TankAdapterInboxPage(): JSX.Element {
  const { toast } = useToast()
  const handleAction = useMaskRowCommands({
    screenId: SCREEN_ID,
    commands: { validate: intake('validate'), process: intake('process'), retry: intake('retry') },
    navigation: { open_source: row => `/tankstelle/adapter-inbox?focus=${seg(row.id)}` },
    payload: (actionKey) => {
      if (actionKey !== 'retry') return undefined
      const corrected = window.prompt('Korrigiertes Payload als JSON (leer = unveraendert):')?.trim()
      if (!corrected) return {}
      try {
        return { corrected_payload: JSON.parse(corrected) as unknown }
      } catch {
        toast({ title: 'Kein gueltiges JSON', description: 'Das korrigierte Payload wurde nicht gesendet.', variant: 'destructive' })
        return null
      }
    },
    reasonPrompt: 'Grund (Audit):',
    successTitle: 'Tankanlagen-Eingang aktualisiert',
  })
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="tank-adapter-inbox" permissions={['tank.adapter.write']} onAction={handleAction} />
}
