/**
 * Automatic Breadcrumb Navigation
 *
 * Derives breadcrumb items from the current URL path and the navigation manifest.
 * Falls back to capitalised path segments when no manifest match is found.
 */

import { Link, useLocation } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'
import { NAV_SECTIONS, type NavItem } from '@/app/navigation/manifest'

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

/** Walk the manifest tree and find the label for a given path. */
function findLabelInManifest(
  items: NavItem[],
  targetPath: string,
): { sectionLabel?: string; itemLabel?: string } {
  for (const section of items) {
    // Check children first
    if (section.children) {
      for (const child of section.children) {
        const childPath = child.path?.replace(/^\//, '') ?? ''
        if (childPath && targetPath.startsWith(childPath)) {
          // Nested children
          if (child.children) {
            for (const grandchild of child.children) {
              const gcPath = grandchild.path?.replace(/^\//, '') ?? ''
              if (gcPath && targetPath === gcPath) {
                return { sectionLabel: section.label, itemLabel: grandchild.label }
              }
            }
          }
          return { sectionLabel: section.label, itemLabel: child.label }
        }
      }
    }
    // Check section itself
    const sectionPath = section.path?.replace(/^\//, '') ?? ''
    if (sectionPath && targetPath === sectionPath) {
      return { itemLabel: section.label }
    }
  }
  return {}
}

export function Breadcrumbs() {
  const location = useLocation()
  const pathname = location.pathname.replace(/^\//, '')

  // Don't render on root/dashboard
  if (!pathname || pathname === '/') {
    return null
  }

  const segments = pathname.split('/').filter(Boolean)
  const crumbs: BreadcrumbItem[] = [{ label: 'Home', path: '/' }]

  // Try manifest lookup for the full path
  const { sectionLabel, itemLabel } = findLabelInManifest(NAV_SECTIONS, pathname)

  if (sectionLabel) {
    // We found a parent section
    crumbs.push({ label: sectionLabel, path: `/${segments[0]}` })
  }

  if (itemLabel) {
    crumbs.push({ label: itemLabel })
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
              >
                {i === 0 ? <Home className="h-3.5 w-3.5" /> : crumb.label}
              </Link>
            ) : (
              <span className={isLast ? 'font-medium text-foreground' : ''}>
                {i === 0 ? <Home className="h-3.5 w-3.5" /> : crumb.label}
              </span>
            )}
          </span>
        )
      })}
    </nav>
  )
}

