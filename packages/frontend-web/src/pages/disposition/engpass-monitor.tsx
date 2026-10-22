import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'disposition/engpass-monitor'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="disposition-engpass-monitor"
      permissions={['logistics.read']}
    />
  )
}
