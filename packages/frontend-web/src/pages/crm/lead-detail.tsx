import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Save, Loader2, ArrowLeft, Target, Trash2 } from 'lucide-react'
import { queryKeys, mutationKeys } from '@/lib/query'
import { crmService, type Lead } from '@/lib/services/crm-service'
import { useToast } from '@/components/ui/toast-provider'

export default function LeadDetailPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams()
  const queryClient = useQueryClient()
  const toast = useToast()
  const isNew = !id || id === 'neu'

  const [lead, setLead] = useState<Partial<Lead>>({
    company: '',
    contactPerson: '',
    email: '',
    phone: '',
    source: '',
    potential: 0,
    priority: 'medium',
    status: 'new',
    assignedTo: '',
    expectedCloseDate: '',
    notes: '',
  })

  const { data: existingLead, isLoading } = useQuery({
    queryKey: queryKeys.crm.leads.detail(id!),
    queryFn: () => crmService.getLead(id!),
    enabled: !isNew && !!id,
  })

  useEffect(() => {
    if (existingLead && !isNew) {
      setLead(existingLead)
    }
  }, [existingLead, isNew])

  const createMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.create,
    mutationFn: (data: Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>) => crmService.createLead(data),
    onSuccess: () => {
      toast.push('Lead erfolgreich erstellt')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
      navigate('/crm/leads')
    },
    onError: (error) => {
      toast.push('Fehler beim Erstellen des Leads')
      console.error('Create error:', error)
    },
  })

  const updateMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.update,
    mutationFn: (data: Partial<Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>>) =>
      crmService.updateLead(id!, data),
    onSuccess: () => {
      toast.push('Lead erfolgreich aktualisiert')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.detail(id!) })
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
    },
    onError: (error) => {
      toast.push('Fehler beim Aktualisieren des Leads')
      console.error('Update error:', error)
    },
  })

  const deleteMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.delete,
    mutationFn: () => crmService.deleteLead(id!),
    onSuccess: () => {
      toast.push('Lead erfolgreich gelöscht')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
      navigate('/crm/leads')
    },
    onError: (error) => {
      toast.push('Fehler beim Löschen des Leads')
      console.error('Delete error:', error)
    },
  })

  const handleSave = () => {
    if (!lead.company || !lead.contactPerson || !lead.source) {
      toast.push('Bitte füllen Sie alle Pflichtfelder aus')
      return
    }

    if (isNew) {
      createMutation.mutate(lead as Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>)
    } else {
      updateMutation.mutate(lead)
    }
  }

  const handleDelete = () => {
    if (window.confirm('Möchten Sie diesen Lead wirklich löschen?')) {
      deleteMutation.mutate()
    }
  }

  const updateField = (field: keyof Lead, value: any) => {
    setLead(prev => ({ ...prev, [field]: value }))
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0,
    }).format(value)
  }

  if (isLoading && !isNew) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Lade Lead...</span>
      </div>
    )
  }

  const priorityColor = lead.priority === 'high' ? 'destructive' : lead.priority === 'medium' ? 'secondary' : 'outline'
  const statusColor = lead.status === 'qualified' ? 'default' : 'outline'

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate('/crm/leads')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Zurück
          </Button>
          <div className="flex items-center gap-3">
            <Target className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                {isNew ? 'Neuer Lead' : lead.company || 'Lead'}
                {!isNew && (
                  <>
                    <Badge variant={priorityColor}>
                      {lead.priority === 'high' ? 'Hoch' : lead.priority === 'medium' ? 'Mittel' : 'Niedrig'}
                    </Badge>
                    <Badge variant={statusColor}>
                      {lead.status === 'new' ? 'Neu' : lead.status === 'contacted' ? 'Kontaktiert' : lead.status === 'qualified' ? 'Qualifiziert' : 'Verloren'}
                    </Badge>
                  </>
                )}
              </h1>
              <p className="text-muted-foreground">
                {isNew ? 'Erstellen Sie einen neuen Lead' : lead.contactPerson || 'Lead-Details'}
              </p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {!isNew && (
            <Button
              variant="outline"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="text-red-600 hover:text-red-700"
            >
              {deleteMutation.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              <Trash2 className="h-4 w-4 mr-2" />
              Löschen
            </Button>
          )}
          <Button variant="outline" onClick={() => navigate('/crm/leads')}>
            Abbrechen
          </Button>
          <Button
            onClick={handleSave}
            disabled={createMutation.isPending || updateMutation.isPending}
            className="gap-2"
          >
            {(createMutation.isPending || updateMutation.isPending) && (
              <Loader2 className="h-4 w-4 animate-spin" />
            )}
            <Save className="h-4 w-4" />
            {isNew ? 'Erstellen' : 'Speichern'}
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Lead-Informationen</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="company">Unternehmen *</Label>
              <Input
                id="company"
                value={lead.company || ''}
                onChange={(e) => updateField('company', e.target.value)}
                placeholder="z.B. Musterfirma GmbH"
              />
            </div>
            <div>
              <Label htmlFor="contactPerson">Ansprechpartner *</Label>
              <Input
                id="contactPerson"
                value={lead.contactPerson || ''}
                onChange={(e) => updateField('contactPerson', e.target.value)}
                placeholder="z.B. Max Mustermann"
              />
            </div>
            <div>
              <Label htmlFor="email">E-Mail</Label>
              <Input
                id="email"
                type="email"
                value={lead.email || ''}
                onChange={(e) => updateField('email', e.target.value)}
                placeholder="z.B. kontakt@musterfirma.de"
              />
            </div>
            <div>
              <Label htmlFor="phone">Telefon</Label>
              <Input
                id="phone"
                value={lead.phone || ''}
                onChange={(e) => updateField('phone', e.target.value)}
                placeholder="z.B. +49 123 456789"
              />
            </div>
            <div>
              <Label htmlFor="source">Quelle *</Label>
              <Select value={lead.source || ''} onValueChange={(value) => updateField('source', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Quelle auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Website">Website</SelectItem>
                  <SelectItem value="Messe">Messe</SelectItem>
                  <SelectItem value="Empfehlung">Empfehlung</SelectItem>
                  <SelectItem value="Kaltakquise">Kaltakquise</SelectItem>
                  <SelectItem value="Social Media">Social Media</SelectItem>
                  <SelectItem value="Sonstiges">Sonstiges</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status & Bewertung</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="potential">Potenzial (EUR)</Label>
              <Input
                id="potential"
                type="number"
                value={lead.potential || ''}
                onChange={(e) => updateField('potential', parseFloat(e.target.value) || 0)}
                placeholder="z.B. 50000"
              />
              {lead.potential && lead.potential > 0 && (
                <p className="text-sm text-muted-foreground mt-1">
                  {formatCurrency(lead.potential)}
                </p>
              )}
            </div>
            <div>
              <Label htmlFor="priority">Priorität</Label>
              <Select value={lead.priority || 'medium'} onValueChange={(value) => updateField('priority', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Priorität auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Niedrig</SelectItem>
                  <SelectItem value="medium">Mittel</SelectItem>
                  <SelectItem value="high">Hoch</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <Select value={lead.status || 'new'} onValueChange={(value) => updateField('status', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Status auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new">Neu</SelectItem>
                  <SelectItem value="contacted">Kontaktiert</SelectItem>
                  <SelectItem value="qualified">Qualifiziert</SelectItem>
                  <SelectItem value="lost">Verloren</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="assignedTo">Zuständig</Label>
              <Input
                id="assignedTo"
                value={lead.assignedTo || ''}
                onChange={(e) => updateField('assignedTo', e.target.value)}
                placeholder="z.B. Hans Mueller"
              />
            </div>
            <div>
              <Label htmlFor="expectedCloseDate">Erwarteter Abschluss</Label>
              <Input
                id="expectedCloseDate"
                type="date"
                value={lead.expectedCloseDate ? lead.expectedCloseDate.split('T')[0] : ''}
                onChange={(e) => updateField('expectedCloseDate', e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Notizen</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={lead.notes || ''}
              onChange={(e) => updateField('notes', e.target.value)}
              placeholder="Zusätzliche Informationen zum Lead..."
              rows={6}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

