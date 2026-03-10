import { useEffect, useState } from 'react'
import type { NavItem, NavigationShortcut, RawNavItem } from '@/app/navigation/types'
import { flattenNavItems, resolveNavItem } from '@/app/navigation/nav-resolver'

const NAV_DOMAIN_LOADERS = {
  core: () => import('./domains/core'),
  commercial: () => import('./domains/commercial'),
  finance: () => import('./domains/finance'),
  operations: () => import('./domains/operations'),
} as const

const NAV_DOMAIN_ORDER = ['core', 'commercial', 'finance', 'operations'] as const

type DomainName = (typeof NAV_DOMAIN_ORDER)[number]

type DomainModule = {
  RAW_NAV_SECTIONS: RawNavItem[]
}

let navSectionsPromise: Promise<NavItem[]> | null = null
let navShortcutsPromise: Promise<NavigationShortcut[]> | null = null

async function loadRawSections(): Promise<RawNavItem[]> {
  const modules = await Promise.all(
    NAV_DOMAIN_ORDER.map((domain) => NAV_DOMAIN_LOADERS[domain as DomainName]()),
  )
  return modules.flatMap((module) => (module as DomainModule).RAW_NAV_SECTIONS)
}

export function loadNavSections(): Promise<NavItem[]> {
  if (!navSectionsPromise) {
    navSectionsPromise = loadRawSections().then((items) => items.map(resolveNavItem))
  }
  return navSectionsPromise
}

export function loadNavigationShortcuts(): Promise<NavigationShortcut[]> {
  if (!navShortcutsPromise) {
    navShortcutsPromise = loadNavSections().then((sections) =>
      flattenNavItems(sections)
        .filter((item): item is NavItem & { path: string } => Boolean(item.path))
        .map((item) => ({
          id: item.id,
          label: item.label,
          icon: item.icon,
          path: item.path,
          keywords: item.keywords,
        })),
    )
  }
  return navShortcutsPromise
}

export function useNavSections(): NavItem[] {
  const [sections, setSections] = useState<NavItem[]>([])

  useEffect(() => {
    let active = true
    void loadNavSections().then((result) => {
      if (active) {
        setSections(result)
      }
    })
    return () => {
      active = false
    }
  }, [])

  return sections
}

export function useNavigationShortcuts(): NavigationShortcut[] {
  const [shortcuts, setShortcuts] = useState<NavigationShortcut[]>([])

  useEffect(() => {
    let active = true
    void loadNavigationShortcuts().then((result) => {
      if (active) {
        setShortcuts(result)
      }
    })
    return () => {
      active = false
    }
  }, [])

  return shortcuts
}
