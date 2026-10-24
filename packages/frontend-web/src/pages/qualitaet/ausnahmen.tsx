import { NativeListPage } from '@/components/mask-builder/NativeListPage'

const SCREEN_ID = 'qualitaet/ausnahmen'

export default function QualitaetAusnahmenPage(): JSX.Element {
  return <NativeListPage screenId={SCREEN_ID} testId="qualitaet-ausnahmen" />
}
