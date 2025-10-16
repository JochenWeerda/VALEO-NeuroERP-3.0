import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Save, Loader2, ArrowLeft, User, Trash2 } from 'lucide-react'
import { queryKeys, mutationKeys } from '@/lib/query'
import { crmService, type Contact } from '@/lib/services/crm-service'
import { useToast } from '@/components/ui/toast-provider'

export default function KontaktDetailPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams()
  const queryClient = useQueryClient()
  const toast = useToast()
  const isNew = !id || id === 'neu'

  const [contact, setContact] = useState<Partial<Contact>>({
    name: '',
    company: '',
    email: '',
    phone: '',
    type: 'customer',
    address: undefined,
    notes: '',
  })

  const { data: existingContact, isLoading } = useQuery({
    queryKey: queryKeys.crm.contacts.detail(id!),
    queryFn: () => crmService.getContact(id!),
    enabled: !isNew && !!id,
  })

  useEffect(() => {
    if (existingContact && !isNew) {
      setContact(existingContact)
    }
  }, [existingContact, isNew])

  const createMutation = useMutation({
    mutationKey: mutationKeys.crm.contacts.create,
    mutationFn: (data: Omit<Contact, 'id' | 'createdAt' | 'updatedAt'>) => crmService.createContact(data),
    onSuccess: () => {
      toast.push('Kontakt erfolgreich erstellt')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.contacts.all })
      navigate('/crm/kontakte-liste')
    },
    onError: (error) => {
      toast.push('Fehler beim Erstellen des Kontakts')
      console.error('Create error:', error)
    },
  })

  const updateMutation = useMutation({
    mutationKey: mutationKeys.crm.contacts.update,
    mutationFn: (data: Partial<Omit<Contact, 'id' | 'createdAt' | 'updatedAt'>>) =>
      crmService.updateContact(id!, data),
    onSuccess: () => {
      toast.push('Kontakt erfolgreich aktualisiert')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.contacts.detail(id!) })
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.contacts.all })
    },
    onError: (error) => {
      toast.push('Fehler beim Aktualisieren des Kontakts')
      console.error('Update error:', error)
    },
  })

  const deleteMutation = useMutation({
    mutationKey: mutationKeys.crm.contacts.delete,
    mutationFn: () => crmService.deleteContact(id!),
    onSuccess: () => {
      toast.push('Kontakt erfolgreich gelöscht')
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.contacts.all })
      navigate('/crm/kontakte-liste')
    },
    onError: (error) => {
      toast.push('Fehler beim Löschen des Kontakts')
      console.error('Delete error:', error)
    },
  })

  const handleSave = () => {
    if (!contact.name || !contact.company || !contact.email) {
      toast.push('Bitte füllen Sie alle Pflichtfelder aus')
      return
    }

    if (isNew) {
      createMutation.mutate(contact as Omit<Contact, 'id' | 'createdAt' | 'updatedAt'>)
    } else {
      updateMutation.mutate(contact)
    }
  }

  const handleDelete = () => {
    if (window.confirm('Möchten Sie diesen Kontakt wirklich löschen?')) {
      deleteMutation.mutate()
    }
  }

  const updateField = (field: keyof Contact, value: any) => {
    setContact(prev => ({ ...prev, [field]: value }))
  }

  const updateAddress = (field: string, value: string) => {
    setContact(prev => ({
      ...prev,
      address: {
        ...(prev.address || { street: '', city: '', zipCode: '', country: '' }),
        [field]: value,
      },
    }))
  }

  if (isLoading && !isNew) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Lade Kontakt...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate('/crm/kontakte-liste')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Zurück
          </Button>
          <div className="flex items-center gap-3">
            <User className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold">
                {isNew ? 'Neuer Kontakt' : contact.name || 'Kontakt'}
              </h1>
              <p className="text-muted-foreground">
                {isNew ? 'Erstellen Sie einen neuen Kontakt' : contact.company || 'Kontaktdetails'}
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
          <Button variant="outline" onClick={() => navigate('/crm/kontakte-liste')}>
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
            <CardTitle>Kontaktdaten</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={contact.name || ''}
                onChange={(e) => updateField('name', e.target.value)}
                placeholder="z.B. Max Mustermann"
              />
            </div>
            <div>
              <Label htmlFor="company">Unternehmen *</Label>
              <Input
                id="company"
                value={contact.company || ''}
                onChange={(e) => updateField('company', e.target.value)}
                placeholder="z.B. Mustermann GmbH"
              />
            </div>
            <div>
              <Label htmlFor="email">E-Mail *</Label>
              <Input
                id="email"
                type="email"
                value={contact.email || ''}
                onChange={(e) => updateField('email', e.target.value)}
                placeholder="z.B. max@mustermann.de"
              />
            </div>
            <div>
              <Label htmlFor="phone">Telefon</Label>
              <Input
                id="phone"
                value={contact.phone || ''}
                onChange={(e) => updateField('phone', e.target.value)}
                placeholder="z.B. +49 123 456789"
              />
            </div>
            <div>
              <Label htmlFor="type">Typ</Label>
              <Select value={contact.type || 'customer'} onValueChange={(value) => updateField('type', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Typ auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="customer">Kunde</SelectItem>
                  <SelectItem value="supplier">Lieferant</SelectItem>
                  <SelectItem value="farmer">Landwirt</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Adresse & Notizen</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="street">Straße</Label>
              <Input
                id="street"
                value={contact.address?.street || ''}
                onChange={(e) => updateAddress('street', e.target.value)}
                placeholder="z.B. Musterstraße 123"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="zipCode">PLZ</Label>
                <Input
                  id="zipCode"
                  value={contact.address?.zipCode || ''}
                  onChange={(e) => updateAddress('zipCode', e.target.value)}
                  placeholder="z.B. 12345"
                />
              </div>
              <div>
                <Label htmlFor="city">Stadt</Label>
                <Input
                  id="city"
                  value={contact.address?.city || ''}
                  onChange={(e) => updateAddress('city', e.target.value)}
                  placeholder="z.B. Berlin"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="country">Land</Label>
              <Input
                id="country"
                value={contact.address?.country || ''}
                onChange={(e) => updateAddress('country', e.target.value)}
                placeholder="z.B. Deutschland"
              />
            </div>
            <div>
              <Label htmlFor="notes">Notizen</Label>
              <Textarea
                id="notes"
                value={contact.notes || ''}
                onChange={(e) => updateField('notes', e.target.value)}
                placeholder="Zusätzliche Informationen..."
                rows={4}
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

