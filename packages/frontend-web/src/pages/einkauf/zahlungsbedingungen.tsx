import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  useCreateZahlungsbedingung,
  useDeleteZahlungsbedingung,
  useUpdateZahlungsbedingung,
  useZahlungsbedingungen,
  ZAHLUNGSARTEN,
  type Zahlungsbedingung,
  type ZahlungsbedingungCreate,
} from '@/lib/api/fibu'
import { CreditCard, Edit3, Plus, Save, Search, Trash2, X } from 'lucide-react'

const emptyForm: ZahlungsbedingungCreate = {
  zabd_nr: '',
  bezeichnung: '',
  zahlungsziel_tage: 30,
  skonto1_tage: null,
  skonto1_prozent: null,
  skonto2_tage: null,
  skonto2_prozent: null,
  netto_tage: 30,
  manuelles_datum: false,
  zahlungsart: 'ueberweisung',
}

function parseOptionalInt(value: string): number | null {
  const trimmed = value.trim()
  if (trimmed === '') return null
  const parsed = Number.parseInt(trimmed, 10)
  return Number.isNaN(parsed) ? null : parsed
}

function parseOptionalFloat(value: string): number | null {
  const trimmed = value.trim()
  if (trimmed === '') return null
  const parsed = Number.parseFloat(trimmed)
  return Number.isNaN(parsed) ? null : parsed
}

function formatSkonto(row: Zahlungsbedingung): string {
  const parts: string[] = []
  if (row.skonto1_tage != null && row.skonto1_prozent != null) {
    parts.push(`${row.skonto1_prozent}% / ${row.skonto1_tage}T`)
  }
  if (row.skonto2_tage != null && row.skonto2_prozent != null) {
    parts.push(`${row.skonto2_prozent}% / ${row.skonto2_tage}T`)
  }
  return parts.length > 0 ? parts.join(', ') : '-'
}

export default function ZahlungsbedingungenPage(): JSX.Element {
  const { data: items, isLoading, isError, error, refetch } = useZahlungsbedingungen()
  const createMutation = useCreateZahlungsbedingung()
  const updateMutation = useUpdateZahlungsbedingung()
  const deleteMutation = useDeleteZahlungsbedingung()
  const [searchTerm, setSearchTerm] = useState('')
  const [editingNr, setEditingNr] = useState<string | null>(null)
  const [deletingNr, setDeletingNr] = useState<string | null>(null)
  const [form, setForm] = useState<ZahlungsbedingungCreate>(emptyForm)

  if (isLoading) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Alert variant="destructive">
          <AlertTitle>Zahlungsbedingungen konnten nicht geladen werden</AlertTitle>
          <AlertDescription>{error instanceof Error ? error.message : 'Unbekannter Fehler'}</AlertDescription>
        </Alert>
        <Button type="button" onClick={() => void refetch()}>
          Erneut laden
        </Button>
      </div>
    )
  }

  const rows = items ?? []
  const list = rows.filter((row) => {
    const query = searchTerm.trim().toLowerCase()
    if (!query) return true
    return row.zabd_nr.toLowerCase().includes(query) || row.bezeichnung.toLowerCase().includes(query)
  })
  const isEditing = editingNr !== null
  const isSaving = createMutation.isPending || updateMutation.isPending
  const canSubmit = form.zabd_nr.trim() !== '' && form.bezeichnung.trim() !== ''

  function resetForm(): void {
    setEditingNr(null)
    setForm(emptyForm)
  }

  function startEdit(item: Zahlungsbedingung): void {
    setEditingNr(item.zabd_nr)
    setForm({
      zabd_nr: item.zabd_nr,
      bezeichnung: item.bezeichnung,
      zahlungsziel_tage: item.zahlungsziel_tage,
      skonto1_tage: item.skonto1_tage,
      skonto1_prozent: item.skonto1_prozent,
      skonto2_tage: item.skonto2_tage,
      skonto2_prozent: item.skonto2_prozent,
      netto_tage: item.netto_tage,
      manuelles_datum: item.manuelles_datum,
      zahlungsart: item.zahlungsart,
    })
  }

  async function submitForm(): Promise<void> {
    if (!canSubmit || isSaving) return
    const payload: ZahlungsbedingungCreate = {
      zabd_nr: form.zabd_nr.trim(),
      bezeichnung: form.bezeichnung.trim(),
      zahlungsziel_tage: form.zahlungsziel_tage ?? 30,
      skonto1_tage: form.skonto1_tage ?? null,
      skonto1_prozent: form.skonto1_prozent ?? null,
      skonto2_tage: form.skonto2_tage ?? null,
      skonto2_prozent: form.skonto2_prozent ?? null,
      netto_tage: form.netto_tage ?? null,
      manuelles_datum: form.manuelles_datum ?? false,
      zahlungsart: form.zahlungsart ?? 'ueberweisung',
    }
    try {
      if (isEditing) {
        await updateMutation.mutateAsync({ zabd_nr: editingNr, payload })
        toast.success('Zahlungsbedingung aktualisiert')
      } else {
        await createMutation.mutateAsync(payload)
        toast.success('Zahlungsbedingung angelegt')
      }
      resetForm()
    } catch {
      toast.error('Speichern fehlgeschlagen')
    }
  }

  async function handleDelete(zabd_nr: string): Promise<void> {
    if (deleteMutation.isPending) return
    setDeletingNr(zabd_nr)
    try {
      await deleteMutation.mutateAsync(zabd_nr)
      toast.success('Zahlungsbedingung deaktiviert')
      if (editingNr === zabd_nr) resetForm()
    } catch {
      toast.error('Loeschen fehlgeschlagen')
    } finally {
      setDeletingNr(null)
    }
  }

  const columns = [
    {
      key: 'zabd_nr' as const,
      label: 'ZABD-Nr.',
      render: (row: Zahlungsbedingung) => (
        <button
          type="button"
          onClick={() => startEdit(row)}
          className="font-medium text-primary hover:underline"
        >
          {row.zabd_nr}
        </button>
      ),
    },
    { key: 'bezeichnung' as const, label: 'Bezeichnung' },
    {
      key: 'zahlungsziel_tage' as const,
      label: 'Zahlungsziel (Tage)',
      render: (row: Zahlungsbedingung) => <span className="tabular-nums">{row.zahlungsziel_tage}</span>,
    },
    {
      key: 'skonto',
      label: 'Skonto',
      render: (row: Zahlungsbedingung) => formatSkonto(row),
    },
    {
      key: 'zahlungsart' as const,
      label: 'Zahlungsart',
      render: (row: Zahlungsbedingung) =>
        ZAHLUNGSARTEN.find((option) => option.value === row.zahlungsart)?.label ?? row.zahlungsart,
    },
    {
      key: 'actions',
      label: '',
      render: (row: Zahlungsbedingung) => (
        <div className="flex justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => startEdit(row)}
            aria-label={`${row.zabd_nr} bearbeiten`}
          >
            <Edit3 className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={deletingNr === row.zabd_nr}
            onClick={() => void handleDelete(row.zabd_nr)}
            aria-label={`${row.zabd_nr} deaktivieren`}
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Zahlungsbedingungen</h1>
          <p className="text-muted-foreground">Stammdaten — Zahlungsziel, Skonto und Zahlungsart (Wave 10)</p>
        </div>
        <Button type="button" onClick={resetForm} className="gap-2">
          <Plus className="h-4 w-4" aria-hidden="true" />
          Neue Zahlungsbedingung
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Zahlungsbedingungen gesamt</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <CreditCard className="h-5 w-5 text-primary" aria-hidden="true" />
            <span className="text-2xl font-bold tabular-nums">{rows.length}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{isEditing ? `Zahlungsbedingung ${editingNr} bearbeiten` : 'Neue Zahlungsbedingung'}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1">
              <Label htmlFor="zabd-nr">ZABD-Nr.</Label>
              <Input
                id="zabd-nr"
                value={form.zabd_nr}
                onChange={(event) => setForm((prev) => ({ ...prev, zabd_nr: event.target.value }))}
                disabled={isEditing}
              />
            </div>
            <div className="space-y-1 md:col-span-2">
              <Label htmlFor="zabd-bezeichnung">Bezeichnung</Label>
              <Input
                id="zabd-bezeichnung"
                value={form.bezeichnung}
                onChange={(event) => setForm((prev) => ({ ...prev, bezeichnung: event.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="zahlungsziel">Zahlungsziel (Tage)</Label>
              <Input
                id="zahlungsziel"
                type="number"
                min={0}
                value={form.zahlungsziel_tage ?? 30}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    zahlungsziel_tage: Number.parseInt(event.target.value, 10) || 0,
                  }))
                }
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="netto-tage">Netto (Tage)</Label>
              <Input
                id="netto-tage"
                type="number"
                min={0}
                value={form.netto_tage ?? ''}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, netto_tage: parseOptionalInt(event.target.value) }))
                }
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="skonto1-tage">Skonto 1 (Tage)</Label>
              <Input
                id="skonto1-tage"
                type="number"
                min={0}
                value={form.skonto1_tage ?? ''}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, skonto1_tage: parseOptionalInt(event.target.value) }))
                }
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="skonto1-prozent">Skonto 1 (%)</Label>
              <Input
                id="skonto1-prozent"
                type="number"
                min={0}
                max={100}
                step="0.01"
                value={form.skonto1_prozent ?? ''}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, skonto1_prozent: parseOptionalFloat(event.target.value) }))
                }
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="skonto2-tage">Skonto 2 (Tage)</Label>
              <Input
                id="skonto2-tage"
                type="number"
                min={0}
                value={form.skonto2_tage ?? ''}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, skonto2_tage: parseOptionalInt(event.target.value) }))
                }
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="skonto2-prozent">Skonto 2 (%)</Label>
              <Input
                id="skonto2-prozent"
                type="number"
                min={0}
                max={100}
                step="0.01"
                value={form.skonto2_prozent ?? ''}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, skonto2_prozent: parseOptionalFloat(event.target.value) }))
                }
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="zahlungsart">Zahlungsart</Label>
              <NativeSelect
                id="zahlungsart"
                ariaLabel="Zahlungsart"
                value={form.zahlungsart ?? 'ueberweisung'}
                onValueChange={(value) => setForm((prev) => ({ ...prev, zahlungsart: value }))}
                options={ZAHLUNGSARTEN.map((option) => ({ value: option.value, label: option.label }))}
              />
            </div>
            <div className="flex items-end gap-2 pb-2">
              <Checkbox
                id="manuelles-datum"
                checked={form.manuelles_datum ?? false}
                onCheckedChange={(checked) =>
                  setForm((prev) => ({ ...prev, manuelles_datum: checked === true }))
                }
              />
              <Label htmlFor="manuelles-datum">Manuelles Faelligkeitsdatum</Label>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              type="button"
              onClick={() => void submitForm()}
              disabled={!canSubmit || isSaving}
              aria-label="Zahlungsbedingung speichern"
            >
              <Save className="mr-2 h-4 w-4" aria-hidden="true" />
              Speichern
            </Button>
            {isEditing && (
              <Button type="button" variant="outline" onClick={resetForm} aria-label="Bearbeitung abbrechen">
                <X className="mr-2 h-4 w-4" aria-hidden="true" />
                Abbrechen
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
            <Input
              placeholder="ZABD-Nr. oder Bezeichnung..."
              aria-label="Zahlungsbedingungen durchsuchen"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {list.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Zahlungsbedingungen vorhanden.</p>
          ) : (
            <DataTable data={list} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
