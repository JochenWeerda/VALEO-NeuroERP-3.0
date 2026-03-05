import { useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { useToast } from '@/components/ui/toast-provider'

type Course = {
  id: string
  course_code: string
  title: string
  is_active: boolean
}

export default function SchulungNeuPage(): JSX.Element {
  const navigate = useNavigate()
  const { push } = useToast()

  const [employeeRef, setEmployeeRef] = useState('')
  const [courseId, setCourseId] = useState('')
  const [assignedBy, setAssignedBy] = useState('')
  const [dueDate, setDueDate] = useState('')

  const coursesQuery = useQuery({
    queryKey: ['training', 'courses'],
    queryFn: async () => (await apiClient.get<Course[]>('/api/v1/training/courses')).data,
    staleTime: 60_000,
  })

  const activeCourses = useMemo(
    () => (coursesQuery.data ?? []).filter((course) => course.is_active),
    [coursesQuery.data],
  )

  const saveMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post('/api/v1/training/assignments', {
        data: {
          employee_ref: employeeRef.trim(),
          course_id: courseId,
          assigned_by: assignedBy.trim() || null,
          due_date: dueDate || null,
          status: 'assigned',
        },
      })
    },
    onSuccess: () => {
      push('Schulung erfolgreich erfasst.')
      navigate('/personal/schulungen')
    },
    onError: (error) => {
      push(error instanceof Error ? error.message : 'Speichern fehlgeschlagen.')
    },
  })

  const submit = (): void => {
    if (!employeeRef.trim()) {
      push('Bitte Mitarbeiter-Referenz angeben.')
      return
    }
    if (!courseId) {
      push('Bitte Schulungskurs auswaehlen.')
      return
    }
    saveMutation.mutate()
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <ModuleToolbar backTarget="/personal/schulungen" closeTarget="/personal/schulungen" title="Schulung erfassen" />
      <div>
        <h1 className="text-3xl font-bold">Schulung erfassen</h1>
        <p className="text-muted-foreground">Neue Schulungszuweisung anlegen</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Basisdaten</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="employee-ref">Mitarbeiter-Referenz</Label>
            <Input
              id="employee-ref"
              value={employeeRef}
              onChange={(event) => setEmployeeRef(event.target.value)}
              placeholder="z. B. EMP-1001"
              disabled={saveMutation.isPending}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="course">Kurs</Label>
            <select
              id="course"
              className="w-full rounded-md border border-input bg-background px-3 py-2"
              value={courseId}
              onChange={(event) => setCourseId(event.target.value)}
              disabled={saveMutation.isPending || coursesQuery.isLoading}
            >
              <option value="">Bitte waehlen</option>
              {activeCourses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.course_code} - {course.title}
                </option>
              ))}
            </select>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="assigned-by">Zugewiesen von</Label>
              <Input
                id="assigned-by"
                value={assignedBy}
                onChange={(event) => setAssignedBy(event.target.value)}
                placeholder="z. B. teamlead"
                disabled={saveMutation.isPending}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="due-date">Faellig bis</Label>
              <Input
                id="due-date"
                type="date"
                value={dueDate}
                onChange={(event) => setDueDate(event.target.value)}
                disabled={saveMutation.isPending}
              />
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <Button variant="outline" onClick={() => navigate('/personal/schulungen')} disabled={saveMutation.isPending}>
              Abbrechen
            </Button>
            <Button onClick={submit} disabled={saveMutation.isPending || coursesQuery.isLoading}>
              {saveMutation.isPending ? 'Speichert...' : 'Speichern'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
