/**
 * Detailrouten: bestehende Entitaet → UniversalMaskRuntime; Anlage (new/neu/fehlende ID) → Legacy-ObjectPage.
 * Entspricht UIX-057 / MASK-PRIMARY-NAV-NATIVE (Create bleibt Legacy bis Create-Paritaet).
 */

import { Suspense, lazy, type ComponentType, type LazyExoticComponent } from 'react'
import { useParams } from '@/app/routing/typed-router'
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

export function createStammNativeDetailPage(
  screenId: string,
  testId: string,
  legacyImport: () => Promise<{ default: ComponentType }>,
): ComponentType {
  const Legacy = lazy(legacyImport)
  return function StammNativeDetailPage(): JSX.Element {
    return <StammNativeDetailRoute screenId={screenId} testId={testId} legacy={Legacy} />
  }
}
