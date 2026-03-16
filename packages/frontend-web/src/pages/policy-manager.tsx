import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/components/ui/toast-provider"
import { CompactDecisionCard } from "@/components/workflow/CompactDecisionCard"
import { useMcpMutation, useMcpQuery } from "@/lib/mcp"
import { buildDecisionView } from "@/policy/decision-view"
import { type AlertInput, type Rule } from "@/policy/schema"

const TEXTAREA_ROWS = 12

type RulesResponse = {
  ok: boolean
  data: Rule[]
}

type UpsertResponse = {
  ok: boolean
}

type DeleteResponse = {
  ok: boolean
}

type TestResponse = {
  ok: boolean
  decision: unknown
}

function prettyJson(obj: unknown): string {
  return JSON.stringify(obj, null, 2)
}

function validateAlertInput(input: AlertInput): string | null {
  if (input.id.trim().length === 0) return "ID ist erforderlich"
  if (input.title.trim().length === 0) return "Titel ist erforderlich"
  if (input.message.trim().length === 0) return "Nachricht ist erforderlich"
  if (input.severity !== "ok" && input.severity !== "warn" && input.severity !== "crit") {
    return "Severity ist ungueltig"
  }
  if (input.kpiId !== undefined && input.kpiId.trim().length === 0) {
    return "KPI darf nicht leer sein"
  }
  if (input.delta !== undefined && !Number.isFinite(input.delta)) {
    return "Delta ist ungueltig"
  }
  return null
}

export default function PolicyManagerPage(): JSX.Element {
  const { data: rulesData } = useMcpQuery<RulesResponse>("policy", "list", [])
  const deleteMutation = useMcpMutation<{ id: string }, DeleteResponse>("policy", "delete")
  const { push } = useToast()

  const rules = rulesData?.data?.data ?? []

  const handleDelete = (id: string): void => {
    if (typeof window !== "undefined" && window.confirm(`Policy "${id}" wirklich loeschen?`)) {
      deleteMutation.mutate(
        { id },
        {
          onSuccess: (): void => {
            push("Policy geloescht")
          },
          onError: (): void => {
            push("Loeschen fehlgeschlagen")
          },
        }
      )
    }
  }

  const handleExport = (): void => {
    const json = prettyJson({ rules })
    const blob = new Blob([json], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement("a")
    anchor.href = url
    anchor.download = "policies-export.json"
    anchor.click()
    URL.revokeObjectURL(url)
    push("Export gestartet")
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Policy Manager</h2>
        <div className="flex gap-2">
          <ImportDialog />
          <Button variant="secondary" onClick={handleExport}>
            Export JSON
          </Button>
        </div>
      </div>

      <Card className="p-4">
        <h3 className="mb-3 font-semibold">Aktive Policies ({rules.length})</h3>
        {rules.length === 0 ? (
          <p className="text-sm opacity-70">Keine Policies vorhanden.</p>
        ) : null}
        <ul className="space-y-2">
          {rules.map((rule): JSX.Element => (
            <li
              key={rule.id}
              className="flex items-start justify-between rounded-lg border p-3"
            >
              <div className="flex-1">
                <div className="font-medium">{rule.id}</div>
                <div className="text-sm opacity-70">
                  {rule.action} | KPI: {rule.when.kpiId} | Severity: {rule.when.severity.join(", ")}
                </div>
                <div className="mt-1 text-xs">
                  {rule.autoExecute === true ? "Auto-Execute" : "Manuelle Ausfuehrung"}
                  {rule.approval?.required === true ? " | Approval required" : ""}
                  {rule.window !== undefined ? " | Zeitfenster aktiv" : ""}
                </div>
              </div>
              <Button
                size="sm"
                variant="destructive"
                onClick={(): void => {
                  handleDelete(rule.id)
                }}
              >
                Loeschen
              </Button>
            </li>
          ))}
        </ul>
      </Card>

      <SimulatorPanel />
    </div>
  )
}

function ImportDialog(): JSX.Element {
  const [open, setOpen] = useState<boolean>(false)
  const [text, setText] = useState<string>("")
  const upsert = useMcpMutation<{ rules: Rule[] }, UpsertResponse>("policy", "upsert")
  const { push } = useToast()

  const handleImport = async (): Promise<void> => {
    try {
      const parsed = JSON.parse(text) as { rules?: unknown }
      if (!Array.isArray(parsed.rules)) {
        throw new Error("rules[] fehlt")
      }

      const { RuleSchema } = await import("@/policy/schema")
      const validRules: Rule[] = []
      for (const rule of parsed.rules) {
        validRules.push(RuleSchema.parse(rule))
      }

      upsert.mutate(
        { rules: validRules },
        {
          onSuccess: (): void => {
            push("Import erfolgreich")
            setOpen(false)
            setText("")
          },
          onError: (): void => {
            push("Import fehlgeschlagen")
          },
        }
      )
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      push(`JSON ungueltig: ${errorMessage}`)
    }
  }

  return (
    <>
      <Button
        variant="secondary"
        onClick={(): void => {
          setOpen(true)
        }}
      >
        Import JSON
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Policies importieren</DialogTitle>
            <DialogDescription>
              Fuege JSON ein (Format: {`{ "rules": Rule[] }`}).
            </DialogDescription>
          </DialogHeader>
          <textarea
            rows={TEXTAREA_ROWS}
            value={text}
            onChange={(event): void => {
              setText(event.target.value)
            }}
            className="w-full rounded-md border p-2 font-mono text-sm"
          />
          <div className="text-right">
            <Button onClick={handleImport}>Importieren</Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

function SimulatorPanel(): JSX.Element {
  const test = useMcpMutation<
    { alert: AlertInput; roles: string[] },
    TestResponse
  >("policy", "test")
  const { push } = useToast()
  const [roles, setRoles] = useState<string>("manager")
  const [values, setValues] = useState<AlertInput>({
    id: "sim-1",
    kpiId: "margin",
    title: "Marge unter Ziel",
    message: "Marge 14,2%",
    severity: "warn",
    delta: -3,
  })
  const [formError, setFormError] = useState<string | null>(null)
  const decisionView = buildDecisionView(test.data?.data?.decision)

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>): void => {
    event.preventDefault()
    const validationError = validateAlertInput(values)
    if (validationError !== null) {
      setFormError(validationError)
      return
    }

    setFormError(null)
    const roleArray = roles
      .split(",")
      .map((value) => value.trim())
      .filter((value) => value.length > 0)

    test.mutate(
      { alert: values, roles: roleArray },
      {
        onError: (): void => {
          push("Test fehlgeschlagen")
        },
      }
    )
  }

  return (
    <Card className="space-y-3 p-4">
      <h3 className="font-semibold">Policy-Test-Simulator</h3>
      <form
        className="grid grid-cols-2 gap-3 md:grid-cols-3"
        onSubmit={handleSubmit}
      >
        <div>
          <Label>KPI</Label>
          <Input value={values.kpiId ?? ""} onChange={(event) => setValues((current) => ({ ...current, kpiId: event.target.value }))} />
        </div>
        <div>
          <Label>Severity</Label>
          <select
            className="h-9 w-full rounded-md border px-3"
            value={values.severity}
            onChange={(event) => setValues((current) => ({ ...current, severity: event.target.value as AlertInput["severity"] }))}
          >
            <option value="warn">warn</option>
            <option value="crit">crit</option>
          </select>
        </div>
        <div>
          <Label>Delta (optional)</Label>
          <Input
            type="number"
            step="0.1"
            value={values.delta ?? ""}
            onChange={(event) =>
              setValues((current) => ({
                ...current,
                delta: event.target.value === "" ? undefined : Number(event.target.value),
              }))
            }
          />
        </div>
        <div>
          <Label>ID</Label>
          <Input value={values.id} onChange={(event) => setValues((current) => ({ ...current, id: event.target.value }))} />
        </div>
        <div>
          <Label>Titel</Label>
          <Input value={values.title} onChange={(event) => setValues((current) => ({ ...current, title: event.target.value }))} />
        </div>
        <div>
          <Label>Nachricht</Label>
          <Input value={values.message} onChange={(event) => setValues((current) => ({ ...current, message: event.target.value }))} />
        </div>
        <div className="md:col-span-3">
          <Label>Rollen (CSV)</Label>
          <Input
            value={roles}
            onChange={(event): void => {
              setRoles(event.target.value)
            }}
          />
        </div>
        {formError !== null ? (
          <div className="md:col-span-3 text-sm text-red-600">{formError}</div>
        ) : null}
        <div className="text-right md:col-span-3">
          <Button type="submit">Entscheidung simulieren</Button>
        </div>
      </form>

      {test.data?.data?.decision !== undefined ? (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <Card className="p-3">
            <div className="mb-2 text-sm opacity-70">Policy-Erklaerung</div>
            {decisionView !== null ? (
              <CompactDecisionCard view={decisionView} title="Policy" />
            ) : (
              <p className="text-sm text-muted-foreground">
                Antwortformat unbekannt, nur Raw-Decision verfuegbar.
              </p>
            )}
          </Card>

          <Card className="p-3">
            <div className="mb-2 text-sm opacity-70">Decision JSON</div>
            <pre className="text-xs whitespace-pre-wrap">
              {prettyJson(test.data.data.decision)}
            </pre>
          </Card>

          <Card className="p-3 md:col-span-2">
            <div className="text-sm opacity-70">Hinweis</div>
            <p className="text-sm">
              "allow" bedeutet erlaubt. "execute:true" bedeutet Auto-Execute.
              "needsApproval" bedeutet Freigabe im Vier-Augen-Prinzip.
            </p>
          </Card>
        </div>
      ) : null}
    </Card>
  )
}
