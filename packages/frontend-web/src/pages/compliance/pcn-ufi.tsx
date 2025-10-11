import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { CheckCircle, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'

type PCNData = {
  produktname: string
  ufi: string
  cas_nummern: string
  gefahrenklassen: string[]
  verwendungskategorie: string
  pcnStatus: 'entwurf' | 'eingereicht' | 'accepted' | 'rejected'
}

export default function PCNUFIPage(): JSX.Element {
  const navigate = useNavigate()
  const [pcn, setPCN] = useState<PCNData>({
    produktname: '',
    ufi: '',
    cas_nummern: '',
    gefahrenklassen: [],
    verwendungskategorie: '',
    pcnStatus: 'entwurf',
  })

  function generateUFI(): void {
    // UFI-Format: XXXX-XXXX-XXXX-XXXX
    const part = () => Math.random().toString(36).substring(2, 6).toUpperCase()
    const ufi = `${part()}-${part()}-${part()}-${part()}`
    setPCN({ ...pcn, ufi })
  }

  const steps = [
    {
      id: 'produkt',
      title: 'Produkt',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="produktname">Produktname *</Label>
            <Input
              id="produktname"
              value={pcn.produktname}
              onChange={(e) => setPCN({ ...pcn, produktname: e.target.value })}
              placeholder="z.B. Fungizid A Professional"
            />
          </div>
          <div>
            <Label htmlFor="ufi">UFI (Unique Formula Identifier) *</Label>
            <div className="flex gap-2">
              <Input
                id="ufi"
                value={pcn.ufi}
                onChange={(e) => setPCN({ ...pcn, ufi: e.target.value })}
                placeholder="XXXX-XXXX-XXXX-XXXX"
                className="font-mono"
              />
              <Button type="button" onClick={generateUFI} variant="outline">
                Generieren
              </Button>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              16-stelliger Code nach Annex VIII (ab 01.01.2025 Pflicht)
            </p>
          </div>
          <div>
            <Label htmlFor="verwendung">Verwendungskategorie</Label>
            <select
              id="verwendung"
              value={pcn.verwendungskategorie}
              onChange={(e) => setPCN({ ...pcn, verwendungskategorie: e.target.value })}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="SU24">SU24 - Pflanzenschutzmittel</option>
              <option value="PC12">PC12 - Düngemittel</option>
              <option value="PC35">PC35 - Wasch- und Reinigungsmittel</option>
            </select>
          </div>
        </div>
      ),
    },
    {
      id: 'gefahrstoffe',
      title: 'Gefahrstoffe',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="cas">CAS-Nummern (kommasepariert)</Label>
            <Textarea
              id="cas"
              value={pcn.cas_nummern}
              onChange={(e) => setPCN({ ...pcn, cas_nummern: e.target.value })}
              placeholder="z.B. 1912-24-9, 107534-96-3"
              rows={3}
            />
          </div>
          <div>
            <Label>Gefahrenklassen (GHS)</Label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {['H302', 'H315', 'H317', 'H400', 'H410'].map((h) => (
                <label key={h} className="flex items-center gap-2 rounded-md border p-3 cursor-pointer hover:bg-accent">
                  <input type="checkbox" className="rounded" />
                  <span className="text-sm font-mono">{h}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="rounded-lg bg-orange-50 p-4 text-sm text-orange-900">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              <p className="font-semibold">Pflichtangaben nach CLP-Verordnung</p>
            </div>
            <p className="mt-1">Vollständige Rezeptur gemäß Annex VIII der CLP-VO erforderlich</p>
          </div>
        </div>
      ),
    },
    {
      id: 'zusammenfassung',
      title: 'Zusammenfassung',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-green-600" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">PCN bereit für ECHA-Übermittlung</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Produktname</dt>
                <dd className="font-semibold">{pcn.produktname || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>UFI</dt>
                <dd className="font-mono font-semibold">{pcn.ufi || 'Nicht generiert'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Verwendung</dt>
                <dd className="font-semibold">{pcn.verwendungskategorie || '-'}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Status</dt>
                <dd>
                  <Badge variant="outline">Entwurf</Badge>
                </dd>
              </div>
            </dl>
            <div className="mt-6 space-y-2">
              <Button className="w-full">XML für ECHA-Portal generieren</Button>
              <div className="rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
                <p className="font-semibold">Poison Centre Notification (ECHA)</p>
                <p className="mt-1">PCN-Portal: poisoncentres.echa.europa.eu</p>
              </div>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="PCN/UFI Generator"
        subtitle="Poison Centre Notification (ECHA Annex VIII)"
        steps={steps}
        onFinish={() => navigate('/compliance/pcn-liste')}
        onCancel={() => navigate('/compliance/pcn-liste')}
      />
    </div>
  )
}
