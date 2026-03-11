import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import { ErrorState } from '@/components/ErrorState'
import { PageLoader } from '@/app/PageLoader'
import { createRouteElementByModule } from '@/app/page-module-loader'
import {
  findMatchingAliasModule,
  normalizeRelativePath,
  stripAliasPrefix,
} from '@/app/route-builders/alias-matching'
import { loadAliasRouteGroup } from '@/app/route-builders/alias-groups/loaders'
import type { AliasGroupEntriesModule, AliasGroupRouteEntry } from '@/app/route-builders/types'

const PORTAL_PREFIX = 'portal'
let portalAliasGroupPromise: Promise<AliasGroupEntriesModule> | null = null

function loadPortalAliasGroup(): Promise<AliasGroupEntriesModule> {
  if (!portalAliasGroupPromise) {
    portalAliasGroupPromise = loadAliasRouteGroup(PORTAL_PREFIX)
  }
  return portalAliasGroupPromise
}

export default function PortalRouteRuntime(): JSX.Element {
  const params = useParams()
  const [aliasEntries, setAliasEntries] = useState<AliasGroupRouteEntry[] | null>(null)
  const [loadError, setLoadError] = useState<Error | null>(null)
  const relativePath = normalizeRelativePath(params['*'])

  useEffect(() => {
    let cancelled = false

    loadPortalAliasGroup()
      .then((module) => {
        if (cancelled) {
          return
        }

        setAliasEntries(
          module.entries.map((entry) => ({
            ...entry,
            path: stripAliasPrefix(entry.path, PORTAL_PREFIX),
          })),
        )
        setLoadError(null)
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return
        }

        setLoadError(error instanceof Error ? error : new Error('Portal-Routen konnten nicht geladen werden.'))
      })

    return () => {
      cancelled = true
    }
  }, [])

  const moduleSpecifier = useMemo(() => {
    if (!aliasEntries) {
      return null
    }

    return findMatchingAliasModule(aliasEntries, relativePath || '/')
  }, [aliasEntries, relativePath])

  if (loadError) {
    return (
      <div className="p-6">
        <ErrorState
          error={loadError}
          title="Fehler beim Laden der Portal-Routen"
          message="Die Seitenkonfiguration des Kundenportals konnte nicht geladen werden."
          recoveryHint="Laden Sie die Seite neu oder wechseln Sie zur Portaluebersicht."
          onReload={() => window.location.reload()}
          onHome={() => {
            window.location.href = '/portal'
          }}
        />
      </div>
    )
  }

  if (!aliasEntries) {
    return <PageLoader />
  }

  if (!moduleSpecifier) {
    return createRouteElementByModule('@/pages/errors/NotFound')
  }

  return createRouteElementByModule(moduleSpecifier)
}
