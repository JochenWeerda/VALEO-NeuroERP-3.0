import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import routeAliases from '@/app/route-aliases.json'
import { ErrorState } from '@/components/ErrorState'
import { PageLoader } from '@/app/PageLoader'
import { createRouteElementByModule } from '@/app/page-module-loader'
import {
  findMatchingAliasModule,
  findMatchingAliasModuleFromRouteAliases,
  normalizeRelativePath,
} from '@/app/route-builders/alias-matching'
import {
  hasAliasRouteGroup,
  loadAliasRouteGroup,
} from '@/app/route-builders/alias-groups/loaders'
import {
  hasAutoRouteGroup,
  loadAutoRouteGroup,
} from '@/app/route-builders/auto-groups/loaders'
import { isProspectingModule } from '@/app/route-builders/predicates'
import type {
  AliasGroupEntriesModule,
  AliasGroupRouteEntry,
  AutoGroupEntriesModule,
  AutoGroupRouteEntry,
} from '@/app/route-builders/types'

type AppRouteRuntimeProps = {
  prospectingEnabled: boolean
}

const autoGroupCache = new Map<string, Promise<AutoGroupEntriesModule>>()
const aliasGroupCache = new Map<string, Promise<AliasGroupEntriesModule>>()

function loadCachedAutoGroup(prefix: string): Promise<AutoGroupEntriesModule> {
  let pending = autoGroupCache.get(prefix)
  if (!pending) {
    pending = loadAutoRouteGroup(prefix)
    autoGroupCache.set(prefix, pending)
  }
  return pending
}

function loadCachedAliasGroup(prefix: string): Promise<AliasGroupEntriesModule> {
  let pending = aliasGroupCache.get(prefix)
  if (!pending) {
    pending = loadAliasRouteGroup(prefix)
    aliasGroupCache.set(prefix, pending)
  }
  return pending
}

export default function AppRouteRuntime({ prospectingEnabled }: AppRouteRuntimeProps): JSX.Element {
  const params = useParams()
  const [autoEntries, setAutoEntries] = useState<AutoGroupRouteEntry[] | null>(null)
  const [aliasEntries, setAliasEntries] = useState<AliasGroupRouteEntry[] | null>(null)
  const [loadError, setLoadError] = useState<Error | null>(null)
  const fullRelativePath = normalizeRelativePath(params['*'])
  const [prefix, ...restSegments] = fullRelativePath.split('/').filter(Boolean)
  const relativePath = restSegments.join('/')

  useEffect(() => {
    if (!prefix) {
      setAutoEntries([])
      setAliasEntries([])
      setLoadError(null)
      return
    }

    let cancelled = false

    Promise.all([
      hasAutoRouteGroup(prefix) ? loadCachedAutoGroup(prefix) : Promise.resolve({ entries: [] }),
      hasAliasRouteGroup(prefix) ? loadCachedAliasGroup(prefix) : Promise.resolve({ entries: [] }),
    ])
      .then(([autoGroup, aliasGroup]) => {
        if (cancelled) {
          return
        }
        setAutoEntries(autoGroup.entries)
        setAliasEntries(aliasGroup.entries)
        setLoadError(null)
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return
        }
        setLoadError(error instanceof Error ? error : new Error('Routen-Gruppe konnte nicht geladen werden.'))
      })

    return () => {
      cancelled = true
    }
  }, [prefix])

  // Single useMemo that resolves both the matching module and the stable JSX element.
  // Keeping this as one hook (same count as before) avoids the "rendered more hooks
  // than previous render" error during HMR when the hook count would otherwise change.
  // createRouteElementByModule() caches the JSX element via WeakMap, so calling it
  // with the same module path always returns the exact same object reference —
  // preventing Suspense from resetting on every parent re-render.
  const routeElement = useMemo(() => {
    if (!prefix || !autoEntries || !aliasEntries) {
      return createRouteElementByModule('@/pages/errors/NotFound')
    }

    const filteredAutoEntries = prospectingEnabled
      ? autoEntries
      : autoEntries.filter((entry) => !isProspectingModule(entry.module))
    const filteredAliasEntries = prospectingEnabled
      ? aliasEntries
      : aliasEntries.filter((entry) => !isProspectingModule(entry.module))

    const autoMatch = filteredAutoEntries.find((entry) => entry.path === relativePath)
    if (autoMatch) {
      return createRouteElementByModule(autoMatch.module)
    }

    const aliasMatch = findMatchingAliasModule(filteredAliasEntries, relativePath || '/')
    if (aliasMatch) {
      return createRouteElementByModule(aliasMatch)
    }

    const globalAliasMatch = findMatchingAliasModuleFromRouteAliases(
      (routeAliases.aliases ?? []) as Array<{ module: string; path?: string; index?: boolean }>,
      prefix,
      relativePath || '/',
    )
    return createRouteElementByModule(globalAliasMatch ?? '@/pages/errors/NotFound')
  }, [aliasEntries, autoEntries, prefix, prospectingEnabled, relativePath])

  if (loadError) {
    return (
      <div className="p-6">
        <ErrorState
          error={loadError}
          title={`Fehler beim Laden der Routen fuer ${prefix ?? 'unbekannt'}`}
          message="Die Seitenkonfiguration konnte nicht geladen werden."
          recoveryHint="Laden Sie die Seite neu oder wechseln Sie zur Startseite."
          onReload={() => window.location.reload()}
          onHome={() => {
            window.location.href = '/'
          }}
        />
      </div>
    )
  }

  if (!autoEntries || !aliasEntries) {
    return <PageLoader />
  }

  return routeElement
}

