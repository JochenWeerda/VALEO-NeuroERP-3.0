import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { toast } from '@/hooks/use-toast'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { BackButton } from '@/components/BackButton'
import { PolicyExplanationBadge, type PolicyExplanationData } from '@/components/policy/PolicyExplanationBadge'
import {
  CheckCircle, XCircle, Loader2, AlertCircle,
  Package, Euro, Clock
} from 'lucide-react'
import { useWorkflowStatus, useApproveWorkflow } from '@/lib/api/workflows'
import { apiClient } from '@/lib/axios'
import { getCapabilityByKey } from '@/lib/agentCapabilities'

export default function WorkflowApprovalPage(): JSX.Element {
  const { workflowId } = useParams<{ workflowId: string }>()
  const navigate = useNavigate()
  const [rejectionReason, setRejectionReason] = useState('')
  
  const { data: workflow, isLoading, error } = useWorkflowStatus(workflowId ?? '')
  const approveWorkflow = useApproveWorkflow()

  // Gap 019 — Policy Explainability: Lade Policy-Kontext für diesen Workflow
  const policyQuery = useQuery({
    queryKey: ['workflow-policy', workflowId],
    queryFn: () => apiClient.get<PolicyExplanationData>(`/api/v1/policies/explain/workflow/${workflowId ?? ''}`),
    enabled: !!workflowId,
    retry: false,
  })
  
  const handleApprove = async (): Promise<void> => {
    if (!workflowId) return
    
    try {
      await approveWorkflow.mutateAsync({
        workflowId,
        approved: true
      })
      
      // Navigate to success page or workflows list
      navigate('/workflows/history')
    } catch (error) {
      console.error('Approval failed:', error)
    }
  }
  
  const handleReject = async (): Promise<void> => {
    if (!workflowId || !rejectionReason.trim()) {
      toast({ title: 'Ablehnungsgrund fehlt', description: 'Bitte geben Sie einen Ablehnungsgrund an.', variant: 'destructive' })
      return
    }
    
    try {
      await approveWorkflow.mutateAsync({
        workflowId,
        approved: false,
        rejection_reason: rejectionReason
      })
      
      navigate('/workflows/history')
    } catch (error) {
      console.error('Rejection failed:', error)
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }
  
  if (error || !workflow) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="p-6 max-w-md">
          <div className="flex items-center gap-3 text-destructive">
            <AlertCircle className="h-6 w-6" />
            <div>
              <h3 className="font-semibold">Workflow nicht gefunden</h3>
              <p className="text-sm text-muted-foreground">
                ID: {workflowId}
              </p>
            </div>
          </div>
        </Card>
      </div>
    )
  }
  
  const proposal = workflow.proposal
  const capability = workflow.capability_key ? getCapabilityByKey(workflow.capability_key) : undefined
  const capabilityTitle = capability?.title ?? workflow.capability_key ?? 'NeuroASSIST-Run'
  const canUseGenericApproval = workflow.capability_key === 'bestellvorschlag_assistant'
  
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">{capabilityTitle} freigeben</h1>
            <p className="text-muted-foreground">Workflow: {workflowId}</p>
          </div>
          <div className="flex gap-2 items-center">
            <BackButton to="/workflows" label="Zurück zu Workflows" />
            <Badge 
              variant={
                workflow.status === 'completed' ? 'default' :
                workflow.status === 'rejected' ? 'destructive' :
                'secondary'
              }
              className="text-lg px-4 py-2"
            >
              {workflow.status === 'pending_approval' && '⏳ Wartet auf Freigabe'}
              {workflow.status === 'completed' && '✅ Genehmigt'}
              {workflow.status === 'rejected' && '❌ Abgelehnt'}
            </Badge>
          </div>
        </div>
        
        {/* Proposal Details */}
        {proposal && (
          <>
            {/* Summary */}
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Artikel</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <Package className="h-5 w-5 text-blue-600" />
                    <span className="text-2xl font-bold">{proposal.items.length}</span>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Gesamtkosten (geschätzt)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <Euro className="h-5 w-5 text-green-600" />
                    <span className="text-2xl font-bold">
                      {new Intl.NumberFormat('de-DE', { 
                        style: 'currency', 
                        currency: 'EUR',
                        maximumFractionDigits: 0 
                      }).format(proposal.total_estimated_cost)}
                    </span>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Erstellt</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-orange-600" />
                    <span className="text-lg font-semibold">
                      {new Date(proposal.created_at).toLocaleTimeString('de-DE', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            {/* Items Table */}
            <Card>
              <CardHeader>
                <CardTitle>Bestellpositionen</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {proposal.items.map((item, idx) => (
                    <div 
                      key={idx} 
                      className="flex items-center justify-between border rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex-1">
                        <div className="font-semibold text-lg">{item.article_name}</div>
                        <div className="text-sm text-muted-foreground mt-1">{item.reason}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-primary">
                          {item.order_quantity} Stk
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {new Intl.NumberFormat('de-DE', { 
                            style: 'currency', 
                            currency: 'EUR' 
                          }).format(item.estimated_cost)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {!proposal && workflow.result ? (
          <Card>
            <CardHeader>
              <CardTitle>Run-Details</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="max-h-72 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-100">
                {JSON.stringify(workflow.result, null, 2)}
              </pre>
            </CardContent>
          </Card>
        ) : null}
        
        {/* Gap 019 — Policy-Kontext */}
        {policyQuery.data && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Policy-Kontext</CardTitle>
            </CardHeader>
            <CardContent>
              <PolicyExplanationBadge explanation={policyQuery.data} showDetails />
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        {workflow.status === 'pending_approval' && canUseGenericApproval && (
          <Card>
            <CardHeader>
              <CardTitle>Freigabe-Entscheidung</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="rejection">Ablehnungsgrund (optional)</Label>
                <Textarea
                  id="rejection"
                  placeholder="Grund für Ablehnung eingeben..."
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  rows={3}
                />
              </div>
              
              <div className="flex gap-4">
                <Button
                  variant="destructive"
                  onClick={handleReject}
                  disabled={approveWorkflow.isPending || !rejectionReason.trim()}
                  className="flex-1 gap-2 text-lg h-14"
                >
                  <XCircle className="h-5 w-5" />
                  Ablehnen
                </Button>
                <Button
                  onClick={handleApprove}
                  disabled={approveWorkflow.isPending}
                  className="flex-1 gap-2 text-lg h-14"
                >
                  <CheckCircle className="h-5 w-5" />
                  Genehmigen
                </Button>
              </div>
              
              {approveWorkflow.isPending && (
                <div className="text-center text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin inline mr-2" />
                  Wird verarbeitet...
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {workflow.status === 'pending_approval' && !canUseGenericApproval ? (
          <Card className="border-dashed">
            <CardContent className="pt-6 text-sm text-muted-foreground">
              Dieser Run wartet auf Human Oversight, exponiert aber aktuell noch keinen generischen UI-Freigabepfad.
            </CardContent>
          </Card>
        ) : null}
        
        {/* Completed */}
        {workflow.status === 'completed' && workflow.order_id && (
          <Card className="border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-8 w-8 text-green-600" />
                <div>
                  <h3 className="font-semibold text-lg">Bestellung erstellt</h3>
                  <p className="text-sm text-muted-foreground">
                    Bestellnummer: {workflow.order_id}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
        
        {/* Rejected */}
        {workflow.status === 'rejected' && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <XCircle className="h-8 w-8 text-red-600" />
                <div>
                  <h3 className="font-semibold text-lg">Vorschlag abgelehnt</h3>
                  <p className="text-sm text-muted-foreground">
                    Keine Bestellung wurde erstellt
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

