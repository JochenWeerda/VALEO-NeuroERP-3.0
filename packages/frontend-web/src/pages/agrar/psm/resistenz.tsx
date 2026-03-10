import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, BarChart3, RotateCcw, TrendingUp, Zap } from 'lucide-react'
import { useWirkstoffGruppen } from '@/lib/api/agrar'

type KulturHistorie = {
  kultur: string
  saison: string
  wirkstoffGruppen: string[]
  resistenzEntwicklung: number
}

type ResistenzStrategie = {
  kultur: string
  aktuelleRisiken: { id: string; name: string; wirkstoffe: string[]; resistenzRisiko: string; letzteAnwendung: string; rotationsEmpfehlung: string }[]
  empfohleneRotation: string[]
  alternativeWirkstoffe: string[]
  monitoringEmpfehlungen: string[]
}

export default function PSMResistenzManagementPage(): JSX.Element {
  const navigate = useNavigate()

  const { data: wirkstoffGruppen, isLoading } = useWirkstoffGruppen()

  const [selectedKultur, setSelectedKultur] = useState('weizen')
  const [selectedSaison, setSelectedSaison] = useState('2024/2025')

  const gruppen = wirkstoffGruppen ?? []

  const kulturHistorie: KulturHistorie[] = [
    {
      kultur: 'weizen',
      saison: '2023/2024',
      wirkstoffGruppen: ['Azole', 'Strobilurine'],
      resistenzEntwicklung: 75
    },
    {
      kultur: 'weizen',
      saison: '2022/2023',
      wirkstoffGruppen: ['Azole', 'Triazole'],
      resistenzEntwicklung: 60
    },
    {
      kultur: 'raps',
      saison: '2023/2024',
      wirkstoffGruppen: ['Pyrethroide', 'Neonicotinoide'],
      resistenzEntwicklung: 45
    }
  ]

  const getResistenzStrategie = (kultur: string): ResistenzStrategie => {
    const aktuelleRisiken = gruppen.filter(g => g.resistenzRisiko === 'hoch' || g.resistenzRisiko === 'mittel')

    return {
      kultur,
      aktuelleRisiken,
      empfohleneRotation: [
        'Wechsel zu alternativen Wirkstoffgruppen',
        'Integrierte Bekämpfungsstrategien',
        'Fruchtwechsel einplanen',
        'Monitoring der Resistenzentwicklung'
      ],
      alternativeWirkstoffe: ['Neue Wirkstoffgruppen', 'Biologische Mittel', 'Mechanische Verfahren'],
      monitoringEmpfehlungen: [
        'Regelmäßige Probenahme',
        'Laboruntersuchungen',
        'Wirksamkeitskontrolle',
        'Dokumentation der Anwendungen'
      ]
    }
  }

  const strategie = getResistenzStrategie(selectedKultur)
  const kulturHistorieFiltered = kulturHistorie.filter(h => h.kultur === selectedKultur)

  const getRisikoColor = (risiko: string) => {
    switch (risiko) {
      case 'hoch': return 'text-red-600 bg-red-50'
      case 'mittel': return 'text-orange-600 bg-orange-50'
      case 'niedrig': return 'text-green-600 bg-green-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getRisikoProgress = (risiko: string) => {
    switch (risiko) {
      case 'hoch': return 85
      case 'mittel': return 60
      case 'niedrig': return 25
      default: return 0
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-1/2" />
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">PSM-Resistenz-Management</h1>
          <p className="text-muted-foreground">Wirkstoff-Rotation und Resistenz-Monitoring</p>
        </div>
        <Button variant="outline" onClick={() => navigate('/agrar/psm/liste')}>
          Zurück zur Liste
        </Button>
      </div>

      {/* Filter */}
      <Card>
        <CardHeader>
          <CardTitle>Auswahl</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="text-sm font-medium">Kultur</label>
              <NativeSelect
                value={selectedKultur}
                onValueChange={setSelectedKultur}
                options={[
                  { value: 'weizen', label: 'Weizen' },
                  { value: 'gerste', label: 'Gerste' },
                  { value: 'raps', label: 'Raps' },
                  { value: 'mais', label: 'Mais' },
                ]}
              />
            </div>
            <div>
              <label className="text-sm font-medium">Saison</label>
              <NativeSelect
                value={selectedSaison}
                onValueChange={setSelectedSaison}
                options={[
                  { value: '2024/2025', label: '2024/2025' },
                  { value: '2023/2024', label: '2023/2024' },
                  { value: '2022/2023', label: '2022/2023' },
                ]}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Aktuelle Resistenz-Risiken */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Aktuelle Resistenz-Risiken
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {gruppen.map((gruppe) => (
              <div key={gruppe.id} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h4 className="font-medium">{gruppe.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      {gruppe.wirkstoffe.join(', ')}
                    </p>
                  </div>
                  <Badge className={getRisikoColor(gruppe.resistenzRisiko)}>
                    {gruppe.resistenzRisiko}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Resistenz-Risiko</span>
                    <span>{getRisikoProgress(gruppe.resistenzRisiko)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-red-600 h-2 rounded-full"
                      style={{ width: `${getRisikoProgress(gruppe.resistenzRisiko)}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Letzte Anwendung: {new Date(gruppe.letzteAnwendung).toLocaleDateString('de-DE')}
                  </div>
                  <div className="text-xs text-blue-600">
                    {gruppe.rotationsEmpfehlung}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Kultur-Historie */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Kultur-Historie
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {kulturHistorieFiltered.map((historie, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h4 className="font-medium">{historie.kultur} - {historie.saison}</h4>
                    <p className="text-sm text-muted-foreground">
                      Wirkstoffgruppen: {historie.wirkstoffGruppen.join(', ')}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">Resistenz: {historie.resistenzEntwicklung}%</div>
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-orange-600 h-2 rounded-full"
                        style={{ width: `${historie.resistenzEntwicklung}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Strategie-Empfehlungen */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Strategie-Empfehlungen
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Empfohlene Rotation */}
          <div>
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <RotateCcw className="h-4 w-4" />
              Empfohlene Rotation
            </h4>
            <div className="space-y-2">
              {strategie.empfohleneRotation.map((empfehlung, index) => (
                <div key={index} className="flex items-center gap-2 p-2 bg-blue-50 rounded">
                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                  <span className="text-sm">{empfehlung}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Alternative Wirkstoffe */}
          <div>
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Alternative Wirkstoffe
            </h4>
            <div className="grid gap-2 md:grid-cols-2">
              {strategie.alternativeWirkstoffe.map((wirkstoff, index) => (
                <Badge key={index} variant="outline" className="justify-center">
                  {wirkstoff}
                </Badge>
              ))}
            </div>
          </div>

          {/* Monitoring-Empfehlungen */}
          <div>
            <h4 className="font-medium mb-3">Monitoring-Empfehlungen</h4>
            <div className="space-y-2">
              {strategie.monitoringEmpfehlungen.map((empfehlung, index) => (
                <div key={index} className="flex items-center gap-2 p-2 bg-green-50 rounded">
                  <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                  <span className="text-sm">{empfehlung}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Handlungsempfehlungen */}
      <Card className="border-orange-500 bg-orange-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-orange-900">
            <AlertTriangle className="h-5 w-5" />
            Handlungsempfehlungen
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-orange-800">
            <p>
              <strong>Dringend:</strong> Bei Azolen besteht hohes Resistenzrisiko.
              Planen Sie eine 3-jährige Pause für diese Wirkstoffgruppe.
            </p>
            <p>
              <strong>Empfehlung:</strong> Integrieren Sie alternative Bekämpfungsstrategien
              wie biologische Mittel und mechanische Verfahren.
            </p>
            <p>
              <strong>Monitoring:</strong> Führen Sie regelmäßige Wirksamkeitstests durch
              und dokumentieren Sie alle Anwendungen.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
