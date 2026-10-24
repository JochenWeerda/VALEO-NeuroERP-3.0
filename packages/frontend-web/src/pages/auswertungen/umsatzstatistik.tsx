import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'auswertungen/umsatzstatistik'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="auswertungen-umsatzstatistik"
      permissions={['reporting.read']}
    />
  )
}
