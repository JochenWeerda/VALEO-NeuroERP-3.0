import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Klaerliste der Partnerzuordnung aus der ScreenDefinition `crm/partner-klaerfaelle-liste`. */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="crm/partner-klaerfaelle-liste" testId="screen-crm/partner-klaerfaelle-liste" />
}
