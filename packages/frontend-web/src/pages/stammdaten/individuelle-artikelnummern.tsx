import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useCreateIndividuelleArtikelnummer,
  useDeleteIndividuelleArtikelnummer,
  useIndividuelleArtikelnummern,
  useLookupIndividuelleArtikelnummer,
  type IndivArtikelNrLookupResult,
} from '@/lib/api/individuelleArtikelnummern'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Hash, Plus, Search, Trash2 } from 'lucide-react'

type FormData = {
  artikel_nr: string
  partner_nr: string
  partner_typ: 'kunden' | 'lieferanten'
  indiv_artikel_nr: string
  indiv_bezeichnung: string
  gueltig_von: string
  gueltig_bis: string
}

const partnerTypOptions = [
  { value: 'kunden', label: 'Kunde (VK)' },
  { value: 'lieferanten', label: 'Lieferant (EK)' },
]

function optionalDate(value: string): string | null {
  return value.trim() === '' ? null : value
}

function optionalText(value: string): string | null {
  return value.trim() === '' ? null : value.trim()
}

export default function IndividuelleArtikelnummernPage() {
  const [filterPartnerNr, setFilterPartnerNr] = useState('')
  const [filterPartnerTyp, setFilterPartnerTyp] = useState<'kunden' | 'lieferanten' | ''>('')
  const [filterArtikelNr, setFilterArtikelNr] = useState('')

  const listFilters = useMemo(
    () => ({
      partner_nr: filterPartnerNr.trim() || undefined,
      partner_typ: filterPartnerTyp || undefined,
      artikel_nr: filterArtikelNr.trim() || undefined,
    }),
    [filterPartnerNr, filterPartnerTyp, filterArtikelNr],
  )

  const { data: nummern, isLoading, isError } = useIndividuelleArtikelnummern(listFilters)
  const createMutation = useCreateIndividuelleArtikelnummer()
  const deleteMutation = useDeleteIndividuelleArtikelnummer()
  const lookupMutation = useLookupIndividuelleArtikelnummer()

  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [lookupPartnerNr, setLookupPartnerNr] = useState('')
  const [lookupPartnerTyp, setLookupPartnerTyp] = useState<'kunden' | 'lieferanten'>('kunden')
  const [lookupIndivNr, setLookupIndivNr] = useState('')
  const [lookupResult, setLookupResult] = useState<IndivArtikelNrLookupResult | null>(null)
  const [lookupError, setLookupError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting },
  } = useForm<FormData>({
    defaultValues: {
      artikel_nr: '',
      partner_nr: '',
      partner_typ: 'kunden',
      indiv_artikel_nr: '',
      indiv_bezeichnung: '',
      gueltig_von: '',
      gueltig_bis: '',
    },
  })

  const onSubmit = async (data: FormData) => {
    try {
      await createMutation.mutateAsync({
        artikel_nr: data.artikel_nr.trim(),
        partner_nr: data.partner_nr.trim(),
        partner_typ: data.partner_typ,
        indiv_artikel_nr: data.indiv_artikel_nr.trim(),
        indiv_bezeichnung: optionalText(data.indiv_bezeichnung),
        gueltig_von: optionalDate(data.gueltig_von),
        gueltig_bis: optionalDate(data.gueltig_bis),
      })
      toast.success(`Zuordnung ${data.indiv_artikel_nr} angelegt.`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der individuellen Artikelnummer.')
    }
  }

  const handleDelete = async (id: string, indivNr: string) => {
    if (deletingId === id) return
    setDeletingId(id)
    try {
      await deleteMutation.mutateAsync(id)
      toast.success(`Zuordnung ${indivNr} deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren der Zuordnung.')
    } finally {
      setDeletingId(null)
    }
  }

  const handleLookup = async () => {
    if (lookupMutation.isPending) return
    setLookupResult(null)
    setLookupError(null)
    const partnerNr = lookupPartnerNr.trim()
    const indivNr = lookupIndivNr.trim()
    if (!partnerNr || !indivNr) {
      setLookupError('Partner-Nr. und externe Artikel-Nr. sind erforderlich.')
      return
    }
    try {
      const result = await lookupMutation.mutateAsync({
        partner_nr: partnerNr,
        indiv_artikel_nr: indivNr,
        partner_typ: lookupPartnerTyp,
      })
      setLookupResult(result)
    } catch {
      setLookupError('Keine interne Artikelnummer für diese externe Nummer gefunden.')
    }
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold">
          <Hash className="h-6 w-6" aria-hidden="true" />
          Individuelle Artikelnummern
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Partner-spezifische Artikelkennungen auf interne Artikelnummern mappen
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Neue Zuordnung anlegen</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            data-testid="ian-form"
            onSubmit={handleSubmit(onSubmit)}
            noValidate
            className="grid grid-cols-1 gap-3 sm:grid-cols-3"
          >
            <div>
              <Label htmlFor="ian_artikel_nr">Interne Artikel-Nr. *</Label>
              <Input id="ian_artikel_nr" placeholder="z. B. 100234" {...register('artikel_nr', { required: true })} />
            </div>
            <div>
              <Label htmlFor="ian_partner_nr">Partner-Nr. *</Label>
              <Input id="ian_partner_nr" placeholder="z. B. K001" {...register('partner_nr', { required: true })} />
            </div>
            <div>
              <Label htmlFor="ian_partner_typ">Partner-Typ *</Label>
              <NativeSelect id="ian_partner_typ" {...register('partner_typ', { required: true })}>
                {partnerTypOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </NativeSelect>
            </div>
            <div>
              <Label htmlFor="ian_indiv_nr">Externe Artikel-Nr. *</Label>
              <Input
                id="ian_indiv_nr"
                placeholder="Partner-Artikelnummer"
                {...register('indiv_artikel_nr', { required: true })}
              />
            </div>
            <div className="sm:col-span-2">
              <Label htmlFor="ian_bezeichnung">Externe Bezeichnung</Label>
              <Input id="ian_bezeichnung" placeholder="Partner-Bezeichnung" {...register('indiv_bezeichnung')} />
            </div>
            <div>
              <Label htmlFor="ian_gueltig_von">Gültig von</Label>
              <Input id="ian_gueltig_von" type="date" {...register('gueltig_von')} />
            </div>
            <div>
              <Label htmlFor="ian_gueltig_bis">Gültig bis</Label>
              <Input id="ian_gueltig_bis" type="date" {...register('gueltig_bis')} />
            </div>
            <div className="flex justify-end sm:col-span-3">
              <Button type="submit" disabled={isSubmitting || createMutation.isPending} aria-label="Zuordnung anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Interne Nummer suchen (Lookup)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
            <div>
              <Label htmlFor="lookup_partner_nr">Partner-Nr.</Label>
              <Input
                id="lookup_partner_nr"
                value={lookupPartnerNr}
                onChange={(e) => setLookupPartnerNr(e.target.value)}
                placeholder="z. B. K001"
              />
            </div>
            <div>
              <Label htmlFor="lookup_partner_typ">Partner-Typ</Label>
              <NativeSelect
                id="lookup_partner_typ"
                value={lookupPartnerTyp}
                onChange={(e) => setLookupPartnerTyp(e.target.value as 'kunden' | 'lieferanten')}
              >
                {partnerTypOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </NativeSelect>
            </div>
            <div>
              <Label htmlFor="lookup_indiv_nr">Externe Artikel-Nr.</Label>
              <Input
                id="lookup_indiv_nr"
                value={lookupIndivNr}
                onChange={(e) => setLookupIndivNr(e.target.value)}
                placeholder="Partner-Artikelnummer"
              />
            </div>
            <div className="flex items-end">
              <Button
                type="button"
                variant="secondary"
                disabled={lookupMutation.isPending}
                onClick={() => void handleLookup()}
                aria-label="Interne Artikelnummer suchen"
              >
                <Search className="mr-1 h-4 w-4" aria-hidden="true" />
                Suchen
              </Button>
            </div>
          </div>
          {lookupError && <p className="text-sm text-destructive">{lookupError}</p>}
          {lookupResult && (
            <div className="rounded-md border bg-muted/40 p-3 text-sm" data-testid="ian-lookup-result">
              <p>
                <span className="font-medium">Interne Artikel-Nr.:</span>{' '}
                <span className="font-mono">{lookupResult.interne_artikel_nr}</span>
              </p>
              {lookupResult.indiv_bezeichnung && (
                <p className="mt-1 text-muted-foreground">{lookupResult.indiv_bezeichnung}</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Zuordnungen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div>
              <Label htmlFor="filter_partner_nr">Filter Partner-Nr.</Label>
              <Input
                id="filter_partner_nr"
                value={filterPartnerNr}
                onChange={(e) => setFilterPartnerNr(e.target.value)}
                placeholder="Alle"
              />
            </div>
            <div>
              <Label htmlFor="filter_partner_typ">Filter Partner-Typ</Label>
              <NativeSelect
                id="filter_partner_typ"
                value={filterPartnerTyp}
                onChange={(e) => setFilterPartnerTyp(e.target.value as '' | 'kunden' | 'lieferanten')}
              >
                <option value="">Alle</option>
                {partnerTypOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </NativeSelect>
            </div>
            <div>
              <Label htmlFor="filter_artikel_nr">Filter Artikel-Nr.</Label>
              <Input
                id="filter_artikel_nr"
                value={filterArtikelNr}
                onChange={(e) => setFilterArtikelNr(e.target.value)}
                placeholder="Alle"
              />
            </div>
          </div>

          {isLoading && (
            <div className="space-y-2">
              {[0, 1, 2].map((i) => (
                <Skeleton key={i} className="h-9 w-full" />
              ))}
            </div>
          )}
          {isError && <p className="text-sm text-destructive">Fehler beim Laden der Zuordnungen.</p>}
          {!isLoading && !isError && (!nummern || nummern.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Zuordnungen vorhanden.</p>
          )}
          {nummern && nummern.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Interne Artikel-Nr.</TableHead>
                  <TableHead>Partner</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Externe Artikel-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Gültigkeit</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {nummern.map((n) => (
                  <TableRow key={n.id}>
                    <TableCell className="font-mono text-sm">{n.artikel_nr}</TableCell>
                    <TableCell className="font-mono text-sm">{n.partner_nr}</TableCell>
                    <TableCell>{n.partner_typ === 'kunden' ? 'Kunde' : 'Lieferant'}</TableCell>
                    <TableCell className="font-mono text-sm">{n.indiv_artikel_nr}</TableCell>
                    <TableCell>{n.indiv_bezeichnung ?? '—'}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {n.gueltig_von ?? '—'} – {n.gueltig_bis ?? '—'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={n.aktiv ? 'default' : 'secondary'}>
                        {n.aktiv ? 'Aktiv' : 'Inaktiv'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={deletingId === n.id || !n.aktiv}
                        onClick={() => void handleDelete(n.id, n.indiv_artikel_nr)}
                        aria-label={`Zuordnung ${n.indiv_artikel_nr} deaktivieren`}
                      >
                        <Trash2 className="h-4 w-4" aria-hidden="true" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
