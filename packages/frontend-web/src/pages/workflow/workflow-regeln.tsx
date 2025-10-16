import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Plus } from 'lucide-react'

type WorkflowRule = {
  id: string
  triggerEntity: string
  triggerAction: string
  targetEntity: string
  targetAction: string
  condition?: string
  active: boolean
}

const mockRules: WorkflowRule[] = [
  {
    id: '1',
    triggerEntity: 'Anfrage',
    triggerAction: 'FREIGEGEBEN',
    targetEntity: 'Anfrage',
    targetAction: 'ANGEBOTSPHASE',
    active: true
  },
  {
    id: '2',
    triggerEntity: 'Angebot',
    triggerAction: 'GENEHMIGT',
    targetEntity: 'Bestellung',
    targetAction: 'CREATE_FROM_ANGEBOT',
    active: true
  },
  {
    id: '3',
    triggerEntity: 'Bestellung',
    triggerAction: 'FREIGEGEBEN',
    targetEntity: 'Auftragsbestaetigung',
    targetAction: 'CREATE_FROM_BESTELLUNG',
    active: true
  },
  {
    id: '4',
    triggerEntity: 'Bestellung',
    triggerAction: 'FREIGEGEBEN',
    targetEntity: 'Anlieferavis',
    targetAction: 'CREATE_FROM_BESTELLUNG',
    active: true
  },
  {
    id: '5',
    triggerEntity: 'Wareneingang',
    triggerAction: 'GEBUCHT',
    targetEntity: 'Rechnungseingang',
    targetAction: 'CREATE_FROM_WE',
    condition: 'status === "GEBUCHT"',
    active: true
  }
]

const entityOptions = [
  'Anfrage', 'Angebot', 'Bestellung', 'Auftragsbestaetigung',
  'Anlieferavis', 'Wareneingang', 'Rechnungseingang'
]

const actionOptions = [
  'ERFASST', 'FREIGEGEBEN', 'GEPRUEFT', 'GENEHMIGT',
  'BESTAETIGT', 'GEBUCHT', 'VOLLGELIEFERT', 'ABGELEHNT'
]

export default function WorkflowRegelnPage(): JSX.Element {
  const [rules, setRules] = useState<WorkflowRule[]>(mockRules)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<WorkflowRule | null>(null)

  const columns = [
    {
      key: 'triggerEntity' as const,
      label: 'Auslöser-Entität',
      render: (rule: WorkflowRule) => <Badge variant="outline">{rule.triggerEntity}</Badge>
    },
    {
      key: 'triggerAction' as const,
      label: 'Auslöser-Aktion',
      render: (rule: WorkflowRule) => <Badge variant="secondary">{rule.triggerAction}</Badge>
    },
    {
      key: 'targetEntity' as const,
      label: 'Ziel-Entität',
      render: (rule: WorkflowRule) => <Badge variant="outline">{rule.targetEntity}</Badge>
    },
    {
      key: 'targetAction' as const,
      label: 'Ziel-Aktion',
      render: (rule: WorkflowRule) => <Badge variant="default">{rule.targetAction}</Badge>
    },
    {
      key: 'condition' as const,
      label: 'Bedingung',
      render: (rule: WorkflowRule) => rule.condition ? <code className="text-xs">{rule.condition}</code> : '-'
    },
    {
      key: 'active' as const,
      label: 'Aktiv',
      render: (rule: WorkflowRule) => (
        <Badge variant={rule.active ? 'outline' : 'secondary'}>
          {rule.active ? 'Aktiv' : 'Inaktiv'}
        </Badge>
      )
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (rule: WorkflowRule) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleEdit(rule)}
          >
            Bearbeiten
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleToggleActive(rule)}
          >
            {rule.active ? 'Deaktivieren' : 'Aktivieren'}
          </Button>
        </div>
      )
    }
  ]

  const handleEdit = (rule: WorkflowRule) => {
    setEditingRule(rule)
    setIsDialogOpen(true)
  }

  const handleToggleActive = (rule: WorkflowRule) => {
    setRules(prev => prev.map(r =>
      r.id === rule.id ? { ...r, active: !r.active } : r
    ))
  }

  const handleSave = (ruleData: Partial<WorkflowRule>) => {
    if (editingRule) {
      // Update existing rule
      setRules(prev => prev.map(r =>
        r.id === editingRule.id ? { ...r, ...ruleData } : r
      ))
    } else {
      // Add new rule
      const newRule: WorkflowRule = {
        id: Date.now().toString(),
        triggerEntity: ruleData.triggerEntity || '',
        triggerAction: ruleData.triggerAction || '',
        targetEntity: ruleData.targetEntity || '',
        targetAction: ruleData.targetAction || '',
        condition: ruleData.condition,
        active: ruleData.active ?? true
      }
      setRules(prev => [...prev, newRule])
    }
    setIsDialogOpen(false)
    setEditingRule(null)
  }

  const handleAddNew = () => {
    setEditingRule(null)
    setIsDialogOpen(true)
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Workflow-Regeln</h1>
          <p className="text-muted-foreground">Automatische Statusübergänge zwischen Belegen</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={handleAddNew} className="gap-2">
              <Plus className="h-4 w-4" />
              Neue Regel
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingRule ? 'Workflow-Regel bearbeiten' : 'Neue Workflow-Regel'}
              </DialogTitle>
            </DialogHeader>
            <WorkflowRuleForm
              rule={editingRule}
              onSave={handleSave}
              onCancel={() => setIsDialogOpen(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Aktive Regeln ({rules.filter(r => r.active).length})</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable data={rules} columns={columns} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Workflow-Beispiele</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold mb-2">Anfrage → Angebot</h4>
              <p className="text-sm text-muted-foreground mb-2">
                Wenn eine Anfrage freigegeben wird, wechselt sie automatisch in die Angebotsphase.
              </p>
              <code className="text-xs bg-muted p-2 rounded block">
                Anfrage:FREIGEGEBEN → Anfrage:ANGEBOTSPHASE
              </code>
            </div>
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold mb-2">Angebot → Bestellung</h4>
              <p className="text-sm text-muted-foreground mb-2">
                Genehmigte Angebote können automatisch in Bestellungen umgewandelt werden.
              </p>
              <code className="text-xs bg-muted p-2 rounded block">
                Angebot:GENEHMIGT → Bestellung:CREATE_FROM_ANGEBOT
              </code>
            </div>
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold mb-2">Bestellung → Folgebelege</h4>
              <p className="text-sm text-muted-foreground mb-2">
                Freigegebene Bestellungen erzeugen automatisch AB und Avis.
              </p>
              <code className="text-xs bg-muted p-2 rounded block">
                Bestellung:FREIGEGEBEN → Auftragsbestätigung + Anlieferavis
              </code>
            </div>
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold mb-2">Wareneingang → Rechnung</h4>
              <p className="text-sm text-muted-foreground mb-2">
                Gebuchte Wareneingänge können automatisch Rechnungen erstellen.
              </p>
              <code className="text-xs bg-muted p-2 rounded block">
                Wareneingang:GEBUCHT → Rechnungseingang:CREATE_FROM_WE
              </code>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

interface WorkflowRuleFormProps {
  rule: WorkflowRule | null
  onSave: (rule: Partial<WorkflowRule>) => void
  onCancel: () => void
}

function WorkflowRuleForm({ rule, onSave, onCancel }: WorkflowRuleFormProps): JSX.Element {
  const [formData, setFormData] = useState<Partial<WorkflowRule>>(rule || {
    active: true
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label>Auslöser-Entität</Label>
          <Select
            value={formData.triggerEntity}
            onValueChange={(value) => setFormData(prev => ({ ...prev, triggerEntity: value }))}
          >
            <SelectTrigger>
              <SelectValue placeholder="Entität auswählen" />
            </SelectTrigger>
            <SelectContent>
              {entityOptions.map(entity => (
                <SelectItem key={entity} value={entity}>{entity}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label>Auslöser-Aktion</Label>
          <Select
            value={formData.triggerAction}
            onValueChange={(value) => setFormData(prev => ({ ...prev, triggerAction: value }))}
          >
            <SelectTrigger>
              <SelectValue placeholder="Aktion auswählen" />
            </SelectTrigger>
            <SelectContent>
              {actionOptions.map(action => (
                <SelectItem key={action} value={action}>{action}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label>Ziel-Entität</Label>
          <Select
            value={formData.targetEntity}
            onValueChange={(value) => setFormData(prev => ({ ...prev, targetEntity: value }))}
          >
            <SelectTrigger>
              <SelectValue placeholder="Entität auswählen" />
            </SelectTrigger>
            <SelectContent>
              {entityOptions.map(entity => (
                <SelectItem key={entity} value={entity}>{entity}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label>Ziel-Aktion</Label>
          <Input
            value={formData.targetAction}
            onChange={(e) => setFormData(prev => ({ ...prev, targetAction: e.target.value }))}
            placeholder="z.B. CREATE_FROM_..."
          />
        </div>
      </div>
      <div>
        <Label>Bedingung (optional)</Label>
        <Input
          value={formData.condition}
          onChange={(e) => setFormData(prev => ({ ...prev, condition: e.target.value }))}
          placeholder="z.B. status === 'GEBUCHT'"
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Abbrechen
        </Button>
        <Button type="submit">
          Speichern
        </Button>
      </div>
    </form>
  )
}