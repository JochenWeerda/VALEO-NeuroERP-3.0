import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Shield, AlertTriangle, CheckCircle, FileText, 
  TrendingUp, Download 
} from 'lucide-react'

export default function ComplianceDashboardPage(): JSX.Element {
  const compliance = {
    overallScore: 92,
    checks: {
      psm: { status: 'compliant', score: 95, details: '45/47 Kunden mit Sachkundenachweis' },
      explosivstoff: { status: 'warning', score: 88, details: '3 Düngemittel ohne Konformitätsnachweis' },
      enni: { status: 'compliant', score: 100, details: 'Q3-Export erfolgreich' },
      traces: { status: 'compliant', score: 94, details: '12 EU-Lieferungen dokumentiert' },
      lksg: { status: 'pending', score: 75, details: 'Lieferketten-Audit läuft' },
      gdpr: { status: 'compliant', score: 98, details: 'Alle Anforderungen erfüllt' },
    },
    recentActions: [
      { id: '1', date: '2025-10-12', action: 'PSM-Sachkundenachweis geprüft', user: 'admin@valeo.de', status: 'success' },
      { id: '2', date: '2025-10-11', action: 'ENNI Q3-Export durchgeführt', user: 'system', status: 'success' },
      { id: '3', date: '2025-10-10', action: 'Explosivstoff-Prüfung Artikel A-1234', user: 'compliance@valeo.de', status: 'warning' },
    ]
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'compliant':
        return <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">✅ Konform</Badge>
      case 'warning':
        return <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">⚠️ Warnung</Badge>
      case 'pending':
        return <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">⏳ Laufend</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Shield className="h-8 w-8 text-blue-600" />
            Compliance-Center
          </h1>
          <p className="text-muted-foreground">Übersicht aller Compliance-Anforderungen</p>
        </div>
        <Button className="gap-2">
          <Download className="h-4 w-4" />
          Compliance-Report (PDF)
        </Button>
      </div>

      {/* Overall Score */}
      <Card className="border-2 border-primary">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold mb-1">Gesamt-Compliance-Score</h2>
              <p className="text-sm text-muted-foreground">Alle Bereiche zusammengefasst</p>
            </div>
            <div className="text-center">
              <div className="text-6xl font-bold text-primary">{compliance.overallScore}%</div>
              <Badge variant="outline" className="mt-2 bg-green-50 text-green-700 border-green-200">
                Sehr gut
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Compliance Checks */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(compliance.checks).map(([key, check]) => (
          <Card key={key} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center justify-between">
                <span className="uppercase">{key}</span>
                {getStatusBadge(check.status)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="text-4xl font-bold text-primary">{check.score}%</div>
                  <TrendingUp className="h-5 w-5 text-green-600" />
                </div>
                <p className="text-sm text-muted-foreground">{check.details}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Letzte Compliance-Aktivitäten
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {compliance.recentActions.map((action) => (
              <div key={action.id} className="flex items-center justify-between p-4 rounded-lg border">
                <div className="flex items-center gap-3">
                  {action.status === 'success' ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <AlertTriangle className="h-5 w-5 text-orange-600" />
                  )}
                  <div>
                    <div className="font-semibold">{action.action}</div>
                    <div className="text-sm text-muted-foreground">
                      {action.date} • {action.user}
                    </div>
                  </div>
                </div>
                <Button variant="ghost" size="sm">Details</Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

