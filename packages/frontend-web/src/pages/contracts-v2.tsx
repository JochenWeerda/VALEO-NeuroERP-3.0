/**
 * Contracts Page V2
 * CRUD interface for managing contracts with Amendment support
 */

import React, { useState, useMemo } from 'react';
import { useNavigate } from '@/app/routing/typed-router';
import { useTranslation } from 'react-i18next';
import { toast } from '@/hooks/use-toast';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Toolbar } from '@/components/ui/toolbar';
import { DetailDrawer } from '@/components/ui/detail-drawer';
import { CrudDeleteDialog, CrudCancelDialog, CrudAuditTrailPanel, CrudPrintButton } from '@/features/crud/components';
import type { ChangeLog } from '@/features/crud/components/CrudAuditTrailPanel';
import { useCrudDelete, useCrudCancel, useCrudAuditTrail } from '@/features/crud/hooks';
import { Badge } from '@/components/ui/badge';
import { getEntityTypeLabel, getListTitle, getDetailTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { NativeSelect } from '@/components/ui/native-select';
import { useAuth } from '@/hooks/useAuth';
import { apiClient } from '@/lib/api-client';
import { useTenant } from '@/hooks/useTenant';
import { summarizeContractHedge } from '@/lib/professional-control-centers';
import { summarizeContractOperations } from '@/lib/domain-depth';
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader';
import { normalizeOperationalStatus } from '@/lib/operational-status';

interface Contract {
  id: string;
  sourceType?: 'agrar' | 'rahmen' | 'kon';
  contractNo: string;
  type: string;
  commodity: string;
  counterpartyId: string;
  status: string;
  contractClass?: string | null;
  contractGroup?: string | null;
  contractVariant?: string | null;
  parityCode?: string | null;
  dispositionFlag?: string | null;
  hedgeQuotePct?: number | null;
  marketValuationEur?: number | null;
  dunningLevel?: number | null;
  writeoffCandidate?: boolean;
  printReady?: boolean;
  alternateArticles?: string[];
  qty: {
    contracted: number;
    unit: string;
  };
  deliveryWindow: {
    from: string;
    to: string;
  };
  createdAt: string;
  updatedAt: string;
}

function daysUntil(dateValue: string): number | null {
  const target = new Date(dateValue);
  if (Number.isNaN(target.getTime())) return null;
  const now = new Date();
  return Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

function getSourceBadgeLabel(sourceType?: Contract['sourceType']): string {
  if (sourceType === 'kon') return 'Kontraktmodul';
  if (sourceType === 'rahmen') return 'Rahmenvertrag';
  if (sourceType === 'agrar') return 'Agrar / Flow Spine';
  return 'Allgemein';
}

interface Amendment {
  id: string;
  contractId: string;
  type: string;
  reason: string;
  status: string;
  changes: Record<string, unknown>;
  createdAt: string;
}

interface AmendmentTemplate {
  id: string;
  code: string;
  name: string;
  description: string;
  bodyMarkdown?: string;
  sectionsSchema?: Record<string, unknown>;
  isActive: boolean;
}

export default function ContractsPageV2(): JSX.Element {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { user } = useAuth();
  const { tenantId } = useTenant();
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [amendments, setAmendments] = useState<Amendment[]>([]);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [amendmentDialogOpen, setAmendmentDialogOpen] = useState(false);
  const [amendmentTemplates, setAmendmentTemplates] = useState<AmendmentTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<AmendmentTemplate | null>(null);
  const [amendmentForm, setAmendmentForm] = useState({
    type: '',
    reason: '',
    changes: {} as Record<string, unknown>,
  });

  const entityType = 'contract';
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Contract');

  // Fetch contracts
  React.useEffect(() => {
    const fetchContracts = async () => {
      setIsLoading(true);
      try {
        const res = await apiClient.get<{ items: Contract[] }>('/api/v1/kontrakte?limit=100');
        setContracts(res.data?.items ?? []);
      } catch {
        setContracts([]);
      } finally {
        setIsLoading(false);
      }
    };
    fetchContracts();
  }, []);

  // Fetch amendments for selected contract
  React.useEffect(() => {
    if (!selectedContract) {
      setAmendments([]);
      return;
    }

    const fetchAmendments = async () => {
      try {
        const res = await apiClient.get<{ items: Amendment[] }>(`/api/v1/kontrakte/${selectedContract.id}/amendments`);
        setAmendments(res.data?.items ?? []);
      } catch {
        setAmendments([]);
      }
    };
    fetchAmendments();
  }, [selectedContract]);

  // Amendment-Vorlagen laden, wenn Dialog geöffnet wird
  React.useEffect(() => {
    if (!amendmentDialogOpen) return;
    const fetchTemplates = async () => {
      try {
        const res = await apiClient.get<{ items: AmendmentTemplate[] }>('/api/v1/kontrakte/amendment-templates?activeOnly=true');
        setAmendmentTemplates(res.data?.items ?? []);
      } catch {
        setAmendmentTemplates([]);
      }
    };
    fetchTemplates();
  }, [amendmentDialogOpen]);

  // Delete handler
  const handleDelete = async (id: string, reason: string) => {
    await apiClient.delete(`/api/v1/kontrakte/${id}`, { data: { reason, tenantId } });
    setContracts(contracts.filter(c => c.id !== id));
    setSelectedContract(null);
  };

  const {
    deleteDialogOpen,
    setDeleteDialogOpen,
    handleDelete: handleDeleteClick,
    handleConfirmDelete,
    isDeleting,
    entityToDelete,
  } = useCrudDelete({
    onDelete: handleDelete,
    entityType: entityTypeLabel,
  });

  // Cancel handler
  const handleCancel = async (id: string, reason: string) => {
    const res = await apiClient.post<Contract>(`/api/v1/kontrakte/${id}/cancel`, { reason, tenantId, cancelledBy: user?.sub ?? 'current-user' });
    setContracts(contracts.map(c => c.id === id ? res.data : c));
    setSelectedContract(null);
  };

  const {
    cancelDialogOpen,
    setCancelDialogOpen,
    handleCancel: handleCancelClick,
    handleConfirmCancel,
    isCancelling,
    entityToCancel,
  } = useCrudCancel({
    onCancel: handleCancel,
    entityType: entityTypeLabel,
  });

  // Create amendment handler
  const handleCreateAmendment = async () => {
    if (!selectedContract || !amendmentForm.reason || amendmentForm.reason.trim().length < 10) {
      toast({ title: 'Pflichtfeld', description: t('crud.dialogs.amend.errorRequired', { defaultValue: 'Bitte geben Sie einen Änderungsgrund mit mindestens 10 Zeichen an.' }), variant: 'destructive' });
      return;
    }

    try {
      const res = await apiClient.post<Amendment>(`/api/v1/kontrakte/${selectedContract.id}/amendments`, {
        contractId: selectedContract.id,
        tenantId,
        type: amendmentForm.type,
        reason: amendmentForm.reason,
        changes: amendmentForm.changes,
        createdBy: user?.sub ?? 'current-user',
      });
      setAmendments([...amendments, res.data]);
      setAmendmentDialogOpen(false);
      setSelectedTemplate(null);
      setAmendmentForm({ type: '', reason: '', changes: {} });
    } catch (error) {
      toast({ title: 'Fehler', description: t('crud.messages.createError', { entityType: t('crud.entities.amendment', { defaultValue: 'Änderung' }), defaultValue: 'Erstellen fehlgeschlagen.' }), variant: 'destructive' });
    }
  };

  // Audit trail
  const fetchAuditTrail = async (entityType: string, entityId: string) => {
    try {
      const res = await apiClient.get<{ data: ChangeLog[] }>(`/api/v1/audit/change-logs/audit-trail/${entityType}/${entityId}`);
      return res.data?.data || [];
    } catch {
      return [];
    }
  };

  const {
    changeLogs,
    isLoading: isLoadingAudit,
  } = useCrudAuditTrail({
    entityType: entityTypeLabel,
    entityId: selectedContract?.id || null,
    fetchAuditTrail,
    enabled: !!selectedContract,
  });

  // Filter contracts
  const filtered = useMemo(() => {
    if (!query) return contracts;
    const q = query.toLowerCase();
    return contracts.filter(
      c =>
        c.contractNo.toLowerCase().includes(q) ||
        c.commodity.toLowerCase().includes(q) ||
        c.type.toLowerCase().includes(q)
    );
  }, [contracts, query]);

  const getStatusColor = (status: string) => {
    const statusLower = status.toLowerCase();
    switch (statusLower) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'fulfilled':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleCopilot = () => {
    navigate('/admin/control-center/agent-ops?context=contracts&intent=margin-risk-review');
    toast({
      title: 'Agent Ops geoeffnet',
      description: 'Vertragspruefungen laufen jetzt ueber den Leitstand fuer Preis-, Mengen- und Aenderungsrisiken.',
    });
  };

  const openContractEditWorkspace = (contract: Contract) => {
    if (contract.sourceType === 'kon') {
      navigate(`/kontrakte/${contract.id}`);
      return;
    }
    if (contract.sourceType === 'rahmen') {
      navigate(`/vertrag/${contract.id}`);
      return;
    }
    if (contract.sourceType === 'agrar') {
      navigate(`/workflow/flow-spine-contract-to-settlement?contractId=${encodeURIComponent(contract.id)}`);
      toast({
        title: 'Prozessarbeitsplatz geoeffnet',
        description: 'Agrarvertraege werden ueber den zugeordneten Flow-Spine-Arbeitsplatz weiterbearbeitet.',
      });
      return;
    }
    navigate(`/kontrakte/${contract.id}`);
  };

  const openContractWorkspace = (contract: Contract) => {
    openContractEditWorkspace(contract);
  };

  const openContractAlarms = () => navigate('/kontrakte/alarme');
  const openContractPositions = () => navigate('/kontrakte/positionen');
  const openContractOverview = () => navigate('/kontrakte');

  const openContracts = useMemo(
    () => contracts.filter((contract) => !['cancelled', 'fulfilled'].includes(contract.status.toLowerCase())),
    [contracts],
  );

  const expiringContracts = useMemo(
    () =>
      openContracts.filter((contract) => {
        const days = daysUntil(contract.deliveryWindow.to);
        return days !== null && days >= 0 && days <= 30;
      }),
    [openContracts],
  );

  const sourceBreakdown = useMemo(
    () => ({
      kon: contracts.filter((contract) => contract.sourceType === 'kon').length,
      rahmen: contracts.filter((contract) => contract.sourceType === 'rahmen').length,
      agrar: contracts.filter((contract) => contract.sourceType === 'agrar').length,
      unknown: contracts.filter((contract) => !contract.sourceType).length,
    }),
    [contracts],
  );

  const nextActionContract = useMemo(() => {
    const expiring = expiringContracts[0];
    if (expiring) return expiring;
    return openContracts[0] ?? null;
  }, [expiringContracts, openContracts]);
  const hedgeSummary = useMemo(() => summarizeContractHedge(contracts), [contracts]);
  const contractOps = useMemo(() => summarizeContractOperations(contracts), [contracts]);
  const operationalStatus = normalizeOperationalStatus(contractOps.operatorPressure);

  return (
    <div className="space-y-4">
      <OperationalCaseHeader
        title="Kontraktübersicht"
        status={operationalStatus}
        blocker={contractOps.unhedgedCount > 0 ? `${contractOps.unhedgedCount} ungesicherte Kontrakte` : null}
        nextAction={contractOps.nextAction}
        caseLabel="Kontrakte"
        tags={contractOps.dunningCount > 0 ? [`${contractOps.dunningCount} Mahnung(en)`] : []}
      />
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">{entityTypeLabel}</h2>
        <div className="flex gap-2">
          <CrudPrintButton
            listData={filtered}
            listColumns={[
              { header: t('crud.fields.number'), field: 'contractNo' },
              { header: t('crud.fields.type'), field: 'type' },
              { header: t('crud.fields.commodity'), field: 'commodity' },
              { header: t('crud.fields.status'), field: 'status' },
              { header: t('crud.fields.quantity'), field: 'qty.contracted' },
            ]}
            entityType={entityTypeLabel}
            printTitle={getListTitle(t, entityTypeLabel)}
          />
          <Button onClick={() => navigate('/kontrakte/neu')}>
            {t('crud.actions.createContract')}
          </Button>
        </div>
      </div>

      <Toolbar
        onSearch={setQuery}
        onCopilot={handleCopilot}
      />

      <div className="grid gap-4 md:grid-cols-4">
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Offene Kontrakte</div>
          <div className="mt-2 text-2xl font-semibold">{openContracts.length}</div>
          <p className="mt-1 text-xs text-muted-foreground">Aktiv bearbeitbare Vertragsobjekte</p>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Ablauf in 30 Tagen</div>
          <div className="mt-2 text-2xl font-semibold">{expiringContracts.length}</div>
          <p className="mt-1 text-xs text-muted-foreground">Frühwarnung für Mengen- und Friststeuerung</p>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Kontraktmodul</div>
          <div className="mt-2 text-2xl font-semibold">{sourceBreakdown.kon}</div>
          <p className="mt-1 text-xs text-muted-foreground">Direkt im Kontrakt-Arbeitsplatz gepflegt</p>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Flow / Rahmen</div>
          <div className="mt-2 text-2xl font-semibold">{sourceBreakdown.agrar + sourceBreakdown.rahmen}</div>
          <p className="mt-1 text-xs text-muted-foreground">Quellenübergreifende Vertragsherkunft</p>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Hedge-Luecken</div>
          <div className="mt-2 text-2xl font-semibold">{hedgeSummary.hedgeGapCount}</div>
          <p className="mt-1 text-xs text-muted-foreground">Absicherung und Fixierungsbedarf im Bestand</p>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Marktwertdruck</div>
          <div className="mt-2 text-2xl font-semibold">{hedgeSummary.marketPressureCount}</div>
          <p className="mt-1 text-xs text-muted-foreground">Kontrakte mit negativer Bewertung zum Markt</p>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Mahnkontext</div>
          <div className="mt-2 text-2xl font-semibold">{hedgeSummary.dunningPressureCount}</div>
          <p className="mt-1 text-xs text-muted-foreground">Rueckstaende mit Einfluss auf Washout oder Abwicklung</p>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Naechster Hedge-Schritt</div>
          <div className="mt-2 text-sm font-semibold">{hedgeSummary.nextAction}</div>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Operator-Druck</div>
          <div className="mt-2 text-lg font-semibold">{contractOps.operatorPressure}</div>
          <p className="mt-1 text-xs text-muted-foreground">Fixierung, Markt und Mahnung als gemeinsamer Operatorzustand</p>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Ungesicherte Mengen</div>
          <div className="mt-2 text-2xl font-semibold">{contractOps.unhedgedCount}</div>
          <p className="mt-1 text-xs text-muted-foreground">Kontrakte mit offenem Fixierungs- oder Hedgebedarf</p>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Naechster Operatorpfad</div>
          <div className="mt-2 text-sm font-semibold">{contractOps.nextAction}</div>
          <p className="mt-1 text-xs text-muted-foreground">Arbeitsfokus fuer Markt, Mahnung oder Abschreibung</p>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <Card className="p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h3 className="font-semibold">Kontrakt-Steuerung</h3>
              <p className="text-sm text-muted-foreground">Schneller Einstieg in die vorhandenen Risiko- und Detailarbeitsplätze.</p>
            </div>
            <Badge variant="outline">Profi-Arbeitsplatz</Badge>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button variant="outline" onClick={openContractOverview}>Kontraktliste</Button>
            <Button variant="outline" onClick={openContractPositions}>Positionsmonitor</Button>
            <Button variant="outline" onClick={openContractAlarms}>Alarmdashboard</Button>
            <Button variant="outline" onClick={openContractPositions}>Hedge / Fixierung</Button>
            <Button variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumentenablage</Button>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <div className="rounded-lg border p-3">
              <div className="text-xs uppercase tracking-wide text-muted-foreground">Quellenbild</div>
              <div className="mt-2 space-y-1 text-sm">
                <p>Kontraktmodul: {sourceBreakdown.kon}</p>
                <p>Rahmenvertrag: {sourceBreakdown.rahmen}</p>
                <p>Agrar / Flow Spine: {sourceBreakdown.agrar}</p>
                {sourceBreakdown.unknown > 0 ? <p>Ohne Quelltyp: {sourceBreakdown.unknown}</p> : null}
                <p>Mahnfaelle: {contractOps.dunningCount}</p>
              </div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-xs uppercase tracking-wide text-muted-foreground">Arbeitslage</div>
              <div className="mt-2 space-y-1 text-sm">
                <p>{expiringContracts.length > 0 ? `${expiringContracts.length} Kontrakte laufen in 30 Tagen ab.` : 'Keine kurzfristigen Ablauffristen im gefilterten Bestand.'}</p>
                <p>{openContracts.length > 0 ? `${openContracts.length} offene Kontrakte erfordern aktive Steuerung.` : 'Keine offenen Kontrakte im aktuellen Bestand.'}</p>
                <p>{contractOps.nextAction}</p>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <h3 className="font-semibold">Nächste empfohlene Aktion</h3>
          {nextActionContract ? (
            <div className="mt-3 space-y-3">
              <div>
                <p className="font-medium">{nextActionContract.contractNo}</p>
                <p className="text-sm text-muted-foreground">
                  {nextActionContract.commodity} · {getSourceBadgeLabel(nextActionContract.sourceType)}
                </p>
              </div>
              <p className="text-sm text-muted-foreground">
                {(() => {
                  const days = daysUntil(nextActionContract.deliveryWindow.to);
                  if (days !== null && days >= 0 && days <= 30) {
                    return `Friststeuerung priorisieren: Kontrakt läuft in ${days} Tagen ab.`;
                  }
                  return 'Vertrag in den passenden Arbeitsplatz ziehen und Mengen-, Preis- oder Änderungslogik prüfen.';
                })()}
              </p>
              <div className="flex flex-wrap gap-2">
                <Button size="sm" onClick={() => openContractWorkspace(nextActionContract)}>Arbeitsplatz öffnen</Button>
                <Button size="sm" variant="outline" onClick={() => setSelectedContract(nextActionContract)}>Kurzsicht</Button>
              </div>
            </div>
          ) : (
            <p className="mt-3 text-sm text-muted-foreground">Aktuell liegt kein offener Kontrakt für eine Priorisierung vor.</p>
          )}
        </Card>
      </div>

      <Card className="p-4">
        {isLoading ? (
          <p>{t('crud.list.loading', { entityType: entityTypeLabel })}</p>
        ) : contracts.length === 0 ? (
          <p>{t('crud.list.noResults', { entityType: entityTypeLabel })}</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('crud.fields.number')}</TableHead>
                <TableHead>Quelle</TableHead>
                <TableHead>Steuerung</TableHead>
                <TableHead>{t('crud.fields.type')}</TableHead>
                <TableHead>{t('crud.fields.commodity')}</TableHead>
                <TableHead>{t('crud.fields.status')}</TableHead>
                <TableHead>{t('crud.fields.quantity')}</TableHead>
                <TableHead>{t('crud.fields.deliveryWindow')}</TableHead>
                <TableHead className="text-right">{t('crud.list.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((contract) => (
                <TableRow key={contract.id}>
                  <TableCell className="font-mono">{contract.contractNo}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{getSourceBadgeLabel(contract.sourceType)}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {contract.contractClass ? <Badge variant="outline">{contract.contractClass}</Badge> : null}
                      {contract.parityCode ? <Badge variant="outline">{contract.parityCode}</Badge> : null}
                      {contract.dispositionFlag ? <Badge variant="outline">{contract.dispositionFlag}</Badge> : null}
                    </div>
                  </TableCell>
                  <TableCell>{contract.type}</TableCell>
                  <TableCell>{contract.commodity}</TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(contract.status)}>
                      {getStatusLabel(t, contract.status.toLowerCase(), contract.status)}
                    </Badge>
                    {(() => {
                      const days = daysUntil(contract.deliveryWindow.to);
                      return days !== null && days >= 0 && days <= 30 ? (
                        <p className="mt-1 text-xs text-amber-700">Ablauf in {days} Tagen</p>
                      ) : null;
                    })()}
                  </TableCell>
                  <TableCell>
                    {contract.qty.contracted} {contract.qty.unit}
                  </TableCell>
                  <TableCell>
                    {new Date(contract.deliveryWindow.from).toLocaleDateString('de-DE')} -{' '}
                    {new Date(contract.deliveryWindow.to).toLocaleDateString('de-DE')}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex gap-2 justify-end">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedContract(contract)}
                      >
                        {t('crud.actions.details')}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openContractEditWorkspace(contract)}
                      >
                        {t('crud.actions.edit')}
                      </Button>
                      {contract.status.toLowerCase() !== 'cancelled' && contract.status.toLowerCase() !== 'fulfilled' && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedContract(contract);
                              setAmendmentDialogOpen(true);
                            }}
                          >
                            {t('crud.actions.amend')}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleCancelClick(contract.id, contract.contractNo)}
                          >
                            {t('crud.actions.cancel')}
                          </Button>
                        </>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeleteClick(contract.id, contract.contractNo)}
                      >
                        {t('crud.actions.delete')}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>

      {/* Delete Dialog */}
      <CrudDeleteDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleConfirmDelete}
        entityName={entityToDelete?.name}
        entityType={entityTypeLabel}
        isLoading={isDeleting}
      />

      {/* Cancel Dialog */}
      <CrudCancelDialog
        open={cancelDialogOpen}
        onOpenChange={setCancelDialogOpen}
        onConfirm={handleConfirmCancel}
        entityName={entityToCancel?.name}
        entityType={entityTypeLabel}
        isLoading={isCancelling}
      />

      {/* Amendment Dialog */}
      <Dialog open={amendmentDialogOpen} onOpenChange={setAmendmentDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{t('crud.dialogs.amend.title', { entityType: entityTypeLabel })}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.amend.description', { entityName: selectedContract?.contractNo })}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="amendment-type">
                {t('crud.dialogs.amend.typeRequired')}
              </Label>
              <NativeSelect
                value={amendmentForm.type}
                onValueChange={(value) => {
                  const tpl = amendmentTemplates.find((x) => x.code === value) ?? null;
                  setSelectedTemplate(tpl);
                  const changes =
                    value === 'EHBEB_NACHTRAG'
                      ? { b1: {}, b2: {}, b3: {}, b4: {}, b5: {}, b6: {}, b7: {}, b8: {}, c: {} }
                      : amendmentForm.changes;
                  setAmendmentForm({ ...amendmentForm, type: value, changes });
                }}
                options={[
                  ...amendmentTemplates.map((tpl) => ({ value: tpl.code, label: tpl.name })),
                  { value: 'QtyChange', label: t('crud.dialogs.amend.types.qtyChange') },
                  { value: 'WindowChange', label: t('crud.dialogs.amend.types.windowChange') },
                  { value: 'PriceRuleChange', label: t('crud.dialogs.amend.types.priceRuleChange') },
                  { value: 'CounterpartyChange', label: t('crud.dialogs.amend.types.counterpartyChange') },
                  { value: 'DeliveryTermsChange', label: t('crud.dialogs.amend.types.deliveryTermsChange') },
                  { value: 'Other', label: t('crud.dialogs.amend.types.other') },
                ]}
                placeholder={t('crud.dialogs.amend.typePlaceholder')}
              />
            </div>
            {selectedTemplate?.bodyMarkdown && (
              <div className="space-y-2 rounded-md border bg-muted/30 p-3">
                <Label className="text-xs text-muted-foreground">Vorlagentext</Label>
                <pre className="max-h-48 overflow-auto whitespace-pre-wrap break-words text-xs font-sans">
                  {selectedTemplate.bodyMarkdown.slice(0, 2000)}
                  {selectedTemplate.bodyMarkdown.length > 2000 ? '\n…' : ''}
                </pre>
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="amendment-reason">
                {t('crud.dialogs.amend.reasonRequired')}
              </Label>
              <Textarea
                id="amendment-reason"
                value={amendmentForm.reason}
                onChange={(e) => setAmendmentForm({ ...amendmentForm, reason: e.target.value })}
                placeholder={t('crud.dialogs.amend.reasonPlaceholder')}
                rows={4}
              />
              <p className="text-xs text-muted-foreground">
                {t('crud.dialogs.amend.reasonMinLength')}
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="amendment-changes">{t('crud.dialogs.amend.changesLabel')}</Label>
              <Textarea
                id="amendment-changes"
                value={JSON.stringify(amendmentForm.changes, null, 2)}
                onChange={(e) => {
                  try {
                    const changes = JSON.parse(e.target.value);
                    setAmendmentForm({ ...amendmentForm, changes });
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"field": "value"}'
                rows={6}
                className="font-mono text-sm"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setAmendmentDialogOpen(false);
                setSelectedTemplate(null);
                setAmendmentForm({ type: '', reason: '', changes: {} });
              }}
            >
              {t('crud.dialogs.amend.cancelButton')}
            </Button>
            <Button
              onClick={handleCreateAmendment}
              disabled={!amendmentForm.type || !amendmentForm.reason || amendmentForm.reason.trim().length < 10}
            >
              {t('crud.dialogs.amend.confirmButton')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Detail Drawer */}
      {selectedContract && (
        <DetailDrawer
          open={!!selectedContract}
          onOpenChange={(open) => !open && setSelectedContract(null)}
          title={getDetailTitle(t, entityTypeLabel, selectedContract.contractNo)}
        >
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">{t('crud.detail.basicInfo')}</h3>
              <div className="space-y-2">
                <p><strong>{t('crud.fields.number')}:</strong> {selectedContract.contractNo}</p>
                <p><strong>Quelle:</strong> {getSourceBadgeLabel(selectedContract.sourceType)}</p>
                <p><strong>Klasse / Gruppe / Variante:</strong> {[selectedContract.contractClass, selectedContract.contractGroup, selectedContract.contractVariant].filter(Boolean).join(' / ') || '-'}</p>
                <p><strong>Paritaet / Disposition:</strong> {[selectedContract.parityCode, selectedContract.dispositionFlag].filter(Boolean).join(' / ') || '-'}</p>
                <p><strong>Ausweichung / Druck:</strong> {selectedContract.alternateArticles?.join(', ') || '-'} / {selectedContract.printReady ? 'druckbereit' : 'Druck offen'}</p>
                <p><strong>{t('crud.fields.type')}:</strong> {selectedContract.type}</p>
                <p><strong>{t('crud.fields.commodity')}:</strong> {selectedContract.commodity}</p>
                <p><strong>{t('crud.fields.status')}:</strong> {getStatusLabel(t, selectedContract.status.toLowerCase(), selectedContract.status)}</p>
                <p><strong>{t('crud.fields.quantity')}:</strong> {selectedContract.qty.contracted} {selectedContract.qty.unit}</p>
                <p><strong>{t('crud.fields.deliveryWindow')}:</strong> {new Date(selectedContract.deliveryWindow.from).toLocaleDateString('de-DE')} - {new Date(selectedContract.deliveryWindow.to).toLocaleDateString('de-DE')}</p>
                <p><strong>Hedge / Marktwert / Mahnung:</strong> {selectedContract.hedgeQuotePct != null ? `${selectedContract.hedgeQuotePct.toFixed(1)}%` : '-'} / {selectedContract.marketValuationEur != null ? `${selectedContract.marketValuationEur.toFixed(2)} EUR` : '-'} / {selectedContract.dunningLevel != null ? `Stufe ${selectedContract.dunningLevel}` : '-'}</p>
                <p><strong>Washout:</strong> {selectedContract.writeoffCandidate ? 'vorgemerkt' : 'nicht vorgemerkt'}</p>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Naechste Aktion</h3>
              <div className="rounded-lg border p-3 text-sm text-muted-foreground">
                {(() => {
                  const days = daysUntil(selectedContract.deliveryWindow.to);
                  if (days !== null && days >= 0 && days <= 30) {
                    return `Friststeuerung priorisieren: dieser Kontrakt laeuft in ${days} Tagen ab.`;
                  }
                  if (selectedContract.status.toLowerCase() === 'draft') {
                    return 'Kontrakt vervollstaendigen und in den fachlich passenden Arbeitsplatz ueberfuehren.';
                  }
                  return 'Detailarbeitsplatz, Positionsmonitor und Alarmdashboard fuer Mengen-, Preis- und Ablaufpruefung nutzen.';
                })()}
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <Button size="sm" variant="outline" onClick={() => openContractWorkspace(selectedContract)}>Arbeitsplatz</Button>
                <Button size="sm" variant="outline" onClick={openContractPositions}>Positionsmonitor</Button>
                <Button size="sm" variant="outline" onClick={openContractAlarms}>Alarme</Button>
              </div>
            </div>

            {amendments.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">{t('crud.entities.amendment')}</h3>
                <div className="space-y-2">
                  {amendments.map((amendment) => (
                    <Card key={amendment.id} className="p-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <p><strong>{t('crud.fields.type')}:</strong> {amendment.type}</p>
                          <p><strong>{t('crud.fields.status')}:</strong> {getStatusLabel(t, amendment.status.toLowerCase(), amendment.status)}</p>
                          <p><strong>{t('crud.fields.reason')}:</strong> {amendment.reason}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(amendment.createdAt).toLocaleString('de-DE')}
                          </p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Audit Trail */}
            <CrudAuditTrailPanel
              entityType={entityTypeLabel}
              entityId={selectedContract.id}
              changeLogs={changeLogs}
              isLoading={isLoadingAudit}
            />
          </div>
        </DetailDrawer>
      )}
    </div>
  );
}



