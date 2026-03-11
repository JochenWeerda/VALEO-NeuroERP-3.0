import type { PageModule, PageModuleFactory } from '@/app/route-builders/types'

export type PageModuleGroup = Record<string, PageModuleFactory>
export type PageModuleGroupModule = { PAGE_MODULES: PageModuleGroup }

export type PageModuleGlob = Record<string, () => Promise<PageModule>>
