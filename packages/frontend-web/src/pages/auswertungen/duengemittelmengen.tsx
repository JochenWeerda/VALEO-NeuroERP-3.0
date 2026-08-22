import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'auswertungen/duengemittelmengen'

export default function DuengemittelmengenPage(): JSX.Element {
  function handleAction(actionKey: string, row: Record<string, unknown>): void {
    if (actionKey !== 'open_source') return
    const deliveryId = String(row.lieferschein_id ?? '')
    if (deliveryId) window.location.assign(`/verkauf/lieferschein-erfassung/${encodeURIComponent(deliveryId)}`)
  }

  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="duengemittelmengen" onAction={handleAction} />
}
