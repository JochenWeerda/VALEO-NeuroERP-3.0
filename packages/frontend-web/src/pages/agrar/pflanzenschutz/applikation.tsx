import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** PSM-Applikationen: Studio-Liste `agrar/pflanzenschutz-applikationen-liste` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="agrar/pflanzenschutz-applikationen-liste" testId="screen-agrar/pflanzenschutz-applikationen-liste" />
}
