import { useMemo } from 'react'
import { BookOpen, ExternalLink, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useLocation } from '@/app/routing/typed-router'
import { DOCS_USER_MANUAL_URL, openDocs, resolveHelpUrl } from '@/lib/docs-help'

/**
 * Eingebettete In-App-Hilfe (`/hilfe`).
 *
 * Bettet die MkDocs-Dokumentation per iframe ein. Über den `ctx`-Query-Parameter
 * (gesetzt vom Hilfe-Button der TopBar) wird kontextsensitiv die passende
 * Handbuch-Seite geladen (vgl. `docs/benutzerhandbuch/in-app-hilfe.md`).
 *
 * Cross-Origin-Hinweis: Die Doku-Site (GitHub Pages) erlaubt das Einbetten;
 * falls ein Reverse-Proxy/CSP das Framing blockiert, steht der „In neuem Tab
 * öffnen"-Fallback bereit.
 */
export default function HilfePage(): JSX.Element {
  const { search } = useLocation()

  const { url, ctx } = useMemo(() => {
    const params = new URLSearchParams(search)
    const ctxValue = params.get('ctx') ?? ''
    return {
      ctx: ctxValue,
      url: ctxValue ? resolveHelpUrl(ctxValue) : DOCS_USER_MANUAL_URL,
    }
  }, [search])

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-primary" />
          <div>
            <h1 className="text-xl font-semibold leading-tight">Hilfe &amp; Dokumentation</h1>
            <p className="text-sm text-muted-foreground">
              {ctx
                ? 'Passende Anleitung zur aktuellen Maske – eingebettetes Handbuch.'
                : 'Benutzerhandbuch und technische Dokumentation.'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => openDocs(DOCS_USER_MANUAL_URL)}>
            <Home className="mr-2 h-4 w-4" />
            Handbuch-Start
          </Button>
          <Button variant="outline" size="sm" onClick={() => openDocs(url)}>
            <ExternalLink className="mr-2 h-4 w-4" />
            In neuem Tab öffnen
          </Button>
        </div>
      </div>

      <div className="relative flex-1 overflow-hidden rounded-lg border bg-background">
        <iframe
          key={url}
          src={url}
          title="VALEO NeuroERP – Dokumentation"
          className="h-full w-full"
          loading="lazy"
          referrerPolicy="no-referrer"
        />
      </div>

      <p className="text-xs text-muted-foreground">
        Bleibt die Vorschau leer? Manche Umgebungen verbieten das Einbetten –
        dann bitte „In neuem Tab öffnen" nutzen.
      </p>
    </div>
  )
}
