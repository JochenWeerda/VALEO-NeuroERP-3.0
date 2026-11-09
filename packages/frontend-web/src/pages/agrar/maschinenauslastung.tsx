import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Maschinenauslastung: Studio-Liste `agrar/maschinen-auslastung-liste` (gleicher Leseweg /agrar/maschinen). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="agrar/maschinen-auslastung-liste" testId="screen-agrar-maschinenauslastung" />
}
