import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId="energie/verbrauch"
      testId="screen-energie-verbrauch"
    />
  )
}
