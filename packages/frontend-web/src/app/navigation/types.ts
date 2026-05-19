import type { ComponentType } from 'react'

export type MCPInfo = {
  businessDomain: string
  scope: string
}

/** Persona-based roles for role-dependent nav filtering */
export type UserRole =
  | 'lagerist'
  | 'sachbearbeiter'
  | 'aussendienst'
  | 'disponent'
  | 'buchhalter'
  | 'geschaeftsfuehrung'
  | 'landwirt'
  | 'admin'

export type RawNavItem = {
  id: string
  label: string
  icon: ComponentType<{ className?: string }>
  module?: string
  preferredPath?: string
  path?: string
  keywords?: string[]
  mcp: MCPInfo
  featureKey?: 'agrar'
  /** When set, item is only shown to users with one of these roles */
  visibleToRoles?: UserRole[]
  children?: RawNavItem[]
}

export type NavItem = Omit<RawNavItem, 'children'> & {
  path?: string
  visibleToRoles?: UserRole[]
  children?: NavItem[]
}

export type NavigationShortcut = {
  id: string
  label: string
  icon: ComponentType<{ className?: string }>
  path: string
  keywords?: string[]
}

export type AiShortcut =
  | {
      id: string
      label: string
      icon: ComponentType<{ className?: string }>
      type: 'event'
      eventName: string
      keywords?: string[]
    }
  | {
      id: string
      label: string
      icon: ComponentType<{ className?: string }>
      type: 'navigate'
      path: string
      keywords?: string[]
    }
