import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import {
  listRules,
  createRule,
  updateRule,
  deleteRule,
  type PositionRule,
  type PositionRuleIn,
} from '@/lib/api/positions'

const defaultRule: PositionRuleIn = {
  scope_type: 'ARTICLE',
  scope_id: '',
  neg_tolerance_qty: -50,
  max_short_days: 0,
  yellow_threshold: null,
  red_threshold: null,
  approval_required: false,
  approval_role: null,
  active_from: null,
  active_to: null,
}

export default function FrmPositionRules(): JSX.Element {
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<PositionRule | null>(null)
  const [form, setForm] = useState<PositionRuleIn>(defaultRule)

  const { data: rules = [], isLoading } = useQuery({
    queryKey: ['positions', 'rules'],
    queryFn: async () => listRules(),
  })

  const createMutation = useMutation({
    mutationFn: (payload: PositionRuleIn) => createRule(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions', 'rules'] })
      setDialogOpen(false)
      setForm(defaultRule)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ ruleId, payload }: { ruleId: string; payload: PositionRuleIn }) =>
      updateRule(ruleId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions', 'rules'] })
      setEditingRule(null)
      setForm(defaultRule)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (ruleId: string) => deleteRule(ruleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions', 'rules'] })
    },
  })

  const handleOpenCreate = () => {
    setEditingRule(null)
    setForm(defaultRule)
    setDialogOpen(true)
  }

  const handleOpenEdit = (r: PositionRule) => {
    setEditingRule(r)
    setForm({
      scope_type: r.scope_type,
      scope_id: r.scope_id,
      neg_tolerance_qty: r.neg_tolerance_qty,
      max_short_days: r.max_short_days,
      yellow_threshold: r.yellow_threshold ?? null,
      red_threshold: r.red_threshold ?? null,
      approval_required: r.approval_required,
      approval_role: r.approval_role ?? null,
      active_from: r.active_from ?? null,
      active_to: r.active_to ?? null,
    })
    setDialogOpen(true)
  }

  const handleSubmit = () => {
    if (form.neg_tolerance_qty > 0) return
    if (editingRule) {
      updateMutation.mutate({ ruleId: editingRule.rule_id, payload: form })
    } else {
      createMutation.mutate(form)
    }
  }

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Position-Regeln (No-Speculation Guard)</h1>
        <Button onClick={handleOpenCreate}>
          <Plus className="mr-2 h-4 w-4" />
          Neue Regel
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Regeln</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground">Lade…</p>}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Scope</TableHead>
                <TableHead>Scope-ID</TableHead>
                <TableHead className="text-right">Negative Toleranz (t)</TableHead>
                <TableHead className="text-right">Max Short Days</TableHead>
                <TableHead>Gelb / Rot</TableHead>
                <TableHead>Freigabe</TableHead>
                <TableHead>Freigaberolle</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rules.map((r) => (
                <TableRow key={r.rule_id}>
                  <TableCell>{r.scope_type}</TableCell>
                  <TableCell>{r.scope_id}</TableCell>
                  <TableCell className="text-right">{r.neg_tolerance_qty}</TableCell>
                  <TableCell className="text-right">{r.max_short_days}</TableCell>
                  <TableCell>
                    {r.yellow_threshold ?? '-'} / {r.red_threshold ?? '-'}
                  </TableCell>
                  <TableCell>{r.approval_required ? 'Ja' : 'Nein'}</TableCell>
                  <TableCell>{r.approval_role ?? '-'}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="icon" onClick={() => handleOpenEdit(r)}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => deleteMutation.mutate(r.rule_id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingRule ? 'Regel bearbeiten' : 'Neue Regel'}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div>
              <Label>Scope-Typ</Label>
              <select
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                value={form.scope_type}
                onChange={(e) => setForm({ ...form, scope_type: e.target.value })}
              >
                <option value="ARTICLE">Artikel</option>
                <option value="GROUP">Gruppe</option>
              </select>
            </div>
            <div>
              <Label>Scope-ID (Artikel-ID oder Gruppen-ID)</Label>
              <Input
                value={form.scope_id}
                onChange={(e) => setForm({ ...form, scope_id: e.target.value })}
              />
            </div>
            <div>
              <Label>Negative Toleranz (t) – muss ≤ 0 sein</Label>
              <Input
                type="number"
                value={form.neg_tolerance_qty}
                onChange={(e) =>
                  setForm({ ...form, neg_tolerance_qty: Number(e.target.value) })
                }
              />
            </div>
            <div>
              <Label>Max. Short-Tage</Label>
              <Input
                type="number"
                min={0}
                value={form.max_short_days ?? 0}
                onChange={(e) =>
                  setForm({ ...form, max_short_days: Number(e.target.value) || 0 })
                }
              />
            </div>
            <div>
              <Label>Gelb-Schwelle (optional)</Label>
              <Input
                type="number"
                value={form.yellow_threshold ?? ''}
                onChange={(e) =>
                  setForm({
                    ...form,
                    yellow_threshold: e.target.value ? Number(e.target.value) : null,
                  })
                }
              />
            </div>
            <div>
              <Label>Rot-Schwelle (optional)</Label>
              <Input
                type="number"
                value={form.red_threshold ?? ''}
                onChange={(e) =>
                  setForm({
                    ...form,
                    red_threshold: e.target.value ? Number(e.target.value) : null,
                  })
                }
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="approval_required"
                checked={form.approval_required}
                onChange={(e) =>
                  setForm({ ...form, approval_required: e.target.checked })
                }
              />
              <Label htmlFor="approval_required">Freigabe erforderlich</Label>
            </div>
            <div>
              <Label>Freigaberolle (z. B. teamleiter, gf)</Label>
              <Input
                value={form.approval_role ?? ''}
                onChange={(e) =>
                  setForm({ ...form, approval_role: e.target.value || null })
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={
                form.neg_tolerance_qty > 0 ||
                !form.scope_id ||
                createMutation.isPending ||
                updateMutation.isPending
              }
            >
              {editingRule ? 'Speichern' : 'Anlegen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
