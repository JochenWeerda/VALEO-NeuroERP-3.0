import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { toast } from 'sonner'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { schliesseAnmeldungAb } from '@/lib/api/postfaecher'

/**
 * Rueckkehr von der Anmeldung bei Google oder Microsoft. Der Anbieter leitet mit ``code`` und ``state`` hierher;
 * die Seite gibt beides an das Backend (das ``state`` gegen Mandant und Zeit prueft)
 * und fuehrt zurueck zu den Postfaechern. Keine Maske, nur ein Durchgang.
 */
export default function PostfaecherAnmeldungRueckrufPage(): JSX.Element {
  const [parameter] = useSearchParams()
  const navigate = useNavigate()
  const [meldung, setMeldung] = useState('Anmeldung beim Anbieter wird abgeschlossen …')
  const einmal = useRef(false)

  useEffect(() => {
    if (einmal.current) return
    einmal.current = true
    const fehler = parameter.get('error')
    const code = parameter.get('code')
    const state = parameter.get('state')
    if (fehler || !code || !state) {
      setMeldung('Die Anmeldung wurde abgebrochen.')
      toast.error('Anmeldung abgebrochen', { description: fehler ?? 'Keine Rückmeldung des Anbieters.' })
      navigate('/admin/postfaecher')
      return
    }
    schliesseAnmeldungAb(code, state)
      .then((postfach) => {
        toast.success(`Verbunden: ${postfach.benutzer ?? postfach.absender_email}`, {
          description: 'Jetzt mit „Testmail senden“ prüfen.',
        })
      })
      .catch((e: unknown) => {
        toast.error('Anmeldung nicht abgeschlossen', { description: getAxiosErrorMessage(e) })
      })
      .finally(() => navigate('/admin/postfaecher'))
  }, [navigate, parameter])

  return <p className="p-6 text-muted-foreground">{meldung}</p>
}
