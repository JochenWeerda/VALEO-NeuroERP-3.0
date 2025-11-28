/**
 * Kundenportal - Nährstoffbilanzen
 * 
 * Jahresübersichten der Nährstoffbilanzen zum Download als PDF
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Download,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Minus,
  Leaf,
  Droplets,
  Calendar,
  Info,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Eye,
} from 'lucide-react'

interface NaehrstoffBilanz {
  jahr: number
  stickstoff: { zugang: number; abgang: number; saldo: number }
  phosphor: { zugang: number; abgang: number; saldo: number }
  kalium: { zugang: number; abgang: number; saldo: number }
  flaeche: number
  status: 'abgeschlossen' | 'vorläufig'
  dokument: string
}

interface SchlagBilanz {
  schlag: string
  kultur: string
  flaeche: number
  nZugang: number
  nAbgang: number
  nSaldo: number
  pZugang: number
  pAbgang: number
  pSaldo: number
}

const mockBilanzen: NaehrstoffBilanz[] = [
  {
    jahr: 2024,
    stickstoff: { zugang: 185, abgang: 170, saldo: 15 },
    phosphor: { zugang: 42, abgang: 38, saldo: 4 },
    kalium: { zugang: 65, abgang: 72, saldo: -7 },
    flaeche: 32.8,
    status: 'vorläufig',
    dokument: 'naehrstoffbilanz-2024.pdf',
  },
  {
    jahr: 2023,
    stickstoff: { zugang: 178, abgang: 165, saldo: 13 },
    phosphor: { zugang: 40, abgang: 35, saldo: 5 },
    kalium: { zugang: 60, abgang: 58, saldo: 2 },
    flaeche: 32.8,
    status: 'abgeschlossen',
    dokument: 'naehrstoffbilanz-2023.pdf',
  },
  {
    jahr: 2022,
    stickstoff: { zugang: 172, abgang: 158, saldo: 14 },
    phosphor: { zugang: 38, abgang: 32, saldo: 6 },
    kalium: { zugang: 55, abgang: 52, saldo: 3 },
    flaeche: 30.5,
    status: 'abgeschlossen',
    dokument: 'naehrstoffbilanz-2022.pdf',
  },
]

const mockSchlagBilanzen: SchlagBilanz[] = [
  { schlag: 'Großer Acker', kultur: 'Winterweizen', flaeche: 12.5, nZugang: 220, nAbgang: 200, nSaldo: 20, pZugang: 45, pAbgang: 40, pSaldo: 5 },
  { schlag: 'Hinteres Feld', kultur: 'Wintergerste', flaeche: 8.3, nZugang: 180, nAbgang: 175, nSaldo: 5, pZugang: 40, pAbgang: 38, pSaldo: 2 },
  { schlag: 'Waldstück', kultur: 'Mais', flaeche: 5.2, nZugang: 160, nAbgang: 150, nSaldo: 10, pZugang: 42, pAbgang: 35, pSaldo: 7 },
  { schlag: 'Wiese am Bach', kultur: 'Grünland', flaeche: 6.8, nZugang: 120, nAbgang: 125, nSaldo: -5, pZugang: 35, pAbgang: 38, pSaldo: -3 },
]

// Gesetzliche Grenzwerte (kg N/ha im 3-Jahres-Durchschnitt)
const N_GRENZWERT = 50
const P_GRENZWERT = 10

export default function PortalNaehrstoffbilanzen() {
  const [loading, setLoading] = useState(true)
  const [bilanzen, setBilanzen] = useState<NaehrstoffBilanz[]>([])
  const [schlagBilanzen, setSchlagBilanzen] = useState<SchlagBilanz[]>([])
  const [selectedJahr, setSelectedJahr] = useState<string>('2024')

  useEffect(() => {
    const timer = setTimeout(() => {
      setBilanzen(mockBilanzen)
      setSchlagBilanzen(mockSchlagBilanzen)
      setLoading(false)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  const currentBilanz = bilanzen.find(b => b.jahr.toString() === selectedJahr)

  // 3-Jahres-Durchschnitt berechnen
  const dreiJahresDurchschnittN = bilanzen.slice(0, 3).reduce((sum, b) => sum + b.stickstoff.saldo, 0) / Math.min(bilanzen.length, 3)
  const dreiJahresDurchschnittP = bilanzen.slice(0, 3).reduce((sum, b) => sum + b.phosphor.saldo, 0) / Math.min(bilanzen.length, 3)

  const getSaldoColor = (saldo: number, grenzwert: number) => {
    if (saldo < 0) return 'text-blue-600'
    if (saldo > grenzwert * 0.8) return 'text-amber-600'
    if (saldo > grenzwert) return 'text-red-600'
    return 'text-emerald-600'
  }

  const getSaldoIcon = (saldo: number) => {
    if (saldo > 0) return <TrendingUp className="h-4 w-4" />
    if (saldo < 0) return <TrendingDown className="h-4 w-4" />
    return <Minus className="h-4 w-4" />
  }

  if (loading) {
    return <NaehrstoffbilanzenSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Nährstoffbilanzen</h1>
          <p className="text-muted-foreground">Jahresübersichten gemäß Düngeverordnung</p>
        </div>
        <Select value={selectedJahr} onValueChange={setSelectedJahr}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Jahr wählen" />
          </SelectTrigger>
          <SelectContent>
            {bilanzen.map((b) => (
              <SelectItem key={b.jahr} value={b.jahr.toString()}>
                {b.jahr}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Compliance Alert */}
      {dreiJahresDurchschnittN > N_GRENZWERT || dreiJahresDurchschnittP > P_GRENZWERT ? (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Grenzwertüberschreitung</AlertTitle>
          <AlertDescription>
            Der 3-Jahres-Durchschnitt überschreitet die gesetzlichen Grenzwerte. 
            Bitte beachten Sie die Düngeverordnung.
          </AlertDescription>
        </Alert>
      ) : (
        <Alert className="border-emerald-200 bg-emerald-50">
          <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          <AlertTitle className="text-emerald-800">Grenzwerte eingehalten</AlertTitle>
          <AlertDescription className="text-emerald-700">
            Der 3-Jahres-Durchschnitt liegt innerhalb der gesetzlichen Grenzwerte.
          </AlertDescription>
        </Alert>
      )}

      {/* KPI Cards */}
      {currentBilanz && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-blue-100 p-2 text-blue-600">
                    <Droplets className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">N-Saldo {selectedJahr}</p>
                    <p className={`text-2xl font-bold ${getSaldoColor(currentBilanz.stickstoff.saldo, N_GRENZWERT)}`}>
                      {currentBilanz.stickstoff.saldo > 0 ? '+' : ''}{currentBilanz.stickstoff.saldo} kg/ha
                    </p>
                  </div>
                </div>
                {getSaldoIcon(currentBilanz.stickstoff.saldo)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-amber-100 p-2 text-amber-600">
                    <Leaf className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">P-Saldo {selectedJahr}</p>
                    <p className={`text-2xl font-bold ${getSaldoColor(currentBilanz.phosphor.saldo, P_GRENZWERT)}`}>
                      {currentBilanz.phosphor.saldo > 0 ? '+' : ''}{currentBilanz.phosphor.saldo} kg/ha
                    </p>
                  </div>
                </div>
                {getSaldoIcon(currentBilanz.phosphor.saldo)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-purple-100 p-2 text-purple-600">
                  <BarChart3 className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">3-J. Ø Stickstoff</p>
                  <p className={`text-2xl font-bold ${getSaldoColor(dreiJahresDurchschnittN, N_GRENZWERT)}`}>
                    {dreiJahresDurchschnittN > 0 ? '+' : ''}{dreiJahresDurchschnittN.toFixed(1)} kg/ha
                  </p>
                </div>
              </div>
              <Progress 
                value={Math.min((dreiJahresDurchschnittN / N_GRENZWERT) * 100, 100)} 
                className="mt-2 h-2"
              />
              <p className="text-xs text-muted-foreground mt-1">Grenzwert: {N_GRENZWERT} kg/ha</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
                  <Calendar className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Fläche {selectedJahr}</p>
                  <p className="text-2xl font-bold">{currentBilanz.flaeche} ha</p>
                </div>
              </div>
              <Badge 
                className={`mt-2 ${currentBilanz.status === 'abgeschlossen' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}
              >
                {currentBilanz.status === 'abgeschlossen' ? 'Abgeschlossen' : 'Vorläufig'}
              </Badge>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Detaillierte Bilanz */}
      {currentBilanz && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Nährstoffbilanz {selectedJahr}</CardTitle>
              <CardDescription>Detaillierte Übersicht in kg/ha</CardDescription>
            </div>
            <Button className="gap-2">
              <Download className="h-4 w-4" />
              PDF herunterladen
            </Button>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nährstoff</TableHead>
                  <TableHead className="text-right">Zugang</TableHead>
                  <TableHead className="text-right">Abgang</TableHead>
                  <TableHead className="text-right">Saldo</TableHead>
                  <TableHead className="text-right">Grenzwert</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Stickstoff (N)</TableCell>
                  <TableCell className="text-right">{currentBilanz.stickstoff.zugang} kg/ha</TableCell>
                  <TableCell className="text-right">{currentBilanz.stickstoff.abgang} kg/ha</TableCell>
                  <TableCell className={`text-right font-bold ${getSaldoColor(currentBilanz.stickstoff.saldo, N_GRENZWERT)}`}>
                    {currentBilanz.stickstoff.saldo > 0 ? '+' : ''}{currentBilanz.stickstoff.saldo} kg/ha
                  </TableCell>
                  <TableCell className="text-right">{N_GRENZWERT} kg/ha (3-J.Ø)</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Phosphor (P₂O₅)</TableCell>
                  <TableCell className="text-right">{currentBilanz.phosphor.zugang} kg/ha</TableCell>
                  <TableCell className="text-right">{currentBilanz.phosphor.abgang} kg/ha</TableCell>
                  <TableCell className={`text-right font-bold ${getSaldoColor(currentBilanz.phosphor.saldo, P_GRENZWERT)}`}>
                    {currentBilanz.phosphor.saldo > 0 ? '+' : ''}{currentBilanz.phosphor.saldo} kg/ha
                  </TableCell>
                  <TableCell className="text-right">{P_GRENZWERT} kg/ha (3-J.Ø)</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Kalium (K₂O)</TableCell>
                  <TableCell className="text-right">{currentBilanz.kalium.zugang} kg/ha</TableCell>
                  <TableCell className="text-right">{currentBilanz.kalium.abgang} kg/ha</TableCell>
                  <TableCell className={`text-right font-bold ${currentBilanz.kalium.saldo < 0 ? 'text-blue-600' : 'text-emerald-600'}`}>
                    {currentBilanz.kalium.saldo > 0 ? '+' : ''}{currentBilanz.kalium.saldo} kg/ha
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">-</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Schlagbezogene Bilanz */}
      <Card>
        <CardHeader>
          <CardTitle>Schlagbezogene Übersicht {selectedJahr}</CardTitle>
          <CardDescription>Nährstoffsalden je Schlag in kg/ha</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Schlag</TableHead>
                <TableHead>Kultur</TableHead>
                <TableHead className="text-right">Fläche</TableHead>
                <TableHead className="text-right">N-Saldo</TableHead>
                <TableHead className="text-right">P-Saldo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {schlagBilanzen.map((sb) => (
                <TableRow key={sb.schlag}>
                  <TableCell className="font-medium">{sb.schlag}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{sb.kultur}</Badge>
                  </TableCell>
                  <TableCell className="text-right">{sb.flaeche} ha</TableCell>
                  <TableCell className={`text-right font-medium ${getSaldoColor(sb.nSaldo, N_GRENZWERT)}`}>
                    {sb.nSaldo > 0 ? '+' : ''}{sb.nSaldo}
                  </TableCell>
                  <TableCell className={`text-right font-medium ${getSaldoColor(sb.pSaldo, P_GRENZWERT)}`}>
                    {sb.pSaldo > 0 ? '+' : ''}{sb.pSaldo}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Historische Bilanzen */}
      <Card>
        <CardHeader>
          <CardTitle>Historische Bilanzen</CardTitle>
          <CardDescription>Alle verfügbaren Jahresbilanzen</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-3">
            {bilanzen.map((bilanz) => (
              <Card key={bilanz.jahr} className="transition-all hover:shadow-md">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-lg font-bold">{bilanz.jahr}</span>
                    <Badge 
                      className={bilanz.status === 'abgeschlossen' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}
                    >
                      {bilanz.status === 'abgeschlossen' ? 'Abgeschlossen' : 'Vorläufig'}
                    </Badge>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">N-Saldo:</span>
                      <span className={`font-medium ${getSaldoColor(bilanz.stickstoff.saldo, N_GRENZWERT)}`}>
                        {bilanz.stickstoff.saldo > 0 ? '+' : ''}{bilanz.stickstoff.saldo} kg/ha
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">P-Saldo:</span>
                      <span className={`font-medium ${getSaldoColor(bilanz.phosphor.saldo, P_GRENZWERT)}`}>
                        {bilanz.phosphor.saldo > 0 ? '+' : ''}{bilanz.phosphor.saldo} kg/ha
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Fläche:</span>
                      <span className="font-medium">{bilanz.flaeche} ha</span>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" className="w-full mt-3 gap-2">
                    <Download className="h-4 w-4" />
                    PDF
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Info */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>Hinweis zur Düngeverordnung</AlertTitle>
        <AlertDescription>
          Die Nährstoffbilanzen werden gemäß DüV erstellt. Der 3-Jahres-Durchschnitt für Stickstoff 
          darf 50 kg N/ha und für Phosphor 10 kg P₂O₅/ha nicht überschreiten.
        </AlertDescription>
      </Alert>
    </div>
  )
}

function NaehrstoffbilanzenSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-10 w-[150px]" />
      </div>
      <Skeleton className="h-20 w-full" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-16 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-48 w-full" />
        </CardContent>
      </Card>
    </div>
  )
}

