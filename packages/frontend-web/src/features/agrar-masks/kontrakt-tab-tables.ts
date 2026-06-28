import type { ScreenTableDefinition } from '@/components/mask-builder/schema'

export const KONTRAKT_PILOT_TAB_TABLES: Record<string, ScreenTableDefinition[]> = {
  positionen: [
    {
      key: 'contract_lines',
      label: 'Kontraktpositionen',
      virtualized: true,
      rowHeight: 52,
      columns: [
        { key: 'position_no', label: 'Pos.', numeric: true },
        { key: 'article_id', label: 'Artikel' },
        { key: 'description1', label: 'Bezeichnung' },
        { key: 'qty_contract', label: 'Kontraktmenge', numeric: true },
        { key: 'qty_remaining', label: 'Restmenge', numeric: true },
        { key: 'unit_price', label: 'Preis', numeric: true },
      ],
    },
  ],
  umsaetze: [
    {
      key: 'contract_movements',
      label: 'Umsaetze',
      virtualized: true,
      rowHeight: 52,
      columns: [
        { key: 'movement_date', label: 'Datum' },
        { key: 'order_no', label: 'Auftrag' },
        { key: 'delivery_note_no', label: 'Lieferschein' },
        { key: 'invoice_no', label: 'Rechnung' },
        { key: 'quantity', label: 'Menge', numeric: true },
        { key: 'unit_price', label: 'Preis', numeric: true },
        { key: 'is_invoiced', label: 'Fakturiert' },
      ],
    },
  ],
}

export const KONTRAKT_PILOT_LAZY_DATA_TABS = new Set(['positionen', 'umsaetze'])
