import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, Euro, FileDown, Search, Loader2 } from 'lucide-react'
import { useDebitoren, useMahnen } from '@/lib/api/fibu'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function DebitorenAPIPage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterUeberfaellig, setFilterUeberfaellig] = useState<boolean | undefined>(undefined)
  const [mahnenPendingId, setMahnenPendingId] = useState<string | null>(null)

  // API Integration
  const { data: debitoren = [], isLoading, error } = useDebitoren({ ueberfaellig: filterUeberfaellig })
  const mahnenMutation = useMahnen()

  async function handleMahnen(id: string): Promise<void> {
    if (mahnenPendingId) return
    setMahnenPendingId(id)
    try {
      const result = await mahnenMutation.mutateAsync(id)
      toast({
        title: 'Mahnung erstellt',
        description: `Mahnstufe ${String(( result as Record<string, unknown>).mahn_stufe ?? 1)} wurde erstellt`,
      })
    } catch (err) {
      toast({
        title: 'Fehler',
        description: 'Mahnung konnte nicht erstellt werden',
        variant: 'destructive',
      })
    } finally {
      setMahnenPendingId(null)
    }
  }

  const columns = [
    {
      key: 'rechnungsnr' as const,
      label: 'Rechnung',
      render: (op: typeof debitoren[0]) => (
        <button type="button" onClick={() => navigate(`/sales/invoice/${op.id}`)} className="min-h-11 font-mono font-medium text-primary touch-manipulation">
          {op.rechnungsnr}
        </button>
      ),
    },
    { key: 'kunde_name' as const, label: 'Kunde' },
    { key: 'kunde_id' as const, label: 'Kd-Nr', render: (op: typeof debitoren[0]) => <span className="font-mono text-sm">{op.kunde_id}</span> },
    { key: 'datum' as const, label: 'Re-Datum', render: (op: typeof debitoren[0]) => new Date(op.datum).toLocaleDateString('de-DE') },
    {
      key: 'faelligkeit' as const,
      label: 'Fälligkeit',
      render: (op: typeof debitoren[0]) => {
        const faellig = new Date(op.faelligkeit)
        const ueberfaellig = faellig < new Date()
        return (
          <span className={ueberfaellig ? 'font-semibold text-status-error' : ''}>
            {faellig.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (op: typeof debitoren[0]) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(op.betrag),
    },
    {
      key: 'offen' as const,
      label: 'Offen',
      render: (op: typeof debitoren[0]) => (
        <span className="font-bold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(op.offen)}
        </span>
      ),
    },
    {
      key: 'mahn_stufe' as const,
      label: 'Status',
      render: (op: typeof debitoren[0]) => {
        if ((op.mahn_stufe ?? 0) > 0) {
          return <Badge variant="destructive">Mahnstufe {op.mahn_stufe}</Badge>
        }
        const ueberfaellig = new Date(op.faelligkeit) < new Date()
        if (ueberfaellig) {
          return <Badge variant="secondary">Überfällig</Badge>
        }
        return <Badge variant="outline">Offen</Badge>
      },
    },
    {
      key: 'id' as const,
      label: 'Aktion',
      render: (op: typeof debitoren[0]) => {
        const ueberfaellig = new Date(op.faelligkeit) < new Date()
        if (ueberfaellig && (op.mahn_stufe ?? 0) < 3) {
          return (
            <Button className="min-h-touch touch-manipulation" variant="outline" onClick={() => void handleMahnen(op.id)} disabled={mahnenPendingId === op.id}>
              {mahnenPendingId === op.id ? 'Mahnen...' : 'Mahnen'}
            </Button>
          )
        }
        return null
      },
    },
  ]

  if (error) {
    return (
      <div className="p-6">
        <Card className="border-red-500">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-status-error">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">Fehler beim Laden der Daten</span>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const sichtbare = searchTerm
    ? debitoren.filter((op) => {
        const term = searchTerm.toLowerCase()
        return (
          String(op.rechnungsnr ?? '').toLowerCase().includes(term) ||
          String(op.kunde_name ?? '').toLowerCase().includes(term) ||
          String(op.kunde_id ?? '').toLowerCase().includes(term)
        )
      })
    : debitoren

  const gesamtOffen = sichtbare.reduce((sum, op) => sum + op.offen, 0)
  const ueberfaellig = sichtbare.filter((op) => new Date(op.faelligkeit) < new Date()).length
  const mahnungen = sichtbare.filter((op) => (op.mahn_stufe ?? 0) > 0).length

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Debitorenbuchhaltung</h1>
          <p className="text-muted-foreground">Offene Posten Kunden (API-integriert)</p>
        </div>
        {isLoading && <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />}
      </div>

      {ueberfaellig > 0 && (
        <Card className="border-status-warning/40 bg-status-warning/10">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-status-warning">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ueberfaellig} überfällige Rechnung(en)!</span>
            </div>
          </CardContent>
        </Card>
      )}

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Posten</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{sichtbare.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-status-warning" />
              <span className="text-2xl font-bold text-status-warning">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtOffen)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Überfällig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-error">{ueberfaellig}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Mahnung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-error">{mahnungen}</span>
          </CardContent>
        </Card>
      </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input aria-label="Suche Debitoren" placeholder="Kunde, Rechnung" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" />
            </div>
            <Button
              variant={filterUeberfaellig === true ? 'default' : 'outline'}
              className="min-h-touch touch-manipulation"
              onClick={() => setFilterUeberfaellig(filterUeberfaellig === true ? undefined : true)}
            >
              Nur Überfällige
            </Button>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation">
              <FileDown className="h-4 w-4" />
              DATEV Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <DataTable data={sichtbare} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
