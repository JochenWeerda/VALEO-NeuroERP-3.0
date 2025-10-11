import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Building2, Save } from 'lucide-react'

type Firmendaten = {
  name: string
  rechtsform: string
  strasse: string
  plz: string
  ort: string
  telefon: string
  email: string
  website: string
  ustid: string
  steuernr: string
  handelsregister: string
  geschaeftsfuehrer: string
  bankname: string
  iban: string
  bic: string
}

export default function FirmaSetupPage(): JSX.Element {
  const [firma, setFirma] = useState<Firmendaten>({
    name: 'VALERO Landhandel GmbH',
    rechtsform: 'GmbH',
    strasse: 'Hauptstraße 42',
    plz: '27356',
    ort: 'Rotenburg (Wümme)',
    telefon: '+49 (0) 4261 12345',
    email: 'info@valero-landhandel.de',
    website: 'www.valero-landhandel.de',
    ustid: 'DE123456789',
    steuernr: '24/123/45678',
    handelsregister: 'HRB 12345',
    geschaeftsfuehrer: 'Max Mustermann',
    bankname: 'Sparkasse Rotenburg-Bremervörde',
    iban: 'DE89 2415 0000 0000 1234 56',
    bic: 'BRLADE21ROB',
  })

  function handleSave(): void {
    console.log('Firmendaten gespeichert:', firma)
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Building2 className="h-10 w-10 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Firmenstammdaten</h1>
            <p className="text-muted-foreground">Zentrale Einstellungen für Ihr Unternehmen</p>
          </div>
        </div>
        <Badge variant="outline">Basis-Setup</Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Allgemeine Daten */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Allgemeine Angaben</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="name">Firmenname *</Label>
              <Input id="name" value={firma.name} onChange={(e) => setFirma({ ...firma, name: e.target.value })} />
            </div>
            <div>
              <Label htmlFor="rechtsform">Rechtsform</Label>
              <select
                id="rechtsform"
                value={firma.rechtsform}
                onChange={(e) => setFirma({ ...firma, rechtsform: e.target.value })}
                className="w-full rounded-md border border-input bg-background px-3 py-2"
              >
                <option value="GmbH">GmbH</option>
                <option value="AG">AG</option>
                <option value="KG">KG</option>
                <option value="OHG">OHG</option>
                <option value="e.K.">e.K.</option>
              </select>
            </div>
            <div>
              <Label htmlFor="strasse">Straße & Hausnummer *</Label>
              <Input id="strasse" value={firma.strasse} onChange={(e) => setFirma({ ...firma, strasse: e.target.value })} />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <div className="col-span-1">
                <Label htmlFor="plz">PLZ *</Label>
                <Input id="plz" value={firma.plz} onChange={(e) => setFirma({ ...firma, plz: e.target.value })} />
              </div>
              <div className="col-span-2">
                <Label htmlFor="ort">Ort *</Label>
                <Input id="ort" value={firma.ort} onChange={(e) => setFirma({ ...firma, ort: e.target.value })} />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Kontaktdaten */}
        <Card>
          <CardHeader>
            <CardTitle>Kontaktdaten</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            <div>
              <Label htmlFor="telefon">Telefon</Label>
              <Input id="telefon" value={firma.telefon} onChange={(e) => setFirma({ ...firma, telefon: e.target.value })} />
            </div>
            <div>
              <Label htmlFor="email">E-Mail</Label>
              <Input id="email" type="email" value={firma.email} onChange={(e) => setFirma({ ...firma, email: e.target.value })} />
            </div>
            <div>
              <Label htmlFor="website">Website</Label>
              <Input id="website" value={firma.website} onChange={(e) => setFirma({ ...firma, website: e.target.value })} />
            </div>
          </CardContent>
        </Card>

        {/* Steuerliche Daten */}
        <Card>
          <CardHeader>
            <CardTitle>Steuerliche Angaben</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            <div>
              <Label htmlFor="ustid">USt-IdNr. *</Label>
              <Input id="ustid" value={firma.ustid} onChange={(e) => setFirma({ ...firma, ustid: e.target.value })} className="font-mono" />
            </div>
            <div>
              <Label htmlFor="steuernr">Steuernummer</Label>
              <Input id="steuernr" value={firma.steuernr} onChange={(e) => setFirma({ ...firma, steuernr: e.target.value })} className="font-mono" />
            </div>
            <div>
              <Label htmlFor="handelsregister">Handelsregister-Nr.</Label>
              <Input id="handelsregister" value={firma.handelsregister} onChange={(e) => setFirma({ ...firma, handelsregister: e.target.value })} className="font-mono" />
            </div>
            <div>
              <Label htmlFor="geschaeftsfuehrer">Geschäftsführer</Label>
              <Input id="geschaeftsfuehrer" value={firma.geschaeftsfuehrer} onChange={(e) => setFirma({ ...firma, geschaeftsfuehrer: e.target.value })} />
            </div>
          </CardContent>
        </Card>

        {/* Bankverbindung */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Bankverbindung</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <div className="md:col-span-3">
              <Label htmlFor="bankname">Bankname</Label>
              <Input id="bankname" value={firma.bankname} onChange={(e) => setFirma({ ...firma, bankname: e.target.value })} />
            </div>
            <div className="md:col-span-2">
              <Label htmlFor="iban">IBAN *</Label>
              <Input id="iban" value={firma.iban} onChange={(e) => setFirma({ ...firma, iban: e.target.value })} className="font-mono" />
            </div>
            <div>
              <Label htmlFor="bic">BIC</Label>
              <Input id="bic" value={firma.bic} onChange={(e) => setFirma({ ...firma, bic: e.target.value })} className="font-mono" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-4">
        <Button variant="outline">Abbrechen</Button>
        <Button onClick={handleSave} className="gap-2">
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>
    </div>
  )
}
