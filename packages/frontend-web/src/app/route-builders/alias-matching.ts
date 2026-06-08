import { matchPath } from '@/app/routing/typed-router'
import type { AliasGroupRouteEntry, RouteAliasEntry } from '@/app/route-builders/types'

export function normalizeRelativePath(value: string | undefined): string {
  return String(value ?? '').replace(/^\/+|\/+$/g, '')
}

function rankPath(path: string): number {
  return path
    .split('/')
    .filter(Boolean)
    .reduce((score, segment) => {
      if (segment === '*') return score + 1
      if (segment.startsWith(':')) return score + 2
      return score + 4
    }, 0)
}

export function compareAliasEntries(a: AliasGroupRouteEntry, b: AliasGroupRouteEntry): number {
  const segmentsA = a.path.split('/').filter(Boolean)
  const segmentsB = b.path.split('/').filter(Boolean)
  if (segmentsA.length !== segmentsB.length) {
    return segmentsB.length - segmentsA.length
  }
  const scoreDiff = rankPath(b.path) - rankPath(a.path)
  if (scoreDiff !== 0) {
    return scoreDiff
  }
  return a.path.localeCompare(b.path)
}

export function stripAliasPrefix(path: string, prefix: string): string {
  const normalizedPath = normalizeRelativePath(path)
  const normalizedPrefix = normalizeRelativePath(prefix)

  if (!normalizedPrefix) {
    return normalizedPath
  }

  if (normalizedPath === normalizedPrefix) {
    return ''
  }

  const prefixWithSlash = `${normalizedPrefix}/`
  if (normalizedPath.startsWith(prefixWithSlash)) {
    return normalizedPath.slice(prefixWithSlash.length)
  }

  return normalizedPath
}

export function findMatchingAliasEntry(
  entries: AliasGroupRouteEntry[],
  candidatePath: string,
): AliasGroupRouteEntry | null {
  // matchPath erwartet eine URL-Pathname mit führendem "/" (RR 6.30); relativePath aus dem
  // Splat ist ohne Slash — sonst schlagen dynamische Aliase (z. B. lead/:id) fehl.
  const pathname =
    !candidatePath || candidatePath === '/'
      ? '/'
      : candidatePath.startsWith('/')
        ? candidatePath
        : `/${candidatePath}`

  return (
    [...entries]
      .sort(compareAliasEntries)
      .find((entry) => matchPath({ path: entry.path || '/', end: true }, pathname)) ?? null
  )
}

export function findMatchingAliasModule(
  entries: AliasGroupRouteEntry[],
  candidatePath: string,
): string | null {
  return findMatchingAliasEntry(entries, candidatePath)?.module ?? null
}

export function findMatchingAliasEntryFromRouteAliases(
  aliases: RouteAliasEntry[],
  prefix: string,
  candidatePath: string,
): RouteAliasEntry | null {
  const normalizedPrefix = normalizeRelativePath(prefix)
  const normalizedCandidatePath = normalizeRelativePath(candidatePath)
  const fullPath = normalizedCandidatePath
    ? `${normalizedPrefix}/${normalizedCandidatePath}`
    : normalizedPrefix

  const pathname = `/${fullPath}`
  // Erst exakte Treffer (statische Pfade), dann dynamische Pattern (matchPath) —
  // sortiert nach Spezifität, damit z. B. crm/lead/:id den Param liefert.
  const ranked = aliases
    .filter((entry): entry is RouteAliasEntry & { path: string } => typeof entry.path === 'string')
    .sort((a, b) => compareAliasEntries({ path: a.path, module: a.module }, { path: b.path, module: b.module }))
  return (
    ranked.find((entry) => normalizeRelativePath(entry.path) === fullPath) ??
    ranked.find((entry) => matchPath({ path: `/${normalizeRelativePath(entry.path)}`, end: true }, pathname)) ??
    null
  )
}

export function findMatchingAliasModuleFromRouteAliases(
  aliases: RouteAliasEntry[],
  prefix: string,
  candidatePath: string,
): string | null {
  return findMatchingAliasEntryFromRouteAliases(aliases, prefix, candidatePath)?.module ?? null
}
