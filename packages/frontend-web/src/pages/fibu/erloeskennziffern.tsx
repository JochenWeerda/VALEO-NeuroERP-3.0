import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  useCreateErloeskennziffer,
  useDeleteErloeskennziffer,
  useErloeskennziffern,
  useUpdateErloeskennziffer,
  type Erloeskennziffer,
  type ErloeskennzifferCreate,
} from '@/lib/api/fibu'
import { Edit3, Hash, Plus, Save, Search, Trash2, X } from 'lucide-react'

const emptyForm: ErloeskennzifferCreate = {
  ekz_nr: '',
  bezeichnung: '',
}

export default function ErloeskennziffernPage(): JSX.Element {
  const { data: items, isLoading, isError, error, refetch } = useErloeskennziffern()
  const createMutation = useCreateErloeskennziffer()
  const updateMutation = useUpdateErloeskennziffer()
  const deleteMutation = useDeleteErloeskennziffer()
  const [searchTerm, setSearchTerm] = useState('')
  const [editingNr, setEditingNr] = useState<string | null>(null)
  const [deletingNr, setDeletingNr] = useState<string | null>(null)
  const [form, setForm] = useState<ErloeskennzifferCreate>(emptyForm)

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
          <AlertTitle>Erlöskennziffern konnten nicht geladen werden</AlertTitle>
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
    return row.ekz_nr.toLowerCase().includes(query) || row.bezeichnung.toLowerCase().includes(query)
  })
  const isEditing = editingNr !== null
  const isSaving = createMutation.isPending || updateMutation.isPending
  const canSubmit = form.ekz_nr.trim() !== '' && form.bezeichnung.trim() !== ''

  function resetForm(): void {
    setEditingNr(null)
    setForm(emptyForm)
  }

  function startEdit(item: Erloeskennziffer): void {
    setEditingNr(item.ekz_nr)
    setForm({
      ekz_nr: item.ekz_nr,
      bezeichnung: item.bezeichnung,
    })
  }

  async function submitForm(): Promise<void> {
    if (!canSubmit || isSaving) return
    const payload = {
      ekz_nr: form.ekz_nr.trim(),
      bezeichnung: form.bezeichnung.trim(),
    }
    try {
      if (isEditing) {
        await updateMutation.mutateAsync({ ekz_nr: editingNr, payload })
        toast.success('Erlöskennziffer aktualisiert')
      } else {
        await createMutation.mutateAsync(payload)
        toast.success('Erlöskennziffer angelegt')
      }
      resetForm()
    } catch {
      toast.error('Speichern fehlgeschlagen')
    }
  }

  async function handleDelete(ekz_nr: string): Promise<void> {
    if (deleteMutation.isPending) return
    setDeletingNr(ekz_nr)
    try {
      await deleteMutation.mutateAsync(ekz_nr)
      toast.success('Erlöskennziffer deaktiviert')
      if (editingNr === ekz_nr) resetForm()
    } catch {
      toast.error('Loeschen fehlgeschlagen')
    } finally {
      setDeletingNr(null)
    }
  }

  const columns = [
    {
      key: 'ekz_nr' as const,
      label: 'EKZ-Nr.',
      render: (row: Erloeskennziffer) => (
        <button
          type="button"
          onClick={() => startEdit(row)}
          className="font-medium text-primary hover:underline"
        >
          {row.ekz_nr}
        </button>
      ),
    },
    { key: 'bezeichnung' as const, label: 'Bezeichnung' },
    {
      key: 'actions',
      label: '',
      render: (row: Erloeskennziffer) => (
        <div className="flex justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => startEdit(row)}
            aria-label={`${row.ekz_nr} bearbeiten`}
          >
            <Edit3 className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={deletingNr === row.ekz_nr}
            onClick={() => void handleDelete(row.ekz_nr)}
            aria-label={`${row.ekz_nr} deaktivieren`}
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
          <h1 className="text-3xl font-bold">Erlöskennziffern</h1>
          <p className="text-muted-foreground">Stammdaten — WaWi→FIBU Kontozuordnung (Wave 10)</p>
        </div>
        <Button type="button" onClick={resetForm} className="gap-2">
          <Plus className="h-4 w-4" aria-hidden="true" />
          Neue Erlöskennziffer
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Erlöskennziffern gesamt</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Hash className="h-5 w-5 text-primary" aria-hidden="true" />
            <span className="text-2xl font-bold tabular-nums">{rows.length}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{isEditing ? `Erlöskennziffer ${editingNr} bearbeiten` : 'Neue Erlöskennziffer'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-[180px_1fr_auto]">
            <Input
              placeholder="EKZ-Nr."
              aria-label="EKZ-Nummer"
              value={form.ekz_nr}
              onChange={(event) => setForm((prev) => ({ ...prev, ekz_nr: event.target.value }))}
              disabled={isEditing}
            />
            <Input
              placeholder="Bezeichnung"
              aria-label="Bezeichnung"
              value={form.bezeichnung}
              onChange={(event) => setForm((prev) => ({ ...prev, bezeichnung: event.target.value }))}
            />
            <div className="flex gap-2">
              <Button
                type="button"
                onClick={() => void submitForm()}
                disabled={!canSubmit || isSaving}
                aria-label="Erlöskennziffer speichern"
              >
                <Save className="h-4 w-4" aria-hidden="true" />
              </Button>
              {isEditing && (
                <Button type="button" variant="outline" onClick={resetForm} aria-label="Bearbeitung abbrechen">
                  <X className="h-4 w-4" aria-hidden="true" />
                </Button>
              )}
            </div>
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
              placeholder="EKZ-Nr. oder Bezeichnung..."
              aria-label="Erlöskennziffern durchsuchen"
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
            <p className="text-sm text-muted-foreground">Keine Erlöskennziffern vorhanden.</p>
          ) : (
            <DataTable data={list} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
