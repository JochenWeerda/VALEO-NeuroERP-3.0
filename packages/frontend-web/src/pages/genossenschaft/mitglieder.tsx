import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Callout } from '@/components/ui/callout'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { ArrowRightLeft, Plus, Search, Users } from 'lucide-react'

/**
 * Mitgliederliste einer eG (§ 30 GenG).
 *
 * Bis zum 05.10.2026 las diese Maske Felder, die es nie gab: `vorname`,
 * `geschaeftsanteile`, `gesamtkapital`. Der Endpunkt lieferte sie nicht — er
 * lieferte überhaupt nichts, weil die Tabelle in keiner Datenbank existierte und
 * der Lesefehler zu `[]` wurde. Die Maske zeigte „undefined, undefined" in der
 * Namensspalte und `NaN €` beim Gesamtkapital, und niemand erfuhr, warum.
 *
 * Jetzt kommen die Felder aus dem Register, das Kapital aus der
 * Kapitalübersicht (§ 337 HGB), und der Anteilsbestand ist abgeleitet — es gibt
 * keine zweite Zahl mehr, die abweichen könnte.
 */
type Mitglied = {
  id: string
  mitglieds_nr: string
  name: string
  adresse: string
  eintrittsdatum: string | null
  austrittsdatum: string | null
  anteilswert_eur: number
  status: string
  iban: string
  bank_name: string
  /** Abgeleitet aus den Anteilsbewegungen. */
  genossenschaftsanteile: number
  geschaeftsguthaben_eur: number
}

type Kapital = {
  total_mitglieder: number
  total_anteile: number
  total_kapital_eur: number
  aktiv: number
  ruhend: number
  ausgetreten: number
  offene_auseinandersetzung_anteile: number
}

const BEWEGUNGSTYPEN = [
  'ZEICHNUNG',
  'ERHOEHUNG',
  'TEILRUECKZAHLUNG',
  'VOLLRUECKZAHLUNG',
] as const

const STATUS_VARIANTE: Record<string, 'default' | 'secondary' | 'outline'> = {
  AKTIV: 'default',
  RUHEND: 'secondary',
  AUSGETRETEN: 'outline',
}

function euro(wert: number): string {
  return `${wert.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €`
}

function fehlertext(fehler: unknown): string {
  const detail = (fehler as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object') {
    const d = detail as { error?: string; grund?: string }
    return [d.error, d.grund].filter(Boolean).join(' — ') || JSON.stringify(detail)
  }
  return (fehler as Error)?.message ?? 'Unbekannter Fehler'
}

export default function GenossenschaftMitgliederPage(): JSX.Element {
  const [suche, setSuche] = useState('')
  const [anlegenOffen, setAnlegenOffen] = useState(false)
  const [bewegungFuer, setBewegungFuer] = useState<Mitglied | null>(null)
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const [name, setName] = useState('')
  const [adresse, setAdresse] = useState('')
  const [eintrittsdatum, setEintrittsdatum] = useState('')
  const [anteilswert, setAnteilswert] = useState('100')
  const [anteile, setAnteile] = useState('0')
  const [iban, setIban] = useState('')
  const [bankName, setBankName] = useState('')

  const [bewegungstyp, setBewegungstyp] = useState<string>('ERHOEHUNG')
  const [bewegungAnzahl, setBewegungAnzahl] = useState('1')
  const [bewegungDatum, setBewegungDatum] = useState('')

  const mitgliederQuery = useQuery<Mitglied[]>({
    queryKey: ['genossenschaft', 'mitglieder'],
    queryFn: async () =>
      (await apiClient.get<Mitglied[]>('/api/v1/genossenschaft/mitglieder?limit=1000')).data,
  })

  const kapitalQuery = useQuery<Kapital>({
    queryKey: ['genossenschaft', 'kapital'],
    queryFn: async () =>
      (await apiClient.get<Kapital>('/api/v1/genossenschaft/kapitaluebersicht')).data,
  })

  const aktualisieren = async (): Promise<void> => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['genossenschaft', 'mitglieder'] }),
      queryClient.invalidateQueries({ queryKey: ['genossenschaft', 'kapital'] }),
    ])
  }

  const anlegen = useMutation({
    mutationFn: async () => {
      await apiClient.post('/api/v1/genossenschaft/mitglieder', {
        name,
        adresse,
        eintrittsdatum,
        anteilswert_eur: Number(anteilswert),
        genossenschaftsanteile: Number(anteile),
        iban,
        bank_name: bankName,
      })
    },
    onSuccess: async () => {
      toast({ title: 'Mitglied aufgenommen', description: `${name} steht in der Mitgliederliste.` })
      setAnlegenOffen(false)
      setName('')
      setAdresse('')
      setEintrittsdatum('')
      setAnteile('0')
      setIban('')
      setBankName('')
      await aktualisieren()
    },
    onError: (fehler) => {
      toast({
        title: 'Mitglied nicht aufgenommen',
        description: fehlertext(fehler),
        variant: 'destructive',
      })
    },
  })

  const buchen = useMutation({
    mutationFn: async (mitglied: Mitglied) => {
      const anzahl = Number(bewegungAnzahl)
      await apiClient.post(
        `/api/v1/genossenschaft/mitglieder/${mitglied.id}/anteilsbewegung`,
        {
          bewegungstyp,
          anzahl_anteile: anzahl,
          wert_eur: anzahl * mitglied.anteilswert_eur,
          datum: bewegungDatum,
        },
      )
    },
    onSuccess: async () => {
      toast({ title: 'Anteilsbewegung gebucht', description: 'Der Bestand folgt aus der Bewegung.' })
      setBewegungFuer(null)
      setBewegungAnzahl('1')
      setBewegungDatum('')
      await aktualisieren()
    },
    onError: (fehler) => {
      toast({
        title: 'Anteilsbewegung nicht gebucht',
        description: fehlertext(fehler),
        variant: 'destructive',
      })
    },
  })

  if (mitgliederQuery.isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-9 w-64" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (mitgliederQuery.isError) {
    return (
      <ErrorState
        error={mitgliederQuery.error as Error}
        onRetry={() => { void mitgliederQuery.refetch() }}
      />
    )
  }

  const mitglieder = mitgliederQuery.data ?? []
  const kapital = kapitalQuery.data
  const gefiltert = mitglieder.filter(
    (m) =>
      m.name.toLowerCase().includes(suche.toLowerCase()) ||
      m.mitglieds_nr.toLowerCase().includes(suche.toLowerCase()),
  )

  const spalten = [
    {
      key: 'mitglieds_nr' as const,
      label: 'Mitglieds-Nr',
      render: (m: Mitglied) => <span className="font-mono">{m.mitglieds_nr}</span>,
    },
    { key: 'name' as const, label: 'Name', render: (m: Mitglied) => m.name },
    {
      key: 'status' as const,
      label: 'Stand',
      render: (m: Mitglied) => (
        <Badge variant={STATUS_VARIANTE[m.status] ?? 'outline'}>{m.status}</Badge>
      ),
    },
    {
      key: 'eintrittsdatum' as const,
      label: 'Eintritt',
      render: (m: Mitglied) =>
        m.eintrittsdatum ? new Date(m.eintrittsdatum).toLocaleDateString('de-DE') : '–',
    },
    {
      key: 'genossenschaftsanteile' as const,
      label: 'Anteile',
      render: (m: Mitglied) => m.genossenschaftsanteile.toLocaleString('de-DE'),
    },
    {
      key: 'geschaeftsguthaben_eur' as const,
      label: 'Geschäftsguthaben',
      render: (m: Mitglied) => euro(m.geschaeftsguthaben_eur),
    },
    {
      key: 'id' as const,
      label: '',
      render: (m: Mitglied) => (
        <Button
          variant="ghost"
          size="sm"
          className="gap-2"
          disabled={m.status === 'AUSGETRETEN' || buchen.isPending}
          onClick={() => {
            setBewegungFuer(m)
            setBewegungstyp('ERHOEHUNG')
            setBewegungAnzahl('1')
            setBewegungDatum(new Date().toISOString().slice(0, 10))
          }}
        >
          <ArrowRightLeft className="h-4 w-4" />
          Anteile
        </Button>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Genossenschaftsmitglieder</h1>
            <p className="text-muted-foreground">
              Mitgliederliste nach § 30 GenG — der Anteilsbestand folgt aus den Anteilsbewegungen
            </p>
          </div>
          <Button className="gap-2" onClick={() => setAnlegenOffen(true)}>
            <Plus className="h-4 w-4" />
            Mitglied aufnehmen
          </Button>
        </div>

        {kapitalQuery.isError && (
          <Callout variant="error">
            Die Kapitalübersicht ist derzeit nicht lesbar. Die angezeigten Summen fehlen —
            sie werden nicht als 0,00 € dargestellt, weil das eine Bilanzaussage wäre.
          </Callout>
        )}

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm">
                <Users className="h-4 w-4" />
                Mitglieder
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">{kapital?.total_mitglieder ?? '–'}</span>
              {kapital && (
                <p className="text-2xs uppercase tracking-wide text-muted-foreground">
                  {kapital.aktiv} aktiv · {kapital.ruhend} ruhend · {kapital.ausgetreten} ausgetreten
                </p>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Anteile</CardTitle></CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">
                {kapital ? kapital.total_anteile.toLocaleString('de-DE') : '–'}
              </span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Geschäftsguthaben</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">
                {kapital ? euro(kapital.total_kapital_eur) : '–'}
              </span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Offene Auseinandersetzung</CardTitle>
            </CardHeader>
            <CardContent>
              <span
                className={
                  (kapital?.offene_auseinandersetzung_anteile ?? 0) > 0
                    ? 'text-2xl font-bold text-status-warning'
                    : 'text-2xl font-bold text-muted-foreground'
                }
              >
                {kapital?.offene_auseinandersetzung_anteile ?? '–'}
              </span>
              <p className="text-2xs uppercase tracking-wide text-muted-foreground">§ 73 GenG</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Mitgliederliste ({gefiltert.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Suche Name oder Mitglieds-Nr…"
                value={suche}
                onChange={(e) => setSuche(e.target.value)}
                className="pl-10"
              />
            </div>
            <DataTable data={gefiltert} columns={spalten} />
          </CardContent>
        </Card>
      </div>

      <Dialog open={anlegenOffen} onOpenChange={setAnlegenOffen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Mitglied aufnehmen</DialogTitle>
            <DialogDescription>
              Eine Erstzeichnung wird als Anteilsbewegung gebucht, nicht als Zahl gespeichert —
              auch der erste Anteil hat damit einen Beleg.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label htmlFor="geno-name">Name</Label>
              <Input id="geno-name" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div>
              <Label htmlFor="geno-adresse">Adresse</Label>
              <Input id="geno-adresse" value={adresse} onChange={(e) => setAdresse(e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="geno-eintritt">Eintrittsdatum</Label>
                <Input
                  id="geno-eintritt"
                  type="date"
                  value={eintrittsdatum}
                  onChange={(e) => setEintrittsdatum(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="geno-anteilswert">Anteilswert (€)</Label>
                <Input
                  id="geno-anteilswert"
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={anteilswert}
                  onChange={(e) => setAnteilswert(e.target.value)}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="geno-anteile">Erstzeichnung (Anteile)</Label>
              <Input
                id="geno-anteile"
                type="number"
                min="0"
                value={anteile}
                onChange={(e) => setAnteile(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="geno-iban">IBAN</Label>
                <Input id="geno-iban" value={iban} onChange={(e) => setIban(e.target.value)} />
              </div>
              <div>
                <Label htmlFor="geno-bank">Bank</Label>
                <Input id="geno-bank" value={bankName} onChange={(e) => setBankName(e.target.value)} />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAnlegenOffen(false)} disabled={anlegen.isPending}>
              Abbrechen
            </Button>
            <Button
              onClick={() => { anlegen.mutate() }}
              disabled={
                anlegen.isPending ||
                !name.trim() ||
                !adresse.trim() ||
                !eintrittsdatum ||
                !iban.trim() ||
                !bankName.trim()
              }
            >
              {anlegen.isPending ? 'Wird aufgenommen…' : 'Aufnehmen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={bewegungFuer !== null} onOpenChange={(offen) => { if (!offen) setBewegungFuer(null) }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Anteilsbewegung buchen</DialogTitle>
            <DialogDescription>
              {bewegungFuer
                ? `${bewegungFuer.mitglieds_nr} · ${bewegungFuer.name} hält ${bewegungFuer.genossenschaftsanteile} Anteile.`
                : null}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label htmlFor="geno-typ">Bewegungstyp</Label>
              <NativeSelect
                id="geno-typ"
                value={bewegungstyp}
                onChange={(e) => setBewegungstyp(e.target.value)}
              >
                {BEWEGUNGSTYPEN.map((typ) => (
                  <option key={typ} value={typ}>{typ}</option>
                ))}
              </NativeSelect>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="geno-anzahl">Anteile</Label>
                <Input
                  id="geno-anzahl"
                  type="number"
                  min="1"
                  value={bewegungAnzahl}
                  onChange={(e) => setBewegungAnzahl(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="geno-datum">Datum</Label>
                <Input
                  id="geno-datum"
                  type="date"
                  value={bewegungDatum}
                  onChange={(e) => setBewegungDatum(e.target.value)}
                />
              </div>
            </div>
            {bewegungstyp === 'VOLLRUECKZAHLUNG' && bewegungFuer && (
              <Callout variant="warning">
                Eine Vollrückzahlung muss den ganzen Bestand treffen —
                {` ${bewegungFuer.genossenschaftsanteile} Anteile.`}
              </Callout>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBewegungFuer(null)} disabled={buchen.isPending}>
              Abbrechen
            </Button>
            <Button
              onClick={() => { if (bewegungFuer) buchen.mutate(bewegungFuer) }}
              disabled={buchen.isPending || !bewegungDatum || Number(bewegungAnzahl) < 1}
            >
              {buchen.isPending ? 'Wird gebucht…' : 'Buchen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
