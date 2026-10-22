import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

type WireProps = {
  screenId: string
  testId?: string
}

/** Statische Gate-E-Zuordnung für Listen-ScreenDefinitions (Aufrufer setzt screenId-Literal). */
export function MadeByStudioListRuntimeWire({ screenId, testId }: WireProps): JSX.Element {
  return <NativeListPage screenId={screenId} testId={testId ?? `screen-${screenId}`} />
}

/** Statische Gate-E-Zuordnung für Cockpit-ScreenDefinitions. */
export function MadeByStudioCockpitRuntimeWire({ screenId, testId }: WireProps): JSX.Element {
  return <UniversalNativeCockpitPage screenId={screenId} testId={testId ?? screenId.replace('/', '-')} />
}

/** Statische Gate-E-Zuordnung für Detail-ScreenDefinitions. */
export function MadeByStudioDetailRuntimeWire({ screenId, testId }: WireProps): JSX.Element {
  return <UniversalNativeDetailPage screenId={screenId} testId={testId ?? screenId.replace('/', '-')} />
}
