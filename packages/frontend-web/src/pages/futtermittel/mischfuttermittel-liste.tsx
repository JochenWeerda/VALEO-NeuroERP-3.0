import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Mischfuttermittel aus der ScreenDefinition `futtermittel/mischfuttermittel-liste`; dieselbe Quelle wie die Objektmaske. */
export default function MischfuttermittelListePage(): JSX.Element {
  return <NativeListPage screenId="futtermittel/mischfuttermittel-liste" testId="screen-futtermittel/mischfuttermittel-liste" />
}
