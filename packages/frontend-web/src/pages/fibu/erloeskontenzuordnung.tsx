import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
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
  useErloeskennziffern,
  useErloeskontenLookup,
  useErloeskontenzuordnungen,
  useUpsertErloeskontenzuordnung,
  type Erloeskontenzuordnung,
  type ErloeskontenzuordnungCreate,
  type ErloeskontenLookupResult,
} from '@/lib/api/fibu'
import { BookOpen, Edit3, Link2, Plus, Save, Search, X } from 'lucide-react'

const emptyForm: ErloeskontenzuordnungCreate = {
  ekz_id: '',
  gueltig_ab: new Date().toISOString().slice(0, 10),
  steuerschluessel: null,
  'erlösklasse': null,
  steuergruppe: null,
  buchungsklasse: null,
  konto_erloese: null,
  konto_aufwand: null,
  konto_umsatzsteuer: null,
  konto_vorsteuer: null,
}

function optionalText(value: string): string | null {
  const trimmed = value.trim()
  return trimmed === '' ? null : trimmed
}

export default function ErloeskontenzuordnungPage(): JSX.Element {
  const { data: ekzList, isLoading: ekzLoading } = useErloeskennziffern()
  const [filterEkzId, setFilterEkzId] = useState('')
  const [filterSteuerschluessel, setFilterSteuerschluessel] = useState('')
  const listFilters = useMemo(
    () => ({
      ekz_id: filterEkzId || undefined,
      steuerschluessel: filterSteuerschluessel.trim() || undefined,
    }),
    [filterEkzId, filterSteuerschluessel],
  )
  const { data: zuordnungen, isLoading, isError, error, refetch } = useErloeskontenzuordnungen(listFilters)
  const upsertMutation = useUpsertErloeskontenzuordnung()
  const lookupMutation = useErloeskontenLookup()

  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState<ErloeskontenzuordnungCreate>(emptyForm)
  const [lookupEkzNr, setLookupEkzNr] = useState('')
  const [lookupSteuerschluessel, setLookupSteuerschluessel] = useState('')
  const [lookupErloesklasse, setLookupErloesklasse] = useState('')
  const [lookupBuchungsklasse, setLookupBuchungsklasse] = useState('')
  const [lookupDatum, setLookupDatum] = useState(new Date().toISOString().slice(0, 10))
  const [lookupResult, setLookupResult] = useState<ErloeskontenLookupResult | null>(null)
  const [lookupError, setLookupError] = useState<string | null>(null)

  const ekzById = useMemo(() => {
    const map = new Map<string, string>()
    for (const ekz of ekzList ?? []) {
      map.set(ekz.id, ekz.ekz_nr)
    }
    return map
  }, [ekzList])

  const ekzOptions = useMemo(
    () => (ekzList ?? []).map((ekz) => ({ value: ekz.id, label: `${ekz.ekz_nr} — ${ekz.bezeichnung}` })),
    [ekzList],
  )

  const lookupEkzOptions = useMemo(
    () => (ekzList ?? []).map((ekz) => ({ value: ekz.ekz_nr, label: `${ekz.ekz_nr} — ${ekz.bezeichnung}` })),
    [ekzList],
  )

  if (isLoading || ekzLoading) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Skeleton className="h-8 w-72" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Alert variant="destructive">
          <AlertTitle>Erlöskontenzuordnungen konnten nicht geladen werden</AlertTitle>
          <AlertDescription>{error instanceof Error ? error.message : 'Unbekannter Fehler'}</AlertDescription>
        </Alert>
        <Button type="button" onClick={() => void refetch()}>
          Erneut laden
        </Button>
      </div>
    )
  }

  const rows = zuordnungen ?? []
  const isEditing = editingId !== null
  const isSaving = upsertMutation.isPending
  const canSubmit = form.ekz_id.trim() !== '' && form.gueltig_ab.trim() !== ''

  function resetForm(): void {
    setEditingId(null)
    setForm(emptyForm)
  }

  function startEdit(item: Erloeskontenzuordnung): void {
    setEditingId(item.id)
    setForm({
      ekz_id: item.ekz_id,
      gueltig_ab: item.gueltig_ab,
      steuerschluessel: item.steuerschluessel,
      'erlösklasse': item['erlösklasse'],
      steuergruppe: item.steuergruppe,
      buchungsklasse: item.buchungsklasse,
      konto_erloese: item.konto_erloese,
      konto_aufwand: item.konto_aufwand,
      konto_umsatzsteuer: item.konto_umsatzsteuer,
      konto_vorsteuer: item.konto_vorsteuer,
    })
  }

  async function submitForm(): Promise<void> {
    if (!canSubmit || isSaving) return
    const payload: ErloeskontenzuordnungCreate = {
      ekz_id: form.ekz_id.trim(),
      gueltig_ab: form.gueltig_ab,
      steuerschluessel: optionalText(form.steuerschluessel ?? ''),
      'erlösklasse': optionalText(form['erlösklasse'] ?? ''),
      steuergruppe: optionalText(form.steuergruppe ?? ''),
      buchungsklasse: optionalText(form.buchungsklasse ?? ''),
      konto_erloese: optionalText(form.konto_erloese ?? ''),
      konto_aufwand: optionalText(form.konto_aufwand ?? ''),
      konto_umsatzsteuer: optionalText(form.konto_umsatzsteuer ?? ''),
      konto_vorsteuer: optionalText(form.konto_vorsteuer ?? ''),
    }
    try {
      await upsertMutation.mutateAsync(payload)
      toast.success(isEditing ? 'Zuordnung aktualisiert' : 'Zuordnung angelegt')
      resetForm()
    } catch {
      toast.error('Speichern fehlgeschlagen')
    }
  }

  async function runLookup(): Promise<void> {
    if (!lookupEkzNr.trim() || lookupMutation.isPending) return
    setLookupResult(null)
    setLookupError(null)
    try {
      const result = await lookupMutation.mutateAsync({
        ekz_nr: lookupEkzNr.trim(),
        steuerschluessel: lookupSteuerschluessel.trim() || undefined,
        'erlösklasse': lookupErloesklasse.trim() || undefined,
        buchungsklasse: lookupBuchungsklasse.trim() || undefined,
        datum: lookupDatum || undefined,
      })
      setLookupResult(result)
      toast.success('Kontenlookup erfolgreich')
    } catch {
      setLookupError('Keine Zuordnung fuer diese Kombination gefunden.')
      toast.error('Lookup fehlgeschlagen')
    }
  }

  const columns = [
    {
      key: 'ekz_id' as const,
      label: 'EKZ',
      render: (row: Erloeskontenzuordnung) => ekzById.get(row.ekz_id) ?? row.ekz_id.slice(0, 8),
    },
    { key: 'gueltig_ab' as const, label: 'Gueltig ab' },
    { key: 'steuerschluessel' as const, label: 'Steuerschluessel', render: (r: Erloeskontenzuordnung) => r.steuerschluessel ?? '-' },
    {
      key: 'erlösklasse' as const,
      label: 'Erloesklasse',
      render: (r: Erloeskontenzuordnung) => r['erlösklasse'] ?? '-',
    },
    { key: 'konto_erloese' as const, label: 'Erloeskonto', render: (r: Erloeskontenzuordnung) => r.konto_erloese ?? '-' },
    { key: 'konto_aufwand' as const, label: 'Aufwandskonto', render: (r: Erloeskontenzuordnung) => r.konto_aufwand ?? '-' },
    {
      key: 'actions',
      label: '',
      render: (row: Erloeskontenzuordnung) => (
        <div className="flex justify-end">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => startEdit(row)}
            aria-label={`Zuordnung ${row.id} bearbeiten`}
          >
            <Edit3 className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Erlöskontenzuordnung</h1>
          <p className="text-muted-foreground">
            EKZZ — Kontenzuordnung und Lookup fuer Erlöskennziffern (Wave 10)
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            Stammdaten:{' '}
            <Link to="/fibu/erloeskennziffern" className="text-primary hover:underline">
              Erlöskennziffern
            </Link>
          </p>
        </div>
        <Button type="button" onClick={resetForm} className="gap-2">
          <Plus className="h-4 w-4" aria-hidden="true" />
          Neue Zuordnung
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Zuordnungen gesamt</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Link2 className="h-5 w-5 text-primary" aria-hidden="true" />
            <span className="text-2xl font-bold tabular-nums">{rows.length}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{isEditing ? 'Zuordnung bearbeiten (Upsert)' : 'Neue Zuordnung'}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1">
              <Label htmlFor="ekz-id">Erlöskennziffer</Label>
              <NativeSelect
                id="ekz-id"
                ariaLabel="Erlöskennziffer"
                value={form.ekz_id}
                onValueChange={(value) => setForm((prev) => ({ ...prev, ekz_id: value }))}
                placeholder="EKZ waehlen"
                options={ekzOptions}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="gueltig-ab">Gueltig ab</Label>
              <Input
                id="gueltig-ab"
                type="date"
                value={form.gueltig_ab}
                onChange={(event) => setForm((prev) => ({ ...prev, gueltig_ab: event.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="steuerschluessel">Steuerschluessel</Label>
              <Input
                id="steuerschluessel"
                value={form.steuerschluessel ?? ''}
                onChange={(event) => setForm((prev) => ({ ...prev, steuerschluessel: event.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="erloesklasse">Erloesklasse</Label>
              <Input
                id="erloesklasse"
                value={form['erlösklasse'] ?? ''}
                onChange={(event) => setForm((prev) => ({ ...prev, 'erlösklasse': event.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="steuergruppe">Steuergruppe</Label>
              <Input
                id="steuergruppe"
                value={form.steuergruppe ?? ''}
                onChange={(event) => setForm((prev) => ({ ...prev, steuergruppe: event.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="buchungsklasse">Buchungsklasse</Label>
              <Input
                id="buchungsklasse"
                value={form.buchungsklasse ?? ''}
                onChange={(event) => setForm((prev) => ({ ...prev, buchungsklasse: event.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="konto-erloese">Konto Erloese</Label>
              <Input
                id="konto-erloese"
                value={form.konto_erloese ?? ''}
                onChange={(event) => setForm((prev) => ({ ...prev, konto_erloese: event.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="konto-aufwand">Konto Aufwand</Label>
              <Input
                id="konto-aufwand"
                value={form.konto_aufwand ?? ''}
                onChange={(event) => setForm((prev) => ({ ...prev, konto_aufwand: event.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="konto-ust">Konto USt</Label>
              <Input
                id="konto-ust"
                value={form.konto_umsatzsteuer ?? ''}
                onChange={(event) => setForm((prev) => ({ ...prev, konto_umsatzsteuer: event.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="konto-vst">Konto VSt</Label>
              <Input
                id="konto-vst"
                value={form.konto_vorsteuer ?? ''}
                onChange={(event) => setForm((prev) => ({ ...prev, konto_vorsteuer: event.target.value }))}
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              type="button"
              onClick={() => void submitForm()}
              disabled={!canSubmit || isSaving}
              aria-label="Zuordnung speichern"
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
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" aria-hidden="true" />
            Konto-Lookup
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-5">
            <div className="space-y-1">
              <Label htmlFor="lookup-ekz">EKZ-Nr.</Label>
              <NativeSelect
                id="lookup-ekz"
                ariaLabel="EKZ-Nr. fuer Lookup"
                value={lookupEkzNr}
                onValueChange={setLookupEkzNr}
                placeholder="EKZ waehlen"
                options={lookupEkzOptions}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="lookup-sk">Steuerschluessel</Label>
              <Input
                id="lookup-sk"
                value={lookupSteuerschluessel}
                onChange={(event) => setLookupSteuerschluessel(event.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="lookup-ek">Erloesklasse</Label>
              <Input
                id="lookup-ek"
                value={lookupErloesklasse}
                onChange={(event) => setLookupErloesklasse(event.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="lookup-bk">Buchungsklasse</Label>
              <Input
                id="lookup-bk"
                value={lookupBuchungsklasse}
                onChange={(event) => setLookupBuchungsklasse(event.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="lookup-datum">Stichtag</Label>
              <Input
                id="lookup-datum"
                type="date"
                value={lookupDatum}
                onChange={(event) => setLookupDatum(event.target.value)}
              />
            </div>
          </div>
          <Button
            type="button"
            onClick={() => void runLookup()}
            disabled={!lookupEkzNr.trim() || lookupMutation.isPending}
            aria-label="Kontenlookup ausfuehren"
          >
            Lookup ausfuehren
          </Button>
          {lookupError ? (
            <Alert variant="destructive">
              <AlertTitle>Lookup</AlertTitle>
              <AlertDescription>{lookupError}</AlertDescription>
            </Alert>
          ) : null}
          {lookupResult ? (
            <div className="rounded-lg border bg-muted/40 p-4 text-sm">
              <p>
                <span className="font-medium">EKZ:</span> {lookupResult.ekz_nr}
              </p>
              <p>
                <span className="font-medium">Gueltig ab:</span> {lookupResult.gueltig_ab}
              </p>
              <p>
                <span className="font-medium">Erloeskonto:</span> {lookupResult.konto_erloese ?? '-'}
              </p>
              <p>
                <span className="font-medium">Aufwandskonto:</span> {lookupResult.konto_aufwand ?? '-'}
              </p>
              <p>
                <span className="font-medium">USt-Konto:</span> {lookupResult.konto_umsatzsteuer ?? '-'}
              </p>
              <p>
                <span className="font-medium">VSt-Konto:</span> {lookupResult.konto_vorsteuer ?? '-'}
              </p>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Filter</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          <NativeSelect
            ariaLabel="Filter Erlöskennziffer"
            value={filterEkzId}
            onValueChange={setFilterEkzId}
            placeholder="Alle EKZ"
            options={[{ value: '', label: 'Alle EKZ' }, ...ekzOptions]}
          />
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
            <Input
              placeholder="Steuerschluessel filtern..."
              aria-label="Steuerschluessel filtern"
              value={filterSteuerschluessel}
              onChange={(event) => setFilterSteuerschluessel(event.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {rows.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Erlöskontenzuordnungen vorhanden.</p>
          ) : (
            <DataTable data={rows} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
