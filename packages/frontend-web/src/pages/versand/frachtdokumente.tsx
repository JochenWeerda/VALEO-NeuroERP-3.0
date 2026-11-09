import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Frachtbriefe: Studio-Liste `logistik/frachtbriefe` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="logistik/frachtbriefe" testId="screen-logistik/frachtbriefe" />
}
