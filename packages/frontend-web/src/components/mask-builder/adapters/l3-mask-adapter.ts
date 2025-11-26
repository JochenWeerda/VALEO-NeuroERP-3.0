/**
 * L3 Mask Builder Adapter
 * Konvertiert die L3 Mask-Builder JSON-Konfiguration in die bestehende MaskConfig-Struktur
 */

import { MaskConfig, Tab, Field, Action, NumberField, SelectField, BaseField } from '../types'
// @ts-ignore - JSON import
import l3MaskConfig from '../../../config/mask-builder-valeo-modern.json'

// Typ für die L3 Mask-Builder JSON-Struktur
interface L3Field {
  comp: string
  bind: string
  label: string
  type?: string
  size?: string
  validators?: string[]
  optional?: boolean
  aiAssist?: {
    from: string[]
    prompt: string
  }
  aiValidate?: {
    tool: string
    argsMap: Record<string, string>
  }
  postAction?: string
  optionsRef?: string
  options?: string[]
  width?: string
  span?: number
}

interface L3Section {
  title: string
  grid?: number
  fields: L3Field[]
}

interface L3View {
  id: string
  sections?: L3Section[]
  tabs?: Array<{
    id: string
    label: string
    sections: L3Section[]
  }>
}

interface L3MaskConfig {
  resource: string
  version: string
  routing: {
    basePath: string
    param: string
  }
  layout: {
    header: {
      primary: L3Field[]
      secondary: L3Field[]
      actions: Array<{
        id: string
        label: string
        type: string
      }>
    }
    nav: Array<{
      id: string
      label: string
      icon: string
    }>
  }
  views: L3View[]
  validation?: {
    rules: Record<string, any>
  }
  ui?: {
    responsive: boolean
    breakpoints: Record<string, any>
    touch?: Record<string, any>
    performance?: Record<string, any>
    offline?: Record<string, any>
    lowAttentionMode?: Record<string, any>
    a11y?: Record<string, any>
  }
  ai?: {
    enabled: boolean
    intentBar?: {
      shortcut: string
      actions: Array<{
        id: string
        label: string
        inputs?: string[]
        writes?: string[]
        context?: string[]
        sidePanel?: string
        tool?: string
        generative?: boolean
        template?: string
      }>
    }
    validators?: Array<{
      id: string
      on?: string[]
      fields?: string[]
      severity?: string
      message?: string
    }>
    ragPanels?: Record<string, any>
    mcp?: {
      tools: Array<{
        name: string
        args: string[]
      }>
    }
    telemetry?: Record<string, boolean>
    roleContext?: {
      enabled: boolean
      weightedSuggestions: Record<string, string[]>
    }
    serverEndpoints?: Record<string, any>
  }
}

// Hilfsfunktion: L3 Field Type zu Mask Builder Field Type
function convertFieldType(l3Type: string | undefined): string {
  const typeMap: Record<string, string> = {
    'Text': 'text',
    'Email': 'text',
    'Url': 'text',
    'Select': 'select',
    'BadgeSelect': 'select',
    'MultiSelect': 'multiselect',
    'Toggle': 'boolean',
    'Number': 'number',
    'Date': 'date',
    'DateTime': 'datetime',
    'TextArea': 'textarea',
    'RichText': 'textarea',
    'File': 'file',
    'CountrySelect': 'select',
    'TagList': 'multiselect',
    'AddressMirrorToggle': 'boolean',
    'AuditLog': 'textarea'
  }
  return typeMap[l3Type || 'Text'] || 'text'
}

// Konvertiert ein L3-Feld in ein Mask-Builder-Feld
function convertField(l3Field: L3Field): Field {
  const baseField: Field = {
    name: l3Field.bind.split('.').pop() || l3Field.bind,
    label: l3Field.label,
    type: convertFieldType(l3Field.comp) as any,
    required: !l3Field.optional && l3Field.validators?.includes('required'),
    readonly: false,
    placeholder: l3Field.label,
    validation: l3Field.validators || []
  }

  // Spezielle Typen
  if (l3Field.comp === 'Select' || l3Field.comp === 'BadgeSelect' || l3Field.comp === 'CountrySelect') {
    return {
      ...baseField,
      type: 'select',
      ...(l3Field.options && {
        options: l3Field.options.map(opt => ({ value: opt, label: opt }))
      })
    } as SelectField
  }

  if (l3Field.comp === 'MultiSelect' || l3Field.comp === 'TagList') {
    return {
      ...baseField,
      type: 'multiselect',
      ...(l3Field.options && {
        options: l3Field.options.map(opt => ({ value: opt, label: opt }))
      })
    } as SelectField
  }

  if (l3Field.comp === 'Toggle' || l3Field.comp === 'AddressMirrorToggle') {
    return {
      ...baseField,
      type: 'boolean'
    } as BaseField
  }

  if (l3Field.comp === 'Number') {
    return {
      ...baseField,
      type: 'number'
    } as NumberField
  }

  if (l3Field.comp === 'Date') {
    return {
      ...baseField,
      type: 'date'
    } as BaseField
  }

  if (l3Field.comp === 'DateTime') {
    return {
      ...baseField,
      type: 'datetime'
    } as BaseField
  }

  if (l3Field.comp === 'TextArea' || l3Field.comp === 'RichText') {
    return {
      ...baseField,
      type: 'textarea'
    } as BaseField
  }

  return baseField
}

// Konvertiert Sections zu Tabs
function _convertSectionsToTabs(view: L3View): Tab[] {
  if (view.tabs) {
    return view.tabs.map(tab => ({
      key: tab.id,
      label: tab.label,
      fields: tab.sections.flatMap(section => section.fields.map(convertField)),
      layout: 'grid' as const,
      columns: 3
    }))
  } else if (view.sections) {
    return [{
      key: view.id,
      label: view.id.charAt(0).toUpperCase() + view.id.slice(1),
      fields: view.sections.flatMap(section => section.fields.map(convertField)),
      layout: 'grid' as const,
      columns: 3
    }]
  }
  return []
}

// Konvertiert Actions
function convertActions(l3Actions: Array<{ id: string; label: string; type: string }>): Action[] {
  return l3Actions.map(action => ({
    key: action.id,
    label: action.label,
    type: action.type === 'primary' ? 'primary' : action.type === 'menu' ? 'secondary' : 'secondary',
    onClick: () => {
      console.log(`Action ${action.id} clicked`)
      // TODO: Implementiere Action-Handler
    }
  }))
}

// Hauptfunktion: Konvertiert L3 Mask-Builder JSON zu MaskConfig
export function convertL3MaskToMaskConfig(): MaskConfig {
  const l3Config = l3MaskConfig as L3MaskConfig

  // Konvertiere ALLE Views zu Tabs
  const allTabs: Tab[] = []
  
  l3Config.views.forEach(view => {
    if (view.tabs) {
      // Wenn die View Tabs hat, konvertiere alle Tabs
      view.tabs.forEach(tab => {
        allTabs.push({
          key: `${view.id}-${tab.id}`,
          label: tab.label,
          fields: tab.sections.flatMap(section => section.fields.map(convertField)),
          layout: 'grid' as const,
          columns: 3
        })
      })
    } else if (view.sections) {
      // Wenn die View Sections hat, erstelle einen Tab
      allTabs.push({
        key: view.id,
        label: view.id.charAt(0).toUpperCase() + view.id.slice(1).replace(/([A-Z])/g, ' $1').trim(),
        fields: view.sections.flatMap(section => section.fields.map(convertField)),
        layout: 'grid' as const,
        columns: 3
      })
    }
  })
  
  return {
    title: l3Config.resource.charAt(0).toUpperCase() + l3Config.resource.slice(1),
    subtitle: `CRM ${l3Config.resource}`,
    type: 'object-page',
    tabs: allTabs,
    actions: convertActions(l3Config.layout.header.actions),
    api: {
      baseUrl: '/api/v1',
      endpoints: {
        list: `${l3Config.routing.basePath}`,
        get: `${l3Config.routing.basePath}/:${l3Config.routing.param}`,
        create: `${l3Config.routing.basePath}`,
        update: `${l3Config.routing.basePath}/:${l3Config.routing.param}`,
        delete: `${l3Config.routing.basePath}/:${l3Config.routing.param}`
      }
    },
    validation: l3Config.validation?.rules || {}
  }
}

// Exportiere auch die L3-Konfiguration direkt für erweiterte Nutzung
export { l3MaskConfig }
export type { L3MaskConfig }
export type { L3Field }
export type { L3Section }
export type { L3View }

