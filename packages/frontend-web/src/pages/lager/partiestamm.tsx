import { useMemo, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  PARTIE_STATUS,
  PARTIE_TYPEN,
  useCreatePartie,
  useCreatePartiegruppe,
  useDeletePartie,
  useDeletePartiegruppe,
  usePartiegruppen,
  usePartien,
  useSetPartieStatus,
  type Partiegruppe,
  type Partiestamm,
  type PartiestammCreate,
} from '@/lib/api/lager'
import { Boxes, Plus, Save, Search, Trash2 } from 'lucide-react'

const emptyPartieForm: PartiestammCreate = {
  partie_nr: '',
  bezeichnung: '',
  artikel_nr: '',
  lager_nr: '',
  partie_typ: 'artikelstamm',
  gruppe_id: '',
  erntejahr: null,
  herkunftsland: '',
}

function optionalText(value: string): string | null {
  const trimmed = value.trim()
  return trimmed === '' ? null : trimmed
}

function parseOptionalInt(value: string): number | null {
  const trimmed = value.trim()
  if (trimmed === '') return null
  const parsed = Number.parseInt(trimmed, 10)
  return Number.isNaN(parsed) ? null : parsed
}

export default function PartiestammPage(): JSX.Element {
  const [filterArtikel, setFilterArtikel] = useState('')
  const [filterLager, setFilterLager] = useState('')
  const [filterGruppeId, setFilterGruppeId] = useState('')
  const [filterErntejahr, setFilterErntejahr] = useState('')
  const listFilters = useMemo(
    () => ({
      artikel_nr: filterArtikel.trim() || undefined,
      lager_nr: filterLager.trim() || undefined,
      gruppe_id: filterGruppeId || undefined,
      erntejahr: parseOptionalInt(filterErntejahr) ?? undefined,
    }),
    [filterArtikel, filterLager, filterGruppeId, filterErntejahr],
  )

  const { data: partien, isLoading, isError, error, refetch } = usePartien(listFilters)
  const { data: gruppen } = usePartiegruppen()
  const createPartieMutation = useCreatePartie()
  const statusMutation = useSetPartieStatus()
  const deletePartieMutation = useDeletePartie()
  const createGruppeMutation = useCreatePartiegruppe()
  const deleteGruppeMutation = useDeletePartiegruppe()

  const [searchTerm, setSearchTerm] = useState('')
  const [partieForm, setPartieForm] = useState<PartiestammCreate>(emptyPartieForm)
  const [gruppeNr, setGruppeNr] = useState('')
  const [gruppeBez, setGruppeBez] = useState('')
  const [statusPending, setStatusPending] = useState<string | null>(null)
  const [deletePending, setDeletePending] = useState<string | null>(null)
  const [deleteGruppePending, setDeleteGruppePending] = useState<string | null>(null)

  const gruppeById = useMemo(() => {
    const map = new Map<string, string>()
    for (const g of gruppen ?? []) {
      map.set(g.id, g.gruppe_nr)
    }
    return map
  }, [gruppen])

  const gruppeOptions = useMemo(
    () => (gruppen ?? []).map((g) => ({ value: g.id, label: `${g.gruppe_nr} — ${g.bezeichnung}` })),
    [gruppen],
  )

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
          <AlertTitle>Partiestamm konnte nicht geladen werden</AlertTitle>
          <AlertDescription>{error instanceof Error ? error.message : 'Unbekannter Fehler'}</AlertDescription>
        </Alert>
        <Button type="button" onClick={() => void refetch()}>
          Erneut laden
        </Button>
      </div>
    )
  }

  const rows = partien ?? []
  const list = rows.filter((row) => {
    const query = searchTerm.trim().toLowerCase()
    if (!query) return true
    return (
      row.partie_nr.toLowerCase().includes(query) ||
      row.artikel_nr.toLowerCase().includes(query) ||
      (row.bezeichnung ?? '').toLowerCase().includes(query)
    )
  })

  const isSavingPartie = createPartieMutation.isPending
  const isMutating = statusMutation.isPending || deletePartieMutation.isPending || deleteGruppeMutation.isPending
  const lagerRequired = partieForm.partie_typ === 'artikel_lager'
  const canSubmitPartie =
    partieForm.artikel_nr.trim() !== '' && (!lagerRequired || (partieForm.lager_nr ?? '').trim() !== '')

  async function submitPartie(): Promise<void> {
    if (!canSubmitPartie || isSavingPartie) return
    const payload: PartiestammCreate = {
      partie_nr: optionalText(partieForm.partie_nr ?? ''),
      bezeichnung: optionalText(partieForm.bezeichnung ?? ''),
      artikel_nr: partieForm.artikel_nr.trim(),
      lager_nr: lagerRequired ? partieForm.lager_nr?.trim() : optionalText(partieForm.lager_nr ?? ''),
      partie_typ: partieForm.partie_typ ?? 'artikelstamm',
      gruppe_id: partieForm.gruppe_id?.trim() ? partieForm.gruppe_id : null,
      erntejahr: partieForm.erntejahr,
      herkunftsland: optionalText(partieForm.herkunftsland ?? ''),
    }
    try {
      await createPartieMutation.mutateAsync(payload)
      toast.success('Partie angelegt')
      setPartieForm(emptyPartieForm)
    } catch {
      toast.error('Partie speichern fehlgeschlagen')
    }
  }

  async function changeStatus(partie_nr: string, status: string): Promise<void> {
    if (isMutating) return
    setStatusPending(partie_nr)
    try {
      await statusMutation.mutateAsync({ partie_nr, status })
      toast.success('Partie-Status aktualisiert')
    } catch {
      toast.error('Status-Aenderung fehlgeschlagen')
    } finally {
      setStatusPending(null)
    }
  }

  async function removePartie(partie_nr: string): Promise<void> {
    if (isMutating) return
    setDeletePending(partie_nr)
    try {
      await deletePartieMutation.mutateAsync(partie_nr)
      toast.success('Partie deaktiviert')
    } catch {
      toast.error('Loeschen fehlgeschlagen')
    } finally {
      setDeletePending(null)
    }
  }

  async function submitGruppe(): Promise<void> {
    if (!gruppeNr.trim() || !gruppeBez.trim() || createGruppeMutation.isPending) return
    try {
      await createGruppeMutation.mutateAsync({ gruppe_nr: gruppeNr.trim(), bezeichnung: gruppeBez.trim() })
      toast.success('Partiegruppe angelegt')
      setGruppeNr('')
      setGruppeBez('')
    } catch {
      toast.error('Partiegruppe speichern fehlgeschlagen')
    }
  }

  async function removeGruppe(nr: string): Promise<void> {
    if (isMutating) return
    setDeleteGruppePending(nr)
    try {
      await deleteGruppeMutation.mutateAsync(nr)
      toast.success('Partiegruppe deaktiviert')
    } catch {
      toast.error('Loeschen fehlgeschlagen')
    } finally {
      setDeleteGruppePending(null)
    }
  }

  const partieColumns = [
    { key: 'partie_nr' as const, label: 'Partie-Nr.' },
    { key: 'artikel_nr' as const, label: 'Artikel' },
    {
      key: 'bezeichnung' as const,
      label: 'Bezeichnung',
      render: (r: Partiestamm) => r.bezeichnung ?? '-',
    },
    { key: 'partie_typ' as const, label: 'Typ' },
    { key: 'status' as const, label: 'Status' },
    {
      key: 'gruppe_id' as const,
      label: 'Gruppe',
      render: (r: Partiestamm) => (r.gruppe_id ? gruppeById.get(r.gruppe_id) ?? r.gruppe_id.slice(0, 8) : '-'),
    },
    { key: 'erntejahr' as const, label: 'Erntejahr', render: (r: Partiestamm) => r.erntejahr ?? '-' },
    {
      key: 'actions',
      label: '',
      render: (row: Partiestamm) => (
        <div className="flex justify-end gap-1">
          <NativeSelect
            ariaLabel={`Status fuer ${row.partie_nr}`}
            value={row.status}
            disabled={isMutating && statusPending === row.partie_nr}
            onValueChange={(value) => void changeStatus(row.partie_nr, value)}
            options={PARTIE_STATUS.map((s) => ({ value: s, label: s }))}
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={isMutating && deletePending === row.partie_nr}
            onClick={() => void removePartie(row.partie_nr)}
            aria-label={`${row.partie_nr} deaktivieren`}
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      ),
    },
  ]

  const gruppeColumns = [
    { key: 'gruppe_nr' as const, label: 'Gruppe-Nr.' },
    { key: 'bezeichnung' as const, label: 'Bezeichnung' },
    {
      key: 'actions',
      label: '',
      render: (row: Partiegruppe) => (
        <div className="flex justify-end">
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={isMutating && deleteGruppePending === row.gruppe_nr}
            onClick={() => void removeGruppe(row.gruppe_nr)}
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
      <div>
        <h1 className="text-3xl font-bold">Partiestamm</h1>
        <p className="text-muted-foreground">PAR/PGR — Chargen-/Lot-Verwaltung (Wave 11)</p>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Partien gesamt</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Boxes className="h-5 w-5 text-primary" aria-hidden="true" />
            <span className="text-2xl font-bold tabular-nums">{rows.length}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Neue Partie</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1">
              <Label htmlFor="par-nr">Partie-Nr. (optional)</Label>
              <Input
                id="par-nr"
                value={partieForm.partie_nr ?? ''}
                onChange={(e) => setPartieForm((p) => ({ ...p, partie_nr: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="par-artikel">Artikel-Nr.</Label>
              <Input
                id="par-artikel"
                value={partieForm.artikel_nr}
                onChange={(e) => setPartieForm((p) => ({ ...p, artikel_nr: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="par-typ">Partie-Typ</Label>
              <NativeSelect
                id="par-typ"
                ariaLabel="Partie-Typ"
                value={partieForm.partie_typ ?? 'artikelstamm'}
                onValueChange={(v) => setPartieForm((p) => ({ ...p, partie_typ: v }))}
                options={PARTIE_TYPEN.map((t) => ({ value: t, label: t }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="par-lager">Lager-Nr.</Label>
              <Input
                id="par-lager"
                value={partieForm.lager_nr ?? ''}
                onChange={(e) => setPartieForm((p) => ({ ...p, lager_nr: e.target.value }))}
              />
            </div>
            <div className="space-y-1 md:col-span-2">
              <Label htmlFor="par-bez">Bezeichnung</Label>
              <Input
                id="par-bez"
                value={partieForm.bezeichnung ?? ''}
                onChange={(e) => setPartieForm((p) => ({ ...p, bezeichnung: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="par-gruppe">Partiegruppe</Label>
              <NativeSelect
                id="par-gruppe"
                ariaLabel="Partiegruppe"
                value={partieForm.gruppe_id ?? ''}
                onValueChange={(v) => setPartieForm((p) => ({ ...p, gruppe_id: v }))}
                placeholder="Keine Gruppe"
                options={[{ value: '', label: 'Keine Gruppe' }, ...gruppeOptions]}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="par-erntejahr">Erntejahr</Label>
              <Input
                id="par-erntejahr"
                type="number"
                value={partieForm.erntejahr ?? ''}
                onChange={(e) => setPartieForm((p) => ({ ...p, erntejahr: parseOptionalInt(e.target.value) }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="par-land">Herkunftsland</Label>
              <Input
                id="par-land"
                maxLength={3}
                value={partieForm.herkunftsland ?? ''}
                onChange={(e) => setPartieForm((p) => ({ ...p, herkunftsland: e.target.value }))}
              />
            </div>
          </div>
          <Button type="button" disabled={!canSubmitPartie || isSavingPartie} onClick={() => void submitPartie()}>
            <Save className="mr-2 h-4 w-4" aria-hidden="true" />
            Partie speichern
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Partiegruppen (PGR)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <div className="space-y-1">
              <Label htmlFor="pgr-nr">Gruppe-Nr.</Label>
              <Input id="pgr-nr" value={gruppeNr} onChange={(e) => setGruppeNr(e.target.value)} />
            </div>
            <div className="space-y-1 md:col-span-2">
              <Label htmlFor="pgr-bez">Bezeichnung</Label>
              <Input id="pgr-bez" value={gruppeBez} onChange={(e) => setGruppeBez(e.target.value)} />
            </div>
          </div>
          <Button type="button" className="gap-2" onClick={() => void submitGruppe()}>
            <Plus className="h-4 w-4" aria-hidden="true" />
            Gruppe anlegen
          </Button>
          {(gruppen ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Partiegruppen vorhanden.</p>
          ) : (
            <DataTable data={gruppen ?? []} columns={gruppeColumns} />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Filter</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Input
            placeholder="Artikel-Nr."
            aria-label="Artikel filtern"
            value={filterArtikel}
            onChange={(e) => setFilterArtikel(e.target.value)}
          />
          <Input
            placeholder="Lager-Nr."
            aria-label="Lager filtern"
            value={filterLager}
            onChange={(e) => setFilterLager(e.target.value)}
          />
          <NativeSelect
            ariaLabel="Partiegruppe filtern"
            value={filterGruppeId}
            onValueChange={setFilterGruppeId}
            placeholder="Alle Gruppen"
            options={[{ value: '', label: 'Alle Gruppen' }, ...gruppeOptions]}
          />
          <Input
            placeholder="Erntejahr"
            aria-label="Erntejahr filtern"
            value={filterErntejahr}
            onChange={(e) => setFilterErntejahr(e.target.value)}
          />
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
              placeholder="Partie-Nr., Artikel oder Bezeichnung..."
              aria-label="Partien suchen"
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
            <p className="text-sm text-muted-foreground">Keine Partien vorhanden.</p>
          ) : (
            <DataTable data={list} columns={partieColumns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
