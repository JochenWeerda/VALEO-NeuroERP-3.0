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
  totalNutrientNKg?: number
  totalNutrientP2o5Kg?: number
  totalCo2eKg?: number
  supplierName?: string
  sachkundeStatus?: 'geprueft' | 'nicht_erforderlich' | 'offen'
  sdsMitgeliefert?: 'ja' | 'nicht_erforderlich' | 'offen'
  adrPunkte?: number
  lines: Array<{
    article: string
    qty: number
    nutrientNKgPerUnit?: number
    nutrientP2o5KgPerUnit?: number
    co2eKgPerUnit?: number
    bvlZulassungsnummer?: string
    sdsReference?: string
    hazardHinweise?: string
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
    supplierName: "",
    sachkundeStatus: "offen",
    sdsMitgeliefert: "offen",
    adrPunkte: 0,
    lines: [{
      article: "",
      qty: 1,
      nutrientNKgPerUnit: 0,
      nutrientP2o5KgPerUnit: 0,
      co2eKgPerUnit: 0,
      bvlZulassungsnummer: "",
      sdsReference: "",
      hazardHinweise: "",
    }],
  })
  const psmLines = delivery.lines.filter((line) =>
    Boolean(line.bvlZulassungsnummer || line.sdsReference || line.hazardHinweise)
  )
  const missingPsmFields = psmLines.flatMap((line) => {
    const issues: string[] = []
    if (!line.bvlZulassungsnummer) issues.push(`${line.article || 'Position'}: BVL-Zulassungsnr fehlt`)
    if (!line.sdsReference && !line.hazardHinweise) issues.push(`${line.article || 'Position'}: SDB/Gefahrhinweis fehlt`)
    return issues
  })
  const psmCompliant =
    psmLines.length === 0 ||
    (
      missingPsmFields.length === 0 &&
      Boolean(delivery.supplierName) &&
      ['geprueft', 'nicht_erforderlich'].includes(delivery.sachkundeStatus || 'offen') &&
      ['ja', 'nicht_erforderlich'].includes(delivery.sdsMitgeliefert || 'offen') &&
      Number(delivery.adrPunkte || 0) <= 1000
    )
  const sustainabilityTotals = delivery.lines.reduce(
    (acc, line) => {
      const qty = Number(line.qty ?? 0)
      const n = Number(line.nutrientNKgPerUnit ?? 0)
      const p2o5 = Number(line.nutrientP2o5KgPerUnit ?? 0)
      const co2e = Number(line.co2eKgPerUnit ?? 0)
      acc.totalNutrientNKg += qty * n
      acc.totalNutrientP2o5Kg += qty * p2o5
      acc.totalCo2eKg += qty * co2e
      return acc
    },
    { totalNutrientNKg: 0, totalNutrientP2o5Kg: 0, totalCo2eKg: 0 }
  )

  async function save(v: SalesDelivery): Promise<void> {
    try {
      const payload: SalesDelivery = {
        ...v,
        totalNutrientNKg: Number(sustainabilityTotals.totalNutrientNKg.toFixed(3)),
        totalNutrientP2o5Kg: Number(sustainabilityTotals.totalNutrientP2o5Kg.toFixed(3)),
        totalCo2eKg: Number(sustainabilityTotals.totalCo2eKg.toFixed(3)),
      }
      const response = await fetch("/api/mcp/documents/sales_delivery", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
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

      <Card className="p-4">
        <h3 className="mb-2 text-sm font-semibold">Bilanzrelevante Summen aus Lieferschein-Positionen</h3>
        <div className="grid gap-2 sm:grid-cols-3 text-sm">
          <div className="rounded border p-2">
            <div className="text-muted-foreground">Gesamt N</div>
            <div className="font-semibold">{sustainabilityTotals.totalNutrientNKg.toFixed(3)} kg</div>
          </div>
          <div className="rounded border p-2">
            <div className="text-muted-foreground">Gesamt P2O5</div>
            <div className="font-semibold">{sustainabilityTotals.totalNutrientP2o5Kg.toFixed(3)} kg</div>
          </div>
          <div className="rounded border p-2">
            <div className="text-muted-foreground">Gesamt CO2e</div>
            <div className="font-semibold">{sustainabilityTotals.totalCo2eKg.toFixed(3)} kg</div>
          </div>
        </div>
      </Card>

      <Card className="p-4">
        <h3 className="mb-2 text-sm font-semibold">PSM-Compliance Check (Lieferschein)</h3>
        <div className="grid gap-2 sm:grid-cols-4 text-sm">
          <div className="rounded border p-2">
            <div className="text-muted-foreground">PSM-Positionen</div>
            <div className="font-semibold">{psmLines.length}</div>
          </div>
          <div className="rounded border p-2">
            <div className="text-muted-foreground">ADR Punkte</div>
            <div className="font-semibold">{Number(delivery.adrPunkte || 0).toFixed(1)}</div>
          </div>
          <div className="rounded border p-2">
            <div className="text-muted-foreground">Sachkunde</div>
            <div className="font-semibold">{delivery.sachkundeStatus || 'offen'}</div>
          </div>
          <div className="rounded border p-2">
            <div className="text-muted-foreground">Status</div>
            <div className={`font-semibold ${psmCompliant ? 'text-emerald-600' : 'text-red-600'}`}>
              {psmCompliant ? 'konform' : 'unvollstaendig'}
            </div>
          </div>
        </div>
        {missingPsmFields.length > 0 && (
          <ul className="mt-3 list-disc pl-5 text-sm text-red-600">
            {missingPsmFields.map((issue) => (
              <li key={issue}>{issue}</li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}

