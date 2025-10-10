import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Table } from '@/components/ui/table'
import { useToast } from '@/hooks/use-toast'
import { FileText, CheckCircle2, XCircle, ExternalLink } from 'lucide-react'

interface InboxDocument {
  id: string
  dms_document_id: number
  dms_url: string
  ocr_text: string
  parsed_fields: Record<string, string>
  confidence: number
  status: string
}

export default function InboxPage() {
  const { toast } = useToast()
  const [documents, setDocuments] = useState<InboxDocument[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadInbox()
  }, [])

  async function loadInbox() {
    try {
      setLoading(true)
      const response = await fetch('/api/dms/inbox')
      const data = await response.json()
      
      if (data.ok) {
        setDocuments(data.items || [])
      }
    } catch (e) {
      toast({
        title: 'Fehler beim Laden',
        description: e instanceof Error ? e.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  async function createFromInbox(doc: InboxDocument) {
    try {
      const response = await fetch(`/api/dms/inbox/${doc.id}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),  // Keine Overrides
      })
      
      const data = await response.json()
      
      if (data.ok) {
        toast({
          title: '✅ Beleg erstellt',
          description: `Belegnummer: ${data.number}`,
        })
        loadInbox()  // Reload
      }
    } catch (e) {
      toast({
        title: 'Fehler beim Erstellen',
        description: e instanceof Error ? e.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    }
  }

  async function deleteFromInbox(docId: string) {
    if (!confirm('Dokument wirklich verwerfen?')) return

    try {
      await fetch(`/api/dms/inbox/${docId}`, { method: 'DELETE' })
      
      toast({
        title: 'Dokument verworfen',
      })
      
      loadInbox()
    } catch (e) {
      toast({
        title: 'Fehler beim Löschen',
        description: e instanceof Error ? e.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    }
  }

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.8) return <Badge variant="default">Hoch ({(confidence * 100).toFixed(0)}%)</Badge>
    if (confidence >= 0.5) return <Badge variant="secondary">Mittel ({(confidence * 100).toFixed(0)}%)</Badge>
    return <Badge variant="destructive">Niedrig ({(confidence * 100).toFixed(0)}%)</Badge>
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <p className="text-center text-muted-foreground">Lädt...</p>
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
                Dokumente werden automatisch angezeigt wenn sie im DMS hochgeladen werden
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
        {documents.map((doc) => (
          <Card key={doc.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg">
                    {doc.parsed_fields.invoice_number || doc.id}
                  </CardTitle>
                  <CardDescription>
                    {doc.parsed_fields.supplier || 'Unbekannter Lieferant'}
                  </CardDescription>
                </div>
                {getConfidenceBadge(doc.confidence)}
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {doc.parsed_fields.date && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Datum</p>
                    <p className="text-base">{doc.parsed_fields.date}</p>
                  </div>
                )}
                {doc.parsed_fields.total && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Betrag</p>
                    <p className="text-base font-semibold">{doc.parsed_fields.total} €</p>
                  </div>
                )}
                {doc.parsed_fields.supplier_id && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Lieferanten-ID</p>
                    <p className="text-base">{doc.parsed_fields.supplier_id}</p>
                  </div>
                )}
                {doc.parsed_fields.domain && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Domain</p>
                    <Badge variant="outline">{doc.parsed_fields.domain}</Badge>
                  </div>
                )}
              </div>

              <div className="flex gap-2 pt-2">
                <Button
                  variant="default"
                  onClick={() => createFromInbox(doc)}
                >
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  Beleg erstellen
                </Button>
                
                <Button
                  variant="outline"
                  onClick={() => window.open(doc.dms_url, '_blank')}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Im DMS öffnen
                </Button>
                
                <Button
                  variant="destructive"
                  onClick={() => deleteFromInbox(doc.id)}
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Verwerfen
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

