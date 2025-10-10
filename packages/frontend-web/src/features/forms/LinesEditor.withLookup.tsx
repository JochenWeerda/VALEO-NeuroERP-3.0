import React from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { InlineArticleLookup } from "@/features/forms/fields/inline-lookup"

type LineCol = { name: string; label: string; type: "string" | "number"; required?: boolean }

export function LinesEditorWithLookup({
  columns,
  value,
  onChange
}: {
  columns: LineCol[]
  value: any[]
  onChange: (rows: any[]) => void
}) {
  const rows = value || []

  function setCell(i: number, name: string, v: unknown) {
    const next = rows.map((r, idx) => (idx === i ? { ...r, [name]: v } : r))
    onChange(next)
  }

  function addRow() {
    onChange([...(rows ?? []), Object.fromEntries(columns.map((c) => [c.name, c.type === "number" ? 0 : ""]))])
  }

  function delRow(i: number) {
    onChange((rows ?? []).filter((_, idx) => idx !== i))
  }

  return (
    <div className="grid gap-2" style={{ gridTemplateColumns: `40px repeat(${columns.length}, 1fr) 80px` }}>
      <div className="font-medium">#</div>
      {columns.map((c) => (
        <div key={c.name} className="font-medium">{c.label}</div>
      ))}
      <div></div>

      {(rows ?? []).map((r, i) => (
        <React.Fragment key={i}>
          <div className="text-sm text-muted-foreground">{i + 1}</div>
          {columns.map((c) => (
            <div key={c.name}>
              {c.name === 'article' ? (
                <InlineArticleLookup
                  value={String(r[c.name] ?? '')}
                  onPick={(it) => {
                    const price = typeof it.price === 'number' ? it.price : (typeof it.cost === 'number' ? Number((it.cost * 1.2).toFixed(2)) : 0)
                    const next = rows.map((row, idx) =>
                      idx === i ? { ...row, article: it.id, cost: it.cost ?? row.cost, price: row.price ?? price } : row
                    )
                    onChange(next)
                  }}
                />
              ) : c.type === "number" ? (
                <Input
                  type="number"
                  value={Number(r[c.name] ?? 0)}
                  onChange={(e) => setCell(i, c.name, Number(e.target.value))}
                />
              ) : (
                <Input
                  value={String(r[c.name] ?? "")}
                  onChange={(e) => setCell(i, c.name, e.target.value)}
                />
              )}
            </div>
          ))}
          <Button type="button" variant="ghost" size="sm" onClick={() => delRow(i)}>
            Löschen
          </Button>
        </React.Fragment>
      ))}

      <div className="col-span-full mt-2">
        <Button type="button" variant="outline" onClick={addRow}>
          Position hinzufügen
        </Button>
      </div>
    </div>
  )
}