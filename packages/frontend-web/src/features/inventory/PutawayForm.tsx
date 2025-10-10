import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { type PutawayInput, PutawaySchema } from "./schema"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { parseDE } from "@/lib/number-de"

export function PutawayForm({ sku, fromLocation, onSubmit, submitting }: {
  sku: string
  fromLocation?: string
  onSubmit: (value: PutawayInput) => void
  submitting?: boolean
}): JSX.Element {
  const { register, handleSubmit, setValue, formState: { errors } } = useForm<PutawayInput>({
    resolver: zodResolver(PutawaySchema),
    defaultValues: { sku, qty: 0, fromLocation: fromLocation ?? "", toLocation: "" }
  })

  return (
    <form className="space-y-3" onSubmit={handleSubmit(onSubmit)}>
      <div>
        <Label>SKU</Label>
        <Input value={sku} readOnly />
      </div>
      <div>
        <Label>Menge</Label>
        <Input
          placeholder="z. B. 12,5"
          {...register("qty", { setValueAs: (value) => parseDE(String(value)) })}
          onBlur={(event) => setValue("qty", parseDE(event.target.value))}
        />
        {errors.qty ? <p className="text-sm text-red-600">{errors.qty.message}</p> : null}
      </div>
      <div>
        <Label>Von</Label>
        <Input placeholder="z. B. RAMPE-1" {...register("fromLocation")} />
      </div>
      <div>
        <Label>Nach</Label>
        <Input placeholder="z. B. REGAL-A-03" {...register("toLocation")} />
        {errors.toLocation ? <p className="text-sm text-red-600">{errors.toLocation.message}</p> : null}
      </div>
      <div className="flex justify-end">
        <Button type="submit" disabled={submitting}>Einlagern</Button>
      </div>
    </form>
  )
}
