import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'auswertungen/vertriebstrichter'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="auswertungen-vertriebstrichter"
      permissions={['reporting.read']}
    />
  )
}
