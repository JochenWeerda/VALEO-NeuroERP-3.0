import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Camera, FileCheck, MapPin, Package } from 'lucide-react'

type WareneingangData = {
  lieferant: string
  lieferscheinNr: string
  artikel: string
  menge: number
  einheit: string
  chargenId: string
  chargenIdAuto: boolean
  gvoStatus: 'gvo-frei-zertifiziert' | 'gvo-frei-erklaerung' | 'spuren' | 'kennzeichnungspflichtig'
  qsMilch: boolean
  eudr: boolean
  nachhaltigRaps: boolean
  lagerort: string
  lagerplatz: string
}

export default function WareneingangPage(): JSX.Element {
  const navigate = useNavigate()
  const [wareneingang, setWareneingang] = useState<WareneingangData>({
    lieferant: '',
    lieferscheinNr: '',
    artikel: '',
    menge: 0,
    einheit: 't',
    chargenId: '',
    chargenIdAuto: true,
    gvoStatus: 'gvo-frei-zertifiziert',
    qsMilch: false,
    eudr: true,
    nachhaltigRaps: false,
    lagerort: '',
    lagerplatz: '',
  })

  function updateField<K extends keyof WareneingangData>(key: K, value: WareneingangData[K]): void {
    const updated = { ...wareneingang, [key]: value }

    // Auto-Generate Chargen-ID
    if (updated.chargenIdAuto && updated.artikel) {
      const datum = new Date().toISOString().slice(2, 10).replace(/-/g, '')
      const artikel = updated.artikel.slice(0, 3).toUpperCase()
      updated.chargenId = `${datum}-${artikel}-001`
    }

    setWareneingang(updated)
  }

  async function handleSubmit(): Promise<void> {
    console.log('Wareneingang buchen:', wareneingang)
    navigate('/charge/liste')
  }

  const steps = [
    {
      id: 'lieferant',
      title: 'Lieferant',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="lieferant">Lieferant *</Label>
            <Input
              id="lieferant"
              value={wareneingang.lieferant}
              onChange={(e) => updateField('lieferant', e.target.value)}
              placeholder="Name des Lieferanten"
              required
            />
          </div>
          <div>
            <Label htmlFor="lieferscheinNr">Lieferschein-Nr. *</Label>
            <div className="flex gap-2">
              <Input
                id="lieferscheinNr"
                value={wareneingang.lieferscheinNr}
                onChange={(e) => updateField('lieferscheinNr', e.target.value)}
                placeholder="z.B. LS-2025-0042"
                required
              />
              <button
                type="button"
                className="flex items-center gap-2 rounded-md border border-input bg-background px-4 hover:bg-accent"
              >
                <Camera className="h-4 w-4" />
                OCR
              </button>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">Lieferschein scannen oder manuell eingeben</p>
          </div>
        </div>
      ),
    },
    {
      id: 'artikel',
      title: 'Artikel',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="artikel">Artikel *</Label>
            <Input
              id="artikel"
              value={wareneingang.artikel}
              onChange={(e) => updateField('artikel', e.target.value)}
              placeholder="z.B. Weizen Qualität A"
              required
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label htmlFor="menge">Menge *</Label>
              <Input
                id="menge"
                type="number"
                value={wareneingang.menge}
                onChange={(e) => updateField('menge', Number(e.target.value))}
                min="0"
                step="0.001"
                required
              />
            </div>
            <div>
              <Label htmlFor="einheit">Einheit</Label>
              <select
                id="einheit"
                value={wareneingang.einheit}
                onChange={(e) => updateField('einheit', e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2"
              >
                <option value="t">Tonnen (t)</option>
                <option value="kg">Kilogramm (kg)</option>
                <option value="l">Liter (l)</option>
                <option value="Stk">Stück</option>
              </select>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'charge',
      title: 'Chargen-ID',
      content: (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="chargenIdAuto"
              checked={wareneingang.chargenIdAuto}
              onChange={(e) => updateField('chargenIdAuto', e.target.checked)}
              className="h-4 w-4"
            />
            <Label htmlFor="chargenIdAuto">Automatisch generieren</Label>
          </div>
          <div>
            <Label htmlFor="chargenId">Chargen-ID *</Label>
            <Input
              id="chargenId"
              value={wareneingang.chargenId}
              onChange={(e) => updateField('chargenId', e.target.value)}
              placeholder="z.B. 251011-WEI-001"
              required
              disabled={wareneingang.chargenIdAuto}
              className="font-mono"
            />
            <p className="mt-1 text-sm text-muted-foreground">
              Format: JJMMTT-ART-SEQ (Jahr-Monat-Tag-Artikelkürzel-Sequenz)
            </p>
          </div>
          {wareneingang.chargenId && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <Package className="h-8 w-8 text-blue-600" />
                  <div>
                    <div className="text-sm text-muted-foreground">Neue Charge</div>
                    <div className="text-xl font-bold font-mono">{wareneingang.chargenId}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      ),
    },
    {
      id: 'qs-attribute',
      title: 'QS-Attribute',
      content: (
        <div className="space-y-4">
          <div className="rounded-lg bg-muted p-4 mb-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <FileCheck className="h-4 w-4" />
              Qualitäts- und Nachhaltigkeits-Attribute (aus Lieferschein oder Zertifikat)
            </div>
          </div>
          <div>
            <Label htmlFor="gvoStatus">GVO-Status *</Label>
            <select
              id="gvoStatus"
              value={wareneingang.gvoStatus}
              onChange={(e) =>
                updateField('gvoStatus', e.target.value as WareneingangData['gvoStatus'])
              }
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="gvo-frei-zertifiziert">GVO-frei zertifiziert (VLOG)</option>
              <option value="gvo-frei-erklaerung">GVO-frei (Eigenerklärung)</option>
              <option value="spuren">Spuren möglich ({'<'} 0,9%)</option>
              <option value="kennzeichnungspflichtig">Kennzeichnungspflichtig</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="qsMilch"
              checked={wareneingang.qsMilch}
              onChange={(e) => updateField('qsMilch', e.target.checked)}
              className="h-4 w-4"
            />
            <Label htmlFor="qsMilch">QS-Milch konform</Label>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="eudr"
              checked={wareneingang.eudr}
              onChange={(e) => updateField('eudr', e.target.checked)}
              className="h-4 w-4"
            />
            <Label htmlFor="eudr">EUDR-konform (entwaldungsfrei)</Label>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="nachhaltigRaps"
              checked={wareneingang.nachhaltigRaps}
              onChange={(e) => updateField('nachhaltigRaps', e.target.checked)}
              className="h-4 w-4"
            />
            <Label htmlFor="nachhaltigRaps">Nachhaltig-Raps (ISCC/REDcert)</Label>
          </div>
        </div>
      ),
    },
    {
      id: 'lagerort',
      title: 'Lagerort',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="lagerort">Lagerort *</Label>
            <select
              id="lagerort"
              value={wareneingang.lagerort}
              onChange={(e) => updateField('lagerort', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Lagerort wählen --</option>
              <option value="silo-1">Silo 1 (Weizen)</option>
              <option value="silo-2">Silo 2 (Gerste)</option>
              <option value="silo-3">Silo 3 (Mais)</option>
              <option value="halle-a">Halle A (Säcke)</option>
              <option value="halle-b">Halle B (Paletten)</option>
            </select>
          </div>
          <div>
            <Label htmlFor="lagerplatz">Lagerplatz</Label>
            <Input
              id="lagerplatz"
              value={wareneingang.lagerplatz}
              onChange={(e) => updateField('lagerplatz', e.target.value)}
              placeholder="z.B. A-12-03"
            />
          </div>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 mb-4">
                <MapPin className="h-6 w-6 text-blue-600" />
                <div>
                  <div className="font-semibold">Lagerplatz-Vorschau</div>
                  <div className="text-sm text-muted-foreground">
                    {wareneingang.lagerort || 'Nicht zugewiesen'} /{' '}
                    {wareneingang.lagerplatz || 'Auto'}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ),
    },
    {
      id: 'bestaetigung',
      title: 'Bestätigung',
      content: (
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <h3 className="mb-4 text-lg font-semibold">Wareneingang Zusammenfassung</h3>
              <dl className="grid gap-3">
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Lieferant</dt>
                  <dd className="text-sm font-semibold">{wareneingang.lieferant || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Lieferschein-Nr.</dt>
                  <dd className="text-sm font-semibold">{wareneingang.lieferscheinNr || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Artikel</dt>
                  <dd className="text-sm font-semibold">{wareneingang.artikel || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Menge</dt>
                  <dd className="text-sm font-semibold">
                    {wareneingang.menge} {wareneingang.einheit}
                  </dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Chargen-ID</dt>
                  <dd className="text-sm font-semibold font-mono">{wareneingang.chargenId || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">GVO-Status</dt>
                  <dd className="text-sm">
                    <Badge variant="outline">
                      {wareneingang.gvoStatus === 'gvo-frei-zertifiziert'
                        ? 'GVO-frei (VLOG)'
                        : wareneingang.gvoStatus === 'gvo-frei-erklaerung'
                          ? 'GVO-frei (Erklärung)'
                          : wareneingang.gvoStatus === 'spuren'
                            ? 'Spuren möglich'
                            : 'Kennzeichnungspflichtig'}
                    </Badge>
                  </dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">QS-Milch</dt>
                  <dd className="text-sm font-semibold">
                    {wareneingang.qsMilch ? '✓ Ja' : '- Nein'}
                  </dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">EUDR-konform</dt>
                  <dd className="text-sm font-semibold">
                    {wareneingang.eudr ? '✓ Ja' : '✗ Nein'}
                  </dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Lagerort</dt>
                  <dd className="text-sm font-semibold">
                    {wareneingang.lagerort || '-'} / {wareneingang.lagerplatz || 'Auto'}
                  </dd>
                </div>
              </dl>
            </CardContent>
          </Card>
          <div className="rounded-lg bg-green-50 p-4 text-center text-sm text-green-900">
            <p className="font-semibold">Wareneingang wird gebucht und Etiketten gedruckt</p>
            <p className="mt-1">Charge wird automatisch im System angelegt</p>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Wareneingang buchen"
        steps={steps}
        onFinish={handleSubmit}
        onCancel={() => navigate('/charge/liste')}
      />
    </div>
  )
}
