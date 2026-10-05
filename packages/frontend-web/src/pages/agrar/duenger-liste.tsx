/**
 * Duenger-Liste Maske
 * ListReport fuer Duenger-Uebersicht mit Filter und Suche
 */

import React, { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useQuery } from '@tanstack/react-query'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  AlertTriangle,
  CheckCircle,
  Droplets,
  Filter,
  Info,
  Plus,
  Search,
  Shield,
  XCircle,
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useTouchDevice } from '@/hooks/useTouchDevice'

interface DuengerListItem {
  id: string
  artikelnummer: string
  name: string
  typ: string
  hersteller?: string
  gefahrstoff_klasse?: string
  wassergefaehrdend?: boolean
  lagerklasse?: string
  kultur_typ?: string
  vk_preis?: number | null
  lagerbestand?: number
  dmv_nummer?: string
  eu_zulassung?: string
  ablauf_zulassung?: string | number | Date | null
  n_gehalt?: number | null
  p_gehalt?: number | null
  k_gehalt?: number | null
  [key: string]: unknown
}

interface DuengerStats {
  total_duenger?: number
  by_safety?: Record<string, number>
  stock_summary?: { total_stock?: number }
}

const TYP_OPTIONS = [
  { value: 'all-types', label: 'Alle Typen' },
  { value: 'Mineralduenger', label: 'Mineralduenger' },
  { value: 'Organischer Duenger', label: 'Organischer Duenger' },
  { value: 'Organisch-Mineralischer Duenger', label: 'Organisch-Mineralischer Duenger' },
  { value: 'Kalkduenger', label: 'Kalkduenger' },
]

const KULTUR_OPTIONS = [
  { value: 'all-kultur', label: 'Alle Kulturtypen' },
  { value: 'Getreide', label: 'Getreide' },
  { value: 'Mais', label: 'Mais' },
  { value: 'Raps', label: 'Raps' },
  { value: 'Gruenland', label: 'Gruenland' },
  { value: 'Gemuese', label: 'Gemuese' },
  { value: 'Obst', label: 'Obst' },
]

const SAFETY_OPTIONS = [
  { value: 'all-safety', label: 'Alle Sicherheitsstufen' },
  { value: 'safe', label: 'Sicher' },
  { value: 'wassergefaehrdend', label: 'Wassergefaehrdend' },
  { value: 'gefahrstoff', label: 'Gefahrstoff' },
]

export default function DuengerListePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const [typFilter, setTypFilter] = useState('all-types')
  const [herstellerFilter, setHerstellerFilter] = useState('')
  const [kulturTypFilter, setKulturTypFilter] = useState('all-kultur')
  const [safetyFilter, setSafetyFilter] = useState('all-safety')

  const { data: duengerList, isLoading } = useQuery<{ items: DuengerListItem[] }>({
    queryKey: ['duenger-list', searchTerm, typFilter, herstellerFilter, kulturTypFilter, safetyFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '100' })
      if (searchTerm) params.set('search', searchTerm)
      if (typFilter !== 'all-types') params.set('typ', typFilter)
      if (herstellerFilter) params.set('hersteller', herstellerFilter)
      if (kulturTypFilter !== 'all-kultur') params.set('kultur_typ', kulturTypFilter)
      const r = await apiClient.get<{ items: DuengerListItem[] }>(`/api/v1/agrar/duenger?${params.toString()}`)
      return r.data
    },
  })

  const { data: stats } = useQuery<DuengerStats>({
    queryKey: ['duenger-stats'],
    queryFn: async () => {
      const r = await apiClient.get<DuengerStats>('/api/v1/agrar/duenger/stats/overview')
      return r.data
    },
  })

  const filteredData = useMemo(() => {
    if (!duengerList?.items) return []

    let filtered = duengerList.items

    if (safetyFilter !== 'all-safety') {
      filtered = filtered.filter((item: DuengerListItem) => {
        if (safetyFilter === 'wassergefaehrdend') return item.wassergefaehrdend
        if (safetyFilter === 'gefahrstoff') return item.gefahrstoff_klasse
        if (safetyFilter === 'safe') return !item.wassergefaehrdend && !item.gefahrstoff_klasse
        return true
      })
    }

    return filtered
  }, [duengerList, safetyFilter])

  const getSafetyBadges = (item: DuengerListItem): JSX.Element[] => {
    const badges = []

    if (item.gefahrstoff_klasse) {
      badges.push(
        <Badge key="danger" variant="destructive" className="flex items-center gap-1">
          <Shield className="h-3 w-3" />
          {item.gefahrstoff_klasse}
        </Badge>,
      )
    }

    if (item.wassergefaehrdend) {
      badges.push(
        <Badge variant="info" key="water" className="flex items-center gap-1">
          <Droplets className="h-3 w-3" />
          WG
        </Badge>,
      )
    }

    if (item.lagerklasse) {
      badges.push(
        <Badge key="storage" variant="outline" className="flex items-center gap-1">
          <AlertTriangle className="h-3 w-3" />
          {item.lagerklasse}
        </Badge>,
      )
    }

    if (badges.length === 0) {
      badges.push(
        <Badge variant="success" key="safe">
          Sicher
        </Badge>,
      )
    }

    return badges
  }

  const getApprovalStatus = (item: DuengerListItem): JSX.Element => {
    const hasDmv = item.dmv_nummer
    const hasEu = item.eu_zulassung
    const expiryDate = item.ablauf_zulassung ? new Date(item.ablauf_zulassung) : null
    const isExpired = expiryDate ? expiryDate < new Date() : false

    if (isExpired) {
      return (
        <Badge variant="destructive" className="flex items-center gap-1">
          <XCircle className="h-3 w-3" />
          Abgelaufen
        </Badge>
      )
    }

    if (hasDmv || hasEu) {
      return (
        <Badge variant="success" className="flex items-center gap-1">
          <CheckCircle className="h-3 w-3" />
          {hasDmv && hasEu ? 'DuMV + EU' : hasDmv ? 'DuMV' : 'EU'}
        </Badge>
      )
    }

    return <Badge variant="secondary">Keine Zulassung</Badge>
  }

  const getNpkDisplay = (item: DuengerListItem): string => {
    const n = item.n_gehalt || 0
    const p = item.p_gehalt || 0
    const k = item.k_gehalt || 0

    if (n === 0 && p === 0 && k === 0) return '-'
    return `${n}-${p}-${k}`
  }

  const clearFilters = () => {
    setSearchTerm('')
    setTypFilter('all-types')
    setHerstellerFilter('')
    setKulturTypFilter('all-kultur')
    setSafetyFilter('all-safety')
  }

  return (
    <div className="mx-auto max-w-7xl space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Dünger</h1>
          <p className="text-muted-foreground">Dünger suchen und öffnen</p>
        </div>
        <Button onClick={() => navigate('/agrar/duenger-stamm')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="mr-2 h-4 w-4" />
          Neuer Dünger
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        {isLoading ? (
          [...Array(4)].map((_, index) => (
            <Card key={index}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-3/4" />
              </CardContent>
            </Card>
          ))
        ) : (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Gesamt Dünger</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_duenger || 0}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Wassergefährdend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-status-info">{stats?.by_safety?.WG || 0}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Gefahrstoffe</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-status-error">{stats?.by_safety?.['GHS+GHS'] || 0}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Gesamtlagerwert</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  EUR {(stats?.stock_summary?.total_stock || 0).toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
      ) : null}

      {!isLoading && filteredData.length === 0 ? (
        <Alert className="mb-6">
          <Info className="h-4 w-4" />
          <AlertTitle>Vorschau-Modus</AlertTitle>
          <AlertDescription>
            Es sind noch keine Dünger-Daten verfügbar. Legen Sie Dünger-Artikel an, um die Übersicht zu füllen.
          </AlertDescription>
        </Alert>
      ) : null}

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-5">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                aria-label="Suche Dünger"
                placeholder="Name, Artikelnummer oder Hersteller"
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                className="min-h-touch pl-9"
              />
            </div>
            <NativeSelect ariaLabel="Typ" value={typFilter} onValueChange={setTypFilter} options={TYP_OPTIONS} />
            <NativeSelect ariaLabel="Kulturtyp" value={kulturTypFilter} onValueChange={setKulturTypFilter} options={KULTUR_OPTIONS} />
            <NativeSelect ariaLabel="Sicherheitsstufe" value={safetyFilter} onValueChange={setSafetyFilter} options={SAFETY_OPTIONS} />
            <Button variant="outline" className="min-h-touch touch-manipulation" onClick={clearFilters}>
              Filter löschen
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Dünger-Liste</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, index) => (
                <Skeleton key={index} className="h-12 w-full" />
              ))}
            </div>
          ) : filteredData.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              <p className="mb-4">Keine Dünger-Einträge gefunden</p>
              <Button className="min-h-touch touch-manipulation" onClick={() => navigate('/agrar/duenger-stamm')}>
                <Plus className="mr-2 h-4 w-4" />
                Ersten Dünger anlegen
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Artikelnummer</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Typ</TableHead>
                    <TableHead>Hersteller</TableHead>
                    <TableHead>NPK</TableHead>
                    <TableHead>Zulassungen</TableHead>
                    <TableHead>Sicherheit</TableHead>
                    <TableHead>Lagerbestand</TableHead>
                    <TableHead>VK-Preis</TableHead>
                    <TableHead>Aktionen</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredData.map(item => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.artikelnummer}</TableCell>
                      <TableCell>
                        <button
                          type="button"
                          className="min-h-11 font-medium text-primary touch-manipulation"
                          onClick={() => navigate(`/agrar/duenger-stamm/${item.id}`)}
                        >
                          {item.name}
                        </button>
                      </TableCell>
                      <TableCell>{item.typ}</TableCell>
                      <TableCell>{item.hersteller}</TableCell>
                      <TableCell className="font-mono">{getNpkDisplay(item)}</TableCell>
                      <TableCell>{getApprovalStatus(item)}</TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">{getSafetyBadges(item)}</div>
                      </TableCell>
                      <TableCell className="text-right">
                        {item.lagerbestand?.toLocaleString('de-DE', { minimumFractionDigits: 2 }) || '0.00'} kg
                      </TableCell>
                      <TableCell>{item.vk_preis ? `EUR ${item.vk_preis.toFixed(2)}` : '-'}</TableCell>
                      <TableCell>
                        <div className="flex flex-col gap-2 sm:flex-row">
                          <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => navigate(`/agrar/duenger-stamm/${item.id}`)}>
                            Anzeigen
                          </Button>
                          <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => navigate(`/agrar/duenger-stamm/${item.id}`)}>
                            Bearbeiten
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
