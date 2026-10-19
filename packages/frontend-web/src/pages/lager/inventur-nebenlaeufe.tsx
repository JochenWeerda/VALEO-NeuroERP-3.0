import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { seg, useMaskRowCommands } from '@/components/mask-builder/runtime/useMaskRowCommands'

const SCREEN_ID = 'lager/inventur-nebenlaeufe'
const base = '/api/v1/inventory/auxiliary'
const batch = (key: string) => (row: Record<string, unknown>) => `${base}/batches/${seg(row.id)}/actions/${key}`
const create = (key: string) => () => `${base}/actions/${key}`
const CREATE = ['create_count_sheet', 'create_control', 'create_valuation']

/**
 * Inventur-Nebenlaeufe: Erzeugen, Pruefen, Freigeben (Vier-Augen) und Uebernehmen ueber dieselben Kommando-Wege
 * wie CLI und MCP. Der Bestandsvortrag (create_opening) bleibt ein Eingabefluss der Maske.
 */
export default function InventurNebenlaeufePage(): JSX.Element {
  const handleAction = useMaskRowCommands({
    screenId: SCREEN_ID,
    commands: {
      review: batch('review'), approve: batch('approve'), apply: batch('apply'),
      ...Object.fromEntries(CREATE.map(key => [key, create(key)])),
    },
    navigation: { open_source: row => row.source_route },
    local: { print: () => window.print() },
    // Kopfaktionen haben keine Zeile: der Wiederholungsschutz gilt je Aktion.
    rowKey: row => String(row.id ?? 'kopf'),
    payload: (actionKey) => {
      if (!CREATE.includes(actionKey)) return undefined
      const countId = window.prompt('Inventur-ID:')?.trim()
      return countId ? { inventory_count_id: countId } : null
    },
    reasonPrompt: 'Grund / Zweck (Audit):',
    successTitle: 'Inventur-Nebenlauf aktualisiert',
  })
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="inventur-nebenlaeufe"
    permissions={['inventory.aux.write']} onAction={handleAction} />
}
