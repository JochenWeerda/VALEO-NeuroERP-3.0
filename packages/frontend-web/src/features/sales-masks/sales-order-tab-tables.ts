import type { ScreenTableDefinition } from '@/components/mask-builder/schema'

export const SALES_ORDER_PILOT_TAB_TABLES: Record<string, ScreenTableDefinition[]> = {
  positionen: [
    {
      key: 'order_items',
      label: 'Auftragspositionen',
      virtualized: true,
      rowHeight: 52,
      columns: [
        { key: 'line_number', label: 'Pos.', numeric: true },
        { key: 'article_number', label: 'Artikel' },
        { key: 'description', label: 'Bezeichnung' },
        { key: 'quantity', label: 'Menge', numeric: true },
        { key: 'unit_price', label: 'Einzelpreis', numeric: true },
        { key: 'line_total', label: 'Summe', numeric: true },
      ],
    },
  ],
  lieferung: [
    {
      key: 'delivery_notes',
      label: 'Lieferscheine',
      virtualized: true,
      rowHeight: 52,
      columns: [
        { key: 'delivery_note_number', label: 'Lieferschein' },
        { key: 'delivery_date', label: 'Datum' },
        { key: 'status', label: 'Status' },
        { key: 'invoice_number', label: 'Rechnung' },
        { key: 'is_delivered', label: 'Geliefert' },
      ],
    },
  ],
  dokumente: [
    {
      key: 'order_documents',
      label: 'Belege',
      virtualized: true,
      rowHeight: 52,
      columns: [
        { key: 'beleg_nr', label: 'Beleg' },
        { key: 'beleg_datum', label: 'Datum' },
        { key: 'status', label: 'Status' },
        { key: 'invoice_number', label: 'Rechnungsnr.' },
      ],
    },
  ],
}

export const SALES_ORDER_PILOT_LAZY_DATA_TABS = new Set(['positionen', 'lieferung', 'dokumente'])
