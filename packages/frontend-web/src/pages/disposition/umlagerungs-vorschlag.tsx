import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'disposition/umlagerungs-vorschlag'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="disposition-umlagerungs-vorschlag"
      permissions={['logistics.read']}
    />
  )
}
