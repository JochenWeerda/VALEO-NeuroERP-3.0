import * as React from "react"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/components/ui/toast-provider"
import { validateValues } from "@/features/forms/validator"
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
  onChange?: (_partial: Partial<T>) => void
  onSubmit: (_values: T) => Promise<void> | void
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
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [validationSummary, setValidationSummary] = useState<string[]>([])
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
    setErrors((prev) => {
      if (prev[name] === undefined) {
        return prev
      }
      const nextErrors = { ...prev }
      delete nextErrors[name]
      return nextErrors
    })
    setValidationSummary([])
    onChange?.({ [name]: value } as Partial<T>)
    void runPolicy(next)
  }

  async function runPolicy(v: Record<string, unknown>): Promise<void> {
    try {
      const lines = (v as { lines?: unknown[] }).lines ?? []
      for (const entry of lines) {
        const line = entry as { qty?: number; price?: number; cost?: number }
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

  async function handleSubmit(event: React.FormEvent): Promise<void> {
    event.preventDefault()
    const { ok, errs, parsed, summary } = validateValues(schema, values)
    if (!ok) {
      setErrors(errs)
      setValidationSummary(summary)
      push("Bitte Eingaben prüfen")
      return
    }
    if (policy.level === "block") {
      push(`Speichern blockiert: ${policy.message ?? "Policy-Verstoß"}`)
      return
    }
    setErrors({})
    setValidationSummary([])
    await onSubmit(parsed as T)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-xl font-semibold">{schema.title}</h2>

      {policy.level !== "allow" ? (
        <Card
          className={`border p-3 ${
            policy.level === "warn"
              ? "border-amber-300 bg-amber-50"
              : "border-red-300 bg-red-50"
          }`}
        >
          <div className="text-sm">
            {policy.message ?? (policy.level === "warn" ? "Bitte prüfen" : "Aktion blockiert")}
          </div>
        </Card>
      ) : null}

      {validationSummary.length > 0 ? (
        <Card className="border border-red-300 bg-red-50 p-3">
          <div className="text-sm font-medium text-red-800">
            Validierung noch nicht abgeschlossen
          </div>
          <ul className="mt-2 list-disc pl-5 text-sm text-red-700">
            {validationSummary.slice(0, 4).map((entry) => (
              <li key={entry}>{entry}</li>
            ))}
          </ul>
        </Card>
      ) : null}

      <Card className="space-y-3 p-4">
        {schema.fields.map((field): JSX.Element => (
          <div key={field.name} className="grid gap-1">
            <Label htmlFor={field.name}>
              {field.label}
              {field.required === true ? " *" : ""}
            </Label>
            <FieldRenderer
              field={field}
              value={values[field.name]}
              onChange={(nextValue): void => {
                setField(field.name, nextValue)
              }}
            />
            {errors[field.name] !== undefined ? (
              <span className="text-sm text-red-600">{errors[field.name]}</span>
            ) : null}
          </div>
        ))}
      </Card>

      {schema.lines !== undefined ? (
        <Card className="space-y-2 p-4">
          <Label>{schema.lines.label}</Label>
          <LinesEditor
            columns={schema.lines.columns}
            value={(values[schema.lines.name] as unknown[]) ?? []}
            onChange={(rows): void => {
              const lines = schema.lines
              if (lines) setField(lines.name, rows)
            }}
          />
          {Object.entries(errors)
            .filter(([path]) => path.startsWith(`${schema.lines?.name}.`))
            .map(([path, message]) => (
              <div key={path} className="text-sm text-red-600">
                {message}
              </div>
            ))}
        </Card>
      ) : null}

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
  onChange: (_rows: unknown[]) => void
}): JSX.Element {
  const rows = value as Record<string, unknown>[]

  async function setCell(index: number, name: string, nextValue: unknown): Promise<void> {
    let next = rows.map((row, rowIndex) =>
      rowIndex === index ? { ...row, [name]: nextValue } : row
    )

    if (name === "article" && typeof nextValue === "string" && nextValue.length > 0) {
      try {
        const response = await fetch(`/api/mcp/lookup/articles?q=${encodeURIComponent(nextValue)}`)
        const data = (await response.json()) as {
          ok: boolean
          data: Array<{ id: string; cost?: number; price?: number }>
        }
        const article = data.data?.find((entry) => entry.id === nextValue)
        if (article !== undefined) {
          next = rows.map((row, rowIndex) =>
            rowIndex === index
              ? {
                  ...row,
                  [name]: nextValue,
                  price: article.price ?? article.cost ?? row.price ?? 0,
                  cost: article.cost ?? row.cost ?? 0,
                }
              : row
          )
        }
      } catch {
        // Ignore optional lookup failures.
      }
    }

    onChange(next)
  }

  function addRow(): void {
    onChange([
      ...(rows ?? []),
      Object.fromEntries(columns.map((column) => [column.name, column.type === "number" ? 0 : ""])),
    ])
  }

  function deleteRow(index: number): void {
    onChange((rows ?? []).filter((_, rowIndex) => rowIndex !== index))
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
        {columns.map((column): JSX.Element => (
          <div key={column.name} className="text-xs opacity-70">
            {column.label}
          </div>
        ))}
        <div />
        {(rows ?? []).map((row, index) => (
          <React.Fragment key={index}>
            <div className="text-sm opacity-70">{index + 1}</div>
            {columns.map((column): JSX.Element => (
              <div key={column.name}>
                {column.type === "number" ? (
                  <Input
                    type="number"
                    value={Number(row[column.name] ?? 0)}
                    onChange={(event): void => {
                      void setCell(index, column.name, Number(event.target.value))
                    }}
                  />
                ) : (
                  <Input
                    value={String(row[column.name] ?? "")}
                    onChange={(event): void => {
                      void setCell(index, column.name, event.target.value)
                    }}
                  />
                )}
              </div>
            ))}
            <div className="text-right">
              <Button
                type="button"
                variant="ghost"
                onClick={(): void => {
                  deleteRow(index)
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
