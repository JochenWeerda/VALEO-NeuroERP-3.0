export type SidebarPageModuleFactory = () => Promise<unknown>
export type SidebarPageModuleMap = Record<string, SidebarPageModuleFactory>
