import { Link } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useFibuCockpit, useFibuConnectorProfiles } from '@/lib/api/fibu'
import { ArrowRight, Building2, LayoutGrid, Zap } from 'lucide-react'

export default function BuchungsuebernahmeConnectorsPage(): JSX.Element {
  const { data: fibuCockpit } = useFibuCockpit()
  const { data: payrollProfiles } = useFibuConnectorProfiles('PAYROLL')
  const { data: assetProfiles } = useFibuConnectorProfiles('ASSET_LEDGER')

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <span className="rounded-lg border bg-muted/40 p-2">
              <Zap className="h-5 w-5" />
            </span>
            <div>
              <CardTitle>Buchungsübernahme Connectors</CardTitle>
              <CardDescription>
                Lohn- und Anlagenimporte mit Profilen, Versionen und Revisionspfad in die Finanzbuchhaltung.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-lg border p-3">
              <div className="text-xs text-muted-foreground">Payroll-Profile</div>
              <div className="text-2xl font-semibold">{payrollProfiles.length}</div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-xs text-muted-foreground">Asset-Profile</div>
              <div className="text-2xl font-semibold">{assetProfiles.length}</div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-xs text-muted-foreground">Exportläufe</div>
              <div className="text-2xl font-semibold">{fibuCockpit.revision.export_runs}</div>
            </div>
          </div>

          <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
            <p className="font-semibold">Verdrahtung zur FiBu</p>
            <p className="mt-1">
              Connector-Läufe erzeugen Journal-Einträge, erscheinen im Hauptbuch und laufen im selben Revisionspfad wie
              Buchungsübergabe, OP und Abschluss.
            </p>
          </div>

          <div className="grid gap-3">
            <Link to="/fibu/lohn-connector">
              <Card className="transition-colors hover:bg-muted/50">
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    <Building2 className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-semibold">Lohn-Connector</p>
                      <p className="text-sm text-muted-foreground">Lohnbuchungen aus externer Lohnbuchhaltung</p>
                      {payrollProfiles[0] ? <Badge variant="outline" className="mt-2">Default: {payrollProfiles[0].name}</Badge> : null}
                    </div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground" />
                </CardContent>
              </Card>
            </Link>

            <Link to="/fibu/anlagen-suite">
              <Card className="transition-colors hover:bg-muted/50">
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    <LayoutGrid className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-semibold">Asset Ledger (Anlagen)</p>
                      <p className="text-sm text-muted-foreground">Abschreibungen, Umbuchungen und Anlagenimporte</p>
                      {assetProfiles[0] ? <Badge variant="outline" className="mt-2">Default: {assetProfiles[0].name}</Badge> : null}
                    </div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground" />
                </CardContent>
              </Card>
            </Link>
          </div>

          <div className="flex gap-2 pt-2">
            <Link to="/fibu/schnittstellen-center">
              <Button variant="outline" size="sm">Schnittstellen-Center</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
