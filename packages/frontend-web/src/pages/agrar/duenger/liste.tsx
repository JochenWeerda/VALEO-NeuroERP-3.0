import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { AlertTriangle, Plus, Filter } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { useDuenger, useDeleteDuenger, type Duenger } from '@/lib/api/agrar'

export default function DuengerListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const [deletePendingId, setDeletePendingId] = useState<string | null>(null)

  const [searchTerm, setSearchTerm] = useState('')
  const [typFilter, setTypFilter] = useState('')
  const [herstellerFilter, setHerstellerFilter] = useState('')
  const [erklaerungFilter, setErklaerungFilter] = useState('')

  const { data, isLoading } = useDuenger({
    search: searchTerm || undefined,
    typ: typFilter || undefined,
    hersteller: herstellerFilter || undefined,
  })
  const deleteMutation = useDeleteDuenger()

  const duenger = data?.items ?? []

  const filteredDuenger = useMemo(() => {
    let filtered = duenger
    if (erklaerungFilter === 'erforderlich') {
      filtered = filtered.filter(d => d.erklaerung_landwirt_erforderlich)
    } else if (erklaerungFilter === 'ausstehend') {
      filtered = filtered.filter(d => d.erklaerung_landwirt_status === 'ausstehend')
    } else if (erklaerungFilter === 'geprueft') {
      filtered = filtered.filter(d => d.erklaerung_landwirt_status === 'geprueft')
    }
    return filtered
  }, [duenger, erklaerungFilter])

  const handleDelete = async (id: string) => {
    if (deletePendingId) return
    if (!confirm('Dünger wirklich löschen?')) return
    setDeletePendingId(id)
    try {
      await deleteMutation.mutateAsync(id)
      toast({ title: "Gelöscht", description: "Dünger wurde erfolgreich gelöscht." })
    } catch {
      toast({ title: "Fehler", description: "Fehler beim Löschen des Düngers.", variant: "destructive" })
    } finally {
      setDeletePendingId(null)
    }
  }

  const getErklaerungBadgeVariant = (status: string | null) => {
    switch (status) {
      case 'geprueft': return 'default' as const
      case 'eingegangen': return 'secondary' as const
      case 'abgelehnt': return 'destructive' as const
      default: return 'outline' as const
    }
  }

  const getErklaerungText = (status: string | null) => {
    switch (status) {
      case 'geprueft': return 'Geprüft'
      case 'eingegangen': return 'Eingegangen'
      case 'abgelehnt': return 'Abgelehnt'
      default: return 'Ausstehend'
    }
  }

  const isZulassungAblaufend = (ablauf: string) => {
    const ablaufDate = new Date(ablauf)
    const warnDate = new Date()
    warnDate.setMonth(warnDate.getMonth() + 6)
    return ablaufDate < warnDate
  }

  const uniqueTypes = [...new Set(duenger.map(d => d.typ))]
  const uniqueHersteller = [...new Set(duenger.map(d => d.hersteller))]

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-64" />
          </div>
          <Skeleton className="h-10 w-24" />
        </div>
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Düngemittel</h1>
          <p className="text-muted-foreground">Dünger suchen, öffnen und prüfen</p>
        </div>
        <Button onClick={() => navigate('/agrar/duenger/stamm')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neu
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-5">
            <div>
              <Input
                aria-label="Suche Dünger"
                placeholder="Suchen"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch w-full"
              />
            </div>
            <div>
              <NativeSelect
                ariaLabel="Typ"
                value={typFilter || 'all'}
                onValueChange={(value) => setTypFilter(value === 'all' ? '' : value)}
                options={[
                  { value: 'all', label: 'Alle Typen' },
                  ...uniqueTypes.map((type) => ({ value: type, label: type })),
                ]}
              />
            </div>
            <div>
              <NativeSelect
                ariaLabel="Hersteller"
                value={herstellerFilter || 'all'}
                onValueChange={(value) => setHerstellerFilter(value === 'all' ? '' : value)}
                options={[
                  { value: 'all', label: 'Alle Hersteller' },
                  ...uniqueHersteller.map((hersteller) => ({ value: hersteller, label: hersteller })),
                ]}
              />
            </div>
            <div>
              <NativeSelect
                ariaLabel="Erklaerung"
                value={erklaerungFilter || 'all'}
                onValueChange={(value) => setErklaerungFilter(value === 'all' ? '' : value)}
                options={[
                  { value: 'all', label: 'Alle' },
                  { value: 'erforderlich', label: 'Erklaerung erforderlich' },
                  { value: 'ausstehend', label: 'Ausstehend' },
                  { value: 'geprueft', label: 'Geprueft' },
                ]}
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                className="min-h-touch touch-manipulation"
                onClick={() => {
                setSearchTerm('')
                setTypFilter('')
                setHerstellerFilter('')
                setErklaerungFilter('')
              }}>
                Zurücksetzen
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle>Düngemittel ({filteredDuenger.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Artikel</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Typ</TableHead>
                <TableHead>NPK</TableHead>
                <TableHead>Hersteller</TableHead>
                <TableHead>Zulassung bis</TableHead>
                <TableHead>Bestand</TableHead>
                <TableHead>Erklärung</TableHead>
                <TableHead>Aktionen</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredDuenger.map((d: Duenger) => (
                <TableRow key={d.id}>
                  <TableCell className="font-mono text-sm">{d.artikelnummer}</TableCell>
                  <TableCell>
                    <div>
                      <button
                        type="button"
                        onClick={() => navigate(`/agrar/duenger/stamm/${d.id}`)}
                        className="min-h-11 font-medium text-primary touch-manipulation"
                      >
                        {d.name}
                      </button>
                      {d.ausgangsstoff_explosivstoffe && (
                        <Badge variant="destructive" className="text-xs mt-1">
                          Ausgangsstoff für Explosivstoffe
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{d.typ}</Badge>
                  </TableCell>
                  <TableCell className="font-mono text-sm">
                    {d.n_gehalt}-{d.p_gehalt}-{d.k_gehalt}
                    {d.s_gehalt > 0 && `-${d.s_gehalt}S`}
                    {d.mg_gehalt > 0 && `-${d.mg_gehalt}Mg`}
                  </TableCell>
                  <TableCell>{d.hersteller}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className={isZulassungAblaufend(d.ablauf_zulassung) ? 'text-status-error font-medium' : ''}>
                        {new Date(d.ablauf_zulassung).toLocaleDateString('de-DE')}
                      </span>
                      {isZulassungAblaufend(d.ablauf_zulassung) && (
                        <AlertTriangle className="h-4 w-4 text-status-error" />
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-right">
                      <div className="font-medium">{d.lagerbestand.toLocaleString('de-DE')} kg</div>
                      <div className="text-sm text-muted-foreground">
                        VK: {d.vk_preis.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    {d.erklaerung_landwirt_erforderlich ? (
                      <Badge variant={getErklaerungBadgeVariant(d.erklaerung_landwirt_status)}>
                        {getErklaerungText(d.erklaerung_landwirt_status)}
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground text-sm">Nicht erforderlich</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col gap-2 sm:flex-row">
                      <Button
                        variant="outline"
                        className="min-h-touch touch-manipulation"
                        onClick={() => navigate(`/agrar/duenger/stamm/${d.id}`)}
                      >
                        Anzeigen
                      </Button>
                      <Button
                        variant="outline"
                        className="min-h-touch touch-manipulation"
                        onClick={() => navigate(`/agrar/duenger/stamm/${d.id}/edit`)}
                      >
                        Bearbeiten
                      </Button>
                      <Button
                        variant="outline"
                        className="min-h-touch touch-manipulation"
                        onClick={() => void handleDelete(d.id)}
                        disabled={deletePendingId === d.id}
                      >
                        {deletePendingId === d.id ? 'Löschen...' : 'Löschen'}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Summary */}
      {!isTouch ? (
      <Card>
        <CardHeader>
          <CardTitle>Zusammenfassung</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{filteredDuenger.length}</div>
              <div className="text-sm text-muted-foreground">Düngemittel</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-status-success">
                {filteredDuenger.filter(d => d.ist_aktiv).length}
              </div>
              <div className="text-sm text-muted-foreground">Aktiv</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-status-warning">
                {filteredDuenger.filter(d => d.erklaerung_landwirt_erforderlich && d.erklaerung_landwirt_status === 'ausstehend').length}
              </div>
              <div className="text-sm text-muted-foreground">Erklärungen ausstehend</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-status-error">
                {filteredDuenger.filter(d => isZulassungAblaufend(d.ablauf_zulassung)).length}
              </div>
              <div className="text-sm text-muted-foreground">Zulassungen ablaufend</div>
            </div>
          </div>
        </CardContent>
      </Card>
      ) : null}
    </div>
  )
}
