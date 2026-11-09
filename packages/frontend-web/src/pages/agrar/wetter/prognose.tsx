import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Wetterprognose: Studio-Liste `agrar/wetter` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="agrar/wetter" testId="screen-agrar/wetter" />
}
