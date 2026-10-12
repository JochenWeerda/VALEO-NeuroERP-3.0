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
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { WorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { salesGutschriftScreen } from '@/masks/capture-screens'
import {
  bucheGutschrift,
  ladeGutschrift,
  listeGutschriften,
  listeSteuerschluessel,
  speichereGutschrift,
  steuerVorschau,
  type Gutschrift,
  type GutschriftPosition,
  type Steuerschluessel,
} from '@/lib/api/gutschrift'

/**
 * Gutschrift (Rechnungskorrektur). Die Seite speichert, der Mask Builder zeichnet — Felder, Tabellen
 * und Aktionen stehen in der ScreenDefinition `sales/gutschrift`.
 *
 * Die Umsatzsteuer kommt aus dem Steuerschluessel der Position. Die Seite rechnet nichts: Netto,
 * Steuer und Brutto liefert der Server, der dieselbe Stelle wie die Buchung benutzt.
 */

const leer: Record<string, unknown> = {
  credit_note_number: '', customer_id: '', customer_name: '', invoice_reference: '',
  correction_type: 'rechnungskorrektur', reason: '', reason_text: '', notes: '',
  pos_description: '', pos_quantity: '', pos_unit_price: '', pos_tax_code: '',
}
const POSITION_LEER = { pos_description: '', pos_quantity: '', pos_unit_price: '', pos_tax_code: '' }
const STATUS: Record<string, string> = { draft: 'Entwurf', posted: 'Gebucht' }
// Der Server prueft die Rolle; hier nur die Freigabe der Aktionen im Builder.
const RECHTE = ['sales.gutschrift.write', 'sales.gutschrift.post']

function text(wert: unknown): string {
  return String(wert ?? '').trim()
}

function zahl(wert: unknown): number {
  return Number(text(wert).replace(',', '.')) || 0
}

function euro(wert: unknown): string {
  return Number(wert ?? 0).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
}

function schluesselText(code: string | null, schluessel: Steuerschluessel[]): string {
  if (!code) return 'nicht gewählt'
  const k = schluessel.find((s) => s.code === code)
  return k ? `${k.code} – ${k.bezeichnung}` : `${code} – nicht (mehr) gültig`
}

export default function CreditNoteEditorPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const liste = useQuery({ queryKey: ['sales-gutschriften'], queryFn: listeGutschriften })
  const steuerschluessel = useQuery({ queryKey: ['finance', 'tax-keys', 'auswahl'], queryFn: listeSteuerschluessel, staleTime: 5 * 60 * 1000 })
  const gutschriften = useMemo(() => liste.data ?? [], [liste.data])
  const schluessel = useMemo(() => steuerschluessel.data ?? [], [steuerschluessel.data])

  const [positionen, setPositionen] = useState<GutschriftPosition[]>([])
  const [geladen, setGeladen] = useState<Gutschrift | null>(null)
  const [laeuft, setLaeuft] = useState<string | null>(null)
  const [pruefgrund, setPruefgrund] = useState<string | null>(null)
  const [buchenFragen, setBuchenFragen] = useState(false)
  const sperre = useRef(false)

  const vorschau = useQuery({
    queryKey: ['sales-gutschrift-steuer', positionen],
    queryFn: () => steuerVorschau(positionen),
    enabled: positionen.length > 0,
  })

  useEffect(() => {
    if (liste.isError) toast.error('Gutschriften nicht geladen', { description: getAxiosErrorMessage(liste.error) })
  }, [liste.error, liste.isError])
  useEffect(() => {
    if (steuerschluessel.isError) {
      toast.error('Steuerschlüssel nicht geladen', { description: getAxiosErrorMessage(steuerschluessel.error) })
    }
  }, [steuerschluessel.error, steuerschluessel.isError])

  const gebucht = geladen?.status === 'posted'
  const gespeichert = geladen !== null
  const steuer = positionen.length > 0 ? vorschau.data : undefined

  const schema = useMemo<ScreenDefinition>(() => ({
    ...salesGutschriftScreen,
    subtitle: geladen ? `${STATUS[geladen.status] ?? geladen.status}: ${geladen.credit_note_number}` : salesGutschriftScreen.subtitle,
    layout: { ...salesGutschriftScreen.layout, density: isTouch ? 'comfortable' : 'compact' },
    summary: salesGutschriftScreen.summary.map((eintrag) => ({
      ...eintrag,
      value: eintrag.key === 'netto'
        ? euro(steuer?.netto ?? 0)
        : steuer?.geklaert
          ? euro(eintrag.key === 'steuer' ? steuer.steuer : steuer.brutto)
          : 'offen',
    })),
    fields: salesGutschriftScreen.fields.map((feld) => ({
      ...feld,
      readOnly: gespeichert,
      ...(feld.key === 'pos_tax_code'
        ? {
            // Verkaufsbeleg: reine Vorsteuerschluessel gehoeren nicht in die Auswahl.
            options: schluessel
              .filter((k) => !(k.debit_account && !k.credit_account))
              .map((k) => ({ value: k.code, label: `${k.code} – ${k.bezeichnung} (${Number(k.steuersatz).toLocaleString('de-DE')} %)` })),
            placeholder: schluessel.length === 0 ? 'Kein Steuerschlüssel eingerichtet' : 'Steuerschlüssel wählen',
          }
        : {}),
    })),
    actions: salesGutschriftScreen.actions.map((aktion) => ({
      ...aktion,
      disabled: laeuft !== null
        || ((aktion.key === 'position' || aktion.key === 'speichern') && gespeichert)
        || (aktion.key === 'buchen' && (!gespeichert || gebucht)),
    })),
  }), [gebucht, geladen, gespeichert, isTouch, laeuft, schluessel, steuer])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema, { permissions: RECHTE }), [schema])
  const form = useUniversalFormState({ screen: schema, initialValues: leer })
  const { resetForm, setValue } = form

  // Ein Ablauf zur Zeit: der Schluessel zeigt, welcher, und sperrt alle Knoepfe.
  const mitSperre = useCallback(async (schluesselName: string, arbeit: () => Promise<void>) => {
    if (sperre.current) return
    sperre.current = true
    setLaeuft(schluesselName)
    try {
      await arbeit()
    } finally {
      sperre.current = false
      setLaeuft(null)
    }
  }, [])

  const neuLaden = useCallback(async () => {
    await queryClient.invalidateQueries({ queryKey: ['sales-gutschriften'] })
  }, [queryClient])

  const zeige = useCallback((gutschrift: Gutschrift | null) => {
    setGeladen(gutschrift)
    setPruefgrund(null)
    setPositionen((gutschrift?.lines ?? []).map((z) => ({
      description: z.description, quantity: Number(z.quantity), unit_price: Number(z.unit_price), tax_code: z.tax_code ?? null,
    })))
    resetForm(gutschrift
      ? {
          ...leer,
          credit_note_number: gutschrift.credit_note_number,
          customer_id: gutschrift.customer_id,
          customer_name: gutschrift.customer_name ?? '',
          invoice_reference: gutschrift.invoice_reference ?? '',
          correction_type: gutschrift.correction_type,
          reason: gutschrift.reason,
          notes: gutschrift.notes ?? '',
        }
      : { ...leer })
  }, [resetForm])

  const positionUebernehmen = useCallback(() => {
    const werte = form.values
    if (!text(werte.pos_description) || zahl(werte.pos_quantity) <= 0 || zahl(werte.pos_unit_price) <= 0) {
      toast.error('Position unvollständig', { description: 'Bezeichnung, Menge und Einzelpreis eintragen.' })
      return
    }
    setPositionen((alt) => [...alt, {
      description: text(werte.pos_description),
      quantity: zahl(werte.pos_quantity),
      unit_price: zahl(werte.pos_unit_price),
      tax_code: text(werte.pos_tax_code) || null,
    }])
    Object.entries(POSITION_LEER).forEach(([feld, wert]) => setValue(feld, wert))
  }, [form.values, setValue])

  const speichern = useCallback(() => mitSperre('speichern', async () => {
    const werte = form.values
    if (!text(werte.credit_note_number) || !text(werte.customer_id) || !text(werte.reason) || positionen.length === 0) {
      form.revealErrors?.()
      toast.error('Gutschrift unvollständig', { description: 'Nummer, Kunde, Grund und mindestens eine Position angeben.' })
      return
    }
    try {
      const nummer = text(werte.credit_note_number)
      const ergebnis = await speichereGutschrift({
        credit_note_number: nummer,
        customer_id: text(werte.customer_id),
        customer_name: text(werte.customer_name) || null,
        invoice_reference: text(werte.invoice_reference) || null,
        reason: text(werte.reason_text) ? `${text(werte.reason)}: ${text(werte.reason_text)}` : text(werte.reason),
        correction_type: text(werte.correction_type) || 'rechnungskorrektur',
        notes: text(werte.notes) || null,
        lines: positionen,
      }, `gutschrift-speichern-${nummer}`)
      if (!ergebnis.success) {
        toast.error('Gutschrift nicht gespeichert', { description: ergebnis.error ?? 'Die Eingabe wurde abgelehnt.' })
        return
      }
      toast.success('Entwurf gespeichert', { description: ergebnis.summary ?? undefined })
      await neuLaden()
      const neu = (await listeGutschriften()).find((g) => g.credit_note_number === nummer)
      if (neu) zeige(await ladeGutschrift(neu.id))
    } catch (fehler) {
      toast.error('Gutschrift nicht gespeichert', { description: getAxiosErrorMessage(fehler) })
    }
  }), [form, mitSperre, neuLaden, positionen, zeige])

  const buchen = useCallback(() => mitSperre('buchen', async () => {
    if (!geladen) return
    try {
      const ergebnis = await bucheGutschrift(geladen.id, `gutschrift-buchen-${geladen.id}`)
      if (!ergebnis.success) {
        const grund = ergebnis.error ?? 'Die Buchung wurde abgelehnt.'
        setPruefgrund(grund)
        toast.error('Nicht gebucht', { description: `${grund} Die Gutschrift bleibt Entwurf.` })
        return
      }
      toast.success('Gutschrift gebucht', { description: ergebnis.summary ?? undefined })
      await neuLaden()
      zeige(await ladeGutschrift(geladen.id))
    } catch (fehler) {
      toast.error('Nicht gebucht', { description: getAxiosErrorMessage(fehler) })
    } finally {
      setBuchenFragen(false)
    }
  }), [geladen, mitSperre, neuLaden, zeige])

  const oeffnen = useCallback((id: unknown) => mitSperre('laden', async () => {
    try {
      zeige(await ladeGutschrift(String(id)))
    } catch (fehler) {
      toast.error('Gutschrift nicht geladen', { description: getAxiosErrorMessage(fehler) })
    }
  }), [mitSperre, zeige])

  const screenContext = useMemo(() => createScreenContext({
    data: { gutschriften, positionen },
    permissions: { granted: RECHTE },
    state: { values: form.values, policies: {} },
    actions: {
      'sales.gutschriftPosition': () => positionUebernehmen(),
      'sales.gutschriftSpeichern': () => speichern(),
      'sales.gutschriftBuchen': () => setBuchenFragen(true),
      'sales.gutschriftNeu': () => zeige(null),
      'sales.gutschriftLaden': (payload) => oeffnen(payload.id),
      'sales.gutschriftPositionEntfernen': (payload) => {
        if (gespeichert) return
        setPositionen((alt) => alt.filter((_, index) => index !== Number(payload.id)))
      },
    },
    navigation: { push: () => undefined },
  }), [form.values, gespeichert, gutschriften, oeffnen, positionUebernehmen, positionen, speichern, zeige])

  const workflow = useMemo<WorkflowState>(() => {
    const ohneSchluessel = positionen.some((p) => !p.tax_code)
    const naechste = gebucht
      ? 'Gebucht. Neue Gutschrift erfassen.'
      : pruefgrund
        ? 'Buchung abgelehnt: Prüfgrund klären (Steuerschlüssel, Konten, Belegbetrag).'
        : gespeichert
          ? 'Entwurf buchen.'
          : positionen.length === 0
            ? 'Position erfassen und übernehmen.'
            : ohneSchluessel
              ? 'Steuerschlüssel für jede Position wählen; ohne ihn wird nicht gebucht.'
              : 'Als Entwurf speichern.'
    const hinweise = [pruefgrund, steuer && !steuer.geklaert ? steuer.pruefgrund : null].filter(Boolean) as string[]
    return {
      status: {
        currentStatus: gebucht ? 'gebucht' : gespeichert ? 'entwurf' : 'erfassen',
        statusLabel: gebucht ? 'Gebucht' : gespeichert ? 'Entwurf' : 'Erfassen',
        tone: gebucht ? 'success' : hinweise.length > 0 ? 'warning' : 'info',
      },
      nextAllowedActions: [{
        actionKey: gebucht ? 'neu' : gespeichert ? 'buchen' : positionen.length === 0 ? 'position' : 'speichern',
        label: naechste,
        dangerLevel: gespeichert && !gebucht ? 'moderate' : 'safe',
        requiresConfirmation: gespeichert && !gebucht,
      }],
      blockingReasons: hinweise.map((meldung, index) => ({ code: `steuer-${index}`, message: meldung, blocking: true })),
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: gebucht,
    }
  }, [gebucht, gespeichert, positionen, pruefgrund, steuer])

  if (liste.isLoading) {
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
          positionen: positionen.map((p, index) => ({
            id: String(index),
            nr: index + 1,
            description: p.description,
            quantity: p.quantity,
            unit_price: p.unit_price,
            tax_code_text: schluesselText(p.tax_code, schluessel),
            netto: p.quantity * p.unit_price,
          })),
          steuer: (steuer?.gruppen ?? []).map((g) => ({
            id: g.tax_code,
            tax_code_text: `${schluesselText(g.tax_code, schluessel)} (${Number(g.satz).toLocaleString('de-DE')} %)`,
            netto: Number(g.netto),
            steuer: Number(g.steuer),
            brutto: Number(g.brutto),
          })),
          gutschriften: gutschriften.map((g) => ({
            id: g.id,
            credit_note_number: g.credit_note_number,
            customer_text: g.customer_name ? `${g.customer_name} (${g.customer_id})` : g.customer_id,
            invoice_reference: g.invoice_reference ?? '–',
            net_amount: g.net_amount == null ? null : Number(g.net_amount),
            tax_amount: g.tax_amount == null ? null : Number(g.tax_amount),
            total_amount: Number(g.total_amount),
            status: g.status,
            status_text: STATUS[g.status] ?? g.status,
          })),
        }}
      />
      <AlertDialog open={buchenFragen} onOpenChange={(offen) => { if (!offen && laeuft === null) setBuchenFragen(false) }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Gutschrift {geladen?.credit_note_number} buchen?</AlertDialogTitle>
            <AlertDialogDescription>
              Gebucht wird der Erlös netto, die Umsatzsteuer getrennt und die Forderung brutto
              {geladen?.invoice_reference ? `; der offene Posten der Rechnung ${geladen.invoice_reference} wird gemindert` : ''}.
              Eine Buchung lässt sich nicht löschen, nur stornieren.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={laeuft !== null}>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              disabled={laeuft !== null}
              onClick={(event) => {
                event.preventDefault()
                void buchen()
              }}
            >
              Buchen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
