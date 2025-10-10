import * as React from "react"
import { useState } from "react"
import { Card } from "@/components/ui/card"
import { useToast } from "@/components/ui/toast-provider"
import { FormBuilder, type FormSchema } from "@/features/forms/FormBuilder"
import { BelegFlowPanel } from "@/features/flows/BelegFlowPanel"
import ApprovalPanel from "@/features/workflow/ApprovalPanel"
import invoiceSchema from "@/domain-schemas/sales_invoice.schema.json"

const ISO_DATE_LENGTH = 10
const DAYS_IN_MS = 24 * 60 * 60 * 1000
const NET_30_DAYS = 30

type SalesInvoice = {
  number: string
  date: string
  customerId: string
  sourceOrder?: string
  sourceDelivery?: string
  paymentTerms: string
  dueDate: string
  notes?: string
  lines: Array<{
    article: string
    qty: number
    price: number
    vatRate: number
  }>
}

/**
 * Sales Invoice Editor Page
 * Rechnung erstellen/bearbeiten
 */
export default function SalesInvoiceEditorPage(): JSX.Element {
  const { push } = useToast()
  const [invoice, setInvoice] = useState<SalesInvoice>({
    number: "INV-2025-0001",
    date: new Date().toISOString().slice(0, ISO_DATE_LENGTH),
    customerId: "",
    paymentTerms: "net30",
    dueDate: new Date(Date.now() + NET_30_DAYS * DAYS_IN_MS)
      .toISOString()
      .slice(0, ISO_DATE_LENGTH),
    notes: "",
    lines: [{ article: "", qty: 1, price: 0, vatRate: 19 }],
  })

  async function save(v: SalesInvoice): Promise<void> {
    try {
      const response = await fetch("/api/mcp/documents/sales_invoice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(v),
      })

      if (!response.ok) {
        throw new Error("Save failed")
      }

      push("✔ Rechnung gespeichert")
    } catch {
      push("❌ Fehler beim Speichern")
    }
  }

  // Rechnung ist End-Beleg, keine Folgebelege
  const nextTypes: Array<{ to: string; label: string }> = []

  return (
    <div className="space-y-4">
      <BelegFlowPanel
        current={{
          id: "1",
          type: "Rechnung",
          number: invoice.number,
          status: "Entwurf",
        }}
        nextTypes={nextTypes}
        onCreateFollowUp={(): void => {
          // Keine Folgebelege
        }}
      />

      <ApprovalPanel domain="sales" doc={invoice} />

      <Card className="p-4">
        <FormBuilder
          schema={invoiceSchema as unknown as FormSchema}
          data={invoice}
          onChange={(p): void => {
            setInvoice((o) => ({ ...o, ...p }))
          }}
          onSubmit={save}
          submitLabel="Rechnung speichern"
        />
      </Card>
    </div>
  )
}

