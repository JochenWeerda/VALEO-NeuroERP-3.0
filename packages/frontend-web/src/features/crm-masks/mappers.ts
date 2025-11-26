import maskBuilderCustomer from '@/config/mask-builder-customer.json'
import { CUSTOMER_FIELDS } from '@/config/l3-customer-field-registry'
import type { Customer, CustomerCreate } from '@/lib/api/crm'
import type { Lead } from '@/lib/services/crm-service'

export type MaskCustomerData = Record<string, unknown>

type MaskBuilderConfig = typeof maskBuilderCustomer

const CORE_ONLY_FIELDS = CUSTOMER_FIELDS.filter((field) => field.priority === 'core')

const MASK_BINDINGS = collectMaskBindings(maskBuilderCustomer)
const REGISTRY_KEYS = CUSTOMER_FIELDS.map((field) => field.key)

const MASK_MISSING_FIELDS = REGISTRY_KEYS.filter((key) => !MASK_BINDINGS.includes(key))
const MASK_EXTRA_FIELDS = MASK_BINDINGS.filter((binding) => !REGISTRY_KEYS.includes(binding))

if (
  (MASK_MISSING_FIELDS.length > 0 || MASK_EXTRA_FIELDS.length > 0) &&
  import.meta.env.MODE !== 'production'
) {
  // eslint-disable-next-line no-console
  console.warn('[crm-masks] registry/mask mismatch detected', {
    missing: MASK_MISSING_FIELDS,
    extra: MASK_EXTRA_FIELDS,
  })
}

export const CUSTOMER_MASK_FIELD_DIFF = {
  missing: MASK_MISSING_FIELDS,
  extra: MASK_EXTRA_FIELDS,
} as const

export function mapCustomerToMask(customer?: Customer | null): MaskCustomerData {
  const result: MaskCustomerData = {}

  for (const field of CORE_ONLY_FIELDS) {
    const value = getNested(customer, field.key)
    if (value !== undefined) {
      setNested(result, field.key, value)
    }
  }

  return result
}

export function mapMaskToCustomer(data: MaskCustomerData): CustomerCreate {
  const result: Record<string, unknown> = {}

  for (const field of CORE_ONLY_FIELDS) {
    const value = getNested(data, field.key)
    if (value !== undefined) {
      setNested(result, field.key, value)
    }
  }

  const name1 = data['customer.name1'] as string | undefined
  let searchKey = data['customer.search_key'] as string | undefined

  if (!searchKey || !searchKey.trim()) {
    searchKey = name1?.trim() ?? ''
  }

  setNested(result, 'customer.search_key', searchKey)

  return result as CustomerCreate
}

export type MaskLeadData = Record<string, unknown>

export function mapLeadToMask(lead?: Lead | null): MaskLeadData {
  if (!lead) {
    return {}
  }

  return {
    'lead.company': lead.company,
    'lead.contact_person': lead.contactPerson,
    'lead.email': lead.email ?? '',
    'lead.phone': lead.phone ?? '',
    'lead.source': lead.source,
    'lead.potential': lead.potential,
    'lead.priority': lead.priority,
    'lead.status': lead.status,
    'lead.assigned_to': lead.assignedTo ?? '',
    'lead.expected_close_date': lead.expectedCloseDate ?? '',
    'lead.notes': lead.notes ?? '',
  }
}

export function mapMaskToLead(data: MaskLeadData): Partial<Lead> {
  const potentialRaw = data['lead.potential']
  const potential =
    typeof potentialRaw === 'number'
      ? potentialRaw
      : potentialRaw
        ? Number(potentialRaw)
        : undefined

  return {
    company: (data['lead.company'] as string) ?? '',
    contactPerson: (data['lead.contact_person'] as string) ?? '',
    email: (data['lead.email'] as string) ?? undefined,
    phone: (data['lead.phone'] as string) ?? undefined,
    source: (data['lead.source'] as string) ?? '',
    potential,
    priority: (data['lead.priority'] as Lead['priority']) ?? 'medium',
    status: (data['lead.status'] as Lead['status']) ?? 'new',
    assignedTo: (data['lead.assigned_to'] as string) ?? undefined,
    expectedCloseDate: (data['lead.expected_close_date'] as string) ?? undefined,
    notes: (data['lead.notes'] as string) ?? undefined,
  }
}

export function getNested<T = unknown>(source: unknown, path: string): T | undefined {
  if (source === null || source === undefined) {
    return undefined
  }

  const segments = path.split('.')
  let current: unknown = source

  for (const segment of segments) {
    if (current === null || typeof current !== 'object') {
      return undefined
    }

    current = (current as Record<string, unknown>)[segment]
  }

  return current as T
}

export function setNested(target: Record<string, unknown>, path: string, value: unknown): void {
  if (value === undefined) {
    return
  }

  const segments = path.split('.')
  const lastKey = segments.pop()

  if (!lastKey) {
    return
  }

  let current = target
  for (const segment of segments) {
    if (
      current[segment] === undefined ||
      current[segment] === null ||
      typeof current[segment] !== 'object'
    ) {
      current[segment] = {}
    }
    current = current[segment] as Record<string, unknown>
  }

  current[lastKey] = value
}

function collectMaskBindings(config: MaskBuilderConfig): string[] {
  const bindings: string[] = []

  for (const tab of config.tabs ?? []) {
    for (const section of tab.sections ?? []) {
      for (const field of section.fields ?? []) {
        if (typeof field.binding === 'string') {
          bindings.push(field.binding)
        }
      }
    }
  }

  return bindings
}
