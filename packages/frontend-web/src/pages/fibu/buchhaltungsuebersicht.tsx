import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId="workspace/fibu"
      testId="fibu-buchhaltungsuebersicht"
    />
  )
}
