import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { useToast } from '@/hooks/use-toast'
import { Wizard } from '@/components/patterns/Wizard'
import { api } from '@/lib/axios'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { Camera, Clock, Truck, Upload, X } from 'lucide-react'

type LKWData = {
  kennzeichen: string
  lieferant: string
  lieferscheinNr: string
  artikel: string
  ankunftszeit: string
  prioritaet: 'hoch' | 'normal' | 'niedrig'
}

export default function LKWRegistrierungPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [lkw, setLKW] = useState<LKWData>({
    kennzeichen: '',
    lieferant: '',
    lieferscheinNr: '',
    artikel: '',
    ankunftszeit: new Date().toISOString().slice(0, 16),
    prioritaet: 'normal',
  })
  const [attachmentIds, setAttachmentIds] = useState<string[]>([])
  const [uploading, setUploading] = useState(false)
  const [scanDialogField, setScanDialogField] = useState<'kennzeichen' | 'lieferscheinNr' | null>(null)

  function updateField<K extends keyof LKWData>(key: K, value: LKWData[K]): void {
    setLKW((prev) => ({ ...prev, [key]: value }))
  }

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

  async function handleSubmit(): Promise<void> {
    try {
      await api.post('/api/v1/annahme/lkw-registrierung', {
        kennzeichen: lkw.kennzeichen,
        lieferant: lkw.lieferant,
        lieferschein_nr: lkw.lieferscheinNr,
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

  const steps = [
    {
      id: 'kennzeichen',
      title: 'Kennzeichen',
      content: (
        <div className="space-y-6">
          <div className="flex items-center justify-center">
            <Truck className="h-24 w-24 text-muted-foreground" />
          </div>
          <div>
            <Label htmlFor="kennzeichen">Kennzeichen *</Label>
            <div className="flex gap-2">
              <Input
                id="kennzeichen"
                value={lkw.kennzeichen}
                onChange={(e) => updateField('kennzeichen', e.target.value.toUpperCase())}
                placeholder="z.B. AB-CD 1234"
                required
                className="text-lg font-semibold text-center"
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-2"
                onClick={() => handleScan('kennzeichen')}
                title="Kennzeichen scannen (in Kürze)"
              >
                <Camera className="h-4 w-4" />
                Scan
              </Button>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              Kennzeichen eingeben oder Foto/Barcode hochladen (mobil geeignet)
            </p>
          </div>
          <div>
            <Label>Foto Kennzeichen / Barcode (optional)</Label>
            <div
              {...dropzoneKennzeichen.getRootProps()}
              className="mt-2 rounded-lg border-2 border-dashed border-muted-foreground/30 bg-muted/30 p-4 text-center cursor-pointer hover:border-primary/50 hover:bg-muted/50 transition-colors min-h-[100px] flex flex-col items-center justify-center"
            >
              <input {...dropzoneKennzeichen.getInputProps()} accept="image/*" capture="environment" />
              <Upload className="h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-sm font-medium">
                {dropzoneKennzeichen.isDragActive ? 'Ablegen…' : 'Tippen oder Foto hierher ziehen'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Bild von Kamera oder Galerie (iOS/Android)</p>
            </div>
          </div>
          <div>
            <Label htmlFor="ankunftszeit">Ankunftszeit</Label>
            <Input
              id="ankunftszeit"
              type="datetime-local"
              value={lkw.ankunftszeit}
              onChange={(e) => updateField('ankunftszeit', e.target.value)}
            />
          </div>
        </div>
      ),
    },
    {
      id: 'lieferung',
      title: 'Lieferung',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="lieferant">Lieferant *</Label>
            <Input
              id="lieferant"
              value={lkw.lieferant}
              onChange={(e) => updateField('lieferant', e.target.value)}
              placeholder="Name des Lieferanten"
              required
            />
          </div>
          <div>
            <Label htmlFor="lieferscheinNr">Lieferschein-Nr.</Label>
            <div className="flex gap-2">
              <Input
                id="lieferscheinNr"
                value={lkw.lieferscheinNr}
                onChange={(e) => updateField('lieferscheinNr', e.target.value)}
                placeholder="z.B. LS-2025-0042"
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-2"
                onClick={() => handleScan('lieferscheinNr')}
                title="Lieferschein-Nr. scannen (in Kürze)"
              >
                <Camera className="h-4 w-4" />
                Scan
              </Button>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              Lieferschein-Nr. eingeben oder Foto/Barcode hochladen
            </p>
          </div>
          <div>
            <Label>Foto Lieferschein / Barcode (optional)</Label>
            <div
              {...dropzoneLieferschein.getRootProps()}
              className="mt-2 rounded-lg border-2 border-dashed border-muted-foreground/30 bg-muted/30 p-4 text-center cursor-pointer hover:border-primary/50 hover:bg-muted/50 transition-colors min-h-[100px] flex flex-col items-center justify-center"
            >
              <input {...dropzoneLieferschein.getInputProps()} accept="image/*" capture="environment" />
              <Upload className="h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-sm font-medium">
                {dropzoneLieferschein.isDragActive ? 'Ablegen…' : 'Tippen oder Foto hierher ziehen'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Bild von Kamera oder Galerie (iOS/Android)</p>
            </div>
          </div>
          <div>
            <Label htmlFor="artikel">Artikel *</Label>
            <Input
              id="artikel"
              value={lkw.artikel}
              onChange={(e) => updateField('artikel', e.target.value)}
              placeholder="z.B. Weizen"
              required
            />
          </div>
          <div>
            <Label htmlFor="prioritaet">Priorität</Label>
            <select
              id="prioritaet"
              value={lkw.prioritaet}
              onChange={(e) => updateField('prioritaet', e.target.value as LKWData['prioritaet'])}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="hoch">Hoch (Express)</option>
              <option value="normal">Normal</option>
              <option value="niedrig">Niedrig</option>
            </select>
          </div>
        </div>
      ),
    },
    {
      id: 'bestaetigung',
      title: 'Bestätigung',
      content: (
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-center mb-6">
                <div className="rounded-full bg-muted p-6">
                  <Truck className="h-16 w-16" />
                </div>
              </div>
              <h3 className="text-center text-2xl font-bold mb-6">{lkw.kennzeichen || 'KENNZEICHEN'}</h3>
              <dl className="grid gap-4">
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Lieferant</dt>
                  <dd className="text-sm font-semibold">{lkw.lieferant || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Lieferschein-Nr.</dt>
                  <dd className="text-sm font-semibold">{lkw.lieferscheinNr || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Artikel</dt>
                  <dd className="text-sm font-semibold">{lkw.artikel || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Ankunftszeit</dt>
                  <dd className="text-sm font-semibold flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    {new Date(lkw.ankunftszeit).toLocaleString('de-DE')}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-muted-foreground">Priorität</dt>
                  <dd>
                    <Badge
                      variant={lkw.prioritaet === 'hoch' ? 'destructive' : lkw.prioritaet === 'normal' ? 'default' : 'secondary'}
                    >
                      {lkw.prioritaet === 'hoch' ? 'Hoch (Express)' : lkw.prioritaet === 'normal' ? 'Normal' : 'Niedrig'}
                    </Badge>
                  </dd>
                </div>
                {attachmentIds.length > 0 && (
                  <div className="flex justify-between items-center border-t pt-2 mt-2">
                    <dt className="text-sm font-medium text-muted-foreground">Anhänge</dt>
                    <dd className="flex flex-wrap gap-1">
                      {attachmentIds.map((id, i) => (
                        <Badge key={id} variant="secondary" className="gap-1">
                          #{i + 1}
                          <button type="button" onClick={() => removeAttachment(i)} className="rounded hover:bg-muted-foreground/20" aria-label="Entfernen">
                            <X className="h-3 w-3" />
                          </button>
                        </Badge>
                      ))}
                    </dd>
                  </div>
                )}
              </dl>
            </CardContent>
          </Card>
          <div className="rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
            <p className="font-semibold">LKW wird in die Warteschlange eingereiht</p>
            <p className="mt-1">Der Fahrer erhält eine Wartenummer per SMS</p>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <ModuleToolbar backTarget="/annahme/warteschlange" closeTarget="/annahme/warteschlange" title="LKW-Registrierung" />
      <Wizard
        title="LKW-Registrierung"
        steps={steps}
        onFinish={handleSubmit}
        onCancel={() => navigate('/annahme/warteschlange')}
      />
      <Dialog open={!!scanDialogField} onOpenChange={(open) => !open && setScanDialogField(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Scan – Kennzeichen / Lieferschein</DialogTitle>
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
  )
}
