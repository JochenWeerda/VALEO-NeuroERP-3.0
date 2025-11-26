export type LeadFieldPriority = 'core' | 'optional'

export interface LeadFieldDef {
  key: string
  label: string
  tab: string
  section: string
  priority: LeadFieldPriority
}

export const LEAD_FIELDS: LeadFieldDef[] = [
  {
    key: 'lead.company',
    label: 'Firma',
    tab: 'masterdata',
    section: 'lead_basic',
    priority: 'core',
  },
  {
    key: 'lead.contact_person',
    label: 'Ansprechpartner',
    tab: 'masterdata',
    section: 'lead_basic',
    priority: 'core',
  },
  {
    key: 'lead.email',
    label: 'E-Mail',
    tab: 'masterdata',
    section: 'lead_basic',
    priority: 'core',
  },
  {
    key: 'lead.phone',
    label: 'Telefon',
    tab: 'masterdata',
    section: 'lead_basic',
    priority: 'optional',
  },
  {
    key: 'lead.source',
    label: 'Quelle',
    tab: 'masterdata',
    section: 'lead_basic',
    priority: 'core',
  },
  {
    key: 'lead.potential',
    label: 'Potenzial',
    tab: 'status',
    section: 'lead_status',
    priority: 'optional',
  },
  {
    key: 'lead.priority',
    label: 'Priorität',
    tab: 'status',
    section: 'lead_status',
    priority: 'optional',
  },
  {
    key: 'lead.status',
    label: 'Status',
    tab: 'status',
    section: 'lead_status',
    priority: 'core',
  },
  {
    key: 'lead.assigned_to',
    label: 'Zugeordnet an',
    tab: 'status',
    section: 'lead_status',
    priority: 'core',
  },
  {
    key: 'lead.expected_close_date',
    label: 'Erwartetes Abschlussdatum',
    tab: 'status',
    section: 'lead_status',
    priority: 'optional',
  },
  {
    key: 'lead.notes',
    label: 'Notizen',
    tab: 'status',
    section: 'lead_notes',
    priority: 'optional',
  },
]
