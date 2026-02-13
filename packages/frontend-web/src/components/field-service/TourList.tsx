/**
 * Tour List
 *
 * Liste der Kundenbesuche für den Tag
 * Sortierung nach Distanz, Uhrzeit oder Priorität
 * Metro Design mit TanStack Query
 */

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { cn } from '@/lib/utils'
import {
  MapPin,
  Clock,
  ArrowUpDown,
  Filter,
  Navigation2,
  CheckCircle2,
  AlertCircle,
  Loader2,
  RefreshCw,
} from 'lucide-react'
import { LocationCard, CustomerLocation } from './LocationCard'
import {
  useGeolocation,
  calculateDistance,
} from '@/hooks/useGeolocation'

type SortMode = 'distance' | 'time' | 'priority' | 'name'
type FilterStatus = 'all' | 'pending' | 'completed'

interface TourListProps {
  date?: Date
  onCustomerClick?: (customer: CustomerLocation) => void
  className?: string
}

// Mock-API Funktion (später durch echte API ersetzen)
async function fetchTourCustomers(date: Date): Promise<CustomerLocation[]> {
  // Simuliere API-Aufruf
  await new Promise(resolve => setTimeout(resolve, 500))

  return [
    {
      id: '1',
      name: 'Landwirtschaft Müller GmbH',
      address: 'Hauptstraße 15',
      city: 'Neustadt',
      postalCode: '12345',
      latitude: 51.0504,
      longitude: 13.7373,
      phone: '+49 123 456789',
      contactPerson: 'Hans Müller',
      scheduledTime: '08:30',
      status: 'completed',
      priority: 'normal',
    },
    {
      id: '2',
      name: 'Agrar Schneider',
      address: 'Feldweg 7',
      city: 'Altdorf',
      postalCode: '12346',
      latitude: 51.0604,
      longitude: 13.7473,
      phone: '+49 123 456790',
      contactPerson: 'Maria Schneider',
      scheduledTime: '10:00',
      status: 'in_progress',
      priority: 'high',
    },
    {
      id: '3',
      name: 'Biolandhof Weber',
      address: 'Am Waldrand 22',
      city: 'Grünfeld',
      postalCode: '12347',
      latitude: 51.0404,
      longitude: 13.7273,
      phone: '+49 123 456791',
      contactPerson: 'Thomas Weber',
      scheduledTime: '13:30',
      status: 'pending',
      priority: 'urgent',
    },
    {
      id: '4',
      name: 'Genossenschaft Blumental',
      address: 'Industriestraße 8',
      city: 'Blumental',
      postalCode: '12348',
      latitude: 51.0704,
      longitude: 13.7573,
      contactPerson: 'Lisa Fischer',
      scheduledTime: '15:00',
      status: 'pending',
      priority: 'normal',
    },
  ]
}

export function TourList({
  date = new Date(),
  onCustomerClick,
  className,
}: TourListProps) {
  const [sortMode, setSortMode] = useState<SortMode>('time')
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all')
  const { position } = useGeolocation({ continuous: true })

  // TanStack Query für Tour-Daten
  const {
    data: customers = [],
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['tour-customers', date.toISOString().split('T')[0]],
    queryFn: () => fetchTourCustomers(date),
    staleTime: 5 * 60 * 1000, // 5 Minuten
    refetchOnWindowFocus: true,
  })

  // Kunden mit Distanz anreichern
  const customersWithDistance = useMemo(() => {
    return customers.map(customer => ({
      ...customer,
      distance: position
        ? calculateDistance(
            position.latitude,
            position.longitude,
            customer.latitude,
            customer.longitude
          )
        : null,
    }))
  }, [customers, position])

  // Filtern
  const filteredCustomers = useMemo(() => {
    if (filterStatus === 'all') return customersWithDistance
    if (filterStatus === 'completed') {
      return customersWithDistance.filter(c => c.status === 'completed')
    }
    return customersWithDistance.filter(c => c.status !== 'completed')
  }, [customersWithDistance, filterStatus])

  // Sortieren
  const sortedCustomers = useMemo(() => {
    const sorted = [...filteredCustomers]

    switch (sortMode) {
      case 'distance':
        return sorted.sort((a, b) => (a.distance ?? Infinity) - (b.distance ?? Infinity))
      case 'time':
        return sorted.sort((a, b) => {
          if (!a.scheduledTime) return 1
          if (!b.scheduledTime) return -1
          return a.scheduledTime.localeCompare(b.scheduledTime)
        })
      case 'priority':
        const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 }
        return sorted.sort((a, b) => {
          const pA = priorityOrder[a.priority ?? 'normal']
          const pB = priorityOrder[b.priority ?? 'normal']
          return pA - pB
        })
      case 'name':
        return sorted.sort((a, b) => a.name.localeCompare(b.name))
      default:
        return sorted
    }
  }, [filteredCustomers, sortMode])

  // Statistiken
  const stats = useMemo(() => {
    const total = customers.length
    const completed = customers.filter(c => c.status === 'completed').length
    const pending = total - completed
    return { total, completed, pending }
  }, [customers])

  if (isLoading) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12', className)}>
        <Loader2 className="h-12 w-12 text-primary animate-spin" />
        <p className="mt-4 text-muted-foreground">Tour wird geladen...</p>
      </div>
    )
  }

  if (isError) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12', className)}>
        <AlertCircle className="h-12 w-12 text-destructive" />
        <p className="mt-4 text-lg font-medium">Fehler beim Laden</p>
        <p className="text-sm text-muted-foreground">
          {error instanceof Error ? error.message : 'Unbekannter Fehler'}
        </p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg"
        >
          Erneut versuchen
        </button>
      </div>
    )
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header mit Statistiken */}
      <div className="bg-card rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold">Tagestour</h2>
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="p-2 rounded-lg hover:bg-muted active:bg-muted/80 transition-colors"
          >
            <RefreshCw className={cn('h-5 w-5', isFetching && 'animate-spin')} />
          </button>
        </div>

        {/* Statistik-Badges */}
        <div className="flex gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-muted rounded-lg">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">{stats.total}</span>
            <span className="text-sm text-muted-foreground">Gesamt</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-100 text-emerald-700 rounded-lg">
            <CheckCircle2 className="h-4 w-4" />
            <span className="font-medium">{stats.completed}</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-100 text-amber-700 rounded-lg">
            <Clock className="h-4 w-4" />
            <span className="font-medium">{stats.pending}</span>
          </div>
        </div>
      </div>

      {/* Filter & Sort */}
      <div className="flex gap-2">
        {/* Sort Buttons */}
        <div className="flex-1 flex gap-1 bg-muted/50 p-1 rounded-lg">
          {([
            { mode: 'time', icon: Clock, label: 'Zeit' },
            { mode: 'distance', icon: Navigation2, label: 'Nähe' },
            { mode: 'priority', icon: ArrowUpDown, label: 'Prio' },
          ] as const).map(({ mode, icon: Icon, label }) => (
            <button
              key={mode}
              onClick={() => setSortMode(mode)}
              className={cn(
                'flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-md text-sm font-medium transition-colors',
                sortMode === mode
                  ? 'bg-background shadow-sm text-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              <Icon className="h-4 w-4" />
              <span className="hidden sm:inline">{label}</span>
            </button>
          ))}
        </div>

        {/* Filter Dropdown */}
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as FilterStatus)}
          className="px-3 py-2 bg-card border border-border rounded-lg text-sm font-medium"
        >
          <option value="all">Alle</option>
          <option value="pending">Offen</option>
          <option value="completed">Erledigt</option>
        </select>
      </div>

      {/* Kundenliste */}
      <div className="space-y-3">
        {sortedCustomers.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <MapPin className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>Keine Kunden gefunden</p>
          </div>
        ) : (
          sortedCustomers.map((customer, index) => (
            <div key={customer.id} className="relative">
              {/* Verbindungslinie */}
              {index < sortedCustomers.length - 1 && sortMode === 'time' && (
                <div className="absolute left-6 top-full h-3 w-0.5 bg-border" />
              )}

              <LocationCard
                customer={customer}
                onClick={() => onCustomerClick?.(customer)}
                showDistance={!!position}
              />
            </div>
          ))
        )}
      </div>
    </div>
  )
}
