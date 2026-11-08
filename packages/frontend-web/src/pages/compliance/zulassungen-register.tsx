import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Zulassungsregister aus der ScreenDefinition `compliance/zulassungen-liste`. */
export default function ComplianceZulassungenRegisterTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="compliance/zulassungen-liste" testId="screen-compliance/zulassungen-liste" />
  )
}
