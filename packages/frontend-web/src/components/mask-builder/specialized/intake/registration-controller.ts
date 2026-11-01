import type { RenderPlan } from '../../render-plan/types'
import { canDomainAction, fieldsEditable, useDomainDispatch } from './domain-runtime'
import { useState, useCallback, useEffect } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { useDropzone } from 'react-dropzone'
import { useToast } from '@/hooks/use-toast'
import { api } from '@/lib/axios'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
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

export function useRegistrationController(plan: RenderPlan) {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
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
  const [artikelOptionen, setArtikelOptionen] = useState<ArticleOption[]>([])  // nur echte Artikel; vorher erfundene mit dem Namen als Kennung
  const [attachmentIds, setAttachmentIds] = useState<string[]>([])
  const [uploading, setUploading] = useState(false)
  const [scanDialogField, setScanDialogField] = useState<'kennzeichen' | 'lieferscheinNr' | null>(null)
  const [scanInputValue, setScanInputValue] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function updateField<K extends keyof LKWData>(key: K, value: LKWData[K]): void {
    if (!plan.fieldsByKey[key]?.visible || plan.fieldsByKey[key]?.readOnly) return
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
      if (!canDomainAction(plan, 'upload') || !fieldsEditable(plan, ['attachmentIds'])) return null
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await api.post<{ id: string }>('/api/v1/annahme/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data?.id ?? null
    },
    [plan],
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
      } catch (_rawErr: unknown) {
        const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
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
      } catch (_rawErr: unknown) {
        const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
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
    disabled: uploading || !canDomainAction(plan, 'upload') || !fieldsEditable(plan, ['attachmentIds']),
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
    if (!fieldsEditable(plan, ['attachmentIds'])) return
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
    if (submitting || !canDomainAction(plan, 'register') || !fieldsEditable(plan, ['kennzeichen', 'lieferant', 'lieferscheinNr', 'articleId', 'artikel', 'ankunftszeit', 'prioritaet'])) return
    const validationError = validateStep('kennzeichen') || validateStep('lieferung')
    if (validationError) { handleStepValidationError('lieferung', validationError); return }
    setSubmitting(true)
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
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({
        title: 'Registrierung fehlgeschlagen',
        description: e.response?.data?.detail ?? e.message,
        variant: 'destructive',
      })
    } finally {
      setSubmitting(false)
    }
  }

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => { void handleSubmit() },
    onCancel: () => navigate('/annahme/warteschlange'),
  })
  useKeyboardShortcuts(shortcuts)

  useDomainDispatch(plan, { register: handleSubmit, cancel: () => navigate('/annahme/warteschlange') })
  return { plan, navigate, isTouch, workflowContext, lkw, setLKW, artikelOptionen, attachmentIds, uploading, scanDialogField, setScanDialogField, scanInputValue, setScanInputValue, submitting, updateField, dropzoneKennzeichen, dropzoneLieferschein, handleScan, applyScannedValue, removeAttachment, validateStep, handleStepValidationError, handleSubmit, shortcuts }
}
export type RegistrationState = ReturnType<typeof useRegistrationController>
