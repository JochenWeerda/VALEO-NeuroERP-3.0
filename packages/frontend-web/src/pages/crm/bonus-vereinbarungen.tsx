import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'crm/bonus-vereinbarungen'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="crm-bonus-vereinbarungen"
      permissions={['crm.read']}
    />
  )
}
