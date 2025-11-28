/**
 * Customer Portal Layout
 * 
 * Separates Layout für Kunden-Zugang via Handy/Tablet
 * Optimiert für mobile Nutzung mit Touch-freundlicher Navigation
 */

import { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import {
  Home,
  ShoppingCart,
  FileText,
  Receipt,
  Download,
  Leaf,
  Menu,
  LogOut,
  User,
  Bell,
  ChevronRight,
  Package,
  ClipboardList,
  Award,
  FileSpreadsheet,
  BarChart3,
} from 'lucide-react'

interface NavItem {
  label: string
  path: string
  icon: React.ReactNode
  badge?: string | number
}

const customerNavItems: NavItem[] = [
  { label: 'Übersicht', path: '/portal', icon: <Home className="h-5 w-5" /> },
  { label: 'Bestellportal', path: '/portal/shop', icon: <ShoppingCart className="h-5 w-5" />, badge: 'NEU' },
  { label: 'Meine Bestellungen', path: '/portal/bestellungen', icon: <Package className="h-5 w-5" /> },
  { label: 'Anfragen', path: '/portal/anfragen', icon: <ClipboardList className="h-5 w-5" /> },
  { label: 'Verträge', path: '/portal/vertraege', icon: <FileText className="h-5 w-5" /> },
  { label: 'Rechnungen', path: '/portal/rechnungen', icon: <Receipt className="h-5 w-5" /> },
  { label: 'Dokumente', path: '/portal/dokumente', icon: <Download className="h-5 w-5" /> },
  { label: 'Zertifikate', path: '/portal/zertifikate', icon: <Award className="h-5 w-5" /> },
  { label: 'Ackerschlagkartei', path: '/portal/feldbuch', icon: <Leaf className="h-5 w-5" /> },
  { label: 'Nährstoffbilanzen', path: '/portal/naehrstoffbilanzen', icon: <BarChart3 className="h-5 w-5" /> },
]

// Mock User Data - wird später durch echte Auth ersetzt
const mockCustomer = {
  name: 'Musterhof GmbH',
  email: 'info@musterhof.de',
  initials: 'MH',
  avatar: '',
  kundennummer: 'K-2024-001',
}

export default function CustomerPortalLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [notifications] = useState(3) // Mock notifications

  const isActivePath = (path: string) => {
    if (path === '/portal') {
      return location.pathname === '/portal'
    }
    return location.pathname.startsWith(path)
  }

  const handleLogout = () => {
    // TODO: Implement actual logout
    navigate('/auth/login')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-amber-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          {/* Logo & Mobile Menu */}
          <div className="flex items-center gap-3">
            <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
              <SheetTrigger asChild className="lg:hidden">
                <Button variant="ghost" size="icon">
                  <Menu className="h-6 w-6" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-80">
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-2">
                    <Leaf className="h-6 w-6 text-emerald-600" />
                    Kundenportal
                  </SheetTitle>
                </SheetHeader>
                <nav className="mt-6 flex flex-col gap-1">
                  {customerNavItems.map((item) => (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setMobileMenuOpen(false)}
                      className={cn(
                        'flex items-center justify-between rounded-lg px-4 py-3 text-sm font-medium transition-colors',
                        isActivePath(item.path)
                          ? 'bg-emerald-100 text-emerald-900'
                          : 'text-gray-600 hover:bg-gray-100'
                      )}
                    >
                      <span className="flex items-center gap-3">
                        {item.icon}
                        {item.label}
                      </span>
                      <span className="flex items-center gap-2">
                        {item.badge && (
                          <Badge variant="secondary" className="text-xs">
                            {item.badge}
                          </Badge>
                        )}
                        <ChevronRight className="h-4 w-4 text-gray-400" />
                      </span>
                    </Link>
                  ))}
                </nav>
              </SheetContent>
            </Sheet>

            <Link to="/portal" className="flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-700 shadow-lg">
                <Leaf className="h-6 w-6 text-white" />
              </div>
              <span className="hidden text-xl font-bold text-gray-900 sm:block">
                VALEO <span className="text-emerald-600">Portal</span>
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden items-center gap-1 lg:flex">
            {customerNavItems.slice(0, 5).map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  'flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActivePath(item.path)
                    ? 'bg-emerald-100 text-emerald-900'
                    : 'text-gray-600 hover:bg-gray-100'
                )}
              >
                {item.icon}
                <span className="hidden xl:block">{item.label}</span>
                {item.badge && (
                  <Badge variant="secondary" className="text-xs">
                    {item.badge}
                  </Badge>
                )}
              </Link>
            ))}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="gap-2">
                  <FileSpreadsheet className="h-4 w-4" />
                  Mehr
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                {customerNavItems.slice(5).map((item) => (
                  <DropdownMenuItem key={item.path} asChild>
                    <Link to={item.path} className="flex items-center gap-2">
                      {item.icon}
                      {item.label}
                      {item.badge && (
                        <Badge variant="secondary" className="ml-auto text-xs">
                          {item.badge}
                        </Badge>
                      )}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </nav>

          {/* User Menu */}
          <div className="flex items-center gap-2">
            {/* Notifications */}
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              {notifications > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">
                  {notifications}
                </span>
              )}
            </Button>

            {/* User Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-2">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={mockCustomer.avatar} />
                    <AvatarFallback className="bg-emerald-100 text-emerald-700">
                      {mockCustomer.initials}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden text-sm font-medium md:block">
                    {mockCustomer.name}
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="flex flex-col">
                    <span>{mockCustomer.name}</span>
                    <span className="text-xs text-muted-foreground">
                      {mockCustomer.kundennummer}
                    </span>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/portal/profil" className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Mein Profil
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  Abmelden
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>

      {/* Mobile Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 border-t bg-white/80 backdrop-blur-md lg:hidden">
        <div className="flex justify-around py-2">
          {customerNavItems.slice(0, 5).map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex flex-col items-center gap-1 rounded-lg px-3 py-2 text-xs transition-colors',
                isActivePath(item.path)
                  ? 'text-emerald-600'
                  : 'text-gray-500'
              )}
            >
              {item.icon}
              <span className="hidden xs:block">{item.label.split(' ')[0]}</span>
            </Link>
          ))}
        </div>
      </nav>

      {/* Spacer for mobile bottom nav */}
      <div className="h-20 lg:hidden" />
    </div>
  )
}

