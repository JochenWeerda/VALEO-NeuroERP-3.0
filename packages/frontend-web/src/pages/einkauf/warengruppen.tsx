import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Edit3, Layers, Plus, Save, Search, Trash2, X } from 'lucide-react'
import {
  useCreateWarengruppe,
  useDeleteWarengruppe,
  useUpdateWarengruppe,
  useWarengruppen,
  type Warengruppe,
  type WarengruppeCreate,
} from '@/lib/api/einkauf'

const emptyForm: WarengruppeCreate = {
  gruppe_nr: '',
  bezeichnung: '',
  ober_id: '',
}

export default function WarengruppenPage(): JSX.Element {
  const { data: items, isLoading } = useWarengruppen()
  const createWarengruppe = useCreateWarengruppe()
  const updateWarengruppe = useUpdateWarengruppe()
  const deleteWarengruppe = useDeleteWarengruppe()
  const [searchTerm, setSearchTerm] = useState('')
  const [editingNr, setEditingNr] = useState<string | null>(null)
  const [form, setForm] = useState<WarengruppeCreate>(emptyForm)

  if (isLoading) return (
    <div className="p-3 md:p-6 space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-[400px] w-full" />
    </div>
  )

  const rows = items ?? []
  const list = rows.filter((w) => {
    const query = searchTerm.trim().toLowerCase()
    if (!query) return true
    return w.gruppe_nr.toLowerCase().includes(query) || w.bezeichnung.toLowerCase().includes(query)
  })
  const isEditing = editingNr !== null
  const isSaving = createWarengruppe.isPending || updateWarengruppe.isPending
  const canSubmit = form.gruppe_nr.trim() !== '' && form.bezeichnung.trim() !== '' && form.ober_id.trim() !== ''

  function resetForm(): void {
    setEditingNr(null)
    setForm(emptyForm)
  }

  function startEdit(item: Warengruppe): void {
    setEditingNr(item.gruppe_nr)
    setForm({
      gruppe_nr: item.gruppe_nr,
      bezeichnung: item.bezeichnung,
      ober_id: item.ober_id,
    })
  }

  async function submitForm(): Promise<void> {
    if (!canSubmit) return
    const payload = {
      gruppe_nr: form.gruppe_nr.trim(),
      bezeichnung: form.bezeichnung.trim(),
      ober_id: form.ober_id.trim(),
    }
    if (isEditing) {
      await updateWarengruppe.mutateAsync({ gruppe_nr: editingNr, payload })
    } else {
      await createWarengruppe.mutateAsync(payload)
    }
    resetForm()
  }

  const columns = [
    {
      key: 'gruppe_nr' as const,
      label: 'Nummer',
      render: (w: Warengruppe) => (
        <button
          type="button"
          onClick={() => startEdit(w)}
          className="font-medium text-blue-600 hover:underline"
        >
          {w.gruppe_nr}
        </button>
      ),
    },
    { key: 'bezeichnung' as const, label: 'Bezeichnung' },
    { key: 'ober_id' as const, label: 'Oberwarengruppe-ID', render: (w: Warengruppe) => w.ober_id || '-' },
    {
      key: 'actions',
      label: '',
      render: (w: Warengruppe) => (
        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" size="sm" onClick={() => startEdit(w)} aria-label={`${w.gruppe_nr} bearbeiten`}>
            <Edit3 className="h-4 w-4" />
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => deleteWarengruppe.mutate(w.gruppe_nr)}
            aria-label={`${w.gruppe_nr} deaktivieren`}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Warengruppen</h1>
          <p className="text-muted-foreground">Stammdaten - 3-stufige Warengruppenhierarchie</p>
        </div>
        <Button type="button" onClick={resetForm} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Warengruppe
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Warengruppen gesamt</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-blue-600" />
            <span className="text-2xl font-bold">{rows.length}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{isEditing ? `Warengruppe ${editingNr} bearbeiten` : 'Neue Warengruppe'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-[180px_1fr_1fr_auto]">
            <Input
              placeholder="Nummer"
              value={form.gruppe_nr}
              onChange={(event) => setForm((prev) => ({ ...prev, gruppe_nr: event.target.value }))}
              disabled={isEditing}
            />
            <Input
              placeholder="Bezeichnung"
              value={form.bezeichnung}
              onChange={(event) => setForm((prev) => ({ ...prev, bezeichnung: event.target.value }))}
            />
            <Input
              placeholder="Oberwarengruppe-ID"
              value={form.ober_id}
              onChange={(event) => setForm((prev) => ({ ...prev, ober_id: event.target.value }))}
            />
            <div className="flex gap-2">
              <Button type="button" onClick={() => void submitForm()} disabled={!canSubmit || isSaving} aria-label="Warengruppe speichern">
                <Save className="h-4 w-4" />
              </Button>
              {isEditing && (
                <Button type="button" variant="outline" onClick={resetForm} aria-label="Bearbeitung abbrechen">
                  <X className="h-4 w-4" />
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
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Nummer oder Bezeichnung..."
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={list} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
