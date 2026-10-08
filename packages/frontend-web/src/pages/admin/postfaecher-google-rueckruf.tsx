import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { toast } from 'sonner'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { schliesseGoogleAnmeldungAb } from '@/lib/api/postfaecher'

/**
 * Rueckkehr von der Google-Anmeldung. Google leitet mit ``code`` und ``state`` hierher;
 * die Seite gibt beides an das Backend (das ``state`` gegen Mandant und Zeit prueft)
 * und fuehrt zurueck zu den Postfaechern. Keine Maske, nur ein Durchgang.
 */
export default function PostfaecherGoogleRueckrufPage(): JSX.Element {
  const [parameter] = useSearchParams()
  const navigate = useNavigate()
  const [meldung, setMeldung] = useState('Google-Anmeldung wird abgeschlossen …')
  const einmal = useRef(false)

  useEffect(() => {
    if (einmal.current) return
    einmal.current = true
    const fehler = parameter.get('error')
    const code = parameter.get('code')
    const state = parameter.get('state')
    if (fehler || !code || !state) {
      setMeldung('Die Google-Anmeldung wurde abgebrochen.')
      toast.error('Google-Anmeldung abgebrochen', { description: fehler ?? 'Keine Rückmeldung von Google.' })
      navigate('/admin/postfaecher')
      return
    }
    schliesseGoogleAnmeldungAb(code, state)
      .then((postfach) => {
        toast.success(`Google verbunden: ${postfach.benutzer ?? postfach.absender_email}`, {
          description: 'Jetzt mit „Testmail senden“ prüfen.',
        })
      })
      .catch((e: unknown) => {
        toast.error('Google-Anmeldung nicht abgeschlossen', { description: getAxiosErrorMessage(e) })
      })
      .finally(() => navigate('/admin/postfaecher'))
  }, [navigate, parameter])

  return <p className="p-6 text-muted-foreground">{meldung}</p>
}
