/**
 * Feldblockfinder-Integration Komponente
 * 
 * Ermöglicht die Einbindung des deutschen Feldblockfinders per iframe
 * mit Fallback auf externen Link, falls iframe blockiert wird.
 */

import { useState, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { ExternalLink, MapPin, AlertTriangle, Maximize2, RefreshCw } from 'lucide-react'

// Bundesländer mit Feldblockfinder-URLs
const BUNDESLAENDER: Record<string, { name: string; url: string; iframeSupported: boolean }> = {
  'niedersachsen': {
    name: 'Niedersachsen',
    url: 'https://sla.niedersachsen.de/mapbender_sla/frames/login_flink.php',
    iframeSupported: false // FLINK blockiert iframe
  },
  'bayern': {
    name: 'Bayern',
    url: 'https://www.lfl.bayern.de/iab/bodenschutz/019127/index.php',
    iframeSupported: false
  },
  'schleswig-holstein': {
    name: 'Schleswig-Holstein',
    url: 'https://www.schleswig-holstein.de/DE/landesregierung/ministerien-behoerden/LLUR/Aufgaben/Boden/feldblockfinder.html',
    iframeSupported: false
  },
  'nrw': {
    name: 'Nordrhein-Westfalen',
    url: 'https://www.landwirtschaftskammer.de/foerderung/flaechenidentifizierung/',
    iframeSupported: false
  },
  'hessen': {
    name: 'Hessen',
    url: 'https://geobox.hessen.de/mapbender/frames/login.php',
    iframeSupported: false
  },
  'baden-wuerttemberg': {
    name: 'Baden-Württemberg',
    url: 'https://www.lgl-bw.de/Produkte/Geodaten/Geoportal-BW/',
    iframeSupported: false
  },
  'rheinland-pfalz': {
    name: 'Rheinland-Pfalz',
    url: 'https://www.geoportal.rlp.de/',
    iframeSupported: false
  },
  'sachsen': {
    name: 'Sachsen',
    url: 'https://www.landwirtschaft.sachsen.de/feldblockfinder/',
    iframeSupported: false
  },
  'sachsen-anhalt': {
    name: 'Sachsen-Anhalt',
    url: 'https://www.geodatenportal.sachsen-anhalt.de/',
    iframeSupported: false
  },
  'thueringen': {
    name: 'Thüringen',
    url: 'https://www.tlllr.thueringen.de/',
    iframeSupported: false
  },
  'brandenburg': {
    name: 'Brandenburg',
    url: 'https://www.luis.brandenburg.de/',
    iframeSupported: false
  },
  'mecklenburg-vorpommern': {
    name: 'Mecklenburg-Vorpommern',
    url: 'https://www.geoport-mv.de/',
    iframeSupported: false
  },
  'saarland': {
    name: 'Saarland',
    url: 'https://geoportal.saarland.de/',
    iframeSupported: false
  },
}

export interface SchlagData {
  flik: string // Feldblock-Identifier
  bundesland: string
  gemarkung?: string
  flur?: string
  flurstueck?: string
  flaeche?: number // in ha
  nutzung?: string
  coordinates?: {
    lat: number
    lng: number
  }
}

interface FeldblockfinderIntegrationProps {
  defaultBundesland?: string
  onSchlagSelected?: (schlagData: SchlagData) => void
  height?: string
  className?: string
}

export function FeldblockfinderIntegration({
  defaultBundesland,
  onSchlagSelected,
  height = '600px',
  className = ''
}: FeldblockfinderIntegrationProps) {
  const [selectedBundesland, setSelectedBundesland] = useState<string>(defaultBundesland || '')
  const [isLoading, setIsLoading] = useState(false)
  const [iframeError, setIframeError] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  
  const bundeslandInfo = selectedBundesland ? BUNDESLAENDER[selectedBundesland] : null

  const handleBundeslandChange = (value: string) => {
    setSelectedBundesland(value)
    setIsLoading(true)
    setIframeError(false)
    // Simulate loading timeout
    setTimeout(() => setIsLoading(false), 1500)
  }

  const openExternalLink = useCallback(() => {
    if (bundeslandInfo) {
      window.open(bundeslandInfo.url, '_blank', 'noopener,noreferrer')
    }
  }, [bundeslandInfo])

  const handleIframeLoad = () => {
    setIsLoading(false)
  }

  const handleIframeError = () => {
    setIsLoading(false)
    setIframeError(true)
  }

  // Manual data entry form for when iframe doesn't work
  const ManualSchlagEntry = () => {
    const [flik, setFlik] = useState('')
    const [flaeche, setFlaeche] = useState('')
    const [nutzung, setNutzung] = useState('')

    const handleSubmit = () => {
      if (onSchlagSelected && flik) {
        onSchlagSelected({
          flik,
          bundesland: bundeslandInfo?.name || '',
          flaeche: flaeche ? parseFloat(flaeche) : undefined,
          nutzung: nutzung || undefined
        })
      }
    }

    return (
      <div className="space-y-4 p-4 border rounded-lg bg-muted/30">
        <h4 className="font-medium">Schlagdaten manuell eingeben</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-sm font-medium">FLIK (Feldblock-ID) *</label>
            <input
              type="text"
              value={flik}
              onChange={(e) => setFlik(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded-md"
              placeholder="DENILI0123456789"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Fläche (ha)</label>
            <input
              type="number"
              step="0.01"
              value={flaeche}
              onChange={(e) => setFlaeche(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded-md"
              placeholder="12.50"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Nutzung</label>
            <input
              type="text"
              value={nutzung}
              onChange={(e) => setNutzung(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded-md"
              placeholder="Ackerland"
            />
          </div>
        </div>
        <Button onClick={handleSubmit} disabled={!flik}>
          Schlag übernehmen
        </Button>
      </div>
    )
  }

  return (
    <Card className={`${className} ${isFullscreen ? 'fixed inset-4 z-50' : ''}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              Feldblockfinder
            </CardTitle>
            <CardDescription>
              Suchen Sie Feldblöcke und übernehmen Sie die Daten in Ihre Schlagkartei
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => setIsFullscreen(!isFullscreen)}
              title={isFullscreen ? 'Vollbild beenden' : 'Vollbild'}
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
            {bundeslandInfo && (
              <Button
                variant="outline"
                size="icon"
                onClick={() => {
                  setIsLoading(true)
                  setIframeError(false)
                  setTimeout(() => setIsLoading(false), 1500)
                }}
                title="Neu laden"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Bundesland-Auswahl */}
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="text-sm font-medium mb-2 block">Bundesland auswählen</label>
            <Select value={selectedBundesland} onValueChange={handleBundeslandChange}>
              <SelectTrigger>
                <SelectValue placeholder="Bitte Bundesland wählen..." />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(BUNDESLAENDER).map(([key, { name }]) => (
                  <SelectItem key={key} value={key}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {bundeslandInfo && (
            <Button variant="outline" onClick={openExternalLink}>
              <ExternalLink className="h-4 w-4 mr-2" />
              Im neuen Tab öffnen
            </Button>
          )}
        </div>

        {/* Iframe oder Fallback */}
        {selectedBundesland && bundeslandInfo && (
          <div className="space-y-4">
            {/* Info-Alert: iframe meist blockiert */}
            {!bundeslandInfo.iframeSupported && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Hinweis</AlertTitle>
                <AlertDescription>
                  Der Feldblockfinder von {bundeslandInfo.name} unterstützt keine iframe-Einbettung.
                  Bitte öffnen Sie den Feldblockfinder im neuen Tab und übernehmen Sie die Daten manuell.
                </AlertDescription>
              </Alert>
            )}

            {/* Loading Skeleton */}
            {isLoading && (
              <div className="space-y-4">
                <Skeleton className="w-full" style={{ height }} />
              </div>
            )}

            {/* iframe (Versuch) */}
            {bundeslandInfo.iframeSupported && !isLoading && !iframeError && (
              <div className="border rounded-lg overflow-hidden" style={{ height }}>
                <iframe
                  src={bundeslandInfo.url}
                  className="w-full h-full"
                  title={`Feldblockfinder ${bundeslandInfo.name}`}
                  onLoad={handleIframeLoad}
                  onError={handleIframeError}
                  sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                />
              </div>
            )}

            {/* Fehler oder nicht unterstützt: Manuelle Eingabe */}
            {(!bundeslandInfo.iframeSupported || iframeError) && !isLoading && (
              <div className="space-y-4">
                {/* Vorschau-Bild / Placeholder */}
                <div 
                  className="border rounded-lg bg-gradient-to-br from-green-100 to-green-200 dark:from-green-900/30 dark:to-green-800/30 flex items-center justify-center"
                  style={{ height: '300px' }}
                >
                  <div className="text-center space-y-4">
                    <MapPin className="h-16 w-16 mx-auto text-green-600 dark:text-green-400" />
                    <div>
                      <h3 className="text-lg font-semibold">Feldblockfinder {bundeslandInfo.name}</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Öffnen Sie den Feldblockfinder im neuen Tab, um Feldblöcke zu suchen
                      </p>
                    </div>
                    <Button onClick={openExternalLink} size="lg">
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Feldblockfinder öffnen
                    </Button>
                  </div>
                </div>

                {/* Manuelle Eingabe */}
                <ManualSchlagEntry />
              </div>
            )}
          </div>
        )}

        {/* Keine Auswahl */}
        {!selectedBundesland && (
          <div 
            className="border rounded-lg bg-muted/30 flex items-center justify-center"
            style={{ height: '300px' }}
          >
            <div className="text-center space-y-2">
              <MapPin className="h-12 w-12 mx-auto text-muted-foreground" />
              <p className="text-muted-foreground">
                Bitte wählen Sie ein Bundesland aus, um den Feldblockfinder zu nutzen
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default FeldblockfinderIntegration

