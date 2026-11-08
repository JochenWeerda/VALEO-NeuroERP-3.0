import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Laborauftraege aus der ScreenDefinition `qualitaet/labor-liste`. */
export default function LaborListePage(): JSX.Element {
  return <NativeListPage screenId="qualitaet/labor-liste" testId="screen-qualitaet/labor-liste" />
}
