import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'einkauf/lieferanten-reklamationen'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="einkauf-lieferanten-reklamationen"
      permissions={['procurement.read']}
    />
  )
}
