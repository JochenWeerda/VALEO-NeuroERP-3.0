/**
 * Warehouse Layout
 *
 * Wrapper-Komponente für Warehouse-Seiten mit:
 * - High-Contrast Theme
 * - Große Touch-Targets
 * - Scanner-Integration
 * - Vereinfachte Navigation
 */

import { ReactNode } from 'react'
import { clsx } from 'clsx'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Home,
  Package,
  PackagePlus,
  PackageMinus,
  ClipboardList,
  Settings,
  LogOut,
  ScanLine,
} from 'lucide-react'
import { useForceWarehouseTheme } from '@/hooks/useWarehouseTheme'

interface WarehouseLayoutProps {
  children: ReactNode
  title: string
  subtitle?: string
  showBack?: boolean
  showScanner?: boolean
  onScan?: (barcode: string) => void
}

interface NavItem {
  path: string
  label: string
  icon: ReactNode
  color: string
}

const navItems: NavItem[] = [
  {
    path: '/lager',
    label: 'Start',
    icon: <Home className="h-8 w-8" />,
    color: 'bg-neutral-700',
  },
  {
    path: '/lager/einlagerung',
    label: 'Eingang',
    icon: <PackagePlus className="h-8 w-8" />,
    color: 'bg-emerald-600',
  },
  {
    path: '/lager/auslagerung',
    label: 'Ausgang',
    icon: <PackageMinus className="h-8 w-8" />,
    color: 'bg-orange-600',
  },
  {
    path: '/lager/bestandsuebersicht',
    label: 'Bestand',
    icon: <Package className="h-8 w-8" />,
    color: 'bg-blue-600',
  },
  {
    path: '/lager/inventur',
    label: 'Inventur',
    icon: <ClipboardList className="h-8 w-8" />,
    color: 'bg-purple-600',
  },
]

export function WarehouseLayout({
  children,
  title,
  subtitle,
  showBack = false,
  showScanner = false,
  onScan,
}: WarehouseLayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()

  // Aktiviere Warehouse Theme
  useForceWarehouseTheme()

  // Scanner-Anzeige im Header
  const handleScanClick = () => {
    if (onScan) {
      // Fokus auf verstecktes Input für Scanner
      const scanInput = document.getElementById('warehouse-scan-input')
      scanInput?.focus()
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Header - kompakt aber touch-friendly */}
      <header className="bg-card border-b-2 border-primary px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          {showBack && (
            <button
              onClick={() => navigate(-1)}
              className="flex items-center justify-center h-14 w-14 rounded-lg bg-neutral-700 text-white active:bg-neutral-600"
              aria-label="Zurück"
            >
              <ArrowLeft className="h-8 w-8" />
            </button>
          )}

          <div>
            <h1 className="text-2xl font-bold text-foreground">{title}</h1>
            {subtitle && (
              <p className="text-sm text-muted-foreground">{subtitle}</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {showScanner && (
            <button
              onClick={handleScanClick}
              className="flex items-center justify-center h-14 w-14 rounded-lg bg-primary text-primary-foreground active:opacity-80"
              aria-label="Scanner"
            >
              <ScanLine className="h-8 w-8" />
            </button>
          )}

          <Link
            to="/einstellungen"
            className="flex items-center justify-center h-14 w-14 rounded-lg bg-neutral-700 text-white active:bg-neutral-600"
            aria-label="Einstellungen"
          >
            <Settings className="h-7 w-7" />
          </Link>

          <button
            onClick={() => navigate('/logout')}
            className="flex items-center justify-center h-14 w-14 rounded-lg bg-red-700 text-white active:bg-red-600"
            aria-label="Abmelden"
          >
            <LogOut className="h-7 w-7" />
          </button>
        </div>
      </header>

      {/* Hauptinhalt */}
      <main className="flex-1 p-4 overflow-auto">
        {children}
      </main>

      {/* Bottom Navigation - große Touch-Buttons */}
      <nav className="bg-card border-t-2 border-border px-2 py-2 safe-bottom">
        <div className="flex justify-around gap-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={clsx(
                  'flex flex-col items-center justify-center min-h-[70px] min-w-[70px] px-3 py-2 rounded-lg transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : `${item.color} text-white active:opacity-80`
                )}
              >
                {item.icon}
                <span className="text-xs font-medium mt-1">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Verstecktes Input für Scanner */}
      {showScanner && onScan && (
        <input
          id="warehouse-scan-input"
          type="text"
          className="absolute -left-[9999px]"
          autoComplete="off"
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              const value = (e.target as HTMLInputElement).value
              if (value) {
                onScan(value)
                ;(e.target as HTMLInputElement).value = ''
              }
            }
          }}
        />
      )}
    </div>
  )
}
