import { useStarfaceCTI } from '@/lib/services/starface-cti'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Phone, PhoneCall, PhoneForwarded, PhoneOff, Pause } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function CallWidget(): JSX.Element | null {
  const navigate = useNavigate()
  const { isConnected, activeCall, answerCall, hangupCall, transferCall, holdCall } = useStarfaceCTI()

  // Widget nur anzeigen wenn Starface verbunden
  if (!isConnected) return null

  // Kein aktiver Anruf
  if (!activeCall) return null

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-80">
      <Card className="border-primary shadow-lg">
        <CardContent className="pt-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-primary text-primary-foreground rounded-full">
              <Phone className="h-6 w-6" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <Badge variant={activeCall.direction === 'inbound' ? 'default' : 'secondary'}>
                  {activeCall.direction === 'inbound' ? 'Eingehend' : 'Ausgehend'}
                </Badge>
                <Badge variant="outline" className="font-mono">
                  {activeCall.state === 'ringing' ? '📞 Klingelt' : activeCall.state === 'connected' ? '🟢 Verbunden' : activeCall.state === 'held' ? '⏸ Gehalten' : '🔴 Beendet'}
                </Badge>
              </div>
              <div className="font-semibold mt-1">{activeCall.contactName || 'Unbekannt'}</div>
              <div className="text-sm text-muted-foreground font-mono">{activeCall.phoneNumber}</div>
              {activeCall.duration && (
                <div className="text-xs text-muted-foreground">Dauer: {formatDuration(activeCall.duration)}</div>
              )}
            </div>
          </div>

          {/* Kunde-Link falls vorhanden */}
          {activeCall.customerId && (
            <Button
              variant="outline"
              size="sm"
              className="w-full mb-3"
              onClick={() => navigate(`/verkauf/kunden-stamm-enhanced/${activeCall.customerId}`)}
            >
              🔗 Kunde öffnen
            </Button>
          )}

          {/* Call-Actions */}
          <div className="grid grid-cols-4 gap-2">
            {activeCall.state === 'ringing' && activeCall.direction === 'inbound' && (
              <Button size="sm" variant="default" className="col-span-4" onClick={() => answerCall(activeCall.callId)}>
                <PhoneCall className="h-4 w-4 mr-2" />
                Annehmen
              </Button>
            )}

            {activeCall.state === 'connected' && (
              <>
                <Button size="sm" variant="outline" onClick={() => holdCall(activeCall.callId)}>
                  <Pause className="h-4 w-4" />
                </Button>
                <Button size="sm" variant="outline" onClick={() => transferCall(activeCall.callId, '100')}>
                  <PhoneForwarded className="h-4 w-4" />
                </Button>
                <Button size="sm" variant="destructive" className="col-span-2" onClick={() => hangupCall(activeCall.callId)}>
                  <PhoneOff className="h-4 w-4 mr-2" />
                  Auflegen
                </Button>
              </>
            )}

            {activeCall.state === 'held' && (
              <Button size="sm" variant="default" className="col-span-4" onClick={() => answerCall(activeCall.callId)}>
                <PhoneCall className="h-4 w-4 mr-2" />
                Fortsetzen
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
