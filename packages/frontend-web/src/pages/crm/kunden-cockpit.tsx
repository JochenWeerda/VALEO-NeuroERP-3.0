import { useEffect } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Loader2 } from 'lucide-react'

/**
 * DEPRECATED (KIM-DEPRECATE-COCKPIT-001):
 * Das klassische „Verkauf Kunden-Cockpit" ist durch das führende KIM-360°-Cockpit
 * unter `/crm` („Kunde im Mittelpunkt") funktional vollständig abgelöst
 * (Stammdaten, Ansprechpartner inkl. Werbe-Matrix/DSGVO, Kontakt-Journal,
 * Information-Module, Belege, Präsente, TAPI, NeuroAI, konfigurierbare Toolbar).
 *
 * Diese Seite bleibt nur als Redirect bestehen, damit alte Links/Lesezeichen auf
 * `/crm/kunden-cockpit` kein 404 erzeugen, sondern auf das KIM-Cockpit führen.
 */
export default function KundenCockpitRedirect() {
  const navigate = useNavigate()

  useEffect(() => {
    navigate('/crm', { replace: true })
  }, [navigate])

  return (
    <div className="flex h-full min-h-[40vh] flex-col items-center justify-center gap-3 p-8 text-center text-muted-foreground">
      <Loader2 className="h-6 w-6 animate-spin text-primary" />
      <h2 className="text-base font-semibold text-foreground">Kunden-Cockpit wurde abgelöst</h2>
      <p className="max-w-md text-sm">
        Das klassische Kunden-Cockpit wurde durch das KIM-360°-Cockpit ersetzt. Du wirst
        automatisch weitergeleitet.
      </p>
      <a href="/crm" className="text-sm font-medium text-primary underline underline-offset-2">
        Weiter zu „Kunde im Mittelpunkt" (/crm)
      </a>
    </div>
  )
}
