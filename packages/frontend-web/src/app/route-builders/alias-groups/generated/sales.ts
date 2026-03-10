import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/sales/angebot-erstellen",
    "path": "angebot/:id"
  },
  {
    "module": "@/pages/sales/angebot-erstellen",
    "path": "angebot/neu"
  },
  {
    "module": "@/pages/sales/angebot-erstellen",
    "path": "angebote"
  },
  {
    "module": "@/pages/verkauf/lieferschein-erfassung",
    "path": "deliveries/new"
  },
  {
    "module": "@/pages/verkauf/lieferschein-erfassung",
    "path": "delivery"
  },
  {
    "module": "@/pages/sales/invoice-editor",
    "path": "invoice"
  },
  {
    "module": "@/pages/sales/invoice-editor",
    "path": "invoices/new"
  },
  {
    "module": "@/pages/sales/order-editor",
    "path": "order"
  },
  {
    "module": "@/pages/sales/order-editor",
    "path": "orders/new"
  },
  {
    "module": "@/pages/sales/auftraege-liste",
    "path": "auftraege"
  },
  {
    "module": "@/pages/sales/credit-note-editor",
    "path": "credit-note-editor"
  },
  {
    "module": "@/pages/sales/lieferungen-liste",
    "path": "lieferungen"
  },
  {
    "module": "@/pages/sales/orders-modern",
    "path": "orders-modern"
  },
  {
    "module": "@/pages/sales/rechnungen-liste",
    "path": "rechnungen"
  }
]
