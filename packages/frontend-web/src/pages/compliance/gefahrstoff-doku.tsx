import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Gefahrstoff-Doku aus der ScreenDefinition `compliance/gefahrstoff-doku-liste`. */
export default function ComplianceGefahrstoffDokuTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="compliance/gefahrstoff-doku-liste" testId="screen-compliance/gefahrstoff-doku-liste" />
  )
}
