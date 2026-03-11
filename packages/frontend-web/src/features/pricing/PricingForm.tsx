import * as React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { parseDE } from "@/lib/number-de"
import { type PriceItem, type PriceTier } from "./schema"
import { TierRow } from "./TierRow"

interface PricingFormProps {
  defaultValues: PriceItem
  submitting?: boolean
  onSubmit: (_v: PriceItem) => void
}

const INITIAL_TIER_MIN_QTY = 0
const INITIAL_TIER_NET = 0

export function PricingForm({
  defaultValues,
  submitting,
  onSubmit,
}: PricingFormProps): JSX.Element {
  const [values, setValues] = React.useState({
    sku: defaultValues.sku,
    name: defaultValues.name,
    currency: defaultValues.currency,
    unit: defaultValues.unit,
    baseNet: String(defaultValues.baseNet),
  })
  const [tiers, setTiers] = React.useState<PriceTier[]>(defaultValues.tiers ?? [])
  const [errors, setErrors] = React.useState<Partial<Record<'sku' | 'name' | 'currency' | 'unit' | 'baseNet', string>>>({})

  const apply = (event: React.FormEvent<HTMLFormElement>): void => {
    event.preventDefault()

    const nextErrors: Partial<Record<'sku' | 'name' | 'currency' | 'unit' | 'baseNet', string>> = {}
    const baseNet = parseDE(values.baseNet)

    if (values.sku.trim().length === 0) nextErrors.sku = 'SKU ist erforderlich'
    if (values.name.trim().length === 0) nextErrors.name = 'Artikel ist erforderlich'
    if (values.currency.trim().length === 0) nextErrors.currency = 'Waehrung ist erforderlich'
    if (values.unit.trim().length === 0) nextErrors.unit = 'Einheit ist erforderlich'
    if (!Number.isFinite(baseNet) || baseNet < 0) nextErrors.baseNet = 'Basis-Netto muss >= 0 sein'

    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) {
      return
    }

    onSubmit({
      sku: values.sku.trim(),
      name: values.name.trim(),
      currency: values.currency.trim(),
      unit: values.unit.trim(),
      baseNet,
      tiers,
    })
  }

  const addTier = (): void => {
    setTiers((prev) => [...prev, { minQty: INITIAL_TIER_MIN_QTY, net: INITIAL_TIER_NET }])
  }

  const changeTier = (idx: number, v: PriceTier): void => {
    setTiers((prev) => prev.map((t, i) => (i === idx ? v : t)))
  }

  const removeTier = (idx: number): void => {
    setTiers((prev) => prev.filter((_, i) => i !== idx))
  }

  return (
    <form className="space-y-4" onSubmit={apply}>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <Label>SKU</Label>
          <Input value={values.sku} readOnly />
          {errors.sku !== undefined ? <p className="text-sm text-red-600">{errors.sku}</p> : null}
        </div>
        <div>
          <Label>Artikel</Label>
          <Input value={values.name} onChange={(event) => setValues((current) => ({ ...current, name: event.target.value }))} />
          {errors.name !== undefined ? <p className="text-sm text-red-600">{errors.name}</p> : null}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <Label>Währung</Label>
          <Input value={values.currency} onChange={(event) => setValues((current) => ({ ...current, currency: event.target.value }))} />
          {errors.currency !== undefined ? <p className="text-sm text-red-600">{errors.currency}</p> : null}
        </div>
        <div>
          <Label>Einheit</Label>
          <Input value={values.unit} onChange={(event) => setValues((current) => ({ ...current, unit: event.target.value }))} />
          {errors.unit !== undefined ? <p className="text-sm text-red-600">{errors.unit}</p> : null}
        </div>
        <div>
          <Label>Basis-Netto</Label>
          <Input value={values.baseNet} onChange={(event) => setValues((current) => ({ ...current, baseNet: event.target.value }))} />
          {errors.baseNet !== undefined ? <p className="text-sm text-red-600">{errors.baseNet}</p> : null}
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold">Staffelpreise</h4>
          <Button type="button" size="sm" onClick={addTier}>
            Tier hinzufügen
          </Button>
        </div>
        <div className="space-y-2">
          {tiers.length === 0 ? <p className="text-sm opacity-70">Keine Tiers definiert.</p> : null}
          {tiers.map((t, i): JSX.Element => (
            <TierRow
              key={i}
              index={i}
              value={t}
              onChange={changeTier}
              onRemove={removeTier}
            />
          ))}
        </div>
      </div>

      <div className="flex justify-end">
        <Button type="submit" disabled={submitting}>
          Speichern
        </Button>
      </div>
    </form>
  )
}
