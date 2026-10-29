import { NativeListPage } from '@/components/mask-builder/NativeListPage'

const SCREEN_ID = 'compliance/sanktionspruefung'

export default function ComplianceSanktionspruefungPage(): JSX.Element {
  return <NativeListPage screenId={SCREEN_ID} testId="compliance-sanktionspruefung" />
}
