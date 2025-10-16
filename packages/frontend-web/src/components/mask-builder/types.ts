// VALEO Mask Builder Types
// Typ-Definitionen für das wiederverwendbare Masken-Framework

export type MaskType = 'object-page' | 'list-report' | 'wizard' | 'worklist' | 'overview-page'

export type FieldType =
  | 'text'
  | 'number'
  | 'date'
  | 'datetime'
  | 'boolean'
  | 'select'
  | 'multiselect'
  | 'textarea'
  | 'file'
  | 'currency'
  | 'percentage'
  | 'lookup'
  | 'table'

export interface BaseField {
  name: string
  label: string
  type: FieldType
  required?: boolean
  readonly?: boolean
  placeholder?: string
  helpText?: string
  validation?: any
  defaultValue?: any
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
  options: Array<{ value: string | number; label: string }>
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
}

export interface Action {
  key: string
  label: string
  type: 'primary' | 'secondary' | 'danger'
  icon?: string
  onClick: () => void
  disabled?: boolean
}

export interface MaskConfig {
  title: string
  subtitle?: string
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
  validation?: any
  permissions?: string[]
}

export interface WizardStep {
  key: string
  title: string
  description?: string
  fields: Field[]
  validation?: any
  isOptional?: boolean
}

export interface WizardConfig extends Omit<MaskConfig, 'tabs' | 'type'> {
  type: 'wizard'
  steps: WizardStep[]
  onComplete: (data: any) => void
}

export interface ListColumn {
  key: string
  label: string
  sortable?: boolean
  filterable?: boolean
  render?: (value: any, row: any) => React.ReactNode
}

export interface ListConfig extends Omit<MaskConfig, 'tabs' | 'type'> {
  type: 'list-report'
  columns: ListColumn[]
  filters?: Field[]
  bulkActions?: Action[]
  defaultSort?: { field: string; direction: 'asc' | 'desc' }
  pageSize?: number
}

export interface WorklistItem {
  id: string
  title: string
  description?: string
  status: 'pending' | 'in-progress' | 'completed' | 'overdue'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  dueDate?: string
  assignedTo?: string
  metadata?: Record<string, any>
}

export interface WorklistAction {
  key: string
  label: string
  type?: 'primary' | 'secondary' | 'danger'
  icon?: string
  condition: (item: WorklistItem) => boolean
  onClick: (item: WorklistItem) => void
}

export interface WorklistConfig extends Omit<MaskConfig, 'tabs' | 'actions' | 'type'> {
  type: 'worklist'
  itemTemplate: (item: WorklistItem) => React.ReactNode
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
  data: any[]
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