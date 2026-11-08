import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Sachkundenachweise aus der ScreenDefinition `compliance/sachkunde-liste`. */
export default function ComplianceSachkundeRegisterTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="compliance/sachkunde-liste" testId="screen-compliance/sachkunde-liste" />
  )
}
