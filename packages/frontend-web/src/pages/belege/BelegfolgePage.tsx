import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'belege/belegfolge'

export default function BelegfolgePage(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="belege-belegfolge"
      permissions={['documents.read']}
    />
  )
}
