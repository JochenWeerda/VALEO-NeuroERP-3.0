import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { AlertTriangle, Brain, CheckCircle, Leaf, Search, Sparkles, Target, Zap } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

type Schadbild = {
  id: string
  name: string
  beschreibung: string
  schwere: 'leicht' | 'mittel' | 'schwer'
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
  effektivitaet: number // 0-100
  umweltscore: number // 0-100
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

  const [schritt, setSchritt] = useState(1)
  const [kultur, setKultur] = useState('')
  const [saison, setSaison] = useState('')
  const [schadbildBeschreibung, setSchadbildBeschreibung] = useState('')
  const [schweregrad, setSchweregrad] = useState<'leicht' | 'mittel' | 'schwer'>('mittel')
  const [ausgewaehltesSchadbild, setAusgewaehltesSchadbild] = useState<Schadbild | null>(null)
  const [beratungsErgebnis, setBeratungsErgebnis] = useState<BeratungsErgebnis | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Mock data
  const verfuegbareKulturen = [
    'Weizen', 'Gerste', 'Raps', 'Mais', 'Kartoffeln', 'Zuckerrüben'
  ]

  const schadbilder: Schadbild[] = [
    {
      id: '1',
      name: 'Gelbrost am Weizen',
      beschreibung: 'Gelbe bis orange Streifen auf Blättern, später schwarze Sporenlager',
      schwere: 'mittel',
      kultur: 'Weizen',
      saison: 'Frühjahr'
    },
    {
      id: '2',
      name: 'Mehltau an Gerste',
      beschreibung: 'Weißer, mehlartiger Belag auf Blättern und Ähren',
      schwere: 'schwer',
      kultur: 'Gerste',
      saison: 'Frühjahr'
    },
    {
      id: '3',
      name: 'Rapserdfloh',
      beschreibung: 'Kleine schwarze Käfer fressen Schadlochmuster in Blätter',
      schwere: 'leicht',
      kultur: 'Raps',
      saison: 'Herbst'
    }
  ]

  const generateEmpfehlungen = (schadbild: Schadbild): PSMEmpfehlung[] => {
    // Mock AI-basierte Empfehlungen
    const basisEmpfehlungen: PSMEmpfehlung[] = [
      {
        id: 'PSM-001',
        name: 'Amistar Opti',
        wirkstoff: 'Azoxystrobin + Difenoconazol',
        wirkstoffGruppe: 'Strobilurine + Triazole',
        dosierung: '1.0 l/ha',
        wartezeit: 35,
        effektivitaet: 92,
        umweltscore: 75,
        kosten: 145.00,
        verfuegbar: true,
        begruendung: 'Hoch effektive Kombination gegen Rostpilze mit systemischer Wirkung'
      },
      {
        id: 'PSM-002',
        name: 'Folicur Solo',
        wirkstoff: 'Tebuconazol',
        wirkstoffGruppe: 'Triazole',
        dosierung: '1.5 l/ha',
        wartezeit: 28,
        effektivitaet: 88,
        umweltscore: 82,
        kosten: 98.00,
        verfuegbar: true,
        begruendung: 'Kostengünstige Alternative mit guter Umweltverträglichkeit'
      },
      {
        id: 'PSM-003',
        name: 'Nativo',
        wirkstoff: 'Trifloxystrobin + Tebuconazol',
        wirkstoffGruppe: 'Strobilurine + Triazole',
        dosierung: '0.8 l/ha',
        wartezeit: 35,
        effektivitaet: 95,
        umweltscore: 78,
        kosten: 165.00,
        verfuegbar: false,
        begruendung: 'Höchste Effektivität, aber aktuell nicht verfügbar'
      }
    ]

    // Filter basierend auf Schadbild und Kultur
    return basisEmpfehlungen.filter(psm => {
      if (schadbild.name.includes('Rost') && psm.wirkstoffGruppe.includes('Strobilurine')) return true
      if (schadbild.name.includes('Mehltau') && psm.wirkstoffGruppe.includes('Triazole')) return true
      if (schadbild.name.includes('Rapserdfloh')) return psm.wirkstoff.includes('Azoxystrobin')
      return true
    })
  }

  const analysiereSchadbild = async () => {
    if (!kultur || !schadbildBeschreibung) return

    setIsLoading(true)

    try {
      // Mock AI-Analyse
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Finde passendes Schadbild oder erstelle neues
      const gefundenesSchadbild = schadbilder.find(s =>
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
      setIsLoading(false)
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
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <Label>Kultur</Label>
            <Select value={kultur} onValueChange={setKultur}>
              <SelectTrigger>
                <SelectValue placeholder="Kultur auswählen" />
              </SelectTrigger>
              <SelectContent>
                {verfuegbareKulturen.map(k => (
                  <SelectItem key={k} value={k}>{k}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Saison</Label>
            <Select value={saison} onValueChange={setSaison}>
              <SelectTrigger>
                <SelectValue placeholder="Saison auswählen" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Frühjahr">Frühjahr</SelectItem>
                <SelectItem value="Sommer">Sommer</SelectItem>
                <SelectItem value="Herbst">Herbst</SelectItem>
                <SelectItem value="Winter">Winter</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div>
          <Label>Schweregrad</Label>
          <Select value={schweregrad} onValueChange={(value: any) => setSchweregrad(value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="leicht">Leicht (unter 10% Befall)</SelectItem>
              <SelectItem value="mittel">Mittel (10-30% Befall)</SelectItem>
              <SelectItem value="schwer">Schwer (über 30% Befall)</SelectItem>
            </SelectContent>
          </Select>
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
            disabled={!kultur || !schadbildBeschreibung || isLoading}
            className="gap-2"
          >
            <Brain className="h-4 w-4" />
            {isLoading ? 'Analysiere...' : 'Schadbild analysieren'}
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
                  ausgewaehltesSchadbild.schwere === 'leicht' ? 'secondary' :
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
                    <div className="text-lg">€{psm.kosten}/ha</div>
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

  return (
    <div className="space-y-6 p-6">
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