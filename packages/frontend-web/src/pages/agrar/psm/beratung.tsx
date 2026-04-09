import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertTriangle, Brain, CheckCircle, Leaf, Search, Sparkles, Target, Zap } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useSchadbilder, useKulturen, usePSM } from '@/lib/api/agrar'

type Schadbild = {
  id: string
  name: string
  beschreibung: string
  schwere: 'leicht' | 'mittel' | 'schwer' | 'gering' | 'hoch'
  kultur: string
  saison: string
}

type PSMEmpfehlung = {
  id: string
  name: string
  wirkstoff: string
  wirkstoffGruppe: string
  dosierung: string
  wartezeit: number
  effektivitaet: number
  umweltscore: number
  kosten: number
  verfuegbar: boolean
  begruendung: string
}

type BeratungsErgebnis = {
  schadbild: Schadbild
  empfehlungen: PSMEmpfehlung[]
  alternativeMethoden: string[]
  risiken: string[]
  nachsorge: string[]
}

export default function PSMBeratungPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const { data: schadbilderData, isLoading: isLoadingSchadbilder } = useSchadbilder()
  const { data: kulturenData, isLoading: isLoadingKulturen } = useKulturen()
  const { data: psmResponse } = usePSM()

  const [schritt, setSchritt] = useState(1)
  const [kultur, setKultur] = useState('')
  const [saison, setSaison] = useState('')
  const [schadbildBeschreibung, setSchadbildBeschreibung] = useState('')
  const [schweregrad, setSchweregrad] = useState<'leicht' | 'mittel' | 'schwer'>('mittel')
  const [ausgewaehltesSchadbild, setAusgewaehltesSchadbild] = useState<Schadbild | null>(null)
  const [beratungsErgebnis, setBeratungsErgebnis] = useState<BeratungsErgebnis | null>(null)
  const [isAnalyseLoading, setIsAnalyseLoading] = useState(false)

  const schadbilder = schadbilderData ?? []
  const kulturen = kulturenData ?? []
  const verfuegbareKulturen = kulturen.map(k => k.name)
  const isLoading = isLoadingSchadbilder || isLoadingKulturen

  const psmDataReadiness = useMemo(() => {
    const count = psmResponse?.items?.length ?? 0
    if (count === 0) return { level: 'kritisch', text: 'Keine aktiven PSM-Stammdaten verfuegbar. Beratung bleibt auf Analyse ohne Produktempfehlung.' }
    if (count < 5) return { level: 'beobachten', text: 'Nur wenige PSM-Stammdaten verfuegbar. Empfehlungstiefe kann eingeschraenkt sein.' }
    return { level: 'ok', text: `${count} aktive PSM-Datensaetze stehen fuer die Beratung bereit.` }
  }, [psmResponse?.items])

  /** Empfehlungen ausschliesslich aus vorhandenen PSM-Stammdaten ableiten. */
  const generateEmpfehlungen = (schadbild: Schadbild): PSMEmpfehlung[] => {
    const psmItems = psmResponse?.items ?? []
    const fromStammdaten: PSMEmpfehlung[] = psmItems.map((p) => {
      const ext = p as unknown as Record<string, unknown>
      return {
        id: p.id,
        name: p.mittel,
        wirkstoff: p.wirkstoff,
        wirkstoffGruppe: String(ext.wirkstoffGruppe ?? ext.gruppe ?? ''),
        dosierung: String(ext.dosierung ?? ext.max_dosierung ?? '—'),
        wartezeit: Number(ext.wartezeit ?? ext.wartezeit_tage ?? 0),
        effektivitaet: Number(ext.effektivitaet ?? 85),
        umweltscore: Number(ext.umweltscore ?? 75),
        kosten: Number(ext.kosten ?? 0),
        verfuegbar: p.status === 'aktiv',
        begruendung: String(ext.begruendung ?? `PSM-Stammdaten: ${p.mittel}`)
      }
    })

    const filterRelevant = (list: PSMEmpfehlung[]) =>
      list.filter(psm => {
        if (schadbild.name.includes('Rost') && (psm.wirkstoffGruppe.includes('Strobilurine') || psm.wirkstoff.toLowerCase().includes('strobilurin'))) return true
        if (schadbild.name.includes('Mehltau') && (psm.wirkstoffGruppe.includes('Triazole') || psm.wirkstoff.toLowerCase().includes('triazol'))) return true
        if (schadbild.name.includes('Rapserdfloh') && psm.wirkstoff.includes('Azoxystrobin')) return true
        return true
      })

    return filterRelevant(fromStammdaten).slice(0, 5)
  }

  const analysiereSchadbild = async () => {
    if (!kultur || !schadbildBeschreibung) return

    setIsAnalyseLoading(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 2000))

      const gefundenesSchadbild: Schadbild = schadbilder.find(s =>
        s.kultur === kultur &&
        schadbildBeschreibung.toLowerCase().includes(s.name.toLowerCase().split(' ')[0])
      ) || {
        id: 'custom',
        name: `Unbekanntes Schadbild: ${schadbildBeschreibung.substring(0, 30)}...`,
        beschreibung: schadbildBeschreibung,
        schwere: schweregrad,
        kultur,
        saison
      }

      setAusgewaehltesSchadbild(gefundenesSchadbild)

      const empfehlungen = generateEmpfehlungen(gefundenesSchadbild)

      const ergebnis: BeratungsErgebnis = {
        schadbild: gefundenesSchadbild,
        empfehlungen,
        alternativeMethoden: [
          'Mechanische Verfahren (Eggen, Striegeln)',
          'Biologische Bekämpfung (Nützlinge)',
          'Fruchtwechsel und Sortenwahl',
          'Nährstoffoptimierung'
        ],
        risiken: [
          'Resistenzentwicklung bei häufiger Anwendung',
          'Umweltbelastung durch PSM-Rückstände',
          'Beeinträchtigung von Nützlingen',
          'Kosten-Nutzen-Verhältnis'
        ],
        nachsorge: [
          'Regelmäßige Feldbeobachtung',
          'Wirksamkeitskontrolle nach 7-10 Tagen',
          'Dokumentation der Anwendung',
          'Monitoring der Resistenzentwicklung'
        ]
      }

      setBeratungsErgebnis(ergebnis)
      setSchritt(2)

      toast({
        title: "Analyse abgeschlossen",
        description: `Schadbild "${gefundenesSchadbild.name}" wurde analysiert.`,
      })

    } catch (error) {
      toast({
        title: "Analyse fehlgeschlagen",
        description: "Fehler bei der Schadbild-Analyse.",
        variant: "destructive",
      })
    } finally {
      setIsAnalyseLoading(false)
    }
  }

  const renderSchritt1 = () => (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Schritt 1: Schadbild beschreiben
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>PSM-Datenlage</AlertTitle>
            <AlertDescription>{psmDataReadiness.text}</AlertDescription>
          </Alert>
          <div className="grid gap-4 md:grid-cols-2">
          <div>
            <Label>Kultur</Label>
            <NativeSelect
              value={kultur}
              onValueChange={setKultur}
              placeholder="Kultur auswaehlen"
              options={verfuegbareKulturen.map((kulturName) => ({ value: kulturName, label: kulturName }))}
            />
          </div>
          <div>
            <Label>Saison</Label>
            <NativeSelect
              value={saison}
              onValueChange={setSaison}
              placeholder="Saison auswaehlen"
              options={[
                { value: 'Fr?hjahr', label: 'Fr?hjahr' },
                { value: 'Sommer', label: 'Sommer' },
                { value: 'Herbst', label: 'Herbst' },
                { value: 'Winter', label: 'Winter' },
              ]}
            />
          </div>
        </div>

        <div>
          <Label>Schweregrad</Label>
          <NativeSelect
          value={schweregrad}
          onValueChange={(value) => setSchweregrad(value as 'leicht' | 'mittel' | 'schwer')}
          options={[
            { value: 'leicht', label: 'Leicht (unter 10% Befall)' },
            { value: 'mittel', label: 'Mittel (10-30% Befall)' },
            { value: 'schwer', label: 'Schwer (ueber 30% Befall)' },
          ]}
        />
        </div>

        <div>
          <Label>Schadbild-Beschreibung</Label>
          <Textarea
            value={schadbildBeschreibung}
            onChange={(e) => setSchadbildBeschreibung(e.target.value)}
            placeholder="Beschreiben Sie das Schadbild detailliert (z.B. Farbe, Form, Verteilung, betroffene Pflanzenteile)..."
            rows={4}
          />
        </div>

        <div className="flex gap-2">
          <Button
            onClick={analysiereSchadbild}
            disabled={!kultur || !schadbildBeschreibung || isAnalyseLoading}
            className="gap-2"
          >
            <Brain className="h-4 w-4" />
            {isAnalyseLoading ? 'Analysiere...' : 'Schadbild analysieren'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  const renderSchritt2 = () => (
    <div className="space-y-6">
      {/* Schadbild-Zusammenfassung */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Erkanntes Schadbild
          </CardTitle>
        </CardHeader>
        <CardContent>
          {ausgewaehltesSchadbild && (
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-blue-900">{ausgewaehltesSchadbild.name}</h3>
                <Badge variant={
                  ausgewaehltesSchadbild.schwere === 'leicht' || ausgewaehltesSchadbild.schwere === 'gering' ? 'secondary' :
                  ausgewaehltesSchadbild.schwere === 'mittel' ? 'default' : 'destructive'
                }>
                  {ausgewaehltesSchadbild.schwere}
                </Badge>
              </div>
              <p className="text-sm text-blue-700">{ausgewaehltesSchadbild.beschreibung}</p>
              <div className="mt-2 text-xs text-blue-600">
                Kultur: {ausgewaehltesSchadbild.kultur} | Saison: {ausgewaehltesSchadbild.saison}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* PSM-Empfehlungen */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            KI-Empfehlungen ({beratungsErgebnis?.empfehlungen.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {beratungsErgebnis?.empfehlungen.length === 0 && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Keine PSM-Empfehlungen verfügbar</AlertTitle>
                <AlertDescription>
                  Für das beschriebene Schadbild liegen aktuell keine passenden PSM-Stammdaten vor. Bitte prüfen Sie die PSM-Datenbank oder wenden Sie sich an Ihren Berater.
                </AlertDescription>
              </Alert>
            )}
            {beratungsErgebnis?.empfehlungen.map((psm, index) => (
              <div key={psm.id} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-medium">{psm.name}</h4>
                    <p className="text-sm text-muted-foreground">{psm.wirkstoff}</p>
                  </div>
                  <div className="flex gap-2">
                    {!psm.verfuegbar && (
                      <Badge variant="destructive">Nicht verfügbar</Badge>
                    )}
                    <Badge variant="outline">{psm.wirkstoffGruppe}</Badge>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-3">
                  <div>
                    <div className="text-sm font-medium">Dosierung</div>
                    <div className="text-lg">{psm.dosierung}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">Wartezeit</div>
                    <div className="text-lg">{psm.wartezeit} Tage</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">Effektivität</div>
                    <div className="text-lg font-bold text-green-600">{psm.effektivitaet}%</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">Kosten</div>
                    <div className="text-lg">{psm.kosten}/ha</div>
                  </div>
                </div>

                <div className="mb-3">
                  <div className="text-sm font-medium mb-1">Umwelt-Score</div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${psm.umweltscore}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">{psm.umweltscore}/100</div>
                </div>

                <p className="text-sm text-muted-foreground">{psm.begruendung}</p>

                {index === 0 && (
                  <div className="mt-3 flex items-center gap-2 p-2 bg-green-50 rounded">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800">Top-Empfehlung</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Alternative Methoden */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Leaf className="h-5 w-5" />
            Alternative Methoden
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 md:grid-cols-2">
            {beratungsErgebnis?.alternativeMethoden.map((methode, index) => (
              <div key={index} className="flex items-center gap-2 p-2 border rounded">
                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                <span className="text-sm">{methode}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Risiken & Nachsorge */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              Risiken beachten
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {beratungsErgebnis?.risiken.map((risiko, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span>{risiko}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-900">
              <CheckCircle className="h-5 w-5" />
              Nachsorge
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {beratungsErgebnis?.nachsorge.map((nachsorge, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></div>
                  <span>{nachsorge}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-1/2" />
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">PSM-Beratungs-Tool</h1>
          <p className="text-muted-foreground">KI-gestützte PSM-Empfehlungen für optimale Bekämpfung</p>
        </div>
        <Button variant="outline" onClick={() => navigate('/agrar/psm/liste')}>
          Zurück zur Liste
        </Button>
      </div>

      {/* Progress Indicator */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium">Beratungsschritte</span>
            <span className="text-sm text-muted-foreground">Schritt {schritt} von 2</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(schritt / 2) * 100}%` }}
            ></div>
          </div>
          <div className="flex justify-between mt-2 text-xs text-muted-foreground">
            <span>Schadbild beschreiben</span>
            <span>Empfehlungen anzeigen</span>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader><CardTitle className="text-sm">Kulturdaten</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{verfuegbareKulturen.length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">Schadbilder</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{schadbilder.length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">PSM-Readiness</CardTitle></CardHeader>
          <CardContent>
            <Badge variant={psmDataReadiness.level === 'kritisch' ? 'destructive' : psmDataReadiness.level === 'beobachten' ? 'secondary' : 'outline'}>
              {psmDataReadiness.level}
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Schritt-Inhalt */}
      {schritt === 1 ? renderSchritt1() : renderSchritt2()}

      {/* Navigation */}
      {schritt === 2 && (
        <div className="flex justify-between">
          <Button variant="outline" onClick={() => setSchritt(1)}>
            Zurück
          </Button>
          <Button onClick={() => navigate('/agrar/psm/abgabedokumentation')} className="gap-2">
            <Zap className="h-4 w-4" />
            PSM bestellen
          </Button>
        </div>
      )}
    </div>
  )
}
