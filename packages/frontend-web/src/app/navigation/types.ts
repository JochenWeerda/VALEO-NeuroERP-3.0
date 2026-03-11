import type { ComponentType } from 'react'

export type MCPInfo = {
  businessDomain: string
  scope: string
}

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
  children?: RawNavItem[]
}

export type NavItem = Omit<RawNavItem, 'children'> & {
  path?: string
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
