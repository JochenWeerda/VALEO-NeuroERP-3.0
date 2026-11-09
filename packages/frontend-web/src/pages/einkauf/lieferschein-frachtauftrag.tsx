import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Frachtauftraege: Studio-Liste `einkauf/frachtauftraege-liste` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="einkauf/frachtauftraege-liste" testId="screen-einkauf/frachtauftraege-liste" />
}
