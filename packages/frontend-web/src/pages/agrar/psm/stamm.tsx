import { useState, useEffect } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, Save, ShieldAlert } from 'lucide-react'
import { usePSMItem, agrarKeys } from '@/lib/api/agrar'
import { apiClient } from '@/lib/api-client'

type PSMData = {
  id: string
  mittel: string
  hersteller: string
  wirkstoff: string
  zulassungsnummer: string
  zulassungBis: string
  kulturen: string[]
  dosierung: string
  wasserschutz: boolean
  bienenschutz: boolean
  auflagen: string[]
  status: 'aktiv' | 'auslaufend' | 'widerrufen'
  ausgangsstoffExplosivstoffe: boolean
  erklaerungLandwirtErforderlich: boolean
  erklaerungLandwirtStatus: string | null
}

const DEFAULT_PSM: PSMData = {
  id: '',
  mittel: '',
  hersteller: '',
  wirkstoff: '',
  zulassungsnummer: '',
  zulassungBis: '',
  kulturen: [],
  dosierung: '',
  wasserschutz: false,
  bienenschutz: false,
  auflagen: [],
  status: 'aktiv',
  ausgangsstoffExplosivstoffe: false,
  erklaerungLandwirtErforderlich: false,
  erklaerungLandwirtStatus: null,
}

export default function PSMStammPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()

  const { data: psmData, isLoading } = usePSMItem(id || '')
  const [psm, setPSM] = useState<PSMData>(DEFAULT_PSM)

  useEffect(() => {
    if (psmData) {
      const ext = psmData as unknown as Record<string, unknown>
      setPSM({
        id: psmData.id,
        mittel: psmData.mittel,
        hersteller: String(ext.hersteller ?? ''),
        wirkstoff: psmData.wirkstoff,
        zulassungsnummer: String(ext.zulassungsnummer ?? ''),
        zulassungBis: psmData.zulassungBis,
        kulturen: psmData.kulturen,
        dosierung: String(ext.dosierung ?? ''),
        wasserschutz: Boolean(ext.wasserschutz ?? false),
        bienenschutz: Boolean(ext.bienenschutz ?? false),
        auflagen: Array.isArray(ext.auflagen) ? ext.auflagen as string[] : [],
        status: psmData.status,
        ausgangsstoffExplosivstoffe: Boolean(ext.ausgangsstoffExplosivstoffe ?? false),
        erklaerungLandwirtErforderlich: Boolean(ext.erklaerungLandwirtErforderlich ?? false),
        erklaerungLandwirtStatus: psmData.erklaerungLandwirtStatus,
      })
    }
  }, [psmData])

  const updateMutation = useMutation({
    mutationFn: async (data: PSMData) => {
      const response = await apiClient.patch<PSMData>(`/api/v1/agrar/psm/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: agrarKeys.psm() })
      navigate('/agrar/psm/liste')
    },
  })

  async function handleSave(): Promise<void> {
    await updateMutation.mutateAsync(psm)
  }

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-48" />
      </div>
    )
  }

  if (!psmData && id && id !== 'neu') {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">PSM-Mittel nicht gefunden.</p>
      </div>
    )
  }

  const istAblaufend = psm.zulassungBis
    ? new Date(psm.zulassungBis) < new Date(Date.now() + 180 * 24 * 60 * 60 * 1000)
    : false

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{psm.mittel || 'PSM-Stammdaten'}</h1>
          <p className="text-muted-foreground">Pflanzenschutzmittel-Stammdaten</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/agrar/psm/liste')}>
            Abbrechen
          </Button>
          <Button onClick={handleSave} disabled={updateMutation.isPending} className="gap-2">
            <Save className="h-4 w-4" />
            Speichern
          </Button>
        </div>
      </div>

      {istAblaufend && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">Zulassung läuft in weniger als 6 Monaten ab!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="allgemein">
        <TabsList>
          <TabsTrigger value="allgemein">Allgemein</TabsTrigger>
          <TabsTrigger value="zulassung">Zulassung</TabsTrigger>
          <TabsTrigger value="anwendung">Anwendung</TabsTrigger>
          <TabsTrigger value="sicherheit">Sicherheit</TabsTrigger>
          <TabsTrigger value="erklaerung">Erklärung Landwirt</TabsTrigger>
        </TabsList>

        <TabsContent value="allgemein" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Grunddaten</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Mittel</Label>
                <Input value={psm.mittel} onChange={(e) => setPSM({ ...psm, mittel: e.target.value })} />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Hersteller</Label>
                  <Input value={psm.hersteller} onChange={(e) => setPSM({ ...psm, hersteller: e.target.value })} />
                </div>
                <div>
                  <Label>Wirkstoff</Label>
                  <Input value={psm.wirkstoff} onChange={(e) => setPSM({ ...psm, wirkstoff: e.target.value })} />
                </div>
              </div>
              <div>
                <Label>Status</Label>
                <div className="mt-2">
                  <Badge variant={psm.status === 'aktiv' ? 'outline' : 'destructive'}>
                    {psm.status === 'aktiv' ? 'Aktiv' : psm.status === 'auslaufend' ? 'Auslaufend' : 'Widerrufen'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="zulassung" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Zulassungsdaten (BVL)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Zulassungsnummer</Label>
                  <Input value={psm.zulassungsnummer} readOnly className="font-mono" />
                </div>
                <div>
                  <Label>Gültig bis</Label>
                  <Input type="date" value={psm.zulassungBis} onChange={(e) => setPSM({ ...psm, zulassungBis: e.target.value })} />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="anwendung" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Anwendungsgebiete</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Zugelassene Kulturen</Label>
                <div className="mt-2 flex flex-wrap gap-2">
                  {psm.kulturen.map((kultur, i) => (
                    <Badge key={i} variant="outline">{kultur}</Badge>
                  ))}
                </div>
              </div>
              <div>
                <Label>Dosierung</Label>
                <Input value={psm.dosierung} onChange={(e) => setPSM({ ...psm, dosierung: e.target.value })} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sicherheit" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldAlert className="h-5 w-5" />
                Sicherheit & Auflagen
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={psm.wasserschutz}
                    onChange={(e) => setPSM({ ...psm, wasserschutz: e.target.checked })}
                    className="h-4 w-4"
                  />
                  <Label>Wasserschutzgebiets-relevant (NW-Auflagen)</Label>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={psm.bienenschutz}
                    onChange={(e) => setPSM({ ...psm, bienenschutz: e.target.checked })}
                    className="h-4 w-4"
                  />
                  <Label>Bienenschutz-Auflagen (B-Auflagen)</Label>
                </div>
              </div>
              <div>
                <Label>Auflagen</Label>
                <div className="mt-2 flex flex-wrap gap-2">
                  {psm.auflagen.map((auflage, i) => (
                    <Badge key={i} variant="destructive">{auflage}</Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="erklaerung" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldAlert className="h-5 w-5" />
                Erklärung des Landwirts (§ 64 PflSchG)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={psm.ausgangsstoffExplosivstoffe}
                    onChange={(e) => setPSM({ ...psm, ausgangsstoffExplosivstoffe: e.target.checked })}
                    className="h-4 w-4"
                  />
                  <Label>Ausgangsstoff für Explosivstoffe (Ammoniumnitrat, Schwefelsäure, etc.)</Label>
                </div>
                {psm.ausgangsstoffExplosivstoffe && (
                  <div className="ml-6 space-y-2">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={psm.erklaerungLandwirtErforderlich}
                        onChange={(e) => setPSM({ ...psm, erklaerungLandwirtErforderlich: e.target.checked })}
                        className="h-4 w-4"
                      />
                      <Label>Erklärung des Landwirts erforderlich</Label>
                    </div>
                    {psm.erklaerungLandwirtErforderlich && (
                      <div className="ml-6">
                        <Label>Status der Erklärung</Label>
                        <select
                          value={psm.erklaerungLandwirtStatus || ''}
                          onChange={(e) => setPSM({ ...psm, erklaerungLandwirtStatus: e.target.value || null })}
                          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                        >
                          <option value="">Nicht eingereicht</option>
                          <option value="eingegangen">Eingegangen</option>
                          <option value="geprueft">Geprüft</option>
                          <option value="abgelehnt">Abgelehnt</option>
                        </select>
                      </div>
                    )}
                  </div>
                )}
              </div>
              {psm.ausgangsstoffExplosivstoffe && psm.erklaerungLandwirtErforderlich && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-900">
                    <strong>Hinweis:</strong> Bei Abgabe dieses PSM-Mittels muss der Landwirt eine Erklärung
                    über die beabsichtigte Verwendung abgeben. Die Erklärung wird im DMS-System gespeichert
                    und dient der Compliance-Nachweisführung.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
