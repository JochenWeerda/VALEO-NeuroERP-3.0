import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/components/ui/toast-provider"
import { useMcpMutation, useMcpQuery } from "@/lib/mcp"
import { type AlertInput, AlertInputSchema, type Rule, RuleSchema } from "@/policy/schema"

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

/**
 * Formatiert JSON für Anzeige
 */
function prettyJson(obj: unknown): string {
  return JSON.stringify(obj, null, 2)
}

/**
 * Policy-Manager Admin-Page
 * CRUD für Policy-Regeln mit Import/Export und Test-Simulator
 */
export default function PolicyManagerPage(): JSX.Element {
  const { data: rulesData } = useMcpQuery<RulesResponse>("policy", "list", [])
  const deleteMutation = useMcpMutation<{ id: string }, DeleteResponse>("policy", "delete")
  const { push } = useToast()

  const rules = rulesData?.data?.data ?? []

  const handleDelete = (id: string): void => {
    if (typeof window !== 'undefined' && window.confirm(`Policy "${id}" wirklich löschen?`)) {
      deleteMutation.mutate(
        { id },
        {
          onSuccess: (): void => {
            push("✔ Policy gelöscht")
          },
          onError: (): void => {
            push("❌ Löschen fehlgeschlagen")
          },
        }
      )
    }
  }

  const handleExport = (): void => {
    const json = prettyJson({ rules })
    const blob = new Blob([json], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "policies-export.json"
    a.click()
    URL.revokeObjectURL(url)
    push("✔ Export gestartet")
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

      {/* Rules-Liste */}
      <Card className="p-4">
        <h3 className="font-semibold mb-3">Aktive Policies ({rules.length})</h3>
        {rules.length === 0 && (
          <p className="text-sm opacity-70">Keine Policies vorhanden.</p>
        )}
        <ul className="space-y-2">
          {rules.map((rule): JSX.Element => (
            <li
              key={rule.id}
              className="border rounded-lg p-3 flex items-start justify-between"
            >
              <div className="flex-1">
                <div className="font-medium">{rule.id}</div>
                <div className="text-sm opacity-70">
                  {rule.action} | KPI: {rule.when.kpiId} | Severity:{" "}
                  {rule.when.severity.join(", ")}
                </div>
                <div className="text-xs mt-1">
                  {rule.autoExecute === true ? "✅ Auto-Execute" : ""}
                  {rule.approval?.required === true
                    ? " | 🔐 Approval required"
                    : ""}
                  {rule.window !== undefined
                    ? ` | ⏰ Zeitfenster`
                    : ""}
                </div>
              </div>
              <Button
                size="sm"
                variant="destructive"
                onClick={(): void => {
                  handleDelete(rule.id)
                }}
              >
                Löschen
              </Button>
            </li>
          ))}
        </ul>
      </Card>

      {/* Simulator */}
      <SimulatorPanel />
    </div>
  )
}

/**
 * Import-Dialog Komponente
 */
function ImportDialog(): JSX.Element {
  const [open, setOpen] = useState<boolean>(false)
  const [text, setText] = useState<string>("")
  const upsert = useMcpMutation<{ rules: Rule[] }, UpsertResponse>("policy", "upsert")
  const { push } = useToast()

  const handleImport = (): void => {
    try {
      const parsed = JSON.parse(text) as { rules?: unknown }
      if (!Array.isArray(parsed.rules)) {
        throw new Error("rules[] fehlt")
      }

      const validRules: Rule[] = []
      for (const r of parsed.rules) {
        const validatedRule = RuleSchema.parse(r)
        validRules.push(validatedRule)
      }

      upsert.mutate(
        { rules: validRules },
        {
          onSuccess: (): void => {
            push("✔ Import erfolgreich")
            setOpen(false)
            setText("")
          },
          onError: (): void => {
            push("❌ Import fehlgeschlagen")
          },
        }
      )
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : String(e)
      push(`❌ JSON ungültig: ${errorMessage}`)
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
              Füge JSON ein (Format: {`{ "rules": Rule[] }`}).
            </DialogDescription>
          </DialogHeader>
          <textarea
            rows={TEXTAREA_ROWS}
            value={text}
            onChange={(e): void => {
              setText(e.target.value)
            }}
            className="w-full border rounded-md p-2 font-mono text-sm"
          />
          <div className="text-right">
            <Button onClick={handleImport}>Importieren</Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

/**
 * Simulator-Panel Komponente
 */
function SimulatorPanel(): JSX.Element {
  const test = useMcpMutation<
    { alert: AlertInput; roles: string[] },
    TestResponse
  >("policy", "test")
  const { push } = useToast()
  const [roles, setRoles] = useState<string>("manager")

  const form = useForm<AlertInput>({
    resolver: zodResolver(AlertInputSchema),
    defaultValues: {
      id: "sim-1",
      kpiId: "margin",
      title: "Marge unter Ziel",
      message: "Marge 14,2%",
      severity: "warn",
      delta: -3,
    },
  })

  const handleSubmit = (values: AlertInput): void => {
    const roleArray = roles
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0)

    test.mutate(
      { alert: values, roles: roleArray },
      {
        onError: (): void => {
          push("❌ Test fehlgeschlagen")
        },
      }
    )
  }

  return (
    <Card className="p-4 space-y-3">
      <h3 className="font-semibold">Policy-Test-Simulator</h3>
      <form
        className="grid grid-cols-2 md:grid-cols-3 gap-3"
        onSubmit={form.handleSubmit(handleSubmit)}
      >
        <div>
          <Label>KPI</Label>
          <Input {...form.register("kpiId")} />
        </div>
        <div>
          <Label>Severity</Label>
          <select
            className="w-full border rounded-md h-9 px-3"
            {...form.register("severity")}
          >
            <option value="warn">warn</option>
            <option value="crit">crit</option>
          </select>
        </div>
        <div>
          <Label>Δ (optional)</Label>
          <Input
            type="number"
            step="0.1"
            {...form.register("delta", { valueAsNumber: true })}
          />
        </div>
        <div className="md:col-span-3">
          <Label>Rollen (CSV)</Label>
          <Input
            value={roles}
            onChange={(e): void => {
              setRoles(e.target.value)
            }}
          />
        </div>
        <div className="md:col-span-3 text-right">
          <Button type="submit">Entscheidung simulieren</Button>
        </div>
      </form>

      {test.data?.data?.decision !== undefined && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Card className="p-3">
            <div className="text-sm opacity-70">Decision</div>
            <pre className="text-xs whitespace-pre-wrap">
              {prettyJson(test.data.data.decision)}
            </pre>
          </Card>
          <Card className="p-3">
            <div className="text-sm opacity-70">Hinweis</div>
            <p className="text-sm">
              "allow" → Aktion erlaubt; "execute:true" → Auto-Execute;
              "needsApproval" → Vier Augen nötig.
            </p>
          </Card>
        </div>
      )}
    </Card>
  )
}

