import * as React from "react"
import { useEffect, useMemo, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/components/ui/toast-provider"
import { buildZodFromSchema, validateValues } from "@/features/forms/validator"
import { FieldRenderer } from "@/features/forms/fields"

export type FormSchema = {
  id: string
  title: string
  fields: Array<{
    name: string
    label: string
    type: "string" | "number" | "date" | "text" | "select" | "lookup" | "lines"
    required?: boolean
    options?: Array<{ value: string; label: string }>
    placeholder?: string
    min?: number
    max?: number
    lookup?: string
  }>
  lines?: {
    name: string
    label: string
    columns: Array<{
      name: string
      label: string
      type: "string" | "number" | "lookup"
      required?: boolean
      lookup?: string
    }>
  }
}

type Props<T> = {
  schema: FormSchema
  data: T
  onChange?: (partial: Partial<T>) => void
  onSubmit: (values: T) => Promise<void> | void
  submitLabel?: string
}

export function FormBuilder<T extends Record<string, unknown>>({
  schema,
  data,
  onChange,
  onSubmit,
  submitLabel = "Speichern",
}: Props<T>): JSX.Element {
  const { push } = useToast()
  const [values, setValues] = useState<Record<string, unknown>>(data)
  const zodSchema = useMemo(() => buildZodFromSchema(schema), [schema])
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [policy, setPolicy] = useState<{
    level: "allow" | "warn" | "block"
    message?: string
  }>({ level: "allow" })

  useEffect(() => {
    setValues(data)
  }, [data])

  function setField(name: string, value: unknown): void {
    const next = { ...values, [name]: value }
    setValues(next)
    onChange?.({ [name]: value } as Partial<T>)
    void runPolicy(next)
  }

  async function runPolicy(v: Record<string, unknown>): Promise<void> {
    try {
      // Einfache Heuristik: block bei negativen Mengen, warn bei Preis < cost
      const lines = (v as { lines?: unknown[] }).lines ?? []
      for (const L of lines) {
        const line = L as { qty?: number; price?: number; cost?: number }
        if (typeof line.qty === "number" && line.qty < 0) {
          setPolicy({
            level: "block",
            message: "Negative Menge nicht erlaubt",
          })
          return
        }
        if (
          typeof line.price === "number" &&
          typeof line.cost === "number" &&
          line.price < line.cost
        ) {
          setPolicy({
            level: "warn",
            message: `Preis (${line.price}) liegt unter EK (${line.cost})`,
          })
          return
        }
      }
      setPolicy({ level: "allow" })
    } catch {
      setPolicy({ level: "allow" })
    }
  }

  async function handleSubmit(e: React.FormEvent): Promise<void> {
    e.preventDefault()
    const { ok, errs, parsed } = validateValues(zodSchema, values)
    if (!ok) {
      setErrors(errs)
      push("⚠️ Bitte Eingaben prüfen")
      return
    }
    if (policy.level === "block") {
      push(`❌ Speichern blockiert: ${policy.message ?? "Policy-Verstoß"}`)
      return
    }
    setErrors({})
    await onSubmit(parsed as T)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-xl font-semibold">{schema.title}</h2>

      {policy.level !== "allow" && (
        <Card
          className={`p-3 border ${
            policy.level === "warn"
              ? "bg-amber-50 border-amber-300"
              : "bg-red-50 border-red-300"
          }`}
        >
          <div className="text-sm">
            {policy.message ??
              (policy.level === "warn" ? "Bitte prüfen" : "Aktion blockiert")}
          </div>
        </Card>
      )}

      <Card className="p-4 space-y-3">
        {schema.fields.map(
          (f): JSX.Element => (
            <div key={f.name} className="grid gap-1">
              <Label htmlFor={f.name}>
                {f.label}
                {f.required === true ? " *" : ""}
              </Label>
              <FieldRenderer
                field={f}
                value={values[f.name]}
                onChange={(v): void => {
                  setField(f.name, v)
                }}
              />
              {errors[f.name] !== undefined && (
                <span className="text-sm text-red-600">{errors[f.name]}</span>
              )}
            </div>
          )
        )}
      </Card>

      {schema.lines !== undefined && (
        <Card className="p-4 space-y-2">
          <Label>{schema.lines.label}</Label>
          <LinesEditor
            columns={schema.lines.columns}
            value={(values[schema.lines.name] as unknown[]) ?? []}
            onChange={(rows): void => {
              if (schema.lines !== undefined) {
                setField(schema.lines.name, rows)
              }
            }}
          />
        </Card>
      )}

      <div className="text-right">
        <Button type="submit" disabled={policy.level === "block"}>
          {submitLabel}
        </Button>
      </div>
    </form>
  )
}

type LineCol = {
  name: string
  label: string
  type: "string" | "number" | "lookup"
  required?: boolean
  lookup?: string
}

function LinesEditor({
  columns,
  value,
  onChange,
}: {
  columns: LineCol[]
  value: unknown[]
  onChange: (rows: unknown[]) => void
}): JSX.Element {
  const rows = value as Record<string, unknown>[]

  async function setCell(i: number, name: string, v: unknown): Promise<void> {
    let next = rows.map((r, idx) => (idx === i ? { ...r, [name]: v } : r))

    // Auto-Fill: Wenn Artikel ausgewählt, hole Metadaten
    if (name === "article" && typeof v === "string" && v.length > 0) {
      try {
        const response = await fetch(`/api/mcp/lookup/articles?q=${encodeURIComponent(v)}`)
        const data = (await response.json()) as {
          ok: boolean
          data: Array<{ id: string; cost?: number; price?: number }>
        }
        const article = data.data?.find((a) => a.id === v)
        if (article !== undefined) {
          // Auto-Fill price und cost
          next = rows.map((r, idx) =>
            idx === i
              ? {
                  ...r,
                  [name]: v,
                  price: article.price ?? article.cost ?? r.price ?? 0,
                  cost: article.cost ?? r.cost ?? 0,
                }
              : r
          )
        }
      } catch {
        // Silent fail
      }
    }

    onChange(next)
  }

  function addRow(): void {
    onChange([
      ...(rows ?? []),
      Object.fromEntries(
        columns.map((c) => [c.name, c.type === "number" ? 0 : ""])
      ),
    ])
  }

  function delRow(i: number): void {
    onChange((rows ?? []).filter((_, idx) => idx !== i))
  }

  return (
    <div className="space-y-2">
      <div
        className="grid gap-2"
        style={{
          gridTemplateColumns: `40px repeat(${columns.length}, 1fr) 80px`,
        }}
      >
        <div className="text-xs opacity-70">#</div>
        {columns.map(
          (c): JSX.Element => (
            <div key={c.name} className="text-xs opacity-70">
              {c.label}
            </div>
          )
        )}
        <div />
        {(rows ?? []).map((r, i) => (
          <React.Fragment key={i}>
            <div className="text-sm opacity-70">{i + 1}</div>
            {columns.map(
              (c): JSX.Element => (
                <div key={c.name}>
                  {c.type === "number" ? (
                    <Input
                      type="number"
                      value={Number(r[c.name] ?? 0)}
                      onChange={(e): void => {
                        void setCell(i, c.name, Number(e.target.value))
                      }}
                    />
                  ) : (
                    <Input
                      value={String(r[c.name] ?? "")}
                      onChange={(e): void => {
                        void setCell(i, c.name, e.target.value)
                      }}
                    />
                  )}
                </div>
              )
            )}
            <div className="text-right">
              <Button
                type="button"
                variant="ghost"
                onClick={(): void => {
                  delRow(i)
                }}
              >
                Löschen
              </Button>
            </div>
          </React.Fragment>
        ))}
      </div>
      <Button type="button" variant="secondary" onClick={addRow}>
        Position hinzufügen
      </Button>
    </div>
  )
}

