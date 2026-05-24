import { useMemo, useState } from 'react'
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
  PERIODISCHE_TURNUS,
  PERIODISCHE_VORGANGSKLASSEN,
  useCreatePeriodischeBuchung,
  useDeletePeriodischeBuchung,
  useFaelligePeriodischeBuchungen,
  usePeriodischeBuchungen,
  useSperrenPeriodischeBuchung,
  type PeriodischeBuchung,
  type PeriodischeBuchungCreate,
} from '@/lib/api/fibu'
import { CalendarClock, Lock, Plus, Save, Search, Trash2 } from 'lucide-react'

const emptyForm: PeriodischeBuchungCreate = {
  bezeichnung: '',
  vorgangsklasse: 'ZA',
  konto: '',
  gegenkonto: '',
  buchungstext: null,
  betrag: 0,
  turnus: 'monatlich',
  gueltig_ab: new Date().toISOString().slice(0, 10),
  gueltig_bis: null,
  gesperrt: false,
  kostenstelle: null,
}

function optionalText(value: string): string | null {
  const trimmed = value.trim()
  return trimmed === '' ? null : trimmed
}

export default function PeriodischeBuchungenPage(): JSX.Element {
  const [filterTurnus, setFilterTurnus] = useState('')
  const [filterGesperrt, setFilterGesperrt] = useState<'all' | 'true' | 'false'>('all')
  const listFilters = useMemo(
    () => ({
      turnus: filterTurnus || undefined,
      gesperrt: filterGesperrt === 'all' ? undefined : filterGesperrt === 'true',
    }),
    [filterTurnus, filterGesperrt],
  )
  const [stichtag, setStichtag] = useState(new Date().toISOString().slice(0, 10))
  const { data: items, isLoading, isError, error, refetch } = usePeriodischeBuchungen(listFilters)
  const { data: faellige, isLoading: faelligLoading } = useFaelligePeriodischeBuchungen(stichtag)
  const createMutation = useCreatePeriodischeBuchung()
  const sperrenMutation = useSperrenPeriodischeBuchung()
  const deleteMutation = useDeletePeriodischeBuchung()
  const [searchTerm, setSearchTerm] = useState('')
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [sperrenId, setSperrenId] = useState<string | null>(null)
  const [form, setForm] = useState<PeriodischeBuchungCreate>(emptyForm)

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
          <AlertTitle>Periodische Buchungen konnten nicht geladen werden</AlertTitle>
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
    return row.bezeichnung.toLowerCase().includes(query) || row.konto.includes(query)
  })
  const isSaving = createMutation.isPending
  const isMutating = sperrenMutation.isPending || deleteMutation.isPending
  const canSubmit =
    form.bezeichnung.trim() !== '' &&
    form.konto.trim() !== '' &&
    form.gegenkonto.trim() !== '' &&
    form.betrag > 0 &&
    form.gueltig_ab.trim() !== ''

  async function submitForm(): Promise<void> {
    if (!canSubmit || isSaving) return
    const payload: PeriodischeBuchungCreate = {
      bezeichnung: form.bezeichnung.trim(),
      vorgangsklasse: form.vorgangsklasse ?? 'ZA',
      konto: form.konto.trim(),
      gegenkonto: form.gegenkonto.trim(),
      buchungstext: optionalText(form.buchungstext ?? ''),
      betrag: form.betrag,
      turnus: form.turnus ?? 'monatlich',
      gueltig_ab: form.gueltig_ab,
      gueltig_bis: form.gueltig_bis?.trim() ? form.gueltig_bis : null,
      gesperrt: form.gesperrt ?? false,
      kostenstelle: optionalText(form.kostenstelle ?? ''),
    }
    try {
      await createMutation.mutateAsync(payload)
      toast.success('Periodische Buchung angelegt')
      setForm(emptyForm)
    } catch {
      toast.error('Speichern fehlgeschlagen')
    }
  }

  async function toggleSperren(row: PeriodischeBuchung): Promise<void> {
    if (isMutating) return
    setSperrenId(row.id)
    try {
      await sperrenMutation.mutateAsync({ id: row.id, gesperrt: !row.gesperrt })
      toast.success(row.gesperrt ? 'Buchung entsperrt' : 'Buchung gesperrt')
    } catch {
      toast.error('Sperren fehlgeschlagen')
    } finally {
      setSperrenId(null)
    }
  }

  async function handleDelete(id: string): Promise<void> {
    if (isMutating) return
    setDeletingId(id)
    try {
      await deleteMutation.mutateAsync(id)
      toast.success('Periodische Buchung deaktiviert')
    } catch {
      toast.error('Loeschen fehlgeschlagen')
    } finally {
      setDeletingId(null)
    }
  }

  const columns = [
    { key: 'bezeichnung' as const, label: 'Bezeichnung' },
    { key: 'vorgangsklasse' as const, label: 'VK' },
    { key: 'konto' as const, label: 'Konto' },
    { key: 'gegenkonto' as const, label: 'Gegenkonto' },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (r: PeriodischeBuchung) => Number(r.betrag).toFixed(2),
    },
    { key: 'turnus' as const, label: 'Turnus' },
    {
      key: 'gesperrt' as const,
      label: 'Gesperrt',
      render: (r: PeriodischeBuchung) => (r.gesperrt ? 'Ja' : 'Nein'),
    },
    {
      key: 'actions',
      label: '',
      render: (row: PeriodischeBuchung) => (
        <div className="flex justify-end gap-1">
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={isMutating && sperrenId === row.id}
            onClick={() => void toggleSperren(row)}
            aria-label={`${row.bezeichnung} ${row.gesperrt ? 'entsperren' : 'sperren'}`}
          >
            <Lock className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={isMutating && deletingId === row.id}
            onClick={() => void handleDelete(row.id)}
            aria-label={`${row.bezeichnung} deaktivieren`}
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      ),
    },
  ]

  const faelligColumns = [
    { key: 'bezeichnung' as const, label: 'Bezeichnung' },
    { key: 'konto' as const, label: 'Konto' },
    { key: 'gegenkonto' as const, label: 'Gegenkonto' },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (r: { betrag: string }) => Number(r.betrag).toFixed(2),
    },
    { key: 'turnus' as const, label: 'Turnus' },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Periodische Buchungen</h1>
        <p className="text-muted-foreground">WZA — Wiederkehrende FIBU-Buchungen (Wave 11)</p>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Stammdaten gesamt</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <CalendarClock className="h-5 w-5 text-primary" aria-hidden="true" />
            <span className="text-2xl font-bold tabular-nums">{rows.length}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Neue periodische Buchung</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1 md:col-span-2">
              <Label htmlFor="wza-bez">Bezeichnung</Label>
              <Input
                id="wza-bez"
                value={form.bezeichnung}
                onChange={(e) => setForm((p) => ({ ...p, bezeichnung: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="wza-vk">Vorgangsklasse</Label>
              <NativeSelect
                id="wza-vk"
                ariaLabel="Vorgangsklasse"
                value={form.vorgangsklasse ?? 'ZA'}
                onValueChange={(v) => setForm((p) => ({ ...p, vorgangsklasse: v }))}
                options={PERIODISCHE_VORGANGSKLASSEN.map((v) => ({ value: v, label: v }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="wza-turnus">Turnus</Label>
              <NativeSelect
                id="wza-turnus"
                ariaLabel="Turnus"
                value={form.turnus ?? 'monatlich'}
                onValueChange={(v) => setForm((p) => ({ ...p, turnus: v }))}
                options={PERIODISCHE_TURNUS.map((t) => ({ value: t, label: t }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="wza-konto">Konto</Label>
              <Input id="wza-konto" value={form.konto} onChange={(e) => setForm((p) => ({ ...p, konto: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="wza-gkonto">Gegenkonto</Label>
              <Input
                id="wza-gkonto"
                value={form.gegenkonto}
                onChange={(e) => setForm((p) => ({ ...p, gegenkonto: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="wza-betrag">Betrag</Label>
              <Input
                id="wza-betrag"
                type="number"
                min="0.01"
                step="0.01"
                value={form.betrag || ''}
                onChange={(e) => setForm((p) => ({ ...p, betrag: Number.parseFloat(e.target.value) || 0 }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="wza-gab">Gueltig ab</Label>
              <Input
                id="wza-gab"
                type="date"
                value={form.gueltig_ab}
                onChange={(e) => setForm((p) => ({ ...p, gueltig_ab: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="wza-gbis">Gueltig bis</Label>
              <Input
                id="wza-gbis"
                type="date"
                value={form.gueltig_bis ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, gueltig_bis: e.target.value }))}
              />
            </div>
            <div className="space-y-1 md:col-span-2">
              <Label htmlFor="wza-text">Buchungstext</Label>
              <Input
                id="wza-text"
                value={form.buchungstext ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, buchungstext: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="wza-kst">Kostenstelle</Label>
              <Input
                id="wza-kst"
                value={form.kostenstelle ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, kostenstelle: e.target.value }))}
              />
            </div>
            <div className="flex items-center gap-2 pt-6">
              <Checkbox
                id="wza-gesperrt"
                checked={form.gesperrt ?? false}
                onCheckedChange={(v) => setForm((p) => ({ ...p, gesperrt: v === true }))}
              />
              <Label htmlFor="wza-gesperrt">Gesperrt</Label>
            </div>
          </div>
          <Button type="button" disabled={!canSubmit || isSaving} onClick={() => void submitForm()}>
            <Save className="mr-2 h-4 w-4" aria-hidden="true" />
            Speichern
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Faellige Buchungen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-end gap-3">
            <div className="space-y-1">
              <Label htmlFor="wza-stichtag">Stichtag</Label>
              <Input id="wza-stichtag" type="date" value={stichtag} onChange={(e) => setStichtag(e.target.value)} />
            </div>
          </div>
          {faelligLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : (faellige ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine faelligen Buchungen zum Stichtag.</p>
          ) : (
            <DataTable data={faellige ?? []} columns={faelligColumns} />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Filter</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          <NativeSelect
            ariaLabel="Turnus filtern"
            value={filterTurnus}
            onValueChange={setFilterTurnus}
            placeholder="Alle Turnus"
            options={[{ value: '', label: 'Alle Turnus' }, ...PERIODISCHE_TURNUS.map((t) => ({ value: t, label: t }))]}
          />
          <NativeSelect
            ariaLabel="Sperrstatus filtern"
            value={filterGesperrt}
            onValueChange={(v) => setFilterGesperrt(v as 'all' | 'true' | 'false')}
            options={[
              { value: 'all', label: 'Alle' },
              { value: 'false', label: 'Nicht gesperrt' },
              { value: 'true', label: 'Gesperrt' },
            ]}
          />
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
            <Input
              placeholder="Bezeichnung oder Konto..."
              aria-label="Periodische Buchungen suchen"
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
            <p className="text-sm text-muted-foreground">Keine periodischen Buchungen vorhanden.</p>
          ) : (
            <DataTable data={list} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
