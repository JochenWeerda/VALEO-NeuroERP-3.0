import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'banken/zahlungsvorschlaege'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="banken-zahlungsvorschlaege"
      permissions={['finance.read']}
    />
  )
}
