import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** NawaRo-Anbauflaechen: dieselbe Studio-Liste wie die NawaRo-Kaskade (Flaechenblaetter, `agrar/nawaro-kaskade`). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="agrar/nawaro-kaskade" testId="screen-nawaro-anbauflaechen" />
}
