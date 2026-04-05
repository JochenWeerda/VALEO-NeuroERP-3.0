/**
 * Article Master Data Page (Artikel-Stammdaten)
 * Comprehensive article management with all required tabs based on templates:
 * - Stammdaten (Master Data)
 * - Gefahrgut (Dangerous Goods)
 * - Kennzeichnung (Labeling)
 * - LH/Lager (Storage)
 * - Suche (Search)
 * - Unterlagen (Documents)
 * - Lieferanten (Suppliers)
 * - Preise (Prices)
 * - Rabatt (Discounts)
 * - Analyse (Analysis)
 * - Einstellungen (Settings)
 */

import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  Package,
  Save,
  Truck,
  FileText,
  DollarSign,
  Percent,
  Search,
  Settings,
  AlertTriangle,
  Thermometer,
  TestTube,
  Leaf,
  Warehouse,
  Plus,
  Trash2,
  Upload,
  Download,
  Edit,
} from 'lucide-react'
import { useToast } from '@/components/ui/toast-provider'
import { ErrorState } from '@/components/ErrorState'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { NativeSelect } from '@/components/ui/native-select'
import {
  articleService,
  type Article,
  type ArticleCreate,
  type ArticleUpdate,
  type ArticleSupplier,
  type ArticleDiscount,
  type ArticlePrice,
  type ArticleDocument,
} from '@/lib/services/article-service'
import { getAxiosErrorMessage } from '@/lib/api-client'

// ============================================================================
// Type Definitions
// ============================================================================

type ArtikelData = {
  // Basic Fields
  id: string
  artikelnr: string
  bezeichnung: string
  beschreibung: string
  beschreibung2: string
  kurzbezeichnung: string
  suchbegriff: string
  matchcode2: string
  hersteller: string
  herkunftsland: string
  naehrwertangaben: string
  warengruppe: string
  kategorie: string
  unterkategorie: string
  einheit: string
  barcode: string
  // Status
  status: 'aktiv' | 'auslaufend'
  // Stock Management
  mhdErforderlich: boolean
  lagerartikel: boolean
  chargenpflicht: boolean
  qsPruefungErforderlich: boolean
  // Pricing
  mwstProzent: number
  vkPreis: number
  ekPreis: number
  bestand: number
  minBestand: number
  maxBestand: number
  // Dangerous Goods
  gefahrgutklasse: string
  gefahrgutUnNummer: string
  gefahrgutVerpackungsgruppe: string
  gefahrgutAnhaenge: string
  // Labeling
  bioKennzeichnung: boolean
  gmpPlusRelevanz: boolean
  kennzeichnungBio: string
  kennzeichnungVegan: string
  kennzeichnungVegetarisch: string
  kennzeichnungAllergene: string
  kennzeichnungHerkunft: string
  // Storage
  lagerorte: string
  lagerMinTemperatur: number
  lagerMaxTemperatur: number
  lagerLagerdauerTage: number
  lagerZentral: boolean
  lagerSilo: boolean
  // Additional
  zolltarifnummer: string
  lieferantennummer: string
  kundenArtikelnummer: string
  gewicht: number
  abmessungen: string
  // Analysis
  analyseProtein: number
  analyseFeuchtigkeit: number
  analyseSchadex: number
  analyseFremdstoffe: number
  analyseSonstiges: string
  // Documents & Extended Data
  dokumente: ArticleDocument[]
  lieferanten: ArticleSupplier[]
  rabatte: ArticleDiscount[]
  preise: ArticlePrice[]
}

// ============================================================================
// Default Values
// ============================================================================

const DEFAULT_ARTIKEL: ArtikelData = {
  id: '',
  artikelnr: '',
  bezeichnung: '',
  beschreibung: '',
  beschreibung2: '',
  kurzbezeichnung: '',
  suchbegriff: '',
  matchcode2: '',
  hersteller: '',
  herkunftsland: 'DE',
  naehrwertangaben: '',
  warengruppe: '',
  kategorie: 'Sonstige',
  unterkategorie: '',
  einheit: 't',
  barcode: '',
  status: 'aktiv',
  mhdErforderlich: false,
  lagerartikel: true,
  chargenpflicht: false,
  qsPruefungErforderlich: false,
  mwstProzent: 19,
  vkPreis: 0,
  ekPreis: 0,
  bestand: 0,
  minBestand: 0,
  maxBestand: 0,
  gefahrgutklasse: '',
  gefahrgutUnNummer: '',
  gefahrgutVerpackungsgruppe: '',
  gefahrgutAnhaenge: '',
  bioKennzeichnung: false,
  gmpPlusRelevanz: false,
  kennzeichnungBio: '',
  kennzeichnungVegan: '',
  kennzeichnungVegetarisch: '',
  kennzeichnungAllergene: '',
  kennzeichnungHerkunft: '',
  lagerorte: '',
  lagerMinTemperatur: -20,
  lagerMaxTemperatur: 40,
  lagerLagerdauerTage: 0,
  lagerZentral: false,
  lagerSilo: false,
  zolltarifnummer: '',
  lieferantennummer: '',
  kundenArtikelnummer: '',
  gewicht: 0,
  abmessungen: '',
  analyseProtein: 0,
  analyseFeuchtigkeit: 0,
  analyseSchadex: 0,
  analyseFremdstoffe: 0,
  analyseSonstiges: '',
  dokumente: [],
  lieferanten: [],
  rabatte: [],
  preise: [],
}

const DEFAULT_TENANT_ID = import.meta.env.VITE_TENANT_ID ?? '00000000-0000-0000-0000-000000000001'

const statusOptions = [
  { value: 'aktiv', label: 'Aktiv' },
  { value: 'auslaufend', label: 'Auslaufend' },
]

const kategorieOptions = [
  { value: 'Saatgut', label: 'Saatgut' },
  { value: 'Duenger', label: 'Duenger' },
  { value: 'PSM', label: 'Pflanzenschutzmittel' },
  { value: 'Biostimulanzien', label: 'Biostimulanzien' },
  { value: 'Futtermittel', label: 'Futtermittel' },
  { value: 'Silo', label: 'Silo' },
  { value: 'Sonstige', label: 'Sonstige' },
]

const einheitOptions = [
  { value: 't', label: 'Tonne (t)' },
  { value: 'kg', label: 'Kilogramm (kg)' },
  { value: 'l', label: 'Liter (l)' },
  { value: 'Stk', label: 'Stueck (Stk)' },
  { value: 'ha', label: 'Hektar (ha)' },
]

const gefahrgutKlasseOptions = [
  { value: 'Klasse 1', label: 'Klasse 1 - Explosivstoffe' },
  { value: 'Klasse 2', label: 'Klasse 2 - Gase' },
  { value: 'Klasse 3', label: 'Klasse 3 - Entzuendbare Fluessigkeiten' },
  { value: 'Klasse 4', label: 'Klasse 4 - Entzuendbare Feststoffe' },
  { value: 'Klasse 5', label: 'Klasse 5 - Oxidierende Mittel' },
  { value: 'Klasse 6', label: 'Klasse 6 - Giftige Stoffe' },
  { value: 'Klasse 7', label: 'Klasse 7 - Radioaktive Stoffe' },
  { value: 'Klasse 8', label: 'Klasse 8 - Aetzende Stoffe' },
  { value: 'Klasse 9', label: 'Klasse 9 - Verschiedene gefaehrliche Stoffe' },
]

const verpackungsgruppeOptions = [
  { value: 'I', label: 'I - Grosser Gefahr' },
  { value: 'II', label: 'II - Mittlerer Gefahr' },
  { value: 'III', label: 'III - Geringer Gefahr' },
]

const bioKennzeichnungOptions = [
  { value: 'EU-Bio', label: 'EU-Bio' },
  { value: 'Demo', label: 'Demo' },
  { value: 'Bio', label: 'Bio' },
  { value: 'Konventionell', label: 'Konventionell' },
]

const jaNeinUnbekanntOptions = [
  { value: 'Ja', label: 'Ja' },
  { value: 'Nein', label: 'Nein' },
  { value: 'Unbekannt', label: 'Unbekannt' },
]

// ============================================================================
// Helper Functions
// ============================================================================

function mapApiToForm(article: Article): ArtikelData {
  return {
    // Basic Fields
    id: article.id,
    artikelnr: article.article_number,
    bezeichnung: article.name,
    beschreibung: article.description ?? '',
    beschreibung2: article.description2 ?? '',
    kurzbezeichnung: article.short_description ?? '',
    suchbegriff: article.suchbegriff ?? '',
    matchcode2: article.matchcode2 ?? '',
    hersteller: article.hersteller ?? '',
    herkunftsland: article.herkunftsland ?? 'DE',
    naehrwertangaben: article.naehrwertangaben ?? '',
    warengruppe: article.warengruppe ?? '',
    kategorie: article.category ?? 'Sonstige',
    unterkategorie: article.subcategory ?? '',
    einheit: article.unit,
    barcode: article.barcode ?? '',
    // Status
    status: article.is_active ? 'aktiv' : 'auslaufend',
    // Stock Management
    mhdErforderlich: Boolean(article.mhd_erforderlich),
    lagerartikel: article.lagerartikel ?? true,
    chargenpflicht: Boolean(article.chargenpflicht),
    qsPruefungErforderlich: Boolean(article.qs_pruefung_erforderlich),
    // Pricing
    mwstProzent: Number(article.mehrwertsteuer_prozent ?? 19),
    vkPreis: Number(article.sales_price ?? 0),
    ekPreis: Number(article.purchase_price ?? 0),
    bestand: Number(article.current_stock ?? 0),
    minBestand: Number(article.min_stock ?? 0),
    maxBestand: Number(article.max_stock ?? 0),
    // Dangerous Goods
    gefahrgutklasse: article.gefahrgutklasse ?? '',
    gefahrgutUnNummer: article.gefahrgut_un_nummer ?? '',
    gefahrgutVerpackungsgruppe: article.gefahrgut_verpackungsgruppe ?? '',
    gefahrgutAnhaenge: article.gefahrgut_anhaenge ?? '',
    // Labeling
    bioKennzeichnung: Boolean(article.bio_kennzeichnung),
    gmpPlusRelevanz: Boolean(article.gmp_plus_relevanz),
    kennzeichnungBio: article.kennzeichnung_bio ?? '',
    kennzeichnungVegan: article.kennzeichnung_vegan ?? '',
    kennzeichnungVegetarisch: article.kennzeichnung_vegetarisch ?? '',
    kennzeichnungAllergene: article.kennzeichnung_allergene ?? '',
    kennzeichnungHerkunft: article.kennzeichnung_herkunft ?? '',
    // Storage
    lagerorte: Array.isArray(article.lagerorte) ? article.lagerorte.join(', ') : '',
    lagerMinTemperatur: article.lager_min_temperatur ?? -20,
    lagerMaxTemperatur: article.lager_max_temperatur ?? 40,
    lagerLagerdauerTage: article.lager_lagerdauer_tage ?? 0,
    lagerZentral: Boolean(article.lager_zentral),
    lagerSilo: Boolean(article.lager_silo),
    // Additional
    zolltarifnummer: article.zolltarifnummer ?? '',
    lieferantennummer: article.lieferantennummer ?? '',
    kundenArtikelnummer: article.customer_article_number ?? '',
    gewicht: Number(article.weight ?? 0),
    abmessungen: article.dimensions ?? '',
    // Analysis
    analyseProtein: article.analyse_protein ?? 0,
    analyseFeuchtigkeit: article.analyse_feuchtigkeit ?? 0,
    analyseSchadex: article.analyse_schadex ?? 0,
    analyseFremdstoffe: article.analyse_fremdstoffe ?? 0,
    analyseSonstiges: article.analyse_sonstiges ?? '',
    // Extended data (will be loaded separately)
    dokumente: [],
    lieferanten: [],
    rabatte: [],
    preise: [],
  }
}

// ============================================================================
// Main Component
// ============================================================================

export default function ArtikelStammPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id?: string }>()
  const { push } = useToast()
  const isNew = !id || id === 'neu'

  const [artikel, setArtikel] = useState<ArtikelData>(DEFAULT_ARTIKEL)

  // Query for loading article data
  const articleQuery = useQuery({
    queryKey: ['article', id],
    queryFn: async () => articleService.getArticle(String(id)),
    enabled: !isNew,
  })

  // Load extended data (suppliers, discounts, prices) using articleService
  const suppliersQuery = useQuery({
    queryKey: ['article-suppliers', id],
    queryFn: async () => articleService.getArticleSuppliers(String(id)),
    enabled: !isNew && !!id,
  })

  const discountsQuery = useQuery({
    queryKey: ['article-discounts', id],
    queryFn: async () => articleService.getArticleDiscounts(String(id)),
    enabled: !isNew && !!id,
  })

  const pricesQuery = useQuery({
    queryKey: ['article-prices', id],
    queryFn: async () => articleService.getArticlePrices(String(id)),
    enabled: !isNew && !!id,
  })

  const documentsQuery = useQuery({
    queryKey: ['article-documents', id],
    queryFn: async () => articleService.getArticleDocuments(String(id)),
    enabled: !isNew && !!id,
  })

  // Update form when data loads
  useEffect(() => {
    if (!isNew && articleQuery.data) {
      const mapped = mapApiToForm(articleQuery.data)
      setArtikel((prev) => ({ ...prev, ...mapped }))
    }
  }, [isNew, articleQuery.data])

  // Update extended data when queries complete
  useEffect(() => {
    if (suppliersQuery.data) {
      setArtikel((prev) => ({ ...prev, lieferanten: suppliersQuery.data ?? [] }))
    }
  }, [suppliersQuery.data])

  useEffect(() => {
    if (discountsQuery.data) {
      setArtikel((prev) => ({ ...prev, rabatte: discountsQuery.data ?? [] }))
    }
  }, [discountsQuery.data])

  useEffect(() => {
    if (pricesQuery.data) {
      setArtikel((prev) => ({ ...prev, preise: pricesQuery.data ?? [] }))
    }
  }, [pricesQuery.data])

  useEffect(() => {
    if (documentsQuery.data) {
      setArtikel((prev) => ({ ...prev, dokumente: documentsQuery.data ?? [] }))
    }
  }, [documentsQuery.data])

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: async () => {
      const basePayload = {
        // Basic
        article_number: artikel.artikelnr,
        name: artikel.bezeichnung,
        description: artikel.beschreibung || undefined,
        description2: artikel.beschreibung2 || undefined,
        short_description: artikel.kurzbezeichnung || undefined,
        suchbegriff: artikel.suchbegriff || undefined,
        matchcode2: artikel.matchcode2 || undefined,
        hersteller: artikel.hersteller || undefined,
        herkunftsland: artikel.herkunftsland || undefined,
        naehrwertangaben: artikel.naehrwertangaben || undefined,
        // Classification
        warengruppe: artikel.warengruppe || undefined,
        category: artikel.kategorie,
        subcategory: artikel.unterkategorie || undefined,
        // Identifiers
        barcode: artikel.barcode || undefined,
        supplier_number: artikel.lieferantennummer || undefined,
        customer_article_number: artikel.kundenArtikelnummer || undefined,
        // Stock flags
        mhd_erforderlich: artikel.mhdErforderlich,
        lagerartikel: artikel.lagerartikel,
        chargenpflicht: artikel.chargenpflicht,
        qs_pruefung_erforderlich: artikel.qsPruefungErforderlich,
        // Pricing
        mehrwertsteuer_prozent: artikel.mwstProzent,
        sales_price: artikel.vkPreis,
        purchase_price: artikel.ekPreis,
        min_stock: artikel.minBestand,
        max_stock: artikel.maxBestand,
        // Dangerous Goods
        gefahrgutklasse: artikel.gefahrgutklasse || undefined,
        gefahrgut_un_nummer: artikel.gefahrgutUnNummer || undefined,
        gefahrgut_verpackungsgruppe: artikel.gefahrgutVerpackungsgruppe || undefined,
        gefahrgut_anhaenge: artikel.gefahrgutAnhaenge || undefined,
        // Labeling
        bio_kennzeichnung: artikel.bioKennzeichnung,
        gmp_plus_relevanz: artikel.gmpPlusRelevanz,
        kennzeichnung_bio: artikel.kennzeichnungBio || undefined,
        kennzeichnung_vegan: artikel.kennzeichnungVegan || undefined,
        kennzeichnung_vegetarisch: artikel.kennzeichnungVegetarisch || undefined,
        kennzeichnung_allergene: artikel.kennzeichnungAllergene || undefined,
        kennzeichnung_herkunft: artikel.kennzeichnungHerkunft || undefined,
        // Storage
        lagerorte: artikel.lagerorte
          .split(',')
          .map((v) => v.trim())
          .filter(Boolean),
        lager_min_temperatur: artikel.lagerMinTemperatur,
        lager_max_temperatur: artikel.lagerMaxTemperatur,
        lager_lagerdauer_tage: artikel.lagerLagerdauerTage,
        lager_zentral: artikel.lagerZentral,
        lager_silo: artikel.lagerSilo,
        // Additional
        zolltarifnummer: artikel.zolltarifnummer || undefined,
        unit: artikel.einheit,
        weight: artikel.gewicht,
        dimensions: artikel.abmessungen || undefined,
        // Analysis
        analyse_protein: artikel.analyseProtein,
        analyse_feuchtigkeit: artikel.analyseFeuchtigkeit,
        analyse_schadex: artikel.analyseSchadex,
        analyse_fremdstoffe: artikel.analyseFremdstoffe,
        analyse_sonstiges: artikel.analyseSonstiges || undefined,
        // Status
        is_active: artikel.status === 'aktiv',
      }

      if (isNew) {
        const payload: ArticleCreate = {
          tenant_id: DEFAULT_TENANT_ID,
          ...basePayload,
        }
        return articleService.createArticle(payload)
      }
      const payload: ArticleUpdate = basePayload
      return articleService.updateArticle(String(id), payload)
    },
    onSuccess: (saved) => {
      push('Artikel gespeichert')
      navigate(`/artikel/${saved.id}`)
    },
    onError: (error) => {
      push(getAxiosErrorMessage(error))
    },
  })

  // Calculate margin
  const marge = artikel.vkPreis > 0 ? ((artikel.vkPreis - artikel.ekPreis) / artikel.vkPreis) * 100 : 0
  const lagerwert = artikel.bestand * artikel.ekPreis

  // Error state
  if (articleQuery.isError) {
    return <ErrorState error={articleQuery.error as Error} onRetry={() => { void articleQuery.refetch() }} />
  }

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Package className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">{artikel.bezeichnung || 'Neuer Artikel'}</h1>
            <p className="text-muted-foreground">Artikel-Nr.: {artikel.artikelnr}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Badge variant={artikel.status === 'aktiv' ? 'outline' : 'secondary'} className="text-sm">
            {artikel.status === 'aktiv' ? 'Aktiv' : 'Auslaufend'}
          </Badge>
          <Button
            onClick={() => {
              void saveMutation.mutateAsync()
            }}
            disabled={saveMutation.isPending || articleQuery.isLoading}
          >
            <Save className="h-4 w-4" />
            Speichern
          </Button>
        </div>
      </div>

      {/* Main Tabs */}
      <Tabs defaultValue="stammdaten" className="w-full">
        <TabsList className="flex flex-wrap">
          <TabsTrigger value="stammdaten">Stammdaten</TabsTrigger>
          <TabsTrigger value="gefahrgut">Gefahrgut</TabsTrigger>
          <TabsTrigger value="kennzeichnung">Kennzeichnung</TabsTrigger>
          <TabsTrigger value="lager">Lager/LH</TabsTrigger>
          <TabsTrigger value="suche">Suche</TabsTrigger>
          <TabsTrigger value="unterlagen">Unterlagen</TabsTrigger>
          <TabsTrigger value="lieferanten">Lieferanten</TabsTrigger>
          <TabsTrigger value="preise">Preise</TabsTrigger>
          <TabsTrigger value="rabatt">Rabatt</TabsTrigger>
          <TabsTrigger value="analyse">Analyse</TabsTrigger>
          <TabsTrigger value="einstellungen">Einstellungen</TabsTrigger>
        </TabsList>

        {/* ========================================================================== */}
        {/* Tab: Stammdaten (Master Data) */}
        {/* ========================================================================== */}
        <TabsContent value="stammdaten">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Basic Data Card */}
            <Card>
              <CardHeader>
                <CardTitle>Grunddaten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label>Artikelnummer *</Label>
                    <Input
                      value={artikel.artikelnr}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, artikelnr: e.target.value }))}
                      className="font-mono font-bold"
                    />
                  </div>
                  <div>
                    <Label>Status</Label>
                    <NativeSelect
                      value={artikel.status}
                      onValueChange={(value) =>
                        setArtikel((prev) => ({ ...prev, status: value as ArtikelData['status'] }))
                      }
                      options={statusOptions}
                    />
                  </div>
                </div>
                <div>
                  <Label>Bezeichnung *</Label>
                  <Input
                    value={artikel.bezeichnung}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, bezeichnung: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Kurzbezeichnung</Label>
                  <Input
                    value={artikel.kurzbezeichnung}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, kurzbezeichnung: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Beschreibung</Label>
                  <Textarea
                    value={artikel.beschreibung}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, beschreibung: e.target.value }))}
                    rows={3}
                  />
                </div>
                <div>
                  <Label>Zweite Bezeichnung</Label>
                  <Textarea
                    value={artikel.beschreibung2}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, beschreibung2: e.target.value }))}
                    rows={2}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Classification Card */}
            <Card>
              <CardHeader>
                <CardTitle>Klassifikation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label>Warengruppe</Label>
                    <Input
                      value={artikel.warengruppe}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, warengruppe: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label>Kategorie</Label>
                    <NativeSelect
                      value={artikel.kategorie}
                      onValueChange={(value) => setArtikel((prev) => ({ ...prev, kategorie: value }))}
                      options={kategorieOptions}
                    />
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label>Unterkategorie</Label>
                    <Input
                      value={artikel.unterkategorie}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, unterkategorie: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label>Einheit</Label>
                    <NativeSelect
                      value={artikel.einheit}
                      onValueChange={(value) => setArtikel((prev) => ({ ...prev, einheit: value }))}
                      options={einheitOptions}
                    />
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label>Hersteller</Label>
                    <Input
                      value={artikel.hersteller}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, hersteller: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label>Herkunftsland (ISO)</Label>
                    <Input
                      value={artikel.herkunftsland}
                      onChange={(e) =>
                        setArtikel((prev) => ({ ...prev, herkunftsland: e.target.value.toUpperCase() }))
                      }
                      maxLength={2}
                    />
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label>Barcode/EAN</Label>
                    <Input
                      value={artikel.barcode}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, barcode: e.target.value }))}
                      className="font-mono"
                    />
                  </div>
                  <div>
                    <Label>Zolltarifnummer</Label>
                    <Input
                      value={artikel.zolltarifnummer}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, zolltarifnummer: e.target.value }))}
                      className="font-mono"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Pricing Card */}
            <Card>
              <CardHeader>
                <CardTitle>Preise</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-3">
                  <div>
                    <Label>VK-Preis (EUR/{artikel.einheit})</Label>
                    <Input
                      type="number"
                      value={artikel.vkPreis}
                      step="0.01"
                      onChange={(e) => setArtikel((prev) => ({ ...prev, vkPreis: Number(e.target.value || 0) }))}
                    />
                  </div>
                  <div>
                    <Label>EK-Preis (EUR/{artikel.einheit})</Label>
                    <Input
                      type="number"
                      value={artikel.ekPreis}
                      step="0.01"
                      onChange={(e) => setArtikel((prev) => ({ ...prev, ekPreis: Number(e.target.value || 0) }))}
                    />
                  </div>
                  <div>
                    <Label>MwSt %</Label>
                    <Input
                      type="number"
                      value={artikel.mwstProzent}
                      step="0.01"
                      onChange={(e) => setArtikel((prev) => ({ ...prev, mwstProzent: Number(e.target.value || 0) }))}
                    />
                  </div>
                </div>
                <div className="rounded-lg border p-4 bg-muted">
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="text-sm text-muted-foreground">Handelsspanne</div>
                      <div className="text-2xl font-bold">{marge.toFixed(1)}%</div>
                    </div>
                    <Badge variant={marge > 20 ? 'outline' : 'secondary'}>
                      {marge > 20 ? 'Gut' : 'Niedrig'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Stock Card */}
            <Card>
              <CardHeader>
                <CardTitle>Bestand</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-3">
                  <div>
                    <Label>Aktueller Bestand</Label>
                    <div className="mt-1 text-2xl font-bold">
                      {artikel.bestand.toLocaleString('de-DE')} {artikel.einheit}
                    </div>
                  </div>
                  <div>
                    <Label>Lagerwert</Label>
                    <div className="mt-1 text-xl font-bold text-blue-600">
                      {new Intl.NumberFormat('de-DE', {
                        style: 'currency',
                        currency: 'EUR',
                        maximumFractionDigits: 0,
                      }).format(lagerwert)}
                    </div>
                  </div>
                  <div>
                    <Label>Lieferantennr.</Label>
                    <Input
                      value={artikel.lieferantennummer}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, lieferantennummer: e.target.value }))}
                      className="font-mono"
                    />
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label>Mindestbestand</Label>
                    <Input
                      type="number"
                      value={artikel.minBestand}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, minBestand: Number(e.target.value || 0) }))}
                    />
                  </div>
                  <div>
                    <Label>Maximalbestand</Label>
                    <Input
                      type="number"
                      value={artikel.maxBestand}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, maxBestand: Number(e.target.value || 0) }))}
                    />
                  </div>
                </div>
                <div className="grid gap-2 sm:grid-cols-4">
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={artikel.mhdErforderlich}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, mhdErforderlich: e.target.checked }))}
                    />
                    MHD
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={artikel.lagerartikel}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, lagerartikel: e.target.checked }))}
                    />
                    Lagerartikel
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={artikel.chargenpflicht}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, chargenpflicht: e.target.checked }))}
                    />
                    Chargenpflicht
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={artikel.qsPruefungErforderlich}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, qsPruefungErforderlich: e.target.checked }))}
                    />
                    QS-Pruefung
                  </label>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* ========================================================================== */}
        {/* Tab: Gefahrgut (Dangerous Goods) */}
        {/* ========================================================================== */}
        <TabsContent value="gefahrgut">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                Gefahrgutdaten
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Gefahrgutklasse</Label>
                  <NativeSelect
                    value={artikel.gefahrgutklasse}
                    onValueChange={(value) => setArtikel((prev) => ({ ...prev, gefahrgutklasse: value }))}
                    placeholder="Auswaehlen..."
                    options={gefahrgutKlasseOptions}
                  />
                </div>
                <div>
                  <Label>UN-Nummer</Label>
                  <Input
                    value={artikel.gefahrgutUnNummer}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, gefahrgutUnNummer: e.target.value }))}
                    placeholder="z.B. 1234"
                  />
                </div>
                <div>
                  <Label>Verpackungsgruppe</Label>
                  <NativeSelect
                    value={artikel.gefahrgutVerpackungsgruppe}
                    onValueChange={(value) =>
                      setArtikel((prev) => ({ ...prev, gefahrgutVerpackungsgruppe: value }))
                    }
                    placeholder="Auswaehlen..."
                    options={verpackungsgruppeOptions}
                  />
                </div>
                <div>
                  <Label>Gefahrgut-Anhaenge</Label>
                  <Input
                    value={artikel.gefahrgutAnhaenge}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, gefahrgutAnhaenge: e.target.value }))}
                    placeholder="z.B. Umweltgefaehrlich"
                  />
                </div>
              </div>
              {artikel.gefahrgutklasse && (
                <div className="rounded-lg border border-orange-200 bg-orange-50 p-4">
                  <div className="flex items-center gap-2 text-orange-700">
                    <AlertTriangle className="h-5 w-5" />
                    <span className="font-medium">
                      Achtung: Dieser Artikel ist als Gefahrgut klassifiziert
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-orange-600">
                    Bitte beachten Sie die gesetzlichen Vorschriften fuer Lagerung und Transport.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ========================================================================== */}
        {/* Tab: Kennzeichnung (Labeling) */}
        {/* ========================================================================== */}
        <TabsContent value="kennzeichnung">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Leaf className="h-5 w-5 text-green-500" />
                Kennzeichnung
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Bio-Kennzeichnung</Label>
                  <NativeSelect
                    value={artikel.kennzeichnungBio}
                    onValueChange={(value) => setArtikel((prev) => ({ ...prev, kennzeichnungBio: value }))}
                    placeholder="Auswaehlen..."
                    options={bioKennzeichnungOptions}
                  />
                </div>
                <div className="flex items-center pt-6">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={artikel.bioKennzeichnung}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, bioKennzeichnung: e.target.checked }))}
                    />
                    Bio-Kennzeichnung aktiv
                  </label>
                </div>
                <div>
                  <Label>Vegan</Label>
                  <NativeSelect
                    value={artikel.kennzeichnungVegan}
                    onValueChange={(value) => setArtikel((prev) => ({ ...prev, kennzeichnungVegan: value }))}
                    placeholder="Auswaehlen..."
                    options={jaNeinUnbekanntOptions}
                  />
                </div>
                <div>
                  <Label>Vegetarisch</Label>
                  <NativeSelect
                    value={artikel.kennzeichnungVegetarisch}
                    onValueChange={(value) =>
                      setArtikel((prev) => ({ ...prev, kennzeichnungVegetarisch: value }))
                    }
                    placeholder="Auswaehlen..."
                    options={jaNeinUnbekanntOptions}
                  />
                </div>
                <div>
                  <Label>Herkunftskennzeichnung</Label>
                  <Input
                    value={artikel.kennzeichnungHerkunft}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, kennzeichnungHerkunft: e.target.value }))}
                    placeholder="z.B. Deutschland, EU"
                  />
                </div>
                <div className="flex items-center pt-6">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={artikel.gmpPlusRelevanz}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, gmpPlusRelevanz: e.target.checked }))}
                    />
                    GMP+ relevant
                  </label>
                </div>
              </div>
              <div>
                <Label>Allergene</Label>
                <Textarea
                  value={artikel.kennzeichnungAllergene}
                  onChange={(e) => setArtikel((prev) => ({ ...prev, kennzeichnungAllergene: e.target.value }))}
                  placeholder="Allergenliste z.B. Gluten, Laktose..."
                  rows={3}
                />
              </div>
              <div>
                <Label>Ernaehrungsangaben</Label>
                <Textarea
                  value={artikel.naehrwertangaben}
                  onChange={(e) => setArtikel((prev) => ({ ...prev, naehrwertangaben: e.target.value }))}
                  placeholder="Nahrwerte pro 100g..."
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ========================================================================== */}
        {/* Tab: Lager/LH (Storage) */}
        {/* ========================================================================== */}
        <TabsContent value="lager">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Warehouse className="h-5 w-5 text-blue-500" />
                Lagerhaltung
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Lagerorte (kommagetrennt)</Label>
                  <Input
                    value={artikel.lagerorte}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, lagerorte: e.target.value }))}
                    placeholder="Lager A, Lager B, Silo 1"
                  />
                </div>
                <div>
                  <Label>Lagerdauer (Tage)</Label>
                  <Input
                    type="number"
                    value={artikel.lagerLagerdauerTage}
                    onChange={(e) =>
                      setArtikel((prev) => ({ ...prev, lagerLagerdauerTage: Number(e.target.value || 0) }))
                    }
                  />
                </div>
                <div className="flex items-center gap-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={artikel.lagerZentral}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, lagerZentral: e.target.checked }))}
                    />
                    Zentrallager
                  </label>
                </div>
                <div className="flex items-center gap-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={artikel.lagerSilo}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, lagerSilo: e.target.checked }))}
                    />
                    Silo-Lagerung
                  </label>
                </div>
              </div>
              <div className="rounded-lg border p-4 bg-muted">
                <div className="flex items-center gap-2 mb-4">
                  <Thermometer className="h-5 w-5" />
                  <span className="font-medium">Lagertemperatur</span>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label>Min. Temperatur (°C)</Label>
                    <Input
                      type="number"
                      value={artikel.lagerMinTemperatur}
                      onChange={(e) =>
                        setArtikel((prev) => ({ ...prev, lagerMinTemperatur: Number(e.target.value || 0) }))
                      }
                    />
                  </div>
                  <div>
                    <Label>Max. Temperatur (°C)</Label>
                    <Input
                      type="number"
                      value={artikel.lagerMaxTemperatur}
                      onChange={(e) =>
                        setArtikel((prev) => ({ ...prev, lagerMaxTemperatur: Number(e.target.value || 0) }))
                      }
                    />
                  </div>
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Gewicht (kg)</Label>
                  <Input
                    type="number"
                    value={artikel.gewicht}
                    step="0.001"
                    onChange={(e) => setArtikel((prev) => ({ ...prev, gewicht: Number(e.target.value || 0) }))}
                  />
                </div>
                <div>
                  <Label>Abmessungen (LxBxH)</Label>
                  <Input
                    value={artikel.abmessungen}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, abmessungen: e.target.value }))}
                    placeholder="z.B. 100x50x30 cm"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ========================================================================== */}
        {/* Tab: Suche (Search) */}
        {/* ========================================================================== */}
        <TabsContent value="suche">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                Suchbegriffe / Index
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Suchbegriff</Label>
                  <Input
                    value={artikel.suchbegriff}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, suchbegriff: e.target.value }))}
                    placeholder="Suchbegriff fuer Schnellsuche"
                  />
                </div>
                <div>
                  <Label>Zweiter Matchcode</Label>
                  <Input
                    value={artikel.matchcode2}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, matchcode2: e.target.value }))}
                    placeholder="Zweiter Suchbegriff"
                  />
                </div>
              </div>
              <div>
                <Label>Kunden-Artikelnummer</Label>
                <Input
                  value={artikel.kundenArtikelnummer}
                  onChange={(e) => setArtikel((prev) => ({ ...prev, kundenArtikelnummer: e.target.value }))}
                  placeholder="Kundenspezifische Artikelnummer"
                />
              </div>
              <div className="rounded-lg border p-4 bg-muted">
                <h4 className="font-medium mb-2">Suchindex-Vorschau</h4>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>
                    <strong>Suchbegriffe:</strong> {[artikel.artikelnr, artikel.bezeichnung, artikel.suchbegriff]
                      .filter(Boolean)
                      .join(', ')}
                  </p>
                  <p>
                    <strong>Index-Werte:</strong> {artikel.artikelnr}, {artikel.bezeichnung}, {artikel.suchbegriff}
                    {artikel.matchcode2 ? `, ${artikel.matchcode2}` : ''}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ========================================================================== */}
        {/* Tab: Unterlagen (Documents) */}
        {/* ========================================================================== */}
        <TabsContent value="unterlagen">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Dokumente
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-end">
                <Button variant="outline" size="sm">
                  <Upload className="h-4 w-4 mr-2" />
                  Dokument hochladen
                </Button>
              </div>
              {artikel.dokumente && artikel.dokumente.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Typ</TableHead>
                      <TableHead>Datum</TableHead>
                      <TableHead className="text-right">Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {artikel.dokumente.map((doc) => (
                      <TableRow key={doc.id}>
                        <TableCell>{doc.document_name}</TableCell>
                        <TableCell>{doc.document_type}</TableCell>
                        <TableCell>{new Date(doc.created_at).toLocaleDateString('de-DE')}</TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Keine Dokumente vorhanden</p>
                  <p className="text-sm">Laden Sie Dokumente hoch, um sie hier anzuzeigen</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ========================================================================== */}
        {/* Tab: Lieferanten (Suppliers) */}
        {/* ========================================================================== */}
        <TabsContent value="lieferanten">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Truck className="h-5 w-5" />
                Lieferanten
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-end">
                <Button variant="outline" size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Lieferant hinzufuegen
                </Button>
              </div>
              {artikel.lieferanten && artikel.lieferanten.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Lieferanten-Nr.</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Artikel-Nr.</TableHead>
                      <TableHead>Einkaufspreis</TableHead>
                      <TableHead>Lieferzeit (Tage)</TableHead>
                      <TableHead>Präferiert</TableHead>
                      <TableHead className="text-right">Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {artikel.lieferanten.map((supplier) => (
                      <TableRow key={supplier.id}>
                        <TableCell className="font-mono">{supplier.supplier_number}</TableCell>
                        <TableCell>{supplier.supplier_name}</TableCell>
                        <TableCell className="font-mono">{supplier.supplier_article_number ?? '-'}</TableCell>
                        <TableCell>
                          {supplier.purchase_price
                            ? `${supplier.purchase_price.toFixed(2)} EUR`
                            : '-'}
                        </TableCell>
                        <TableCell>{supplier.lead_time_days ?? '-'}</TableCell>
                        <TableCell>
                          {supplier.is_preferred ? (
                            <Badge variant="outline">Praefentiert</Badge>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
                  <Truck className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Keine Lieferanten zugeordnet</p>
                  <p className="text-sm">Fuegen Sie Lieferanten hinzu, um Einkaufspreise zu verwalten</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ========================================================================== */}
        {/* Tab: Preise (Prices) */}
        {/* ========================================================================== */}
        <TabsContent value="preise">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Preise / Preisvereinbarungen
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-end">
                <Button variant="outline" size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Preisvereinbarung hinzufuegen
                </Button>
              </div>
              {/* Base Price Card */}
              <div className="rounded-lg border p-4">
                <h4 className="font-medium mb-2">Grundpreis</h4>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div>
                    <Label>VK-Preis</Label>
                    <div className="text-xl font-bold">
                      {artikel.vkPreis.toFixed(2)} EUR / {artikel.einheit}
                    </div>
                  </div>
                  <div>
                    <Label>EK-Preis</Label>
                    <div className="text-xl font-bold">
                      {artikel.ekPreis.toFixed(2)} EUR / {artikel.einheit}
                    </div>
                  </div>
                  <div>
                    <Label>MwSt</Label>
                    <div className="text-xl font-bold">{artikel.mwstProzent}%</div>
                  </div>
                </div>
              </div>
              {/* Price Agreements */}
              {artikel.preise && artikel.preise.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Kunde</TableHead>
                      <TableHead>Netto-Preis</TableHead>
                      <TableHead>Preis inkl. Fracht</TableHead>
                      <TableHead> Gueltig ab</TableHead>
                      <TableHead>Gueltig bis</TableHead>
                      <TableHead className="text-right">Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {artikel.preise.map((price) => (
                      <TableRow key={price.id}>
                        <TableCell>{price.customer_name ?? '-'}</TableCell>
                        <TableCell>{price.price_net?.toFixed(2) ?? '-'} EUR</TableCell>
                        <TableCell>{price.price_incl_freight?.toFixed(2) ?? '-'} EUR</TableCell>
                        <TableCell>{price.valid_from ? new Date(price.valid_from).toLocaleDateString('de-DE') : '-'}</TableCell>
                        <TableCell>{price.valid_to ? new Date(price.valid_to).toLocaleDateString('de-DE') : '-'}</TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
                  <DollarSign className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Keine individuellen Preisvereinbarungen</p>
                  <p className="text-sm">Erstellen Sie kundenspezifische Preise</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ========================================================================== */}
        {/* Tab: Rabatt (Discounts) */}
        {/* ========================================================================== */}
        <TabsContent value="rabatt">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Percent className="h-5 w-5" />
                Rabatte
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-end">
                <Button variant="outline" size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Rabatt hinzufuegen
                </Button>
              </div>
              {artikel.rabatte && artikel.rabatte.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Kunde</TableHead>
                      <TableHead>Rabatt %</TableHead>
                      <TableHead>Listen-Nr.</TableHead>
                      <TableHead>Gueltig ab</TableHead>
                      <TableHead>Gueltig bis</TableHead>
                      <TableHead className="text-right">Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {artikel.rabatte.map((discount) => (
                      <TableRow key={discount.id}>
                        <TableCell>{discount.customer_name ?? '-'}</TableCell>
                        <TableCell>
                          <Badge variant={discount.discount_percent > 10 ? 'default' : 'secondary'}>
                            {discount.discount_percent}%
                          </Badge>
                        </TableCell>
                        <TableCell>{discount.discount_list_number ?? '-'}</TableCell>
                        <TableCell>
                          {discount.valid_from ? new Date(discount.valid_from).toLocaleDateString('de-DE') : '-'}
                        </TableCell>
                        <TableCell>
                          {discount.valid_to ? new Date(discount.valid_to).toLocaleDateString('de-DE') : '-'}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
                  <Percent className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Keine Rabatte definiert</p>
                  <p className="text-sm">Erstellen Sie kundenspezifische Rabatte</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ========================================================================== */}
        {/* Tab: Analyse (Analysis) */}
        {/* ========================================================================== */}
        <TabsContent value="analyse">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TestTube className="h-5 w-5 text-purple-500" />
                Analysewerte
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-4">
                <div>
                  <Label>Protein (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={artikel.analyseProtein}
                    onChange={(e) =>
                      setArtikel((prev) => ({ ...prev, analyseProtein: Number(e.target.value || 0) }))
                    }
                  />
                </div>
                <div>
                  <Label>Feuchtigkeit (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={artikel.analyseFeuchtigkeit}
                    onChange={(e) =>
                      setArtikel((prev) => ({ ...prev, analyseFeuchtigkeit: Number(e.target.value || 0) }))
                    }
                  />
                </div>
                <div>
                  <Label>Schadex (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={artikel.analyseSchadex}
                    onChange={(e) =>
                      setArtikel((prev) => ({ ...prev, analyseSchadex: Number(e.target.value || 0) }))
                    }
                  />
                </div>
                <div>
                  <Label>Fremdstoffe (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={artikel.analyseFremdstoffe}
                    onChange={(e) =>
                      setArtikel((prev) => ({ ...prev, analyseFremdstoffe: Number(e.target.value || 0) }))
                    }
                  />
                </div>
              </div>
              <div>
                <Label>Sonstige Analysewerte</Label>
                <Textarea
                  value={artikel.analyseSonstiges}
                  onChange={(e) => setArtikel((prev) => ({ ...prev, analyseSonstiges: e.target.value }))}
                  placeholder="Zusaetzliche Analyseergebnisse..."
                  rows={4}
                />
              </div>
              {/* Analysis Summary */}
              <div className="rounded-lg border p-4 bg-muted">
                <h4 className="font-medium mb-2">Analyseuebersicht</h4>
                <div className="grid gap-2 sm:grid-cols-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{artikel.analyseProtein}%</div>
                    <div className="text-xs text-muted-foreground">Protein</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{artikel.analyseFeuchtigkeit}%</div>
                    <div className="text-xs text-muted-foreground">Feuchtigkeit</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{artikel.analyseSchadex}%</div>
                    <div className="text-xs text-muted-foreground">Schadex</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{artikel.analyseFremdstoffe}%</div>
                    <div className="text-xs text-muted-foreground">Fremdstoffe</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ========================================================================== */}
        {/* Tab: Einstellungen (Settings) */}
        {/* ========================================================================== */}
        <TabsContent value="einstellungen">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Artikel-Einstellungen
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Erstellt am</Label>
                  <div className="text-muted-foreground">
                    {articleQuery.data?.created_at
                      ? new Date(articleQuery.data.created_at).toLocaleString('de-DE')
                      : '-'}
                  </div>
                </div>
                <div>
                  <Label>Zuletzt geaendert</Label>
                  <div className="text-muted-foreground">
                    {articleQuery.data?.updated_at
                      ? new Date(articleQuery.data.updated_at).toLocaleString('de-DE')
                      : '-'}
                  </div>
                </div>
              </div>
              <div className="rounded-lg border p-4">
                <h4 className="font-medium mb-4">Allgemeine Einstellungen</h4>
                <div className="space-y-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={artikel.status === 'aktiv'}
                      onChange={(e) =>
                        setArtikel((prev) => ({ ...prev, status: e.target.checked ? 'aktiv' : 'auslaufend' }))
                      }
                    />
                    Artikel ist aktiv
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={artikel.lagerartikel}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, lagerartikel: e.target.checked }))}
                    />
                    Bestandsfuehrung aktiv
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={artikel.mhdErforderlich}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, mhdErforderlich: e.target.checked }))}
                    />
                    MHD-Pflicht
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={artikel.chargenpflicht}
                      onChange={(e) => setArtikel((prev) => ({ ...prev, chargenpflicht: e.target.checked }))}
                    />
                    Chargenpflicht
                  </label>
                </div>
              </div>
              <div className="rounded-lg border border-red-200 p-4">
                <h4 className="font-medium text-red-600 mb-4">Gefahr</h4>
                <div className="space-y-2">
                  <Button variant="destructive">Artikel loeschen</Button>
                  <p className="text-sm text-muted-foreground">
                    Das Loeschen des Artikels kann nicht rueckgaengig gemacht werden.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
