import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** PCN-Meldungen aus der ScreenDefinition `compliance/pcn-liste`; Aktionen und Spalten stehen in der Definition. */
export default function PcnListePage(): JSX.Element {
  return <NativeListPage screenId="compliance/pcn-liste" testId="screen-compliance/pcn-liste" />
}
