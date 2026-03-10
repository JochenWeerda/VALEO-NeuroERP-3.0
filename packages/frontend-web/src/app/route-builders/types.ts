import type { ComponentType } from 'react'

export type PageModule = { default: ComponentType<unknown> }
export type PageModuleFactory = () => Promise<PageModule>

export type RouteAliasEntry = {
  module: string
  path?: string
  index?: boolean
}

export type AliasGroupRouteEntry = {
  module: string
  path: string
}

export type AliasGroupEntriesModule = {
  entries: AliasGroupRouteEntry[]
}

export type AutoGroupRouteEntry = {
  module: string
  path: string
}

export type AutoGroupEntriesModule = {
  entries: AutoGroupRouteEntry[]
}
