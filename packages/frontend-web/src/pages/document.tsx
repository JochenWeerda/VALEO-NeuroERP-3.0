import * as React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useToast } from "@/components/ui/toast-provider"
import { DropUpload } from "@/features/document/DropUpload"
import type { Doc } from "@/features/document/schema"
import { useMcpMutation, useMcpQuery } from "@/lib/mcp"
import { useMcpRealtime } from "@/lib/useMcpRealtime"
import { useQueryClient } from "@tanstack/react-query"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { 
  FileText, 
  FileSpreadsheet, 
  FileImage, 
  File, 
  Search, 
  Upload, 
  Trash2, 
  ScanLine,
  Info,
  FolderOpen,
  Shield,
  CheckCircle2,
  Calendar
} from "lucide-react"
import { useTranslation } from "react-i18next"

const KB_PRECISION = 0

// Mock-Daten für Vorschau wenn API nicht verfügbar
const mockDocuments: Doc[] = [
  {
    id: '1',
    title: 'ISO 9001:2015 Zertifikat',
    type: 'pdf',
    sizeKB: 245,
    ts: new Date('2024-12-15').toISOString(),
  },
  {
    id: '2',
    title: 'HACCP-Konzept Futtermittelproduktion',
    type: 'pdf',
    sizeKB: 1250,
    ts: new Date('2024-11-20').toISOString(),
  },
  {
    id: '3',
    title: 'GMP+ B1 Zertifikat',
    type: 'pdf',
    sizeKB: 189,
    ts: new Date('2024-10-05').toISOString(),
  },
  {
    id: '4',
    title: 'QS-Prüfbericht 2024',
    type: 'pdf',
    sizeKB: 856,
    ts: new Date('2024-09-18').toISOString(),
  },
  {
    id: '5',
    title: 'Lieferantenaudit Protokoll',
    type: 'docx',
    sizeKB: 125,
    ts: new Date('2024-08-22').toISOString(),
  },
  {
    id: '6',
    title: 'Rückverfolgbarkeitsmatrix Q3',
    type: 'xlsx',
    sizeKB: 456,
    ts: new Date('2024-07-30').toISOString(),
  },
]

// Icon basierend auf Dateityp
function getFileIcon(type: string) {
  switch (type.toLowerCase()) {
    case 'pdf':
      return <FileText className="h-5 w-5 text-red-500" />
    case 'xlsx':
    case 'xls':
    case 'csv':
      return <FileSpreadsheet className="h-5 w-5 text-green-600" />
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
      return <FileImage className="h-5 w-5 text-blue-500" />
    default:
      return <File className="h-5 w-5 text-gray-500" />
  }
}

// KPI Cards
function QMKpiCards({ documentCount, categories }: { documentCount: number; categories: number }) {
  return (
    <div className="grid gap-4 md:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Dokumente gesamt</CardTitle>
          <FolderOpen className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{documentCount}</div>
          <p className="text-xs text-muted-foreground">QM-relevante Dokumente</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Zertifikate</CardTitle>
          <Shield className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{Math.ceil(documentCount * 0.3)}</div>
          <p className="text-xs text-muted-foreground">Aktive Zertifizierungen</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Geprüft</CardTitle>
          <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{Math.ceil(documentCount * 0.85)}</div>
          <p className="text-xs text-muted-foreground">Dokumente freigegeben</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Kategorien</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{categories}</div>
          <p className="text-xs text-muted-foreground">Dokumententypen</p>
        </CardContent>
      </Card>
    </div>
  )
}

// Skeleton Loading
function DocumentSkeleton() {
  return (
    <div className="space-y-6">
      {/* KPI Skeletons */}
      <div className="grid gap-4 md:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16 mb-1" />
              <Skeleton className="h-3 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
      
      {/* Document List Skeleton */}
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-60" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-10 w-full" />
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center justify-between py-3 border-b">
              <div className="flex items-center gap-3">
                <Skeleton className="h-10 w-10 rounded" />
                <div>
                  <Skeleton className="h-5 w-48 mb-1" />
                  <Skeleton className="h-3 w-32" />
                </div>
              </div>
              <div className="flex gap-2">
                <Skeleton className="h-8 w-16" />
                <Skeleton className="h-8 w-16" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

export default function DocumentPanel(): JSX.Element {
  const { t } = useTranslation()
  const { data, isLoading, isError } = useMcpQuery<{ data: Doc[] }>('document', 'list', [])
  const [useMockData, setUseMockData] = React.useState(false)
  
  // Verwende Mock-Daten wenn API nicht verfügbar
  const apiRows: Doc[] = (data?.data ?? []) as Doc[]
  const rows = useMockData || (apiRows.length === 0 && !isLoading) ? mockDocuments : apiRows
  
  const [q, setQ] = React.useState<string>("")
  const { push } = useToast()
  const qc = useQueryClient()
  const key = ['mcp', 'document', 'list'] as const

  // Prüfe ob API verfügbar ist
  React.useEffect(() => {
    if (!isLoading && apiRows.length === 0) {
      setUseMockData(true)
    }
  }, [isLoading, apiRows.length])

  useMcpRealtime('document', (evt): void => {
    if (evt.type === 'uploaded' || evt.type === 'deleted' || evt.type === 'scanned') {
      void qc.invalidateQueries({ queryKey: key })
      push(`Document ${evt.type}`)
    }
  })

  const upload = useMcpMutation<FormData, { ok: boolean; id?: string }>('document', 'upload')
  const scan = useMcpMutation<{ id: string }, { ok: boolean }>('document', 'scan')
  const remove = useMcpMutation<{ id: string }, { ok: boolean }>('document', 'delete')

  const filtered: Doc[] = React.useMemo(
    (): Doc[] => rows.filter((d): boolean =>
      d.title.toLowerCase().includes(q.toLowerCase()) ||
      d.type.toLowerCase().includes(q.toLowerCase())
    ),
    [rows, q]
  )

  // Kategorien zählen
  const categories = React.useMemo(() => {
    const types = new Set(rows.map(d => d.type))
    return types.size
  }, [rows])

  const onFiles = async (files: File[]): Promise<void> => {
    if (files.length === 0) return

    for (const f of files) {
      const fd = new FormData()
      fd.append('file', f, f.name)

      upload.mutate(fd, {
        onSuccess: (): void => push(`✔ Hochgeladen: ${f.name}`),
        onError: (): void => push(`❌ Upload fehlgeschlagen: ${f.name}`),
        onSettled: (): Promise<void> => qc.invalidateQueries({ queryKey: key }),
      })
    }
  }

  const handleScan = (id: string): void => {
    scan.mutate({ id }, {
      onSuccess: (): void => push("✔ Scan gestartet"),
      onError: (): void => push("❌ Scan fehlgeschlagen")
    })
  }

  const handleDelete = (id: string): void => {
    remove.mutate({ id }, {
      onSuccess: (): void => push("✔ Gelöscht"),
      onError: (): void => push("❌ Löschen fehlgeschlagen"),
      onSettled: (): Promise<void> => qc.invalidateQueries({ queryKey: key })
    })
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setQ(e.target.value)
  }

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">QM-Dokumente</h1>
          <p className="text-muted-foreground">
            Qualitätsmanagement-Dokumente, Zertifikate und Nachweise
          </p>
        </div>
        <DocumentSkeleton />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">QM-Dokumente</h1>
        <p className="text-muted-foreground">
          Qualitätsmanagement-Dokumente, Zertifikate und Nachweise
        </p>
      </div>

      {/* Vorschau-Modus Alert */}
      {useMockData && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Vorschau-Modus</AlertTitle>
          <AlertDescription>
            Das Dokumentenmanagement-Backend ist nicht verfügbar. Es werden Beispieldaten angezeigt.
            Funktionen wie Upload, Scan und Löschen sind im Vorschau-Modus deaktiviert.
          </AlertDescription>
        </Alert>
      )}

      {/* KPI Cards */}
      <QMKpiCards documentCount={rows.length} categories={categories} />

      {/* Document Upload & List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FolderOpen className="h-5 w-5" />
            Dokumentenverwaltung
          </CardTitle>
          <CardDescription>
            QM-relevante Dokumente hochladen, verwalten und durchsuchen
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Upload Zone */}
          {!useMockData && <DropUpload onFiles={onFiles} />}
          
          {/* Search */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                className="pl-9"
                placeholder="Suche nach Titel oder Dokumenttyp…"
                value={q}
                onChange={handleSearchChange}
              />
            </div>
          </div>

          {/* Document List */}
          <div className="border rounded-lg divide-y">
            {filtered.length === 0 ? (
              <div className="p-8 text-center">
                <FileText className="mx-auto h-12 w-12 text-muted-foreground/50" />
                <h3 className="mt-4 text-lg font-semibold">Keine Dokumente gefunden</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  {q ? 'Versuchen Sie einen anderen Suchbegriff.' : 'Laden Sie QM-Dokumente hoch, um sie hier zu verwalten.'}
                </p>
              </div>
            ) : (
              filtered.map((d: Doc): JSX.Element => (
                <div key={d.id} className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-muted rounded-lg">
                      {getFileIcon(d.type)}
                    </div>
                    <div>
                      <div className="font-medium">{d.title}</div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Badge variant="outline" className="text-xs">
                          {d.type.toUpperCase()}
                        </Badge>
                        <span>•</span>
                        <span>{Math.round(d.sizeKB).toFixed(KB_PRECISION)} KB</span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(d.ts).toLocaleDateString('de-DE')}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={(): void => handleScan(d.id)}
                      disabled={scan.isPending || useMockData}
                    >
                      <ScanLine className="h-4 w-4 mr-1" />
                      Scan
                    </Button>
                    <Button 
                      size="sm" 
                      variant="destructive"
                      onClick={(): void => handleDelete(d.id)}
                      disabled={remove.isPending || useMockData}
                    >
                      <Trash2 className="h-4 w-4 mr-1" />
                      Löschen
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer Info */}
          <div className="text-sm text-muted-foreground text-center pt-2">
            {filtered.length} von {rows.length} Dokument(en) angezeigt
          </div>
        </CardContent>
      </Card>

      {/* QM Kategorien Übersicht */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-600" />
              Zertifikate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex justify-between">
                <span>ISO 9001:2015</span>
                <Badge variant="outline" className="text-green-600">Gültig</Badge>
              </li>
              <li className="flex justify-between">
                <span>GMP+ B1</span>
                <Badge variant="outline" className="text-green-600">Gültig</Badge>
              </li>
              <li className="flex justify-between">
                <span>QS-Zertifikat</span>
                <Badge variant="outline" className="text-green-600">Gültig</Badge>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <FileText className="h-4 w-4 text-blue-600" />
              Verfahrensanweisungen
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex justify-between">
                <span>VA-001 HACCP</span>
                <Badge variant="outline">Rev. 5</Badge>
              </li>
              <li className="flex justify-between">
                <span>VA-002 Rückverfolgbarkeit</span>
                <Badge variant="outline">Rev. 3</Badge>
              </li>
              <li className="flex justify-between">
                <span>VA-003 Reklamationen</span>
                <Badge variant="outline">Rev. 2</Badge>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-amber-600" />
              Prüfberichte
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex justify-between">
                <span>Internes Audit Q4/2024</span>
                <Badge variant="outline" className="text-green-600">Bestanden</Badge>
              </li>
              <li className="flex justify-between">
                <span>Lieferantenaudit</span>
                <Badge variant="outline" className="text-green-600">Bestanden</Badge>
              </li>
              <li className="flex justify-between">
                <span>Kundenaudit</span>
                <Badge variant="outline" className="text-amber-600">Offen</Badge>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
