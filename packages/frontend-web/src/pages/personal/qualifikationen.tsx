import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  useCreateQualifikation,
  useQualifikationen,
  type QualificationLevel,
  type Qualifikation,
} from '@/lib/api/personal'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useToast } from '@/components/ui/toast-provider'

const levels: QualificationLevel[] = ['basic', 'advanced', 'expert']

export default function QualifikationenPage(): JSX.Element {
  const { push } = useToast()
  const { data: qualifikationen, isLoading } = useQualifikationen()
  const createMutation = useCreateQualifikation()

  const [employeeRef, setEmployeeRef] = useState('')
  const [roleCode, setRoleCode] = useState('')
  const [level, setLevel] = useState<QualificationLevel>('basic')
  const [skills, setSkills] = useState('')
  const [validUntil, setValidUntil] = useState('')

  const list = useMemo(() => qualifikationen ?? [], [qualifikationen])

  const save = (): void => {
    if (!employeeRef.trim() || !roleCode.trim()) {
      push('Bitte Mitarbeiter-Referenz und Rollen-Code angeben.')
      return
    }
    const skillList = skills
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
    createMutation.mutate(
      {
        employeeRef: employeeRef.trim(),
        roleCode: roleCode.trim(),
        qualificationLevel: level,
        skills: skillList,
        validUntil: validUntil || undefined,
      },
      {
        onSuccess: () => {
          push('Qualifikation gespeichert.')
          setEmployeeRef('')
          setRoleCode('')
          setLevel('basic')
          setSkills('')
          setValidUntil('')
        },
        onError: (error) => {
          push(getAxiosErrorMessage(error))
        },
      },
    )
  }

  const columns = [
    { key: 'employeeRef' as const, label: 'Mitarbeiter' },
    { key: 'roleCode' as const, label: 'Rolle' },
    {
      key: 'qualificationLevel' as const,
      label: 'Level',
      render: (item: Qualifikation) => <Badge variant="outline">{item.qualificationLevel}</Badge>,
    },
    {
      key: 'skills' as const,
      label: 'Skills',
      render: (item: Qualifikation) =>
        item.skills.length > 0 ? item.skills.join(', ') : <span className="text-muted-foreground">-</span>,
    },
    {
      key: 'validUntil' as const,
      label: 'Gueltig bis',
      render: (item: Qualifikation) =>
        item.validUntil ? new Date(item.validUntil).toLocaleDateString('de-DE') : <span className="text-muted-foreground">-</span>,
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Qualifikationen</h1>
        <p className="text-muted-foreground">Rollenbezogene Qualifikationsprofile</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Qualifikation erfassen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="employee-ref">Mitarbeiter-Referenz</Label>
              <Input id="employee-ref" value={employeeRef} onChange={(e) => setEmployeeRef(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="role-code">Rollen-Code</Label>
              <Input id="role-code" value={roleCode} onChange={(e) => setRoleCode(e.target.value)} />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="grid gap-2">
              <Label htmlFor="level">Level</Label>
              <select
                id="level"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={level}
                onChange={(e) => setLevel(e.target.value as QualificationLevel)}
              >
                {levels.map((entry) => (
                  <option key={entry} value={entry}>
                    {entry}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-2 md:col-span-2">
              <Label htmlFor="skills">Skills (kommagetrennt)</Label>
              <Input id="skills" value={skills} onChange={(e) => setSkills(e.target.value)} placeholder="z. B. HACCP, QS, Fuhrpark" />
            </div>
          </div>

          <div className="grid gap-2 md:w-64">
            <Label htmlFor="valid-until">Gueltig bis</Label>
            <Input id="valid-until" type="date" value={validUntil} onChange={(e) => setValidUntil(e.target.value)} />
          </div>

          <Button onClick={save} disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Speichert...' : 'Speichern'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Eintraege</CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          {isLoading ? <div className="text-sm text-muted-foreground">Laedt...</div> : <DataTable data={list} columns={columns} />}
        </CardContent>
      </Card>
    </div>
  )
}
