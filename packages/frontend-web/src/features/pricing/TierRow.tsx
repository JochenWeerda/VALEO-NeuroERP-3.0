import * as React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { formatDE, parseDE } from "@/lib/number-de"

const MIN_QUANTITY = 0

interface TierRowProps {
  index: number
  value: { minQty: number; net: number }
  onChange: (_idx: number, _v: { minQty: number; net: number }) => void
  onRemove: (_idx: number) => void
}

export function TierRow({ index, value, onChange, onRemove }: TierRowProps): JSX.Element {
  const handleMinQtyBlur = (e: React.FocusEvent<HTMLInputElement>): void => {
    const parsed = parseDE(e.target.value)
    const minQty = Math.max(MIN_QUANTITY, Math.floor(parsed))
    onChange(index, { ...value, minQty })
  }

  const handleNetBlur = (e: React.FocusEvent<HTMLInputElement>): void => {
    const parsed = parseDE(e.target.value)
    const net = Math.max(MIN_QUANTITY, parsed)
    onChange(index, { ...value, net })
  }

  const handleRemove = (): void => {
    onRemove(index)
  }

  return (
    <div className="grid grid-cols-5 gap-2 items-end">
      <div className="col-span-2">
        <Label>Mindestmenge</Label>
        <Input
          defaultValue={String(value.minQty)}
          onBlur={handleMinQtyBlur}
        />
      </div>
      <div className="col-span-2">
        <Label>Netto (€)</Label>
        <Input
          defaultValue={formatDE(value.net)}
          onBlur={handleNetBlur}
        />
      </div>
      <div className="text-right">
        <Button variant="ghost" type="button" onClick={handleRemove}>
          Entfernen
        </Button>
      </div>
    </div>
  )
}
