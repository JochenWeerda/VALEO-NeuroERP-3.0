/**
 * Sorte-Auswahl-Dialog für Ernte-Annahme
 * Lädt Sorten von /api/v1/agrar/varieties, Fallback auf Standard-Sorten
 */

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

export type Variety = {
  id: string
  variety_number: string
  name: string
  description: string | null
  crop_type: string | null
}

type VarietySelectionDialogProps = {
  open: boolean
  onClose: () => void
  onSelect: (variety: Variety) => void
  articleId?: string | null
}

// Standard-Sorten (kann später aus API/DB geladen werden)
const STANDARD_VARIETIES: Variety[] = [
  { id: '1', variety_number: '245', name: 'Weizen', description: 'Standard-Weizen', crop_type: 'WHEAT' },
  { id: '2', variety_number: '100', name: 'Mais', description: 'Standard-Mais', crop_type: 'MAIZE' },
  { id: '3', variety_number: '200', name: 'Gerste', description: 'Standard-Gerste', crop_type: 'BARLEY' },
  { id: '4', variety_number: '300', name: 'Hafer', description: 'Standard-Hafer', crop_type: 'OATS' },
  { id: '5', variety_number: '400', name: 'Raps', description: 'Standard-Raps', crop_type: 'RAPESEED' },
]

export function VarietySelectionDialog({
  open,
  onClose,
  onSelect,
  articleId,
}: VarietySelectionDialogProps): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedVariety, setSelectedVariety] = useState<Variety | null>(null)

  const { data: apiVarieties } = useQuery({
    queryKey: ['agrar-varieties'],
    queryFn: async () => {
      try {
        const res = await apiClient.get<Variety[]>('/api/v1/agrar/varieties')
        return Array.isArray(res) ? res : (res as any)?.items ?? []
      } catch {
        return []
      }
    },
    enabled: open,
  })

  const varieties = (apiVarieties?.length ? apiVarieties : STANDARD_VARIETIES) as Variety[]

  const filteredVarieties = useMemo(() => {
    if (!varieties?.length) return []
    if (!searchTerm.trim()) return varieties

    const searchLower = searchTerm.toLowerCase()
    return varieties.filter((variety: Variety) => {
      return (
        variety.variety_number?.toLowerCase().includes(searchLower) ||
        variety.name?.toLowerCase().includes(searchLower) ||
        (variety.description && variety.description.toLowerCase().includes(searchLower)) ||
        (variety.crop_type && variety.crop_type.toLowerCase().includes(searchLower))
      )
    })
  }, [varieties, searchTerm])

  const handleSelect = (): void => {
    if (selectedVariety) {
      onSelect(selectedVariety)
      setSelectedVariety(null)
      setSearchTerm('')
    }
  }

  const handleClose = (): void => {
    setSelectedVariety(null)
    setSearchTerm('')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Sorte auswählen</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 flex-1 overflow-hidden flex flex-col">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <Label htmlFor="variety-search">Suche:</Label>
              <Input
                id="variety-search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Sorte-Nr., Name, Beschreibung suchen..."
                autoFocus
              />
            </div>
          </div>

          <div className="flex-1 overflow-auto border rounded">
            {filteredVarieties.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground">
                {searchTerm ? 'Keine Sorten gefunden' : 'Keine Sorten verfügbar'}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-24">Sorte-Nr.</TableHead>
                    <TableHead className="w-48">Name</TableHead>
                    <TableHead className="w-64">Beschreibung</TableHead>
                    <TableHead className="w-32">Kulturart</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredVarieties.map((variety: Variety) => (
                    <TableRow
                      key={variety.id}
                      className={selectedVariety?.id === variety.id ? 'bg-green-100' : 'cursor-pointer'}
                      onClick={() => setSelectedVariety(variety)}
                    >
                      <TableCell className="font-mono">{variety.variety_number}</TableCell>
                      <TableCell className="font-semibold">{variety.name}</TableCell>
                      <TableCell>{variety.description || '-'}</TableCell>
                      <TableCell>{variety.crop_type || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Abbrechen
          </Button>
          <Button onClick={handleSelect} disabled={!selectedVariety}>
            Auswählen
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}


