import { useEffect, useRef, useState } from 'react'
import { clsx } from 'clsx'
import { Outlet, Link, useLocation, useNavigate } from '@/app/routing/typed-router'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import {
  Home,
  ShoppingCart,
  FileText,
  Receipt,
  Download,
  Leaf,
  Menu,
  LogOut,
  Bell,
  ChevronRight,
  Package,
  ClipboardList,
  Award,
  FileSpreadsheet,
  BarChart3,
  Calculator,
  ArrowLeft,
  X,
  type LucideIcon,
} from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { isTerraAgrarPortalPath } from '@/lib/portal-theme'
import { INNENDIENST_ROLLEN, kontoDarf, usePortalKonto } from '@/lib/portal-konto'
import { PortalKontoGate, PortalKontoWahl } from '@/components/portal/PortalKontoWahl'

interface NavItem {
  label: string
  path: string
  icon: LucideIcon
  badge?: string | number
  /** Portalrecht des aktiven Kontos (app/auth/portal_kunde.PORTAL_RECHTE); ohne: fuer alle. */
  recht?: string
}

const customerNavItems: NavItem[] = [
  { label: 'Uebersicht', path: '/portal', icon: Home, recht: 'uebersicht' },
  { label: 'Bestellportal', path: '/portal/shop', icon: ShoppingCart, badge: 'NEU', recht: 'verkauf' },
  { label: 'Meine Bestellungen', path: '/portal/bestellungen', icon: Package, recht: 'verkauf' },
  { label: 'Anfragen', path: '/portal/anfragen', icon: ClipboardList, recht: 'verkauf' },
  { label: 'Vertraege', path: '/portal/vertraege', icon: FileText, recht: 'kontrakte' },
  { label: 'Rechnungen', path: '/portal/rechnungen', icon: Receipt, recht: 'finanzen' },
  { label: 'Dokumente', path: '/portal/dokumente', icon: Download, recht: 'finanzen' },
  { label: 'Zertifikate', path: '/portal/zertifikate', icon: Award, recht: 'auswertungen' },
  { label: 'Ackerschlagkartei', path: '/portal/feldbuch', icon: Leaf, recht: 'feldbuch_lesen' },
  { label: 'Naehrstoffbilanzen', path: '/portal/naehrstoffbilanzen', icon: BarChart3, recht: 'auswertungen' },
  { label: 'Rationsoptimierung', path: '/portal/rationsoptimierung', icon: Calculator, recht: 'auswertungen' },
]

function PortalNavLink({
  item,
  active,
  onNavigate,
  compact = false,
  terra = false,
}: {
  item: NavItem
  active: boolean
  onNavigate?: () => void
  compact?: boolean
  terra?: boolean
}) {
  const Icon = item.icon

  return (
    <Link
      to={item.path}
      onClick={onNavigate}
      className={clsx(
        'flex items-center justify-between rounded-lg px-4 py-3 text-sm font-medium transition-colors',
        terra
          ? active
            ? 'bg-primary/10 text-primary'
            : 'text-muted-foreground hover:bg-muted hover:text-foreground'
          : active
            ? 'bg-emerald-100 text-emerald-900'
            : 'text-gray-600 hover:bg-gray-100',
        compact && 'px-3 py-2',
      )}
    >
      <span className="flex items-center gap-3">
        <Icon className="h-5 w-5" />
        <span>{item.label}</span>
      </span>
      <span className="flex items-center gap-2">
        {item.badge && (
          <Badge variant="secondary" className="text-xs">
            {item.badge}
          </Badge>
        )}
        {!compact && <ChevronRight className="h-4 w-4 text-muted-foreground" />}
      </span>
    </Link>
  )
}

export default function CustomerPortalLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { hasRole } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [moreMenuOpen, setMoreMenuOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [notifications] = useState(3)
  const moreMenuRef = useRef<HTMLDivElement>(null)
  const userMenuRef = useRef<HTMLDivElement>(null)

  const isAnwender = hasRole('admin') || hasRole('user') || hasRole('manager')
  const isTerraAgrar = isTerraAgrarPortalPath(location.pathname)
  // Kunde und Rechte kommen aus der Anmeldung und der gewaehlten Zuordnung (PORTAL-CONTEXT-001), kein Demo-Kunde.
  const konto = usePortalKonto((state) => state.aktiv)
  const navItems = customerNavItems.filter((item) => kontoDarf(konto, item.recht))
  const kontoName = konto?.name ?? 'Kundenportal'
  const kontoKuerzel = kontoName.split(/\s+/).map((teil) => teil[0] ?? '').join('').slice(0, 2).toUpperCase()

  const navActiveClass = isTerraAgrar
    ? 'bg-primary/10 text-primary'
    : 'bg-emerald-100 text-emerald-900'
  const navInactiveClass = isTerraAgrar
    ? 'text-muted-foreground hover:bg-muted hover:text-foreground'
    : 'text-gray-600 hover:bg-gray-100'

  const isActivePath = (path: string) => {
    if (path === '/portal') {
      return location.pathname === '/portal'
    }
    return location.pathname.startsWith(path)
  }

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      const target = event.target as Node
      if (moreMenuRef.current && !moreMenuRef.current.contains(target)) {
        setMoreMenuOpen(false)
      }
      if (userMenuRef.current && !userMenuRef.current.contains(target)) {
        setUserMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  const handleLogout = () => {
    navigate('/auth/login')
  }

  return (
    <div
      className={clsx(
        'min-h-screen',
        isTerraAgrar
          ? 'theme-terra bg-background text-foreground'
          : 'bg-linear-to-br from-emerald-50 via-white to-amber-50',
      )}
    >
      <header
        className={clsx(
          'sticky top-0 z-50 border-b backdrop-blur-md',
          isTerraAgrar ? 'border-border bg-card/90' : 'bg-white/80',
        )}
      >
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setMobileMenuOpen(true)}
            >
              <Menu className="h-6 w-6" />
            </Button>

            <Link to="/portal" className="flex items-center gap-2">
              <div
                className={clsx(
                  'flex h-10 w-10 items-center justify-center rounded-lg shadow-lg',
                  isTerraAgrar
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-linear-to-br from-emerald-500 to-emerald-700',
                )}
              >
                <Leaf className="h-6 w-6 text-white" />
              </div>
              <span className="hidden text-xl font-bold sm:block">
                VALEO{' '}
                <span className={isTerraAgrar ? 'text-primary' : 'text-status-success'}>
                  Portal
                </span>
              </span>
            </Link>

            {isAnwender && (
              <Link
                to="/"
                className="ml-2 flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 hover:text-status-success"
              >
                <ArrowLeft className="h-4 w-4" />
                <span className="hidden sm:inline">Zur Startseite</span>
              </Link>
            )}
          </div>

          <nav className="hidden items-center gap-1 lg:flex">
            {navItems.slice(0, 5).map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={clsx(
                    'flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    isActivePath(item.path) ? navActiveClass : navInactiveClass,
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span className="hidden xl:block">{item.label}</span>
                  {item.badge && (
                    <Badge variant="secondary" className="text-xs">
                      {item.badge}
                    </Badge>
                  )}
                </Link>
              )
            })}
            <div className="relative" ref={moreMenuRef}>
              <Button
                variant="ghost"
                className="min-h-touch gap-2"
                onClick={() => setMoreMenuOpen((open) => !open)}
              >
                <FileSpreadsheet className="h-4 w-4" />
                Mehr
              </Button>
              {moreMenuOpen && (
                <div className="absolute right-0 top-full z-50 mt-2 w-64 rounded-lg border bg-white p-2 shadow-lg">
                  {navItems.slice(5).map((item) => (
                    <PortalNavLink
                      key={item.path}
                      item={item}
                      active={isActivePath(item.path)}
                      compact
                      terra={isTerraAgrar}
                      onNavigate={() => setMoreMenuOpen(false)}
                    />
                  ))}
                </div>
              )}
            </div>
          </nav>

          <div className="flex items-center gap-2">
            <PortalKontoWahl />
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              {notifications > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">
                  {notifications}
                </span>
              )}
            </Button>

            <div className="relative" ref={userMenuRef}>
              <Button
                variant="ghost"
                className="flex items-center gap-2"
                onClick={() => setUserMenuOpen((open) => !open)}
              >
                <Avatar className="h-8 w-8">
                  <AvatarFallback
                    className={isTerraAgrar ? 'bg-primary/10 text-primary' : 'bg-emerald-100 text-emerald-700'}
                  >
                    {kontoKuerzel}
                  </AvatarFallback>
                </Avatar>
                <span className="hidden text-sm font-medium md:block">
                  {kontoName}
                </span>
              </Button>
              {userMenuOpen && (
                <div className="absolute right-0 top-full z-50 mt-2 w-56 rounded-lg border bg-white p-2 shadow-lg">
                  <div className="border-b px-3 py-2">
                    <div className="font-medium">{kontoName}</div>
                    <div className="text-xs text-muted-foreground">{konto?.customer_number ?? ''}</div>
                  </div>
                  {/*
                    „Mein Profil" führte auf `/portal/profil` — und diese Route
                    zeigte auf `@/pages/portal/index`, also auf die Übersicht.
                    Der Kunde klickte sein Profil an und bekam die Startseite;
                    eine `profil.tsx` gibt es nicht.

                    Seit 14.10.2026 kommt der Kunde aus der Anmeldung und der
                    Kontowahl (PORTAL-CONTEXT-001), nicht mehr aus Konstanten.
                    Eine Profilseite (Stammdaten des Betriebs, eigene Zugänge)
                    ist noch nicht gebaut; deshalb steht hier kein Link, statt
                    einer, der woanders hinführt.
                  */}
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="mt-1 flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm text-status-error hover:bg-red-50"
                  >
                    <LogOut className="h-4 w-4" />
                    Abmelden
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {mobileMenuOpen && (
        <div className="fixed inset-0 z-60 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/40"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Menue schliessen"
          />
          <aside className="relative h-full w-80 max-w-[85vw] overflow-y-auto border-r bg-white p-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-lg font-semibold">
                <Leaf className={clsx('h-6 w-6', isTerraAgrar ? 'text-primary' : 'text-status-success')} />
                Kundenportal
              </div>
              <Button variant="ghost" size="icon" onClick={() => setMobileMenuOpen(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            <nav className="mt-6 flex flex-col gap-1">
              {isAnwender && (
                <Link
                  to="/"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center justify-between rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800 transition-colors hover:bg-emerald-100"
                >
                  <span className="flex items-center gap-3">
                    <ArrowLeft className="h-5 w-5" />
                    Zur Startseite
                  </span>
                  <ChevronRight className="h-4 w-4 text-status-success" />
                </Link>
              )}
              {navItems.map((item) => (
                <PortalNavLink
                  key={item.path}
                  item={item}
                  active={isActivePath(item.path)}
                  terra={isTerraAgrar}
                  onNavigate={() => setMobileMenuOpen(false)}
                />
              ))}
            </nav>
          </aside>
        </div>
      )}

      <main className="mx-auto max-w-7xl px-4 py-6">
        <PortalKontoGate intern={INNENDIENST_ROLLEN.some((rolle) => hasRole(rolle))}>
          <Outlet />
        </PortalKontoGate>
      </main>

      <nav
        className={clsx(
          'fixed bottom-0 left-0 right-0 z-50 border-t backdrop-blur-md lg:hidden',
          isTerraAgrar ? 'border-border bg-card/90' : 'bg-white/80',
        )}
      >
        <div className="flex justify-around py-2">
          {navItems.slice(0, 5).map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={clsx(
                  'flex flex-col items-center gap-1 rounded-lg px-3 py-2 text-xs transition-colors',
                  isActivePath(item.path)
                    ? isTerraAgrar
                      ? 'text-primary'
                      : 'text-status-success'
                    : isTerraAgrar
                      ? 'text-muted-foreground'
                      : 'text-gray-500',
                )}
              >
                <Icon className="h-5 w-5" />
                <span className="hidden xs:block">{item.label.split(' ')[0]}</span>
              </Link>
            )
          })}
        </div>
      </nav>

      <div className="h-20 lg:hidden" />
    </div>
  )
}
