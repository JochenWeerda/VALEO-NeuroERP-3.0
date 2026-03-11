import { useState } from "react"
import { type AdjustInput } from "./schema"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { parseDE } from "@/lib/number-de"

export function AdjustForm({ sku, onSubmit, submitting }: {
  sku: string
  onSubmit: (_value: AdjustInput) => void
  submitting?: boolean
}): JSX.Element {
  const [deltaInput, setDeltaInput] = useState("0")
  const [reason, setReason] = useState<AdjustInput["reason"]>("counting")
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>): void => {
    event.preventDefault()
    const delta = parseDE(deltaInput)

    if (!Number.isFinite(delta) || delta === 0) {
      setError("Delta darf nicht 0 sein")
      return
    }

    setError(null)
    onSubmit({ sku, delta, reason })
  }

  return (
    <form className="space-y-3" onSubmit={handleSubmit}>
      <div>
        <Label>SKU</Label>
        <Input value={sku} readOnly />
      </div>
      <div>
        <Label>Delta (±)</Label>
        <Input
          placeholder="z. B. -5,5"
          value={deltaInput}
          onChange={(event) => setDeltaInput(event.target.value)}
        />
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
      </div>
      <div>
        <Label>Grund</Label>
        <select className="h-9 w-full rounded-md border px-3" value={reason} onChange={(event) => setReason(event.target.value as AdjustInput["reason"])}>
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
