import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, Euro, FileDown, Search, Loader2 } from 'lucide-react'
import { useDebitoren, useMahnen } from '@/lib/api/fibu'
import { useToast } from '@/hooks/use-toast'

export default function DebitorenAPIPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterUeberfaellig, setFilterUeberfaellig] = useState<boolean | undefined>(undefined)

  // API Integration
  const { data: debitoren = [], isLoading, error } = useDebitoren({ ueberfaellig: filterUeberfaellig })
  const mahnenMutation = useMahnen()

  async function handleMahnen(id: string): Promise<void> {
    try {
      const result = await mahnenMutation.mutateAsync(id)
      toast({
        title: 'Mahnung erstellt',
        description: `Mahnstufe ${(result as any).mahn_stufe || 1} wurde erstellt`,
      })
    } catch (err) {
      toast({
        title: 'Fehler',
        description: 'Mahnung konnte nicht erstellt werden',
        variant: 'destructive',
      })
    }
  }

  const columns = [
    {
      key: 'rechnungsnr' as const,
      label: 'Rechnung',
      render: (op: typeof debitoren[0]) => (
        <button onClick={() => navigate(`/sales/invoice/${op.id}`)} className="font-medium text-blue-600 hover:underline font-mono">
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
          <span className={ueberfaellig ? 'font-semibold text-red-600' : ''}>
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
            <Button size="sm" variant="outline" onClick={() => handleMahnen(op.id)} disabled={mahnenMutation.isPending}>
              Mahnen
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
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">Fehler beim Laden der Daten</span>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const gesamtOffen = debitoren.reduce((sum, op) => sum + op.offen, 0)
  const ueberfaellig = debitoren.filter((op) => new Date(op.faelligkeit) < new Date()).length
  const mahnungen = debitoren.filter((op) => (op.mahn_stufe ?? 0) > 0).length

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
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ueberfaellig} überfällige Rechnung(en)!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Posten</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{debitoren.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">
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
            <span className="text-2xl font-bold text-red-600">{ueberfaellig}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Mahnung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{mahnungen}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button
              variant={filterUeberfaellig === true ? 'default' : 'outline'}
              onClick={() => setFilterUeberfaellig(filterUeberfaellig === true ? undefined : true)}
            >
              Nur Überfällige
            </Button>
            <Button variant="outline" className="gap-2">
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
            <DataTable data={debitoren} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
