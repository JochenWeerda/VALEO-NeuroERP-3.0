import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { seg, useMaskRowCommands } from '@/components/mask-builder/runtime/useMaskRowCommands'

const SCREEN_ID = 'lager/fremdware'
const item = (key: string) => (row: Record<string, unknown>) => `/api/v1/foreign-goods/${seg(row.id)}/actions/${key}`

/** Eingaben der Aktion; ``null`` bricht ab (Abfrage verworfen). */
function eingabe(actionKey: string, row: Record<string, unknown>): Record<string, unknown> | null {
  if (actionKey === 'transfer') {
    const warehouseId = window.prompt('Ziellager:', String(row.warehouse_id ?? ''))?.trim()
    if (!warehouseId) return null
    return { warehouse_id: warehouseId, location: window.prompt('Lagerort:', String(row.lagerort ?? ''))?.trim() || null }
  }
  const remaining = window.prompt('Restmenge nach Auslagerung:', '0')?.trim()
  if (remaining == null || remaining === '' || Number.isNaN(Number(remaining))) return null
  return { remaining_quantity: Number(remaining) }
}

/** Fremdware: Umbuchen und Auslagern ueber dieselben Kommando-Wege wie CLI und MCP (MASK-COMMANDS-ROLLOUT). */
export default function FremdwarePage(): JSX.Element {
  const handleAction = useMaskRowCommands({
    screenId: SCREEN_ID,
    commands: { transfer: item('transfer'), complete: item('complete') },
    navigation: { open_source: row => row.source_route },
    local: { print: () => window.print() },
    payload: eingabe,
    reasonPrompt: 'Grund (Audit):',
    successTitle: 'Fremdware aktualisiert',
  })
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="fremdware"
    permissions={['inventory.foreign-goods.write']} onAction={handleAction} />
}
