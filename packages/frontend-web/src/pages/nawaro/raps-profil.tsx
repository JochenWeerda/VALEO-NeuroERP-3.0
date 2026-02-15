import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import { Plus, Save, Trash2 } from 'lucide-react'
import {
  createRapsProfile,
  deleteRapsProfile,
  deriveRapsProfileFromOps,
  listRapsProfiles,
  updateRapsProfile,
  type NawaroRapsBalance,
  type NawaroRapsCertificate,
} from '@/lib/api/nawaro'

function emptyCert(): NawaroRapsCertificate {
  return {
    scheme: 'REDcert',
    certificate_number: '',
    chain_stage: 'farm',
    valid_from: '',
    valid_until: '',
    issuer: '',
    status: 'valid',
  }
}

function emptyBalance(): NawaroRapsBalance {
  return {
    booking_period: '',
    input_seed_tons: '0',
    output_oil_tons: '0',
    output_meal_tons: '0',
    output_other_tons: '0',
    allocation_oil_pct: '0',
    allocation_meal_pct: '0',
    heap_location: '',
    logistics_note: '',
  }
}

export default function NawaroRapsProfilPage(): JSX.Element {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const [selectedId, setSelectedId] = useState<string>('')
  const [articleId, setArticleId] = useState<string>('')
  const [articleNumber, setArticleNumber] = useState<string>('RAPS-001')
  const [articleName, setArticleName] = useState<string>('Raps (NaWaRo)')
  const [harvestYear, setHarvestYear] = useState<number>(2025)
  const [usageFood, setUsageFood] = useState<string>('10')
  const [usageFeed, setUsageFeed] = useState<string>('20')
  const [usageEnergy, setUsageEnergy] = useState<string>('70')
  const [usageMaterial, setUsageMaterial] = useState<string>('0')
  const [thgValue, setThgValue] = useState<string>('35.000')
  const [yieldPerHa, setYieldPerHa] = useState<string>('36.300')
  const [notes, setNotes] = useState<string>('')
  const [certs, setCerts] = useState<NawaroRapsCertificate[]>([emptyCert()])
  const [balances, setBalances] = useState<NawaroRapsBalance[]>([emptyBalance()])
  const [derivePeriod, setDerivePeriod] = useState<string>('2025-08')

  const profileQuery = useQuery({
    queryKey: ['nawaro', 'raps-profiles'],
    queryFn: listRapsProfiles,
  })

  useEffect(() => {
    if (!profileQuery.data || profileQuery.data.length === 0 || selectedId) {
      return
    }
    loadProfile(profileQuery.data[0].id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profileQuery.data, selectedId])

  const usageTotal = useMemo(() => {
    const n = (v: string) => Number(v.replace(',', '.')) || 0
    return n(usageFood) + n(usageFeed) + n(usageEnergy) + n(usageMaterial)
  }, [usageFood, usageFeed, usageEnergy, usageMaterial])

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        article_id: articleId || null,
        article_number: articleNumber || null,
        article_name: articleName,
        harvest_year: harvestYear,
        usage_food_pct: usageFood,
        usage_feed_pct: usageFeed,
        usage_energy_pct: usageEnergy,
        usage_material_pct: usageMaterial,
        thg_gco2eq_mj: thgValue || null,
        yield_dt_per_ha: yieldPerHa || null,
        notes: notes || null,
        certificates: certs,
        balances,
      }
      if (selectedId) {
        return updateRapsProfile(selectedId, payload)
      }
      return createRapsProfile(payload)
    },
    onSuccess: (saved) => {
      setSelectedId(saved.id)
      toast({ title: 'Raps-Profil gespeichert', description: `${saved.article_name} ${saved.harvest_year}` })
      void queryClient.invalidateQueries({ queryKey: ['nawaro', 'raps-profiles'] })
    },
    onError: (err: unknown) => {
      const message = err instanceof Error ? err.message : 'Fehler beim Speichern'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async () => {
      if (!selectedId) return
      await deleteRapsProfile(selectedId)
    },
    onSuccess: () => {
      clearForm()
      toast({ title: 'Raps-Profil geloescht' })
      void queryClient.invalidateQueries({ queryKey: ['nawaro', 'raps-profiles'] })
    },
  })

  const deriveMutation = useMutation({
    mutationFn: async () => {
      if (!selectedId) {
        throw new Error('Bitte zuerst ein Profil speichern oder auswaehlen')
      }
      return deriveRapsProfileFromOps(selectedId, derivePeriod || undefined)
    },
    onSuccess: (result) => {
      const item = result.profile
      setSelectedId(item.id)
      setArticleId(item.article_id ?? '')
      setArticleNumber(item.article_number ?? '')
      setArticleName(item.article_name)
      setHarvestYear(item.harvest_year)
      setUsageFood(item.usage_food_pct)
      setUsageFeed(item.usage_feed_pct)
      setUsageEnergy(item.usage_energy_pct)
      setUsageMaterial(item.usage_material_pct)
      setThgValue(item.thg_gco2eq_mj ?? '')
      setYieldPerHa(item.yield_dt_per_ha ?? '')
      setNotes(item.notes ?? '')
      setCerts(item.certificates.length > 0 ? item.certificates : [emptyCert()])
      setBalances(item.balances.length > 0 ? item.balances : [emptyBalance()])

      const message = result.plausibility_messages.length > 0
        ? result.plausibility_messages.join(' | ')
        : `Periode ${result.period}: Input ${result.source_input_tons} t (Tickets ${result.source_tickets_kg} kg, Settlements ${result.source_settlements_kg} kg)`
      toast({ title: 'Aus Operativdaten abgeleitet', description: message })
      void queryClient.invalidateQueries({ queryKey: ['nawaro', 'raps-profiles'] })
    },
    onError: (err: unknown) => {
      const message = err instanceof Error ? err.message : 'Fehler bei Auto-Ableitung'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    },
  })

  function clearForm(): void {
    setSelectedId('')
    setArticleId('')
    setArticleNumber('RAPS-001')
    setArticleName('Raps (NaWaRo)')
    setHarvestYear(2025)
    setUsageFood('10')
    setUsageFeed('20')
    setUsageEnergy('70')
    setUsageMaterial('0')
    setThgValue('35.000')
    setYieldPerHa('36.300')
    setNotes('')
    setCerts([emptyCert()])
    setBalances([emptyBalance()])
  }

  function loadProfile(id: string): void {
    const item = profileQuery.data?.find((p) => p.id === id)
    if (!item) return
    setSelectedId(item.id)
    setArticleId(item.article_id ?? '')
    setArticleNumber(item.article_number ?? '')
    setArticleName(item.article_name)
    setHarvestYear(item.harvest_year)
    setUsageFood(item.usage_food_pct)
    setUsageFeed(item.usage_feed_pct)
    setUsageEnergy(item.usage_energy_pct)
    setUsageMaterial(item.usage_material_pct)
    setThgValue(item.thg_gco2eq_mj ?? '')
    setYieldPerHa(item.yield_dt_per_ha ?? '')
    setNotes(item.notes ?? '')
    setCerts(item.certificates.length > 0 ? item.certificates : [emptyCert()])
    setBalances(item.balances.length > 0 ? item.balances : [emptyBalance()])
  }

  function updateCert(index: number, key: keyof NawaroRapsCertificate, value: string): void {
    setCerts((prev) => prev.map((c, i) => (i === index ? { ...c, [key]: value } : c)))
  }

  function updateBalance(index: number, key: keyof NawaroRapsBalance, value: string): void {
    setBalances((prev) => prev.map((b, i) => (i === index ? { ...b, [key]: value } : b)))
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">NaWaRo Raps-Profil</h1>
        <p className="text-muted-foreground">Verwendungszweck, Zertifikatskette, Koppelprodukte, THG</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Profile</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap items-center gap-2">
          <Button variant="outline" size="sm" onClick={clearForm}>Neu</Button>
          <Input className="w-32" placeholder="YYYY-MM" value={derivePeriod} onChange={(e) => setDerivePeriod(e.target.value)} />
          <Button variant="outline" size="sm" onClick={() => deriveMutation.mutate()} disabled={!selectedId || deriveMutation.isPending}>
            Aus Ops ableiten
          </Button>
          {(profileQuery.data ?? []).map((item) => (
            <Button key={item.id} variant={item.id === selectedId ? 'default' : 'outline'} size="sm" onClick={() => loadProfile(item.id)}>
              {item.harvest_year} {item.article_number ?? 'RAPS'}
            </Button>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Produkt und Verwendungszweck</CardTitle></CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-4">
          <div><Label>Artikel-ID</Label><Input value={articleId} onChange={(e) => setArticleId(e.target.value)} /></div>
          <div><Label>Artikel-Nr.</Label><Input value={articleNumber} onChange={(e) => setArticleNumber(e.target.value)} /></div>
          <div><Label>Artikelname</Label><Input value={articleName} onChange={(e) => setArticleName(e.target.value)} /></div>
          <div><Label>Erntejahr</Label><Input type="number" value={harvestYear} onChange={(e) => setHarvestYear(Number(e.target.value) || 0)} /></div>
          <div><Label>Lebensmittel %</Label><Input value={usageFood} onChange={(e) => setUsageFood(e.target.value)} /></div>
          <div><Label>Futter %</Label><Input value={usageFeed} onChange={(e) => setUsageFeed(e.target.value)} /></div>
          <div><Label>Energie %</Label><Input value={usageEnergy} onChange={(e) => setUsageEnergy(e.target.value)} /></div>
          <div><Label>Stofflich %</Label><Input value={usageMaterial} onChange={(e) => setUsageMaterial(e.target.value)} /></div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Kennzahlen</CardTitle></CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div><Label>THG (gCO2eq/MJ)</Label><Input value={thgValue} onChange={(e) => setThgValue(e.target.value)} /></div>
          <div><Label>Ertrag (dt/ha)</Label><Input value={yieldPerHa} onChange={(e) => setYieldPerHa(e.target.value)} /></div>
          <div className="rounded border p-3 text-sm">Verwendungssumme: <span className={usageTotal === 100 ? 'font-semibold text-green-700' : 'font-semibold text-red-700'}>{usageTotal.toFixed(2)}%</span></div>
          <div className="md:col-span-3"><Label>Notiz</Label><Textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} /></div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between"><CardTitle>Zertifikatskette (REDcert/ISCC)</CardTitle><Button variant="outline" size="sm" onClick={() => setCerts((prev) => [...prev, emptyCert()])}><Plus className="h-4 w-4" /></Button></CardHeader>
        <CardContent className="overflow-x-auto">
          <Table>
            <TableHeader><TableRow><TableHead>Schema</TableHead><TableHead>Nummer</TableHead><TableHead>Stufe</TableHead><TableHead>Gueltig von</TableHead><TableHead>Gueltig bis</TableHead><TableHead>Issuer</TableHead><TableHead>Status</TableHead><TableHead className="w-12" /></TableRow></TableHeader>
            <TableBody>
              {certs.map((c, i) => (
                <TableRow key={`cert-${i}`}>
                  <TableCell><Input value={c.scheme} onChange={(e) => updateCert(i, 'scheme', e.target.value)} /></TableCell>
                  <TableCell><Input value={c.certificate_number} onChange={(e) => updateCert(i, 'certificate_number', e.target.value)} /></TableCell>
                  <TableCell><Input value={c.chain_stage ?? ''} onChange={(e) => updateCert(i, 'chain_stage', e.target.value)} /></TableCell>
                  <TableCell><Input type="date" value={c.valid_from ?? ''} onChange={(e) => updateCert(i, 'valid_from', e.target.value)} /></TableCell>
                  <TableCell><Input type="date" value={c.valid_until ?? ''} onChange={(e) => updateCert(i, 'valid_until', e.target.value)} /></TableCell>
                  <TableCell><Input value={c.issuer ?? ''} onChange={(e) => updateCert(i, 'issuer', e.target.value)} /></TableCell>
                  <TableCell><Input value={c.status} onChange={(e) => updateCert(i, 'status', e.target.value)} /></TableCell>
                  <TableCell><Button variant="ghost" size="icon" onClick={() => setCerts((prev) => prev.length > 1 ? prev.filter((_, idx) => idx !== i) : prev)}><Trash2 className="h-4 w-4" /></Button></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between"><CardTitle>Koppelprodukt-Bilanz (Oel/Schrot)</CardTitle><Button variant="outline" size="sm" onClick={() => setBalances((prev) => [...prev, emptyBalance()])}><Plus className="h-4 w-4" /></Button></CardHeader>
        <CardContent className="overflow-x-auto">
          <Table>
            <TableHeader><TableRow><TableHead>Periode</TableHead><TableHead>Saat t</TableHead><TableHead>Oel t</TableHead><TableHead>Schrot t</TableHead><TableHead>Sonstige t</TableHead><TableHead>Kosten Oel %</TableHead><TableHead>Kosten Schrot %</TableHead><TableHead>Miete/Lager</TableHead><TableHead>Logistik-Notiz</TableHead><TableHead className="w-12" /></TableRow></TableHeader>
            <TableBody>
              {balances.map((b, i) => (
                <TableRow key={`bal-${i}`}>
                  <TableCell><Input value={b.booking_period ?? ''} onChange={(e) => updateBalance(i, 'booking_period', e.target.value)} /></TableCell>
                  <TableCell><Input value={b.input_seed_tons} onChange={(e) => updateBalance(i, 'input_seed_tons', e.target.value)} /></TableCell>
                  <TableCell><Input value={b.output_oil_tons} onChange={(e) => updateBalance(i, 'output_oil_tons', e.target.value)} /></TableCell>
                  <TableCell><Input value={b.output_meal_tons} onChange={(e) => updateBalance(i, 'output_meal_tons', e.target.value)} /></TableCell>
                  <TableCell><Input value={b.output_other_tons} onChange={(e) => updateBalance(i, 'output_other_tons', e.target.value)} /></TableCell>
                  <TableCell><Input value={b.allocation_oil_pct ?? ''} onChange={(e) => updateBalance(i, 'allocation_oil_pct', e.target.value)} /></TableCell>
                  <TableCell><Input value={b.allocation_meal_pct ?? ''} onChange={(e) => updateBalance(i, 'allocation_meal_pct', e.target.value)} /></TableCell>
                  <TableCell><Input value={b.heap_location ?? ''} onChange={(e) => updateBalance(i, 'heap_location', e.target.value)} /></TableCell>
                  <TableCell><Input value={b.logistics_note ?? ''} onChange={(e) => updateBalance(i, 'logistics_note', e.target.value)} /></TableCell>
                  <TableCell><Button variant="ghost" size="icon" onClick={() => setBalances((prev) => prev.length > 1 ? prev.filter((_, idx) => idx !== i) : prev)}><Trash2 className="h-4 w-4" /></Button></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <div className="flex gap-2">
        <Button className="gap-2" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}><Save className="h-4 w-4" />Speichern</Button>
        <Button variant="destructive" className="gap-2" onClick={() => deleteMutation.mutate()} disabled={!selectedId || deleteMutation.isPending}><Trash2 className="h-4 w-4" />Loeschen</Button>
      </div>
    </div>
  )
}
