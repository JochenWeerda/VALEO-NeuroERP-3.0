import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'disposition/bestell-vorschlag'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="disposition-bestell-vorschlag"
      permissions={['procurement.read']}
    />
  )
}
