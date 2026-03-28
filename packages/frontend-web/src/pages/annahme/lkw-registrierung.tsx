/**
 * LKW-Registrierung — Touch-optimierter Feldworkflow (Gap 024, Wave 76)
 * Priorität via TouchCards statt <select>, alle Touch-Targets >= 44px
 */
import { useState, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
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
  const { toast } = useToast()
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
      } catch (error) {
        console.warn('Article options for LKW registration could not be loaded:', error)
      }
    }

    void loadArticles()

    return () => {
      active = false
    }
  }, [])

  /** Datei an Backend senden, ID in attachmentIds aufnehmen. */
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

  /** Scan-Button: öffnet Info-Dialog (Foto-Upload nutzen oder manuell eingeben; Barcode-Scanner in Planung). */
  function handleScan(field: 'kennzeichen' | 'lieferscheinNr'): void {
    setScanDialogField(field)
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
        description: `${lkw.kennzeichen} — ${lkw.artikel} — wurde in die Warteschlange eingereiht.`,
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
              Kennzeichen scannen (in Kürze)
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
                {dropzoneKennzeichen.isDragActive ? 'Ablegen…' : 'Tippen oder Foto hierher ziehen'}
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
              Lieferschein scannen (in Kürze)
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
                {dropzoneLieferschein.isDragActive ? 'Ablegen…' : 'Tippen oder Foto hierher ziehen'}
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
          <TouchCardGroup label="Priorität">
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
      title: 'Bestätigung',
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
              { label: 'Lieferant', value: lkw.lieferant || '—' },
              { label: 'Lieferschein-Nr.', value: lkw.lieferscheinNr || '—' },
              { label: 'Artikel', value: lkw.artikel || '—', highlight: true },
              { label: 'Ankunft', value: new Date(lkw.ankunftszeit).toLocaleString('de-DE') },
              { label: 'Priorität', value: lkw.prioritaet === 'hoch' ? 'Hoch (Express)' : lkw.prioritaet === 'normal' ? 'Normal' : 'Niedrig', highlight: lkw.prioritaet === 'hoch' },
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
              Der Fahrer erhält eine Wartenummer
            </p>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
      <div className="p-6">
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
            <DialogTitle>Scan – Kennzeichen / Lieferschein</DialogTitle>
            <DialogDescription>
              Foto-Upload oder manuelle Eingabe fuer Kennzeichen und Lieferschein im Touch-Workflow.
            </DialogDescription>
          </DialogHeader>
          <p className="text-sm text-muted-foreground py-2">
            {scanDialogField === 'kennzeichen'
              ? 'Nutzen Sie das Foto-Upload-Feld unter dem Kennzeichen-Eingabefeld, um ein Bild hochzuladen, oder geben Sie das Kennzeichen manuell ein. Barcode-Scanner-Anbindung ist in Planung.'
              : 'Nutzen Sie das Foto-Upload-Feld unter der Lieferschein-Nr., um ein Bild hochzuladen, oder geben Sie die Nummer manuell ein. Barcode-Scanner-Anbindung ist in Planung.'}
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setScanDialogField(null)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
