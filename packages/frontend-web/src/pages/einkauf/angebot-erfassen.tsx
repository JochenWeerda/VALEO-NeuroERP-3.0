import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'einkauf/angebot-erfassen'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="einkauf-angebot-erfassen"
      permissions={['procurement.read']}
    />
  )
}
