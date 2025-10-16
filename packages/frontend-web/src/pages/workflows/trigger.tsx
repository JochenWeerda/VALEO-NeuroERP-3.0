import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Zap, Loader2, CheckCircle, TrendingDown, Package, AlertCircle } from 'lucide-react'
import { useTriggerWorkflow } from '@/lib/api/workflows'

export default function WorkflowTriggerPage(): JSX.Element {
  const navigate = useNavigate()
  const [lastWorkflowId, setLastWorkflowId] = useState<string | null>(null)
  const triggerWorkflow = useTriggerWorkflow()
  
  const handleTrigger = async (): Promise<void> => {
    try {
      const result = await triggerWorkflow.mutateAsync('system') as any
      setLastWorkflowId(result.workflow_id)
      
      // Navigate to approval page
      navigate(`/workflows/approval/${result.workflow_id}`)
    } catch (error) {
      console.error('Failed to trigger workflow:', error)
    }
  }
  
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold">KI-Workflows</h1>
          <p className="text-muted-foreground">Automatisierte Geschäftsprozesse</p>
        </div>
        
        {/* Workflow Cards */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Bestellvorschlag */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingDown className="h-5 w-5 text-orange-600" />
                Bestellvorschlag
                <Badge variant="default" className="ml-auto">KI-Agent</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Analysiert Lagerbestände und Verkaufshistorie, um automatisch 
                Bestellvorschläge zu generieren.
              </p>
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Niedrige Bestände erkennen</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Verkaufstrends analysieren</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Optimale Bestellmenge berechnen</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Human-in-the-Loop Freigabe</span>
                </div>
              </div>
              
              <Button
                onClick={handleTrigger}
                disabled={triggerWorkflow.isPending}
                className="w-full gap-2"
              >
                {triggerWorkflow.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Workflow läuft...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4" />
                    Workflow starten
                  </>
                )}
              </Button>
              
              {lastWorkflowId && (
                <div className="text-xs text-center text-muted-foreground">
                  Letzter Workflow: {lastWorkflowId.slice(0, 8)}...
                </div>
              )}
            </CardContent>
          </Card>
          
          {/* Weitere Workflows (Placeholder) */}
          <Card className="opacity-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                Weitere Workflows
                <Badge variant="secondary" className="ml-auto">Bald verfügbar</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Weitere KI-Workflows werden in zukünftigen Versionen hinzugefügt:
              </p>
              <ul className="text-sm text-muted-foreground mt-2 space-y-1">
                <li>• Preis-Optimierung</li>
                <li>• Mahnwesen-Automation</li>
                <li>• Compliance-Check</li>
              </ul>
            </CardContent>
          </Card>
        </div>
        
        {/* Info */}
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-semibold text-blue-900 mb-1">
                  Human-in-the-Loop-Prinzip
                </p>
                <p className="text-blue-700">
                  Alle KI-Workflows pausieren vor kritischen Entscheidungen und 
                  warten auf menschliche Freigabe. Sie behalten die volle Kontrolle.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

