import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** PSM-Zulassungen aus dem lokalen PSM-Stamm. */
export default function ComplianceUspKonformitaet(): JSX.Element {
  return <NativeListPage screenId="compliance/zulassungen-liste" testId="screen-compliance/zulassungen-liste" />
}
