/**
 * Newsletter an ausgewaehlte Kunden/Lieferanten — mit Inhalt, wirklich versendet.
 *
 * Bis 08.10.2026 schickten die Listen nur einen Betreff, das Backend meldete
 * "in_queue" ohne Warteschlange, und die Maske zeigte "Newsletter versendet".
 * Jetzt fragt die Aktion Betreff und Text deklarativ ab (ActionInputDialog aus dem
 * Mask-Builder), versendet ueber SMTP und meldet, was der Server angenommen hat.
 */

import { useCallback, useRef, useState } from 'react'
import { ActionInputDialog } from '@/components/mask-builder/renderers/ActionInputDialog'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'
import { toast } from '@/hooks/use-toast'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'

const NEWSLETTER_AKTION: ScreenActionDefinition = {
  key: 'newsletter',
  label: 'Newsletter senden',
  inputFields: [
    { key: 'betreff', label: 'Betreff', type: 'text', required: true },
    { key: 'text', label: 'Text', type: 'textarea', required: true },
  ],
}

interface NewsletterErgebnis {
  versendet?: number
  fehlgeschlagen?: number
  empfaenger_ungueltig?: number
}

export function useNewsletterVersand(typ: 'kunden' | 'lieferanten'): {
  starten: (_emails: string[]) => void
  dialog: JSX.Element
} {
  const [empfaenger, setEmpfaenger] = useState<string[] | null>(null)
  const laeuft = useRef(false)

  const starten = useCallback((emails: string[]) => setEmpfaenger(emails), [])

  const senden = useCallback(async (werte: Record<string, unknown>) => {
    if (laeuft.current || !empfaenger) return
    laeuft.current = true
    const liste = empfaenger
    setEmpfaenger(null)
    try {
      const { data } = await apiClient.post<NewsletterErgebnis>('/api/v1/crm/kommunikation/newsletter', {
        empfaenger: liste,
        typ,
        betreff: String(werte.betreff ?? ''),
        text: String(werte.text ?? ''),
      })
      const fehlgeschlagen = (data.fehlgeschlagen ?? 0) + (data.empfaenger_ungueltig ?? 0)
      toast({
        title: fehlgeschlagen ? 'Newsletter teilweise versendet' : 'Newsletter versendet',
        description: `${data.versendet ?? 0} von ${liste.length} Empfängern erreicht.`,
        variant: fehlgeschlagen ? 'destructive' : undefined,
      })
    } catch (e: unknown) {
      toast({ title: 'Versand fehlgeschlagen', description: getAxiosErrorMessage(e), variant: 'destructive' })
    } finally {
      laeuft.current = false
    }
  }, [empfaenger, typ])

  const dialog = (
    <ActionInputDialog
      action={NEWSLETTER_AKTION}
      open={empfaenger !== null}
      onSubmit={(werte) => void senden(werte)}
      onCancel={() => setEmpfaenger(null)}
    />
  )
  return { starten, dialog }
}
