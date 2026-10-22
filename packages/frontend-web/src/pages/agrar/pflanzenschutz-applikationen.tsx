import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Pflanzenschutz-Applikationen aus der ScreenDefinition `agrar/pflanzenschutz-applikationen-liste`. */
export default function AgrarPflanzenschutzApplikationenTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="agrar/pflanzenschutz-applikationen-liste" testId="screen-agrar/pflanzenschutz-applikationen-liste" />
  )
}
