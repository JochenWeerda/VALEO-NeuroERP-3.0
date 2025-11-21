/**
 * Dünger-Stammdaten Maske
 * ObjectPage für Dünger-Verwaltung mit vollständiger CRUD-Funktionalität
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Save, ArrowLeft, CheckCircle, XCircle, AlertTriangle, Droplets, Shield } from 'lucide-react';
import { toast } from 'sonner';

// API Client
const apiClient = {
  async getDuenger(id: string) {
    const response = await fetch(`/api/v1/agrar/duenger/${id}`);
    if (!response.ok) throw new Error('Failed to fetch Dünger');
    return response.json();
  },

  async createDuenger(data: any) {
    const response = await fetch('/api/v1/agrar/duenger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create Dünger');
    return response.json();
  },

  async updateDuenger(id: string, data: any) {
    const response = await fetch(`/api/v1/agrar/duenger/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update Dünger');
    return response.json();
  },
};

// Form Data Interface
interface DuengerFormData {
  artikelnummer: string;
  name: string;
  typ: string;
  hersteller: string;
  n_gehalt: number | null;
  p_gehalt: number | null;
  k_gehalt: number | null;
  s_gehalt: number | null;
  mg_gehalt: number | null;
  dmv_nummer: string;
  eu_zulassung: string;
  ablauf_zulassung: Date | null;
  gefahrstoff_klasse: string;
  wassergefaehrdend: boolean;
  lagerklasse: string;
  kultur_typ: string;
  dosierung_min: number | null;
  dosierung_max: number | null;
  zeitpunkt: string;
  ek_preis: number | null;
  vk_preis: number | null;
  waehrung: string;
  lagerbestand: number;
  // Compliance - Erklärung des Landwirts für Ausgangsstoffe für Explosivstoffe
  ausgangsstoff_explosivstoffe: boolean;
  erklaerung_landwirt_erforderlich: boolean;
  erklaerung_landwirt_status: string;
}

const DuengerStammPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = !!id;

  // Form State
  const [formData, setFormData] = useState<DuengerFormData>({
    artikelnummer: '',
    name: '',
    typ: '',
    hersteller: '',
    n_gehalt: null,
    p_gehalt: null,
    k_gehalt: null,
    s_gehalt: null,
    mg_gehalt: null,
    dmv_nummer: '',
    eu_zulassung: '',
    ablauf_zulassung: null,
    gefahrstoff_klasse: '',
    wassergefaehrdend: false,
    lagerklasse: '',
    kultur_typ: '',
    dosierung_min: null,
    dosierung_max: null,
    zeitpunkt: '',
    ek_preis: null,
    vk_preis: null,
    waehrung: 'EUR',
    lagerbestand: 0,
    // Compliance - Erklärung des Landwirts für Ausgangsstoffe für Explosivstoffe
    ausgangsstoff_explosivstoffe: false,
    erklaerung_landwirt_erforderlich: false,
    erklaerung_landwirt_status: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Queries
  const { data: duenger, isLoading } = useQuery({
    queryKey: ['duenger', id],
    queryFn: () => apiClient.getDuenger(id ?? ''),
    enabled: isEditing && !!id,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: apiClient.createDuenger,
    onSuccess: () => {
      toast.success('Dünger erfolgreich erstellt');
      queryClient.invalidateQueries({ queryKey: ['duenger'] });
      navigate('/agrar/duenger-liste');
    },
    onError: (error: any) => {
      toast.error(`Fehler beim Erstellen: ${error.message}`);
      if (error.response?.data?.detail) {
        setErrors({ general: error.response.data.detail });
      }
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => apiClient.updateDuenger(id, data),
    onSuccess: () => {
      toast.success('Dünger erfolgreich aktualisiert');
      queryClient.invalidateQueries({ queryKey: ['duenger', id] });
    },
    onError: (error: any) => {
      toast.error(`Fehler beim Aktualisieren: ${error.message}`);
    },
  });

  // Load data when editing
  useEffect(() => {
    if (duenger) {
      setFormData({
        artikelnummer: duenger.artikelnummer || '',
        name: duenger.name || '',
        typ: duenger.typ || '',
        hersteller: duenger.hersteller || '',
        n_gehalt: duenger.n_gehalt || null,
        p_gehalt: duenger.p_gehalt || null,
        k_gehalt: duenger.k_gehalt || null,
        s_gehalt: duenger.s_gehalt || null,
        mg_gehalt: duenger.mg_gehalt || null,
        dmv_nummer: duenger.dmv_nummer || '',
        eu_zulassung: duenger.eu_zulassung || '',
        ablauf_zulassung: duenger.ablauf_zulassung ? new Date(duenger.ablauf_zulassung) : null,
        gefahrstoff_klasse: duenger.gefahrstoff_klasse || '',
        wassergefaehrdend: duenger.wassergefaehrdend || false,
        lagerklasse: duenger.lagerklasse || '',
        kultur_typ: duenger.kultur_typ || '',
        dosierung_min: duenger.dosierung_min || null,
        dosierung_max: duenger.dosierung_max || null,
        zeitpunkt: duenger.zeitpunkt || '',
        ek_preis: duenger.ek_preis || null,
        vk_preis: duenger.vk_preis || null,
        waehrung: duenger.waehrung || 'EUR',
        lagerbestand: duenger.lagerbestand || 0,
        // Compliance - Erklärung des Landwirts für Ausgangsstoffe für Explosivstoffe
        ausgangsstoff_explosivstoffe: duenger.ausgangsstoff_explosivstoffe || false,
        erklaerung_landwirt_erforderlich: duenger.erklaerung_landwirt_erforderlich || false,
        erklaerung_landwirt_status: duenger.erklaerung_landwirt_status || '',
      });
    }
  }, [duenger]);

  // Form Handlers
  const handleInputChange = (field: keyof DuengerFormData, value: any) => {
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
    if (!formData.typ.trim()) {
      newErrors.typ = 'Typ ist erforderlich';
    }

    // NPK validation
    const npkFields = ['n_gehalt', 'p_gehalt', 'k_gehalt', 's_gehalt', 'mg_gehalt'];
    for (const field of npkFields) {
      const value = formData[field as keyof DuengerFormData] as number | null;
      if (value !== null && (value < 0 || value > 100)) {
        newErrors[field] = 'Wert muss zwischen 0 und 100 liegen';
      }
    }

    // Zulassungs-Validierung
    if (formData.ablauf_zulassung && formData.ablauf_zulassung < new Date()) {
      newErrors.ablauf_zulassung = 'Ablaufdatum darf nicht in der Vergangenheit liegen';
    }

    // Dosierung validation
    if (formData.dosierung_min !== null && formData.dosierung_max !== null &&
        formData.dosierung_min > formData.dosierung_max) {
      newErrors.dosierung_min = 'Mindestdosierung darf nicht größer als Höchstdosierung sein';
    }

    // Compliance validation - Ausgangsstoffe für Explosivstoffe
    if (formData.ausgangsstoff_explosivstoffe && !formData.erklaerung_landwirt_erforderlich) {
      newErrors.erklaerung_landwirt_erforderlich = 'Bei Ausgangsstoffen für Explosivstoffe ist eine Landwirt-Erklärung erforderlich';
    }

    if (formData.erklaerung_landwirt_erforderlich && !formData.erklaerung_landwirt_status) {
      newErrors.erklaerung_landwirt_status = 'Status der Landwirt-Erklärung muss angegeben werden';
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
      tenant_id: 'system', // TODO: Get from auth context
    };

    if (isEditing) {
      updateMutation.mutate({ id, data: submitData });
    } else {
      createMutation.mutate(submitData);
    }
  };

  const handleCancel = () => {
    navigate('/agrar/duenger-liste');
  };

  if (isLoading) {
    return <div className="p-6">Laden...</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={handleCancel}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Zurück
          </Button>
          <div>
            <h1 className="text-2xl font-bold">
              {isEditing ? 'Dünger bearbeiten' : 'Neuer Dünger'}
            </h1>
            <p className="text-muted-foreground">
              {isEditing ? `Artikel: ${formData.artikelnummer}` : 'Stammdaten für Dünger anlegen'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleCancel}>
            Abbrechen
          </Button>
          <Button onClick={handleSave} disabled={createMutation.isPending || updateMutation.isPending}>
            <Save className="w-4 h-4 mr-2" />
            {createMutation.isPending || updateMutation.isPending ? 'Speichern...' : 'Speichern'}
          </Button>
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
              <TabsTrigger value="zusammensetzung">Zusammensetzung</TabsTrigger>
              <TabsTrigger value="zulassungen">Zulassungen</TabsTrigger>
              <TabsTrigger value="anwendung">Anwendung</TabsTrigger>
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
                    className={errors.artikelnummer ? 'border-red-500' : ''}
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
                    className={errors.name ? 'border-red-500' : ''}
                  />
                  {errors.name && (
                    <p className="text-sm text-red-500">{errors.name}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="typ">Typ *</Label>
                  <Select value={formData.typ} onValueChange={(value) => handleInputChange('typ', value)}>
                    <SelectTrigger className={errors.typ ? 'border-red-500' : ''}>
                      <SelectValue placeholder="Dünger-Typ auswählen" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Mineraldünger">Mineraldünger</SelectItem>
                      <SelectItem value="Organischer Dünger">Organischer Dünger</SelectItem>
                      <SelectItem value="Organisch-Mineralischer Dünger">Organisch-Mineralischer Dünger</SelectItem>
                      <SelectItem value="Kalkdünger">Kalkdünger</SelectItem>
                      <SelectItem value="Sonstige">Sonstige</SelectItem>
                    </SelectContent>
                  </Select>
                  {errors.typ && (
                    <p className="text-sm text-red-500">{errors.typ}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="hersteller">Hersteller</Label>
                  <Input
                    id="hersteller"
                    value={formData.hersteller}
                    onChange={(e) => handleInputChange('hersteller', e.target.value)}
                  />
                </div>
              </div>
            </TabsContent>

            {/* Zusammensetzung Tab */}
            <TabsContent value="zusammensetzung" className="space-y-6">
              <div className="grid grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="n_gehalt">Stickstoff (N) %</Label>
                  <Input
                    id="n_gehalt"
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={formData.n_gehalt || ''}
                    onChange={(e) => handleInputChange('n_gehalt', e.target.value ? parseFloat(e.target.value) : null)}
                    className={errors.n_gehalt ? 'border-red-500' : ''}
                  />
                  {errors.n_gehalt && (
                    <p className="text-sm text-red-500">{errors.n_gehalt}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="p_gehalt">Phosphor (P₂O₅) %</Label>
                  <Input
                    id="p_gehalt"
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={formData.p_gehalt || ''}
                    onChange={(e) => handleInputChange('p_gehalt', e.target.value ? parseFloat(e.target.value) : null)}
                    className={errors.p_gehalt ? 'border-red-500' : ''}
                  />
                  {errors.p_gehalt && (
                    <p className="text-sm text-red-500">{errors.p_gehalt}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="k_gehalt">Kalium (K₂O) %</Label>
                  <Input
                    id="k_gehalt"
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={formData.k_gehalt || ''}
                    onChange={(e) => handleInputChange('k_gehalt', e.target.value ? parseFloat(e.target.value) : null)}
                    className={errors.k_gehalt ? 'border-red-500' : ''}
                  />
                  {errors.k_gehalt && (
                    <p className="text-sm text-red-500">{errors.k_gehalt}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="s_gehalt">Schwefel (S) %</Label>
                  <Input
                    id="s_gehalt"
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={formData.s_gehalt || ''}
                    onChange={(e) => handleInputChange('s_gehalt', e.target.value ? parseFloat(e.target.value) : null)}
                    className={errors.s_gehalt ? 'border-red-500' : ''}
                  />
                  {errors.s_gehalt && (
                    <p className="text-sm text-red-500">{errors.s_gehalt}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="mg_gehalt">Magnesium (MgO) %</Label>
                  <Input
                    id="mg_gehalt"
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={formData.mg_gehalt || ''}
                    onChange={(e) => handleInputChange('mg_gehalt', e.target.value ? parseFloat(e.target.value) : null)}
                    className={errors.mg_gehalt ? 'border-red-500' : ''}
                  />
                  {errors.mg_gehalt && (
                    <p className="text-sm text-red-500">{errors.mg_gehalt}</p>
                  )}
                </div>
              </div>

              {/* NPK Summary */}
              <Card className="bg-gray-50">
                <CardContent className="p-4">
                  <h4 className="font-semibold mb-2">NPK-Zusammenfassung</h4>
                  <div className="text-sm text-gray-600">
                    N: {formData.n_gehalt || 0}% |
                    P: {formData.p_gehalt || 0}% |
                    K: {formData.k_gehalt || 0}%
                    {(formData.s_gehalt || formData.mg_gehalt) &&
                      ` | S: ${formData.s_gehalt || 0}% | Mg: ${formData.mg_gehalt || 0}%`
                    }
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Zulassungen Tab */}
            <TabsContent value="zulassungen" className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="dmv_nummer">DüMV-Nummer</Label>
                  <Input
                    id="dmv_nummer"
                    value={formData.dmv_nummer}
                    onChange={(e) => handleInputChange('dmv_nummer', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="eu_zulassung">EU-Zulassung</Label>
                  <Input
                    id="eu_zulassung"
                    value={formData.eu_zulassung}
                    onChange={(e) => handleInputChange('eu_zulassung', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ablauf_zulassung">Ablauf Zulassung</Label>
                  <Input
                    id="ablauf_zulassung"
                    type="date"
                    value={formData.ablauf_zulassung ? formData.ablauf_zulassung.toISOString().split('T')[0] : ''}
                    onChange={(e) => handleInputChange('ablauf_zulassung', e.target.value ? new Date(e.target.value) : null)}
                    className={errors.ablauf_zulassung ? 'border-red-500' : ''}
                  />
                  {errors.ablauf_zulassung && (
                    <p className="text-sm text-red-500">{errors.ablauf_zulassung}</p>
                  )}
                </div>
              </div>

              {/* Safety Information */}
              <div className="space-y-4">
                <h4 className="font-semibold">Sicherheitsdaten</h4>
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="gefahrstoff_klasse">Gefahrstoffklasse</Label>
                    <Select value={formData.gefahrstoff_klasse} onValueChange={(value) => handleInputChange('gefahrstoff_klasse', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Gefahrstoffklasse" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">Keine</SelectItem>
                        <SelectItem value="GHS05">GHS05 - Ätzend</SelectItem>
                        <SelectItem value="GHS07">GHS07 - Reizend</SelectItem>
                        <SelectItem value="GHS08">GHS08 - Gesundheitsschädlich</SelectItem>
                        <SelectItem value="GHS09">GHS09 - Umweltgefährlich</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="lagerklasse">Lagerklasse</Label>
                    <Select value={formData.lagerklasse} onValueChange={(value) => handleInputChange('lagerklasse', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Lagerklasse" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1A">1A - Nicht brennbare Flüssigkeiten</SelectItem>
                        <SelectItem value="2">2 - Schwach brennbare Flüssigkeiten</SelectItem>
                        <SelectItem value="3">3 - Normale brennbare Flüssigkeiten</SelectItem>
                        <SelectItem value="4.1">4.1 - Entzündbare Feststoffe</SelectItem>
                        <SelectItem value="4.2">4.2 - Selbstentzündliche Stoffe</SelectItem>
                        <SelectItem value="4.3">4.3 - Stoffe die mit Wasser reagieren</SelectItem>
                        <SelectItem value="5.1">5.1 - Entzündend wirkende Stoffe</SelectItem>
                        <SelectItem value="5.2">5.2 - Organische Peroxide</SelectItem>
                        <SelectItem value="6.1">6.1 - Giftige Stoffe</SelectItem>
                        <SelectItem value="6.2">6.2 - Ansteckungsgefährliche Stoffe</SelectItem>
                        <SelectItem value="8">8 - Ätzende Stoffe</SelectItem>
                        <SelectItem value="9">9 - Verschiedene gefährliche Stoffe</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="wassergefaehrdend"
                    checked={formData.wassergefaehrdend}
                    onChange={(e) => handleInputChange('wassergefaehrdend', e.target.checked)}
                    className="rounded"
                  />
                  <Label htmlFor="wassergefaehrdend" className="flex items-center gap-2">
                    {formData.wassergefaehrdend ? (
                      <Droplets className="w-4 h-4 text-blue-500" />
                    ) : (
                      <Droplets className="w-4 h-4 text-gray-400" />
                    )}
                    Wassergefährdend
                  </Label>
                </div>
              </div>

              {/* Safety Status */}
             <div className="flex gap-2 flex-wrap">
               {formData.gefahrstoff_klasse && (
                 <Badge variant="destructive" className="flex items-center gap-1">
                   <Shield className="w-3 h-3" />
                   {formData.gefahrstoff_klasse}
                 </Badge>
               )}
               {formData.wassergefaehrdend && (
                 <Badge variant="secondary" className="bg-blue-100 text-blue-800 flex items-center gap-1">
                   <Droplets className="w-3 h-3" />
                   Wassergefährdend
                 </Badge>
               )}
               {formData.lagerklasse && (
                 <Badge variant="outline">
                   Lagerklasse {formData.lagerklasse}
                 </Badge>
               )}
             </div>

             {/* Compliance Section - Erklärung des Landwirts für Ausgangsstoffe für Explosivstoffe */}
             <div className="space-y-4 border-t pt-4">
               <h4 className="font-semibold">Compliance - Ausgangsstoffe für Explosivstoffe</h4>
               <div className="grid grid-cols-1 gap-4">
                 <div className="flex items-center space-x-2">
                   <input
                     type="checkbox"
                     id="ausgangsstoff_explosivstoffe"
                     checked={formData.ausgangsstoff_explosivstoffe}
                     onChange={(e) => handleInputChange('ausgangsstoff_explosivstoffe', e.target.checked)}
                     className="rounded"
                   />
                   <Label htmlFor="ausgangsstoff_explosivstoffe" className="flex items-center gap-2">
                     {formData.ausgangsstoff_explosivstoffe ? (
                       <AlertTriangle className="w-4 h-4 text-orange-500" />
                     ) : (
                       <AlertTriangle className="w-4 h-4 text-gray-400" />
                     )}
                     Enthält Ausgangsstoffe für Explosivstoffe
                   </Label>
                 </div>

                 {formData.ausgangsstoff_explosivstoffe && (
                   <>
                     <div className="flex items-center space-x-2">
                       <input
                         type="checkbox"
                         id="erklaerung_landwirt_erforderlich"
                         checked={formData.erklaerung_landwirt_erforderlich}
                         onChange={(e) => handleInputChange('erklaerung_landwirt_erforderlich', e.target.checked)}
                         className="rounded"
                       />
                       <Label htmlFor="erklaerung_landwirt_erforderlich" className="flex items-center gap-2">
                         {formData.erklaerung_landwirt_erforderlich ? (
                           <CheckCircle className="w-4 h-4 text-green-500" />
                         ) : (
                           <XCircle className="w-4 h-4 text-gray-400" />
                         )}
                         Erklärung des Landwirts erforderlich
                       </Label>
                     </div>

                     {formData.erklaerung_landwirt_erforderlich && (
                       <div className="space-y-2">
                         <Label htmlFor="erklaerung_landwirt_status">Status der Erklärung</Label>
                         <Select
                           value={formData.erklaerung_landwirt_status}
                           onValueChange={(value) => handleInputChange('erklaerung_landwirt_status', value)}
                         >
                           <SelectTrigger>
                             <SelectValue placeholder="Status auswählen" />
                           </SelectTrigger>
                           <SelectContent>
                             <SelectItem value="">Nicht eingereicht</SelectItem>
                             <SelectItem value="eingegangen">Eingegangen</SelectItem>
                             <SelectItem value="geprueft">Geprüft</SelectItem>
                             <SelectItem value="abgelehnt">Abgelehnt</SelectItem>
                           </SelectContent>
                         </Select>
                       </div>
                     )}
                   </>
                 )}
               </div>

               {/* Compliance Status Badges */}
               {formData.ausgangsstoff_explosivstoffe && (
                 <div className="flex gap-2 flex-wrap">
                   <Badge variant="destructive" className="flex items-center gap-1">
                     <AlertTriangle className="w-3 h-3" />
                     Explosivstoff-Ausgangsstoff
                   </Badge>
                   {formData.erklaerung_landwirt_erforderlich && (
                     <Badge
                       variant={formData.erklaerung_landwirt_status === 'geprueft' ? 'default' :
                               formData.erklaerung_landwirt_status === 'abgelehnt' ? 'destructive' : 'secondary'}
                       className="flex items-center gap-1"
                     >
                       {formData.erklaerung_landwirt_status === 'geprueft' ? (
                         <CheckCircle className="w-3 h-3" />
                       ) : formData.erklaerung_landwirt_status === 'abgelehnt' ? (
                         <XCircle className="w-3 h-3" />
                       ) : (
                         <AlertTriangle className="w-3 h-3" />
                       )}
                       Landwirt-Erklärung: {
                         formData.erklaerung_landwirt_status === 'eingegangen' ? 'Eingegangen' :
                         formData.erklaerung_landwirt_status === 'geprueft' ? 'Geprüft' :
                         formData.erklaerung_landwirt_status === 'abgelehnt' ? 'Abgelehnt' :
                         'Nicht eingereicht'
                       }
                     </Badge>
                   )}
                 </div>
               )}
             </div>
            </TabsContent>

            {/* Anwendung Tab */}
            <TabsContent value="anwendung" className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="kultur_typ">Kulturtyp</Label>
                  <Select value={formData.kultur_typ} onValueChange={(value) => handleInputChange('kultur_typ', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Kulturtyp auswählen" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Getreide">Getreide</SelectItem>
                      <SelectItem value="Mais">Mais</SelectItem>
                      <SelectItem value="Raps">Raps</SelectItem>
                      <SelectItem value="Grünland">Grünland</SelectItem>
                      <SelectItem value="Gemüse">Gemüse</SelectItem>
                      <SelectItem value="Obst">Obst</SelectItem>
                      <SelectItem value="Alle Kulturen">Alle Kulturen</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="zeitpunkt">Anwendungszeitpunkt</Label>
                  <Input
                    id="zeitpunkt"
                    value={formData.zeitpunkt}
                    onChange={(e) => handleInputChange('zeitpunkt', e.target.value)}
                    placeholder="z.B. Herbst, Frühjahr, vor Aussaat"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="dosierung_min">Mindestdosierung (kg/ha)</Label>
                  <Input
                    id="dosierung_min"
                    type="number"
                    step="0.1"
                    value={formData.dosierung_min || ''}
                    onChange={(e) => handleInputChange('dosierung_min', e.target.value ? parseFloat(e.target.value) : null)}
                    className={errors.dosierung_min ? 'border-red-500' : ''}
                  />
                  {errors.dosierung_min && (
                    <p className="text-sm text-red-500">{errors.dosierung_min}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="dosierung_max">Höchstdosierung (kg/ha)</Label>
                  <Input
                    id="dosierung_max"
                    type="number"
                    step="0.1"
                    value={formData.dosierung_max || ''}
                    onChange={(e) => handleInputChange('dosierung_max', e.target.value ? parseFloat(e.target.value) : null)}
                  />
                </div>
              </div>

              {/* Lager & Preise */}
              <div className="grid grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="lagerbestand">Lagerbestand</Label>
                  <Input
                    id="lagerbestand"
                    type="number"
                    step="0.01"
                    value={formData.lagerbestand}
                    onChange={(e) => handleInputChange('lagerbestand', parseFloat(e.target.value) || 0)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ek_preis">EK-Preis</Label>
                  <Input
                    id="ek_preis"
                    type="number"
                    step="0.01"
                    value={formData.ek_preis || ''}
                    onChange={(e) => handleInputChange('ek_preis', e.target.value ? parseFloat(e.target.value) : null)}
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

export default DuengerStammPage;