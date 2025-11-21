import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { type AdjustInput, AdjustSchema } from "./schema"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { parseDE } from "@/lib/number-de"

export function AdjustForm({ sku, onSubmit, submitting }: {
  sku: string
  onSubmit: (_value: AdjustInput) => void
  submitting?: boolean
}): JSX.Element {
  const { register, handleSubmit, setValue, formState: { errors } } = useForm<AdjustInput>({
    resolver: zodResolver(AdjustSchema),
    defaultValues: { sku, delta: 0, reason: "counting" }
  })

  return (
    <form className="space-y-3" onSubmit={handleSubmit(onSubmit)}>
      <div>
        <Label>SKU</Label>
        <Input value={sku} readOnly />
      </div>
      <div>
        <Label>Delta (±)</Label>
        <Input
          placeholder="z. B. -5,5"
          {...register("delta", { setValueAs: (value) => parseDE(String(value)) })}
          onBlur={(event) => setValue("delta", parseDE(event.target.value))}
        />
        {errors.delta ? <p className="text-sm text-red-600">{errors.delta.message}</p> : null}
      </div>
      <div>
        <Label>Grund</Label>
        <select className="w-full rounded-md border px-3 h-9" {...register("reason")}>
          <option value="counting">Inventur</option>
          <option value="damage">Beschaedigung</option>
          <option value="shrinkage">Schwund</option>
          <option value="other">Sonstiges</option>
        </select>
      </div>
      <div className="flex justify-end">
        <Button type="submit" disabled={submitting}>Verbuchen</Button>
      </div>
    </form>
  )
}
