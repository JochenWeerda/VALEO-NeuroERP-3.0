import { useState, useEffect } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { BackButton } from '@/components/BackButton'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { AlertTriangle, FileText, Save, User, Calendar, CheckCircle, XCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

type PSMAbgabeData = {
  id: string
  psmId: string
  psmName: string
  wirkstoff: string
  menge: number
  einheit: string
  kundeId: string
  kundeName: string
  landwirtName: string
  sachkundeNummer: string
  sachkundeGueltigBis: string
  verwendungszweck: string
  auflagen: string[]
  wasserschutzgebiet: boolean
  bienenschutz: boolean
  erklaerungLandwirt: boolean
  erklaerungStatus: 'ausstehend' | 'eingegangen' | 'geprueft' | 'abgelehnt'
  dokumente: Array<{
    id: string
    name: string
    type: string
    uploadedAt: string
  }>
  status: 'entwurf' | 'freigegeben' | 'abgeschlossen'
  createdAt: string
  updatedAt: string
}

function getInitialAbgabe(routeId: string | undefined): PSMAbgabeData {
  const now = new Date().toISOString()
  return {
    id: routeId && routeId !== 'neu' ? routeId : '',
    psmId: '',
    psmName: '',
    wirkstoff: '',
    menge: 0,
    einheit: 'Liter',
    kundeId: '',
    kundeName: '',
    landwirtName: '',
    sachkundeNummer: '',
    sachkundeGueltigBis: '',
    verwendungszweck: '',
    auflagen: [],
    wasserschutzgebiet: false,
    bienenschutz: false,
    erklaerungLandwirt: false,
    erklaerungStatus: 'ausstehend',
    dokumente: [],
    status: 'entwurf',
    createdAt: now,
    updatedAt: now
  }
}

export default function PSMAbgabeDokumentationPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams()
  const { toast } = useToast()

  const [abgabe, setAbgabe] = useState<PSMAbgabeData>(() => getInitialAbgabe(id))

  const { data: abgabeApiData } = useQuery({
    queryKey: ['agrar', 'psm-abgabe', id],
    queryFn: async () => {
      const response = await apiClient.get<PSMAbgabeData>(`/api/v1/agrar/psm/abgabe/${id}`)
      return response.data
    },
    enabled: !!id && id !== 'neu',
  })

  useEffect(() => {
    if (id === 'neu' || !id) {
      setAbgabe(getInitialAbgabe(id))
      return
    }
    if (abgabeApiData) setAbgabe(abgabeApiData)
  }, [id, abgabeApiData])

  const saveMutation = useMutation({
    mutationFn: async (data: PSMAbgabeData) => {
      const response = await apiClient.put<PSMAbgabeData>(`/api/v1/agrar/psm/abgabe/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      toast({ title: 'Gespeichert', description: 'PSM-Abgabe-Dokumentation wurde erfolgreich gespeichert.' })
      navigate('/agrar/psm/liste')
    },
    onError: () => {
      toast({ title: 'Fehler', description: 'Fehler beim Speichern der PSM-Abgabe-Dokumentation.', variant: 'destructive' })
    },
  })

  const statusMutation = useMutation({
    mutationFn: async (newStatus: PSMAbgabeData['status']) => {
      const response = await apiClient.put(`/api/v1/agrar/psm/abgabe/${id}/status`, { status: newStatus })
      return response.data
    },
    onSuccess: (_data, newStatus) => {
      setAbgabe(prev => ({ ...prev, status: newStatus, updatedAt: new Date().toISOString() }))
      toast({ title: 'Status aktualisiert', description: `PSM-Abgabe wurde auf "${newStatus}" gesetzt.` })
    },
    onError: () => {
      toast({ title: 'Fehler', description: 'Fehler beim Aktualisieren des Status.', variant: 'destructive' })
    },
  })

  const erklaerungMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post(`/api/v1/agrar/psm/${abgabe.psmId}/erklaerung`, {})
      return response.data
    },
    onSuccess: () => {
      setAbgabe(prev => ({ ...prev, erklaerungStatus: 'eingegangen', updatedAt: new Date().toISOString() }))
      toast({ title: 'Erklärung hochgeladen', description: 'Die Erklärung des Landwirts wurde erfolgreich hochgeladen.' })
    },
    onError: () => {
      toast({ title: 'Fehler', description: 'Fehler beim Hochladen der Erklärung.', variant: 'destructive' })
    },
  })

  const isLoading = saveMutation.isPending || statusMutation.isPending || erklaerungMutation.isPending

  const handleSave = () => saveMutation.mutate(abgabe)
  const handleStatusChange = (newStatus: PSMAbgabeData['status']) => statusMutation.mutate(newStatus)
  const handleErklaerungUpload = () => erklaerungMutation.mutate()

  const isSachkundeValid = new Date(abgabe.sachkundeGueltigBis) > new Date()
  const hasAllRequiredDocs = abgabe.dokumente.length > 0 && abgabe.erklaerungStatus !== 'ausstehend'

  return (
    <div className="space-y-6 p-6">
      <ModuleToolbar backTarget="/agrar/psm/liste" closeTarget="/agrar/psm/liste" title="PSM-Abgabe-Dokumentation" />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">PSM-Abgabe-Dokumentation</h1>
          <p className="text-muted-foreground">
            {abgabe.psmName || abgabe.kundeName
              ? `Abgabe von ${abgabe.psmName || '—'} an ${abgabe.kundeName || '—'}`
              : 'Neue PSM-Abgabe erfassen'}
          </p>
        </div>
        <div className="flex gap-2">
          <BackButton to="/agrar/psm" label="Zurück zu PSM-Übersicht" />
          <Button onClick={handleSave} disabled={isLoading} className="gap-2">
            <Save className="h-4 w-4" />
            Speichern
          </Button>
        </div>
      </div>

      {/* Status Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Abgabe-Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex items-center gap-2">
              <Badge variant={abgabe.status === 'abgeschlossen' ? 'default' : 'secondary'}>
                {abgabe.status === 'entwurf' ? 'Entwurf' : abgabe.status === 'freigegeben' ? 'Freigegeben' : 'Abgeschlossen'}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <User className="h-4 w-4" />
              <span className="text-sm">{abgabe.landwirtName}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span className="text-sm">{new Date(abgabe.createdAt).toLocaleDateString('de-DE')}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* PSM Details */}
      <Card>
        <CardHeader>
          <CardTitle>PSM-Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>PSM</Label>
              <Input value={abgabe.psmName} readOnly />
            </div>
            <div>
              <Label>Wirkstoff</Label>
              <Input value={abgabe.wirkstoff} readOnly />
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <Label>Menge</Label>
              <Input
                type="number"
                value={abgabe.menge}
                onChange={(e) => setAbgabe(prev => ({ ...prev, menge: parseFloat(e.target.value) }))}
              />
            </div>
            <div>
              <Label>Einheit</Label>
              <NativeSelect
                value={abgabe.einheit}
                onValueChange={(value) => setAbgabe(prev => ({ ...prev, einheit: value }))}
                options={[
                  { value: 'Liter', label: 'Liter' },
                  { value: 'kg', label: 'kg' },
                  { value: 'Stueck', label: 'Stueck' },
                ]}
              />
            </div>
            <div>
              <Label>Verwendungszweck</Label>
              <Input
                value={abgabe.verwendungszweck}
                onChange={(e) => setAbgabe(prev => ({ ...prev, verwendungszweck: e.target.value }))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Kunde & Sachkunde */}
      <Card>
        <CardHeader>
          <CardTitle>Kunde & Sachkunde</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Kunde</Label>
              <Input value={abgabe.kundeName} readOnly />
            </div>
            <div>
              <Label>Landwirt</Label>
              <Input
                value={abgabe.landwirtName}
                onChange={(e) => setAbgabe(prev => ({ ...prev, landwirtName: e.target.value }))}
              />
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Sachkunde-Nummer</Label>
              <Input
                value={abgabe.sachkundeNummer}
                onChange={(e) => setAbgabe(prev => ({ ...prev, sachkundeNummer: e.target.value }))}
              />
            </div>
            <div>
              <Label>Gültig bis</Label>
              <Input
                type="date"
                value={abgabe.sachkundeGueltigBis}
                onChange={(e) => setAbgabe(prev => ({ ...prev, sachkundeGueltigBis: e.target.value }))}
              />
            </div>
          </div>
          {!isSachkundeValid && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <span className="text-red-800 font-medium">Sachkunde abgelaufen!</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Auflagen & Sicherheit */}
      <Card>
        <CardHeader>
          <CardTitle>Auflagen & Sicherheit</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Auflagen</Label>
            <div className="mt-2 flex flex-wrap gap-2">
              {abgabe.auflagen.map((auflage, i) => (
                <Badge key={i} variant="destructive">{auflage}</Badge>
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={abgabe.wasserschutzgebiet}
                onChange={(e) => setAbgabe(prev => ({ ...prev, wasserschutzgebiet: e.target.checked }))}
                className="h-4 w-4"
              />
              <Label>Wasserschutzgebiet (NW-Auflagen)</Label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={abgabe.bienenschutz}
                onChange={(e) => setAbgabe(prev => ({ ...prev, bienenschutz: e.target.checked }))}
                className="h-4 w-4"
              />
              <Label>Bienenschutz-Auflagen (B-Auflagen)</Label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Erklärung des Landwirts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Erklärung des Landwirts
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {abgabe.erklaerungStatus === 'eingegangen' && <CheckCircle className="h-5 w-5 text-green-600" />}
              {abgabe.erklaerungStatus === 'abgelehnt' && <XCircle className="h-5 w-5 text-red-600" />}
              <span>Status: </span>
              <Badge variant={
                abgabe.erklaerungStatus === 'geprueft' ? 'default' :
                abgabe.erklaerungStatus === 'eingegangen' ? 'secondary' :
                abgabe.erklaerungStatus === 'abgelehnt' ? 'destructive' : 'outline'
              }>
                {abgabe.erklaerungStatus === 'ausstehend' ? 'Ausstehend' :
                 abgabe.erklaerungStatus === 'eingegangen' ? 'Eingegangen' :
                 abgabe.erklaerungStatus === 'geprueft' ? 'Geprüft' : 'Abgelehnt'}
              </Badge>
            </div>
            <Button onClick={handleErklaerungUpload} disabled={abgabe.erklaerungStatus !== 'ausstehend'}>
              Erklärung hochladen
            </Button>
          </div>
          {abgabe.erklaerungStatus === 'ausstehend' && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-yellow-800">
                Die Erklärung des Landwirts ist erforderlich, da dieses PSM Ausgangsstoffe für Explosivstoffe enthält.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dokumente */}
      <Card>
        <CardHeader>
          <CardTitle>Dokumente</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {abgabe.dokumente.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-2 border rounded">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  <span>{doc.name}</span>
                  <Badge variant="outline">{doc.type.toUpperCase()}</Badge>
                </div>
                <span className="text-sm text-muted-foreground">
                  {new Date(doc.uploadedAt).toLocaleDateString('de-DE')}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-end gap-2">
        {abgabe.status === 'entwurf' && (
          <Button
            onClick={() => handleStatusChange('freigegeben')}
            disabled={!hasAllRequiredDocs || !isSachkundeValid}
            className="gap-2"
          >
            <CheckCircle className="h-4 w-4" />
            Freigeben
          </Button>
        )}
        {abgabe.status === 'freigegeben' && (
          <Button
            onClick={() => handleStatusChange('abgeschlossen')}
            className="gap-2"
          >
            <CheckCircle className="h-4 w-4" />
            Abschließen
          </Button>
        )}
      </div>
    </div>
  )
}