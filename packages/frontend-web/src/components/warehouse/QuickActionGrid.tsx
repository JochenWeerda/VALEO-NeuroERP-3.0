/**
 * Quick Action Grid
 *
 * Große, touch-optimierte Buttons für häufige Lager-Aktionen
 * Optimiert für Handschuh-Bedienung und schnelle Erkennung
 */

import { ReactNode } from 'react'
import { clsx } from 'clsx'
import { Link } from '@/app/routing/typed-router'
import {
  PackagePlus,
  PackageMinus,
  ClipboardList,
  Package,
  Search,
  ArrowLeftRight,
  Truck,
  Scan,
  MapPin,
} from 'lucide-react'

export interface QuickAction {
  id: string
  label: string
  sublabel?: string
  icon: ReactNode
  color: string
  href?: string
  onClick?: () => void
  badge?: string | number
}

interface QuickActionGridProps {
  actions: QuickAction[]
  columns?: 2 | 3
  className?: string
}

// Standard-Aktionen für Warehouse
export const warehouseActions: QuickAction[] = [
  {
    id: 'eingang',
    label: 'Wareneingang',
    sublabel: 'Artikel einbuchen',
    icon: <PackagePlus className="h-12 w-12" />,
    color: 'bg-emerald-600 hover:bg-emerald-700',
    href: '/lager/einlagerung',
  },
  {
    id: 'ausgang',
    label: 'Warenausgang',
    sublabel: 'Artikel ausbuchen',
    icon: <PackageMinus className="h-12 w-12" />,
    color: 'bg-orange-600 hover:bg-orange-700',
    href: '/lager/auslagerung',
  },
  {
    id: 'umlagerung',
    label: 'Umlagerung',
    sublabel: 'Lagerplatz wechseln',
    icon: <ArrowLeftRight className="h-12 w-12" />,
    color: 'bg-cyan-600 hover:bg-cyan-700',
    href: '/lager/umlagerung',
  },
  {
    id: 'bestand',
    label: 'Bestand',
    sublabel: 'Übersicht',
    icon: <Package className="h-12 w-12" />,
    color: 'bg-blue-600 hover:bg-blue-700',
    href: '/lager/bestandsuebersicht',
  },
  {
    id: 'inventur',
    label: 'Inventur',
    sublabel: 'Zählung',
    icon: <ClipboardList className="h-12 w-12" />,
    color: 'bg-purple-600 hover:bg-purple-700',
    href: '/lager/inventur',
  },
  {
    id: 'suche',
    label: 'Suche',
    sublabel: 'Artikel finden',
    icon: <Search className="h-12 w-12" />,
    color: 'bg-neutral-600 hover:bg-neutral-700',
    href: '/lager/suche',
  },
]

// Erweiterte Aktionen
export const extendedWarehouseActions: QuickAction[] = [
  ...warehouseActions,
  {
    id: 'scan',
    label: 'Schnellscan',
    sublabel: 'Barcode prüfen',
    icon: <Scan className="h-12 w-12" />,
    color: 'bg-amber-600 hover:bg-amber-700',
    href: '/lager/scan',
  },
  {
    id: 'lagerorte',
    label: 'Lagerorte',
    sublabel: 'Verwaltung',
    icon: <MapPin className="h-12 w-12" />,
    color: 'bg-rose-600 hover:bg-rose-700',
    href: '/lager/lagerorte-liste',
  },
  {
    id: 'kommission',
    label: 'Kommission',
    sublabel: 'Aufträge',
    icon: <Truck className="h-12 w-12" />,
    color: 'bg-indigo-600 hover:bg-indigo-700',
    href: '/lager/kommissionierung',
  },
]

export function QuickActionGrid({
  actions,
  columns = 2,
  className,
}: QuickActionGridProps) {
  const gridCols = columns === 3 ? 'grid-cols-3' : 'grid-cols-2'

  return (
    <div className={clsx('grid gap-3', gridCols, className)}>
      {actions.map((action) => {
        const content = (
          <>
            {/* Badge */}
            {action.badge && (
              <span className="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full min-w-[24px] text-center">
                {action.badge}
              </span>
            )}

            {/* Icon */}
            <div className="mb-2">{action.icon}</div>

            {/* Label */}
            <span className="text-lg font-bold">{action.label}</span>

            {/* Sublabel */}
            {action.sublabel && (
              <span className="text-sm opacity-80">{action.sublabel}</span>
            )}
          </>
        )

        const baseStyles = clsx(
          'relative flex flex-col items-center justify-center',
          'min-h-[140px] p-4 rounded-xl',
          'text-white text-center',
          'active:scale-95 transition-transform',
          'focus:outline-hidden focus:ring-4 focus:ring-white/50',
          action.color
        )

        if (action.href) {
          return (
            <Link key={action.id} to={action.href} className={baseStyles}>
              {content}
            </Link>
          )
        }

        return (
          <button
            key={action.id}
            onClick={action.onClick}
            className={baseStyles}
          >
            {content}
          </button>
        )
      })}
    </div>
  )
}

/**
 * Kompakte Variante für kleinere Bereiche
 */
export function QuickActionStrip({
  actions,
  className,
}: {
  actions: QuickAction[]
  className?: string
}) {
  return (
    <div className={clsx('flex gap-2 overflow-x-auto pb-2', className)}>
      {actions.map((action) => {
        const content = (
          <>
            {action.icon}
            <span className="text-sm font-medium">{action.label}</span>
          </>
        )

        const baseStyles = clsx(
          'shrink-0 flex flex-col items-center justify-center gap-1',
          'min-h-[80px] min-w-[90px] p-3 rounded-lg',
          'text-white',
          'active:scale-95 transition-transform',
          action.color
        )

        if (action.href) {
          return (
            <Link key={action.id} to={action.href} className={baseStyles}>
              {content}
            </Link>
          )
        }

        return (
          <button
            key={action.id}
            onClick={action.onClick}
            className={baseStyles}
          >
            {content}
          </button>
        )
      })}
    </div>
  )
}
