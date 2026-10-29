import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'docflow/nachweisraum'

export default function NachweisraumPage(): JSX.Element {
  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey !== 'open_detail') return
    const doc = String(row.doc_number ?? '')
    if (!doc) return
    window.location.assign(`/docflow/nachweisraum/${encodeURIComponent(doc)}`)
  }

  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="docflow-nachweisraum" onAction={handleAction} />
}
