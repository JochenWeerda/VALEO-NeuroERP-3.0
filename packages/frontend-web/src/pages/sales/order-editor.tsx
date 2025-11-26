import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Card } from "@/components/ui/card"
import { useToast } from "@/components/ui/toast-provider"
import { FormBuilder, type FormSchema } from "@/features/forms/FormBuilder"
import { BelegFlowPanel } from "@/features/flows/BelegFlowPanel"
import { PolicyWarningBanner } from "@/features/forms/PolicyWarningBanner"
import ApprovalPanel from "@/features/workflow/ApprovalPanel"
import orderSchema from "@/domain-schemas/sales_order.schema.json"
import { getEntityTypeLabel, getSuccessMessage, getErrorMessage, getStatusLabel } from "@/features/crud/utils/i18n-helpers"

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
  const { t } = useTranslation()
  const { push } = useToast()
  const entityType = 'salesOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Verkaufsauftrag')
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
          fromType: "sales_order",
          toType,
          payload: order,
        }),
      })

      if (!response.ok) {
        throw new Error("Follow-up creation failed")
      }

      const data = (await response.json()) as { ok: boolean; number: string }
      const followUpTypeLabel = toType === "delivery" 
        ? getEntityTypeLabel(t, 'delivery', 'Lieferschein')
        : getEntityTypeLabel(t, 'invoice', 'Rechnung')
      
      push(`${getSuccessMessage(t, 'create', toType)}: ${data.number}`)

      // TODO: Navigate to new document
      // navigate(`/sales/${toType}/${data.number}`)
    } catch {
      push(getErrorMessage(t, 'create', 'followUp'))
    }
  }

  return (
    <div className="space-y-4">
      <BelegFlowPanel
        current={{
          id: "1",
          type: entityTypeLabel,
          number: order.number,
          status: t('status.draft'),
        }}
        nextTypes={[
          { to: "delivery", label: getEntityTypeLabel(t, 'delivery', 'Lieferschein') },
          { to: "invoice", label: getEntityTypeLabel(t, 'invoice', 'Rechnung') },
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
          submitLabel={`${t('crud.actions.save')} ${entityTypeLabel}`}
        />
      </Card>
    </div>
  )
}

