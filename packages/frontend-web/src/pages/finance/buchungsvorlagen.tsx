import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Buchungsvorlagen aus der ScreenDefinition `finance/buchungsvorlagen`; Aktionen und Spalten stehen in der Definition. */
export default function BuchungsvorlagenPage(): JSX.Element {
  return <NativeListPage screenId="finance/buchungsvorlagen" testId="screen-finance/buchungsvorlagen" />
}
