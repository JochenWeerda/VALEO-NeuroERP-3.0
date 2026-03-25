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

  const matchingModule = useMemo(() => {
    if (!prefix || !autoEntries || !aliasEntries) {
      return null
    }

    const filteredAutoEntries = prospectingEnabled
      ? autoEntries
      : autoEntries.filter((entry) => !isProspectingModule(entry.module))
    const filteredAliasEntries = prospectingEnabled
      ? aliasEntries
      : aliasEntries.filter((entry) => !isProspectingModule(entry.module))

    const autoMatch = filteredAutoEntries.find((entry) => entry.path === relativePath)
    if (autoMatch) {
      return autoMatch.module
    }

    const aliasMatch = findMatchingAliasModule(filteredAliasEntries, relativePath || '/')
    if (aliasMatch) {
      return aliasMatch
    }

    return findMatchingAliasModuleFromRouteAliases(
      (routeAliases.aliases ?? []) as Array<{ module: string; path?: string; index?: boolean }>,
      prefix,
      relativePath || '/',
    )
  }, [aliasEntries, autoEntries, prefix, prospectingEnabled, relativePath])

  // useMemo must be called unconditionally (Rules of Hooks) — before any early
  // returns. createRouteElementByModule() caches via WeakMap so the call is cheap
  // even when we ultimately show a loading or error state instead.
  // This ensures React always receives the same JSX element object for the same
  // route, preventing Suspense from resetting on every parent re-render.
  const resolvedModule = matchingModule ?? '@/pages/errors/NotFound'
  const routeElement = useMemo(
    () => createRouteElementByModule(resolvedModule),
    [resolvedModule],
  )

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
