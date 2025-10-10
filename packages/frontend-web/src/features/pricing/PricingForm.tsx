import * as React from "react"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { parseDE } from "@/lib/number-de"
import { type PriceItem, PriceItemSchema, type PriceTier } from "./schema"
import { TierRow } from "./TierRow"

interface PricingFormProps {
  defaultValues: PriceItem
  submitting?: boolean
  onSubmit: (v: PriceItem) => void
}

const INITIAL_TIER_MIN_QTY = 0
const INITIAL_TIER_NET = 0

type PriceFormValues = z.input<typeof PriceItemSchema>

export function PricingForm({
  defaultValues,
  submitting,
  onSubmit,
}: PricingFormProps): JSX.Element {
  const { register, handleSubmit, setValue, formState: { errors } } = useForm<PriceFormValues>({
    resolver: zodResolver(PriceItemSchema),
    defaultValues,
  })

  const [tiers, setTiers] = React.useState<PriceTier[]>(defaultValues.tiers ?? [])

  const apply = (data: PriceFormValues): void => {
    const parsed = PriceItemSchema.parse({ ...data, tiers })
    onSubmit(parsed)
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

  const handleBaseNetBlur = (e: React.FocusEvent<HTMLInputElement>): void => {
    setValue("baseNet", parseDE(e.target.value), { shouldValidate: true })
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit(apply)}>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <Label>SKU</Label>
          <Input {...register("sku")} readOnly />
          {errors.sku !== undefined ? (
            <p className="text-sm text-red-600">{errors.sku.message}</p>
          ) : null}
        </div>
        <div>
          <Label>Artikel</Label>
          <Input {...register("name")} />
          {errors.name !== undefined ? (
            <p className="text-sm text-red-600">{errors.name.message}</p>
          ) : null}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <Label>Währung</Label>
          <Input {...register("currency")} />
          {errors.currency !== undefined ? (
            <p className="text-sm text-red-600">{errors.currency.message}</p>
          ) : null}
        </div>
        <div>
          <Label>Einheit</Label>
          <Input {...register("unit")} />
          {errors.unit !== undefined ? (
            <p className="text-sm text-red-600">{errors.unit.message}</p>
          ) : null}
        </div>
        <div>
          <Label>Basis-Netto</Label>
          <Input
            defaultValue={String(defaultValues.baseNet)}
            {...register("baseNet", {
              setValueAs: (v): number => parseDE(String(v)),
            })}
            onBlur={handleBaseNetBlur}
          />
          {errors.baseNet !== undefined ? (
            <p className="text-sm text-red-600">{errors.baseNet.message}</p>
          ) : null}
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
          {tiers.length === 0 ? (
            <p className="opacity-70 text-sm">Keine Tiers definiert.</p>
          ) : null}
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


