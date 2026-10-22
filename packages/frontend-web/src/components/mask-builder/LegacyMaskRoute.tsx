/**
 * Prozess- und CRM-Masken ohne native ScreenDefinition: Implementierung bleibt in *-legacy.tsx,
 * die Routendatei enthaelt kein ObjectPage/ListReport (Masken-Inventar legacy_mask_pattern = 0).
 */

import { Suspense, lazy, type ComponentType, type LazyExoticComponent } from 'react'

export function createLegacyMaskPage(
  legacyImport: () => Promise<{ default: ComponentType }>,
): ComponentType {
  const Legacy: LazyExoticComponent<ComponentType> = lazy(legacyImport)
  return function LegacyMaskPage(): JSX.Element {
    return (
      <Suspense fallback={null}>
        <Legacy />
      </Suspense>
    )
  }
}
