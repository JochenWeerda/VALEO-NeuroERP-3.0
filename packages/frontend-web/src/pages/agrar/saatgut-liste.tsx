import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Saatgut aus der ScreenDefinition `agrar/saatgut-liste`; Zeilen oeffnen die native Objektmaske `agrar/saatgut`. */
export default function SaatgutListePage(): JSX.Element {
  return <NativeListPage screenId="agrar/saatgut-liste" testId="screen-agrar/saatgut-liste" />
}
