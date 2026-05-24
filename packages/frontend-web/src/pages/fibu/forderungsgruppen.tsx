import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  useCreateForderungsgruppe,
  useDeleteForderungsgruppe,
  useForderungsgruppen,
  useUpdateForderungsgruppe,
  type Forderungsgruppe,
  type ForderungsgruppeCreate,
} from '@/lib/api/fibu'
import { Edit3, Plus, Save, Search, Trash2, Users, X } from 'lucide-react'

const emptyForm: ForderungsgruppeCreate = {
  gruppe_nr: '',
  bezeichnung: '',
  konto_forderungen: null,
  konto_verbindlichkeiten: null,
  konto_sammel_1: null,
  konto_sammel_2: null,
  konto_sammel_3: null,
}

function optionalText(value: string): string | null {
  const trimmed = value.trim()
  return trimmed === '' ? null : trimmed
}

export default function ForderungsgruppenPage(): JSX.Element {
  const { data: items, isLoading, isError, error, refetch } = useForderungsgruppen()
  const createMutation = useCreateForderungsgruppe()
  const updateMutation = useUpdateForderungsgruppe()
  const deleteMutation = useDeleteForderungsgruppe()
  const [searchTerm, setSearchTerm] = useState('')
  const [editingNr, setEditingNr] = useState<string | null>(null)
  const [deletingNr, setDeletingNr] = useState<string | null>(null)
  const [form, setForm] = useState<ForderungsgruppeCreate>(emptyForm)

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
          <AlertTitle>Forderungsgruppen konnten nicht geladen werden</AlertTitle>
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
    return row.gruppe_nr.toLowerCase().includes(query) || row.bezeichnung.toLowerCase().includes(query)
  })
  const isEditing = editingNr !== null
  const isSaving = createMutation.isPending || updateMutation.isPending
  const isDeleting = deleteMutation.isPending
  const canSubmit = form.gruppe_nr.trim() !== '' && form.bezeichnung.trim() !== ''

  function resetForm(): void {
    setEditingNr(null)
    setForm(emptyForm)
  }

  function startEdit(item: Forderungsgruppe): void {
    setEditingNr(item.gruppe_nr)
    setForm({
      gruppe_nr: item.gruppe_nr,
      bezeichnung: item.bezeichnung,
      konto_forderungen: item.konto_forderungen,
      konto_verbindlichkeiten: item.konto_verbindlichkeiten,
      konto_sammel_1: item.konto_sammel_1,
      konto_sammel_2: item.konto_sammel_2,
      konto_sammel_3: item.konto_sammel_3,
    })
  }

  async function submitForm(): Promise<void> {
    if (!canSubmit || isSaving) return
    const payload: ForderungsgruppeCreate = {
      gruppe_nr: form.gruppe_nr.trim(),
      bezeichnung: form.bezeichnung.trim(),
      konto_forderungen: optionalText(form.konto_forderungen ?? ''),
      konto_verbindlichkeiten: optionalText(form.konto_verbindlichkeiten ?? ''),
      konto_sammel_1: optionalText(form.konto_sammel_1 ?? ''),
      konto_sammel_2: optionalText(form.konto_sammel_2 ?? ''),
      konto_sammel_3: optionalText(form.konto_sammel_3 ?? ''),
    }
    try {
      if (isEditing && editingNr) {
        await updateMutation.mutateAsync({ gruppe_nr: editingNr, payload })
        toast.success('Forderungsgruppe aktualisiert')
      } else {
        await createMutation.mutateAsync(payload)
        toast.success('Forderungsgruppe angelegt')
      }
      resetForm()
    } catch {
      toast.error('Speichern fehlgeschlagen')
    }
  }

  async function handleDelete(gruppe_nr: string): Promise<void> {
    if (isDeleting) return
    setDeletingNr(gruppe_nr)
    try {
      await deleteMutation.mutateAsync(gruppe_nr)
      toast.success('Forderungsgruppe deaktiviert')
      if (editingNr === gruppe_nr) resetForm()
    } catch {
      toast.error('Loeschen fehlgeschlagen')
    } finally {
      setDeletingNr(null)
    }
  }

  const columns = [
    { key: 'gruppe_nr' as const, label: 'Gruppe-Nr.' },
    { key: 'bezeichnung' as const, label: 'Bezeichnung' },
    {
      key: 'konto_forderungen' as const,
      label: 'Konto Forderungen',
      render: (r: Forderungsgruppe) => r.konto_forderungen ?? '-',
    },
    {
      key: 'konto_verbindlichkeiten' as const,
      label: 'Konto Verbindlichkeiten',
      render: (r: Forderungsgruppe) => r.konto_verbindlichkeiten ?? '-',
    },
    {
      key: 'actions',
      label: '',
      render: (row: Forderungsgruppe) => (
        <div className="flex justify-end gap-1">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => startEdit(row)}
            aria-label={`${row.gruppe_nr} bearbeiten`}
          >
            <Edit3 className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={isDeleting && deletingNr === row.gruppe_nr}
            onClick={() => void handleDelete(row.gruppe_nr)}
            aria-label={`${row.gruppe_nr} deaktivieren`}
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Forderungsgruppen</h1>
          <p className="text-muted-foreground">FORG — Kundensegmentierung fuer Bestandskontenzuordnung (Wave 11)</p>
        </div>
        <Button type="button" onClick={resetForm} className="gap-2">
          <Plus className="h-4 w-4" aria-hidden="true" />
          Neue Gruppe
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Gruppen gesamt</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" aria-hidden="true" />
            <span className="text-2xl font-bold tabular-nums">{rows.length}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{isEditing ? 'Gruppe bearbeiten' : 'Neue Forderungsgruppe'}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-1">
              <Label htmlFor="forg-nr">Gruppe-Nr.</Label>
              <Input
                id="forg-nr"
                value={form.gruppe_nr}
                disabled={isEditing}
                onChange={(e) => setForm((p) => ({ ...p, gruppe_nr: e.target.value }))}
              />
            </div>
            <div className="space-y-1 md:col-span-2">
              <Label htmlFor="forg-bez">Bezeichnung</Label>
              <Input
                id="forg-bez"
                value={form.bezeichnung}
                onChange={(e) => setForm((p) => ({ ...p, bezeichnung: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="forg-kf">Konto Forderungen</Label>
              <Input
                id="forg-kf"
                value={form.konto_forderungen ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, konto_forderungen: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="forg-kv">Konto Verbindlichkeiten</Label>
              <Input
                id="forg-kv"
                value={form.konto_verbindlichkeiten ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, konto_verbindlichkeiten: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="forg-ks1">Sammelkonto 1</Label>
              <Input
                id="forg-ks1"
                value={form.konto_sammel_1 ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, konto_sammel_1: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="forg-ks2">Sammelkonto 2</Label>
              <Input
                id="forg-ks2"
                value={form.konto_sammel_2 ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, konto_sammel_2: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="forg-ks3">Sammelkonto 3</Label>
              <Input
                id="forg-ks3"
                value={form.konto_sammel_3 ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, konto_sammel_3: e.target.value }))}
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button type="button" disabled={!canSubmit || isSaving} onClick={() => void submitForm()}>
              <Save className="mr-2 h-4 w-4" aria-hidden="true" />
              Speichern
            </Button>
            {isEditing && (
              <Button type="button" variant="outline" onClick={resetForm}>
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
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
            <Input
              placeholder="Gruppe-Nr. oder Bezeichnung..."
              aria-label="Forderungsgruppen suchen"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {list.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Forderungsgruppen vorhanden.</p>
          ) : (
            <DataTable data={list} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
