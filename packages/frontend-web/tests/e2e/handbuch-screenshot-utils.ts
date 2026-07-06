import * as fs from 'node:fs'
import * as path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export const PLACEHOLDER = 'demo-1'
export const ADMIN_PREFIXES = ['admin', 'admin-suite', 'api-docs', 'mcp'] as const

export interface RouteInventoryEntry {
  path: string
  module: string
  source?: string
}

export interface CaptureRoute {
  path: string
  module: string
  slug: string
  urlPath: string
}

export function resolveRoutePath(routePath: string): string {
  return routePath.replace(/:\w+|\{[^}]+\}/g, PLACEHOLDER)
}

export function normalizeRoutePath(routePath: string): string {
  return routePath.trim().replace(/^\/+|\/+$/g, '').toLowerCase()
}

export function routeToImgSlug(routePath: string): string {
  const resolved = resolveRoutePath(routePath)
  if (!resolved) return 'start-dashboard'
  let slug = resolved.toLowerCase().replace(/\//g, '__')
  slug = slug.replace(/[^a-z0-9_-]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '')
  return slug.slice(0, 140) || 'route'
}

export function isAdminRoute(routePath: string): boolean {
  const p = normalizeRoutePath(routePath)
  return ADMIN_PREFIXES.some((prefix) => p === prefix || p.startsWith(`${prefix}/`))
}

export function isCaptureRoute(routePath: string): boolean {
  if (isAdminRoute(routePath)) return false
  const p = normalizeRoutePath(routePath)
  if (p === 'auth/callback' || p === 'auth/login') return false
  return true
}

export function loadCaptureRoutes(): CaptureRoute[] {
  const inventoryPath = path.join(
    __dirname,
    '../../src/app/routing/route-inventory.gen.json',
  )
  const data = JSON.parse(fs.readFileSync(inventoryPath, 'utf-8')) as {
    routes: RouteInventoryEntry[]
  }

  const seen = new Set<string>()
  const routes: CaptureRoute[] = []

  for (const entry of data.routes) {
    const routePath = entry.path ?? ''
    if (!isCaptureRoute(routePath)) continue
    const key = normalizeRoutePath(routePath)
    if (seen.has(key)) continue
    seen.add(key)

    const urlPath = resolveRoutePath(routePath)
    routes.push({
      path: routePath,
      module: entry.module ?? '',
      slug: routeToImgSlug(routePath),
      urlPath,
    })
  }

  return routes.sort((a, b) => a.path.localeCompare(b.path))
}

export function imgOutputPaths(repoRoot: string, slug: string): { png: string; webp: string } {
  const imgDir = path.join(repoRoot, 'docs/benutzerhandbuch/img')
  return {
    png: path.join(imgDir, `${slug}.png`),
    webp: path.join(imgDir, `${slug}.webp`),
  }
}
