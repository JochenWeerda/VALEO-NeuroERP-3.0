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
import { Save, Loader2, ArrowLeft, Calendar, Mail, Phone, Users, Trash2 } from 'lucide-react'
import { queryKeys, mutationKeys } from '@/lib/query'
import { crmService, type Activity } from '@/lib/services/crm-service'
import { useToast } from '@/components/ui/toast-provider'

export default function AktivitaetDetailPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams()
  const queryClient = useQueryClient()
  const toast = useToast()
  const isNew = !id || id === 'neu'

  const [activity, setActivity] = useState<Partial<Activity>>({
    type: 'meeting',
    title: '',
    customer: '',
    contactPerson: '',
    date: new Date().toISOString().split('T')[0],
    status: 'planned',
    assignedTo: '',
    description: '',
  })

  const { data: existingActivity, isLoading } = useQuery({
    queryKey: queryKeys.crm.activities.detail(id!),
    queryFn: () => crmService.getActivity(id!),
    enabled: !isNew && !!id,
  })

  useEffect(() => {
    if (existingActivity && !isNew) {
      setActivity(existingActivity)
    }
  }, [existingActivity, isNew])

  const createMutation = useMutation({
    mutationKey: mutationKeys.crm.activities.create,
    mutationFn: (data: Omit<Activity, 'id' | 'createdAt' | 'updatedAt'>) => crmService.createActivity(data),
    onSuccess: () => {
      toast.push('Aktivität erfolgreich erstellt')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.activities.all })
      navigate('/crm/aktivitaeten')
    },
    onError: (error) => {
      toast.push('Fehler beim Erstellen der Aktivität')
      console.error('Create error:', error)
    },
  })

  const updateMutation = useMutation({
    mutationKey: mutationKeys.crm.activities.update,
    mutationFn: (data: Partial<Omit<Activity, 'id' | 'createdAt' | 'updatedAt'>>) =>
      crmService.updateActivity(id!, data),
    onSuccess: () => {
      toast.push('Aktivität erfolgreich aktualisiert')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.activities.detail(id!) })
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.activities.all })
    },
    onError: (error) => {
      toast.push('Fehler beim Aktualisieren der Aktivität')
      console.error('Update error:', error)
    },
  })

  const deleteMutation = useMutation({
    mutationKey: mutationKeys.crm.activities.delete,
    mutationFn: () => crmService.deleteActivity(id!),
    onSuccess: () => {
      toast.push('Aktivität erfolgreich gelöscht')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.activities.all })
      navigate('/crm/aktivitaeten')
    },
    onError: (error) => {
      toast.push('Fehler beim Löschen der Aktivität')
      console.error('Delete error:', error)
    },
  })

  const handleSave = () => {
    if (!activity.title || !activity.customer || !activity.contactPerson || !activity.date) {
      toast.push('Bitte füllen Sie alle Pflichtfelder aus')
      return
    }

    if (isNew) {
      createMutation.mutate(activity as Omit<Activity, 'id' | 'createdAt' | 'updatedAt'>)
    } else {
      updateMutation.mutate(activity)
    }
  }

  const handleDelete = () => {
    if (window.confirm('Möchten Sie diese Aktivität wirklich löschen?')) {
      deleteMutation.mutate()
    }
  }

  const updateField = (field: keyof Activity, value: any) => {
    setActivity(prev => ({ ...prev, [field]: value }))
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'meeting':
        return Calendar
      case 'call':
        return Phone
      case 'email':
        return Mail
      default:
        return Users
    }
  }

  const TypeIcon = getTypeIcon(activity.type || 'meeting')

  if (isLoading && !isNew) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Lade Aktivität...</span>
      </div>
    )
  }

  const statusColor = activity.status === 'completed' ? 'outline' : activity.status === 'overdue' ? 'destructive' : 'secondary'

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate('/crm/aktivitaeten')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Zurück
          </Button>
          <div className="flex items-center gap-3">
            <TypeIcon className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                {isNew ? 'Neue Aktivität' : activity.title || 'Aktivität'}
                {!isNew && (
                  <Badge variant={statusColor}>
                    {activity.status === 'completed' ? 'Abgeschlossen' : activity.status === 'overdue' ? 'Überfällig' : 'Geplant'}
                  </Badge>
                )}
              </h1>
              <p className="text-muted-foreground">
                {isNew ? 'Erstellen Sie eine neue Aktivität' : `${activity.customer} - ${activity.contactPerson}`}
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
          <Button variant="outline" onClick={() => navigate('/crm/aktivitaeten')}>
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
            <CardTitle>Aktivitäts-Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="type">Typ *</Label>
              <Select value={activity.type || 'meeting'} onValueChange={(value) => updateField('type', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Typ auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="meeting">Termin</SelectItem>
                  <SelectItem value="call">Anruf</SelectItem>
                  <SelectItem value="email">E-Mail</SelectItem>
                  <SelectItem value="note">Notiz</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="title">Titel *</Label>
              <Input
                id="title"
                value={activity.title || ''}
                onChange={(e) => updateField('title', e.target.value)}
                placeholder="z.B. Jahresgespräch 2025"
              />
            </div>
            <div>
              <Label htmlFor="customer">Kunde *</Label>
              <Input
                id="customer"
                value={activity.customer || ''}
                onChange={(e) => updateField('customer', e.target.value)}
                placeholder="z.B. Musterfirma GmbH"
              />
            </div>
            <div>
              <Label htmlFor="contactPerson">Ansprechpartner *</Label>
              <Input
                id="contactPerson"
                value={activity.contactPerson || ''}
                onChange={(e) => updateField('contactPerson', e.target.value)}
                placeholder="z.B. Max Mustermann"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Zeitplanung & Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="date">Datum *</Label>
              <Input
                id="date"
                type="date"
                value={activity.date ? activity.date.split('T')[0] : ''}
                onChange={(e) => updateField('date', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <Select value={activity.status || 'planned'} onValueChange={(value) => updateField('status', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Status auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="planned">Geplant</SelectItem>
                  <SelectItem value="completed">Abgeschlossen</SelectItem>
                  <SelectItem value="overdue">Überfällig</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="assignedTo">Zuständig *</Label>
              <Input
                id="assignedTo"
                value={activity.assignedTo || ''}
                onChange={(e) => updateField('assignedTo', e.target.value)}
                placeholder="z.B. Hans Mueller"
              />
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Beschreibung</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={activity.description || ''}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Detaillierte Beschreibung der Aktivität..."
              rows={6}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

