/** Transitional lazy loader. It preserves component props and is never migration evidence. */

import { Suspense, lazy, type ComponentType } from 'react'

export function createLegacyMaskPage<Props extends object>(
  legacyImport: () => Promise<{ default: ComponentType<Props> }>,
): ComponentType<Props> {
  // React.lazy wraps ref types; the loader preserves the exact declared Props contract.
  const Legacy = lazy(legacyImport) as unknown as ComponentType<Props>
  return function LegacyMaskPage(props: Props): JSX.Element {
    return (
      <Suspense fallback={null}>
        <Legacy {...props} />
      </Suspense>
    )
  }
}
