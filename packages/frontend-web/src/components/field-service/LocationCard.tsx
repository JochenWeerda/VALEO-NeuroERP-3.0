/**
 * Location Card
 *
 * Zeigt Kundenstandort mit Distanz und Navigation
 * Metro Design, Touch-optimiert für Tablets
 */

import { useMemo } from 'react'
import { cn } from '@/lib/utils'
import {
  MapPin,
  Navigation,
  Phone,
  Clock,
  ChevronRight,
  Building2,
  User,
} from 'lucide-react'
import {
  useGeolocation,
  calculateDistance,
  formatDistance,
  estimateTravelTime,
  formatTravelTime,
  openNavigation,
} from '@/hooks/useGeolocation'

export interface CustomerLocation {
  id: string
  name: string
  address: string
  city: string
  postalCode: string
  latitude: number
  longitude: number
  phone?: string
  contactPerson?: string
  scheduledTime?: string
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority?: 'low' | 'normal' | 'high' | 'urgent'
}

interface LocationCardProps {
  customer: CustomerLocation
  onClick?: () => void
  onNavigate?: () => void
  onCall?: () => void
  showDistance?: boolean
  compact?: boolean
  className?: string
}

export function LocationCard({
  customer,
  onClick,
  onNavigate,
  onCall,
  showDistance = true,
  compact = false,
  className,
}: LocationCardProps) {
  const { position } = useGeolocation({ continuous: false })

  // Distanz berechnen
  const distanceInfo = useMemo(() => {
    if (!position || !showDistance) return null

    const meters = calculateDistance(
      position.latitude,
      position.longitude,
      customer.latitude,
      customer.longitude
    )
    const minutes = estimateTravelTime(meters)

    return {
      distance: formatDistance(meters),
      travelTime: formatTravelTime(minutes),
      meters,
    }
  }, [position, customer.latitude, customer.longitude, showDistance])

  // Status-Farben (Metro Style)
  const statusStyles = {
    pending: 'border-l-amber-500 bg-amber-500/5',
    in_progress: 'border-l-blue-500 bg-blue-500/5',
    completed: 'border-l-emerald-500 bg-emerald-500/5',
    cancelled: 'border-l-neutral-400 bg-neutral-100',
  }

  const priorityBadge = {
    low: null,
    normal: null,
    high: 'bg-amber-500 text-white',
    urgent: 'bg-red-500 text-white animate-pulse',
  }

  const handleNavigate = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (onNavigate) {
      onNavigate()
    } else {
      openNavigation(customer.latitude, customer.longitude)
    }
  }

  const handleCall = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (onCall) {
      onCall()
    } else if (customer.phone) {
      window.location.href = `tel:${customer.phone}`
    }
  }

  if (compact) {
    return (
      <button
        onClick={onClick}
        className={cn(
          'w-full flex items-center gap-3 p-3 rounded-lg border-l-4 text-left',
          'bg-card hover:bg-muted/50 active:bg-muted transition-colors',
          customer.status && statusStyles[customer.status],
          className
        )}
      >
        <MapPin className="h-5 w-5 text-muted-foreground shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">{customer.name}</p>
          <p className="text-sm text-muted-foreground truncate">
            {customer.city}
          </p>
        </div>
        {distanceInfo && (
          <span className="text-sm font-medium text-primary">
            {distanceInfo.distance}
          </span>
        )}
        <ChevronRight className="h-5 w-5 text-muted-foreground" />
      </button>
    )
  }

  return (
    <div
      className={cn(
        'rounded-xl border-l-4 overflow-hidden',
        'bg-card shadow-sm',
        customer.status && statusStyles[customer.status],
        onClick && 'cursor-pointer hover:shadow-md transition-shadow',
        className
      )}
      onClick={onClick}
    >
      {/* Header */}
      <div className="p-4 pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {/* Priorität Badge */}
            {customer.priority && priorityBadge[customer.priority] && (
              <span
                className={cn(
                  'inline-block px-2 py-0.5 text-xs font-bold rounded mb-2',
                  priorityBadge[customer.priority]
                )}
              >
                {customer.priority === 'urgent' ? 'DRINGEND' : 'PRIORITÄT'}
              </span>
            )}

            {/* Kundenname */}
            <h3 className="text-lg font-bold leading-tight">{customer.name}</h3>

            {/* Ansprechpartner */}
            {customer.contactPerson && (
              <div className="flex items-center gap-1.5 mt-1 text-sm text-muted-foreground">
                <User className="h-3.5 w-3.5" />
                <span>{customer.contactPerson}</span>
              </div>
            )}
          </div>

          {/* Termin */}
          {customer.scheduledTime && (
            <div className="text-right shrink-0">
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span className="font-medium">{customer.scheduledTime}</span>
              </div>
            </div>
          )}
        </div>

        {/* Adresse */}
        <div className="flex items-start gap-2 mt-3 text-sm">
          <Building2 className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
          <div>
            <p>{customer.address}</p>
            <p className="text-muted-foreground">
              {customer.postalCode} {customer.city}
            </p>
          </div>
        </div>
      </div>

      {/* Distanz-Leiste */}
      {distanceInfo && (
        <div className="px-4 py-2 bg-muted/50 border-t border-border flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm">
            <span className="font-medium">{distanceInfo.distance}</span>
            <span className="text-muted-foreground">
              ca. {distanceInfo.travelTime}
            </span>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex border-t border-border">
        <button
          onClick={handleNavigate}
          className="flex-1 flex items-center justify-center gap-2 py-3.5 text-primary font-medium hover:bg-primary/5 active:bg-primary/10 transition-colors"
        >
          <Navigation className="h-5 w-5" />
          <span>Navigation</span>
        </button>

        {customer.phone && (
          <>
            <div className="w-px bg-border" />
            <button
              onClick={handleCall}
              className="flex-1 flex items-center justify-center gap-2 py-3.5 text-primary font-medium hover:bg-primary/5 active:bg-primary/10 transition-colors"
            >
              <Phone className="h-5 w-5" />
              <span>Anrufen</span>
            </button>
          </>
        )}
      </div>
    </div>
  )
}
