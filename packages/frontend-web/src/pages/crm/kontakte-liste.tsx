import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Kontakte aus der ScreenDefinition `crm/kontakte-liste`. */
export default function KontakteListePage(): JSX.Element {
  return <NativeListPage screenId="crm/kontakte-liste" testId="screen-crm/kontakte-liste" />
}
