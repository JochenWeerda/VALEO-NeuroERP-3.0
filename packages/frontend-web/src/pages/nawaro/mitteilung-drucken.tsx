import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Checkbox } from '@/components/ui/checkbox'
import { useToast } from '@/hooks/use-toast'
import { Eye, Printer, Save, Trash2 } from 'lucide-react'
import { buildCsvArtifact, downloadArtifact, openHtmlPreview } from '@/lib/nawaro-communication'
import {
  createPrintNotification,
  deletePrintNotification,
  listPrintNotifications,
  updatePrintNotification,
  type DeliveryOption,
} from '@/lib/api/nawaro'

const documentOptions = [
  'Ernteerklaerung zum Anbau nachwachsender Rohstoffe',
  'Mitteilung des Aufkaeufers ueber die Lieferung',
] as const

export default function NaWaRoMitteilungDruckenPage(): JSX.Element {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const [selectedId, setSelectedId] = useState<string>('')
  const [documentName, setDocumentName] = useState<string>(documentOptions[0])
  const [ernteJahr, setErnteJahr] = useState<number>(2025)
  const [artikelNr, setArtikelNr] = useState<string>('')
  const [debitorVon, setDebitorVon] = useState<string>('')
  const [debitorBis, setDebitorBis] = useState<string>('')
  const [deliveryOption, setDeliveryOption] = useState<DeliveryOption>('vollstaendige_ablieferung')
  const [formular, setFormular] = useState<string>('W12151')
  const [anzahl, setAnzahl] = useState<number>(1)
  const [drucker, setDrucker] = useState<string>('Groothusen/Kyocera M3540dn Fach 1')

  const notificationsQuery = useQuery({
    queryKey: ['nawaro', 'print-notifications'],
    queryFn: listPrintNotifications,
  })

  useEffect(() => {
    if (!notificationsQuery.data || notificationsQuery.data.length === 0) {
      return
    }
    if (selectedId) {
      return
    }
    const latest = notificationsQuery.data[0]
    setSelectedId(latest.id)
    setDocumentName(latest.document_name)
    setErnteJahr(latest.harvest_year)
    setArtikelNr(latest.article_number ?? '')
    setDebitorVon(latest.debtor_from ?? '')
    setDebitorBis(latest.debtor_to ?? '')
    setDeliveryOption(latest.delivery_option)
    setFormular(latest.form_code)
    setAnzahl(latest.copies)
    setDrucker(latest.printer_name ?? '')
  }, [notificationsQuery.data, selectedId])

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        document_name: documentName,
        harvest_year: ernteJahr,
        article_number: artikelNr || null,
        debtor_from: debitorVon || null,
        debtor_to: debitorBis || null,
        delivery_option: deliveryOption,
        form_code: formular,
        copies: anzahl,
        printer_name: drucker || null,
      }
      if (selectedId) {
        return updatePrintNotification(selectedId, payload)
      }
      return createPrintNotification(payload)
    },
    onSuccess: (saved) => {
      setSelectedId(saved.id)
      toast({ title: 'Gespeichert', description: `Datensatz ${saved.id.slice(0, 8)}` })
      void queryClient.invalidateQueries({ queryKey: ['nawaro', 'print-notifications'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async () => {
      if (!selectedId) {
        return
      }
      await deletePrintNotification(selectedId)
    },
    onSuccess: () => {
      setSelectedId('')
      toast({ title: 'Geloescht' })
      void queryClient.invalidateQueries({ queryKey: ['nawaro', 'print-notifications'] })
    },
  })

  const optionLabel = useMemo(() => {
    switch (deliveryOption) {
      case 'vollstaendige_ablieferung':
        return 'Vollstaendige Ablieferung'
      case 'hoflagerung':
        return 'Hoflagerung beim Erzeuger'
      case 'berichtigung':
        return 'Berichtigung'
      case 'nachmeldung':
        return 'Nachmeldung'
      default:
        return ''
    }
  }, [deliveryOption])

  const communicationSummary = useMemo(
    () => [
      { label: 'Dokument', value: documentName },
      { label: 'Erntejahr', value: String(ernteJahr) },
      { label: 'Artikel', value: artikelNr || '-' },
      { label: 'Debitoren', value: `${debitorVon || '-'} bis ${debitorBis || '-'}` },
      { label: 'Meldungsart', value: optionLabel },
      { label: 'Formular', value: formular },
      { label: 'Drucker', value: drucker || '-' },
    ],
    [artikelNr, debitorBis, debitorVon, documentName, drucker, ernteJahr, formular, optionLabel],
  )

  function clearForm(): void {
    setSelectedId('')
    setDocumentName(documentOptions[0])
    setErnteJahr(2025)
    setArtikelNr('')
    setDebitorVon('')
    setDebitorBis('')
    setDeliveryOption('vollstaendige_ablieferung')
    setFormular('W12151')
    setAnzahl(1)
    setDrucker('Groothusen/Kyocera M3540dn Fach 1')
  }

  function loadRecord(recordId: string): void {
    const item = notificationsQuery.data?.find((entry) => entry.id === recordId)
    if (!item) {
      return
    }
    setSelectedId(item.id)
    setDocumentName(item.document_name)
    setErnteJahr(item.harvest_year)
    setArtikelNr(item.article_number ?? '')
    setDebitorVon(item.debtor_from ?? '')
    setDebitorBis(item.debtor_to ?? '')
    setDeliveryOption(item.delivery_option)
    setFormular(item.form_code)
    setAnzahl(item.copies)
    setDrucker(item.printer_name ?? '')
  }

  const deliveryOptions: Array<{ key: DeliveryOption; label: string }> = [
    { key: 'vollstaendige_ablieferung', label: 'Vollstaendige Ablieferung' },
    { key: 'hoflagerung', label: 'Hoflagerung beim Erzeuger' },
    { key: 'berichtigung', label: 'Berichtigung' },
    { key: 'nachmeldung', label: 'Nachmeldung' },
  ]

  function handlePreview(): void {
    openHtmlPreview(`${documentName} (${formular})`, communicationSummary)
    toast({ title: 'Vorschau erstellt', description: `${documentName} wurde im neuen Fenster geoeffnet.` })
  }

  function handlePrint(): void {
    downloadArtifact({
      fileName: `nawaro-mitteilung-${ernteJahr}-${formular}.txt`,
      content: communicationSummary.map((entry) => `${entry.label}: ${entry.value}`).join('\n'),
    })
    toast({ title: 'Druckartefakt erstellt', description: `Datei fuer ${documentName} wurde heruntergeladen.` })
  }

  function handleExportRecipients(): void {
    const artifact = buildCsvArtifact(
      `nawaro-mitteilung-${ernteJahr}-${formular}-empfaenger.csv`,
      ['Dokument', 'Erntejahr', 'DebitorVon', 'DebitorBis', 'Formular', 'Drucker'],
      [[documentName, ernteJahr, debitorVon || '', debitorBis || '', formular, drucker || '']],
    )
    downloadArtifact(artifact, 'text/csv;charset=utf-8')
    toast({ title: 'Empfaengerliste exportiert', description: 'Der Versand- und Druckkontext wurde als CSV exportiert.' })
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">NaWaRo-Mitteilung drucken</h1>
        <p className="text-muted-foreground">CRUD + DB angebunden</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Gespeicherte Datensaetze</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" onClick={clearForm}>Neu</Button>
            {(notificationsQuery.data ?? []).map((entry) => (
              <Button key={entry.id} variant={entry.id === selectedId ? 'default' : 'outline'} size="sm" onClick={() => loadRecord(entry.id)}>
                {entry.harvest_year} {entry.form_code}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Dokumentdaten</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="document">Dokument</Label>
              <NativeSelect
                value={documentName}
                onValueChange={(value) => setDocumentName(value as (typeof documentOptions)[number])}
                options={documentOptions.map((item) => ({ value: item, label: item }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ernteJahr">Ernte-Jahr</Label>
              <Input id="ernteJahr" type="number" min={2000} max={2100} value={ernteJahr} onChange={(e) => setErnteJahr(Number(e.target.value) || 0)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="artikelNr">Artikel-Nr.</Label>
              <Input id="artikelNr" value={artikelNr} onChange={(e) => setArtikelNr(e.target.value)} />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="debitorVon">Debitor-Kto. von</Label>
                <Input id="debitorVon" value={debitorVon} onChange={(e) => setDebitorVon(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="debitorBis">Debitor-Kto. bis</Label>
                <Input id="debitorBis" value={debitorBis} onChange={(e) => setDebitorBis(e.target.value)} />
              </div>
            </div>
          </div>

          <div className="space-y-3 rounded-md border p-4">
            <p className="text-sm font-medium">Meldungsart</p>
            <div className="grid gap-3 md:grid-cols-2">
              {deliveryOptions.map((option) => (
                <label key={option.key} className="flex items-center gap-2 text-sm">
                  <Checkbox checked={deliveryOption === option.key} onCheckedChange={() => setDeliveryOption(option.key)} />
                  {option.label}
                </label>
              ))}
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="formular">Formular</Label>
              <Input id="formular" value={formular} onChange={(e) => setFormular(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="anzahl">Anzahl</Label>
              <Input id="anzahl" type="number" min={1} value={anzahl} onChange={(e) => setAnzahl(Math.max(1, Number(e.target.value) || 1))} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="drucker">Drucker</Label>
              <Input id="drucker" value={drucker} onChange={(e) => setDrucker(e.target.value)} />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Kommunikations- und Versandbild</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p><span className="font-medium">Dokument:</span> {documentName}</p>
          <p><span className="font-medium">Erntejahr:</span> {ernteJahr}</p>
          <p><span className="font-medium">Artikel:</span> {artikelNr || '-'}</p>
          <p><span className="font-medium">Debitoren:</span> {debitorVon || '-'} bis {debitorBis || '-'}</p>
          <p><span className="font-medium">Option:</span> {optionLabel}</p>
          <p><span className="font-medium">Formular:</span> {formular}</p>
          <p><span className="font-medium">Anzahl:</span> {anzahl}</p>
          <p><span className="font-medium">Drucker:</span> {drucker}</p>
          <div className="rounded border bg-muted/40 p-3">
            <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Naechste Aktion</div>
            <div className="mt-1 font-medium">
              {selectedId ? 'Dokumentvorschau und Empfaengerexport vor dem Druck pruefen.' : 'Datensatz zuerst speichern, dann Druck- und Versandartefakte erzeugen.'}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-wrap gap-2">
        <Button variant="outline" className="gap-2" onClick={handlePreview}>
          <Eye className="h-4 w-4" />
          Vorschau
        </Button>
        <Button variant="outline" className="gap-2" onClick={handlePrint}>
          <Printer className="h-4 w-4" />
          Drucken
        </Button>
        <Button variant="outline" className="gap-2" onClick={handleExportRecipients}>
          Empfaenger exportieren
        </Button>
        <Button className="gap-2" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
          <Save className="h-4 w-4" />
          Speichern
        </Button>
        <Button variant="destructive" className="gap-2" onClick={() => deleteMutation.mutate()} disabled={!selectedId || deleteMutation.isPending}>
          <Trash2 className="h-4 w-4" />
          Loeschen
        </Button>
      </div>
    </div>
  )
}
