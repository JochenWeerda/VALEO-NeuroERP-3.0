import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'crm/events-messen'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="crm-events-messen"
      permissions={['crm.read']}
    />
  )
}
