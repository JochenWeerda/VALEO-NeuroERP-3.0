import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'einkauf/bestellung-freigabe'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="einkauf-bestellung-freigabe"
      permissions={['procurement.approve']}
    />
  )
}
