import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from '@/app/routing/react-router-compat'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  useCreateMitarbeiter,
  useMitarbeiterDetail,
  useUpdateMitarbeiter,
  type MitarbeiterInput,
  type MitarbeiterStatus,
} from '@/lib/api/personal'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useToast } from '@/components/ui/toast-provider'

const DEFAULT_FORM: MitarbeiterInput = {
  name: '',
  email: '',
  abteilung: 'Allgemein',
  position: 'mitarbeiter',
  status: 'aktiv',
}

export default function MitarbeiterStammPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams()
  const { push } = useToast()
  const isNew = id === 'neu' || !id

  const detailQuery = useMitarbeiterDetail(!isNew ? id : undefined)
  const createMutation = useCreateMitarbeiter()
  const updateMutation = useUpdateMitarbeiter(id || '')

  const [form, setForm] = useState<MitarbeiterInput>(DEFAULT_FORM)

  useEffect(() => {
    if (detailQuery.data) {
      setForm({
        name: detailQuery.data.name,
        email: detailQuery.data.email || '',
        abteilung: detailQuery.data.abteilung || 'Allgemein',
        position: detailQuery.data.position || 'mitarbeiter',
        status: detailQuery.data.status || 'aktiv',
      })
    }
  }, [detailQuery.data])

  const isSaving = createMutation.isPending || updateMutation.isPending
  const title = useMemo(() => (isNew ? 'Mitarbeiter neu' : 'Mitarbeiter bearbeiten'), [isNew])

  const save = (): void => {
    if (!form.name.trim() || !form.email.trim()) {
      push('Bitte Name und E-Mail angeben.')
      return
    }

    const onError = (error: unknown): void => {
      push(getAxiosErrorMessage(error))
    }
    if (isNew) {
      createMutation.mutate(form, {
        onSuccess: (created) => {
          push('Mitarbeiter angelegt.')
          navigate(`/personal/mitarbeiter/${created.id}`)
        },
        onError,
      })
      return
    }

    updateMutation.mutate(form, {
      onSuccess: () => {
        push('Mitarbeiter aktualisiert.')
      },
      onError,
    })
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">{title}</h1>
        <p className="text-muted-foreground">Personalstammdaten</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Basisdaten</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="name">Name</Label>
            <Input id="name" value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="email">E-Mail</Label>
            <Input id="email" type="email" value={form.email} onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))} />
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="grid gap-2">
              <Label htmlFor="abteilung">Abteilung</Label>
              <Input id="abteilung" value={form.abteilung} onChange={(e) => setForm((p) => ({ ...p, abteilung: e.target.value }))} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="position">Position</Label>
              <Input id="position" value={form.position} onChange={(e) => setForm((p) => ({ ...p, position: e.target.value }))} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={form.status}
                onChange={(e) => setForm((p) => ({ ...p, status: e.target.value as MitarbeiterStatus }))}
              >
                <option value="aktiv">aktiv</option>
                <option value="urlaub">urlaub</option>
                <option value="krank">krank</option>
              </select>
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate('/personal/mitarbeiter-liste')} disabled={isSaving}>
              Zurueck
            </Button>
            <Button onClick={save} disabled={isSaving || detailQuery.isLoading}>
              {isSaving ? 'Speichert...' : 'Speichern'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
