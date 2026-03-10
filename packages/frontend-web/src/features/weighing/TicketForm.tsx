import { useEffect, useMemo, useState } from "react"
import { type Ticket } from "./schema"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { formatDE, parseDE } from "@/lib/number-de"

type TicketErrors = Partial<Record<keyof Ticket, string>>

function validateTicket(value: Ticket): TicketErrors {
  const errors: TicketErrors = {}

  if (!value.id.trim()) errors.id = "Ticket ist erforderlich"
  if (!value.vehicle.trim()) errors.vehicle = "Fahrzeug ist erforderlich"
  if (value.gross < 0) errors.gross = "Brutto darf nicht negativ sein"
  if (value.tare < 0) errors.tare = "Tara darf nicht negativ sein"
  if (!value.material.trim()) errors.material = "Material ist erforderlich"
  if (!value.ts.trim()) errors.ts = "Zeitpunkt ist erforderlich"

  return errors
}

export function TicketForm({ defaultValues, onSubmit, submitting }: {
  defaultValues: Ticket
  onSubmit: (_value: Ticket) => void
  submitting?: boolean
}): JSX.Element {
  const [formData, setFormData] = useState<Ticket>(defaultValues)
  const [errors, setErrors] = useState<TicketErrors>({})

  useEffect(() => {
    setFormData(defaultValues)
    setErrors({})
  }, [defaultValues])

  useEffect(() => {
    const net = Math.max(0, (formData.gross ?? 0) - (formData.tare ?? 0))
    setFormData((current) => (current.net === net ? current : { ...current, net }))
  }, [formData.gross, formData.tare])

  const netDisplay = useMemo(() => formatDE(formData.net ?? 0), [formData.net])

  const updateField = <K extends keyof Ticket>(field: K, value: Ticket[K]) => {
    setFormData((current) => ({ ...current, [field]: value }))
    setErrors((current) => {
      if (!current[field]) return current
      const next = { ...current }
      delete next[field]
      return next
    })
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const nextErrors = validateTicket(formData)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return
    onSubmit(formData)
  }

  return (
    <form className="space-y-3" onSubmit={handleSubmit}>
      <div>
        <Label>Ticket</Label>
        <Input value={formData.id} readOnly />
      </div>
      <div>
        <Label>Fahrzeug</Label>
        <Input value={formData.vehicle} onChange={(event) => updateField("vehicle", event.target.value)} />
        {errors.vehicle ? <p className="text-sm text-red-600">{errors.vehicle}</p> : null}
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div>
          <Label>Brutto</Label>
          <Input
            value={formatDE(formData.gross)}
            onChange={(event) => updateField("gross", parseDE(event.target.value) || 0)}
            onBlur={(event) => updateField("gross", parseDE(event.target.value) || 0)}
          />
          {errors.gross ? <p className="text-sm text-red-600">{errors.gross}</p> : null}
        </div>
        <div>
          <Label>Tara</Label>
          <Input
            value={formatDE(formData.tare)}
            onChange={(event) => updateField("tare", parseDE(event.target.value) || 0)}
            onBlur={(event) => updateField("tare", parseDE(event.target.value) || 0)}
          />
          {errors.tare ? <p className="text-sm text-red-600">{errors.tare}</p> : null}
        </div>
        <div>
          <Label>Netto</Label>
          <Input value={netDisplay} readOnly />
        </div>
      </div>
      <div>
        <Label>Material</Label>
        <Input value={formData.material} onChange={(event) => updateField("material", event.target.value)} />
        {errors.material ? <p className="text-sm text-red-600">{errors.material}</p> : null}
      </div>
      <div>
        <Label>Zeitpunkt (ISO)</Label>
        <Input value={formData.ts} onChange={(event) => updateField("ts", event.target.value)} />
        {errors.ts ? <p className="text-sm text-red-600">{errors.ts}</p> : null}
      </div>
      <div className="flex justify-end gap-2">
        <Button type="submit" disabled={submitting}>Speichern</Button>
      </div>
    </form>
  )
}
