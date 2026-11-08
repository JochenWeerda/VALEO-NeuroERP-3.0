import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** EUDR Compliance aus der ScreenDefinition `compliance/eudr-compliance-liste`. */
export default function ComplianceEudrComplianceTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="compliance/eudr-compliance-liste" testId="screen-compliance/eudr-compliance-liste" />
  )
}
