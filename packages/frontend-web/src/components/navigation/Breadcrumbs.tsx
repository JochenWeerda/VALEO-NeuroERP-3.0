/**
 * Automatic Breadcrumb Navigation
 *
 * Derives breadcrumb items from the current URL path and the navigation manifest.
 * Falls back to capitalised path segments when no manifest match is found.
 */

import { Link, useRouterState } from '@tanstack/react-router'
import { ChevronRight, Home } from 'lucide-react'
import { useNavSections } from '@/app/navigation/nav-runtime'
import type { NavItem } from '@/app/navigation/types'

type BreadcrumbItem = {
  label: string
  path?: string
}

/** Pretty-print a URL segment: "offene-posten" → "Offene Posten" */
function humanise(segment: string): string {
  return segment
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

type ManifestPathMatch = {
  sectionId?: string
  sectionLabel?: string
  itemId: string
  itemLabel: string
  path: string
  exact: boolean
  sectionMatchesRoot: boolean
}

/** Walk the manifest tree and find the best label for a given path. */
export function findLabelInManifest(
  items: NavItem[],
  targetPath: string,
): { sectionLabel?: string; itemLabel?: string } {
  const normalizedTarget = targetPath.replace(/^\/+|\/+$/g, '')
  const rootSegment = normalizedTarget.split('/')[0] ?? ''
  const candidates: ManifestPathMatch[] = []

  function visit(item: NavItem, section: NavItem): void {
    const itemPath = item.path?.replace(/^\/+|\/+$/g, '') ?? ''
    if (itemPath) {
      const exact = normalizedTarget === itemPath
      const isParentPath = normalizedTarget.startsWith(`${itemPath}/`)
      if (exact || isParentPath) {
        const isTopLevelMatch = item.id === section.id
        candidates.push({
          sectionId: isTopLevelMatch ? undefined : section.id,
          sectionLabel: isTopLevelMatch ? undefined : section.label,
          itemId: item.id,
          itemLabel: item.label,
          path: itemPath,
          exact,
          sectionMatchesRoot: section.id === rootSegment || section.id.startsWith(rootSegment),
        })
      }
    }

    for (const child of item.children ?? []) {
      visit(child, section)
    }
  }

  for (const section of items) {
    visit(section, section)
  }

  const best = candidates.sort((a, b) => {
    if (a.exact !== b.exact) return a.exact ? -1 : 1
    if (a.path.length !== b.path.length) return b.path.length - a.path.length
    if (a.sectionMatchesRoot !== b.sectionMatchesRoot) return a.sectionMatchesRoot ? -1 : 1
    return 0
  })[0]

  return best ? { sectionLabel: best.sectionLabel, itemLabel: best.itemLabel } : {}
}

export function Breadcrumbs() {
  const matches = useRouterState({ select: (state) => state.matches })
  const navSections = useNavSections()
  const leafMatch = matches.at(-1)
  const pathname = leafMatch?.pathname.replace(/^\//, '') ?? ''
  const routeLabel = (leafMatch?.staticData as { breadcrumb?: string } | undefined)?.breadcrumb

  // Don't render on root/dashboard
  if (!pathname || pathname === '/') {
    return null
  }

  const segments = pathname.split('/').filter(Boolean)
  const crumbs: BreadcrumbItem[] = [{ label: 'Home', path: '/' }]

  // Try manifest lookup for the full path
  const { sectionLabel, itemLabel } = findLabelInManifest(navSections, pathname)

  if (sectionLabel) {
    // We found a parent section
    crumbs.push({ label: sectionLabel, path: `/${segments[0]}` })
  }

  if (routeLabel || itemLabel) {
    crumbs.push({ label: routeLabel ?? itemLabel ?? humanise(segments.at(-1) ?? '') })
  } else {
    // Fallback: build from URL segments
    let currentPath = ''
    for (let i = 0; i < segments.length; i++) {
      currentPath += `/${segments[i]}`
      const isLast = i === segments.length - 1
      crumbs.push({
        label: humanise(segments[i]),
        path: isLast ? undefined : currentPath,
      })
    }
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm text-muted-foreground px-6 pt-3 pb-0">
      {crumbs.map((crumb, i) => {
        const isLast = i === crumbs.length - 1
        return (
          <span key={i} className="flex items-center gap-1.5">
            {i > 0 && <ChevronRight className="h-3.5 w-3.5 shrink-0" />}
            {crumb.path && !isLast ? (
              <Link
                to={crumb.path}
                className="hover:text-foreground transition-colors"
                aria-label={i === 0 ? 'Home' : undefined}
              >
                {i === 0 ? <Home className="h-3.5 w-3.5" aria-hidden="true" /> : crumb.label}
              </Link>
            ) : (
              <span className={isLast ? 'font-medium text-foreground' : ''}>
                {i === 0 ? <Home className="h-3.5 w-3.5" aria-hidden="true" /> : crumb.label}
              </span>
            )}
          </span>
        )
      })}
    </nav>
  )
}

