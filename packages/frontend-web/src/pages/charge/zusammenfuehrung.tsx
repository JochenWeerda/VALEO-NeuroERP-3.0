import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'charge/zusammenfuehrung'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="charge-zusammenfuehrung"
      permissions={['inventory.read']}
    />
  )
}
