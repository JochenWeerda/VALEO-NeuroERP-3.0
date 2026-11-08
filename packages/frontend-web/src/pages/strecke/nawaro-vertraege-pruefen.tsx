import { NativeListPage } from '@/components/mask-builder/NativeListPage'

const SCREEN_ID = 'strecke/nawaro-vertraege-pruefen'

export default function NawaroVertraegePruefenPage(): JSX.Element {
  return <NativeListPage screenId={SCREEN_ID} testId="strecke-nawaro-vertraege-pruefen" />
}
