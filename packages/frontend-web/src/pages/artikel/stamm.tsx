import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Package, Save } from 'lucide-react'
import { useToast } from '@/components/ui/toast-provider'
import { ErrorState } from '@/components/ErrorState'
import { articleService, type ArticleCreate, type ArticleUpdate } from '@/lib/services/article-service'

type ArtikelData = {
  id: string
  artikelnr: string
  bezeichnung: string
  suchbegriff: string
  hersteller: string
  herkunftsland: string
  naehrwertangaben: string
  warengruppe: string
  mhdErforderlich: boolean
  lagerartikel: boolean
  mwstProzent: number
  gefahrgutklasse: string
  lagerorte: string
  chargenpflicht: boolean
  qsPruefungErforderlich: boolean
  zolltarifnummer: string
  bioKennzeichnung: boolean
  gmpPlusRelevanz: boolean
  lieferantennummer: string
  einheit: string
  vkPreis: number
  ekPreis: number
  bestand: number
  status: 'aktiv' | 'auslaufend'
}

const DEFAULT_ARTIKEL: ArtikelData = {
  id: '',
  artikelnr: '',
  bezeichnung: '',
  suchbegriff: '',
  hersteller: '',
  herkunftsland: 'DE',
  naehrwertangaben: '',
  warengruppe: '',
  mhdErforderlich: false,
  lagerartikel: true,
  mwstProzent: 19,
  gefahrgutklasse: '',
  lagerorte: '',
  chargenpflicht: false,
  qsPruefungErforderlich: false,
  zolltarifnummer: '',
  bioKennzeichnung: false,
  gmpPlusRelevanz: false,
  lieferantennummer: '',
  einheit: 't',
  vkPreis: 0,
  ekPreis: 0,
  bestand: 0,
  status: 'aktiv',
}
const DEFAULT_TENANT_ID = import.meta.env.VITE_TENANT_ID ?? '00000000-0000-0000-0000-000000000001'

function mapApiToForm(article: {
  id: string
  article_number: string
  name: string
  suchbegriff?: string
  hersteller?: string
  herkunftsland?: string
  naehrwertangaben?: string
  mhd_erforderlich?: boolean
  lagerartikel?: boolean
  mehrwertsteuer_prozent?: number
  gefahrgutklasse?: string
  lagerorte?: string[]
  chargenpflicht?: boolean
  qs_pruefung_erforderlich?: boolean
  zolltarifnummer?: string
  bio_kennzeichnung?: boolean
  gmp_plus_relevanz?: boolean
  lieferantennummer?: string
  warengruppe?: string
  category: string
  unit: string
  sales_price: number
  purchase_price?: number
  current_stock: number
  is_active: boolean
}): ArtikelData {
  return {
    id: article.id,
    artikelnr: article.article_number,
    bezeichnung: article.name,
    suchbegriff: article.suchbegriff ?? '',
    hersteller: article.hersteller ?? '',
    herkunftsland: article.herkunftsland ?? 'DE',
    naehrwertangaben: article.naehrwertangaben ?? '',
    warengruppe: article.warengruppe ?? article.category,
    mhdErforderlich: Boolean(article.mhd_erforderlich),
    lagerartikel: article.lagerartikel ?? true,
    mwstProzent: Number(article.mehrwertsteuer_prozent ?? 19),
    gefahrgutklasse: article.gefahrgutklasse ?? '',
    lagerorte: Array.isArray(article.lagerorte) ? article.lagerorte.join(', ') : '',
    chargenpflicht: Boolean(article.chargenpflicht),
    qsPruefungErforderlich: Boolean(article.qs_pruefung_erforderlich),
    zolltarifnummer: article.zolltarifnummer ?? '',
    bioKennzeichnung: Boolean(article.bio_kennzeichnung),
    gmpPlusRelevanz: Boolean(article.gmp_plus_relevanz),
    lieferantennummer: article.lieferantennummer ?? '',
    einheit: article.unit,
    vkPreis: Number(article.sales_price ?? 0),
    ekPreis: Number(article.purchase_price ?? 0),
    bestand: Number(article.current_stock ?? 0),
    status: article.is_active ? 'aktiv' : 'auslaufend',
  }
}

export default function ArtikelStammPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id?: string }>()
  const { push } = useToast()
  const isNew = !id || id === 'neu'

  const [artikel, setArtikel] = useState<ArtikelData>(DEFAULT_ARTIKEL)

  const articleQuery = useQuery({
    queryKey: ['article', id],
    queryFn: async () => articleService.getArticle(String(id)),
    enabled: !isNew,
  })

  useEffect(() => {
    if (!isNew && articleQuery.data) {
      setArtikel(mapApiToForm(articleQuery.data))
    }
  }, [isNew, articleQuery.data])

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (isNew) {
        const payload: ArticleCreate = {
          tenant_id: DEFAULT_TENANT_ID,
          article_number: artikel.artikelnr,
          name: artikel.bezeichnung,
          suchbegriff: artikel.suchbegriff || undefined,
          hersteller: artikel.hersteller || undefined,
          herkunftsland: artikel.herkunftsland || undefined,
          naehrwertangaben: artikel.naehrwertangaben || undefined,
          mhd_erforderlich: artikel.mhdErforderlich,
          lagerartikel: artikel.lagerartikel,
          mehrwertsteuer_prozent: artikel.mwstProzent,
          warengruppe: artikel.warengruppe || undefined,
          gefahrgutklasse: artikel.gefahrgutklasse || undefined,
          lagerorte: artikel.lagerorte
            .split(',')
            .map((value) => value.trim())
            .filter(Boolean),
          chargenpflicht: artikel.chargenpflicht,
          qs_pruefung_erforderlich: artikel.qsPruefungErforderlich,
          zolltarifnummer: artikel.zolltarifnummer || undefined,
          bio_kennzeichnung: artikel.bioKennzeichnung,
          gmp_plus_relevanz: artikel.gmpPlusRelevanz,
          lieferantennummer: artikel.lieferantennummer || undefined,
          unit: artikel.einheit,
          category: artikel.warengruppe || 'Sonstige',
          purchase_price: artikel.ekPreis,
          sales_price: artikel.vkPreis,
        }
        return articleService.createArticle(payload)
      }
      const payload: ArticleUpdate = {
        article_number: artikel.artikelnr,
        name: artikel.bezeichnung,
        suchbegriff: artikel.suchbegriff || undefined,
        hersteller: artikel.hersteller || undefined,
        herkunftsland: artikel.herkunftsland || undefined,
        naehrwertangaben: artikel.naehrwertangaben || undefined,
        mhd_erforderlich: artikel.mhdErforderlich,
        lagerartikel: artikel.lagerartikel,
        mehrwertsteuer_prozent: artikel.mwstProzent,
        warengruppe: artikel.warengruppe || undefined,
        gefahrgutklasse: artikel.gefahrgutklasse || undefined,
        lagerorte: artikel.lagerorte
          .split(',')
          .map((value) => value.trim())
          .filter(Boolean),
        chargenpflicht: artikel.chargenpflicht,
        qs_pruefung_erforderlich: artikel.qsPruefungErforderlich,
        zolltarifnummer: artikel.zolltarifnummer || undefined,
        bio_kennzeichnung: artikel.bioKennzeichnung,
        gmp_plus_relevanz: artikel.gmpPlusRelevanz,
        lieferantennummer: artikel.lieferantennummer || undefined,
        unit: artikel.einheit,
        category: artikel.warengruppe || 'Sonstige',
        purchase_price: artikel.ekPreis,
        sales_price: artikel.vkPreis,
        is_active: artikel.status === 'aktiv',
      }
      return articleService.updateArticle(String(id), payload)
    },
    onSuccess: (saved) => {
      push('Artikel gespeichert')
      navigate(`/artikel/${saved.id}`)
    },
    onError: (error) => {
      const message = error instanceof Error ? error.message : 'Speichern fehlgeschlagen'
      push(message)
    },
  })

  const marge = artikel.vkPreis > 0 ? ((artikel.vkPreis - artikel.ekPreis) / artikel.vkPreis) * 100 : 0

  if (articleQuery.isError) {
    return <ErrorState error={articleQuery.error as Error} onRetry={() => { void articleQuery.refetch() }} />
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Package className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{artikel.bezeichnung || 'Neuer Artikel'}</h1>
              <p className="text-muted-foreground">Artikel-Nr.: {artikel.artikelnr}</p>
            </div>
          </div>
        </div>
        <Button
          className="gap-2"
          onClick={() => {
            void saveMutation.mutateAsync()
          }}
          disabled={saveMutation.isPending || articleQuery.isLoading}
        >
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>

      <Tabs defaultValue="stammdaten">
        <TabsList>
          <TabsTrigger value="stammdaten">Stammdaten</TabsTrigger>
          <TabsTrigger value="preise">Preise</TabsTrigger>
          <TabsTrigger value="bestand">Bestand</TabsTrigger>
        </TabsList>

        <TabsContent value="stammdaten">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Grunddaten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Artikelnummer</Label>
                  <Input
                    value={artikel.artikelnr}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, artikelnr: e.target.value }))}
                    className="font-mono font-bold"
                  />
                </div>
                <div>
                  <Label>Bezeichnung</Label>
                  <Input
                    value={artikel.bezeichnung}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, bezeichnung: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Suchbegriff</Label>
                  <Input
                    value={artikel.suchbegriff}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, suchbegriff: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Warengruppe</Label>
                  <Input
                    value={artikel.warengruppe}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, warengruppe: e.target.value }))}
                  />
                </div>
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
                    onChange={(e) => setArtikel((prev) => ({ ...prev, herkunftsland: e.target.value.toUpperCase() }))}
                  />
                </div>
                <div>
                  <Label>Lieferantennummer</Label>
                  <Input
                    value={artikel.lieferantennummer}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, lieferantennummer: e.target.value }))}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Einheiten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Einheit</Label>
                  <Input
                    value={artikel.einheit}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, einheit: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Lagerorte (kommagetrennt)</Label>
                  <Input
                    value={artikel.lagerorte}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, lagerorte: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Gefahrgutklasse</Label>
                  <Input
                    value={artikel.gefahrgutklasse}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, gefahrgutklasse: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Zolltarifnummer</Label>
                  <Input
                    value={artikel.zolltarifnummer}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, zolltarifnummer: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Status</Label>
                  <div className="mt-2">
                    <Badge variant={artikel.status === 'aktiv' ? 'outline' : 'secondary'}>
                      {artikel.status === 'aktiv' ? 'Aktiv' : 'Auslaufend'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="preise">
          <Card>
            <CardHeader>
              <CardTitle>Preisinformationen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Verkaufspreis (EUR/{artikel.einheit})</Label>
                  <Input
                    type="number"
                    value={artikel.vkPreis}
                    step="0.01"
                    onChange={(e) => setArtikel((prev) => ({ ...prev, vkPreis: Number(e.target.value || 0) }))}
                  />
                </div>
                <div>
                  <Label>Einkaufspreis (EUR/{artikel.einheit})</Label>
                  <Input
                    type="number"
                    value={artikel.ekPreis}
                    step="0.01"
                    onChange={(e) => setArtikel((prev) => ({ ...prev, ekPreis: Number(e.target.value || 0) }))}
                  />
                </div>
                <div>
                  <Label>Mehrwertsteuer %</Label>
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
                    <div className="text-3xl font-bold">{marge.toFixed(1)}%</div>
                  </div>
                  <Badge variant={marge > 20 ? 'outline' : 'secondary'} className="text-lg px-4 py-2">
                    {marge > 20 ? 'Gut' : 'Niedrig'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bestand">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div>
                <Label>Aktueller Bestand</Label>
                <div className="mt-2 text-3xl font-bold">
                  {artikel.bestand.toLocaleString('de-DE')} {artikel.einheit}
                </div>
              </div>
              <div>
                <Label>Lagerwert</Label>
                <div className="mt-2 text-2xl font-bold text-blue-600">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(
                    artikel.bestand * artikel.ekPreis,
                  )}
                </div>
              </div>
              <div className="grid gap-2 sm:grid-cols-2">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={artikel.mhdErforderlich}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, mhdErforderlich: e.target.checked }))}
                  />
                  MHD erforderlich
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
                  QS-Pruefung erforderlich
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={artikel.bioKennzeichnung}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, bioKennzeichnung: e.target.checked }))}
                  />
                  Bio-Kennzeichnung
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={artikel.gmpPlusRelevanz}
                    onChange={(e) => setArtikel((prev) => ({ ...prev, gmpPlusRelevanz: e.target.checked }))}
                  />
                  GMP+ relevant
                </label>
              </div>
              <div>
                <Label>Naehrwertangaben</Label>
                <Input
                  value={artikel.naehrwertangaben}
                  onChange={(e) => setArtikel((prev) => ({ ...prev, naehrwertangaben: e.target.value }))}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
