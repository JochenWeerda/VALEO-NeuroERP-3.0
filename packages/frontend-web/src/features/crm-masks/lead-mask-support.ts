import type { MaskConfig, Field } from '@/components/mask-builder/types'
import leadMaskConfig from '@/config/mask-builder-lead.json'
import type { Lead } from '@/lib/services/crm-service'
import {
  mapLeadToMask,
  mapMaskToLead,
  type MaskLeadData,
} from '@/features/crm-masks/mappers'

type LeadMaskConfig = typeof leadMaskConfig
type LeadMaskTab = LeadMaskConfig['tabs'][number]
type LeadMaskField = LeadMaskTab['sections'][number]['fields'][number]

const COMPONENT_TO_FIELD_TYPE: Record<string, Field['type']> = {
  TextField: 'text',
  TextArea: 'textarea',
  Select: 'select',
  DatePicker: 'date',
  Checkbox: 'boolean',
  Switch: 'boolean',
}

export const ENABLE_LEAD_MASK_BUILDER_FORM =
  import.meta.env.VITE_ENABLE_MASK_BUILDER_LEAD_FORM === 'true'

export const LEAD_MASK_OBJECT_PAGE_CONFIG: MaskConfig = convertLeadMaskToObjectPageConfig(
  leadMaskConfig,
)

export function validateLeadPayload(payload: Partial<Lead>): string | null {
  if (!payload.company) {
    return 'Firma ist erforderlich.'
  }
  if (!payload.contactPerson) {
    return 'Ansprechpartner ist erforderlich.'
  }
  if (!payload.source) {
    return 'Quelle ist erforderlich.'
  }
  return null
}

export { mapLeadToMask, mapMaskToLead, type MaskLeadData }

function convertLeadMaskToObjectPageConfig(config: LeadMaskConfig): MaskConfig {
  return {
    title: 'Lead bearbeiten',
    subtitle: 'CRM Mask Builder (Beta)',
    type: 'object-page',
    tabs: (config.tabs ?? []).map((tab) => ({
      key: tab.id,
      label: tab.label,
      columns: resolveTabColumns(tab),
      fields:
        tab.sections?.flatMap((section) =>
          section.fields.map((field) => convertLeadMaskField(field, section.label)),
        ) ?? [],
    })),
    actions: [],
    api: {
      baseUrl: '',
      endpoints: {},
    },
  }
}

function resolveTabColumns(tab: LeadMaskTab): number {
  const sectionColumns = tab.sections?.map((section) => section.layout?.columns ?? 2) ?? []
  return sectionColumns.length ? Math.max(...sectionColumns) : 2
}

function convertLeadMaskField(field: LeadMaskField, sectionLabel: string): Field {
  const type = COMPONENT_TO_FIELD_TYPE[field.component] ?? 'text'

  if (type === 'select') {
    return {
      name: field.binding,
      label: field.label,
      type: 'select',
      required: Boolean(field.required),
      readonly: Boolean(field.readonly),
      helpText: sectionLabel,
      placeholder: field.optionsRef ? `Optionen: ${field.optionsRef}` : undefined,
      options: [],
    }
  }

  return {
    name: field.binding,
    label: field.label,
    type,
    required: Boolean(field.required),
    readonly: Boolean(field.readonly),
    helpText: sectionLabel,
  } as Field
}
