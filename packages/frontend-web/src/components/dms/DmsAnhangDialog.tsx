/**
 * DMS Anhang-Dialog
 *
 * Universeller Dialog zum Anzeigen, Hochladen und Herunterladen von Dokumenten
 * aus Paperless-ngx. Verknüpfung über businessObjectType + businessObjectId.
 */

import { useState, useEffect, useCallback } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Loader2, Download, Trash2, FileText, AlertCircle } from 'lucide-react'
import { DropUpload } from '@/features/document/DropUpload'
import { dmsService, type Document } from '@/lib/services/dms-service'
import { useToast } from '@/components/ui/toast-provider'

const TENANT_ID = import.meta.env.VITE_TENANT_ID ?? ''

type DmsAnhangDialogProps = {
  open: boolean
  onClose: () => void
  businessObjectType: string
  businessObjectId: string | null
  title?: string
}

export function DmsAnhangDialog({
  open,
  onClose,
  businessObjectType,
  businessObjectId,
  title = 'UNTERLAGEN / DATEIEN',
}: DmsAnhangDialogProps): JSX.Element {
  const { push } = useToast()
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)

  const loadDocuments = useCallback(async (): Promise<void> => {
    if (!businessObjectId) return
    setLoading(true)
    try {
      const docs = await dmsService.getDocumentsForObject(
        TENANT_ID,
        businessObjectType,
        businessObjectId
      )
      setDocuments(docs)
    } catch {
      push('Dokumente konnten nicht geladen werden')
    } finally {
      setLoading(false)
    }
  }, [businessObjectId, businessObjectType, push])

  useEffect(() => {
    if (open && businessObjectId) {
      void loadDocuments()
    } else if (!open) {
      setDocuments([])
    }
  }, [open, businessObjectId, loadDocuments])

  const handleFiles = async (files: File[]): Promise<void> => {
    if (!businessObjectId) return
    setUploading(true)
    try {
      for (const file of files) {
        await dmsService.uploadDocument({
          file,
          tenantId: TENANT_ID,
          title: file.name,
          businessObjectType,
          businessObjectId,
        })
      }
      push(`${files.length} Datei(en) erfolgreich hochgeladen`)
      await loadDocuments()
    } catch {
      push('Upload fehlgeschlagen')
    } finally {
      setUploading(false)
    }
  }

  const handleDownload = async (doc: Document): Promise<void> => {
    try {
      const blob = await dmsService.downloadDocument(doc.id, TENANT_ID)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = doc.filename ?? doc.title
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      push('Download fehlgeschlagen')
    }
  }

  const handleDelete = async (doc: Document): Promise<void> => {
    try {
      await dmsService.deleteDocument(doc.id, TENANT_ID)
      push('Dokument gelöscht')
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id))
    } catch {
      push('Löschen fehlgeschlagen')
    }
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-auto space-y-4 py-2">
          {!businessObjectId ? (
            <div className="flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 p-4 text-amber-800">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <span>Bitte zuerst speichern, um Anhänge hinzuzufügen.</span>
            </div>
          ) : (
            <>
              <DropUpload onFiles={(files) => void handleFiles(files)} />

              {uploading && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Wird hochgeladen…
                </div>
              )}

              {loading ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Lade Dokumente…
                </div>
              ) : documents.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  Keine Anhänge vorhanden
                </p>
              ) : (
                <div className="space-y-1">
                  {documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center gap-2 rounded border border-input bg-background px-3 py-2 text-sm"
                    >
                      <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                      <span className="flex-1 truncate">{doc.title}</span>
                      {doc.sizeKb !== undefined && (
                        <span className="text-xs text-muted-foreground whitespace-nowrap">
                          {doc.sizeKb < 1024
                            ? `${doc.sizeKb} KB`
                            : `${(doc.sizeKb / 1024).toFixed(1)} MB`}
                        </span>
                      )}
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={() => void handleDownload(doc)}
                        title="Herunterladen"
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-destructive hover:text-destructive"
                        onClick={() => void handleDelete(doc)}
                        title="Löschen"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        <div className="flex justify-end pt-2 border-t">
          <Button variant="outline" onClick={onClose}>
            Schließen
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
