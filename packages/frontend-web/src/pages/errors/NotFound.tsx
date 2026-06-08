import { Link } from '@/app/routing/typed-router'
import { Button } from '@/components/ui/button'

export default function NotFoundPage(): JSX.Element {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="max-w-md space-y-4 text-center">
        <h1 className="text-3xl font-semibold tracking-tight">404 - Seite nicht gefunden</h1>
        <p className="text-sm text-muted-foreground">
          Die angeforderte Seite existiert nicht oder wurde verschoben.
        </p>
        <div className="flex items-center justify-center gap-2">
          <Button asChild variant="default">
            <Link to="/">Zur Startseite</Link>
          </Button>
          <Button asChild variant="outline">
            <Link to="/verkauf/kunden-liste">Zu Kunden</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
