/**
 * Annahme QR-Code
 * Zeigt einen QR-Code, der zur LKW-Registrierung führt.
 * Für Handy-Nutzung: QR an Tor/Annahme scannen → Eingabemaske öffnet sich auf dem Smartphone.
 * Mobil (Lager, Waage, Außendienst): Dokumente/Registrierung per Handy (iOS/Android).
 */

import { useState, useEffect } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { QRCodeSVG } from 'qrcode.react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Smartphone, Truck } from 'lucide-react'

const PATH_LKW_REGISTRIERUNG = '/annahme/lkw-registrierung'

export default function AnnahmeQRPage(): JSX.Element {
  const navigate = useNavigate()
  const [registrationUrl, setRegistrationUrl] = useState<string>('')

  useEffect(() => {
    const base = typeof window !== 'undefined' ? window.location.origin : ''
    const basePath = (import.meta.env.BASE_URL || '/').replace(/\/$/, '')
    const path = `${basePath}/${PATH_LKW_REGISTRIERUNG.replace(/^\//, '')}`
    setRegistrationUrl(`${base}${path}`)
  }, [])

  return (
    <div className="min-h-screen bg-muted/30 p-4 md:p-6">
      <div className="mx-auto max-w-md space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Annahme — per Handy anmelden</h1>
          <Button variant="ghost" size="sm" onClick={() => navigate('/annahme/warteschlange')}>
            Zur Warteschlange
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Smartphone className="h-5 w-5" />
              QR-Code scannen
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Fahrer oder Mitarbeiter scannen den Code mit dem Handy (iOS/Android). Die
              LKW-Registrierung öffnet sich im Browser — Kennzeichen, Lieferschein und Fotos
              können direkt eingegeben bzw. hochgeladen werden.
            </p>
            {registrationUrl ? (
              <div className="flex flex-col items-center rounded-lg border bg-white p-6">
                <QRCodeSVG
                  value={registrationUrl}
                  size={220}
                  level="M"
                  includeMargin
                  role="img"
                  aria-label="QR-Code: LKW-Registrierung öffnen"
                />
                <p className="mt-3 text-center text-xs text-muted-foreground">
                  Öffnet: LKW-Registrierung
                </p>
              </div>
            ) : (
              <div className="flex h-[250px] items-center justify-center rounded-lg border bg-muted/50 text-sm text-muted-foreground">
                QR wird geladen…
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <Truck className="h-10 w-10 shrink-0 text-muted-foreground" />
              <div>
                <h2 className="font-semibold">Mobil nutzbar</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Lager, Waage und Außendienst können Belege und Registrierungen direkt vom
                  Handy aus erfassen — Fotos von Kennzeichen und Barcodes werden im
                  Upload-Bereich der Eingabemaske hochgeladen.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Button
          variant="outline"
          className="w-full"
          onClick={() => navigate(PATH_LKW_REGISTRIERUNG)}
        >
          Direkt zur LKW-Registrierung
        </Button>
      </div>
    </div>
  )
}
