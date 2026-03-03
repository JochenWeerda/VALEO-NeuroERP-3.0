import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { AlertTriangle, Plus, Filter, Eye, Edit, Trash2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useDuenger, useDeleteDuenger, type Duenger } from '@/lib/api/agrar'

export default function DuengerListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

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
    if (!confirm('Dünger wirklich löschen?')) return

    try {
      await deleteMutation.mutateAsync(id)
      toast({ title: "Gelöscht", description: "Dünger wurde erfolgreich gelöscht." })
    } catch {
      toast({ title: "Fehler", description: "Fehler beim Löschen des Düngers.", variant: "destructive" })
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
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Düngemittel</h1>
          <p className="text-muted-foreground">Übersicht aller Düngemittel</p>
        </div>
        <Button onClick={() => navigate('/agrar/duenger/stamm')} className="gap-2">
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
                placeholder="Suchen..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <div>
              <Select value={typFilter || 'all'} onValueChange={(v) => setTypFilter(v === 'all' ? '' : v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Typ" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Typen</SelectItem>
                  {uniqueTypes.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Select value={herstellerFilter || 'all'} onValueChange={(v) => setHerstellerFilter(v === 'all' ? '' : v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Hersteller" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Hersteller</SelectItem>
                  {uniqueHersteller.map(hersteller => (
                    <SelectItem key={hersteller} value={hersteller}>{hersteller}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Select value={erklaerungFilter || 'all'} onValueChange={(v) => setErklaerungFilter(v === 'all' ? '' : v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Erklärung" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle</SelectItem>
                  <SelectItem value="erforderlich">Erklärung erforderlich</SelectItem>
                  <SelectItem value="ausstehend">Ausstehend</SelectItem>
                  <SelectItem value="geprueft">Geprüft</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => {
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
                      <div className="font-medium">{d.name}</div>
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
                      <span className={isZulassungAblaufend(d.ablauf_zulassung) ? 'text-red-600 font-medium' : ''}>
                        {new Date(d.ablauf_zulassung).toLocaleDateString('de-DE')}
                      </span>
                      {isZulassungAblaufend(d.ablauf_zulassung) && (
                        <AlertTriangle className="h-4 w-4 text-red-600" />
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
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/agrar/duenger/stamm/${d.id}`)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/agrar/duenger/stamm/${d.id}/edit`)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(d.id)}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="h-4 w-4" />
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
      <Card>
        <CardHeader>
          <CardTitle>Zusammenfassung</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{filteredDuenger.length}</div>
              <div className="text-sm text-muted-foreground">Düngemittel</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {filteredDuenger.filter(d => d.ist_aktiv).length}
              </div>
              <div className="text-sm text-muted-foreground">Aktiv</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {filteredDuenger.filter(d => d.erklaerung_landwirt_erforderlich && d.erklaerung_landwirt_status === 'ausstehend').length}
              </div>
              <div className="text-sm text-muted-foreground">Erklärungen ausstehend</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {filteredDuenger.filter(d => isZulassungAblaufend(d.ablauf_zulassung)).length}
              </div>
              <div className="text-sm text-muted-foreground">Zulassungen ablaufend</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
