/**
 * Contracts Page V2
 * CRUD interface for managing contracts with Amendment support
 */

import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Toolbar } from '@/components/ui/toolbar';
import { DetailDrawer } from '@/components/ui/detail-drawer';
import { CrudDeleteDialog, CrudCancelDialog, CrudAuditTrailPanel, CrudPrintButton } from '@/features/crud/components';
import { useCrudDelete, useCrudCancel, useCrudAuditTrail } from '@/features/crud/hooks';
import { crudPrintService } from '@/features/crud/services';
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
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Contract {
  id: string;
  contractNo: string;
  type: string;
  commodity: string;
  counterpartyId: string;
  status: string;
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

interface Amendment {
  id: string;
  contractId: string;
  type: string;
  reason: string;
  status: string;
  changes: Record<string, any>;
  createdAt: string;
}

export default function ContractsPageV2(): JSX.Element {
  const { t } = useTranslation();
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [amendments, setAmendments] = useState<Amendment[]>([]);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [amendmentDialogOpen, setAmendmentDialogOpen] = useState(false);
  const [amendmentForm, setAmendmentForm] = useState({
    type: '',
    reason: '',
    changes: {} as Record<string, any>,
  });

  const entityType = 'contract';
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Contract');

  // Fetch contracts
  React.useEffect(() => {
    const fetchContracts = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('/api/contracts');
        if (response.ok) {
          const data = await response.json();
          setContracts(data.items || []);
        }
      } catch (error) {
        console.error('Error fetching contracts:', error);
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
        const response = await fetch(`/api/contracts/${selectedContract.id}/amendments`);
        if (response.ok) {
          const data = await response.json();
          setAmendments(data.items || []);
        }
      } catch (error) {
        console.error('Error fetching amendments:', error);
      }
    };
    fetchAmendments();
  }, [selectedContract]);

  // Delete handler
  const handleDelete = async (id: string, reason: string) => {
    try {
      const response = await fetch(`/api/contracts/${id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason, tenantId: 'default' }),
      });
      if (response.ok) {
        setContracts(contracts.filter(c => c.id !== id));
        setSelectedContract(null);
      } else {
        throw new Error('Failed to delete contract');
      }
    } catch (error) {
      console.error('Error deleting contract:', error);
      throw error;
    }
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
    try {
      const response = await fetch(`/api/contracts/${id}/cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason, tenantId: 'default', cancelledBy: 'current-user' }),
      });
      if (response.ok) {
        const updated = await response.json();
        setContracts(contracts.map(c => c.id === id ? updated : c));
        setSelectedContract(null);
      } else {
        throw new Error('Failed to cancel contract');
      }
    } catch (error) {
      console.error('Error cancelling contract:', error);
      throw error;
    }
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
      alert(t('crud.dialogs.amend.errorRequired'));
      return;
    }

    try {
      const response = await fetch(`/api/contracts/${selectedContract.id}/amendments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contractId: selectedContract.id,
          tenantId: 'default',
          type: amendmentForm.type,
          reason: amendmentForm.reason,
          changes: amendmentForm.changes,
          createdBy: 'current-user',
        }),
      });
      if (response.ok) {
        const amendment = await response.json();
        setAmendments([...amendments, amendment]);
        setAmendmentDialogOpen(false);
        setAmendmentForm({ type: '', reason: '', changes: {} });
      } else {
        throw new Error('Failed to create amendment');
      }
    } catch (error) {
      console.error('Error creating amendment:', error);
      alert(t('crud.messages.createError', { entityType: t('crud.entities.amendment') }));
    }
  };

  // Audit trail
  const fetchAuditTrail = async (entityType: string, entityId: string) => {
    const response = await fetch(`/api/audit/change-logs/audit-trail/${entityType}/${entityId}`);
    if (response.ok) {
      const data = await response.json();
      return data.data || [];
    }
    return [];
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
    switch (status) {
      case 'Active':
        return 'bg-green-100 text-green-800';
      case 'Fulfilled':
        return 'bg-blue-100 text-blue-800';
      case 'Cancelled':
        return 'bg-red-100 text-red-800';
      case 'Draft':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
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
          <Button onClick={() => {/* Navigate to create */}}>
            {t('crud.actions.new')} {entityTypeLabel}
          </Button>
        </div>
      </div>

      <Toolbar
        onSearch={setQuery}
        onCopilot={() => window.alert('Copilot analyzing contracts...')}
      />

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
                  <TableCell>{contract.type}</TableCell>
                  <TableCell>{contract.commodity}</TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(contract.status)}>
                      {getStatusLabel(t, contract.status, contract.status)}
                    </Badge>
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
                        onClick={() => {/* Navigate to edit */}}
                      >
                        {t('crud.actions.edit')}
                      </Button>
                      {contract.status !== 'Cancelled' && contract.status !== 'Fulfilled' && (
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
              <Select
                value={amendmentForm.type}
                onValueChange={(value) => setAmendmentForm({ ...amendmentForm, type: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.dialogs.amend.typePlaceholder')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="QtyChange">{t('crud.dialogs.amend.types.qtyChange')}</SelectItem>
                  <SelectItem value="WindowChange">{t('crud.dialogs.amend.types.windowChange')}</SelectItem>
                  <SelectItem value="PriceRuleChange">{t('crud.dialogs.amend.types.priceRuleChange')}</SelectItem>
                  <SelectItem value="CounterpartyChange">{t('crud.dialogs.amend.types.counterpartyChange')}</SelectItem>
                  <SelectItem value="DeliveryTermsChange">{t('crud.dialogs.amend.types.deliveryTermsChange')}</SelectItem>
                  <SelectItem value="Other">{t('crud.dialogs.amend.types.other')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
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
                <p><strong>{t('crud.fields.type')}:</strong> {selectedContract.type}</p>
                <p><strong>{t('crud.fields.commodity')}:</strong> {selectedContract.commodity}</p>
                <p><strong>{t('crud.fields.status')}:</strong> {getStatusLabel(t, selectedContract.status, selectedContract.status)}</p>
                <p><strong>{t('crud.fields.quantity')}:</strong> {selectedContract.qty.contracted} {selectedContract.qty.unit}</p>
                <p><strong>{t('crud.fields.deliveryWindow')}:</strong> {new Date(selectedContract.deliveryWindow.from).toLocaleDateString('de-DE')} - {new Date(selectedContract.deliveryWindow.to).toLocaleDateString('de-DE')}</p>
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
                          <p><strong>{t('crud.fields.status')}:</strong> {getStatusLabel(t, amendment.status, amendment.status)}</p>
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

