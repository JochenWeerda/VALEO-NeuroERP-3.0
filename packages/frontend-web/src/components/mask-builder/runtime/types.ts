export type FilterOperator =
  | 'eq'      // exact match
  | 'neq'     // not equal
  | 'lt'      // less than
  | 'lte'     // less than or equal
  | 'gt'      // greater than
  | 'gte'     // greater than or equal
  | 'contains' // string contains (case-insensitive)
  | 'in'      // value in list
  | 'between' // range [from, to]

export interface FilterValue {
  op: FilterOperator
  value: unknown
  /** human-readable label for filter chips */
  label?: string
}

/** Machine-readable filter structure — both human UI chips and agent queries derive from this */
export interface FilterPlan {
  [columnKey: string]: FilterValue
}

export interface TableQueryState {
  page: number
  pageSize: number
  sort?: string
  sortDir?: 'asc' | 'desc'
  q?: string
  /** Structured per-column filters. Serialized as filterPlan=<JSON> in query params. */
  filterPlan?: FilterPlan
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
