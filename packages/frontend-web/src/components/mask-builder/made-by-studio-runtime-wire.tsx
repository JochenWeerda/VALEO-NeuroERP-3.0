import { useParams } from '@/app/routing/typed-router'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

type WireProps = {
  entityId?: string
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
export function MadeByStudioDetailRuntimeWire({ screenId, testId, entityId }: WireProps): JSX.Element {
  const params = useParams<{ id: string; entityId: string }>()
  const resolved = entityId ?? params.entityId ?? params.id
  if (!resolved) return <p role="status">Bitte einen Datensatz auswählen.</p>
  return <UniversalNativeDetailPage entityId={resolved} screenId={screenId} testId={testId ?? screenId.replace('/', '-')} />
}
