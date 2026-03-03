/**
 * DMS Anhang-Dialog
 *
 * Zwei Tabs:
 * 1. "Anhänge" — verknüpfte Dokumente, Upload per Drag & Drop
 * 2. "Eingang" — unzugeordnete Paperless-Inbox-Dokumente (z.B. vom Netzwerkscanner),
 *    per Klick dem aktuellen Beleg zuordnen
 */

import { useState, useEffect, useCallback } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import {
  Loader2,
  Download,
  Trash2,
  FileText,
  AlertCircle,
  Link as LinkIcon,
  RefreshCw,
  Inbox,
} from 'lucide-react'
import { DropUpload } from '@/features/document/DropUpload'
import { dmsService, type Document } from '@/lib/services/dms-service'
import { useToast } from '@/components/ui/toast-provider'
import { useTenant } from '@/hooks/useTenant'

type DmsAnhangDialogProps = {
  open: boolean
  onClose: () => void
  businessObjectType: string
  businessObjectId: string | null
  title?: string
}

// ─── Hilfsfunktion: Dateigröße formatieren ───────────────────────────────────

function formatSize(sizeKb: number): string {
  if (sizeKb < 1024) return `${sizeKb} KB`
  return `${(sizeKb / 1024).toFixed(1)} MB`
}

// ─── Dokumentzeile (wiederverwendet in beiden Tabs) ──────────────────────────

function DocRow({
  doc,
  onDownload,
  onDelete,
  onLink,
  linking,
}: {
  doc: Document
  onDownload?: () => void
  onDelete?: () => void
  onLink?: () => void
  linking?: boolean
}): JSX.Element {
  return (
    <div className="flex items-center gap-2 rounded border border-input bg-background px-3 py-2 text-sm">
      <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
      <span className="flex-1 truncate" title={doc.title}>{doc.title}</span>
      {doc.createdAt && (
        <span className="text-xs text-muted-foreground whitespace-nowrap">
          {new Date(doc.createdAt).toLocaleDateString('de-DE')}
        </span>
      )}
      {doc.sizeKb !== undefined && (
        <span className="text-xs text-muted-foreground whitespace-nowrap">
          {formatSize(doc.sizeKb)}
        </span>
      )}
      {onDownload && (
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={onDownload}
          title="Herunterladen"
        >
          <Download className="h-4 w-4" />
        </Button>
      )}
      {onDelete && (
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7 text-destructive hover:text-destructive"
          onClick={onDelete}
          title="Löschen"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      )}
      {onLink && (
        <Button
          variant="outline"
          size="sm"
          className="h-7 gap-1 text-xs"
          onClick={onLink}
          disabled={linking}
          title="Diesem Beleg zuordnen"
        >
          {linking ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <LinkIcon className="h-3 w-3" />
          )}
          Zuordnen
        </Button>
      )}
    </div>
  )
}

// ─── Hauptkomponente ──────────────────────────────────────────────────────────

export function DmsAnhangDialog({
  open,
  onClose,
  businessObjectType,
  businessObjectId,
  title = 'UNTERLAGEN / DATEIEN',
}: DmsAnhangDialogProps): JSX.Element {
  const { push } = useToast()
  const { tenantId } = useTenant()

  // Tab "Anhänge"
  const [documents, setDocuments] = useState<Document[]>([])
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [uploading, setUploading] = useState(false)

  // Tab "Eingang"
  const [inboxDocs, setInboxDocs] = useState<Document[]>([])
  const [loadingInbox, setLoadingInbox] = useState(false)
  const [linkingId, setLinkingId] = useState<number | null>(null)

  // ── Anhänge laden ──────────────────────────────────────────────────────────

  const loadDocuments = useCallback(async (): Promise<void> => {
    if (!businessObjectId) return
    setLoadingDocs(true)
    try {
      const docs = await dmsService.getDocumentsForObject(
        tenantId,
        businessObjectType,
        businessObjectId
      )
      setDocuments(docs)
    } catch {
      push('Anhänge konnten nicht geladen werden')
    } finally {
      setLoadingDocs(false)
    }
  }, [businessObjectId, businessObjectType, push, tenantId])

  // ── Inbox laden ───────────────────────────────────────────────────────────

  const loadInbox = useCallback(async (): Promise<void> => {
    setLoadingInbox(true)
    try {
      const result = await dmsService.getInbox(tenantId)
      setInboxDocs(result.data)
    } catch {
      push('Paperless-Eingang konnte nicht geladen werden')
    } finally {
      setLoadingInbox(false)
    }
  }, [push, tenantId])

  useEffect(() => {
    if (open) {
      if (businessObjectId) void loadDocuments()
      void loadInbox()
    } else {
      setDocuments([])
      setInboxDocs([])
    }
  }, [open, businessObjectId, loadDocuments, loadInbox])

  // ── Upload ────────────────────────────────────────────────────────────────

  const handleFiles = async (files: File[]): Promise<void> => {
    if (!businessObjectId) return
    setUploading(true)
    try {
      for (const file of files) {
        await dmsService.uploadDocument({
          file,
          tenantId,
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

  // ── Download ──────────────────────────────────────────────────────────────

  const handleDownload = async (doc: Document): Promise<void> => {
    try {
      const blob = await dmsService.downloadDocument(doc.id, tenantId)
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

  // ── Löschen ───────────────────────────────────────────────────────────────

  const handleDelete = async (doc: Document): Promise<void> => {
    try {
      await dmsService.deleteDocument(doc.id, tenantId)
      push('Dokument gelöscht')
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id))
    } catch {
      push('Löschen fehlgeschlagen')
    }
  }

  // ── Inbox-Dokument zuordnen ───────────────────────────────────────────────

  const handleLink = async (doc: Document): Promise<void> => {
    if (!businessObjectId || doc.paperlessId === undefined) return
    setLinkingId(doc.id)
    try {
      await dmsService.linkDocument({
        paperlessId: doc.paperlessId,
        tenantId,
        businessObjectType,
        businessObjectId,
      })
      push(`„${doc.title}" diesem Beleg zugeordnet`)
      // Aus Inbox entfernen, Anhänge neu laden
      setInboxDocs((prev) => prev.filter((d) => d.id !== doc.id))
      await loadDocuments()
    } catch {
      push('Zuordnung fehlgeschlagen')
    } finally {
      setLinkingId(null)
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-2xl max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="anhaenge" className="flex-1 flex flex-col min-h-0">
          <TabsList className="w-full justify-start">
            <TabsTrigger value="anhaenge">
              Anhänge
              {documents.length > 0 && (
                <span className="ml-1.5 rounded-full bg-primary/15 px-1.5 text-[10px] font-semibold">
                  {documents.length}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="eingang">
              <Inbox className="h-3.5 w-3.5 mr-1" />
              Eingang (Scanner)
              {inboxDocs.length > 0 && (
                <span className="ml-1.5 rounded-full bg-amber-500/20 text-amber-700 px-1.5 text-[10px] font-semibold">
                  {inboxDocs.length}
                </span>
              )}
            </TabsTrigger>
          </TabsList>

          {/* ── Tab: Anhänge ─────────────────────────────────────────────── */}
          <TabsContent value="anhaenge" className="flex-1 overflow-auto space-y-3 pt-2">
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

                {loadingDocs ? (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Lade Anhänge…
                  </div>
                ) : documents.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    Keine Anhänge vorhanden
                  </p>
                ) : (
                  <div className="space-y-1">
                    {documents.map((doc) => (
                      <DocRow
                        key={doc.id}
                        doc={doc}
                        onDownload={() => void handleDownload(doc)}
                        onDelete={() => void handleDelete(doc)}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </TabsContent>

          {/* ── Tab: Eingang ─────────────────────────────────────────────── */}
          <TabsContent value="eingang" className="flex-1 overflow-auto space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Unzugeordnete Dokumente aus dem Paperless-Eingang (z.B. vom Netzwerkscanner).
                Per „Zuordnen" direkt mit diesem Beleg verknüpfen.
              </p>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 shrink-0"
                onClick={() => void loadInbox()}
                title="Aktualisieren"
              >
                <RefreshCw className={`h-4 w-4 ${loadingInbox ? 'animate-spin' : ''}`} />
              </Button>
            </div>

            {!businessObjectId && (
              <div className="flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 text-amber-800 text-sm">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>Bitte zuerst speichern, um Dokumente zuordnen zu können.</span>
              </div>
            )}

            {loadingInbox ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Lade Eingang…
              </div>
            ) : inboxDocs.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-6">
                Keine unzugeordneten Dokumente im Eingang
              </p>
            ) : (
              <div className="space-y-1">
                {inboxDocs.map((doc) => (
                  <DocRow
                    key={doc.id}
                    doc={doc}
                    onDownload={() => void handleDownload(doc)}
                    onLink={businessObjectId ? () => void handleLink(doc) : undefined}
                    linking={linkingId === doc.id}
                  />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>

        <div className="flex justify-end pt-2 border-t">
          <Button variant="outline" onClick={onClose}>
            Schließen
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
