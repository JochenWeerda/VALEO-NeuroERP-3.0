import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Save, Tractor, Plus, Minus, Loader2, ArrowLeft, MapPin } from 'lucide-react'
import { queryKeys } from '@/lib/query'
import { crmService, type FarmProfile } from '@/lib/services/crm-service'
import { useToast } from '@/components/ui/toast-provider'

export default function BetriebsprofilePage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams()
  const queryClient = useQueryClient()
  const toast = useToast()
  const isNew = !id || id === 'neu'

  const [farmProfile, setFarmProfile] = useState<Partial<FarmProfile>>({
    farmName: '',
    owner: '',
    totalArea: 0,
    crops: [{ crop: '', area: 0 }],
    livestock: [{ type: '', count: 0 }],
    location: {
      latitude: 0,
      longitude: 0,
      address: '',
    },
    certifications: [],
    notes: '',
  })

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.crm.farmProfiles.detail(id ?? ''),
    queryFn: () => crmService.getFarmProfile(id ?? ''),
    enabled: !isNew && !!id,
  })

  useEffect(() => {
    if (data) {
      setFarmProfile(data)
    }
  }, [data])

  const createMutation = useMutation({
    mutationFn: (data: Omit<FarmProfile, 'id' | 'createdAt' | 'updatedAt'>) => crmService.createFarmProfile(data),
    onSuccess: () => {
      toast.push('Betriebsprofil erfolgreich erstellt')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.farmProfiles.all })
      navigate('/crm/betriebsprofile')
    },
    onError: (error) => {
      toast.push('Fehler beim Erstellen des Betriebsprofils')
      console.error('Create error:', error)
    },
  })

  const updateMutation = useMutation({
    mutationFn: (data: Partial<Omit<FarmProfile, 'id' | 'createdAt' | 'updatedAt'>>) =>
      crmService.updateFarmProfile(id ?? '', data),
    onSuccess: () => {
      toast.push('Betriebsprofil erfolgreich aktualisiert')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.farmProfiles.detail(id ?? '') })
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.farmProfiles.all })
    },
    onError: (error) => {
      toast.push('Fehler beim Aktualisieren des Betriebsprofils')
      console.error('Update error:', error)
    },
  })

  const handleSave = () => {
    if (isNew) {
      createMutation.mutate(farmProfile as Omit<FarmProfile, 'id' | 'createdAt' | 'updatedAt'>)
    } else {
      updateMutation.mutate(farmProfile)
    }
  }

  const updateField = (field: keyof FarmProfile, value: any) => {
    setFarmProfile(prev => ({ ...prev, [field]: value }))
  }

  const addCrop = () => {
    setFarmProfile(prev => ({
      ...prev,
      crops: [...(prev.crops || []), { crop: '', area: 0 }]
    }))
  }

  const removeCrop = (index: number) => {
    setFarmProfile(prev => ({
      ...prev,
      crops: prev.crops?.filter((_, i) => i !== index) || []
    }))
  }

  const updateCrop = (index: number, field: 'crop' | 'area', value: string | number) => {
    setFarmProfile(prev => ({
      ...prev,
      crops: prev.crops?.map((crop, i) =>
        i === index ? { ...crop, [field]: value } : crop
      ) || []
    }))
  }

  const addLivestock = () => {
    setFarmProfile(prev => ({
      ...prev,
      livestock: [...(prev.livestock || []), { type: '', count: 0 }]
    }))
  }

  const removeLivestock = (index: number) => {
    setFarmProfile(prev => ({
      ...prev,
      livestock: prev.livestock?.filter((_, i) => i !== index) || []
    }))
  }

  const updateLivestock = (index: number, field: 'type' | 'count', value: string | number) => {
    setFarmProfile(prev => ({
      ...prev,
      livestock: prev.livestock?.map((animal, i) =>
        i === index ? { ...animal, [field]: value } : animal
      ) || []
    }))
  }

  const totalCropArea = farmProfile.crops?.reduce((sum, crop) => sum + (crop.area || 0), 0) || 0

  if (isLoading && !isNew) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Lade Betriebsprofil...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {!isNew && (
            <Button variant="outline" size="sm" onClick={() => navigate('/crm/betriebsprofile')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Zurück
            </Button>
          )}
          <div className="flex items-center gap-3">
            <Tractor className="h-8 w-8 text-green-600" />
            <div>
              <h1 className="text-3xl font-bold">
                {isNew ? 'Neues Betriebsprofil' : farmProfile.farmName || 'Betriebsprofil'}
              </h1>
              <p className="text-muted-foreground">
                {isNew ? 'Erstellen Sie ein neues Betriebsprofil' : `Inhaber: ${farmProfile.owner || 'Nicht angegeben'}`}
              </p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/crm/betriebsprofile')}>
            Abbrechen
          </Button>
          <Button
            onClick={handleSave}
            disabled={createMutation.isPending || updateMutation.isPending}
            className="gap-2"
          >
            {(createMutation.isPending || updateMutation.isPending) && (
              <Loader2 className="h-4 w-4 animate-spin" />
            )}
            <Save className="h-4 w-4" />
            {isNew ? 'Erstellen' : 'Speichern'}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="allgemein" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="allgemein">Allgemein</TabsTrigger>
          <TabsTrigger value="kulturen">Kulturen</TabsTrigger>
          <TabsTrigger value="tiere">Tierbestand</TabsTrigger>
          <TabsTrigger value="standort">Standort</TabsTrigger>
          <TabsTrigger value="zertifizierungen">Zertifizierungen</TabsTrigger>
        </TabsList>

        <TabsContent value="allgemein">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Grunddaten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="farmName">Betriebsname *</Label>
                  <Input
                    id="farmName"
                    value={farmProfile.farmName || ''}
                    onChange={(e) => updateField('farmName', e.target.value)}
                    placeholder="z.B. Hof Schmidt GmbH"
                  />
                </div>
                <div>
                  <Label htmlFor="owner">Inhaber *</Label>
                  <Input
                    id="owner"
                    value={farmProfile.owner || ''}
                    onChange={(e) => updateField('owner', e.target.value)}
                    placeholder="z.B. Hermann Schmidt"
                  />
                </div>
                <div>
                  <Label htmlFor="totalArea">Gesamtfläche (ha) *</Label>
                  <Input
                    id="totalArea"
                    type="number"
                    step="0.01"
                    value={farmProfile.totalArea || ''}
                    onChange={(e) => updateField('totalArea', parseFloat(e.target.value) || 0)}
                    placeholder="z.B. 250.5"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Notizen</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  value={farmProfile.notes || ''}
                  onChange={(e) => updateField('notes', e.target.value)}
                  placeholder="Zusätzliche Informationen zum Betrieb..."
                  rows={6}
                />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="kulturen">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Anbauflächen</CardTitle>
              <Button onClick={addCrop} size="sm" className="gap-2">
                <Plus className="h-4 w-4" />
                Kultur hinzufügen
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {farmProfile.crops?.map((crop, index) => (
                  <div key={index} className="flex items-center gap-4 p-4 border rounded-lg">
                    <div className="flex-1">
                      <Label>Kultur</Label>
                      <Input
                        value={crop.crop}
                        onChange={(e) => updateCrop(index, 'crop', e.target.value)}
                        placeholder="z.B. Weizen"
                      />
                    </div>
                    <div className="w-32">
                      <Label>Fläche (ha)</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={crop.area || ''}
                        onChange={(e) => updateCrop(index, 'area', parseFloat(e.target.value) || 0)}
                        placeholder="0.00"
                      />
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeCrop(index)}
                      className="mt-6"
                    >
                      <Minus className="h-4 w-4" />
                    </Button>
                  </div>
                ))}

                <div className="mt-6 p-4 bg-muted rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">Gesamtfläche Anbau:</span>
                    <span className="text-lg font-bold">{totalCropArea.toFixed(2)} ha</span>
                  </div>
                  {farmProfile.totalArea && totalCropArea > farmProfile.totalArea && (
                    <p className="text-sm text-red-600 mt-2">
                      ⚠️ Anbaufläche überschreitet Gesamtfläche des Betriebs
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tiere">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Tierbestand</CardTitle>
              <Button onClick={addLivestock} size="sm" className="gap-2">
                <Plus className="h-4 w-4" />
                Tierart hinzufügen
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {farmProfile.livestock?.map((animal, index) => (
                  <div key={index} className="flex items-center gap-4 p-4 border rounded-lg">
                    <div className="flex-1">
                      <Label>Tierart</Label>
                      <Select
                        value={animal.type}
                        onValueChange={(value) => updateLivestock(index, 'type', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Tierart auswählen" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Milchkühe">Milchkühe</SelectItem>
                          <SelectItem value="Mastbullen">Mastbullen</SelectItem>
                          <SelectItem value="Kälber">Kälber</SelectItem>
                          <SelectItem value="Schweine">Schweine</SelectItem>
                          <SelectItem value="Schafe">Schafe</SelectItem>
                          <SelectItem value="Geflügel">Geflügel</SelectItem>
                          <SelectItem value="Pferde">Pferde</SelectItem>
                          <SelectItem value="Sonstige">Sonstige</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="w-32">
                      <Label>Anzahl</Label>
                      <Input
                        type="number"
                        value={animal.count || ''}
                        onChange={(e) => updateLivestock(index, 'count', parseInt(e.target.value) || 0)}
                        placeholder="0"
                      />
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeLivestock(index)}
                      className="mt-6"
                    >
                      <Minus className="h-4 w-4" />
                    </Button>
                  </div>
                ))}

                <div className="mt-6 p-4 bg-muted rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">Gesamt Viehbestand:</span>
                    <span className="text-lg font-bold">
                      {farmProfile.livestock?.reduce((sum, animal) => sum + (animal.count || 0), 0) || 0} Tiere
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="standort">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Standort & Geodaten
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="address">Adresse</Label>
                <Textarea
                  id="address"
                  value={farmProfile.location?.address || ''}
                  onChange={(e) => updateField('location', {
                    ...farmProfile.location,
                    address: e.target.value
                  })}
                  placeholder="Straße, PLZ, Ort, Land"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="latitude">Breitengrad</Label>
                  <Input
                    id="latitude"
                    type="number"
                    step="0.000001"
                    value={farmProfile.location?.latitude || ''}
                    onChange={(e) => updateField('location', {
                      ...farmProfile.location,
                      latitude: parseFloat(e.target.value) || 0
                    })}
                    placeholder="z.B. 52.520008"
                  />
                </div>
                <div>
                  <Label htmlFor="longitude">Längengrad</Label>
                  <Input
                    id="longitude"
                    type="number"
                    step="0.000001"
                    value={farmProfile.location?.longitude || ''}
                    onChange={(e) => updateField('location', {
                      ...farmProfile.location,
                      longitude: parseFloat(e.target.value) || 0
                    })}
                    placeholder="z.B. 13.404954"
                  />
                </div>
              </div>

              <div className="text-sm text-muted-foreground">
                <p>Koordinaten können automatisch aus der Adresse ermittelt werden oder manuell eingetragen werden.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="zertifizierungen">
          <Card>
            <CardHeader>
              <CardTitle>Zertifizierungen & Standards</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label>Zertifizierungen</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {['Bio', 'GAP', 'QS', 'IFS', 'HACCP', 'GMP+', 'RSPO', 'Rainforest Alliance'].map(cert => (
                      <Badge
                        key={cert}
                        variant={farmProfile.certifications?.includes(cert) ? 'default' : 'outline'}
                        className="cursor-pointer"
                        onClick={() => {
                          const current = farmProfile.certifications || []
                          const updated = current.includes(cert)
                            ? current.filter(c => c !== cert)
                            : [...current, cert]
                          updateField('certifications', updated)
                        }}
                      >
                        {cert}
                      </Badge>
                    ))}
                  </div>
                </div>

                {farmProfile.certifications && farmProfile.certifications.length > 0 && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <h4 className="font-semibold text-green-800 mb-2">Aktive Zertifizierungen:</h4>
                    <div className="flex flex-wrap gap-2">
                      {farmProfile.certifications.map(cert => (
                        <Badge key={cert} variant="default" className="bg-green-600">
                          {cert}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
