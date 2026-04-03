import { matchPath } from 'react-router-dom'
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

export function findMatchingAliasModule(
  entries: AliasGroupRouteEntry[],
  candidatePath: string,
): string | null {
  // matchPath erwartet eine URL-Pathname mit führendem "/" (RR 6.30); relativePath aus dem
  // Splat ist ohne Slash — sonst schlagen dynamische Aliase (z. B. lead/:id) fehl.
  const pathname =
    !candidatePath || candidatePath === '/'
      ? '/'
      : candidatePath.startsWith('/')
        ? candidatePath
        : `/${candidatePath}`

  const match = [...entries]
    .sort(compareAliasEntries)
    .find((entry) => matchPath({ path: entry.path || '/', end: true }, pathname))

  return match?.module ?? null
}

export function findMatchingAliasModuleFromRouteAliases(
  aliases: RouteAliasEntry[],
  prefix: string,
  candidatePath: string,
): string | null {
  const normalizedPrefix = normalizeRelativePath(prefix)
  const normalizedCandidatePath = normalizeRelativePath(candidatePath)
  const fullPath = normalizedCandidatePath
    ? `${normalizedPrefix}/${normalizedCandidatePath}`
    : normalizedPrefix

  const match = aliases.find(
    (entry) => typeof entry.path === 'string' && normalizeRelativePath(entry.path) === fullPath,
  )

  return match?.module ?? null
}
