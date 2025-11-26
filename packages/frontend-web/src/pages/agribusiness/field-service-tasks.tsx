/**
 * Field Service Tasks Page
 * CRUD interface for managing field service tasks
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

interface FieldServiceTask {
  id: string;
  taskNumber: string;
  title: string;
  taskType: string;
  status: string;
  priority: string;
  assignedToName: string;
  farmerName?: string;
  scheduledStartDate: string;
  completionPercentage: number;
}

export default function FieldServiceTasksPage(): JSX.Element {
  const { t } = useTranslation();
  const [tasks, setTasks] = useState<FieldServiceTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<FieldServiceTask | null>(null);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const entityType = 'fieldServiceTask';
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Field Service Task');

  // Fetch tasks
  React.useEffect(() => {
    const fetchTasks = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('/api/agribusiness/field-service-tasks');
        if (response.ok) {
          const data = await response.json();
          setTasks(data.data || []);
        }
      } catch (error) {
        console.error('Error fetching tasks:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchTasks();
  }, []);

  // Delete handler
  const handleDelete = async (id: string, reason: string) => {
    try {
      const response = await fetch(`/api/agribusiness/field-service-tasks/${id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      });
      if (response.ok) {
        setTasks(tasks.filter(t => t.id !== id));
        setSelectedTask(null);
      } else {
        throw new Error('Failed to delete task');
      }
    } catch (error) {
      console.error('Error deleting task:', error);
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
      const response = await fetch(`/api/agribusiness/field-service-tasks/${id}/cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      });
      if (response.ok) {
        const updated = await response.json();
        setTasks(tasks.map(t => t.id === id ? updated : t));
        setSelectedTask(null);
      } else {
        throw new Error('Failed to cancel task');
      }
    } catch (error) {
      console.error('Error cancelling task:', error);
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
    entityId: selectedTask?.id || null,
    fetchAuditTrail,
    enabled: !!selectedTask,
  });

  // Filter tasks
  const filtered = useMemo(() => {
    if (!query) return tasks;
    const q = query.toLowerCase();
    return tasks.filter(
      t =>
        t.title.toLowerCase().includes(q) ||
        t.taskNumber.includes(q) ||
        t.assignedToName.toLowerCase().includes(q)
    );
  }, [tasks, query]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-100 text-green-800';
      case 'IN_PROGRESS':
        return 'bg-blue-100 text-blue-800';
      case 'CANCELLED':
        return 'bg-red-100 text-red-800';
      case 'SCHEDULED':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return 'bg-red-100 text-red-800';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800';
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
              { header: t('crud.fields.number'), field: 'taskNumber' },
              { header: t('crud.fields.name'), field: 'title' },
              { header: t('crud.fields.type'), field: 'taskType' },
              { header: t('crud.fields.status'), field: 'status' },
              { header: t('crud.fields.priority'), field: 'priority' },
              { header: t('crud.fields.assignedTo'), field: 'assignedToName' },
            ]}
            entityType={entityTypeLabel}
            printTitle={getListTitle(t, entityTypeLabel)}
          />
          <Button onClick={() => {/* Navigate to create */}}>
            {t('crud.actions.new')} {t('crud.entities.task')}
          </Button>
        </div>
      </div>

      <Toolbar
        onSearch={setQuery}
        onCopilot={() => window.alert('Copilot analyzing tasks...')}
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
                <TableHead>{t('crud.fields.type')}</TableHead>
                <TableHead>{t('crud.fields.status')}</TableHead>
                <TableHead>{t('crud.fields.priority')}</TableHead>
                <TableHead>{t('crud.fields.assignedTo')}</TableHead>
                <TableHead>{t('crud.fields.completionPercentage')}</TableHead>
                <TableHead className="text-right">{t('crud.list.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((task) => (
                <TableRow key={task.id}>
                  <TableCell className="font-mono">{task.taskNumber}</TableCell>
                  <TableCell>{task.title}</TableCell>
                  <TableCell>{task.taskType}</TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(task.status)}>
                      {getStatusLabel(t, task.status, task.status)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getPriorityColor(task.priority)}>
                      {task.priority}
                    </Badge>
                  </TableCell>
                  <TableCell>{task.assignedToName}</TableCell>
                  <TableCell>{task.completionPercentage}%</TableCell>
                  <TableCell className="text-right">
                    <div className="flex gap-2 justify-end">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedTask(task)}
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
                      {task.status !== 'CANCELLED' && task.status !== 'COMPLETED' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleCancelClick(task.id, task.title)}
                        >
                          {t('crud.actions.cancel')}
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeleteClick(task.id, task.title)}
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

      {/* Detail Drawer */}
      {selectedTask && (
        <DetailDrawer
          open={!!selectedTask}
          onOpenChange={(open) => !open && setSelectedTask(null)}
          title={getDetailTitle(t, entityTypeLabel, selectedTask.title)}
        >
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">{t('crud.detail.basicInfo')}</h3>
              <div className="space-y-2">
                <p><strong>{t('crud.fields.number')}:</strong> {selectedTask.taskNumber}</p>
                <p><strong>{t('crud.fields.name')}:</strong> {selectedTask.title}</p>
                <p><strong>{t('crud.fields.type')}:</strong> {selectedTask.taskType}</p>
                <p><strong>{t('crud.fields.status')}:</strong> {getStatusLabel(t, selectedTask.status, selectedTask.status)}</p>
                <p><strong>{t('crud.fields.priority')}:</strong> {selectedTask.priority}</p>
                <p><strong>{t('crud.fields.assignedTo')}:</strong> {selectedTask.assignedToName}</p>
                <p><strong>{t('crud.entities.farmer')}:</strong> {selectedTask.farmerName || '-'}</p>
                <p><strong>{t('crud.fields.date')}:</strong> {new Date(selectedTask.scheduledStartDate).toLocaleDateString('de-DE')}</p>
                <p><strong>{t('crud.fields.completionPercentage')}:</strong> {selectedTask.completionPercentage}%</p>
              </div>
            </div>

            {/* Audit Trail */}
            <CrudAuditTrailPanel
              entityType={entityTypeLabel}
              entityId={selectedTask.id}
              changeLogs={changeLogs}
              isLoading={isLoadingAudit}
            />
          </div>
        </DetailDrawer>
      )}
    </div>
  );
}

