import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { v4 as uuidv4 } from 'uuid'
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
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { financeSteuerschluesselScreen } from '@/masks/capture-screens'
import {
  ladeKontenvorschlaege,
  listeSteuerschluessel,
  speichereSteuerschluessel,
  type Kontovorschlag,
  type Steuerschluessel,
  type SteuerschluesselEingabe,
} from '@/lib/api/steuerschluessel'

/**
 * Steuerschluessel des Mandanten. Die Seite speichert, der Mask Builder zeichnet — Felder, Tabelle
 * und Aktionen stehen in der ScreenDefinition `finance/steuerschluessel`.
 *
 * Aus diesen Schluesseln nehmen alle Belege Satz und Konten. Deshalb gibt es keinen Vorgabewert,
 * weder fuer den Satz noch fuer ein Konto; geprueft wird auf dem Server.
 *
 * Die Konten sind eine Auswahl aus dem Kontenplan: je Feld nur Konten der passenden Art, die zum
 * Satz passenden zuerst. Der Server reiht, die Seite waehlt nichts vor.
 */

const leer: Record<string, unknown> = {
  code: '', bezeichnung: '', steuersatz: '', credit_account: '', revenue_account: '', debit_account: '',
  expense_account: '',
  par_24_ustg: false, reverse_charge: false, intracom: false, export: false,
  ustva_position: '', ustva_bezeichnung: '', gueltig_von: '', gueltig_bis: '', active: true, notizen: '',
}
const PFLICHT = ['code', 'bezeichnung', 'steuersatz', 'gueltig_von']
// Der Server prueft die Rolle; hier nur die Freigabe der Aktion im Builder.
const RECHTE = ['finance.steuerschluessel.write']
const LISTE = ['finance', 'tax-keys']
const BUCHT_NICHT = 'Bucht nicht automatisch'
const KONTENFELDER = ['credit_account', 'revenue_account', 'debit_account', 'expense_account'] as const
type Kontenfeld = (typeof KONTENFELDER)[number]

function kontenAuswahl(vorschlaege: Kontovorschlag[], gewaehlt: string): Array<{ value: string; label: string }> {
  const auswahl = vorschlaege.map((k) => ({
    value: k.account_number,
    label: `${k.account_number} – ${k.account_name}${k.grund?.startsWith('passt') ? ` (Vorschlag: ${k.grund})` : ''}`,
  }))
  // Ein hinterlegtes Konto, das der Kontenplan nicht mehr anbietet, bleibt sichtbar — der Server lehnt es beim Speichern ab.
  return gewaehlt && !auswahl.some((o) => o.value === gewaehlt)
    ? [{ value: gewaehlt, label: `${gewaehlt} – nicht im Kontenplan, gesperrt oder falsche Kontenart` }, ...auswahl]
    : auswahl
}

function text(wert: unknown): string {
  return String(wert ?? '').trim()
}

function prozent(wert: unknown): string {
  return `${Number(wert).toLocaleString('de-DE')} %`
}

function kennzeichen(k: Steuerschluessel): string {
  const teile = [
    k.par_24_ustg ? '§ 24 UStG' : null,
    k.reverse_charge ? 'Reverse Charge' : null,
    k.intracom ? 'Innergemeinschaftlich' : null,
    k.export ? 'Ausfuhr' : null,
  ].filter(Boolean)
  return teile.length > 0 ? teile.join(', ') : '–'
}

export default function SteuerschluesselPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const liste = useQuery({ queryKey: [...LISTE, 'pflege'], queryFn: listeSteuerschluessel })
  const schluessel = useMemo(() => liste.data ?? [], [liste.data])

  const [geladen, setGeladen] = useState<Steuerschluessel | null>(null)
  // Der Satz aus der Eingabe reiht die Kontenvorschlaege.
  const [satz, setSatz] = useState('')
  const konten = useQuery({
    queryKey: [...LISTE, 'kontenvorschlaege', satz],
    queryFn: () => ladeKontenvorschlaege(satz),
    placeholderData: (vorher) => vorher,
  })
  const [laeuft, setLaeuft] = useState(false)
  const [fragen, setFragen] = useState<SteuerschluesselEingabe | null>(null)
  const sperre = useRef(false)
  // Ein Auftrag je bestaetigtem Speichern: Eine Wiederholung derselben Anfrage schreibt nicht zweimal.
  const auftrag = useRef('')

  useEffect(() => {
    if (liste.isError) toast.error('Steuerschlüssel nicht geladen', { description: getAxiosErrorMessage(liste.error) })
  }, [liste.error, liste.isError])
  useEffect(() => {
    if (konten.isError) toast.error('Kontenplan nicht geladen', { description: getAxiosErrorMessage(konten.error) })
  }, [konten.error, konten.isError])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...financeSteuerschluesselScreen,
    subtitle: geladen ? `Schlüssel ${geladen.code} bearbeiten` : financeSteuerschluesselScreen.subtitle,
    layout: { ...financeSteuerschluesselScreen.layout, density: isTouch ? 'comfortable' : 'compact' },
    summary: financeSteuerschluesselScreen.summary.map((eintrag) => ({
      ...eintrag,
      value: String(eintrag.key === 'anzahl'
        ? schluessel.length
        : schluessel.filter((k) => k.active && (k.verwendung ?? '').startsWith(BUCHT_NICHT)).length),
    })),
    // Der Schluessel entscheidet ueber Anlage oder Aenderung; beim Bearbeiten steht er fest.
    fields: financeSteuerschluesselScreen.fields.map((feld) => ({
      ...feld,
      readOnly: feld.key === 'code' && geladen !== null,
      ...(KONTENFELDER.includes(feld.key as Kontenfeld)
        ? {
            options: kontenAuswahl(konten.data?.[feld.key as Kontenfeld] ?? [], geladen?.[feld.key as Kontenfeld] ?? ''),
            placeholder: 'Kein Konto',
          }
        : {}),
    })),
    actions: financeSteuerschluesselScreen.actions.map((aktion) => ({ ...aktion, disabled: laeuft })),
  }), [geladen, isTouch, konten.data, laeuft, schluessel])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema, { permissions: RECHTE }), [schema])
  const form = useUniversalFormState({ screen: schema, initialValues: leer })
  const { resetForm } = form
  const satzEingabe = text(form.values.steuersatz)
  useEffect(() => setSatz(satzEingabe), [satzEingabe])

  const zeige = useCallback((k: Steuerschluessel | null) => {
    setGeladen(k)
    resetForm(k
      ? {
          ...leer,
          code: k.code, bezeichnung: k.bezeichnung, steuersatz: String(Number(k.steuersatz)),
          credit_account: k.credit_account ?? '', revenue_account: k.revenue_account ?? '', debit_account: k.debit_account ?? '',
          expense_account: k.expense_account ?? '',
          par_24_ustg: k.par_24_ustg, reverse_charge: k.reverse_charge, intracom: k.intracom, export: k.export,
          ustva_position: k.ustva_position ?? '', ustva_bezeichnung: k.ustva_bezeichnung ?? '',
          gueltig_von: k.gueltig_von, gueltig_bis: k.gueltig_bis ?? '', active: k.active, notizen: k.notizen ?? '',
        }
      : { ...leer })
  }, [resetForm])

  const vorhanden = useCallback((code: string) => schluessel.find((k) => k.code === code) ?? null, [schluessel])

  const speichernFragen = useCallback(() => {
    const werte = form.values
    if (PFLICHT.some((feld) => !text(werte[feld]))) {
      form.revealErrors?.()
      toast.error('Steuerschlüssel unvollständig', {
        description: 'Schlüssel, Bezeichnung, Steuersatz und Gültig von angeben. Es gibt keinen Vorgabewert.',
      })
      return
    }
    auftrag.current = `steuerschluessel-speichern-${uuidv4()}`
    setFragen({
      code: text(werte.code),
      bezeichnung: text(werte.bezeichnung),
      steuersatz: text(werte.steuersatz),
      credit_account: text(werte.credit_account) || null,
      revenue_account: text(werte.revenue_account) || null,
      debit_account: text(werte.debit_account) || null,
      expense_account: text(werte.expense_account) || null,
      par_24_ustg: werte.par_24_ustg === true,
      reverse_charge: werte.reverse_charge === true,
      intracom: werte.intracom === true,
      export: werte.export === true,
      ustva_position: text(werte.ustva_position) || null,
      ustva_bezeichnung: text(werte.ustva_bezeichnung) || null,
      gueltig_von: text(werte.gueltig_von),
      gueltig_bis: text(werte.gueltig_bis) || null,
      active: werte.active !== false,
      notizen: text(werte.notizen) || null,
    })
  }, [form])

  const speichern = useCallback(async () => {
    if (!fragen || sperre.current) return
    sperre.current = true
    setLaeuft(true)
    try {
      const ergebnis = await speichereSteuerschluessel(fragen, auftrag.current)
      if (!ergebnis.success) {
        const gruende = (ergebnis.validationErrors ?? []).map((f) => f.message).join(' ')
        toast.error('Steuerschlüssel nicht gespeichert', { description: gruende || ergebnis.error || 'Die Eingabe wurde abgelehnt.' })
        return
      }
      toast.success('Steuerschlüssel gespeichert', { description: ergebnis.summary ?? undefined })
      await queryClient.invalidateQueries({ queryKey: LISTE })
      zeige((await listeSteuerschluessel()).find((k) => k.code === fragen.code) ?? null)
    } catch (fehler) {
      toast.error('Steuerschlüssel nicht gespeichert', { description: getAxiosErrorMessage(fehler) })
    } finally {
      sperre.current = false
      setLaeuft(false)
      setFragen(null)
    }
  }, [fragen, queryClient, zeige])

  const screenContext = useMemo(() => createScreenContext({
    data: { steuerschluessel: schluessel },
    permissions: { granted: RECHTE },
    state: { values: form.values, policies: {} },
    actions: {
      'finance.steuerschluesselSpeichern': () => speichernFragen(),
      'finance.steuerschluesselNeu': () => zeige(null),
      'finance.steuerschluesselBearbeiten': (payload) => zeige(schluessel.find((k) => k.id === String(payload.id)) ?? null),
    },
    navigation: { push: () => undefined },
  }), [form.values, schluessel, speichernFragen, zeige])

  if (liste.isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="min-h-touch h-10 w-48" />
        <Skeleton className="h-40" />
      </div>
    )
  }

  const bestand = fragen ? vorhanden(fragen.code) : null

  return (
    <div className="space-y-6 p-3 md:p-6">
      <UniversalMaskRenderer
        plan={plan}
        formState={form}
        hideFormSubmit
        screenContext={screenContext}
        tables={{
          steuerschluessel: schluessel.map((k) => ({
            id: k.id,
            code: k.code,
            bezeichnung: k.bezeichnung,
            satz_text: prozent(k.steuersatz),
            credit_account: k.credit_account ?? '–',
            revenue_account: k.revenue_account ?? '–',
            debit_account: k.debit_account ?? '–',
            expense_account: k.expense_account ?? '–',
            kennzeichen_text: kennzeichen(k),
            verwendung: k.verwendung ?? '–',
            status_text: k.active ? 'Aktiv' : 'Inaktiv',
          })),
        }}
      />
      <AlertDialog open={fragen !== null} onOpenChange={(offen) => { if (!offen && !laeuft) setFragen(null) }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Steuerschlüssel {fragen?.code} {bestand ? 'ändern' : 'anlegen'}?
            </AlertDialogTitle>
            <AlertDialogDescription>
              {bestand
                ? `Den Schlüssel gibt es schon (${bestand.bezeichnung}, ${prozent(bestand.steuersatz)}); er wird geändert. `
                : ''}
              Neue Belege rechnen ab sofort mit {prozent(fragen?.steuersatz.replace(',', '.'))} und den angegebenen Konten.
              Gebuchte Belege bleiben unverändert.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={laeuft}>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              disabled={laeuft}
              onClick={(event) => {
                event.preventDefault()
                void speichern()
              }}
            >
              Speichern
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
