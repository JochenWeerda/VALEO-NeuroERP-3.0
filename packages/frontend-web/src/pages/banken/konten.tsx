import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useBankkonten, type BankKonto } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Building2, Euro, FileDown, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

export default function BankkontenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: konten = [], isLoading, isError, error, refetch } = useBankkonten()

  const filteredKonten = useMemo(() => {
    if (!searchTerm) return konten
    const term = searchTerm.toLowerCase()
    return konten.filter(k => 
      k.bank?.toLowerCase().includes(term) ||
      k.iban?.toLowerCase().includes(term) ||
      k.kontoart?.toLowerCase().includes(term)
    )
  }, [konten, searchTerm])

  const gesamtSaldo = filteredKonten.reduce((sum, k) => sum + (k.saldo || 0), 0)

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32 mt-2" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          <Card><CardContent className="pt-4"><Skeleton className="h-16 w-full" /></CardContent></Card>
        </div>
        <Card><CardContent className="pt-4"><Skeleton className="h-64 w-full" /></CardContent></Card>
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const columns = [
    {
      key: 'bank' as const,
      label: 'Bank',
      render: (k: BankKonto) => (
        <button onClick={() => navigate(`/banken/konto/${k.id}`)} className="font-medium text-blue-600 hover:underline">
          {k.bank}
        </button>
      ),
    },
    { key: 'iban' as const, label: 'IBAN', render: (k: BankKonto) => <span className="font-mono text-sm">{k.iban}</span> },
    { key: 'kontoart' as const, label: 'Kontoart', render: (k: BankKonto) => <Badge variant="outline">{k.kontoart}</Badge> },
    {
      key: 'saldo' as const,
      label: 'Saldo',
      render: (k: BankKonto) => (
        <span className="font-bold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(k.saldo)}
        </span>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (k: BankKonto) => (
        <Badge variant={k.status === 'aktiv' ? 'outline' : 'secondary'}>
          {k.status === 'aktiv' ? 'Aktiv' : 'Inaktiv'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bankkonten</h1>
          <p className="text-muted-foreground">Konten-Verwaltung</p>
        </div>
        <Button onClick={() => navigate('/banken/konto/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues Konto
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Konten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{konten.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Saldo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtSaldo)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktive Konten</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{konten.filter((k) => k.status === 'aktiv').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredKonten} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}


