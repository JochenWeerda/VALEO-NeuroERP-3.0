import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Positionsmatrix: Studio-Liste `kontrakte/positionen` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="kontrakte/positionen" testId="screen-kontrakte/positionen" />
}
