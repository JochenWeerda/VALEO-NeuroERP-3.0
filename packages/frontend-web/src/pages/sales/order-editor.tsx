import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Card } from "@/components/ui/card"
import { useToast } from "@/components/ui/toast-provider"
import { FormBuilder, type FormSchema } from "@/features/forms/FormBuilder"
import { BelegFlowPanel } from "@/features/flows/BelegFlowPanel"
import { PolicyWarningBanner } from "@/features/forms/PolicyWarningBanner"
import ApprovalPanel from "@/features/workflow/ApprovalPanel"
import orderSchema from "@/domain-schemas/sales_order.schema.json"
import { getEntityTypeLabel, getSuccessMessage, getErrorMessage } from "@/features/crud/utils/i18n-helpers"
import { apiClient } from "@/lib/api-client"

type SalesOrder = {
  number: string
  date: string
  customerId: string
  deliveryAddress?: string
  shippingMethod?: string
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
    shippingMethod: "spedition",
    notes: "",
    lines: [{ article: "", qty: 1, price: 0 }],
  })

  async function save(v: SalesOrder): Promise<void> {
    if (!v.customerId?.trim()) {
      push(t("sales.orderEditor.validation.customerRequired", "Bitte einen Kunden auswaehlen."))
      return
    }

    try {
      const totalAmount = v.lines.reduce((sum, line) => sum + Number(line.qty || 0) * Number(line.price || 0), 0)
      const payload = {
        tenant_id: import.meta.env.VITE_TENANT_ID ?? "00000000-0000-0000-0000-000000000001",
        customer_id: v.customerId,
        order_number: v.number,
        subject: `Verkaufsauftrag ${v.number}`,
        description: v.notes || "",
        total_amount: totalAmount,
        currency: "EUR",
        status: "open",
        delivery_date: v.date ? new Date(v.date).toISOString() : null,
        delivery_address: v.deliveryAddress || null,
        shipping_method: v.shippingMethod || null,
        payment_terms: v.paymentTerms || null,
        notes: v.notes || null,
        items: v.lines.map((line) => ({
          article_number: line.article,
          description: line.article,
          quantity: Number(line.qty || 0),
          unit_price: Number(line.price || 0),
          discount_percent: 0,
        })),
      }

      await apiClient.post("/api/v1/sales/orders", payload)

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

