import { NativeListPage } from '@/components/mask-builder/NativeListPage'

const SCREEN_ID = 'compliance/export-pruefprotokoll'

export default function ComplianceExportPruefprotokollPage(): JSX.Element {
  return <NativeListPage screenId={SCREEN_ID} testId="compliance-export-pruefprotokoll" />
}
