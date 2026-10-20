import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Einzelfuttermittel aus der ScreenDefinition `futtermittel/einzelfuttermittel-liste`; dieselbe Quelle wie die Objektmaske. */
export default function EinzelfuttermittelListePage(): JSX.Element {
  return <NativeListPage screenId="futtermittel/einzelfuttermittel-liste" testId="screen-futtermittel/einzelfuttermittel-liste" />
}
