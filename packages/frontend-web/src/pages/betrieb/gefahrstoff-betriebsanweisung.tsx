import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'betrieb/gefahrstoff-betriebsanweisung'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="betrieb-gefahrstoff-betriebsanweisung"
      permissions={['compliance.read']}
    />
  )
}
