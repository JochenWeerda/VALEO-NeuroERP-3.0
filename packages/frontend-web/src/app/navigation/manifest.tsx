import { ACTION_SHORTCUTS } from '@/app/navigation/action-shortcuts'
import { AI_SHORTCUTS } from '@/app/navigation/ai-shortcuts'
import { RAW_NAV_SECTIONS as CORE_NAV_SECTIONS } from '@/app/navigation/domains/core'
import { RAW_NAV_SECTIONS as COMMERCIAL_NAV_SECTIONS } from '@/app/navigation/domains/commercial'
import { RAW_NAV_SECTIONS as FINANCE_NAV_SECTIONS } from '@/app/navigation/domains/finance'
import { RAW_NAV_SECTIONS as OPERATIONS_NAV_SECTIONS } from '@/app/navigation/domains/operations'
import { flattenNavItems, resolveNavItem } from '@/app/navigation/nav-resolver'
import type { ActionShortcut } from '@/app/navigation/action-shortcuts'
import type { AiShortcut, NavItem, NavigationShortcut, RawNavItem } from '@/app/navigation/types'

export type { AiShortcut, MCPInfo, NavItem, NavigationShortcut, RawNavItem } from '@/app/navigation/types'
export { ACTION_SHORTCUTS }
export type { ActionShortcut }
export { AI_SHORTCUTS }

const NAV_SECTIONS_CONFIG: RawNavItem[] = [
  ...CORE_NAV_SECTIONS,
  ...COMMERCIAL_NAV_SECTIONS,
  ...FINANCE_NAV_SECTIONS,
  ...OPERATIONS_NAV_SECTIONS,
]

export const NAV_SECTIONS: NavItem[] = NAV_SECTIONS_CONFIG.map(resolveNavItem)
export const NAV_LINKS: NavItem[] = flattenNavItems(NAV_SECTIONS)
export const NAVIGATION_SHORTCUTS: NavigationShortcut[] = NAV_LINKS.filter(
  (item): item is NavItem & { path: string } => Boolean(item.path),
).map((item) => ({
  id: item.id,
  label: item.label,
  icon: item.icon,
  path: item.path,
  keywords: item.keywords,
}))
