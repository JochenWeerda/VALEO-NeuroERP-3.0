import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Dokumentenablage aus der ScreenDefinition `dokumente/ablage-liste`. */
export default function DokumenteAblageTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="dokumente/ablage-liste" testId="screen-dokumente/ablage-liste" />
  )
}
