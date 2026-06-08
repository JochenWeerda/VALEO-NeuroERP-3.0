/**
 * FIBU Suite – Dashboard (Index): großflächige Cards zur Maskenauswahl.
 * Wird als Index-Route unter /fibu-suite angezeigt.
 */

import { Link } from '@/app/routing/react-router-compat'
import { FIBU_SUITE_ITEMS } from '@/app/navigation/fibu-suite'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Euro } from 'lucide-react'

const MAX_CARDS = 24

function getSuitePath(child: { path?: string; module?: string }): string | null {
  if (!child.path) return null
  const p = child.path.startsWith('/') ? child.path.slice(1) : child.path
  if (p.startsWith('fibu/')) return p.replace('fibu/', '')
  if (p.startsWith('finance/')) return `finance/${p.replace('finance/', '')}`
  if (p.startsWith('export/')) return p.replace('export/', '')
  if (p.startsWith('pos/')) return p
  return p
}

export default function FibuSuiteDashboard(): JSX.Element {
  const suiteBase = '/fibu-suite'

  const cards = FIBU_SUITE_ITEMS
    .map((child) => {
      const path = getSuitePath(child)
      if (!path) return null
      const Icon = child.icon
      return {
        id: child.id,
        label: child.label,
        path: `${suiteBase}/${path}`,
        Icon,
      }
    })
    .filter((x): x is NonNullable<typeof x> => x != null)
    .slice(0, MAX_CARDS)

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center gap-3">
        <Euro className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">FIBU Suite</h1>
          <p className="text-muted-foreground text-sm">Finanzbuchhaltung – Masken auswählen</p>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {cards.map((item) => (
          <Link key={item.id} to={item.path}>
            <Card className="h-full transition-colors hover:bg-muted/50">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                  <span className="rounded-lg border bg-muted/40 p-2">
                    <item.Icon className="h-5 w-5" />
                  </span>
                  <CardTitle className="text-base">{item.label}</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <CardDescription className="text-xs">Maske öffnen</CardDescription>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
