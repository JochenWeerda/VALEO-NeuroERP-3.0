/**
 * CSV Import Component
 * CSV-Import-Funktionalität für Listen
 */

import { useState, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react'

export interface CSVImportProps {
  onImport: (data: any[]) => Promise<void>
  expectedColumns?: string[]
  entityName: string
}

export function CSVImport({ onImport, expectedColumns, entityName }: CSVImportProps) {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState<any[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const parseCSV = (text: string): any[] => {
    const lines = text.split('\n').filter(line => line.trim())
    if (lines.length === 0) return []

    // Erste Zeile als Header
    const headers = lines[0].split(';').map(h => h.trim().replace(/^"|"$/g, ''))
    
    // Rest als Daten
    const data = lines.slice(1).map(line => {
      const values = line.split(';').map(v => v.trim().replace(/^"|"$/g, ''))
      const row: any = {}
      headers.forEach((header, index) => {
        row[header] = values[index] || ''
      })
      return row
    })

    return data
  }

  const validateData = (data: any[]): string[] => {
    const validationErrors: string[] = []
    
    if (expectedColumns) {
      const firstRow = data[0]
      if (firstRow) {
        const missingColumns = expectedColumns.filter(col => !(col in firstRow))
        if (missingColumns.length > 0) {
          validationErrors.push(`Fehlende Spalten: ${missingColumns.join(', ')}`)
        }
      }
    }

    if (data.length === 0) {
      validationErrors.push('Keine Daten gefunden')
    }

    return validationErrors
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setLoading(true)
    setPreview([])
    setErrors([])

    try {
      const text = await file.text()
      const data = parseCSV(text)
      const validationErrors = validateData(data)

      if (validationErrors.length > 0) {
        setErrors(validationErrors)
        toast({
          variant: 'destructive',
          title: t('crud.messages.validationError'),
          description: validationErrors.join(', '),
        })
      } else {
        setPreview(data.slice(0, 5)) // Zeige erste 5 Zeilen
        toast({
          title: t('crud.messages.importInfo'),
          description: `${data.length} Zeilen gefunden. Klicken Sie auf "Importieren" um fortzufahren.`,
        })
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unbekannter Fehler'
      setErrors([errorMessage])
      toast({
        variant: 'destructive',
        title: t('crud.messages.importError'),
        description: errorMessage,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleImport = async () => {
    if (preview.length === 0) {
      toast({
        variant: 'destructive',
        title: 'Keine Daten',
        description: 'Bitte wählen Sie zuerst eine CSV-Datei aus.',
      })
      return
    }

    setLoading(true)
    try {
      // Lade vollständige Datei nochmal
      const file = fileInputRef.current?.files?.[0]
      if (file) {
        const text = await file.text()
        const data = parseCSV(text)
        await onImport(data)
        toast({
          title: t('crud.messages.importSuccess'),
          description: `${data.length} ${entityName} wurden importiert.`,
        })
        setPreview([])
        setErrors([])
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.importError'),
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          CSV Import
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileSelect}
            className="hidden"
            id="csv-import-input"
          />
          <Button
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
          >
            <FileText className="h-4 w-4 mr-2" />
            CSV-Datei auswählen
          </Button>
        </div>

        {errors.length > 0 && (
          <div className="space-y-2">
            {errors.map((error, index) => (
              <div key={index} className="flex items-center gap-2 text-destructive text-sm">
                <AlertCircle className="h-4 w-4" />
                {error}
              </div>
            ))}
          </div>
        )}

        {preview.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CheckCircle className="h-4 w-4 text-green-600" />
              Vorschau ({preview.length} von {preview.length} Zeilen)
            </div>
            <div className="max-h-48 overflow-auto border rounded">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    {Object.keys(preview[0] || {}).map((key) => (
                      <th key={key} className="px-2 py-1 text-left border-b">
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.map((row, index) => (
                    <tr key={index}>
                      {Object.values(row).map((value: any, colIndex) => (
                        <td key={colIndex} className="px-2 py-1 border-b">
                          {String(value)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Button onClick={handleImport} disabled={loading}>
              {loading ? 'Importiere...' : 'Importieren'}
            </Button>
          </div>
        )}

        {expectedColumns && (
          <div className="text-xs text-muted-foreground">
            <p className="font-medium mb-1">Erwartete Spalten:</p>
            <p>{expectedColumns.join(', ')}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

