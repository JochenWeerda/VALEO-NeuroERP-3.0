import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/toast-provider"
import { FormBuilder, type FormSchema } from "@/features/forms/FormBuilder"
import { BelegFlowPanel } from "@/features/flows/BelegFlowPanel"
import ApprovalPanel from "@/features/workflow/ApprovalPanel"
import invoiceSchema from "@/domain-schemas/sales_invoice.schema.json"
import { getEntityTypeLabel, getSuccessMessage, getErrorMessage } from "@/features/crud/utils/i18n-helpers"
import { apiClient } from "@/lib/api-client"

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
  status: string
  notes?: string
  lines: Array<{
    article: string
    qty: number
    price: number
    vatRate: number
  }>
  subtotalNet: number
  totalTax: number
  totalGross: number
}

/**
 * Sales Invoice Editor Page
 * Rechnung erstellen/bearbeiten
 */
export default function SalesInvoiceEditorPage(): JSX.Element {
  const { t } = useTranslation()
  const { push } = useToast()
  const [searchParams] = useSearchParams()
  const editId = searchParams.get("id")
  const entityType = 'invoice'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Rechnung')
  const [docId, setDocId] = useState<string | null>(editId)
  const [invoice, setInvoice] = useState<SalesInvoice>({
    number: "",
    date: new Date().toISOString().slice(0, ISO_DATE_LENGTH),
    customerId: "",
    paymentTerms: "net30",
    dueDate: new Date(Date.now() + NET_30_DAYS * DAYS_IN_MS)
      .toISOString()
      .slice(0, ISO_DATE_LENGTH),
    status: "ENTWURF",
    notes: "",
    lines: [{ article: "", qty: 1, price: 0, vatRate: 19 }],
    subtotalNet: 0,
    totalTax: 0,
    totalGross: 0,
  })

  useEffect(() => {
    if (!editId) {
      return
    }
    void (async () => {
      try {
        const { data: doc } = await apiClient.get(`/api/v1/docflow/${editId}`) as any
        setDocId(String(doc.id))
        setInvoice((prev) => ({
          ...prev,
          number: doc.doc_number ?? prev.number,
          date: String(doc.document_date ?? prev.date).slice(0, ISO_DATE_LENGTH),
          customerId: doc.customer_id ?? "",
          status: doc.status ?? prev.status,
          lines: Array.isArray(doc.items)
            ? doc.items.map((it: any) => ({
                article: it.article_number ?? "",
                qty: Number(it.quantity ?? 0),
                price: Number(it.unit_price ?? 0),
                vatRate: Number(it.tax_rate ?? 0),
              }))
            : prev.lines,
          subtotalNet: Number(doc.total_net ?? prev.subtotalNet),
          totalTax: Number(doc.total_tax ?? prev.totalTax),
          totalGross: Number(doc.total_gross ?? prev.totalGross),
        }))
      } catch {
        push(t('crud.messages.readError', { defaultValue: 'Rechnung konnte nicht geladen werden' }))
      }
    })()
  }, [editId, push, t])

  async function save(v: SalesInvoice): Promise<void> {
    try {
      const docPayload = {
        doc_type: "sales_invoice",
        doc_number: v.number,
        status: "open",
        customer_id: v.customerId || null,
        document_date: v.date ? new Date(v.date).toISOString() : null,
        posting_date: v.dueDate || null,
        items: v.lines.map((line) => ({
          article_number: line.article || "n/a",
          description: line.article || "",
          quantity: Number(line.qty || 0),
          unit_price: Number(line.price || 0),
          discount_percent: 0,
          tax_rate: Number(line.vatRate || 0),
        })),
      }
      if (docId) {
        await apiClient.put(`/api/v1/docflow/${docId}`, docPayload)
      } else {
        const idempotencyKey = crypto.randomUUID()
        const { data: created } = await apiClient.post("/api/v1/docflow", {
          ...docPayload,
          idempotency_key: idempotencyKey,
        }) as any
        setDocId(String((created as { id?: string }).id ?? ''))
      }

      push(getSuccessMessage(t, 'update', entityType))
    } catch {
      push(getErrorMessage(t, 'update', entityType))
    }
  }

  async function recordPrint(): Promise<void> {
    if (!docId) {
      push('Bitte zuerst speichern')
      return
    }
    try {
      await apiClient.post(`/api/v1/docflow/${docId}/record-print`, { printed_by: null })
      push('Druck protokolliert')
    } catch {
      push('Druck-Protokoll fehlgeschlagen')
    }
  }

  async function recordExport(): Promise<void> {
    if (!docId) {
      push('Bitte zuerst speichern')
      return
    }
    try {
      await apiClient.post(`/api/v1/docflow/${docId}/record-export`, { exported_by: null })
      push('Export protokolliert')
    } catch {
      push('Export-Protokoll fehlgeschlagen')
    }
  }

  // Rechnung ist End-Beleg, keine Folgebelege
  const nextTypes: Array<{ to: string; label: string }> = []

  return (
    <div className="space-y-4">
      <BelegFlowPanel
        current={{
          id: docId ?? "new",
          type: entityTypeLabel,
          number: invoice.number,
          status: t('status.draft'),
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
          submitLabel={`${t('crud.actions.save')} ${entityTypeLabel}`}
        />
        {docId && (
          <div className="mt-4 flex gap-2">
            <Button type="button" variant="outline" size="sm" onClick={() => void recordPrint()}>
              Druck protokollieren
            </Button>
            <Button type="button" variant="outline" size="sm" onClick={() => void recordExport()}>
              Export protokollieren
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}

