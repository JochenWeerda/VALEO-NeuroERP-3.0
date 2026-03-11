import { matchPath } from 'react-router-dom'
import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

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
  const match = [...entries]
    .sort(compareAliasEntries)
    .find((entry) => matchPath({ path: entry.path || '/', end: true }, candidatePath))

  return match?.module ?? null
}
