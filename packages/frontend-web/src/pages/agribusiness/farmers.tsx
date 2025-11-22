/**
 * Farmers Page
 * CRUD interface for managing farmers using the CRUD framework
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
import { getEntityTypeLabel, getFieldLabel, getListTitle, getDetailTitle } from '@/features/crud/utils/i18n-helpers';

interface Farmer {
  id: string;
  farmerNumber: string;
  firstName: string;
  lastName: string;
  fullName: string;
  email: string;
  phone?: string;
  farmerType: string;
  status: string;
  portalAccessEnabled: boolean;
  createdAt: string;
  updatedAt: string;
}

export default function FarmersPage(): JSX.Element {
  const { t } = useTranslation();
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [selectedFarmer, setSelectedFarmer] = useState<Farmer | null>(null);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const entityType = 'farmer';
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Farmer');

  // Fetch farmers
  React.useEffect(() => {
    const fetchFarmers = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('/api/agribusiness/farmers');
        if (response.ok) {
          const data = await response.json();
          setFarmers(data.data || []);
        }
      } catch (error) {
        console.error('Error fetching farmers:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchFarmers();
  }, []);

  // Delete handler
  const handleDelete = async (id: string, reason: string) => {
    try {
      const response = await fetch(`/api/agribusiness/farmers/${id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      });
      if (response.ok) {
        setFarmers(farmers.filter(f => f.id !== id));
        setSelectedFarmer(null);
      } else {
        throw new Error('Failed to delete farmer');
      }
    } catch (error) {
      console.error('Error deleting farmer:', error);
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

  // Cancel handler (if needed)
  const handleCancel = async (id: string, reason: string) => {
    // Implementation if farmers can be cancelled
    console.log('Cancel farmer:', id, reason);
  };

  const {
    cancelDialogOpen,
    setCancelDialogOpen,
    handleCancel: handleCancelClick,
    handleConfirmCancel,
    isCancelling,
  } = useCrudCancel({
    onCancel: handleCancel,
    entityType: entityTypeLabel,
  });

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
    entityId: selectedFarmer?.id || null,
    fetchAuditTrail,
    enabled: !!selectedFarmer,
  });

  // Filter farmers
  const filtered = useMemo(() => {
    if (!query) return farmers;
    const q = query.toLowerCase();
    return farmers.filter(
      f =>
        f.fullName.toLowerCase().includes(q) ||
        f.email.toLowerCase().includes(q) ||
        f.farmerNumber.includes(q)
    );
  }, [farmers, query]);

  // Print handlers
  const handlePrintPDF = async () => {
    await crudPrintService.printListAsPDF(
      filtered,
      [
        { header: t('crud.fields.number'), field: 'farmerNumber' },
        { header: t('crud.fields.name'), field: 'fullName' },
        { header: t('crud.fields.email'), field: 'email' },
        { header: t('crud.fields.type'), field: 'farmerType' },
        { header: t('crud.fields.status'), field: 'status' },
      ],
      { title: getListTitle(t, entityTypeLabel), format: 'PDF' }
    );
  };

  const handlePrintExcel = async () => {
    await crudPrintService.printListAsExcel(
      filtered,
      [
        { header: t('crud.fields.number'), field: 'farmerNumber' },
        { header: t('crud.fields.name'), field: 'fullName' },
        { header: t('crud.fields.email'), field: 'email' },
        { header: t('crud.fields.type'), field: 'farmerType' },
        { header: t('crud.fields.status'), field: 'status' },
      ],
      { title: getListTitle(t, entityTypeLabel), format: 'EXCEL' }
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">{entityTypeLabel}</h2>
        <div className="flex gap-2">
          <CrudPrintButton
            listData={filtered}
            listColumns={[
              { header: t('crud.fields.number'), field: 'farmerNumber' },
              { header: t('crud.fields.name'), field: 'fullName' },
              { header: t('crud.fields.email'), field: 'email' },
              { header: t('crud.fields.type'), field: 'farmerType' },
              { header: t('crud.fields.status'), field: 'status' },
            ]}
            entityType={entityTypeLabel}
            printTitle={getListTitle(t, entityTypeLabel)}
            onPrintPDF={handlePrintPDF}
            onPrintExcel={handlePrintExcel}
          />
          <Button onClick={() => {/* Navigate to create page */}}>
            {t('crud.actions.new')} {entityTypeLabel}
          </Button>
        </div>
      </div>

      <Toolbar
        onSearch={setQuery}
        onCopilot={() => window.alert('Copilot analyzing farmers...')}
      />

      <Card className="p-4">
        {isLoading ? (
          <p>{t('crud.list.loading', { entityType: entityTypeLabel })}</p>
        ) : filtered.length === 0 ? (
          <p>{t('crud.list.noResults', { entityType: entityTypeLabel })}</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('crud.fields.number')}</TableHead>
                <TableHead>{t('crud.fields.name')}</TableHead>
                <TableHead>{t('crud.fields.email')}</TableHead>
                <TableHead>{t('crud.fields.type')}</TableHead>
                <TableHead>{t('crud.fields.status')}</TableHead>
                <TableHead className="text-right">{t('crud.list.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((farmer) => (
                <TableRow key={farmer.id}>
                  <TableCell className="font-mono">{farmer.farmerNumber}</TableCell>
                  <TableCell>{farmer.fullName}</TableCell>
                  <TableCell>{farmer.email}</TableCell>
                  <TableCell>{farmer.farmerType}</TableCell>
                  <TableCell>{farmer.status}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex gap-2 justify-end">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedFarmer(farmer)}
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
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeleteClick(farmer.id, farmer.fullName)}
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
        entityType={entityTypeLabel}
        isLoading={isCancelling}
      />

      {/* Detail Drawer */}
      {selectedFarmer && (
        <DetailDrawer
          open={!!selectedFarmer}
          onOpenChange={(open) => !open && setSelectedFarmer(null)}
          title={getDetailTitle(t, entityTypeLabel, selectedFarmer.fullName)}
        >
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">{t('crud.detail.basicInfo')}</h3>
              <div className="space-y-2">
                <p><strong>{t('crud.fields.number')}:</strong> {selectedFarmer.farmerNumber}</p>
                <p><strong>{t('crud.fields.name')}:</strong> {selectedFarmer.fullName}</p>
                <p><strong>{t('crud.fields.email')}:</strong> {selectedFarmer.email}</p>
                <p><strong>{t('crud.fields.phone')}:</strong> {selectedFarmer.phone || '-'}</p>
                <p><strong>{t('crud.fields.type')}:</strong> {selectedFarmer.farmerType}</p>
                <p><strong>{t('crud.fields.status')}:</strong> {selectedFarmer.status}</p>
                <p><strong>Portal-Zugang:</strong> {selectedFarmer.portalAccessEnabled ? t('status.active') : t('status.inactive')}</p>
              </div>
            </div>

            {/* Audit Trail */}
            <CrudAuditTrailPanel
              entityType={entityTypeLabel}
              entityId={selectedFarmer.id}
              changeLogs={changeLogs}
              isLoading={isLoadingAudit}
            />
          </div>
        </DetailDrawer>
      )}
    </div>
  );
}

