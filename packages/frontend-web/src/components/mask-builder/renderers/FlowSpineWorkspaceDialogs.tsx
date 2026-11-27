import { lazy, Suspense } from 'react'
import { Building2 } from 'lucide-react'
import type { CustomerLite } from '@/components/crm/CustomerCombobox'
import type { Customer } from '@/components/sales/CustomerSelectionDialog'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'
import type { FlowSpineWorkspaceRuntime } from '../runtime/useFlowSpineWorkspaceRuntime'
const CustomerCombobox = lazy(() => import('@/components/crm/CustomerCombobox').then(m => ({ default: m.CustomerCombobox })))
const CustomerSelectionDialog = lazy(() => import('@/components/sales/CustomerSelectionDialog').then(m => ({ default: m.CustomerSelectionDialog })))
const REASON_CATEGORY_OPTIONS = [
  { value: 'customer', label: 'Kunde' },
  { value: 'supplier', label: 'Lieferant' },
  { value: 'logistics', label: 'Logistik' },
  { value: 'quality', label: 'Qualitaet' },
  { value: 'finance', label: 'Finanzen' },
  { value: 'compliance', label: 'Compliance' },
  { value: 'technical', label: 'Technik' },
  { value: 'internal', label: 'Intern' },
]

/**
 * FSX-003 Fall 3 — ein operatives Feld ohne ermittelbaren Wert.
 *
 * Bewusst sichtbar und benannt: ein leerer Bereich liest sich wie ein Ladefehler,
 * ein Vorgabewert aus dem Prozessregister waere eine Falschaussage. „Nicht
 * ermittelt“ ist die einzige ehrliche dritte Moeglichkeit.
 */

export function FlowSpineWorkspaceDialogs({ state }: { state: FlowSpineWorkspaceRuntime }): JSX.Element {
  const { processKey, instanceId, navigate, location, startConfig, workspaceQuery, workspace, nodes, selectedNode, processNavItems, viewMode, setViewMode, showNodeDetails, showSideFlaechen, copilotOpen, setCopilotOpen, progressWidth, go, handleAction, handleAgentAction, handleCreateInstance, openLifecycleDialog, closeLifecycleDialog, handleSaveLifecycle, handleResumeLifecycle, handleSubmitLifecycleDialog, setSelectedNodeId, showNewInstanceDialog, setShowNewInstanceDialog, newInstanceLabel, setNewInstanceLabel, newInstancePartnerName, setNewInstancePartnerName, newInstanceSubject, setNewInstanceSubject, newInstanceEntryMode, setNewInstanceEntryMode, newInstanceCustomer, setNewInstanceCustomer, showAdvancedCustomerSearch, setShowAdvancedCustomerSearch, createInstance, executeAction, executeAgentAction, instanceSearch, setInstanceSearch, instancesQuery, timelineQuery, saveInstance, resumeInstance, holdInstance, completeInstance, cancelInstance, failInstance, lifecycleDialog, setLifecycleDialog } = state
  const lifecycleBusy = saveInstance.isPending || resumeInstance.isPending || holdInstance.isPending || completeInstance.isPending || cancelInstance.isPending || failInstance.isPending
  return (<>
      <Dialog open={showNewInstanceDialog} onOpenChange={setShowNewInstanceDialog}>
          <DialogContent className="border-border bg-card text-foreground">
          <DialogHeader>
            <DialogTitle>{startConfig.dialogTitle}</DialogTitle>
            <DialogDescription className="text-muted-foreground">{startConfig.dialogDescription}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid gap-3 md:grid-cols-3">
              {startConfig.entryModes.map((mode) => (
                    <button
                      key={mode.value}
                      type="button"
                      onClick={() => setNewInstanceEntryMode(mode.value)}
                      className={cn(
                        'rounded-2xl border px-4 py-3 text-left text-sm transition',
                        newInstanceEntryMode === mode.value
                          ? 'border-primary/60 bg-primary/15 text-primary'
                          : 'border-border bg-muted text-muted-foreground hover:bg-muted',
                      )}
                    >
                      <div className="font-medium">{mode.value}</div>
                      <div className="mt-1 text-xs text-muted-foreground">{mode.description}</div>
                    </button>
                  ))}
            </div>
            <div className="space-y-2">
              <Label htmlFor="instance-partner" className="text-muted-foreground">{startConfig.partnerLabel}</Label>
              {processKey === 'order-to-cash' ? (
                <Suspense fallback={<div className="h-10 animate-pulse rounded bg-muted" />}><CustomerCombobox
                  id="instance-partner"
                  value={newInstanceCustomer}
                  onChange={(c) => {
                    setNewInstanceCustomer(c)
                    setNewInstancePartnerName(c ? c.company_name : '')
                  }}
                  onCreateNew={(initialName) => {
                    const currentHref = `${location.pathname}${location.search}`
                    const params = new URLSearchParams()
                    params.set('returnTo', currentHref)
                    if (initialName) params.set('initialName', initialName)
                    if (newInstanceSubject.trim()) params.set('subject', newInstanceSubject.trim())
                    if (newInstanceLabel.trim()) params.set('label', newInstanceLabel.trim())
                    navigate(`/verkauf/kunde-neu?${params.toString()}`)
                  }}
                  onOpenAdvanced={() => setShowAdvancedCustomerSearch(true)}
                  placeholder="Kunde suchen (Name oder Nummer) …"
                /></Suspense>
              ) : (
                <div className="relative">
                  <Building2 className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="instance-partner"
                    value={newInstancePartnerName}
                    onChange={(e) => setNewInstancePartnerName(e.target.value)}
                    placeholder="z.B. Agrarhandel Nord eG"
                    className="border-border bg-muted pl-9 text-foreground placeholder:text-muted-foreground"
                  />
                </div>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="instance-subject" className="text-muted-foreground">{startConfig.subjectLabel}</Label>
              <Input
                id="instance-subject"
                value={newInstanceSubject}
                onChange={(e) => setNewInstanceSubject(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') void handleCreateInstance() }}
                placeholder="z.B. Themenbeschreibung oder operative Referenz"
                className="border-border bg-muted text-foreground placeholder:text-muted-foreground"
              />
            </div>
            <div className="rounded-2xl border border-border bg-muted/50 px-4 py-3 text-sm text-muted-foreground">
              <div className="font-medium text-foreground">Praxislogik</div>
              <div className="mt-1">{startConfig.explanation}</div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="instance-label" className="text-muted-foreground">{startConfig.labelLabel}</Label>
              <Input
                id="instance-label"
                value={newInstanceLabel}
                onChange={(e) => setNewInstanceLabel(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') void handleCreateInstance() }}
                placeholder={startConfig.labelPlaceholder}
                className="border-border bg-muted text-foreground placeholder:text-muted-foreground"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => { setShowNewInstanceDialog(false); setNewInstanceLabel(''); setNewInstancePartnerName(''); setNewInstanceSubject(''); setNewInstanceEntryMode(startConfig.entryModes[0]?.value ?? 'Direktauftrag'); setNewInstanceCustomer(null) }}
              className="border-border bg-muted text-foreground hover:bg-muted"
            >
              Abbrechen
            </Button>
            <Button
              onClick={() => void handleCreateInstance()}
              disabled={(!newInstanceLabel.trim() && !newInstancePartnerName.trim() && !newInstanceSubject.trim()) || createInstance.isPending}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {createInstance.isPending ? 'Wird erstellt...' : startConfig.submitLabel}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={!!lifecycleDialog} onOpenChange={(open) => { if (!open) closeLifecycleDialog() }}>
        <DialogContent className="border-border bg-card text-foreground">
          <DialogHeader>
            <DialogTitle>
              {lifecycleDialog?.mode === 'hold' && 'Vorgang pausieren'}
              {lifecycleDialog?.mode === 'complete' && 'Vorgang abschliessen'}
              {lifecycleDialog?.mode === 'cancel' && 'Vorgang abbrechen'}
              {lifecycleDialog?.mode === 'fail' && 'Vorgang als gescheitert markieren'}
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Der Dialog ist bewusst prozessneutral. Flow-spezifische Grundkataloge folgen in einem spaeteren Slice.
            </DialogDescription>
          </DialogHeader>
          {lifecycleDialog ? (
            <div className="space-y-4 py-2">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label className="text-muted-foreground">Business-Status</Label>
                  <Input
                    value={lifecycleDialog.businessStatus}
                    onChange={(e) => setLifecycleDialog({ ...lifecycleDialog, businessStatus: e.target.value })}
                    placeholder="z.B. lieferung_blockiert"
                    className="border-border bg-muted text-foreground placeholder:text-muted-foreground"
                  />
                </div>
                {lifecycleDialog.mode === 'hold' ? (
                  <div className="space-y-2">
                    <Label className="text-muted-foreground">Blockiert bis</Label>
                    <Input
                      type="datetime-local"
                      value={lifecycleDialog.blockedUntil}
                      onChange={(e) => setLifecycleDialog({ ...lifecycleDialog, blockedUntil: e.target.value })}
                      className="border-border bg-muted text-foreground"
                    />
                  </div>
                ) : null}
              </div>

              {lifecycleDialog.mode !== 'complete' ? (
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label className="text-muted-foreground">
                      Kategorie <span className="text-status-error">*</span>
                    </Label>
                    <Select
                      value={lifecycleDialog.reasonCategory}
                      onValueChange={(value) => setLifecycleDialog({ ...lifecycleDialog, reasonCategory: value })}
                    >
                      <SelectTrigger
                        aria-required="true"
                        className={cn(
                          'border-border bg-muted text-foreground',
                          !lifecycleDialog.reasonCategory && 'border-status-error/40',
                        )}
                      >
                        <SelectValue placeholder="Kategorie waehlen …" />
                      </SelectTrigger>
                      <SelectContent>
                        {REASON_CATEGORY_OPTIONS.map((option) => (
                          <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {!lifecycleDialog.reasonCategory && (
                      <p className="text-2xs text-status-error">Pflichtfeld</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label className="text-muted-foreground">
                      Grundcode <span className="text-status-error">*</span>
                    </Label>
                    <Input
                      aria-required="true"
                      value={lifecycleDialog.reasonCode}
                      onChange={(e) => setLifecycleDialog({ ...lifecycleDialog, reasonCode: e.target.value })}
                      placeholder="z.B. customer_order_cancelled"
                      className={cn(
                        'border-border bg-muted text-foreground placeholder:text-muted-foreground',
                        !lifecycleDialog.reasonCode.trim() && 'border-status-error/40',
                      )}
                    />
                    {!lifecycleDialog.reasonCode.trim() && (
                      <p className="text-2xs text-status-error">Pflichtfeld</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <Label className="text-muted-foreground">Abschlusscode</Label>
                  <Input
                    value={lifecycleDialog.reasonCode}
                    onChange={(e) => setLifecycleDialog({ ...lifecycleDialog, reasonCode: e.target.value })}
                    placeholder="z.B. workflow_completed"
                    className="border-border bg-muted text-foreground placeholder:text-muted-foreground"
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label className="text-muted-foreground">Bemerkung</Label>
                <Textarea
                  value={lifecycleDialog.reasonNote}
                  onChange={(e) => setLifecycleDialog({ ...lifecycleDialog, reasonNote: e.target.value })}
                  placeholder="Freitext fuer Ursache, Kontext oder Lessons Learned"
                  className="min-h-[110px] border-border bg-muted text-foreground placeholder:text-muted-foreground"
                />
              </div>
            </div>
          ) : null}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={closeLifecycleDialog}
              className="border-border bg-muted text-foreground hover:bg-muted"
            >
              Abbrechen
            </Button>
            <Button
              onClick={() => void handleSubmitLifecycleDialog()}
              disabled={
                !lifecycleDialog ||
                lifecycleBusy ||
                (lifecycleDialog.mode !== 'complete' &&
                  (!lifecycleDialog.reasonCategory || !lifecycleDialog.reasonCode.trim()))
              }
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {lifecycleBusy ? 'Wird gespeichert...' : 'Bestaetigen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {processKey === 'order-to-cash' ? (
        <Suspense fallback={null}><CustomerSelectionDialog
          open={showAdvancedCustomerSearch}
          onClose={() => setShowAdvancedCustomerSearch(false)}
          onSelect={(customer: Customer) => {
            const selected: CustomerLite = {
              id: customer.id,
              customer_number: customer.customer_number ?? customer.customerNumber ?? '',
              company_name: customer.company_name ?? customer.name ?? '',
              city: customer.city ?? customer.address?.city ?? null,
              postal_code: customer.postalCode ?? customer.address?.postalCode ?? null,
              is_active: customer.is_active,
            }
            setNewInstanceCustomer(selected)
            setNewInstancePartnerName(selected.company_name)
            setShowAdvancedCustomerSearch(false)
          }}
          title="Erweiterte Kundensuche"
        /></Suspense>
      ) : null}
  </>)
}
