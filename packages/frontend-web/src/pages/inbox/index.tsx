import { useCallback, useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { CheckCircle2, ExternalLink, FileText, XCircle } from 'lucide-react'

interface InboxDocument {
  id: string
  dms_document_id: number
  dms_url: string
  ocr_text: string
  parsed_fields: Record<string, string>
  confidence: number
  status: string
}

interface InboxListResponse {
  ok: boolean
  items?: InboxDocument[]
  message?: string
}

interface InboxCreateResponse {
  ok: boolean
  number?: string
  message?: string
}

const INBOX_ENDPOINT = '/api/dms/inbox'
const CREATE_ENDPOINT = (id: string): string => `${INBOX_ENDPOINT}/${id}/create`
const DELETE_ENDPOINT = (id: string): string => `${INBOX_ENDPOINT}/${id}`
const HIGH_CONFIDENCE_THRESHOLD = 0.8
const MEDIUM_CONFIDENCE_THRESHOLD = 0.5
const DELETE_CONFIRMATION_MESSAGE = 'Dokument wirklich verwerfen?'

const isNonEmptyString = (value: unknown): value is string => {
  return typeof value === 'string' && value.trim().length > 0
}

const getFieldValue = (fields: Record<string, string>, key: string): string | undefined => {
  const value = fields[key]
  return isNonEmptyString(value) ? value : undefined
}

const getConfidenceBadge = (confidence: number): JSX.Element => {
  if (confidence >= HIGH_CONFIDENCE_THRESHOLD) {
    return <Badge variant="default">Hoch {(confidence * 100).toFixed(0)}%</Badge>
  }
  if (confidence >= MEDIUM_CONFIDENCE_THRESHOLD) {
    return <Badge variant="secondary">Mittel {(confidence * 100).toFixed(0)}%</Badge>
  }
  return <Badge variant="destructive">Niedrig {(confidence * 100).toFixed(0)}%</Badge>
}

const formatCurrency = (value: string): string => `${value} EUR`

export default function InboxPage(): JSX.Element {
  const { toast } = useToast()
  const [documents, setDocuments] = useState<InboxDocument[]>([])
  const [loading, setLoading] = useState<boolean>(true)

  const loadInbox = useCallback(async (): Promise<void> => {
    try {
      setLoading(true)
      const response = await fetch(INBOX_ENDPOINT)
      const data = (await response.json()) as InboxListResponse

      if (data.ok && Array.isArray(data.items)) {
        setDocuments(data.items)
      } else {
        setDocuments([])
        if (isNonEmptyString(data.message)) {
          toast({
            title: 'Keine Dokumente',
            description: data.message,
          })
        }
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unbekannter Fehler'
      toast({
        title: 'Fehler beim Laden',
        description: message,
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [toast])

  useEffect(() => {
    void loadInbox()
  }, [loadInbox])

  const createFromInbox = useCallback(async (doc: InboxDocument): Promise<void> => {
    try {
      const response = await fetch(CREATE_ENDPOINT(doc.id), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })

      const data = (await response.json()) as InboxCreateResponse

      if (data.ok) {
        toast({
          title: 'Beleg erstellt',
          description: isNonEmptyString(data.number) ? `Belegnummer: ${data.number}` : undefined,
        })
        await loadInbox()
        return
      }

      toast({
        title: 'Erstellen fehlgeschlagen',
        description: data.message ?? 'Unbekannter Fehler',
        variant: 'destructive',
      })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unbekannter Fehler'
      toast({
        title: 'Fehler beim Erstellen',
        description: message,
        variant: 'destructive',
      })
    }
  }, [loadInbox, toast])

  const deleteFromInbox = useCallback(async (docId: string): Promise<void> => {
    if (!window.confirm(DELETE_CONFIRMATION_MESSAGE)) {
      return
    }

    try {
      const response = await fetch(DELETE_ENDPOINT(docId), { method: 'DELETE' })
      if (!response.ok) {
        throw new Error(`Status ${response.status}`)
      }

      toast({
        title: 'Dokument verworfen',
      })

      await loadInbox()
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unbekannter Fehler'
      toast({
        title: 'Fehler beim Loeschen',
        description: message,
        variant: 'destructive',
      })
    }
  }, [loadInbox, toast])

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <p className="text-center text-muted-foreground">Laedt...</p>
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardHeader>
            <CardTitle>Posteingang (DMS)</CardTitle>
            <CardDescription>Eingehende Dokumente zur Verarbeitung</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Keine eingehenden Dokumente</p>
              <p className="text-sm mt-2">
                Dokumente werden automatisch angezeigt, wenn sie im DMS hochgeladen werden.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Posteingang (DMS)</h1>
        <p className="text-muted-foreground">
          Eingehende Dokumente zur Verarbeitung ({documents.length})
        </p>
      </div>

      <div className="grid gap-4">
        {documents.map((doc) => {
          const invoiceNumber = getFieldValue(doc.parsed_fields, 'invoice_number')
          const supplier = getFieldValue(doc.parsed_fields, 'supplier')
          const invoiceDate = getFieldValue(doc.parsed_fields, 'date')
          const invoiceTotal = getFieldValue(doc.parsed_fields, 'total')
          const supplierId = getFieldValue(doc.parsed_fields, 'supplier_id')
          const domain = getFieldValue(doc.parsed_fields, 'domain')

          return (
            <Card key={doc.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg">
                    {invoiceNumber ?? doc.id}
                  </CardTitle>
                  <CardDescription>
                    {supplier ?? 'Unbekannter Lieferant'}
                  </CardDescription>
                </div>
                {getConfidenceBadge(doc.confidence)}
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {invoiceDate != null && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Datum</p>
                    <p className="text-base">{invoiceDate}</p>
                  </div>
                )}
                {invoiceTotal != null && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Betrag</p>
                    <p className="text-base font-semibold">
                      {formatCurrency(invoiceTotal)}
                    </p>
                  </div>
                )}
                {supplierId != null && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Lieferanten-ID</p>
                    <p className="text-base">{supplierId}</p>
                  </div>
                )}
                {domain != null && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Domain</p>
                    <Badge variant="outline">{domain}</Badge>
                  </div>
                )}
              </div>

              <div className="flex gap-2 pt-2">
                <Button variant="default" onClick={() => { void createFromInbox(doc) }}>
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  Beleg erstellen
                </Button>

                <Button variant="outline" onClick={() => window.open(doc.dms_url, '_blank', 'noopener')}>
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Im DMS oeffnen
                </Button>

                <Button variant="destructive" onClick={() => { void deleteFromInbox(doc.id) }}>
                  <XCircle className="h-4 w-4 mr-2" />
                  Verwerfen
                </Button>
              </div>
            </CardContent>
          </Card>
          )
        })}
      </div>
    </div>
  )
}
