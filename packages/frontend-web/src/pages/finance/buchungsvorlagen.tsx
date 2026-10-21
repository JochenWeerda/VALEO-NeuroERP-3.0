import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Buchungsvorlagen aus der ScreenDefinition `finance/buchungsvorlagen`; Anwenden erzeugt einen Buchungsentwurf. */
export default function BuchungsvorlagenPage(): JSX.Element {
  return <NativeListPage screenId="finance/buchungsvorlagen" testId="screen-finance/buchungsvorlagen" />
}
