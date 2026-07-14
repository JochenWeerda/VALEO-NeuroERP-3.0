import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Wizard } from '@/components/patterns/Wizard'
import { useKulturen } from '@/lib/api/agrar'
import { useToast } from '@/components/ui/toast-provider'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle, FileDown, ClipboardList } from 'lucide-react'
import { NextActionPanel, OperationalTaskPlan } from '@/components/workflow'
import {
  type GruenlandNutzung,
  type StandortTyp,
  type Bestandstyp,
  getGruenlandTabelle,
  GRUENLAND_NUTZUNG_LABELS,
  TAB1_MARSCH,
  TAB2_GEEST,
  WINTERGERSTE_OFFSET_KG,
  SCHWEFEL_RAPS_KG_HA,
  SCHWEFEL_GETREIDE_MARSCH_KG_HA,
} from './lwkDuengeTabellen'

type BedarfData = {
  flaeche: number
  kultur: string
  /** Phase 2: Grünland */
  gruenlandNutzung?: GruenlandNutzung
  standortTyp?: StandortTyp | 'marsch' | 'geest'
  vorjahresOrgDungung?: boolean
  /** Phase 2: Wintergetreide/Raps */
  bestandstyp?: Bestandstyp
  bodenanalyse: {
    n: number
    p: number
    k: number
  }
  ertragsziel: number
  empfehlung: {
    n: number
    p: number
    k: number
  }
}

export default function BedarfsrechnerPage(): JSX.Element {
  const navigate = useNavigate()
  const { push } = useToast()
  const { data: kulturenListe = [] } = useKulturen()
  const [bedarf, setBedarf] = useState<BedarfData>({
    flaeche: 0,
    kultur: '',
    bodenanalyse: { n: 0, p: 0, k: 0 },
    ertragsziel: 0,
    empfehlung: { n: 0, p: 0, k: 0 },
  })

  function updateFlaeche(value: number): void {
    setBedarf((prev) => ({ ...prev, flaeche: value }))
  }

  function updateKultur(value: string): void {
    setBedarf((prev) => ({
      ...prev,
      kultur: value,
      gruenlandNutzung: undefined,
      standortTyp: undefined,
      bestandstyp: undefined,
    }))
  }

  function updateGruenlandNutzung(value: GruenlandNutzung): void {
    setBedarf((prev) => ({ ...prev, gruenlandNutzung: value }))
  }

  function updateStandortTyp(value: StandortTyp | 'marsch' | 'geest'): void {
    setBedarf((prev) => ({ ...prev, standortTyp: value }))
  }

  function updateVorjahresOrgDungung(checked: boolean): void {
    setBedarf((prev) => ({ ...prev, vorjahresOrgDungung: checked }))
  }

  function updateBestandstyp(value: Bestandstyp): void {
    setBedarf((prev) => ({ ...prev, bestandstyp: value }))
  }

  function updateBodenanalyse(key: keyof BedarfData['bodenanalyse'], value: number): void {
    setBedarf((prev) => ({
      ...prev,
      bodenanalyse: { ...prev.bodenanalyse, [key]: value },
    }))
  }

  function updateErtragsziel(value: number): void {
    const n = value * 2.5
    const p = value * 0.8
    const k = value * 1.2
    setBedarf((prev) => ({
      ...prev,
      ertragsziel: value,
      empfehlung: { n, p, k },
    }))
  }

  const handleErgebnisSpeichern = (): void => {
    const payload = {
      ...bedarf,
      exportiertAm: new Date().toISOString(),
      quelle: 'Bedarfsrechner',
    }
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Duengebedarf_${bedarf.kultur || 'Kultur'}_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    push('Ergebnis als JSON gespeichert.')
  }

  const handleAlsDuengeplanUebernehmen = (): void => {
    navigate('/agrar/duengung/planung', { state: { fromBedarfsrechner: bedarf } })
    push('Empfehlung an Düngungsplanung übergeben.')
  }

  const isGruenland = bedarf.kultur === 'gruenland' || bedarf.kultur === 'grünland'
  const isWintergetreideRaps = ['weizen', 'gerste', 'raps'].includes(bedarf.kultur)

  const gruenlandZeile = useMemo(() => {
    if (!isGruenland || !bedarf.gruenlandNutzung || !bedarf.standortTyp || bedarf.standortTyp === 'marsch' || bedarf.standortTyp === 'geest') return null
    const tab = getGruenlandTabelle(bedarf.standortTyp as StandortTyp, bedarf.vorjahresOrgDungung ?? false)
    return tab[bedarf.gruenlandNutzung] ?? null
  }, [isGruenland, bedarf.gruenlandNutzung, bedarf.standortTyp, bedarf.vorjahresOrgDungung])

  const wintergetreideN = useMemo(() => {
    if (!isWintergetreideRaps || !bedarf.standortTyp || !bedarf.bestandstyp) return null
    const standort = bedarf.standortTyp === 'marsch' ? 'marsch' : bedarf.standortTyp === 'geest' ? 'geest' : null
    if (!standort) return null
    if (standort === 'geest') {
      if (bedarf.kultur === 'raps') return TAB2_GEEST.raps
      return bedarf.bestandstyp === 'ueppig' ? TAB2_GEEST.getreide_ueppig : TAB2_GEEST.getreide_normal
    }
    if (bedarf.kultur === 'raps') {
      return bedarf.bestandstyp === 'duenn' ? TAB1_MARSCH.weizen_raps_duenn : TAB1_MARSCH.raps_normal
    }
    const weizen =
      bedarf.bestandstyp === 'ueppig' ? TAB1_MARSCH.weizen_ueppig
      : bedarf.bestandstyp === 'duenn' ? TAB1_MARSCH.weizen_raps_duenn
      : TAB1_MARSCH.weizen_normal
    if (bedarf.kultur === 'gerste') {
      return { min: Math.max(0, weizen.min - WINTERGERSTE_OFFSET_KG), max: Math.max(0, weizen.max - WINTERGERSTE_OFFSET_KG) }
    }
    return weizen
  }, [isWintergetreideRaps, bedarf.kultur, bedarf.standortTyp, bedarf.bestandstyp])

  const steps = [
    {
      id: 'grunddaten',
      title: 'Grunddaten',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="flaeche">Fläche (ha) *</Label>
            <Input
              id="flaeche"
              type="number"
              value={bedarf.flaeche}
              onChange={(e) => updateFlaeche(Number(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <Label htmlFor="kultur">Kultur *</Label>
            <p className="text-xs text-muted-foreground mb-1">
              {kulturenListe.length > 0
                ? 'Aus Stammdaten.'
                : 'Standard-Optionen (keine Stammdaten geladen).'}
            </p>
            <select
              id="kultur"
              value={bedarf.kultur}
              onChange={(e) => updateKultur(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              {kulturenListe.length > 0
                ? kulturenListe.map(k => (
                    <option key={k.id} value={k.name.toLowerCase()}>{k.name}</option>
                  ))
                : (
                  // Fallback-Optionen, wenn useKulturen() keine Daten liefert (inkl. Grünland)
                  <>
                    <option value="weizen">Weizen</option>
                    <option value="gerste">Gerste</option>
                    <option value="raps">Raps</option>
                    <option value="mais">Mais</option>
                    <option value="gruenland">Grünland</option>
                  </>
                )}
            </select>
            {kulturenListe.length === 0 && ['weizen', 'gerste', 'raps'].includes(bedarf.kultur) && (
              <p className="text-xs text-muted-foreground mt-1">
                Wintergetreide/Raps: 1. N-Gabe siehe LWK-Hinweis Tab. 1 (Marsch) / Tab. 2 (Geest).
              </p>
            )}
            {kulturenListe.length === 0 && bedarf.kultur === 'gruenland' && (
              <p className="text-xs text-muted-foreground mt-1">
                Grünland: N-Düngebedarf und Aufteilung siehe LWK-Hinweis (z. B. Tab. 3a/3b).
              </p>
            )}

            {/* Phase 2: Grünland – Nutzungsintensität + Standort */}
            {(bedarf.kultur === 'gruenland' || bedarf.kultur === 'grünland') && (
              <>
                <div className="mt-4">
                  <Label htmlFor="gruenland-nutzung">Nutzungsintensität (Grünland)</Label>
                  <select
                    id="gruenland-nutzung"
                    value={bedarf.gruenlandNutzung ?? ''}
                    onChange={(e) => updateGruenlandNutzung(e.target.value as GruenlandNutzung)}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 mt-1"
                  >
                    <option value="">-- Wählen --</option>
                    {(Object.keys(GRUENLAND_NUTZUNG_LABELS) as GruenlandNutzung[]).map((key) => (
                      <option key={key} value={key}>{GRUENLAND_NUTZUNG_LABELS[key]}</option>
                    ))}
                  </select>
                </div>
                <div className="mt-2">
                  <Label htmlFor="standort-gruenland">Standorttyp</Label>
                  <select
                    id="standort-gruenland"
                    value={bedarf.standortTyp && bedarf.standortTyp !== 'marsch' && bedarf.standortTyp !== 'geest' ? bedarf.standortTyp : ''}
                    onChange={(e) => updateStandortTyp(e.target.value as StandortTyp)}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 mt-1"
                  >
                    <option value="">-- Wählen --</option>
                    <option value="mineral">Mineralboden (0–8 % Humus)</option>
                    <option value="hochmoor">Hochmoor</option>
                    <option value="niedermoor">Niedermoor</option>
                  </select>
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="vorjahres-org"
                    checked={bedarf.vorjahresOrgDungung ?? false}
                    onChange={(e) => updateVorjahresOrgDungung(e.target.checked)}
                    className="h-4 w-4"
                  />
                  <Label htmlFor="vorjahres-org" className="font-normal">Vorjahres-org. Düngung berücksichtigen (Tab. 3b)</Label>
                </div>
              </>
            )}

            {/* Phase 2: Wintergetreide/Raps – Standort + Bestandstyp */}
            {['weizen', 'gerste', 'raps'].includes(bedarf.kultur) && (
              <>
                <div className="mt-4">
                  <Label htmlFor="standort-getreide">Standort (1. N-Gabe)</Label>
                  <select
                    id="standort-getreide"
                    value={bedarf.standortTyp === 'marsch' || bedarf.standortTyp === 'geest' ? bedarf.standortTyp : ''}
                    onChange={(e) => updateStandortTyp(e.target.value as 'marsch' | 'geest')}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 mt-1"
                  >
                    <option value="">-- Wählen --</option>
                    <option value="marsch">Marsch (Tab. 1)</option>
                    <option value="geest">Geest (Tab. 2)</option>
                  </select>
                </div>
                <div className="mt-2">
                  <Label htmlFor="bestandstyp">Bestandstyp</Label>
                  <select
                    id="bestandstyp"
                    value={bedarf.bestandstyp ?? ''}
                    onChange={(e) => updateBestandstyp(e.target.value as Bestandstyp)}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 mt-1"
                  >
                    <option value="">-- Wählen --</option>
                    <option value="normal">Normal bis gut entwickelt</option>
                    {bedarf.kultur !== 'raps' && <option value="ueppig">Üppige Frühsaaten (Getreide)</option>}
                    <option value="duenn">Dünne Bestände / späte Saaten</option>
                  </select>
                </div>
              </>
            )}
          </div>
        </div>
      ),
    },
    {
      id: 'bodenanalyse',
      title: 'Bodenanalyse',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="n">Stickstoff (N) mg/100g</Label>
            <Input
              id="n"
              type="number"
              value={bedarf.bodenanalyse.n}
              onChange={(e) => updateBodenanalyse('n', Number(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <Label htmlFor="p">Phosphor (P) mg/100g</Label>
            <Input
              id="p"
              type="number"
              value={bedarf.bodenanalyse.p}
              onChange={(e) => updateBodenanalyse('p', Number(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <Label htmlFor="k">Kalium (K) mg/100g</Label>
            <Input
              id="k"
              type="number"
              value={bedarf.bodenanalyse.k}
              onChange={(e) => updateBodenanalyse('k', Number(e.target.value))}
              step="0.1"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'ertrag',
      title: 'Ertragsziel',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="ertragsziel">Ertragsziel (dt/ha) *</Label>
            <Input
              id="ertragsziel"
              type="number"
              value={bedarf.ertragsziel}
              onChange={(e) => updateErtragsziel(Number(e.target.value))}
              step="1"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'empfehlung',
      title: 'Empfehlung',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-status-success" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Dünge-Empfehlung</h3>

            {/* Phase 2: Grünland – N-Düngebedarf + Aufteilung Tab. 3a/3b */}
            {gruenlandZeile && (
              <div className="mb-6 space-y-3 rounded-lg border border-green-200 bg-green-50/50 p-4">
                <div className="font-semibold text-green-900">
                  Grünland (LWK {bedarf.vorjahresOrgDungung ? 'Tab. 3b' : 'Tab. 3a'})
                </div>
                <div className="flex justify-between text-sm">
                  <span>N-Düngebedarf (Jahresgabe)</span>
                  <span className="font-bold">{gruenlandZeile.nDuengebedarf} kg N/ha</span>
                </div>
                <div className="text-sm">
                  <span className="font-medium">Aufteilung N-Gaben (1.–6. Aufwuchs):</span>
                  <ul className="mt-1 flex flex-wrap gap-x-4 gap-y-1">
                    {gruenlandZeile.gaben.map((g, i) => (
                      g > 0 ? <li key={i}>{i + 1}. Aufwuchs: {g} kg N/ha</li> : null
                    ))}
                  </ul>
                </div>
                <p className="text-xs text-muted-foreground">Jahres-Obergrenze aus Düngebedarfsermittlung beachten. Grundnährstoffe siehe Tab. 5.</p>
              </div>
            )}

            {/* Phase 2: Wintergetreide/Raps – 1. N-Gabe Tab. 1/2 + Schwefel */}
            {wintergetreideN && (
              <div className="mb-6 space-y-3 rounded-lg border border-blue-200 bg-blue-50/50 p-4">
                <div className="font-semibold text-blue-900">Wintergetreide/Raps – 1. N-Gabe (LWK Tab. 1/2)</div>
                <div className="flex justify-between text-sm">
                  <span>1. Gabe (kg N/ha)</span>
                  <span className="font-bold">{wintergetreideN.min}–{wintergetreideN.max} kg N/ha</span>
                </div>
                <p className="text-xs text-muted-foreground">Die nach Düngebedarfsermittlung errechnete Jahres-N-Menge darf nicht überschritten werden.</p>
                {bedarf.kultur === 'raps' && (
                  <p className="text-xs">Schwefel: {SCHWEFEL_RAPS_KG_HA.min}–{SCHWEFEL_RAPS_KG_HA.max} kg S/ha empfohlen.</p>
                )}
                {bedarf.kultur !== 'raps' && bedarf.standortTyp === 'marsch' && (
                  <p className="text-xs">Getreide Marsch: Bei schwachen Beständen/leichten Böden {SCHWEFEL_GETREIDE_MARSCH_KG_HA.min}–{SCHWEFEL_GETREIDE_MARSCH_KG_HA.max} kg S/ha in 1. Gabe.</p>
                )}
              </div>
            )}

            <div className="space-y-3">
              <div className="flex justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">Stickstoff (N)</div>
                  <Badge variant="outline">Hauptnährstoff</Badge>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">
                    {gruenlandZeile ? `${gruenlandZeile.nDuengebedarf} (Jahresgabe)` : wintergetreideN ? `${wintergetreideN.min}–${wintergetreideN.max} (1. Gabe)` : `${bedarf.empfehlung.n.toFixed(0)}`} kg/ha
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {gruenlandZeile
                      ? `${(gruenlandZeile.nDuengebedarf * bedarf.flaeche).toFixed(0)} kg gesamt (Jahr)`
                      : wintergetreideN
                        ? `1. Gabe; Gesamt-Jahr aus Düngebedarfsermittlung`
                        : `${(bedarf.empfehlung.n * bedarf.flaeche).toFixed(0)} kg gesamt`}
                  </div>
                </div>
              </div>
              <div className="flex justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">Phosphor (P)</div>
                  <Badge variant="outline">Hauptnährstoff</Badge>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">{bedarf.empfehlung.p.toFixed(0)} kg/ha</div>
                  <div className="text-sm text-muted-foreground">{(bedarf.empfehlung.p * bedarf.flaeche).toFixed(0)} kg gesamt</div>
                </div>
              </div>
              <div className="flex justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">Kalium (K)</div>
                  <Badge variant="outline">Hauptnährstoff</Badge>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">{bedarf.empfehlung.k.toFixed(0)} kg/ha</div>
                  <div className="text-sm text-muted-foreground">{(bedarf.empfehlung.k * bedarf.flaeche).toFixed(0)} kg gesamt</div>
                </div>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 mt-6">
              <Button variant="outline" className="gap-2" onClick={() => handleErgebnisSpeichern()}>
                <FileDown className="h-4 w-4" />
                Ergebnis speichern
              </Button>
              <Button variant="outline" className="gap-2" onClick={() => handleAlsDuengeplanUebernehmen()}>
                <ClipboardList className="h-4 w-4" />
                Als Düngeplan übernehmen
              </Button>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
        <NextActionPanel
          title="Naechster Schritt"
          action="Flaeche, Kultur und Bodenwerte erfassen. Danach Empfehlung speichern oder direkt in die Duengungsplanung uebernehmen."
          tone={bedarf.kultur && bedarf.flaeche > 0 ? 'blue' : 'amber'}
        />
        <OperationalTaskPlan
          title="Bedarf sauber ermitteln"
          items={[
            { label: 'Grunddaten erfassen', done: bedarf.flaeche > 0 && Boolean(bedarf.kultur), hint: 'Flaeche und Kultur sind Grundlage fuer die Empfehlung.' },
            { label: 'Bodenwerte pruefen', done: bedarf.bodenanalyse.n > 0 || bedarf.bodenanalyse.p > 0 || bedarf.bodenanalyse.k > 0, hint: 'N, P und K koennen aus aktueller Analyse uebernommen werden.' },
            { label: 'Ergebnis weitergeben', done: bedarf.empfehlung.n > 0 || Boolean(gruenlandZeile) || Boolean(wintergetreideN), hint: 'Empfehlung speichern oder als Duengeplan uebernehmen.' },
          ]}
        />
      </div>
      <Wizard
        title="Düngebedarf berechnen"
        steps={steps}
        onFinish={() => navigate('/agrar/duenger/liste')}
        onCancel={() => navigate('/agrar/duenger/liste')}
      />
    </div>
  )
}
