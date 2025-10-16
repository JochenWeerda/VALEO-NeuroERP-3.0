import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { AlertTriangle, Plus, Filter, Eye, Edit, Trash2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

type Duenger = {
  id: string
  artikelnummer: string
  name: string
  typ: string
  hersteller: string
  n_gehalt: number
  p_gehalt: number
  k_gehalt: number
  s_gehalt: number
  mg_gehalt: number
  dmv_nummer: string
  eu_zulassung: string
  ablauf_zulassung: string
  gefahrstoff_klasse: string
  wassergefaehrdend: boolean
  lagerklasse: string
  kultur_typ: string
  dosierung_min: number
  dosierung_max: number
  zeitpunkt: string
  ek_preis: number
  vk_preis: number
  lagerbestand: number
  ist_aktiv: boolean
  ausgangsstoff_explosivstoffe: boolean
  erklaerung_landwirt_erforderlich: boolean
  erklaerung_landwirt_status: string | null
}

export default function DuengerListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const [duenger, setDuenger] = useState<Duenger[]>([
    {
      id: 'DUE-001',
      artikelnummer: 'DUE-001',
      name: 'NPK 15-15-15 Universal',
      typ: 'Mineraldünger',
      hersteller: 'BASF',
      n_gehalt: 15.0,
      p_gehalt: 15.0,
      k_gehalt: 15.0,
      s_gehalt: 8.0,
      mg_gehalt: 2.0,
      dmv_nummer: 'DMV-2024-001',
      eu_zulassung: 'EU-2024-001',
      ablauf_zulassung: '2026-12-31',
      gefahrstoff_klasse: 'Nicht gefährlich',
      wassergefaehrdend: false,
      lagerklasse: 'Nicht wassergefährdend',
      kultur_typ: 'Getreide',
      dosierung_min: 200,
      dosierung_max: 400,
      zeitpunkt: 'Herbst',
      ek_preis: 450.00,
      vk_preis: 520.00,
      lagerbestand: 2500,
      ist_aktiv: true,
      ausgangsstoff_explosivstoffe: false,
      erklaerung_landwirt_erforderlich: false,
      erklaerung_landwirt_status: null
    },
    {
      id: 'DUE-002',
      artikelnummer: 'DUE-002',
      name: 'Kalkammonsalpeter 27',
      typ: 'Mineraldünger',
      hersteller: 'Yara',
      n_gehalt: 27.0,
      p_gehalt: 0.0,
      k_gehalt: 0.0,
      s_gehalt: 0.0,
      mg_gehalt: 0.0,
      dmv_nummer: 'DMV-2024-002',
      eu_zulassung: 'EU-2024-002',
      ablauf_zulassung: '2027-06-30',
      gefahrstoff_klasse: 'Nicht gefährlich',
      wassergefaehrdend: false,
      lagerklasse: 'Nicht wassergefährdend',
      kultur_typ: 'Mais',
      dosierung_min: 150,
      dosierung_max: 300,
      zeitpunkt: 'Frühjahr',
      ek_preis: 380.00,
      vk_preis: 445.00,
      lagerbestand: 1800,
      ist_aktiv: true,
      ausgangsstoff_explosivstoffe: true,
      erklaerung_landwirt_erforderlich: true,
      erklaerung_landwirt_status: 'ausstehend'
    },
    {
      id: 'DUE-003',
      artikelnummer: 'DUE-003',
      name: 'Schwefelsaures Ammoniak',
      typ: 'Mineraldünger',
      hersteller: 'K+S',
      n_gehalt: 21.0,
      p_gehalt: 0.0,
      k_gehalt: 0.0,
      s_gehalt: 24.0,
      mg_gehalt: 0.0,
      dmv_nummer: 'DMV-2024-003',
      eu_zulassung: 'EU-2024-003',
      ablauf_zulassung: '2026-08-15',
      gefahrstoff_klasse: 'Reizend',
      wassergefaehrdend: true,
      lagerklasse: 'WGK 1',
      kultur_typ: 'Raps',
      dosierung_min: 100,
      dosierung_max: 200,
      zeitpunkt: 'Herbst',
      ek_preis: 295.00,
      vk_preis: 355.00,
      lagerbestand: 950,
      ist_aktiv: true,
      ausgangsstoff_explosivstoffe: true,
      erklaerung_landwirt_erforderlich: true,
      erklaerung_landwirt_status: 'geprueft'
    }
  ])

  const [filteredDuenger, setFilteredDuenger] = useState<Duenger[]>(duenger)
  const [searchTerm, setSearchTerm] = useState('')
  const [typFilter, setTypFilter] = useState('')
  const [herstellerFilter, setHerstellerFilter] = useState('')
  const [erklaerungFilter, setErklaerungFilter] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    filterDuenger()
  }, [duenger, searchTerm, typFilter, herstellerFilter, erklaerungFilter])

  const filterDuenger = () => {
    let filtered = duenger

    if (searchTerm) {
      filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        d.artikelnummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
        d.hersteller.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (typFilter) {
      filtered = filtered.filter(d => d.typ === typFilter)
    }

    if (herstellerFilter) {
      filtered = filtered.filter(d => d.hersteller === herstellerFilter)
    }

    if (erklaerungFilter) {
      if (erklaerungFilter === 'erforderlich') {
        filtered = filtered.filter(d => d.erklaerung_landwirt_erforderlich)
      } else if (erklaerungFilter === 'ausstehend') {
        filtered = filtered.filter(d => d.erklaerung_landwirt_status === 'ausstehend')
      } else if (erklaerungFilter === 'geprueft') {
        filtered = filtered.filter(d => d.erklaerung_landwirt_status === 'geprueft')
      }
    }

    setFilteredDuenger(filtered)
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Dünger wirklich löschen?')) return

    setIsLoading(true)
    try {
      // API call to delete Dünger
      // await fetch(`/api/v1/agrar/duenger/${id}`, { method: 'DELETE' })

      setDuenger(prev => prev.filter(d => d.id !== id))

      toast({
        title: "Gelöscht",
        description: "Dünger wurde erfolgreich gelöscht.",
      })
    } catch (error) {
      toast({
        title: "Fehler",
        description: "Fehler beim Löschen des Düngers.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getErklaerungBadgeVariant = (status: string | null) => {
    switch (status) {
      case 'geprueft': return 'default'
      case 'eingegangen': return 'secondary'
      case 'abgelehnt': return 'destructive'
      default: return 'outline'
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
              <Select value={typFilter} onValueChange={setTypFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Typ" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Alle Typen</SelectItem>
                  {uniqueTypes.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Select value={herstellerFilter} onValueChange={setHerstellerFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Hersteller" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Alle Hersteller</SelectItem>
                  {uniqueHersteller.map(hersteller => (
                    <SelectItem key={hersteller} value={hersteller}>{hersteller}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Select value={erklaerungFilter} onValueChange={setErklaerungFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Erklärung" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Alle</SelectItem>
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
              {filteredDuenger.map((d) => (
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
                        disabled={isLoading}
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
