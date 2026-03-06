/**
 * Buchungsübernahme aus Connectors
 * Hub für Lohn, Asset Ledger und weitere Connectors – erzeugte Buchungen gehen in FiBu.
 */

import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Zap, Building2, LayoutGrid, ArrowRight } from 'lucide-react'

export default function BuchungsuebernahmeConnectorsPage(): JSX.Element {
  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <span className="rounded-lg border bg-muted/40 p-2">
              <Zap className="h-5 w-5" />
            </span>
            <div>
              <CardTitle>Buchungsübernahme Connectors</CardTitle>
              <CardDescription>
                Buchungen aus externen Systemen (Lohn, Anlagen) in die Finanzbuchhaltung übernehmen
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
            <p className="font-semibold">Verdrahtung zur FiBu</p>
            <p className="mt-1">
              Connector-Läufe erzeugen Journal-Einträge (journal_entries) und erscheinen im Hauptbuch
              sowie in der Buchungsübergabe (ASC-Export).
            </p>
          </div>

          <div className="grid gap-3">
            <Link to="/fibu-suite/lohn-connector">
              <Card className="hover:bg-muted/50 transition-colors">
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Building2 className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-semibold">Lohn-Connector</p>
                      <p className="text-sm text-muted-foreground">
                        Lohnbuchungen aus LEXWARE / externer Lohnbuchhaltung
                      </p>
                    </div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground" />
                </CardContent>
              </Card>
            </Link>

            <Link to="/fibu-suite/anlagen-suite">
              <Card className="hover:bg-muted/50 transition-colors">
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <LayoutGrid className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-semibold">Asset Ledger (Anlagen)</p>
                      <p className="text-sm text-muted-foreground">
                        Abschreibungen und Anlagenbuchungen
                      </p>
                    </div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground" />
                </CardContent>
              </Card>
            </Link>
          </div>

          <div className="flex gap-2 pt-2">
            <Link to="/fibu-suite/schnittstellen-center">
              <Button variant="outline" size="sm">Schnittstellen-Center</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
