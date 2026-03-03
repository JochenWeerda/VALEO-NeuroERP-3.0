/**
 * Kontrakt-Auswahl-Dialog fÃ¼r Ernte-Annahme
 */

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
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
import { apiClient } from '@/lib/axios'

export type AgrarContract = {
  id: string
  contract_number: string
  contract_type: 'buy' | 'sell'
  harvest_year: number
  partner_id: string
  article_id: string
  pricing_model: 'fixed' | 'follow' | 'pool'
  fixed_price: number | null
  currency: string
  total_quantity_kg: number
  remaining_quantity_kg: number
  status: string
  valid_from: string | null
  valid_until: string | null
}

type ContractSelectionDialogProps = {
  open: boolean
  onClose: () => void
  onSelect: (contract: AgrarContract) => void
  customerId?: string | null
}

export function ContractSelectionDialog({
  open,
  onClose,
  onSelect,
  customerId,
}: ContractSelectionDialogProps): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedContract, setSelectedContract] = useState<AgrarContract | null>(null)

  const { data: contractsData, isLoading, error } = useQuery({
    queryKey: ['agrar-contracts', customerId],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('limit', '200')
      if (customerId) {
        // TODO: Filter nach Kunde (partner_id), wenn API das unterstÃ¼tzt
      }
      
      try {
        const response = await apiClient.get<any>('/api/v1/agrar/contracts', { params })
        
        let items: any[] = []
        if (Array.isArray(response)) {
          items = response
        } else if (response?.items && Array.isArray(response.items)) {
          items = response.items
        } else if (response?.data) {
          if (Array.isArray(response.data)) {
            items = response.data
          } else if (response.data.items && Array.isArray(response.data.items)) {
            items = response.data.items
          }
        }
        
        return items.map((c: any) => ({
          id: c.id,
          contract_number: c.contract_number || c.contractNumber || '',
          contract_type: c.contract_type || c.contractType || 'buy',
          harvest_year: c.harvest_year || c.harvestYear || new Date().getFullYear(),
          partner_id: c.partner_id || c.partnerId || '',
          article_id: c.article_id || c.articleId || '',
          pricing_model: c.pricing_model || c.pricingModel || 'fixed',
          fixed_price: c.fixed_price || c.fixedPrice || null,
          currency: c.currency || 'EUR',
          total_quantity_kg: c.total_quantity_kg || c.totalQuantityKg || 0,
          remaining_quantity_kg: c.remaining_quantity_kg || c.remainingQuantityKg || 0,
          status: c.status || 'open',
          valid_from: c.valid_from || c.validFrom || null,
          valid_until: c.valid_until || c.validUntil || null,
        }))
      } catch (err: any) {
        console.error('[ContractSelectionDialog] Error fetching contracts:', err)
        return []
      }
    },
    enabled: open,
  })

  const filteredContracts = useMemo(() => {
    if (!contractsData) return []
    if (!searchTerm.trim()) return contractsData

    const searchLower = searchTerm.toLowerCase()
    return contractsData.filter((contract: AgrarContract) => {
      return (
        contract.contract_number.toLowerCase().includes(searchLower) ||
        contract.contract_type.toLowerCase().includes(searchLower) ||
        contract.status.toLowerCase().includes(searchLower)
      )
    })
  }, [contractsData, searchTerm])

  const handleSelect = (): void => {
    if (selectedContract) {
      onSelect(selectedContract)
      setSelectedContract(null)
      setSearchTerm('')
    }
  }

  const handleClose = (): void => {
    setSelectedContract(null)
    setSearchTerm('')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-5xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Kontrakt auswÃ¤hlen</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 flex-1 overflow-hidden flex flex-col">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <Label htmlFor="contract-search">Suche:</Label>
              <Input
                id="contract-search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Kontrakt-Nr., Typ, Status suchen..."
                autoFocus
              />
            </div>
          </div>

          <div className="flex-1 overflow-auto border rounded">
            {isLoading ? (
              <div className="p-4 text-center text-muted-foreground">Lade Kontrakte...</div>
            ) : error ? (
              <div className="p-4 text-center text-red-500">Fehler beim Laden der Kontrakte</div>
            ) : filteredContracts.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground">
                {searchTerm ? 'Keine Kontrakte gefunden' : 'Keine Kontrakte in der Datenbank gefunden'}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-32">Kontrakt-Nr.</TableHead>
                    <TableHead className="w-24">Typ</TableHead>
                    <TableHead className="w-24">Erntejahr</TableHead>
                    <TableHead className="w-32">Preismodell</TableHead>
                    <TableHead className="w-24">Preis (EUR/t)</TableHead>
                    <TableHead className="w-32">Gesamtmenge (kg)</TableHead>
                    <TableHead className="w-32">Restmenge (kg)</TableHead>
                    <TableHead className="w-24">Status</TableHead>
                    <TableHead className="w-32">GÃ¼ltig ab</TableHead>
                    <TableHead className="w-32">GÃ¼ltig bis</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredContracts.map((contract: AgrarContract) => (
                    <TableRow
                      key={contract.id}
                      className={selectedContract?.id === contract.id ? 'bg-green-100' : 'cursor-pointer'}
                      onClick={() => setSelectedContract(contract)}
                    >
                      <TableCell className="font-mono">{contract.contract_number}</TableCell>
                      <TableCell>{contract.contract_type === 'buy' ? 'Kauf' : 'Verkauf'}</TableCell>
                      <TableCell>{contract.harvest_year}</TableCell>
                      <TableCell>
                        {contract.pricing_model === 'fixed' ? 'Festpreis' :
                         contract.pricing_model === 'follow' ? 'Folgepreis' :
                         contract.pricing_model === 'pool' ? 'Pool' : contract.pricing_model}
                      </TableCell>
                      <TableCell>{contract.fixed_price?.toFixed(2) || '-'}</TableCell>
                      <TableCell>{contract.total_quantity_kg.toFixed(2)}</TableCell>
                      <TableCell className="font-semibold">{contract.remaining_quantity_kg.toFixed(2)}</TableCell>
                      <TableCell>{contract.status}</TableCell>
                      <TableCell>
                        {contract.valid_from
                          ? new Date(contract.valid_from).toLocaleDateString('de-DE')
                          : '-'}
                      </TableCell>
                      <TableCell>
                        {contract.valid_until
                          ? new Date(contract.valid_until).toLocaleDateString('de-DE')
                          : '-'}
                      </TableCell>
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
          <Button onClick={handleSelect} disabled={!selectedContract}>
            AuswÃ¤hlen
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}


