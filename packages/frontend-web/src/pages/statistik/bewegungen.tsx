import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Lagerbewegungen: Studio-Liste `lager/lagerbewegungen-liste` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="lager/lagerbewegungen-liste" testId="screen-lager/lagerbewegungen-liste" />
}
