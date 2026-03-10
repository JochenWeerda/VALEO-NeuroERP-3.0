import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/finance/index",
    "path": ""
  },
  {
    "module": "@/pages/finance/invoices-list",
    "path": "invoices"
  },
  {
    "module": "@/pages/finance/invoice-form",
    "path": "invoices/new"
  },
  {
    "module": "@/pages/finance/audit-trail",
    "path": "audit-trail"
  },
  {
    "module": "@/pages/finance/periods",
    "path": "periods"
  },
  {
    "module": "@/pages/finance/payment-matching",
    "path": "payments"
  },
  {
    "module": "@/pages/finance/ap-invoices-list",
    "path": "ap/invoices"
  },
  {
    "module": "@/pages/finance/ap-invoice-form",
    "path": "ap/invoices/new"
  },
  {
    "module": "@/pages/finance/ap-invoice-form",
    "path": "ap/invoices/:id"
  },
  {
    "module": "@/pages/finance/op-kreditoren",
    "path": "op-kreditoren"
  },
  {
    "module": "@/pages/finance/debitoren-stamm",
    "path": "debitoren"
  },
  {
    "module": "@/pages/finance/debitoren-stamm",
    "path": "debitoren/:id"
  },
  {
    "module": "@/pages/finance/bankkonten-stamm",
    "path": "bankkonten"
  },
  {
    "module": "@/pages/finance/bankkonten-stamm",
    "path": "bankkonten/:id"
  },
  {
    "module": "@/pages/fibu/buchungsjournal",
    "path": "bookings/new"
  },
  {
    "module": "@/pages/finance/abschluss",
    "path": "abschluss"
  },
  {
    "module": "@/pages/finance/bank-abgleich",
    "path": "bank-abgleich"
  },
  {
    "module": "@/pages/finance/buchungserfassung",
    "path": "buchungserfassung"
  },
  {
    "module": "@/pages/finance/chart-of-accounts",
    "path": "chart-of-accounts"
  },
  {
    "module": "@/pages/finance/debitoren-liste",
    "path": "debitoren-liste"
  },
  {
    "module": "@/pages/finance/dunning-editor",
    "path": "dunning-editor"
  },
  {
    "module": "@/pages/finance/kasse",
    "path": "kasse"
  },
  {
    "module": "@/pages/finance/kontenplan",
    "path": "kontenplan"
  },
  {
    "module": "@/pages/finance/kreditoren-stamm",
    "path": "kreditoren"
  },
  {
    "module": "@/pages/finance/lastschriften-debitoren",
    "path": "lastschriften-debitoren"
  },
  {
    "module": "@/pages/finance/mahnwesen",
    "path": "mahnwesen"
  },
  {
    "module": "@/pages/finance/nebenbuch-abstimmung",
    "path": "nebenbuch-abstimmung"
  },
  {
    "module": "@/pages/finance/op-debitoren",
    "path": "op-debitoren"
  },
  {
    "module": "@/pages/finance/steuerschluessel",
    "path": "steuerschluessel"
  },
  {
    "module": "@/pages/finance/ustva",
    "path": "ustva"
  },
  {
    "module": "@/pages/finance/zahlungslauf-kreditoren",
    "path": "zahlungslauf-kreditoren"
  }
]
