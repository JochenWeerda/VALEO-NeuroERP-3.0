import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { type Ticket, TicketSchema } from "./schema"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { formatDE, parseDE } from "@/lib/number-de"

export function TicketForm({ defaultValues, onSubmit, submitting }: {
  defaultValues: Ticket
  onSubmit: (value: Ticket) => void
  submitting?: boolean
}): JSX.Element {
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<Ticket>({
    resolver: zodResolver(TicketSchema),
    defaultValues
  })

  const gross = watch("gross")
  const tare = watch("tare")

  useEffect(() => {
    const net = Math.max(0, (gross ?? 0) - (tare ?? 0))
    setValue("net", net, { shouldDirty: true })
  }, [gross, tare, setValue])

  const netDisplay = formatDE(watch("net") ?? 0)

  return (
    <form className="space-y-3" onSubmit={handleSubmit(onSubmit)}>
      <div>
        <Label>Ticket</Label>
        <Input value={defaultValues.id} readOnly />
      </div>
      <div>
        <Label>Fahrzeug</Label>
        <Input {...register("vehicle")} />
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div>
          <Label>Brutto</Label>
          <Input
            defaultValue={formatDE(defaultValues.gross)}
            {...register("gross", { setValueAs: (value) => parseDE(String(value)) })}
            onBlur={(event) => setValue("gross", parseDE(event.target.value))}
          />
          {errors.gross ? <p className="text-sm text-red-600">{errors.gross.message}</p> : null}
        </div>
        <div>
          <Label>Tara</Label>
          <Input
            defaultValue={formatDE(defaultValues.tare)}
            {...register("tare", { setValueAs: (value) => parseDE(String(value)) })}
            onBlur={(event) => setValue("tare", parseDE(event.target.value))}
          />
          {errors.tare ? <p className="text-sm text-red-600">{errors.tare.message}</p> : null}
        </div>
        <div>
          <Label>Netto</Label>
          <Input value={netDisplay} readOnly />
        </div>
      </div>
      <div>
        <Label>Material</Label>
        <Input {...register("material")} />
      </div>
      <div>
        <Label>Zeitpunkt (ISO)</Label>
        <Input {...register("ts")} />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="submit" disabled={submitting}>Speichern</Button>
      </div>
    </form>
  )
}
