import { useNavigate } from '@/app/routing/typed-router'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'annahme/warteschlange'

export default function WarteschlangePage(): JSX.Element {
  const navigate = useNavigate()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey !== 'open_harvest') return
    const id = String(row.id ?? '')
    if (!id) return
    const searchParams = new URLSearchParams({
      workflowProcess: 'harvest-to-settlement',
      workflowLabel: `queue-entry:${id}`,
      entryMode: 'Warteschlange',
    })
    navigate(`/agrar/ernte/annahme?${searchParams.toString()}`)
  }

  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="annahme-warteschlange" onAction={handleAction} />
}
