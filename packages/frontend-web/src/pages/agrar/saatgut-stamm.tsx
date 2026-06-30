/**
 * Saatgut-Stammdaten Maske
 * ObjectPage für Saatgut-Verwaltung mit vollständiger CRUD-Funktionalität
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from '@/app/routing/typed-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { NativeSelect } from '@/components/ui/native-select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';
import { Save, ArrowLeft, CheckCircle, XCircle, AlertTriangle, Pencil } from 'lucide-react';
import { toast } from 'sonner';
import { useTenant } from '@/hooks/useTenant';
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar';
import { apiClient } from '@/lib/api-client';
import { apiErrorDetail, errorMessage } from '@/lib/record-utils';

// API response type (server returns strings for dates, all fields optional)
interface SaatgutApiData {
  artikelnummer?: string
  name?: string
  sorte?: string
  art?: string
  zuechter?: string
  zulassungsnummer?: string
  bsa_zulassung?: boolean
  eu_zulassung?: boolean
  ablauf_zulassung?: string | null
  tkm?: number | null
  keimfaehigkeit?: number | null
  aussaatstaerke?: number | null
  ek_preis?: number | null
  vk_preis?: number | null
  waehrung?: string
  mindestabnahme?: number | null
  lagerbestand?: number
  reserviert?: number
  verfuegbar?: number
  lagerort?: string
}

// Form Data Interface
interface SaatgutFormData {
  artikelnummer: string;
  name: string;
  sorte: string;
  art: string;
  zuechter: string;
  zulassungsnummer: string;
  bsa_zulassung: boolean;
  eu_zulassung: boolean;
  ablauf_zulassung: Date | null;
  tkm: number | null;
  keimfaehigkeit: number | null;
  aussaatstaerke: number | null;
  ek_preis: number | null;
  vk_preis: number | null;
  waehrung: string;
  mindestabnahme: number | null;
  lagerbestand: number;
  reserviert: number;
  verfuegbar: number;
  lagerort: string;
}

const SaatgutStammPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { tenantId } = useTenant();
  const isEditing = !!id;
  const readOnlyMode = searchParams.get('mode') === 'view' && !!id;

  // Form State
  const [formData, setFormData] = useState<SaatgutFormData>({
    artikelnummer: '',
    name: '',
    sorte: '',
    art: '',
    zuechter: '',
    zulassungsnummer: '',
    bsa_zulassung: false,
    eu_zulassung: false,
    ablauf_zulassung: null,
    tkm: null,
    keimfaehigkeit: null,
    aussaatstaerke: null,
    ek_preis: null,
    vk_preis: null,
    waehrung: 'EUR',
    mindestabnahme: null,
    lagerbestand: 0,
    reserviert: 0,
    verfuegbar: 0,
    lagerort: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Queries
  const { data: saatgut, isLoading } = useQuery<SaatgutApiData>({
    queryKey: ['saatgut', id],
    queryFn: async () => {
      const r = await apiClient.get<SaatgutApiData>(`/api/v1/agrar/saatgut/${id}`)
      return r.data
    },
    enabled: isEditing && !!id,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: async (data: Record<string, unknown>) => { const r = await apiClient.post('/api/v1/agrar/saatgut', data); return r.data },
    onSuccess: () => {
      toast.success('Saatgut erfolgreich erstellt');
      queryClient.invalidateQueries({ queryKey: ['saatgut'] });
      navigate('/agrar/saatgut-liste');
    },
    onError: (error: unknown) => {
      toast.error(`Fehler beim Erstellen: ${errorMessage(error)}`);
      const detail = apiErrorDetail(error);
      if (detail) {
        setErrors({ general: detail });
      }
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Record<string, unknown> }) => { const r = await apiClient.put(`/api/v1/agrar/saatgut/${id}`, data); return r.data },
    onSuccess: () => {
      toast.success('Saatgut erfolgreich aktualisiert');
      queryClient.invalidateQueries({ queryKey: ['saatgut', id] });
    },
    onError: (error: unknown) => {
      toast.error(`Fehler beim Aktualisieren: ${errorMessage(error)}`);
    },
  });

  // Load data when editing
  useEffect(() => {
    if (saatgut) {
      setFormData({
        artikelnummer: saatgut.artikelnummer || '',
        name: saatgut.name || '',
        sorte: saatgut.sorte || '',
        art: saatgut.art || '',
        zuechter: saatgut.zuechter || '',
        zulassungsnummer: saatgut.zulassungsnummer || '',
        bsa_zulassung: saatgut.bsa_zulassung || false,
        eu_zulassung: saatgut.eu_zulassung || false,
        ablauf_zulassung: saatgut.ablauf_zulassung ? new Date(saatgut.ablauf_zulassung) : null,
        tkm: saatgut.tkm || null,
        keimfaehigkeit: saatgut.keimfaehigkeit || null,
        aussaatstaerke: saatgut.aussaatstaerke || null,
        ek_preis: saatgut.ek_preis || null,
        vk_preis: saatgut.vk_preis || null,
        waehrung: saatgut.waehrung || 'EUR',
        mindestabnahme: saatgut.mindestabnahme || null,
        lagerbestand: saatgut.lagerbestand || 0,
        reserviert: saatgut.reserviert || 0,
        verfuegbar: saatgut.verfuegbar || 0,
        lagerort: saatgut.lagerort || '',
      });
    }
  }, [saatgut]);

  // Form Handlers
  const handleInputChange = (field: keyof SaatgutFormData, value: unknown) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.artikelnummer.trim()) {
      newErrors.artikelnummer = 'Artikelnummer ist erforderlich';
    }
    if (!formData.name.trim()) {
      newErrors.name = 'Name ist erforderlich';
    }
    if (!formData.sorte.trim()) {
      newErrors.sorte = 'Sorte ist erforderlich';
    }
    if (!formData.art.trim()) {
      newErrors.art = 'Art ist erforderlich';
    }

    // Zulassungs-Validierung
    if (formData.ablauf_zulassung && formData.ablauf_zulassung < new Date()) {
      newErrors.ablauf_zulassung = 'Ablaufdatum darf nicht in der Vergangenheit liegen';
    }

    // Prozent-Validierungen
    if (formData.keimfaehigkeit !== null && (formData.keimfaehigkeit < 0 || formData.keimfaehigkeit > 100)) {
      newErrors.keimfaehigkeit = 'Keimfähigkeit muss zwischen 0 und 100 liegen';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      toast.error('Bitte korrigieren Sie die Fehler im Formular');
      return;
    }

    const submitData = {
      ...formData,
      ablauf_zulassung: formData.ablauf_zulassung?.toISOString().split('T')[0] || null,
      tenant_id: tenantId,
    };

    if (isEditing) {
      updateMutation.mutate({ id, data: submitData });
    } else {
      createMutation.mutate(submitData);
    }
  };

  const handleCancel = () => {
    navigate('/agrar/saatgut-liste');
  };

  if (isLoading) {
    return <div className="p-6">Laden...</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <ModuleToolbar
        backTarget="/agrar/saatgut-liste"
        closeTarget="/agrar/saatgut-liste"
        title={readOnlyMode ? 'Saatgut anzeigen' : isEditing ? 'Saatgut bearbeiten' : 'Neues Saatgut'}
      />
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={handleCancel}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Zurück
          </Button>
          <div>
            <h1 className="text-2xl font-bold">
              {readOnlyMode ? 'Saatgut anzeigen' : isEditing ? 'Saatgut bearbeiten' : 'Neues Saatgut'}
            </h1>
            <p className="text-muted-foreground">
              {isEditing ? `Artikel: ${formData.artikelnummer}` : 'Stammdaten für Saatgut anlegen'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          {readOnlyMode ? (
            <Button onClick={() => navigate(`/agrar/saatgut-stamm/${id}`)}>
              <Pencil className="w-4 h-4 mr-2" />
              Bearbeiten
            </Button>
          ) : (
            <>
              <Button variant="outline" onClick={handleCancel}>
                Abbrechen
              </Button>
              <Button onClick={handleSave} disabled={createMutation.isPending || updateMutation.isPending}>
                <Save className="w-4 h-4 mr-2" />
                {createMutation.isPending || updateMutation.isPending ? 'Speichern...' : 'Speichern'}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Error Messages */}
      {errors.general && (
        <Alert className="mb-6" variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{errors.general}</AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <Card>
        <CardContent className="p-6">
          <Tabs defaultValue="allgemein" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="allgemein">Allgemein</TabsTrigger>
              <TabsTrigger value="zulassungen">Zulassungen</TabsTrigger>
              <TabsTrigger value="agronomie">Agronomie</TabsTrigger>
              <TabsTrigger value="lager">Lager</TabsTrigger>
            </TabsList>

            {/* Allgemein Tab */}
            <TabsContent value="allgemein" className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="artikelnummer">Artikelnummer *</Label>
                  <Input
                    id="artikelnummer"
                    value={formData.artikelnummer}
                    onChange={(e) => handleInputChange('artikelnummer', e.target.value)}
                    readOnly={readOnlyMode}
                    className={errors.artikelnummer ? 'border-red-500' : readOnlyMode ? 'bg-muted' : ''}
                  />
                  {errors.artikelnummer && (
                    <p className="text-sm text-red-500">{errors.artikelnummer}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="name">Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    readOnly={readOnlyMode}
                    className={errors.name ? 'border-red-500' : readOnlyMode ? 'bg-muted' : ''}
                  />
                  {errors.name && (
                    <p className="text-sm text-red-500">{errors.name}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="sorte">Sorte *</Label>
                  <Input
                    id="sorte"
                    value={formData.sorte}
                    onChange={(e) => handleInputChange('sorte', e.target.value)}
                    readOnly={readOnlyMode}
                    className={errors.sorte ? 'border-red-500' : readOnlyMode ? 'bg-muted' : ''}
                  />
                  {errors.sorte && (
                    <p className="text-sm text-red-500">{errors.sorte}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="art">Art *</Label>
                  <NativeSelect
                    value={formData.art}
                    onValueChange={(value) => handleInputChange('art', value)}
                    placeholder="Art auswaehlen"
                    disabled={readOnlyMode}
                    className={errors.art ? 'border-red-500' : readOnlyMode ? 'bg-muted' : ''}
                    options={[
                      { value: 'Weizen', label: 'Weizen' },
                      { value: 'Gerste', label: 'Gerste' },
                      { value: 'Roggen', label: 'Roggen' },
                      { value: 'Hafer', label: 'Hafer' },
                      { value: 'Mais', label: 'Mais' },
                      { value: 'Raps', label: 'Raps' },
                      { value: 'Sonstige', label: 'Sonstige' },
                    ]}
                  />
                  {errors.art && (
                    <p className="text-sm text-red-500">{errors.art}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="zuechter">Züchter</Label>
                  <Input
                    id="zuechter"
                    value={formData.zuechter}
                    onChange={(e) => handleInputChange('zuechter', e.target.value)}
                    readOnly={readOnlyMode}
                    className={readOnlyMode ? 'bg-muted' : ''}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="zulassungsnummer">Zulassungsnummer</Label>
                  <Input
                    id="zulassungsnummer"
                    value={formData.zulassungsnummer}
                    onChange={(e) => handleInputChange('zulassungsnummer', e.target.value)}
                    readOnly={readOnlyMode}
                    className={readOnlyMode ? 'bg-muted' : ''}
                  />
                </div>
              </div>
            </TabsContent>

            {/* Zulassungen Tab */}
            <TabsContent value="zulassungen" className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="bsa_zulassung"
                      checked={formData.bsa_zulassung}
                      onChange={(e) => handleInputChange('bsa_zulassung', e.target.checked)}
                      disabled={readOnlyMode}
                      className="rounded"
                    />
                    <Label htmlFor="bsa_zulassung" className="flex items-center gap-2">
                      {formData.bsa_zulassung ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-gray-400" />
                      )}
                      BSA-Zulassung
                    </Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="eu_zulassung"
                      checked={formData.eu_zulassung}
                      onChange={(e) => handleInputChange('eu_zulassung', e.target.checked)}
                      disabled={readOnlyMode}
                      className="rounded"
                    />
                    <Label htmlFor="eu_zulassung" className="flex items-center gap-2">
                      {formData.eu_zulassung ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-gray-400" />
                      )}
                      EU-Zulassung
                    </Label>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ablauf_zulassung">Ablauf Zulassung</Label>
                  <Input
                    id="ablauf_zulassung"
                    type="date"
                    value={formData.ablauf_zulassung ? formData.ablauf_zulassung.toISOString().split('T')[0] : ''}
                    onChange={(e) => handleInputChange('ablauf_zulassung', e.target.value ? new Date(e.target.value) : null)}
                    readOnly={readOnlyMode}
                    className={errors.ablauf_zulassung ? 'border-red-500' : readOnlyMode ? 'bg-muted' : ''}
                  />
                  {errors.ablauf_zulassung && (
                    <p className="text-sm text-red-500">{errors.ablauf_zulassung}</p>
                  )}
                </div>
              </div>

              {/* Zulassungs-Status */}
              <div className="flex gap-2">
                {formData.bsa_zulassung && (
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    BSA-zugelassen
                  </Badge>
                )}
                {formData.eu_zulassung && (
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    EU-zugelassen
                  </Badge>
                )}
                {formData.ablauf_zulassung && (
                  <Badge
                    variant={formData.ablauf_zulassung < new Date() ? "destructive" : "secondary"}
                  >
                    Ablauf: {format(formData.ablauf_zulassung, 'dd.MM.yyyy', { locale: de })}
                  </Badge>
                )}
              </div>
            </TabsContent>

            {/* Agronomie Tab */}
            <TabsContent value="agronomie" className="space-y-6">
              <div className="grid grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="tkm">TKM (Tausendkornmasse)</Label>
                  <Input
                    id="tkm"
                    type="number"
                    step="0.1"
                    value={formData.tkm || ''}
                    onChange={(e) => handleInputChange('tkm', e.target.value ? parseFloat(e.target.value) : null)}
                    readOnly={readOnlyMode}
                    className={readOnlyMode ? 'bg-muted' : ''}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="keimfaehigkeit">Keimfähigkeit (%)</Label>
                  <Input
                    id="keimfaehigkeit"
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={formData.keimfaehigkeit || ''}
                    onChange={(e) => handleInputChange('keimfaehigkeit', e.target.value ? parseFloat(e.target.value) : null)}
                    readOnly={readOnlyMode}
                    className={errors.keimfaehigkeit ? 'border-red-500' : readOnlyMode ? 'bg-muted' : ''}
                  />
                  {errors.keimfaehigkeit && (
                    <p className="text-sm text-red-500">{errors.keimfaehigkeit}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="aussaatstaerke">Aussaatstärke (kg/ha)</Label>
                  <Input
                    id="aussaatstaerke"
                    type="number"
                    step="0.1"
                    value={formData.aussaatstaerke || ''}
                    onChange={(e) => handleInputChange('aussaatstaerke', e.target.value ? parseFloat(e.target.value) : null)}
                    readOnly={readOnlyMode}
                    className={readOnlyMode ? 'bg-muted' : ''}
                  />
                </div>
              </div>
            </TabsContent>

            {/* Lager Tab */}
            <TabsContent value="lager" className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="lagerbestand">Lagerbestand</Label>
                  <Input
                    id="lagerbestand"
                    type="number"
                    step="0.01"
                    value={formData.lagerbestand}
                    onChange={(e) => handleInputChange('lagerbestand', parseFloat(e.target.value) || 0)}
                    readOnly={readOnlyMode}
                    className={readOnlyMode ? 'bg-muted' : ''}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="reserviert">Reserviert</Label>
                  <Input
                    id="reserviert"
                    type="number"
                    step="0.01"
                    value={formData.reserviert}
                    onChange={(e) => handleInputChange('reserviert', parseFloat(e.target.value) || 0)}
                    readOnly={readOnlyMode}
                    className={readOnlyMode ? 'bg-muted' : ''}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Verfügbar</Label>
                  <Input
                    value={(formData.lagerbestand - formData.reserviert).toFixed(2)}
                    readOnly
                    className={readOnlyMode ? 'bg-muted' : 'bg-gray-50'}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lagerort">Lagerort</Label>
                  <Input
                    id="lagerort"
                    value={formData.lagerort}
                    onChange={(e) => handleInputChange('lagerort', e.target.value)}
                    readOnly={readOnlyMode}
                    className={readOnlyMode ? 'bg-muted' : ''}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="ek_preis">EK-Preis</Label>
                  <Input
                    id="ek_preis"
                    type="number"
                    step="0.01"
                    value={formData.ek_preis || ''}
                    onChange={(e) => handleInputChange('ek_preis', e.target.value ? parseFloat(e.target.value) : null)}
                    readOnly={readOnlyMode}
                    className={readOnlyMode ? 'bg-muted' : ''}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="vk_preis">VK-Preis</Label>
                  <Input
                    id="vk_preis"
                    type="number"
                    step="0.01"
                    value={formData.vk_preis || ''}
                    onChange={(e) => handleInputChange('vk_preis', e.target.value ? parseFloat(e.target.value) : null)}
                    readOnly={readOnlyMode}
                    className={readOnlyMode ? 'bg-muted' : ''}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="mindestabnahme">Mindestabnahme</Label>
                  <Input
                    id="mindestabnahme"
                    type="number"
                    step="0.01"
                    value={formData.mindestabnahme || ''}
                    onChange={(e) => handleInputChange('mindestabnahme', e.target.value ? parseFloat(e.target.value) : null)}
                    readOnly={readOnlyMode}
                    className={readOnlyMode ? 'bg-muted' : ''}
                  />
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default SaatgutStammPage;
