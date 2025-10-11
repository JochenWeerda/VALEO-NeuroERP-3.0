import { useState } from "react"
import { Card } from "@/components/ui/card"
import { useToast } from "@/components/ui/toast-provider"
import { FormBuilder, type FormSchema } from "@/features/forms/FormBuilder"
import { BelegFlowPanel } from "@/features/flows/BelegFlowPanel"
import { PolicyWarningBanner } from "@/features/forms/PolicyWarningBanner"
import ApprovalPanel from "@/features/workflow/ApprovalPanel"
import orderSchema from "@/domain-schemas/sales_order.schema.json"

type SalesOrder = {
  number: string
  date: string
  customerId: string
  deliveryAddress?: string
  paymentTerms: string
  notes?: string
  lines: Array<{
    article: string
    qty: number
    price: number
  }>
}

/**
 * Sales Order Editor Page
 * Verkaufsauftrag erstellen/bearbeiten mit Folgebeleg-Funktionen
 */
const ISO_DATE_LENGTH = 10

export default function SalesOrderEditorPage(): JSX.Element {
  const { push } = useToast()
  const [order, setOrder] = useState<SalesOrder>({
    number: "SO-2025-0001",
    date: new Date().toISOString().slice(0, ISO_DATE_LENGTH),
    customerId: "",
    paymentTerms: "net30",
    notes: "",
    lines: [{ article: "", qty: 1, price: 0 }],
  })

  async function save(v: SalesOrder): Promise<void> {
    try {
      const response = await fetch("/api/mcp/documents/sales_order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(v),
      })

      if (!response.ok) {
        throw new Error("Save failed")
      }

      push("✔ Auftrag gespeichert")
    } catch {
      push("❌ Fehler beim Speichern")
    }
  }

  async function createFollowUp(toType: string): Promise<void> {
    try {
      const response = await fetch("/api/mcp/documents/follow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fromType: "sales_order",
          toType,
          payload: order,
        }),
      })

      if (!response.ok) {
        throw new Error("Follow-up creation failed")
      }

      const data = (await response.json()) as { ok: boolean; number: string }

      push(`✔ ${toType === "delivery" ? "Lieferschein" : "Rechnung"} erstellt: ${data.number}`)

      // TODO: Navigate to new document
      // navigate(`/sales/${toType}/${data.number}`)
    } catch {
      push("❌ Fehler beim Erstellen des Folgebelegs")
    }
  }

  return (
    <div className="space-y-4">
      <BelegFlowPanel
        current={{
          id: "1",
          type: "Verkaufsauftrag",
          number: order.number,
          status: "Entwurf",
        }}
        nextTypes={[
          { to: "delivery", label: "Lieferschein" },
          { to: "invoice", label: "Rechnung" },
        ]}
        onCreateFollowUp={createFollowUp}
      />

      <ApprovalPanel domain="sales" doc={order} />

      <PolicyWarningBanner
        formData={order}
        kpiId="sales_order"
        userRoles={["manager"]}
      />

      <Card className="p-4">
        <FormBuilder
          schema={orderSchema as unknown as FormSchema}
          data={order}
          onChange={(p): void => {
            setOrder((o) => ({ ...o, ...p }))
          }}
          onSubmit={save}
          submitLabel="Auftrag speichern"
        />
      </Card>
    </div>
  )
}

