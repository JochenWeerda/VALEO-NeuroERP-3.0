import { useQuery } from '@tanstack/react-query'
import {
  Bot,
  ChevronDown,
  ChevronUp,
  FileText,
  History,
  Lightbulb,
  Loader2,
  MessageSquare,
  RefreshCw,
  ShoppingCart,
  TrendingUp,
} from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import { authenticatedFetch } from '@/lib/fetch'

interface RAGPanelProps {
  customerId: string
  customerName?: string
  className?: string
}

interface CustomerInsight {
  type: 'info' | 'warning' | 'opportunity' | 'action'
  title: string
  description: string
  confidence?: number
}

interface CustomerContext {
  summary: string
  insights: CustomerInsight[]
  recentActivity: {
    type: string
    description: string
    date: string
  }[]
  suggestedActions: {
    action: string
    reason: string
    priority: 'high' | 'medium' | 'low'
  }[]
}

// Mock data generator for demo
function generateMockContext(customerId: string, customerName?: string): CustomerContext {
  return {
    summary: `${customerName || 'Dieser Kunde'} ist seit 2019 ein aktiver Kunde mit durchschnittlichem Bestellvolumen. Die letzte Bestellung war vor 2 Wochen. Zahlungsmoral ist gut (Ø 12 Tage).`,
    insights: [
      {
        type: 'opportunity',
        title: 'Cross-Selling-Potenzial',
        description: 'Kunde bestellt regelmäßig Dünger, aber noch keine Pflanzenschutzmittel.',
        confidence: 0.85,
      },
      {
        type: 'info',
        title: 'Saisonaler Trend',
        description: 'Bestellungen steigen typischerweise im März/April um 40%.',
        confidence: 0.92,
      },
      {
        type: 'warning',
        title: 'Offene Reklamation',
        description: 'Lieferung vom 15.01. wurde beanstandet - noch nicht abgeschlossen.',
        confidence: 1.0,
      },
    ],
    recentActivity: [
      { type: 'order', description: 'Bestellung #12345 - €2.450', date: '2 Wochen' },
      { type: 'call', description: 'Telefongespräch mit Vertrieb', date: '3 Wochen' },
      { type: 'email', description: 'Angebot #A789 versendet', date: '1 Monat' },
    ],
    suggestedActions: [
      {
        action: 'Reklamation prüfen und kontaktieren',
        reason: 'Offene Reklamation bearbeiten',
        priority: 'high',
      },
      {
        action: 'Pflanzenschutz-Angebot erstellen',
        reason: 'Cross-Selling-Potenzial nutzen',
        priority: 'medium',
      },
      {
        action: 'Frühlings-Kampagne vorbereiten',
        reason: 'Saisonaler Umsatzanstieg erwartet',
        priority: 'low',
      },
    ],
  }
}

export function RAGPanel({ customerId, customerName, className }: RAGPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true)

  const { data: context, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['customer-rag-context', customerId],
    queryFn: async () => {
      // Try to fetch from AI service
      try {
        const response = await authenticatedFetch(
          `/api/v1/ai/customer-context/${customerId}`
        )
        if (response.ok) {
          return response.json()
        }
      } catch {
        // Fallback to mock data
      }
      // Return mock data for demo
      return generateMockContext(customerId, customerName)
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const insightIcons = {
    info: Lightbulb,
    warning: MessageSquare,
    opportunity: TrendingUp,
    action: ShoppingCart,
  }

  const insightColors = {
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    opportunity: 'bg-green-50 text-green-700 border-green-200',
    action: 'bg-purple-50 text-purple-700 border-purple-200',
  }

  const priorityColors = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-amber-100 text-amber-800',
    low: 'bg-gray-100 text-gray-800',
  }

  return (
    <Card className={cn('border-primary/20', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <Bot className="h-5 w-5 text-primary" />
            KI-Kontext
            <Badge variant="secondary" className="text-xs">
              RAG
            </Badge>
          </CardTitle>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => refetch()}
              disabled={isRefetching}
            >
              <RefreshCw
                className={cn('h-4 w-4', isRefetching && 'animate-spin')}
              />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-sm text-muted-foreground">
                Analysiere Kundendaten...
              </span>
            </div>
          ) : context ? (
            <ScrollArea className="h-[400px] pr-4">
              <div className="space-y-4">
                {/* Summary */}
                <div className="p-3 bg-muted/50 rounded-lg text-sm">
                  {context.summary}
                </div>

                {/* Insights */}
                <div>
                  <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
                    <Lightbulb className="h-4 w-4" />
                    Erkenntnisse
                  </h4>
                  <div className="space-y-2">
                    {context.insights.map((insight, i) => {
                      const Icon = insightIcons[insight.type]
                      return (
                        <div
                          key={i}
                          className={cn(
                            'p-3 rounded-lg border text-sm',
                            insightColors[insight.type]
                          )}
                        >
                          <div className="flex items-start gap-2">
                            <Icon className="h-4 w-4 mt-0.5 flex-shrink-0" />
                            <div>
                              <div className="font-medium">{insight.title}</div>
                              <div className="text-xs mt-1 opacity-80">
                                {insight.description}
                              </div>
                              {insight.confidence && (
                                <div className="text-xs mt-1 opacity-60">
                                  Konfidenz: {Math.round(insight.confidence * 100)}%
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Recent Activity */}
                <div>
                  <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
                    <History className="h-4 w-4" />
                    Letzte Aktivitäten
                  </h4>
                  <div className="space-y-1">
                    {context.recentActivity.map((activity, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between text-sm py-1"
                      >
                        <span className="text-muted-foreground">
                          {activity.description}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {activity.date}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Suggested Actions */}
                <div>
                  <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
                    <FileText className="h-4 w-4" />
                    Empfohlene Aktionen
                  </h4>
                  <div className="space-y-2">
                    {context.suggestedActions.map((action, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between p-2 bg-muted/30 rounded text-sm"
                      >
                        <div>
                          <div className="font-medium">{action.action}</div>
                          <div className="text-xs text-muted-foreground">
                            {action.reason}
                          </div>
                        </div>
                        <Badge className={priorityColors[action.priority]}>
                          {action.priority === 'high'
                            ? 'Hoch'
                            : action.priority === 'medium'
                            ? 'Mittel'
                            : 'Niedrig'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </ScrollArea>
          ) : null}
        </CardContent>
      )}
    </Card>
  )
}

