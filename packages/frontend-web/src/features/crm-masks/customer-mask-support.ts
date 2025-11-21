import type { MaskConfig, Field } from '@/components/mask-builder/types'
import customerMaskConfig from '@/config/mask-builder-customer.json'
import type { CustomerCreate } from '@/lib/api/crm'
import { ENABLE_PROSPECTING_UI } from '@/features/prospecting/feature-flags'
import { getNested } from './mappers'

type CustomerMaskConfig = typeof customerMaskConfig
type CustomerMaskTab = CustomerMaskConfig['tabs'][number]
type CustomerMaskField = CustomerMaskTab['sections'][number]['fields'][number]

const COMPONENT_TO_FIELD_TYPE: Record<string, Field['type']> = {
  TextField: 'text',
  TextArea: 'textarea',
  Select: 'select',
  DatePicker: 'date',
  Checkbox: 'boolean',
  Switch: 'boolean',
}

export const ENABLE_CUSTOMER_MASK_BUILDER_FORM =
  import.meta.env.VITE_ENABLE_MASK_BUILDER_CUSTOMER_FORM === 'true'

export const CUSTOMER_MASK_OBJECT_PAGE_CONFIG: MaskConfig = convertCustomerMaskToObjectPageConfig(
  customerMaskConfig,
)

export function validateCustomerPayload(payload: CustomerCreate): string | null {
  const customerNumber = getFirstStringValue(payload, ['customer.customer_number', 'customer_number'])
  const name = getFirstStringValue(payload, ['customer.name1', 'name'])

  if (!customerNumber || !name) {
    return 'Bitte alle Pflichtfelder ausfuellen.'
  }

  const email = getFirstStringValue(payload, ['contact.email', 'email'])
  if (email && !isValidEmail(email)) {
    return 'Ungueltiges E-Mail-Format.'
  }

  const phone = getFirstStringValue(payload, ['contact.phone1', 'phone'])
  if (phone && phone.trim().length < 5) {
    return 'Telefonnummer sieht ungewoehnlich kurz aus.'
  }

  return null
}

function convertCustomerMaskToObjectPageConfig(config: CustomerMaskConfig): MaskConfig {
  const tabs = (config.tabs ?? []).filter(
    (tab) => ENABLE_PROSPECTING_UI || tab.id !== 'potential',
  )
  return {
    title: 'Neuen Kunden anlegen',
    subtitle: 'CRM Mask Builder (Beta)',
    type: 'object-page',
    tabs: tabs.map((tab) => ({
      key: tab.id,
      label: tab.label,
      columns: resolveTabColumns(tab),
      fields:
        tab.sections?.flatMap((section) =>
          section.fields.map((field) => convertCustomerMaskField(field, section.label)),
        ) ?? [],
    })),
    actions: [],
    api: {
      baseUrl: '',
      endpoints: {},
    },
  }
}

function convertCustomerMaskField(field: CustomerMaskField, sectionLabel: string): Field {
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

function resolveTabColumns(tab: CustomerMaskTab): number {
  const sectionColumns = tab.sections?.map((section) => section.layout?.columns ?? 2) ?? []
  return sectionColumns.length ? Math.max(...sectionColumns) : 2
}

function getFirstStringValue(source: unknown, paths: string[]): string | undefined {
  for (const path of paths) {
    const value = getNested<string>(source, path)
    if (typeof value === 'string') {
      const trimmed = value.trim()
      if (trimmed) {
        return trimmed
      }
    }
  }
  return undefined
}

function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
}
