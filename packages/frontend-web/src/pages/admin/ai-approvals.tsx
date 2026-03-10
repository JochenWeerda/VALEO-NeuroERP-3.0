/**
 * AI-Aktionen zur Freigabe (Gap 015).
 * Human-in-the-loop für AI/Agent-Vorschläge.
 * API-Integration: Hauptstrang (Agent Layer).
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Bot, CheckCircle2, Clock, Info } from 'lucide-react'

export default function AiApprovalsPage(): JSX.Element {
  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold">
          <Bot className="h-6 w-6" />
          AI-Aktionen zur Freigabe
        </h1>
        <p className="mt-1 text-muted-foreground">
          Human-in-the-loop: Vorgeschlagene Aktionen von KI/Agenten prüfen und freigeben (Gap 015).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Ausstehende Freigaben
          </CardTitle>
          <CardDescription>
            KI-/Agent-Vorschläge, die eine manuelle Bestätigung erfordern.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center gap-4 rounded-lg border border-dashed py-12">
            <Info className="h-12 w-12 text-muted-foreground" />
            <p className="text-center text-muted-foreground">
              Keine ausstehenden AI-Aktionen. Die Integration mit dem Agent-Layer erfolgt über den Hauptstrang.
            </p>
            <Badge variant="outline">API: /api/v1/agents/pending-approvals (geplant)</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            Status
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <ul className="text-sm text-muted-foreground">
            <li>• Frontend-Stub bereit (diese Seite)</li>
            <li>• Workflow-Freigaben: <code>workflows/approval</code></li>
            <li>• AI-spezifische Queue: Hauptstrang (Agent Layer + Audit-Trail)</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
