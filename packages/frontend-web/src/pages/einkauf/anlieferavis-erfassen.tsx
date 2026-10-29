import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'einkauf/anlieferavis-erfassen'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="einkauf-anlieferavis-erfassen"
      permissions={['procurement.read']}
    />
  )
}
