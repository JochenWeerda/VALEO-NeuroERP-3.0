/**
 * ATLAS (Zoll) – Platzhalter für Zollanmeldungen, Ausfuhr, EU-Übermittlung.
 * Status: Geplant. Backend-Anbindung an ATLAS-Portal folgt.
 */

import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { FileDown, ArrowLeft } from 'lucide-react'

export default function AtlasPage(): JSX.Element {
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <span className="rounded-lg border bg-muted/40 p-2">
              <FileDown className="h-5 w-5" />
            </span>
            <div>
              <CardTitle>ATLAS (Zoll)</CardTitle>
              <Badge variant="secondary" className="mt-1">Geplant</Badge>
            </div>
          </div>
          <CardDescription>
            Zollanmeldungen, Ausfuhr, EU-Übermittlung – Integration mit dem ATLAS-Portal der Bundeszollverwaltung.
            Voraussichtliche Funktionen: Anmeldung (Ausfuhr/Verbringung), Statusabfrage, Export-Übermittlung.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Diese Schnittstelle wird in einer kommenden Version verfügbar sein. Für Rückfragen wenden Sie sich an die IT.
          </p>
          <Link to="/fibu/schnittstellen-center">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Zurück zum Schnittstellen-Center
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  )
}
