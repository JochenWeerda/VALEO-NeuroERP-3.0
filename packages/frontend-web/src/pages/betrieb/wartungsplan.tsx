import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'betrieb/wartungsplan'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="betrieb-wartungsplan"
      permissions={['operations.read']}
    />
  )
}
