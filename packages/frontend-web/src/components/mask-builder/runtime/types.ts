export interface TableQueryState {
  page: number
  pageSize: number
  sort?: string
  sortDir?: 'asc' | 'desc'
  q?: string
  filters?: Record<string, unknown>
}

export interface TableBinding {
  tableKey: string
  endpoint: string
  requiresServerQuery: boolean
  staleTimeMs?: number
}

export interface LookupBinding {
  fieldKey: string
  lookupEndpoint: string
  minSearchChars: number
  resultLimit: number
  cacheTtlMs: number
  debounceMs: number
}

export interface EntityBinding {
  entityId?: string
  entityEndpoint?: string
}

export interface ActionBinding {
  actionKey: string
  endpoint?: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  permission?: string
}

export interface DataBindingPlan {
  screenId: string
  entityBinding: EntityBinding
  tableBindings: Record<string, TableBinding>
  lookupBindings: Record<string, LookupBinding>
  actionBindings: Record<string, ActionBinding>
}
