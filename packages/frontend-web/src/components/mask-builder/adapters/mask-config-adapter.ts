import type { MaskConfig, Field, Tab } from '../types'
import type {
  ScreenActionDefinition,
  ScreenDefinition,
  ScreenFieldDefinition,
  ScreenMode,
  ScreenTabDefinition,
} from '../schema'

function screenOptions(value: unknown): Array<{ value: string | number; label: string }> | undefined {
  if (!Array.isArray(value)) return undefined
  const options = value
    .map((option) => {
      if (option === null || typeof option !== 'object') return null
      const record = option as Record<string, unknown>
      const rawValue = record.value
      if (typeof rawValue !== 'string' && typeof rawValue !== 'number') return null
      return {
        value: rawValue,
        label: typeof record.label === 'string' ? record.label : String(rawValue),
      }
    })
    .filter((option): option is { value: string | number; label: string } => option !== null)
  return options.length > 0 ? options : undefined
}

function toScreenMode(type: MaskConfig['type']): ScreenMode {
  if (type === 'list-report') return 'list'
  if (type === 'overview-page') return 'cockpit'
  if (type === 'object-page') return 'detail'
  if (type === 'worklist') return 'workflow'
  return 'wizard'
}

function fieldKey(field: Field): string {
  return String(field.name ?? field.key ?? field.label)
}

function toScreenField(field: Field): ScreenFieldDefinition {
  return {
    key: fieldKey(field),
    label: field.label,
    type: field.type === 'checkbox' ? 'boolean' : field.type,
    required: field.required,
    readOnly: field.readonly ?? field.readOnly,
    placeholder: field.placeholder,
    helpText: field.helpText,
    options: 'options' in field ? screenOptions(field.options) : undefined,
    dataSourceKey: field.type === 'lookup' ? fieldKey(field) : undefined,
    minSearchChars: field.type === 'lookup' ? 2 : undefined,
  }
}

function toScreenTab(tab: Tab): ScreenTabDefinition {
  return {
    key: tab.key,
    label: tab.label,
    lazy: true,
    keepAlive: true,
    fields: tab.fields.map(toScreenField),
  }
}

function toScreenAction(action: MaskConfig['actions'][number]): ScreenActionDefinition {
  return {
    key: action.key,
    label: action.label,
    kind: action.type === 'primary' ? 'primary' : action.type === 'danger' || action.type === 'destructive' ? 'danger' : 'secondary',
    disabled: action.disabled,
  }
}

export function adaptMaskConfigToScreenDefinition(
  config: MaskConfig,
  options: {
    id: string
    domain?: ScreenDefinition['domain']
    sourceId?: string
    summaryEndpoint?: string
  },
): ScreenDefinition {
  return {
    schemaVersion: 1,
    id: options.id,
    domain: options.domain ?? 'platform',
    mode: toScreenMode(config.type),
    title: config.title,
    subtitle: config.subtitle,
    permissions: config.permissions,
    adapter: {
      type: 'maskConfig',
      sourceId: options.sourceId ?? options.id,
      temporary: true,
      deprecationTarget: 'native ScreenDefinition',
    },
    summaryEndpoint: options.summaryEndpoint,
    tabs: config.tabs.map(toScreenTab),
    actions: config.actions.map(toScreenAction),
    dataSources: [
      {
        key: 'primary',
        endpoint: config.api.baseUrl,
        staleTimeMs: 5 * 60_000,
        pageSize: 50,
      },
    ],
    layout: {
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      touchTargetPx: 44,
    },
    performance: {
      initialPayloadBudgetKb: 64,
      requiresLazyTabs: config.tabs.length > 1,
      requiresVirtualTables: false,
      lookupMinChars: 2,
      bundleGroup: options.domain ?? 'platform',
    },
  }
}
