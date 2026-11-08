/**
 * Detailrouten: bestehende Entitaet → UniversalMaskRuntime; Anlage (new/neu/fehlende ID) → native Anlage
 * (``creation`` der ScreenDefinition) oder, bis zur Create-Paritaet, die Legacy-ObjectPage.
 * Entspricht UIX-057 / MASK-PRIMARY-NAV-NATIVE.
 */

import { Suspense, lazy, type ComponentType, type LazyExoticComponent } from 'react'
import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export function isStammCreationEntityId(entityId: string | undefined): boolean {
  return entityId == null || entityId === '' || entityId === 'new' || entityId === 'neu'
}

export interface StammNativeDetailRouteProps {
  screenId: string
  testId: string
  legacy: ComponentType | LazyExoticComponent<ComponentType>
}

export function StammNativeDetailRoute({
  screenId,
  testId,
  legacy: Legacy,
}: StammNativeDetailRouteProps): JSX.Element {
  const { id } = useParams<{ id?: string }>()

  if (isStammCreationEntityId(id)) {
    return (
      <Suspense fallback={null}>
        <Legacy />
      </Suspense>
    )
  }

  return <UniversalNativeDetailPage screenId={screenId} entityId={id} testId={testId} />
}

/**
 * Stamm-Detailroute. Ohne ``legacyImport`` legt die Seite ueber den ``creation``-Block der ScreenDefinition an
 * (``createScreenId``, Standard ``screenId``); mit ``legacyImport`` bleibt die Anlage bis zur Create-Paritaet alt.
 */
export function createStammNativeDetailPage(
  screenId: string,
  testId: string,
  legacyImport?: () => Promise<{ default: ComponentType }>,
  createScreenId: string = screenId,
): ComponentType {
  if (!legacyImport) {
    return function StammNativePage(): JSX.Element {
      const { id } = useParams<{ id?: string }>()
      if (isStammCreationEntityId(id)) {
        return <UniversalNativeCreatePage screenId={createScreenId} testId={`${testId}-create`} />
      }
      return <UniversalNativeDetailPage screenId={screenId} entityId={id} testId={testId} />
    }
  }
  const Legacy = lazy(legacyImport)
  return function StammNativeDetailPage(): JSX.Element {
    return <StammNativeDetailRoute screenId={screenId} testId={testId} legacy={Legacy} />
  }
}
