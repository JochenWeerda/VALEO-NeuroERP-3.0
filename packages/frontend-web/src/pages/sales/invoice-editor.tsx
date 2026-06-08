import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate, useSearchParams } from '@/app/routing/react-router-compat'
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/toast-provider"
import { FormBuilder, type FormSchema } from "@/features/forms/FormBuilder"
import { BelegFlowPanel } from "@/features/flows/BelegFlowPanel"
import ApprovalPanel from "@/features/workflow/ApprovalPanel"
import invoiceSchema from "@/domain-schemas/sales_invoice.schema.json"
import { getEntityTypeLabel, getSuccessMessage, getErrorMessage } from "@/features/crud/utils/i18n-helpers"
import { apiClient } from "@/lib/api-client"
import { downloadXRechnung, downloadZugferd } from "@/lib/api/einvoice"
import { CustomerSalesEligibilityBanner } from "@/components/sales/CustomerSalesEligibilityBanner"
import { useCustomerSalesEligibility } from "@/hooks/useCustomerSalesEligibility"
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from "@/components/workflow"

const ISO_DATE_LENGTH = 10
const DAYS_IN_MS = 24 * 60 * 60 * 1000
const NET_30_DAYS = 30

type InvoiceRoleFocus = "all" | "billing" | "sales" | "finance" | "management"

const invoiceRoleProfiles: Array<{ id: InvoiceRoleFocus; label: string; description: string }> = [
  {
    id: "all",
    label: "Alle Rollen",
    description: "Zeigt die Rechnung fuer Faktura, Vertrieb, Finance und Leitung.",
  },
  {
    id: "billing",
    label: "Faktura",
    description: "Fokus auf Kunde, Positionen, Faelligkeit, Speichern, Druck und Export.",
  },
  {
    id: "sales",
    label: "Vertrieb",
    description: "Fokus auf Kundenfreigabe, Auftrags-/Lieferscheinbezug und Belegstatus.",
  },
  {
    id: "finance",
    label: "Finance",
    description: "Fokus auf Betrag, Steuer, Faelligkeit und offenen Posten.",
  },
  {
    id: "management",
    label: "Leitung",
    description: "Fokus auf Rechnungsfaehigkeit, Blocker und naechste Aktion.",
  },
]

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
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const editId = searchParams.get("id")
  const entityType = 'invoice'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Rechnung')
  const [docId, setDocId] = useState<string | null>(editId)
  const [roleFocus, setRoleFocus] = useState<InvoiceRoleFocus>("all")
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
  const { data: salesEligibility } = useCustomerSalesEligibility(invoice.customerId || undefined)

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
      if (salesEligibility && v.customerId && !salesEligibility.allowed_invoice) {
        push(
          salesEligibility.reasons.join(" ") ||
            "Kunde ist für Rechnungen nicht freigegeben (Stammdaten).",
        )
        return
      }
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

  const [einvoicePending, setEinvoicePending] = useState<'xrechnung' | 'zugferd' | null>(null)

  async function exportEInvoice(format: 'xrechnung' | 'zugferd'): Promise<void> {
    const invoiceNumber = invoice.number?.trim()
    if (!invoiceNumber) {
      push('Rechnungsnummer fehlt — bitte zuerst speichern')
      return
    }
    if (einvoicePending) return
    setEinvoicePending(format)
    try {
      if (format === 'xrechnung') {
        await downloadXRechnung(invoiceNumber)
      } else {
        await downloadZugferd(invoiceNumber)
      }
      push(`E-Rechnung (${format.toUpperCase()}) generiert`)
    } catch (error) {
      const detail = error instanceof Error ? error.message : 'Generierung fehlgeschlagen'
      push(`E-Rechnung-Export fehlgeschlagen: ${detail}`)
    } finally {
      setEinvoicePending(null)
    }
  }

  // Rechnung ist End-Beleg, keine Folgebelege
  const nextTypes: Array<{ to: string; label: string }> = []
  const hasCustomer = Boolean(invoice.customerId)
  const hasLines = invoice.lines.some((line) => line.article && Number(line.qty) > 0)
  const hasDueDate = Boolean(invoice.dueDate)
  const hasAmount = Number(invoice.totalGross) > 0 || invoice.lines.some((line) => Number(line.price) > 0)
  const customerBlocksInvoice = Boolean(salesEligibility && invoice.customerId && !salesEligibility.allowed_invoice)
  const isInvoiceReady = hasCustomer && hasLines && hasDueDate && hasAmount && !customerBlocksInvoice
  const nextInvoiceAction = !hasCustomer
    ? "Kunden fuer die Rechnung eintragen."
    : customerBlocksInvoice
      ? "Kundenfreigabe pruefen, bevor die Rechnung gespeichert wird."
      : !hasLines
        ? "Mindestens eine Rechnungsposition erfassen."
        : !hasAmount
          ? "Preis oder Gesamtbetrag pruefen."
          : !hasDueDate
            ? "Faelligkeit setzen."
            : docId
              ? "Druck, Export oder OP-Klaerung fortfuehren."
              : "Rechnung speichern und danach Druck oder Export protokollieren."
  const invoiceTaskItems: UxTaskItem[] = [
    {
      label: "Kunde und Freigabe pruefen",
      done: hasCustomer && !customerBlocksInvoice,
      hint: customerBlocksInvoice ? "Die Kundenfreigabe blockiert diese Rechnung." : hasCustomer ? "Kunde ist eingetragen und nicht blockiert." : "Kunde fehlt noch.",
    },
    {
      label: "Positionen erfassen",
      done: hasLines,
      hint: hasLines ? `${invoice.lines.length} Positionen sind angelegt.` : "Mindestens eine Position mit Artikel und Menge erfassen.",
    },
    {
      label: "Betrag und Faelligkeit klaeren",
      done: hasAmount && hasDueDate,
      hint: hasAmount && hasDueDate ? `Faellig am ${invoice.dueDate}.` : "Betrag, Steuer und Faelligkeit pruefen.",
    },
    {
      label: "Nachweis und OP-Folge sichern",
      done: Boolean(docId),
      hint: docId ? "Rechnung ist gespeichert; Druck, Export und OP-Klaerung sind verfuegbar." : "Nach dem Speichern werden Druck, Export und OP-Folge moeglich.",
    },
  ]
  const invoiceCrudCapabilities = [
    {
      key: "create",
      label: "Anlegen/Speichern",
      available: isInvoiceReady,
      hint: isInvoiceReady ? "Rechnung kann gespeichert werden." : "Kunde, Positionen, Betrag und Faelligkeit muessen belastbar sein.",
    },
    {
      key: "read",
      label: "Lesen",
      available: true,
      hint: "Rechnungsdaten, Belegfluss, Freigabe, Positionen und Summen sind sichtbar.",
    },
    {
      key: "update",
      label: "Bearbeiten",
      available: true,
      hint: "Kopf- und Positionsdaten koennen im Formular bearbeitet werden.",
    },
    {
      key: "approve",
      label: "Druck/Export",
      available: Boolean(docId),
      hint: docId ? "Druck und Export koennen protokolliert werden." : "Druck und Export starten nach dem ersten Speichern.",
    },
    {
      key: "follow-up",
      label: "OP-Folge",
      available: Boolean(docId && invoice.number?.trim()),
      hint: docId && invoice.number?.trim() ? "Offener Posten und Zahlungseingang sind erreichbar." : "OP-Folge braucht gespeicherte Rechnung mit Nummer.",
    },
    {
      key: "audit",
      label: "Nachverfolgung",
      available: Boolean(docId),
      hint: docId ? "Docflow-ID, Druck und Export bilden die Belegspur." : "Die Belegspur entsteht beim Speichern.",
    },
  ]

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

      <div className="space-y-4">
        <RoleFocusBar
          roles={invoiceRoleProfiles}
          value={roleFocus}
          onChange={setRoleFocus}
          visibleCount={roleFocus === "all" ? 4 : 1}
          totalCount={4}
        />
        <ManagementDecisionPanel
          decision={{
            allowed: isInvoiceReady,
            allowedLabel: "Rechnungsfaehig",
            blockedLabel: "Noch nicht rechnungsfaehig",
            summary: isInvoiceReady
              ? `Die Rechnung ist fachlich bereit. ${invoice.lines.length} Positionen, ${invoice.totalGross.toFixed(2)} EUR brutto und Faelligkeit ${invoice.dueDate}.`
              : `Vor der Rechnung ist noch etwas offen: ${nextInvoiceAction}`,
            blockerCount: [!hasCustomer, customerBlocksInvoice, !hasLines, !hasAmount, !hasDueDate].filter(Boolean).length,
            nextFocus: nextInvoiceAction,
            template: {
              label: "Rechnungsliste oeffnen",
              href: "/sales/rechnungen",
            },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan title="Rechnungs-Folgebelegplan" items={invoiceTaskItems} />
          <div className="space-y-3">
            <NextActionPanel
              action={nextInvoiceAction}
              tone={isInvoiceReady ? "emerald" : customerBlocksInvoice ? "red" : hasCustomer ? "amber" : "blue"}
            />
            <EvidenceTemplateLink link={{ label: "Offene Posten pruefen", href: "/finance/op-debitoren" }} />
          </div>
        </div>
        <CrudCapabilityChecklist capabilities={invoiceCrudCapabilities} />
      </div>

      <ApprovalPanel domain="sales" doc={invoice} />

      <Card className="p-4">
        {invoice.customerId ? (
          <CustomerSalesEligibilityBanner
            crmCustomerId={invoice.customerId}
            modus="rechnung"
          />
        ) : null}
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
          <div className="mt-4 flex flex-wrap gap-2">
            <Button type="button" variant="outline" size="sm" onClick={() => void recordPrint()}>
              Druck protokollieren
            </Button>
            <Button type="button" variant="outline" size="sm" onClick={() => void recordExport()}>
              Export protokollieren
            </Button>
            <Button
              type="button"
              variant="default"
              size="sm"
              onClick={() => void exportEInvoice('xrechnung')}
              disabled={einvoicePending !== null || !invoice.number?.trim()}
              data-testid="einvoice-xrechnung"
            >
              {einvoicePending === 'xrechnung' ? 'Erzeuge…' : 'XRechnung (XML)'}
            </Button>
            <Button
              type="button"
              variant="default"
              size="sm"
              onClick={() => void exportEInvoice('zugferd')}
              disabled={einvoicePending !== null || !invoice.number?.trim()}
              data-testid="einvoice-zugferd"
            >
              {einvoicePending === 'zugferd' ? 'Erzeuge…' : 'ZUGFeRD (PDF/A-3)'}
            </Button>
            {invoice.number?.trim() ? (
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() =>
                  navigate(`/finance/op-debitoren?rechnungsnr=${encodeURIComponent(invoice.number.trim())}`)
                }
              >
                OP / Zahlungseingang (OTC-011)
              </Button>
            ) : null}
          </div>
        )}
      </Card>
    </div>
  )
}

