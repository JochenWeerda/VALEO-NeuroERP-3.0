import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { validateIBAN, formatIBAN } from '@/lib/utils/iban-validator'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Building2, Plus, Pencil } from 'lucide-react'
import { toast } from 'sonner'

type BankAccount = {
  id: string
  account_number: string
  bank_name: string
  iban?: string | null
  bic?: string | null
  currency: string
  balance?: number | null
  is_active: boolean
  gl_account_number?: string
}

type BankAccountPayload = {
  account_number: string
  bank_name: string
  iban: string
  bic: string
  currency: string
  is_active: boolean
}

const defaultForm: BankAccountPayload = {
  account_number: '',
  bank_name: '',
  iban: '',
  bic: '',
  currency: 'EUR',
  is_active: true,
}

const fmt = (n: number, currency = 'EUR') =>
  new Intl.NumberFormat('de-DE', { style: 'currency', currency, maximumFractionDigits: 2 }).format(n || 0)

export default function BankStammPage(): JSX.Element {
  const queryClient = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [formData, setFormData] = useState<BankAccountPayload>(defaultForm)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const { data: accounts = [], isLoading, isError } = useQuery({
    queryKey: ['finance', 'bank-accounts'],
    queryFn: async () => (await apiClient.get<BankAccount[]>('/api/v1/finance/bank-accounts')).data,
    staleTime: 2 * 60 * 1000,
  })

  const createMutation = useMutation({
    mutationFn: async (payload: BankAccountPayload) =>
      apiClient.post<BankAccount>('/api/v1/finance/bank-accounts', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance', 'bank-accounts'] })
      toast.success('Bankkonto wurde angelegt.')
      setCreateOpen(false)
      setFormData(defaultForm)
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail ?? 'Anlage fehlgeschlagen')
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: Partial<BankAccountPayload> }) =>
      apiClient.put<BankAccount>(`/api/v1/finance/bank-accounts/${id}`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance', 'bank-accounts'] })
      toast.success('Bankkonto wurde aktualisiert.')
      setEditOpen(false)
      setSelectedId(null)
      setFormData(defaultForm)
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail ?? 'Aktualisierung fehlgeschlagen')
    },
  })

  const openEdit = (acc: BankAccount) => {
    setSelectedId(acc.id)
    setFormData({
      account_number: acc.account_number,
      bank_name: acc.bank_name,
      iban: acc.iban ?? '',
      bic: acc.bic ?? '',
      currency: acc.currency ?? 'EUR',
      is_active: acc.is_active,
    })
    setEditOpen(true)
  }

  const submitCreate = () => {
    if (!formData.account_number.trim() || !formData.bank_name.trim()) {
      toast.error('Kontonummer und Bankname sind Pflicht.')
      return
    }
    const iban = (formData.iban ?? '').replace(/\s/g, '')
    if (iban && !validateIBAN(iban)) {
      toast.error('IBAN ist ungültig (Prüfziffer oder Format).')
      return
    }
    const payload = { ...formData, iban: iban ? formatIBAN(iban) : formData.iban }
    createMutation.mutate(payload)
  }

  const submitEdit = () => {
    if (!selectedId) return
    if (!formData.bank_name.trim()) {
      toast.error('Bankname ist Pflicht.')
      return
    }
    const iban = (formData.iban ?? '').replace(/\s/g, '')
    if (iban && !validateIBAN(iban)) {
      toast.error('IBAN ist ungültig (Prüfziffer oder Format).')
      return
    }
    updateMutation.mutate({
      id: selectedId,
      payload: {
        bank_name: formData.bank_name,
        iban: iban ? formatIBAN(iban) : (formData.iban || undefined),
        bic: formData.bic || undefined,
        currency: formData.currency,
        is_active: formData.is_active,
      },
    })
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Bankkonten (Bankstamm)</h1>
          <p className="text-muted-foreground">
            Bankkonten verwalten und dem Kontenplan zuordnen (Gegenkonto für Buchungen).
          </p>
        </div>
        <Button onClick={() => { setFormData(defaultForm); setCreateOpen(true) }}>
          <Plus className="mr-2 h-4 w-4" />
          Neues Bankkonto
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Konten ({accounts.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground text-sm">Lade Bankkonten...</p>}
          {isError && <p className="text-red-600 text-sm">Fehler beim Laden.</p>}
          {!isLoading && !isError && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Kontonummer</th>
                    <th className="py-2 pr-4 font-medium">Bank / Bezeichnung</th>
                    <th className="py-2 pr-4 font-medium">IBAN</th>
                    <th className="py-2 pr-4 font-medium">BIC</th>
                    <th className="py-2 pr-4 font-medium text-right">Saldo</th>
                    <th className="py-2 pr-4 font-medium">Aktiv</th>
                    <th className="py-2 font-medium text-right">Aktionen</th>
                  </tr>
                </thead>
                <tbody>
                  {accounts.length === 0 && (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-muted-foreground">
                        Noch keine Bankkonten angelegt.
                      </td>
                    </tr>
                  )}
                  {accounts.map((acc) => (
                    <tr key={acc.id} className="border-b hover:bg-muted/50 transition-colors">
                      <td className="py-2 pr-4 font-mono">{acc.account_number}</td>
                      <td className="py-2 pr-4 font-medium">{acc.bank_name}</td>
                      <td className="py-2 pr-4 font-mono text-xs">{acc.iban ?? '–'}</td>
                      <td className="py-2 pr-4 font-mono text-xs">{acc.bic ?? '–'}</td>
                      <td className="py-2 pr-4 text-right">{acc.balance != null ? fmt(Number(acc.balance), acc.currency) : '–'}</td>
                      <td className="py-2 pr-4">{acc.is_active ? 'Ja' : 'Nein'}</td>
                      <td className="py-2 text-right">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(acc)}>
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Neues Bankkonto anlegen</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            <Label>Kontonummer (Konto im Kontenplan)</Label>
            <Input
              value={formData.account_number}
              onChange={(e) => setFormData((p) => ({ ...p, account_number: e.target.value }))}
              placeholder="z. B. 1200"
            />
            <Label>Bank / Bezeichnung</Label>
            <Input
              value={formData.bank_name}
              onChange={(e) => setFormData((p) => ({ ...p, bank_name: e.target.value }))}
              placeholder="z. B. Hauptkonto Deutsche Bank"
            />
            <Label>IBAN</Label>
            <Input
              value={formData.iban}
              onChange={(e) => setFormData((p) => ({ ...p, iban: e.target.value }))}
              placeholder="DE89 3704 0044 …"
            />
            <Label>BIC</Label>
            <Input
              value={formData.bic}
              onChange={(e) => setFormData((p) => ({ ...p, bic: e.target.value }))}
              placeholder="COBADEFFXXX"
            />
            <Label>Währung</Label>
            <Input
              value={formData.currency}
              onChange={(e) => setFormData((p) => ({ ...p, currency: e.target.value }))}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Abbrechen</Button>
            <Button onClick={submitCreate} disabled={createMutation.isPending}>Anlegen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Bankkonto bearbeiten</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            <Label>Bank / Bezeichnung</Label>
            <Input
              value={formData.bank_name}
              onChange={(e) => setFormData((p) => ({ ...p, bank_name: e.target.value }))}
            />
            <Label>IBAN</Label>
            <Input
              value={formData.iban}
              onChange={(e) => setFormData((p) => ({ ...p, iban: e.target.value }))}
            />
            <Label>BIC</Label>
            <Input
              value={formData.bic}
              onChange={(e) => setFormData((p) => ({ ...p, bic: e.target.value }))}
            />
            <Label>Währung</Label>
            <Input
              value={formData.currency}
              onChange={(e) => setFormData((p) => ({ ...p, currency: e.target.value }))}
            />
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData((p) => ({ ...p, is_active: e.target.checked }))}
              />
              <Label htmlFor="is_active">Aktiv</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)}>Abbrechen</Button>
            <Button onClick={submitEdit} disabled={updateMutation.isPending}>Speichern</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
