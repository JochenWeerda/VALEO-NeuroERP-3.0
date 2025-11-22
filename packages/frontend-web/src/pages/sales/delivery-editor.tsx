import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Card } from "@/components/ui/card"
import { useToast } from "@/components/ui/toast-provider"
import { FormBuilder, type FormSchema } from "@/features/forms/FormBuilder"
import { BelegFlowPanel } from "@/features/flows/BelegFlowPanel"
import ApprovalPanel from "@/features/workflow/ApprovalPanel"
import deliverySchema from "@/domain-schemas/sales_delivery.schema.json"
import { getEntityTypeLabel, getSuccessMessage, getErrorMessage, getStatusLabel } from "@/features/crud/utils/i18n-helpers"

const ISO_DATE_LENGTH = 10

type SalesDelivery = {
  number: string
  date: string
  customerId: string
  sourceOrder?: string
  deliveryAddress: string
  carrier?: string
  deliveryDate?: string
  status: string
  notes?: string
  lines: Array<{
    article: string
    qty: number
  }>
}

/**
 * Sales Delivery Editor Page
 * Lieferschein erstellen/bearbeiten
 */
export default function SalesDeliveryEditorPage(): JSX.Element {
  const { t } = useTranslation()
  const { push } = useToast()
  const entityType = 'delivery'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Lieferschein')
  const [delivery, setDelivery] = useState<SalesDelivery>({
    number: "DL-2025-0001",
    date: new Date().toISOString().slice(0, ISO_DATE_LENGTH),
    customerId: "",
    deliveryAddress: "",
    carrier: "dhl",
    deliveryDate: new Date().toISOString().slice(0, ISO_DATE_LENGTH),
    status: "ENTWURF",
    notes: "",
    lines: [{ article: "", qty: 1 }],
  })

  async function save(v: SalesDelivery): Promise<void> {
    try {
      const response = await fetch("/api/mcp/documents/sales_delivery", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(v),
      })

      if (!response.ok) {
        throw new Error("Save failed")
      }

      push(getSuccessMessage(t, 'update', entityType))
    } catch {
      push(getErrorMessage(t, 'update', entityType))
    }
  }

  async function createFollowUp(toType: string): Promise<void> {
    try {
      const response = await fetch("/api/mcp/documents/follow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fromType: "sales_delivery",
          toType,
          payload: delivery,
        }),
      })

      if (!response.ok) {
        throw new Error("Follow-up creation failed")
      }

      const data = (await response.json()) as { ok: boolean; number: string }
      const invoiceTypeLabel = getEntityTypeLabel(t, 'invoice', 'Rechnung')
      push(`${getSuccessMessage(t, 'create', 'invoice')}: ${data.number}`)
    } catch {
      push(getErrorMessage(t, 'create', 'invoice'))
    }
  }

  return (
    <div className="space-y-4">
      <BelegFlowPanel
        current={{
          id: "1",
          type: entityTypeLabel,
          number: delivery.number,
          status: getStatusLabel(t, delivery.status, delivery.status),
        }}
        nextTypes={[{ to: "invoice", label: getEntityTypeLabel(t, 'invoice', 'Rechnung') }]}
        onCreateFollowUp={createFollowUp}
      />

      <ApprovalPanel domain="sales" doc={delivery} />

      <Card className="p-4">
        <FormBuilder
          schema={deliverySchema as unknown as FormSchema}
          data={delivery}
          onChange={(p): void => {
            setDelivery((o) => ({ ...o, ...p }))
          }}
          onSubmit={save}
          submitLabel={`${t('crud.actions.save')} ${entityTypeLabel}`}
        />
      </Card>
    </div>
  )
}

