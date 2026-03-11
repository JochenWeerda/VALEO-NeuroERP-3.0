import { useState } from "react"
import { type PutawayInput } from "./schema"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { parseDE } from "@/lib/number-de"

export function PutawayForm({ sku, fromLocation, onSubmit, submitting }: {
  sku: string
  fromLocation?: string
  onSubmit: (_value: PutawayInput) => void
  submitting?: boolean
}): JSX.Element {
  const [qtyInput, setQtyInput] = useState("0")
  const [from, setFrom] = useState(fromLocation ?? "")
  const [to, setTo] = useState("")
  const [errors, setErrors] = useState<{ qty?: string; fromLocation?: string; toLocation?: string }>({})

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>): void => {
    event.preventDefault()
    const qty = parseDE(qtyInput)
    const nextErrors: { qty?: string; fromLocation?: string; toLocation?: string } = {}

    if (!Number.isFinite(qty) || qty <= 0) {
      nextErrors.qty = "Menge muss groesser als 0 sein"
    }
    if (from.trim().length === 0) {
      nextErrors.fromLocation = "Von ist erforderlich"
    }
    if (to.trim().length === 0) {
      nextErrors.toLocation = "Nach ist erforderlich"
    }

    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) {
      return
    }

    onSubmit({ sku, qty, fromLocation: from.trim(), toLocation: to.trim() })
  }

  return (
    <form className="space-y-3" onSubmit={handleSubmit}>
      <div>
        <Label>SKU</Label>
        <Input value={sku} readOnly />
      </div>
      <div>
        <Label>Menge</Label>
        <Input
          placeholder="z. B. 12,5"
          value={qtyInput}
          onChange={(event) => setQtyInput(event.target.value)}
        />
        {errors.qty ? <p className="text-sm text-red-600">{errors.qty}</p> : null}
      </div>
      <div>
        <Label>Von</Label>
        <Input placeholder="z. B. RAMPE-1" value={from} onChange={(event) => setFrom(event.target.value)} />
        {errors.fromLocation ? <p className="text-sm text-red-600">{errors.fromLocation}</p> : null}
      </div>
      <div>
        <Label>Nach</Label>
        <Input placeholder="z. B. REGAL-A-03" value={to} onChange={(event) => setTo(event.target.value)} />
        {errors.toLocation ? <p className="text-sm text-red-600">{errors.toLocation}</p> : null}
      </div>
      <div className="flex justify-end">
        <Button type="submit" disabled={submitting}>Einlagern</Button>
      </div>
    </form>
  )
}
