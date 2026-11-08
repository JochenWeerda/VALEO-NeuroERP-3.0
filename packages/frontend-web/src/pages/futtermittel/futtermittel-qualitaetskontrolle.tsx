import { NativeListPage } from '@/components/mask-builder/NativeListPage'

const SCREEN_ID = 'futtermittel/futtermittel-qualitaetskontrolle'

export default function FuttermittelQualitaetskontrollePage(): JSX.Element {
  return <NativeListPage screenId={SCREEN_ID} testId="futtermittel-qualitaetskontrolle" />
}
