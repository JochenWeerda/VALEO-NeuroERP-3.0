import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'auswertungen/warengruppen-analyse'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="auswertungen-warengruppen-analyse"
      permissions={['reporting.read']}
    />
  )
}
