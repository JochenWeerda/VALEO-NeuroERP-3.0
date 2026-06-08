/**
 * LKW-Registrierung - Touch-optimierter Feldworkflow (Gap 024, Wave 76)
 * Prioritaet via TouchCards statt <select>, alle Touch-Targets >= 44px
 */
import { useState, useCallback, useEffect } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/react-router-compat'
import { useDropzone } from 'react-dropzone'
import { useToast } from '@/hooks/use-toast'
import { Wizard } from '@/components/patterns/Wizard'
import { api } from '@/lib/axios'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { Camera, Clock, Truck, Upload, X } from 'lucide-react'
import {
  TouchSection,
  TouchTextInput,
  TouchCard,
  TouchCardGroup,
  TouchConfirmCard,
} from '@/components/touch/TouchFieldLayout'
import { WorkflowEntryBanner, readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'

type LKWData = {
  kennzeichen: string
  lieferant: string
  lieferscheinNr: string
  articleId: string | null
  artikel: string
  ankunftszeit: string
  prioritaet: 'hoch' | 'normal' | 'niedrig'
}

type ArticleOption = {
  id: string
  label: string
}

const FALLBACK_ARTIKEL_OPTIONEN: ArticleOption[] = [
  'Weizen',
  'Gerste',
  'Raps',
  'Mais',
  'Roggen',
  'Hafer',
  'Sonnenblumen',
].map((label) => ({ id: label, label }))

export default function LKWRegistrierungPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { toast } = useToast()
  const workflowContext = readWorkflowEntryContext(searchParams)
  const [lkw, setLKW] = useState<LKWData>({
    kennzeichen: '',
    lieferant: '',
    lieferscheinNr: '',
    articleId: null,
    artikel: '',
    ankunftszeit: new Date().toISOString().slice(0, 16),
    prioritaet: 'normal',
  })
  const [artikelOptionen, setArtikelOptionen] = useState<ArticleOption[]>(FALLBACK_ARTIKEL_OPTIONEN)
  const [attachmentIds, setAttachmentIds] = useState<string[]>([])
  const [uploading, setUploading] = useState(false)
  const [scanDialogField, setScanDialogField] = useState<'kennzeichen' | 'lieferscheinNr' | null>(null)
  const [scanInputValue, setScanInputValue] = useState('')

  function updateField<K extends keyof LKWData>(key: K, value: LKWData[K]): void {
    setLKW((prev) => ({ ...prev, [key]: value }))
  }

  useEffect(() => {
    let active = true

    const loadArticles = async (): Promise<void> => {
      try {
        const response = await api.get<{ items?: Array<{ id: string; name?: string; article_number?: string }> }>('/api/v1/articles?limit=100')
        const items =
          response.data?.items
            ?.map((item) => ({
              id: item.id,
              label: item.name || item.article_number || item.id,
            }))
            .filter((item) => item.id && item.label) ?? []
        if (!active || items.length === 0) {
          return
        }
        setArtikelOptionen(items)
      } catch {
        // Artikel-Dropdown bleibt leer — LKW-Registrierung ist trotzdem möglich
      }
    }

    void loadArticles()

    return () => {
      active = false
    }
  }, [])

  const uploadAttachment = useCallback(
    async (file: File): Promise<string | null> => {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await api.post<{ id: string }>('/api/v1/annahme/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data?.id ?? null
    },
    [],
  )

  const onDropKennzeichen = useCallback(
    async (accepted: File[]) => {
      if (accepted.length === 0) return
      setUploading(true)
      try {
        for (const file of accepted) {
          const id = await uploadAttachment(file)
          if (id) setAttachmentIds((prev) => [...prev, id])
        }
      } catch (e: any) {
        toast({
          title: 'Upload fehlgeschlagen',
          description: e.response?.data?.detail ?? e.message,
          variant: 'destructive',
        })
      } finally {
        setUploading(false)
      }
    },
    [uploadAttachment, toast],
  )

  const onDropLieferschein = useCallback(
    async (accepted: File[]) => {
      if (accepted.length === 0) return
      setUploading(true)
      try {
        for (const file of accepted) {
          const id = await uploadAttachment(file)
          if (id) setAttachmentIds((prev) => [...prev, id])
        }
      } catch (e: any) {
        toast({
          title: 'Upload fehlgeschlagen',
          description: e.response?.data?.detail ?? e.message,
          variant: 'destructive',
        })
      } finally {
        setUploading(false)
      }
    },
    [uploadAttachment, toast],
  )

  const dropzoneCommon = {
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'] },
    maxSize: 10 * 1024 * 1024,
    multiple: true,
    disabled: uploading,
  }
  const dropzoneKennzeichen = useDropzone({
    ...dropzoneCommon,
    onDrop: onDropKennzeichen,
  })
  const dropzoneLieferschein = useDropzone({
    ...dropzoneCommon,
    onDrop: onDropLieferschein,
  })

  function handleScan(field: 'kennzeichen' | 'lieferscheinNr'): void {
    setScanInputValue(field === 'kennzeichen' ? lkw.kennzeichen : lkw.lieferscheinNr)
    setScanDialogField(field)
  }

  function applyScannedValue(): void {
    if (!scanDialogField) return
    const normalizedValue = scanDialogField === 'kennzeichen' ? scanInputValue.toUpperCase().trim() : scanInputValue.trim()
    if (!normalizedValue) {
      toast({
        title: 'Kein Scanwert vorhanden',
        description: 'Bitte Wert aus Handscanner, Kamera-App oder OCR einfuegen.',
        variant: 'destructive',
      })
      return
    }
    updateField(scanDialogField, normalizedValue as LKWData[typeof scanDialogField])
    setScanDialogField(null)
    toast({
      title: 'Scanwert uebernommen',
      description: scanDialogField === 'kennzeichen' ? `Kennzeichen ${normalizedValue} uebernommen.` : `Lieferschein ${normalizedValue} uebernommen.`,
    })
  }

  function removeAttachment(index: number): void {
    setAttachmentIds((prev) => prev.filter((_, i) => i !== index))
  }

  const validateStep = (stepId: string): string | null => {
    if (stepId === 'kennzeichen') {
      if (!lkw.kennzeichen.trim()) {
        return 'Kennzeichen ist ein Pflichtfeld.'
      }
      return null
    }
    if (stepId === 'lieferung') {
      if (!lkw.lieferant.trim()) {
        return 'Lieferant ist ein Pflichtfeld.'
      }
      if (!lkw.articleId && !lkw.artikel.trim()) {
        return 'Artikel ist ein Pflichtfeld.'
      }
    }
    return null
  }

  const handleStepValidationError = (_stepId: string, message: string): void => {
    toast({
      title: 'Schritt unvollstaendig',
      description: message,
      variant: 'destructive',
    })
  }

  async function handleSubmit(): Promise<void> {
    try {
      await api.post('/api/v1/annahme/lkw-registrierung', {
        kennzeichen: lkw.kennzeichen,
        lieferant: lkw.lieferant,
        lieferschein_nr: lkw.lieferscheinNr,
        article_id: lkw.articleId,
        artikel: lkw.artikel,
        ankunftszeit: lkw.ankunftszeit || new Date().toISOString(),
        prioritaet: lkw.prioritaet,
        attachment_ids: attachmentIds,
      })
      toast({
        title: 'LKW registriert',
        description: `${lkw.kennzeichen} - ${lkw.artikel} - wurde in die Warteschlange eingereiht.`,
      })
      navigate('/annahme/warteschlange')
    } catch (e: any) {
      toast({
        title: 'Registrierung fehlgeschlagen',
        description: e.response?.data?.detail ?? e.message,
        variant: 'destructive',
      })
    }
  }

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => { void handleSubmit() },
    onCancel: () => navigate('/annahme/warteschlange'),
  })
  useKeyboardShortcuts(shortcuts)

  const PRIORITAETEN = [
    { id: 'hoch', label: 'Hoch (Express)', description: 'Sofortige Bearbeitung' },
    { id: 'normal', label: 'Normal', description: 'Standard-Warteschlange' },
    { id: 'niedrig', label: 'Niedrig', description: 'Flexibel, kein Zeitdruck' },
  ] as const

  const steps = [
    {
      id: 'kennzeichen',
      title: 'Kennzeichen',
      content: (
        <TouchSection>
          <div className="flex items-center justify-center py-2">
            <Truck className="h-16 w-16 text-slate-300" />
          </div>
          <div className="space-y-1">
            <TouchTextInput
              label="Kennzeichen"
              value={lkw.kennzeichen}
              onChange={(v) => updateField('kennzeichen', v.toUpperCase())}
              placeholder="z.B. AB-CD 1234"
              autoCapitalize="characters"
              required
            />
            <Button
              type="button"
              variant="outline"
              className="w-full min-h-[44px] gap-2"
              onClick={() => handleScan('kennzeichen')}
            >
              <Camera className="h-4 w-4" />
              Kennzeichen scannen / uebernehmen
            </Button>
          </div>
          <div>
            <p className="mb-2 text-base font-medium text-slate-700">Foto Kennzeichen (optional)</p>
            <div
              {...dropzoneKennzeichen.getRootProps()}
              className="flex min-h-[80px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-4 text-center transition-colors hover:border-blue-400 hover:bg-blue-50"
            >
              <input {...dropzoneKennzeichen.getInputProps()} accept="image/*" capture="environment" aria-label="Foto Kennzeichen hochladen" />
              <Upload className="mb-1 h-6 w-6 text-slate-400" />
              <p className="text-sm text-slate-500">
                {dropzoneKennzeichen.isDragActive ? 'Ablegen...' : 'Tippen oder Foto hierher ziehen'}
              </p>
            </div>
          </div>
          <div className="space-y-1">
            <label htmlFor="ankunftszeit" className="block text-base font-medium text-slate-700">Ankunftszeit</label>
            <input
              id="ankunftszeit"
              type="datetime-local"
              value={lkw.ankunftszeit}
              onChange={(e) => updateField('ankunftszeit', e.target.value)}
              className="flex w-full min-h-[54px] rounded-lg border-2 border-slate-200 bg-white px-4 py-3 text-lg text-slate-900 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </TouchSection>
      ),
    },
    {
      id: 'lieferung',
      title: 'Lieferung',
      content: (
        <TouchSection>
          <TouchTextInput
            label="Lieferant"
            value={lkw.lieferant}
            onChange={(v) => updateField('lieferant', v)}
            placeholder="Name des Lieferanten"
            required
          />
          <div className="space-y-1">
            <TouchTextInput
              label="Lieferschein-Nr."
              value={lkw.lieferscheinNr}
              onChange={(v) => updateField('lieferscheinNr', v)}
              placeholder="z.B. LS-2025-0042"
            />
            <Button
              type="button"
              variant="outline"
              className="w-full min-h-[44px] gap-2"
              onClick={() => handleScan('lieferscheinNr')}
            >
              <Camera className="h-4 w-4" />
              Lieferschein scannen / uebernehmen
            </Button>
          </div>
          <div>
            <p className="mb-2 text-base font-medium text-slate-700">Foto Lieferschein (optional)</p>
            <div
              {...dropzoneLieferschein.getRootProps()}
              className="flex min-h-[80px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-4 text-center transition-colors hover:border-blue-400 hover:bg-blue-50"
            >
              <input {...dropzoneLieferschein.getInputProps()} accept="image/*" capture="environment" aria-label="Foto Lieferschein hochladen" />
              <Upload className="mb-1 h-6 w-6 text-slate-400" />
              <p className="text-sm text-slate-500">
                {dropzoneLieferschein.isDragActive ? 'Ablegen...' : 'Tippen oder Foto hierher ziehen'}
              </p>
            </div>
          </div>
          <TouchCardGroup label="Artikel" required>
            {artikelOptionen.map((art) => (
              <TouchCard
                key={art.id}
                selected={lkw.articleId === art.id || (!lkw.articleId && lkw.artikel === art.label)}
                onSelect={() => setLKW((prev) => ({ ...prev, articleId: art.id, artikel: art.label }))}
              >
                {art.label}
              </TouchCard>
            ))}
          </TouchCardGroup>
          <TouchCardGroup label="Prioritaet">
            {PRIORITAETEN.map((p) => (
              <TouchCard
                key={p.id}
                selected={lkw.prioritaet === p.id}
                onSelect={() => updateField('prioritaet', p.id)}
                description={p.description}
              >
                {p.label}
              </TouchCard>
            ))}
          </TouchCardGroup>
        </TouchSection>
      ),
    },
    {
      id: 'bestaetigung',
      title: 'Bestaetigung',
      content: (
        <div className="space-y-5">
          <div className="flex flex-col items-center gap-2 py-2">
            <div className="rounded-full bg-slate-100 p-5">
              <Truck className="h-12 w-12 text-slate-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-900">{lkw.kennzeichen || 'KENNZEICHEN'}</h3>
          </div>
          <TouchConfirmCard
            title="Lieferungsdetails"
            fields={[
              { label: 'Lieferant', value: lkw.lieferant || '-' },
              { label: 'Lieferschein-Nr.', value: lkw.lieferscheinNr || '-' },
              { label: 'Artikel', value: lkw.artikel || '-', highlight: true },
              { label: 'Ankunft', value: new Date(lkw.ankunftszeit).toLocaleString('de-DE') },
              { label: 'Prioritaet', value: lkw.prioritaet === 'hoch' ? 'Hoch (Express)' : lkw.prioritaet === 'normal' ? 'Normal' : 'Niedrig', highlight: lkw.prioritaet === 'hoch' },
            ]}
          />
          {attachmentIds.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {attachmentIds.map((id, i) => (
                <Badge key={id} variant="secondary" className="gap-1">
                  Anhang #{i + 1}
                  <button type="button" onClick={() => removeAttachment(i)} aria-label="Entfernen">
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          )}
          <div className="rounded-xl bg-blue-50 px-4 py-3 text-center text-sm text-blue-900">
            <p className="font-semibold">LKW wird in die Warteschlange eingereiht</p>
            <p className="mt-0.5 flex items-center justify-center gap-1 text-blue-700">
              <Clock className="h-3.5 w-3.5" />
              Der Fahrer erhaelt eine Wartenummer
            </p>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
      <div className="p-6">
        {workflowContext ? <div className="mb-6"><WorkflowEntryBanner context={workflowContext} /></div> : null}
        <div className="mb-6 space-y-6">
          <OperationalCaseHeader
            title={lkw.kennzeichen || 'LKW-Registrierung'}
            description="Anlieferung als gefuehrter Annahmevorgang mit Scanquelle, Ressourcenlage und naechster Aktion."
            status={attachmentIds.length > 0 || lkw.lieferscheinNr ? 'in_pruefung' : 'offen'}
            owner="Annahme / Waage"
            blocker={!lkw.kennzeichen ? 'Kennzeichen fehlt fuer die eindeutige Fahrzeugzuordnung.' : null}
            nextAction={
              !lkw.kennzeichen
                ? 'Kennzeichen erfassen'
                : !lkw.lieferant || (!lkw.articleId && !lkw.artikel)
                  ? 'Lieferant und Artikel zuordnen'
                  : 'Annahme registrieren und in Warteschlange uebergeben'
            }
            caseLabel={workflowContext?.caseNumber || 'Annahmevorgang'}
            tags={[lkw.prioritaet, lkw.articleId ? 'Artikel zugeordnet' : 'Artikel offen']}
          />
          <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
            <OperationalTimeline
              title="Annahme-Timeline"
              items={[
                {
                  label: 'Fahrzeugdaten',
                  detail: lkw.kennzeichen ? `Kennzeichen ${lkw.kennzeichen} uebernommen.` : 'Kennzeichen noch offen.',
                },
                {
                  label: 'Beleg- und Scanpfad',
                  detail: lkw.lieferscheinNr ? `Lieferschein ${lkw.lieferscheinNr} uebernommen.` : 'Lieferschein noch nicht uebernommen.',
                },
                {
                  label: 'Bildanhaenge',
                  detail: attachmentIds.length > 0 ? `${attachmentIds.length} Bild-/Scananhaenge verknuepft.` : 'Noch keine Bildanhaenge vorhanden.',
                },
              ]}
            />
            <OperationalContextPanel
              title="Annahmekontext"
              sections={[
                {
                  title: 'Ressourcenlage',
                  items: [
                    { label: 'Artikel', value: lkw.artikel || 'Noch nicht zugeordnet' },
                    { label: 'Ankunft', value: lkw.ankunftszeit ? new Date(lkw.ankunftszeit).toLocaleString('de-DE') : '-' },
                  ],
                },
                {
                  title: 'Logistiklage',
                  items: [
                    { label: 'Lieferant', value: lkw.lieferant || 'Noch offen' },
                    { label: 'Prioritaet', value: lkw.prioritaet },
                  ],
                },
                {
                  title: 'Governance',
                  items: [
                    { label: 'Scanquelle', value: scanDialogField ? 'Scanner/OCR aktiv' : 'Touch / Upload' },
                    { label: 'Naechste Aktion', value: lkw.kennzeichen && (lkw.articleId || lkw.artikel) ? 'Warteschlange buchen' : 'Pflichtfelder vervollstaendigen' },
                  ],
                },
              ]}
            />
          </div>
        </div>
        <ModuleToolbar backTarget="/annahme/warteschlange" closeTarget="/annahme/warteschlange" title="LKW-Registrierung" />
        <Wizard
          title="LKW-Registrierung"
          steps={steps}
          onFinish={handleSubmit}
          onCancel={() => navigate('/annahme/warteschlange')}
          getStepValidationError={validateStep}
          onStepValidationError={handleStepValidationError}
        />
        <Dialog open={!!scanDialogField} onOpenChange={(open) => !open && setScanDialogField(null)}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Scan - Kennzeichen / Lieferschein</DialogTitle>
              <DialogDescription>
                Werte aus Handscanner, Kamera-App oder OCR koennen direkt in den Touch-Workflow uebernommen werden.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-3 py-2">
              <label className="text-sm font-medium text-slate-700" htmlFor="scan-input">
                {scanDialogField === 'kennzeichen' ? 'Kennzeichen aus Scanner oder OCR' : 'Lieferschein-Nr. aus Scanner oder OCR'}
              </label>
              <input
                id="scan-input"
                type="text"
                value={scanInputValue}
                onChange={(event) => setScanInputValue(event.target.value)}
                placeholder={scanDialogField === 'kennzeichen' ? 'z.B. AB-CD 1234' : 'z.B. LS-2026-0042'}
                className="flex w-full min-h-[52px] rounded-lg border-2 border-slate-200 bg-white px-4 py-3 text-lg text-slate-900 focus:border-blue-500 focus:outline-none"
                autoFocus
              />
              <div className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-600">
                {scanDialogField === 'kennzeichen'
                  ? 'Praxispfad: Scanner als Tastaturkeil oder OCR-App verwenden, Wert hier pruefen und direkt in den Vorgang uebernehmen. Das Foto-Upload-Feld darunter bleibt fuer Belegbilder nutzbar.'
                  : 'Praxispfad: Lieferschein per Scanner oder OCR erfassen, Nummer hier pruefen und in die Registrierung uebernehmen. Das Foto-Upload-Feld darunter bleibt fuer den eigentlichen Beleg nutzbar.'}
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setScanDialogField(null)}>Schliessen</Button>
              <Button onClick={applyScannedValue}>Uebernehmen</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
