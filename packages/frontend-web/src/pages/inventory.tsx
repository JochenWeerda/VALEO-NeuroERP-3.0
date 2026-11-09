import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Bestandskorrektur: Studio-Liste `lager/bestandskorrektur` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="lager/bestandskorrektur" testId="screen-lager/bestandskorrektur" />
}
