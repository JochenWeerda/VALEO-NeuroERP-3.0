import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { Save, User } from 'lucide-react'

type KundeData = {
  id: string
  name: string
  typ: string
  strasse: string
  plz: string
  ort: string
  email: string
  telefon: string
  zahlungsziel: number
  kreditlimit: number
  status: 'aktiv' | 'gesperrt'
}

export default function KundenStammPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const defaultTenantId = import.meta.env.VITE_TENANT_ID ?? '00000000-0000-0000-0000-000000000001'
  const [kunde, setKunde] = useState<KundeData>({
    id: 'K-001',
    name: 'Landhandel Nord GmbH',
    typ: 'Landhandel',
    strasse: 'Hauptstraße 42',
    plz: '12345',
    ort: 'Nordhausen',
    email: 'info@landhandel-nord.de',
    telefon: '+49 123 456789',
    zahlungsziel: 30,
    kreditlimit: 50000,
    status: 'aktiv',
  })
  const [isSaving, setIsSaving] = useState(false)

  const validateForm = (): string | null => {
    // Pflichtfelder prüfen
    if (!kunde.name.trim()) {
      return 'Firmenname ist ein Pflichtfeld'
    }
    if (!kunde.strasse.trim()) {
      return 'Straße ist ein Pflichtfeld'
    }
    if (!kunde.plz.trim()) {
      return 'PLZ ist ein Pflichtfeld'
    }
    if (!kunde.ort.trim()) {
      return 'Ort ist ein Pflichtfeld'
    }
    
    // E-Mail-Format prüfen (wenn vorhanden)
    if (kunde.email?.trim()) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(kunde.email)) {
        return 'Ungültiges E-Mail-Format'
      }
    }
    
    // PLZ-Format prüfen (5 Ziffern)
    if (kunde.plz && !/^\d{5}$/.test(kunde.plz)) {
      return 'PLZ muss 5 Ziffern enthalten'
    }
    
    // Zahlungsziel prüfen
    if (kunde.zahlungsziel < 0 || kunde.zahlungsziel > 365) {
      return 'Zahlungsziel muss zwischen 0 und 365 Tagen liegen'
    }
    
    // Kreditlimit prüfen
    if (kunde.kreditlimit < 0) {
      return 'Kreditlimit darf nicht negativ sein'
    }
    
    return null
  }

  const handleSave = async () => {
    // Validierung durchführen
    const validationError = validateForm()
    if (validationError) {
      toast({
        title: 'Validierungsfehler',
        description: validationError,
        variant: 'destructive',
      })
      return
    }
    
    setIsSaving(true)
    try {
      // Transform frontend data to backend format
      const customerData = {
        tenant_id: defaultTenantId,
        customer_number: kunde.id,
        company_name: kunde.name,
        customer_type: kunde.typ,
        contact_person: kunde.typ,
        address: `${kunde.strasse}`,
        city: kunde.ort,
        postal_code: kunde.plz,
        country: 'DE',
        email: kunde.email,
        phone: kunde.telefon,
        payment_terms: kunde.zahlungsziel,
        credit_limit: kunde.kreditlimit,
        status: kunde.status,
      }

      const savedCustomer = await apiClient.post('/api/v1/crm/customers', customerData)
      
      toast({
        title: 'Kunde gespeichert',
        description: `Kunde ${savedCustomer.company_name} wurde erfolgreich gespeichert.`,
      })

      // Navigate to customer list after successful save
      setTimeout(() => navigate('/verkauf/kunden-liste'), 1000)
    } catch (error) {
      toast({
        title: 'Fehler beim Speichern',
        description: error instanceof Error ? error.message : 'Ein unbekannter Fehler ist aufgetreten.',
        variant: 'destructive',
      })
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <User className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{kunde.name}</h1>
              <p className="text-muted-foreground">Kundennummer: {kunde.id}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/verkauf/kunden-liste')} disabled={isSaving}>
            Zurück
          </Button>
          <Button className="gap-2" onClick={handleSave} disabled={isSaving}>
            <Save className="h-4 w-4" />
            {isSaving ? 'Speichere...' : 'Speichern'}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="stammdaten">
        <TabsList>
          <TabsTrigger value="stammdaten">Stammdaten</TabsTrigger>
          <TabsTrigger value="konditionen">Konditionen</TabsTrigger>
          <TabsTrigger value="historie">Historie</TabsTrigger>
        </TabsList>

        <TabsContent value="stammdaten">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Unternehmensdaten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Firmenname <span className="text-destructive">*</span></Label>
                  <Input 
                    value={kunde.name} 
                    onChange={(e) => setKunde({ ...kunde, name: e.target.value })} 
                    required
                  />
                </div>
                <div>
                  <Label>Typ</Label>
                  <Input value={kunde.typ} onChange={(e) => setKunde({ ...kunde, typ: e.target.value })} />
                </div>
                <div>
                  <Label>Status</Label>
                  <div className="mt-2">
                    <Badge variant={kunde.status === 'aktiv' ? 'outline' : 'destructive'}>
                      {kunde.status === 'aktiv' ? 'Aktiv' : 'Gesperrt'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Adresse</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Straße <span className="text-destructive">*</span></Label>
                  <Input 
                    value={kunde.strasse} 
                    onChange={(e) => setKunde({ ...kunde, strasse: e.target.value })} 
                    required
                  />
                </div>
                <div className="grid gap-4 grid-cols-3">
                  <div className="col-span-1">
                    <Label>PLZ <span className="text-destructive">*</span></Label>
                    <Input 
                      value={kunde.plz} 
                      onChange={(e) => setKunde({ ...kunde, plz: e.target.value })} 
                      maxLength={5}
                      required
                    />
                  </div>
                  <div className="col-span-2">
                    <Label>Ort <span className="text-destructive">*</span></Label>
                    <Input 
                      value={kunde.ort} 
                      onChange={(e) => setKunde({ ...kunde, ort: e.target.value })} 
                      required
                    />
                  </div>
                </div>
                <div>
                  <Label>E-Mail</Label>
                  <Input 
                    type="email" 
                    value={kunde.email} 
                    onChange={(e) => setKunde({ ...kunde, email: e.target.value })} 
                  />
                </div>
                <div>
                  <Label>Telefon</Label>
                  <Input type="tel" value={kunde.telefon} onChange={(e) => setKunde({ ...kunde, telefon: e.target.value })} />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="konditionen">
          <Card>
            <CardHeader>
              <CardTitle>Zahlungskonditionen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Zahlungsziel (Tage)</Label>
                  <Input 
                    type="number" 
                    value={kunde.zahlungsziel} 
                    onChange={(e) => setKunde({ ...kunde, zahlungsziel: parseInt(e.target.value) || 0 })} 
                  />
                </div>
                <div>
                  <Label>Kreditlimit (€)</Label>
                  <Input 
                    type="number" 
                    value={kunde.kreditlimit} 
                    onChange={(e) => setKunde({ ...kunde, kreditlimit: parseFloat(e.target.value) || 0 })} 
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="historie">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground">Keine Einträge</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
