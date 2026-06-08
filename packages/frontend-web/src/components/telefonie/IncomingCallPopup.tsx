import { useNavigate } from '@/app/routing/typed-router'
import { Phone, PhoneOff, User2, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { usePendingCalls, useAckCall, type TapiCall } from '@/lib/api/tapi'

/**
 * Globales Popup für eingehende Anrufe (TAPI/Click-to-Customer).
 * Pollt /crm/tapi/pending; ein lokaler TAPI-Bridge-Dienst meldet Anrufe per
 * POST /crm/tapi/incoming. Zeigt den erkannten Kunden und führt ins Cockpit.
 * Wird global in der AppShell gemountet.
 */
export function IncomingCallPopup(): JSX.Element | null {
  const navigate = useNavigate()
  const { data } = usePendingCalls(5000)
  const ack = useAckCall()
  const call: TapiCall | undefined = (data ?? [])[0]

  if (!call) return null

  const handleOpen = () => {
    if (call.kunden_nr) navigate('/crm/kunden-cockpit')
    ack.mutate(call.id)
  }

  return (
    <div className="fixed bottom-4 right-4 z-[60] w-80 animate-in slide-in-from-bottom-2">
      <div className="rounded-lg border bg-card shadow-lg">
        <div className="flex items-center justify-between border-b bg-green-50 px-3 py-2">
          <span className="flex items-center gap-2 text-sm font-semibold text-green-700">
            <Phone className="h-4 w-4 animate-pulse" />Eingehender Anruf
          </span>
          <button onClick={() => ack.mutate(call.id)} className="text-muted-foreground hover:text-foreground" aria-label="Schließen">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="space-y-1 px-3 py-3">
          {call.kunden_nr ? (
            <>
              <p className="flex items-center gap-2 font-medium"><User2 className="h-4 w-4 text-blue-600" />{call.kunde_name ?? call.kunden_nr}</p>
              <p className="text-xs text-muted-foreground">{call.kunden_nr} · {call.caller}</p>
            </>
          ) : (
            <>
              <p className="font-medium">Unbekannte Nummer</p>
              <p className="text-xs text-muted-foreground">{call.caller}</p>
            </>
          )}
        </div>
        <div className="flex gap-2 border-t px-3 py-2">
          <Button size="sm" className="flex-1 gap-2" onClick={handleOpen} disabled={!call.kunden_nr}>
            <User2 className="h-4 w-4" />Kunde öffnen
          </Button>
          <Button size="sm" variant="outline" className="gap-2" onClick={() => ack.mutate(call.id)}>
            <PhoneOff className="h-4 w-4" />Erledigt
          </Button>
        </div>
      </div>
    </div>
  )
}
