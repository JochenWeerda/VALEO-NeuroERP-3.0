import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** QS-Checkliste aus der ScreenDefinition `compliance/qs-checkliste-liste`. */
export default function ComplianceQsChecklisteTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="compliance/qs-checkliste-liste" testId="screen-compliance/qs-checkliste-liste" />
  )
}
