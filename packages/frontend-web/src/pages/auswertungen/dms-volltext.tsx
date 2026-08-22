import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'auswertungen/dms-volltext'

export default function DmsVolltextPage(): JSX.Element {
  function handleAction(actionKey: string, row: Record<string, unknown>): void {
    if (actionKey === 'open_source') {
      const route = String(row.source_route ?? '')
      if (route.startsWith('/')) window.location.assign(route)
    }
    if (actionKey === 'preview') {
      const url = String(row.preview_url ?? '')
      if (url.startsWith('http')) window.open(url, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="dms-volltext"
      permissions={['documents.read']}
      onAction={handleAction}
    />
  )
}
