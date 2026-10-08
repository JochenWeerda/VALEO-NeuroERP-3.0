import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Skeleton } from '@/components/ui/skeleton'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { ActionInputDialog } from '@/components/mask-builder/renderers/ActionInputDialog'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import type { ScreenActionDefinition, ScreenDefinition } from '@/components/mask-builder/schema'
import type { WorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { adminPostfaecherScreen } from '@/masks/capture-screens'
import {
  entfernePostfach,
  listePostfaecher,
  speicherePostfach,
  starteGoogleAnmeldung,
  testePostfach,
  type Postfach,
} from '@/lib/api/postfaecher'

const ANBIETER: Record<string, string> = {
  ionos: 'IONOS',
  google: 'Google',
  smtp: 'SMTP',
  alias: 'Alias',
}
const STATUS: Record<string, string> = { neu: 'Ungeprüft', geprueft: 'Geprüft', fehler: 'Fehler' }

const leer: Record<string, unknown> = {
  kennung: '', bezeichnung: '', absender_email: '', absender_name: '', anbieter: 'ionos', anmeldung: 'passwort',
  passwort: '', benutzer: '', smtp_host: '', smtp_port: '', sicherheit: 'starttls', zugang_von: '',
  verwendungen: '', rollen: '', benutzer_freigabe: '', persoenlich_fuer: '', ist_standard: false,
}

function text(wert: unknown): string {
  return String(wert ?? '').trim()
}

function liste(wert: unknown): string[] {
  return text(wert).split(',').map((teil) => teil.trim()).filter(Boolean)
}

function alsFormular(postfach: Postfach): Record<string, unknown> {
  return {
    ...leer,
    ...postfach,
    passwort: '',
    smtp_port: postfach.smtp_port ?? '',
    zugang_von: postfach.zugang_von ?? '',
    verwendungen: postfach.verwendungen.join(', '),
    rollen: postfach.rollen.join(', '),
    benutzer_freigabe: postfach.benutzer_freigabe.join(', '),
  }
}

export default function AdminPostfaecherPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const abfrage = useQuery({ queryKey: ['admin-postfaecher'], queryFn: listePostfaecher })
  const postfaecher = useMemo(() => abfrage.data ?? [], [abfrage.data])
  const [geladen, setGeladen] = useState<string | null>(null)
  const [laeuft, setLaeuft] = useState<string | null>(null)
  const sperre = useRef(false)
  const [testFragen, setTestFragen] = useState(false)
  const [entfernenFragen, setEntfernenFragen] = useState<Postfach | null>(null)

  useEffect(() => {
    if (!abfrage.isError) return
    toast.error('Postfächer nicht geladen', { description: getAxiosErrorMessage(abfrage.error) })
  }, [abfrage.error, abfrage.isError])

  const aktuell = postfaecher.find((p) => p.id === geladen) ?? null
  const standard = postfaecher.find((p) => p.ist_standard)

  const schema = useMemo<ScreenDefinition>(() => ({
    ...adminPostfaecherScreen,
    subtitle: aktuell ? `Bearbeitet: ${aktuell.absender_email}` : adminPostfaecherScreen.subtitle,
    layout: { ...adminPostfaecherScreen.layout, density: isTouch ? 'comfortable' : 'compact' },
    summary: adminPostfaecherScreen.summary.map((item) => ({
      ...item,
      value: item.key === 'postfaecher' ? String(postfaecher.length) : (standard?.absender_email ?? '–'),
    })),
    fields: adminPostfaecherScreen.fields.map((feld) => feld.key === 'zugang_von'
      ? {
          ...feld,
          options: postfaecher
            .filter((p) => p.anbieter !== 'alias' && p.id !== geladen)
            .map((p) => ({ value: p.id, label: `${p.kennung} (${p.absender_email})` })),
        }
      : feld.key === 'passwort' && aktuell?.hat_geheimnis
        ? { ...feld, placeholder: 'hinterlegt – leer lassen zum Behalten' }
        : feld),
    actions: adminPostfaecherScreen.actions.map((action) => ({
      ...action,
      disabled: laeuft !== null
        || (action.key === 'testen' && !aktuell)
        || (action.key === 'google' && !(aktuell?.anbieter === 'google' && aktuell.anmeldung === 'oauth2')),
    })),
  }), [aktuell, geladen, isTouch, laeuft, postfaecher, standard])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema, { permissions: ['admin.postfach.testen'] }), [schema])
  const form = useUniversalFormState({ screen: schema, initialValues: leer })
  const { resetForm } = form

  const laden = useCallback((postfach: Postfach | null) => {
    setGeladen(postfach?.id ?? null)
    resetForm(postfach ? alsFormular(postfach) : { ...leer })
  }, [resetForm])

  // Ein Ablauf zur Zeit: der Schluessel zeigt, welcher, und sperrt alle Knoepfe.
  const mitSperre = useCallback(async (schluessel: string, arbeit: () => Promise<void>) => {
    if (sperre.current) return
    sperre.current = true
    setLaeuft(schluessel)
    try {
      await arbeit()
    } finally {
      sperre.current = false
      setLaeuft(null)
    }
  }, [])

  const neuLaden = useCallback(async () => {
    await queryClient.invalidateQueries({ queryKey: ['admin-postfaecher'] })
  }, [queryClient])

  const speichern = useCallback(() => mitSperre('speichern', async () => {
    const werte = form.values
    if (!text(werte.kennung) || !text(werte.absender_email)) {
      form.revealErrors?.()
      toast.error('Postfach unvollständig', { description: 'Kennung und Absender-Adresse eintragen.' })
      return
    }
    try {
      const gespeichert = await speicherePostfach({
        kennung: text(werte.kennung),
        bezeichnung: text(werte.bezeichnung) || null,
        anbieter: text(werte.anbieter) || 'smtp',
        anmeldung: text(werte.anmeldung) || 'passwort',
        smtp_host: text(werte.smtp_host) || null,
        smtp_port: text(werte.smtp_port) ? Number(werte.smtp_port) : null,
        sicherheit: text(werte.sicherheit) || null,
        benutzer: text(werte.benutzer) || null,
        absender_email: text(werte.absender_email),
        absender_name: text(werte.absender_name) || null,
        passwort: text(werte.passwort) || null,
        zugang_von: text(werte.zugang_von) || null,
        ist_standard: werte.ist_standard === true,
        verwendungen: liste(werte.verwendungen),
        rollen: liste(werte.rollen),
        benutzer_freigabe: liste(werte.benutzer_freigabe),
        persoenlich_fuer: text(werte.persoenlich_fuer) || null,
      }, geladen ?? undefined)
      toast.success(`Postfach ${gespeichert.kennung} gespeichert`, {
        description: 'Mit „Testmail senden“ prüfen, ob der Versand funktioniert.',
      })
      await neuLaden()
      laden(gespeichert)
    } catch (fehler) {
      toast.error('Postfach nicht gespeichert', { description: getAxiosErrorMessage(fehler) })
    }
  }), [form, geladen, laden, mitSperre, neuLaden])

  const testen = useCallback((empfaenger?: string) => mitSperre('testen', async () => {
    if (!geladen) return
    try {
      const ergebnis = await testePostfach(geladen, empfaenger)
      toast.success('Testmail angenommen', { description: `Der Server hat sie an ${ergebnis.testmail_an} angenommen.` })
    } catch (fehler) {
      toast.error('Testmail nicht versendet', { description: getAxiosErrorMessage(fehler) })
    } finally {
      await neuLaden()
    }
  }), [geladen, mitSperre, neuLaden])

  const google = useCallback(() => mitSperre('google', async () => {
    if (!geladen) return
    try {
      window.location.assign(await starteGoogleAnmeldung(geladen))
    } catch (fehler) {
      toast.error('Google-Anmeldung nicht gestartet', { description: getAxiosErrorMessage(fehler) })
    }
  }), [geladen, mitSperre])

  const entfernen = useCallback((postfach: Postfach) => mitSperre(`entfernen:${postfach.id}`, async () => {
    try {
      await entfernePostfach(postfach.id)
      toast.success(`Postfach ${postfach.kennung} entfernt`)
      if (geladen === postfach.id) laden(null)
      await neuLaden()
    } catch (fehler) {
      toast.error('Postfach nicht entfernt', { description: getAxiosErrorMessage(fehler) })
    } finally {
      setEntfernenFragen(null)
    }
  }), [geladen, laden, mitSperre, neuLaden])

  const zeile = useCallback((payload: Record<string, unknown>) => postfaecher.find((p) => p.id === payload.id) ?? null,
    [postfaecher])

  const screenContext = useMemo(() => createScreenContext({
    data: { postfaecher },
    // Die Rolle prueft das Backend (admin); hier nur die Freigabe der Aktion im Builder.
    permissions: { granted: ['admin.postfach.testen'] },
    state: { values: form.values, policies: {} },
    actions: {
      'admin.postfachSpeichern': () => speichern(),
      'admin.postfachNeu': () => laden(null),
      'admin.postfachTesten': () => setTestFragen(true),
      'admin.postfachGoogle': () => google(),
      'admin.postfachBearbeiten': (payload) => laden(zeile(payload)),
      'admin.postfachEntfernen': (payload) => setEntfernenFragen(zeile(payload)),
    },
    navigation: { push: () => undefined },
  }), [form.values, google, laden, postfaecher, speichern, zeile])

  const workflow = useMemo<WorkflowState>(() => {
    const keins = postfaecher.length === 0
    const ungeprueft = postfaecher.filter((p) => p.status !== 'geprueft').length
    const naechste = keins
      ? 'Ein Postfach anlegen; ohne Postfach versendet das Haus keine E-Mails.'
      : !standard
        ? 'Ein Standard-Postfach festlegen; es fängt jeden Versand ohne passende Verwendung auf.'
        : ungeprueft
          ? `${ungeprueft} Postfach/Postfächer mit einer Testmail prüfen.`
          : 'Alle Postfächer sind geprüft.'
    return {
      status: {
        currentStatus: keins ? 'leer' : ungeprueft || !standard ? 'offen' : 'bereit',
        statusLabel: keins ? 'Kein Postfach' : ungeprueft ? `${ungeprueft} ungeprüft` : 'Bereit',
        tone: keins || !standard ? 'warning' : ungeprueft ? 'warning' : 'success',
      },
      nextAllowedActions: [{ actionKey: keins ? 'speichern' : 'testen', label: naechste, dangerLevel: 'safe', requiresConfirmation: false }],
      blockingReasons: keins ? [{ code: 'kein-postfach', message: naechste, blocking: true }] : [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [postfaecher, standard])

  const testAktion = adminPostfaecherScreen.actions.find((a) => a.key === 'testen') as ScreenActionDefinition

  if (abfrage.isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="min-h-touch h-10 w-48" />
        <Skeleton className="h-40" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <UniversalMaskRenderer
        plan={plan}
        formState={form}
        hideFormSubmit
        screenContext={screenContext}
        workflowState={workflow}
        tables={{
          postfaecher: postfaecher.map((p) => ({
            id: p.id,
            kennung: p.ist_standard ? `${p.kennung} (Standard)` : p.kennung,
            absender_email: p.absender_email,
            anbieter_text: ANBIETER[p.anbieter] ?? p.anbieter,
            verwendung_text: p.verwendungen.join(', ') || '–',
            freigabe_text: p.persoenlich_fuer
              ? `persönlich: ${p.persoenlich_fuer}`
              : [...p.rollen, ...p.benutzer_freigabe].join(', ') || 'alle',
            status_text: p.status === 'fehler' && p.letzter_fehler
              ? `Fehler: ${p.letzter_fehler.slice(0, 80)}`
              : STATUS[p.status] ?? p.status,
          })),
        }}
      />
      <ActionInputDialog
        action={testAktion}
        open={testFragen}
        onCancel={() => setTestFragen(false)}
        onSubmit={(werte) => {
          setTestFragen(false)
          void testen(text(werte.empfaenger) || undefined)
        }}
      />
      <AlertDialog open={entfernenFragen !== null} onOpenChange={(offen) => { if (!offen && laeuft === null) setEntfernenFragen(null) }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Postfach {entfernenFragen?.kennung} entfernen?</AlertDialogTitle>
            <AlertDialogDescription>
              Danach geht kein Versand mehr über {entfernenFragen?.absender_email}. Aliase, die seine Anmeldung
              nutzen, müssen vorher umgestellt werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={laeuft !== null}>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              disabled={laeuft !== null}
              onClick={(event) => {
                event.preventDefault()
                if (entfernenFragen) void entfernen(entfernenFragen)
              }}
            >
              Entfernen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
