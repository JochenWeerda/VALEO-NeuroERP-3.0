// VALEO Mask Builder Types

export type MaskType = 'object-page' | 'list-report' | 'wizard' | 'worklist' | 'overview-page'

export type FieldType =
  | 'text'
  | 'number'
  | 'date'
  | 'datetime'
  | 'boolean'
  | 'checkbox'
  | 'select'
  | 'multiselect'
  | 'textarea'
  | 'file'
  | 'currency'
  | 'percentage'
  | 'lookup'
  | 'table'
  | 'custom'

export interface BaseField {
  name?: string
  key?: string
  label: string
  labelKey?: string
  type: FieldType
  required?: boolean
  readonly?: boolean
  readOnly?: boolean
  placeholder?: string
  placeholderKey?: string
  helpText?: string
  helpTextKey?: string
  validation?: unknown
  defaultValue?: unknown
  default?: unknown
  rows?: number
  [key: string]: unknown
}

export interface TextField extends BaseField {
  type: 'text'
  minLength?: number
  maxLength?: number
}

export interface NumberField extends BaseField {
  type: 'number'
  min?: number
  max?: number
  step?: number
}

export interface SelectField extends BaseField {
  type: 'select'
  options: Array<{ value: string | number; label: string; labelKey?: string }>
  multiple?: boolean
}

export interface LookupField extends BaseField {
  type: 'lookup'
  endpoint: string
  displayField: string
  valueField: string
  searchFields?: string[]
}

export interface TableField extends BaseField {
  type: 'table'
  columns: Array<{
    key: string
    label: string
    type: FieldType
    required?: boolean
  }>
  minRows?: number
  maxRows?: number
}

export type Field = TextField | NumberField | SelectField | LookupField | TableField | BaseField

export interface Tab {
  key: string
  label: string
  fields: Field[]
  layout?: 'grid' | 'flex'
  columns?: number
  customRender?: (_data: Record<string, unknown>, _onChange: (_data: Record<string, unknown>) => void) => React.ReactNode
}

type ActionPayload = Record<string, unknown> | Record<string, unknown>[]
type ActionClickHandler = {
  bivarianceHack(_payload?: ActionPayload): unknown | Promise<unknown>
}['bivarianceHack']

export interface Action {
  key: string
  label: string
  labelKey?: string
  type?: 'primary' | 'secondary' | 'danger' | 'default' | 'destructive' | 'outline'
  icon?: string
  onClick?: ActionClickHandler
  disabled?: boolean
  [key: string]: unknown
}

export interface MaskConfig {
  title: string
  titleKey?: string
  subtitle?: string
  subtitleKey?: string
  type: MaskType
  tabs: Tab[]
  actions: Action[]
  api: {
    baseUrl: string
    endpoints: {
      list?: string
      get?: string
      create?: string
      update?: string
      delete?: string
    }
  }
  validation?: unknown
  permissions?: string[]
  domain?: string
}

export interface WizardStep {
  key: string
  title: string
  description?: string
  fields: Field[]
  validation?: unknown
  isOptional?: boolean
}

export interface WizardConfig extends Omit<MaskConfig, 'tabs' | 'type'> {
  type: 'wizard'
  steps: WizardStep[]
  onComplete: (_data: Record<string, unknown>) => void
}

export interface ListColumn {
  key: string
  label: string
  labelKey?: string
  sortable?: boolean
  filterable?: boolean
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  render?: (_value: any, _row: any) => React.ReactNode
}

export interface EmptyStateConfig {
  icon?: string
  title: string
  description?: string
  actionLabel?: string
}

export interface ListConfig extends Omit<MaskConfig, 'tabs' | 'type'> {
  type: 'list-report'
  columns: ListColumn[]
  filters?: Array<Field & { labelKey?: string; placeholderKey?: string }>
  bulkActions?: Array<Action & { labelKey?: string }>
  defaultSort?: { field: string; direction: 'asc' | 'desc' }
  pageSize?: number
  serverPagination?: boolean
  /** Custom empty state shown when list has no data */
  emptyState?: EmptyStateConfig
}

export interface WorklistItem {
  id: string
  title: string
  description?: string
  status: 'pending' | 'in-progress' | 'completed' | 'overdue'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  dueDate?: string
  assignedTo?: string
  metadata?: Record<string, unknown>
}

export interface WorklistAction {
  key: string
  label: string
  type?: 'primary' | 'secondary' | 'danger'
  icon?: string
  condition: (_item: WorklistItem) => boolean
  onClick: (_item: WorklistItem) => void
}

export interface WorklistConfig extends Omit<MaskConfig, 'tabs' | 'actions' | 'type'> {
  type: 'worklist'
  itemTemplate: (_item: WorklistItem) => React.ReactNode
  actions: WorklistAction[]
  filters?: Field[]
  groupBy?: string
}

export interface OverviewCard {
  title: string
  value: string | number
  change?: {
    value: number
    type: 'increase' | 'decrease'
    period: string
  }
  icon?: string
  color?: string
}

export interface OverviewChart {
  title: string
  type: 'line' | 'bar' | 'pie' | 'area'
  data: unknown[]
  xAxis?: string
  yAxis?: string
}

export interface OverviewConfig extends Omit<MaskConfig, 'tabs' | 'type'> {
  type: 'overview-page'
  cards: OverviewCard[]
  charts: OverviewChart[]
  sections?: Array<{
    title: string
    content: React.ReactNode
  }>
}
