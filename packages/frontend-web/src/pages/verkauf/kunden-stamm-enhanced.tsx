import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, Award, Building2, CheckCircle, CreditCard, Save, Shield, XCircle } from 'lucide-react'

type KundeStammdaten = {
  id: string
  name: string
  kundennr: string
  strasse: string
  plz: string
  ort: string
  telefon: string
  email: string
  ustid: string
  
  // Compliance
  vvvo?: string
  vvvoStatus: 'aktiv' | 'inaktiv' | 'fehlend'
  psmSachkunde?: string
  sachkundeGueltigBis?: string
  sachkundeStatus: 'gueltig' | 'ablaufend' | 'abgelaufen' | 'fehlend'
  
  // Fibu/Kredit
  kreditlinie: number
  kreditAusgenutzt: number
  bonitaet: 'A' | 'B' | 'C' | 'D'
  zahlungsziel: number
  offenePosten: number
  ueberfaellig: number
  
  // Sicherheiten
  sicherheiten: Array<{
    typ: string
    wert: number
    gegenstand: string
  }>
  
  // Auto-Flags
  verkaufGesperrt: boolean
  psmVerkaufErlaubt: boolean
  duengerVerkaufErlaubt: boolean
}

export default function KundenStammEnhancedPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  
  const [kunde, setKunde] = useState<KundeStammdaten>({
    id: id ?? '1',
    name: 'Agrar Schmidt GmbH',
    kundennr: 'K-10023',
    strasse: 'Hauptstraße 15',
    plz: '27356',
    ort: 'Rotenburg (Wümme)',
    telefon: '+49 (0) 4261 98765',
    email: 'info@agrar-schmidt.de',
    ustid: 'DE987654321',
    
    // Auto-gefüllt aus VVVO-Register
    vvvo: '03-276-123456',
    vvvoStatus: 'aktiv',
    
    // Auto-gefüllt aus Sachkunde-Register
    psmSachkunde: 'SK-NDS-2022-4567',
    sachkundeGueltigBis: '2025-03-15',
    sachkundeStatus: 'ablaufend',
    
    // Auto-gefüllt aus Kreditlinien
    kreditlinie: 200000,
    kreditAusgenutzt: 145000,
    bonitaet: 'A',
    zahlungsziel: 30,
    offenePosten: 145000,
    ueberfaellig: 0,
    
    // Auto-gefüllt aus Sicherheiten
    sicherheiten: [
      { typ: 'Abtretung', wert: 150000, gegenstand: 'Forderungsabtretung Ernteerlöse 2025' },
    ],
    
    // Auto-berechnet
    verkaufGesperrt: false,
    psmVerkaufErlaubt: true,
    duengerVerkaufErlaubt: true,
  })

  // Auto-Validierung beim Laden
  useEffect(() => {
    validateKunde()
  }, [])

  function validateKunde(): void {
    const sachkundeAblauf = kunde.sachkundeGueltigBis ? new Date(kunde.sachkundeGueltigBis) : null
    const sachkundeAblaufend = sachkundeAblauf ? sachkundeAblauf <= new Date(Date.now() + 90 * 24 * 60 * 60 * 1000) : false
    const sachkundeAbgelaufen = sachkundeAblauf ? sachkundeAblauf < new Date() : true
    
    const kreditUeberzogen = kunde.kreditAusgenutzt >= kunde.kreditlinie
    const hatUeberfaellige = kunde.ueberfaellig > 0
    
    setKunde((prev) => ({
      ...prev,
      sachkundeStatus: sachkundeAbgelaufen ? 'abgelaufen' : sachkundeAblaufend ? 'ablaufend' : 'gueltig',
      verkaufGesperrt: kreditUeberzogen || hatUeberfaellige || prev.bonitaet === 'D',
      psmVerkaufErlaubt: !sachkundeAbgelaufen && prev.vvvoStatus === 'aktiv',
      duengerVerkaufErlaubt: prev.vvvoStatus === 'aktiv',
    }))
  }

  const kreditAuslastung = (kunde.kreditAusgenutzt / kunde.kreditlinie) * 100
  const gesamtSicherheiten = kunde.sicherheiten.reduce((sum, s) => sum + s.wert, 0)

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Building2 className="h-10 w-10 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Kundenstammdaten (Enhanced)</h1>
            <p className="text-muted-foreground">Automatisches Vorbelegen aus Compliance & Fibu</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {kunde.verkaufGesperrt && (
            <Badge variant="destructive" className="gap-1">
              <XCircle className="h-3 w-3" />
              Verkauf gesperrt
            </Badge>
          )}
          {kunde.psmVerkaufErlaubt && (
            <Badge variant="outline" className="gap-1 bg-green-50">
              <CheckCircle className="h-3 w-3 text-green-600" />
              PSM-Verkauf OK
            </Badge>
          )}
          <Button onClick={() => navigate('/verkauf/kunden-liste')} variant="outline">
            Abbrechen
          </Button>
          <Button className="gap-2">
            <Save className="h-4 w-4" />
            Speichern
          </Button>
        </div>
      </div>

      {/* Alert-Banner */}
      {(kunde.verkaufGesperrt || kunde.sachkundeStatus === 'ablaufend' || kreditAuslastung > 80) && (
        <div className="space-y-2">
          {kunde.verkaufGesperrt && (
            <Card className="border-red-500 bg-red-50">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-red-900">
                  <AlertTriangle className="h-5 w-5" />
                  <span className="font-semibold">
                    Verkauf gesperrt! Grund: {kunde.bonitaet === 'D' ? 'Bonität D (nur Vorkasse)' : kunde.ueberfaellig > 0 ? 'Überfällige Rechnungen' : 'Kreditlinie überzogen'}
                  </span>
                </div>
              </CardContent>
            </Card>
          )}
          {kunde.sachkundeStatus === 'ablaufend' && !kunde.verkaufGesperrt && (
            <Card className="border-orange-500 bg-orange-50">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-orange-900">
                  <AlertTriangle className="h-5 w-5" />
                  <span className="font-semibold">PSM-Sachkunde läuft in 3 Monaten ab! (Gültig bis: {kunde.sachkundeGueltigBis})</span>
                </div>
              </CardContent>
            </Card>
          )}
          {kreditAuslastung > 80 && !kunde.verkaufGesperrt && (
            <Card className="border-orange-500 bg-orange-50">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-orange-900">
                  <AlertTriangle className="h-5 w-5" />
                  <span className="font-semibold">Kreditlinie zu {kreditAuslastung.toFixed(0)}% ausgelastet!</span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      <Tabs defaultValue="stammdaten" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="stammdaten">Stammdaten</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="fibu">Finanzen & Kredit</TabsTrigger>
          <TabsTrigger value="sicherheiten">Sicherheiten</TabsTrigger>
        </TabsList>

        <TabsContent value="stammdaten">
          <Card>
            <CardHeader>
              <CardTitle>Allgemeine Daten</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div>
                <Label htmlFor="name">Firmenname *</Label>
                <Input id="name" value={kunde.name} onChange={(e) => setKunde({ ...kunde, name: e.target.value })} />
              </div>
              <div>
                <Label htmlFor="kundennr">Kundennummer</Label>
                <Input id="kundennr" value={kunde.kundennr} disabled className="font-mono bg-muted" />
              </div>
              <div className="md:col-span-2">
                <Label htmlFor="strasse">Straße & Hausnummer</Label>
                <Input id="strasse" value={kunde.strasse} onChange={(e) => setKunde({ ...kunde, strasse: e.target.value })} />
              </div>
              <div>
                <Label htmlFor="plz">PLZ</Label>
                <Input id="plz" value={kunde.plz} onChange={(e) => setKunde({ ...kunde, plz: e.target.value })} />
              </div>
              <div>
                <Label htmlFor="ort">Ort</Label>
                <Input id="ort" value={kunde.ort} onChange={(e) => setKunde({ ...kunde, ort: e.target.value })} />
              </div>
              <div>
                <Label htmlFor="telefon">Telefon</Label>
                <Input id="telefon" value={kunde.telefon} onChange={(e) => setKunde({ ...kunde, telefon: e.target.value })} />
              </div>
              <div>
                <Label htmlFor="email">E-Mail</Label>
                <Input id="email" type="email" value={kunde.email} onChange={(e) => setKunde({ ...kunde, email: e.target.value })} />
              </div>
              <div className="md:col-span-2">
                <Label htmlFor="ustid">USt-IdNr.</Label>
                <Input id="ustid" value={kunde.ustid} onChange={(e) => setKunde({ ...kunde, ustid: e.target.value })} className="font-mono" />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compliance">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5" />
                  VVVO Betriebsnummer
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <Label htmlFor="vvvo">VVVO-Nummer (12-stellig)</Label>
                  <Input id="vvvo" value={kunde.vvvo ?? ''} disabled className="font-mono font-bold text-lg bg-muted" />
                  <p className="mt-1 text-xs text-muted-foreground">Auto-geladen aus VVVO-Register</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm">Status:</span>
                  <Badge variant={kunde.vvvoStatus === 'aktiv' ? 'outline' : 'destructive'}>
                    {kunde.vvvoStatus === 'aktiv' ? 'Aktiv' : kunde.vvvoStatus === 'inaktiv' ? 'Inaktiv' : 'Fehlend'}
                  </Badge>
                </div>
                <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-900">
                  <p className="font-semibold">Viehverkehrsverordnung</p>
                  <p className="mt-1 text-xs">Pflicht für Tierhaltung & Futtermittelverkauf</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  PSM-Sachkunde
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <Label htmlFor="sachkunde">Nachweis-Nummer</Label>
                  <Input id="sachkunde" value={kunde.psmSachkunde ?? ''} disabled className="font-mono bg-muted" />
                  <p className="mt-1 text-xs text-muted-foreground">Auto-geladen aus Sachkunde-Register</p>
                </div>
                <div>
                  <Label htmlFor="gueltigBis">Gültig bis</Label>
                  <Input id="gueltigBis" value={kunde.sachkundeGueltigBis ?? ''} disabled className="bg-muted" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm">Status:</span>
                  <Badge variant={kunde.sachkundeStatus === 'gueltig' ? 'outline' : kunde.sachkundeStatus === 'ablaufend' ? 'secondary' : 'destructive'}>
                    {kunde.sachkundeStatus === 'gueltig' ? 'Gültig' : kunde.sachkundeStatus === 'ablaufend' ? 'Läuft ab' : kunde.sachkundeStatus === 'abgelaufen' ? 'Abgelaufen' : 'Fehlend'}
                  </Badge>
                </div>
                <div className={`rounded-lg p-3 text-sm ${kunde.psmVerkaufErlaubt ? 'bg-green-50 text-green-900' : 'bg-red-50 text-red-900'}`}>
                  <p className="font-semibold">{kunde.psmVerkaufErlaubt ? '✓ PSM-Verkauf erlaubt' : '✗ PSM-Verkauf gesperrt'}</p>
                  <p className="mt-1 text-xs">§ 9 PflSchG - Sachkundenachweis erforderlich</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="fibu">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Kreditlinie & Bonität
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <Label>Bonität</Label>
                  <div className="mt-2">
                    <span className={`text-4xl font-bold ${kunde.bonitaet === 'A' ? 'text-green-600' : kunde.bonitaet === 'B' ? 'text-blue-600' : kunde.bonitaet === 'C' ? 'text-orange-600' : 'text-red-600'}`}>
                      {kunde.bonitaet}
                    </span>
                    <p className="mt-1 text-xs text-muted-foreground">Auto-berechnet aus Zahlungsverhalten</p>
                  </div>
                </div>
                <div>
                  <Label>Kreditlimit</Label>
                  <div className="mt-2">
                    <div className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kunde.kreditlinie)}</div>
                    <p className="mt-1 text-xs text-muted-foreground">Bonität {kunde.bonitaet}-abhängig</p>
                  </div>
                </div>
                <div>
                  <Label>Zahlungsziel</Label>
                  <div className="mt-2">
                    <div className="text-2xl font-bold">{kunde.zahlungsziel} Tage</div>
                    <p className="mt-1 text-xs text-muted-foreground">Standard-Zahlungsziel</p>
                  </div>
                </div>
              </div>

              <div>
                <Label>Kreditauslastung</Label>
                <div className="mt-2 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Ausgenutzt: {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kunde.kreditAusgenutzt)}</span>
                    <span className="font-semibold">{kreditAuslastung.toFixed(0)}%</span>
                  </div>
                  <div className="h-3 w-full bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${kreditAuslastung >= 100 ? 'bg-red-500' : kreditAuslastung > 80 ? 'bg-orange-500' : 'bg-green-500'}`}
                      style={{ width: `${Math.min(kreditAuslastung, 100)}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Verfügbar</span>
                    <span className="font-semibold text-green-600">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kunde.kreditlinie - kunde.kreditAusgenutzt)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-lg border p-3">
                  <div className="text-sm text-muted-foreground">Offene Posten</div>
                  <div className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kunde.offenePosten)}</div>
                </div>
                <div className="rounded-lg border p-3">
                  <div className="text-sm text-muted-foreground">Überfällig</div>
                  <div className={`text-2xl font-bold ${kunde.ueberfaellig > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {kunde.ueberfaellig > 0 ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kunde.ueberfaellig) : '–'}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sicherheiten">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Hinterlegte Sicherheiten
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
                <p className="font-semibold">Gesamtwert Sicherheiten: {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtSicherheiten)}</p>
                <p className="mt-1 text-xs">Auto-geladen aus Sicherheiten-Verwaltung</p>
              </div>

              <div className="space-y-2">
                {kunde.sicherheiten.map((s, i) => (
                  <div key={i} className="rounded-lg border p-3">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-semibold">{s.typ}</div>
                        <div className="text-sm text-muted-foreground">{s.gegenstand}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(s.wert)}</div>
                        <Badge variant="outline">Aktiv</Badge>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <Button variant="outline" className="w-full" onClick={() => navigate('/fibu/sicherheiten')}>
                Zu Sicherheiten-Verwaltung
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
