import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'einkauf/bestellvorschlag-kontrakt'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="einkauf-bestellvorschlag-kontrakt"
      permissions={['procurement.read']}
    />
  )
}
