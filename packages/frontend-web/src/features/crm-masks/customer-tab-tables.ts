import type { ScreenTableDefinition } from '@/components/mask-builder/schema'

/** Read-only Tabellen fuer den Universal Customer Mask Pilot (Wave 27). */
export const CUSTOMER_PILOT_TAB_TABLES: Record<string, ScreenTableDefinition[]> = {
  contacts: [
    {
      key: 'contacts_list',
      label: 'Ansprechpartner',
      virtualized: true,
      rowHeight: 52,
      columns: [
        { key: 'name', label: 'Name' },
        { key: 'firstName', label: 'Vorname' },
        { key: 'position', label: 'Position' },
        { key: 'email', label: 'E-Mail' },
        { key: 'phone1', label: 'Telefon' },
      ],
    },
  ],
  finance: [
    {
      key: 'open_items',
      label: 'Offene Posten',
      virtualized: true,
      rowHeight: 52,
      columns: [
        { key: 'rechnungsnr', label: 'Rechnung' },
        { key: 'faelligkeit', label: 'Faelligkeit' },
        { key: 'amount', label: 'Betrag', numeric: true },
        { key: 'days_overdue', label: 'Tage ueberfaellig', numeric: true },
        { key: 'op_status', label: 'Status' },
      ],
    },
  ],
  auftraege: [
    {
      key: 'recent_orders',
      label: 'Auftraege',
      virtualized: true,
      rowHeight: 52,
      columns: [
        { key: 'order_number', label: 'Auftrag' },
        { key: 'status', label: 'Status' },
        { key: 'total_amount', label: 'Betrag', numeric: true },
        { key: 'created_at', label: 'Erstellt' },
      ],
    },
  ],
  aktivitaeten: [
    {
      key: 'recent_activities',
      label: 'Aktivitaeten',
      virtualized: true,
      rowHeight: 52,
      columns: [
        { key: 'activity_type', label: 'Typ' },
        { key: 'subject', label: 'Betreff' },
        { key: 'assigned_to', label: 'Zustaendig' },
        { key: 'created_at', label: 'Datum' },
      ],
    },
  ],
  dokumente: [
    {
      key: 'open_documents',
      label: 'Belege / Offene Posten',
      virtualized: true,
      rowHeight: 52,
      columns: [
        { key: 'rechnungsnr', label: 'Beleg' },
        { key: 'faelligkeit', label: 'Datum' },
        { key: 'amount', label: 'Betrag', numeric: true },
        { key: 'op_status', label: 'Status' },
      ],
    },
  ],
}

/** Tabs mit Lazy-Listendaten (Mask-Keys und Summary-Aliase). */
export const CUSTOMER_PILOT_LAZY_DATA_TABS = new Set([
  'contacts',
  'kontakte',
  'finance',
  'auftraege',
  'aktivitaeten',
  'dokumente',
])
