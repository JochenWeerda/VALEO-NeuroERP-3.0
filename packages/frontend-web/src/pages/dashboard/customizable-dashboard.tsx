import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'dashboard/customizable-dashboard'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="dashboard-customizable-dashboard"
      permissions={['controlling.read']}
    />
  )
}
