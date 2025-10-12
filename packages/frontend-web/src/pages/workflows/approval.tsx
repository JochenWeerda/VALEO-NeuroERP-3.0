import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { 
  CheckCircle, XCircle, Loader2, AlertCircle, 
  Package, Euro, Clock 
} from 'lucide-react'
import { useWorkflowStatus, useApproveWorkflow } from '@/lib/api/workflows'

export default function WorkflowApprovalPage(): JSX.Element {
  const { workflowId } = useParams<{ workflowId: string }>()
  const navigate = useNavigate()
  const [rejectionReason, setRejectionReason] = useState('')
  
  const { data: workflow, isLoading, error } = useWorkflowStatus(workflowId ?? '')
  const approveWorkflow = useApproveWorkflow()
  
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
      alert('Bitte einen Ablehnungsgrund angeben')
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
  
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Bestellvorschlag freigeben</h1>
            <p className="text-muted-foreground">Workflow: {workflowId}</p>
          </div>
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
        
        {/* Actions */}
        {workflow.status === 'pending_approval' && (
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

