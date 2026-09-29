/**
 * Buchungsvorlagen
 * FIBU-GL-07: Automatische Buchungsschemata verwalten und anwenden
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FileText, Plus, Play, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

type TemplateLine = {
  account_number: string
  debit_percentage: number
  credit_percentage: number
  description_template?: string
  line_number: number
}

type BookingTemplate = {
  id: string
  name: string
  description?: string
  category: string
  trigger_type: string
  lines: TemplateLine[]
  default_amount?: number
  currency: string
  active: boolean
  created_at: string
}

type ApplyResult = {
  journal_entry_id: string
  entry_number: string
  total_debit: number
  total_credit: number
}

function useBookingTemplates() {
  return useQuery({
    queryKey: ['finance', 'booking-templates'],
    queryFn: async () => (await apiClient.get<BookingTemplate[]>('/api/v1/finance/booking-templates')).data,
    staleTime: 5 * 60 * 1000,
  })
}

function useApplyTemplate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, amount, entry_date }: { id: string; amount: number; entry_date: string }) =>
      (await apiClient.post<ApplyResult>(`/api/v1/finance/booking-templates/${id}/apply`, {
        template_id: id,
        amount,
        entry_date,
      })).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['finance', 'journal-entries'] })
    },
  })
}

function useDeleteTemplate() {
  const qc = useQueryClient()
  const { toast } = useToast()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/finance/booking-templates/${id}`)
    },
    onSuccess: () => {
      toast({ title: 'Vorlage gelöscht' })
      void qc.invalidateQueries({ queryKey: ['finance', 'booking-templates'] })
    },
    onError: () => {
      toast({ title: 'Löschen fehlgeschlagen', description: 'Die Vorlage konnte nicht gelöscht werden.', variant: 'destructive' })
    },
  })
}

const CATEGORIES = ['GENERAL', 'RECURRING', 'PAYROLL', 'DEPRECIATION', 'TAX', 'INTERCOMPANY'] as const

const CATEGORY_LABELS: Record<(typeof CATEGORIES)[number], string> = {
  GENERAL: 'Allgemein',
  RECURRING: 'Wiederkehrend',
  PAYROLL: 'Personal',
  DEPRECIATION: 'Abschreibung',
  TAX: 'Steuer',
  INTERCOMPANY: 'Konzern',
}

function ApplyDialog({ template, onClose }: { template: BookingTemplate; onClose: () => void }) {
  const apply = useApplyTemplate()
  const [amount, setAmount] = useState(String(template.default_amount ?? ''))
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [result, setResult] = useState<ApplyResult | null>(null)

  const handleApply = async () => {
    try {
      const res = await apply.mutateAsync({ id: template.id, amount: parseFloat(amount), entry_date: date })
      setResult(res as unknown as ApplyResult)
    } catch {
      // Fehlertext unter den Knöpfen über apply.isError
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-3">
      <Card className="max-h-[90vh] w-full max-w-md overflow-y-auto">
        <CardHeader>
          <CardTitle>Vorlage anwenden: {template.name}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {result ? (
            <div className="space-y-2 text-sm">
              <p className="text-status-success font-medium">Buchung erfolgreich erstellt!</p>
              <p>Buchungs-Nr.: <span className="font-mono font-semibold">{result.entry_number}</span></p>
              <p>Soll: <span className="font-semibold">{Number(result.total_debit).toFixed(2)} {template.currency}</span></p>
              <p>Haben: <span className="font-semibold">{Number(result.total_credit).toFixed(2)} {template.currency}</span></p>
              <Button className="min-h-touch w-full touch-manipulation" onClick={onClose}>Schließen</Button>
            </div>
          ) : (
            <>
              <div className="space-y-1">
                <Label>Betrag ({template.currency})</Label>
                <Input
                  className="min-h-touch text-base"
                  type="number"
                  inputMode="decimal"
                  step="0.01"
                  min="0"
                  required
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <Label>Buchungsdatum</Label>
                <Input
                  className="min-h-touch text-base"
                  type="date"
                  required
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                />
              </div>
              <div className="flex flex-wrap gap-2">
                <Button className="min-h-touch touch-manipulation" onClick={() => { void handleApply() }} disabled={apply.isPending || !amount}>
                  <Play className="h-4 w-4 mr-2" />
                  {apply.isPending ? 'Buche…' : 'Buchung erstellen'}
                </Button>
                <Button variant="outline" className="min-h-touch touch-manipulation" onClick={onClose} disabled={apply.isPending}>Abbrechen</Button>
              </div>
              {apply.isError && (
                <p className="text-status-error text-sm">Fehler beim Anwenden der Vorlage.</p>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function TemplateCard({ template }: { template: BookingTemplate }) {
  const [expanded, setExpanded] = useState(false)
  const [applying, setApplying] = useState(false)
  const deleteTemplate = useDeleteTemplate()

  return (
    <>
      {applying && <ApplyDialog template={template} onClose={() => setApplying(false)} />}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold text-base">{template.name}</h3>
              {template.description && (
                <p className="text-sm text-muted-foreground">{template.description}</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{CATEGORY_LABELS[template.category as (typeof CATEGORIES)[number]] ?? template.category}</Badge>
              <Badge variant={template.active ? 'default' : 'secondary'}>
                {template.active ? 'Aktiv' : 'Inaktiv'}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Auslöser: <strong className="text-foreground">{template.trigger_type === 'manual' ? 'manuell' : template.trigger_type}</strong></span>
            <span>Währung: <strong className="text-foreground">{template.currency}</strong></span>
            {template.default_amount && (
              <span>Standardbetrag: <strong className="text-foreground">
                {Number(template.default_amount).toFixed(2)} {template.currency}
              </strong></span>
            )}
          </div>

          <button
            type="button"
            className="inline-flex min-h-touch items-center gap-1 text-sm text-muted-foreground touch-manipulation hover:text-foreground"
            onClick={() => setExpanded((v) => !v)}
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            {template.lines.length} Buchungszeile{template.lines.length !== 1 ? 'n' : ''}
          </button>

          {expanded && (
            <div className="overflow-x-auto border rounded">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b bg-muted/50 text-left text-muted-foreground">
                    <th className="py-1 px-2 font-medium">Konto</th>
                    <th className="py-1 px-2 font-medium text-right">Soll %</th>
                    <th className="py-1 px-2 font-medium text-right">Haben %</th>
                    <th className="py-1 px-2 font-medium">Buchungstext</th>
                  </tr>
                </thead>
                <tbody>
                  {template.lines.map((line) => (
                    <tr key={line.line_number} className="border-b last:border-0">
                      <td className="py-1 px-2 font-mono">{line.account_number}</td>
                      <td className="py-1 px-2 text-right">{Number(line.debit_percentage).toFixed(2)}</td>
                      <td className="py-1 px-2 text-right">{Number(line.credit_percentage).toFixed(2)}</td>
                      <td className="py-1 px-2 text-muted-foreground">{line.description_template ?? '–'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="flex flex-wrap gap-2 pt-1">
            <Button className="min-h-touch touch-manipulation" onClick={() => setApplying(true)} disabled={!template.active}>
              <Play className="h-3 w-3 mr-1" />
              Anwenden
            </Button>
            <Button
              variant="ghost"
              className="min-h-touch touch-manipulation text-status-error hover:text-status-error"
              onClick={() => {
                if (!window.confirm(`Vorlage „${template.name}“ wirklich löschen?`)) return
                deleteTemplate.mutate(template.id)
              }}
              disabled={deleteTemplate.isPending}
            >
              <Trash2 className="h-3 w-3 mr-1" />
              Löschen
            </Button>
          </div>
        </CardContent>
      </Card>
    </>
  )
}

export default function BuchungsvorlagenPage(): JSX.Element {
  const { data: templates = [], isLoading } = useBookingTemplates()
  const [filterCategory, setFilterCategory] = useState('')
  const { toast } = useToast()

  const filtered = filterCategory
    ? templates.filter((t) => t.category === filterCategory)
    : templates

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Buchungsvorlagen</h1>
          <p className="text-muted-foreground">Wiederkehrende Buchungsschemata anwenden</p>
        </div>
        <Button
          className="min-h-touch touch-manipulation"
          onClick={() => {
            toast({
              title: 'Anlegen folgt noch',
              description: 'Neue Vorlagen legt die Buchhaltung derzeit über die API an. Anwenden und Löschen gehen hier.',
            })
          }}
        >
          <Plus className="h-4 w-4 mr-2" />
          Neue Vorlage
        </Button>
      </div>

      <div className="flex gap-2 flex-wrap">
        <Button
          variant={filterCategory === '' ? 'default' : 'outline'}
          className="min-h-touch touch-manipulation"
          onClick={() => setFilterCategory('')}
        >
          Alle
        </Button>
        {CATEGORIES.map((cat) => (
          <Button
            key={cat}
            variant={filterCategory === cat ? 'default' : 'outline'}
            className="min-h-touch touch-manipulation"
            onClick={() => setFilterCategory(cat)}
          >
            {CATEGORY_LABELS[cat]}
          </Button>
        ))}
      </div>

      {isLoading && (
        <p className="text-muted-foreground text-sm">Lade Buchungsvorlagen…</p>
      )}

      {!isLoading && filtered.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">Keine Buchungsvorlagen vorhanden.</p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {filtered.map((t) => (
          <TemplateCard key={t.id} template={t} />
        ))}
      </div>
    </div>
  )
}
