/**
 * Field Service Tasks Page
 * CRUD interface for managing field service tasks
 */

import React, { useState, useMemo } from 'react';
import { useNavigate, useSearchParams } from '@/app/routing/typed-router';
import { useTranslation } from 'react-i18next';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
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
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow';

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

type FieldServiceRole = 'disposition' | 'aussendienst' | 'beratung' | 'leitung';

const fieldServiceRoles = [
  {
    id: 'disposition',
    label: 'Disposition',
    description: 'Einsaetze priorisieren, Termine halten und offene Aufgaben verteilen.',
  },
  {
    id: 'aussendienst',
    label: 'Aussendienst',
    description: 'Eigene Einsaetze vorbereiten, Status pflegen und Rueckmeldung sichern.',
  },
  {
    id: 'beratung',
    label: 'Beratung',
    description: 'Landwirt, Aufgabe und fachlichen Nachweis im Blick behalten.',
  },
  {
    id: 'leitung',
    label: 'Leitung',
    description: 'Rueckstand, Prioritaet und Abschlussfaehigkeit der Einsatzlage bewerten.',
  },
] satisfies Array<{ id: FieldServiceRole; label: string; description: string }>;

export default function FieldServiceTasksPage(): JSX.Element {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const workflowInstanceId = searchParams.get('workflowInstanceId') || '';
  const workflowCase = searchParams.get('workflowCase') || '';
  const isWorkflowEntry = Boolean(workflowInstanceId || workflowCase);

  const workflowQuery = useMemo(() => {
    const p = new URLSearchParams();
    if (workflowInstanceId) p.set('workflowInstanceId', workflowInstanceId);
    if (workflowCase) p.set('workflowCase', workflowCase);
    const s = p.toString();
    return s ? `?${s}` : '';
  }, [workflowInstanceId, workflowCase]);

  const [selectedTask, setSelectedTask] = useState<FieldServiceTask | null>(null);
  const [query, setQuery] = useState('');
  const [roleFocus, setRoleFocus] = useState<FieldServiceRole>('disposition');

  const entityType = 'fieldServiceTask';
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Field Service Task');

  const queryClient = useQueryClient();
  const listQueryKey = ['field-service-tasks', workflowInstanceId] as const;

  // Fetch tasks
  const { data: tasks = [], isLoading } = useQuery({
    queryKey: listQueryKey,
    queryFn: async () => {
      const response = await apiClient.get<FieldServiceTask[] | { items?: FieldServiceTask[] }>('/api/v1/agribusiness/field-service-tasks')
      const payload = response.data
      return Array.isArray(payload) ? payload : Array.isArray(payload?.items) ? payload.items : []
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason: string }) => {
      await apiClient.delete(`/api/v1/agribusiness/field-service-tasks/${id}`, { data: { reason } });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: listQueryKey });
      setSelectedTask(null);
    },
  });

  // Delete handler
  const handleDelete = async (id: string, reason: string) => {
    await deleteMutation.mutateAsync({ id, reason });
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

  const cancelMutation = useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason: string }) => {
      await apiClient.post(`/api/v1/agribusiness/field-service-tasks/${id}/cancel`, { reason });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: listQueryKey });
      setSelectedTask(null);
    },
  });

  // Cancel handler
  const handleCancel = async (id: string, reason: string) => {
    await cancelMutation.mutateAsync({ id, reason });
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
    try {
      const data = await apiClient.get<{ data?: ChangeLog[] }>(`/api/v1/audit/change-logs/audit-trail/${entityType}/${entityId}`);
      return data.data || [];
    } catch {
      return [];
    }
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
        String(t.title ?? '').toLowerCase().includes(q) ||
        String(t.taskNumber ?? '').includes(q) ||
        String(t.assignedToName ?? '').toLowerCase().includes(q)
    );
  }, [tasks, query]);

  const activeTasks = tasks.filter((task) => !['COMPLETED', 'CANCELLED'].includes(task.status ?? '')).length;
  const urgentTasks = tasks.filter((task) => task.priority === 'URGENT' && !['COMPLETED', 'CANCELLED'].includes(task.status ?? '')).length;
  const inProgressTasks = tasks.filter((task) => task.status === 'IN_PROGRESS').length;
  const completedTasks = tasks.filter((task) => task.status === 'COMPLETED').length;
  const averageCompletion = tasks.length > 0
    ? Math.round(tasks.reduce((sum, task) => sum + (task.completionPercentage || 0), 0) / tasks.length)
    : 0;
  const focusTask = filtered.find((task) => task.priority === 'URGENT' && !['COMPLETED', 'CANCELLED'].includes(task.status ?? '')) ?? filtered[0];
  const fieldServiceReady = urgentTasks === 0 && activeTasks === 0;
  const nextFieldServiceAction = focusTask
    ? focusTask.status === 'SCHEDULED'
      ? `${focusTask.taskNumber} terminlich bestaetigen und Einsatz vorbereiten.`
      : focusTask.status === 'IN_PROGRESS'
        ? `${focusTask.taskNumber} Rueckmeldung und Restaufwand nachhalten.`
        : focusTask.status === 'COMPLETED'
          ? `${focusTask.taskNumber} Nachweis pruefen und Abschluss dokumentieren.`
          : `${focusTask.taskNumber} Status klaeren und Verantwortlichen bestaetigen.`
    : query
      ? 'Suche anpassen oder neuen Feldservice-Einsatz anlegen.'
      : 'Neuen Feldservice-Einsatz anlegen, sobald eine Beratung oder Vor-Ort-Aufgabe ansteht.';

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

  const handleCopilot = () => {
    navigate(`/admin/control-center/agent-ops?context=field-service&intent=dispatch-review${workflowQuery ? `&${workflowQuery.slice(1)}` : ''}`);
    toast({
      title: 'Agent Ops geöffnet',
      description: 'Außendienst-Aufgaben können jetzt im Leitstand priorisiert, überwacht und eskaliert werden.',
    });
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
          <Button onClick={() => navigate(`/agribusiness/field-service-tasks/neu${workflowQuery}`)}>
            {t('crud.actions.new')} {t('crud.entities.task')}
          </Button>
        </div>
      </div>

      {isWorkflowEntry && (
        <div className="rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-xs text-blue-900">
          {workflowCase ? `Workflow-Vorgang ${workflowCase}` : 'Workflow-Einstieg'}
          {workflowInstanceId ? ` · Instanz ${workflowInstanceId}` : ''}
        </div>
      )}

      <RoleFocusBar
        roles={fieldServiceRoles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={filtered.length}
        totalCount={tasks.length}
        title="Arbeitsrolle fuer Feldservice"
      />

      <ManagementDecisionPanel
        decision={{
          allowed: fieldServiceReady,
          allowedLabel: 'Einsatzlage erledigt',
          blockedLabel: 'Einsaetze offen',
          summary: fieldServiceReady
            ? 'Es sind keine aktiven oder dringenden Feldservice-Aufgaben offen. Die Liste dient aktuell als Nachweis und Historie.'
            : 'Aktive oder dringende Feldservice-Aufgaben brauchen klare Zustaendigkeit, Terminsteuerung und Rueckmeldung, bevor die Einsatzlage abgeschlossen ist.',
          blockerCount: fieldServiceReady ? 0 : activeTasks + urgentTasks,
          nextFocus: nextFieldServiceAction,
          template: {
            label: 'Feldservice-Einsatznachweis',
            href: '/docs/agribusiness/feldservice-einsatznachweis.md',
          },
        }}
      />

      <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr_1fr]">
        <OperationalTaskPlan
          title="Einsatzplan"
          items={[
            {
              label: 'Einsatz erfassen',
              done: tasks.length > 0,
              hint: `${tasks.length} Aufgabe(n) in der Feldservice-Liste.`,
            },
            {
              label: 'Dringende Aufgaben klaeren',
              done: urgentTasks === 0,
              hint: urgentTasks > 0 ? `${urgentTasks} dringende Aufgabe(n) zuerst disponieren.` : 'Keine dringenden offenen Aufgaben.',
            },
            {
              label: 'Rueckmeldung nachhalten',
              done: inProgressTasks === 0,
              hint: inProgressTasks > 0 ? `${inProgressTasks} laufende Aufgabe(n) brauchen Status oder Rueckmeldung.` : 'Keine laufenden Einsaetze ohne Abschluss.',
            },
            {
              label: 'Nachweis sichern',
              done: completedTasks > 0 || tasks.length === 0,
              hint: completedTasks > 0 ? `${completedTasks} abgeschlossene Aufgabe(n) fuer Audit und Druck verfuegbar.` : 'Abschlussnachweise entstehen nach erledigtem Einsatz.',
            },
          ]}
        />
        <NextActionPanel action={nextFieldServiceAction} tone={fieldServiceReady ? 'emerald' : urgentTasks > 0 ? 'red' : 'amber'} />
        <div className="space-y-3">
          <EvidenceTemplateLink
            link={{
              label: 'Feldservice-Rueckmeldeprotokoll',
              href: '/docs/agribusiness/feldservice-rueckmeldung.md',
            }}
          />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'create', label: 'Anlegen', available: true, hint: 'Neue Feldservice-Aufgabe kann direkt erstellt werden.' },
              { key: 'read', label: 'Lesen', available: true, hint: 'Status, Prioritaet, Owner und Fortschritt sind sichtbar.' },
              { key: 'update', label: 'Bearbeiten', available: true, hint: 'Bearbeiten-Route fuehrt die Einsatzdaten weiter.' },
              { key: 'reject', label: 'Abbrechen', available: true, hint: 'Abbruchdialog verlangt eine begruendete Entscheidung.' },
              { key: 'delete', label: 'Loeschen', available: true, hint: 'Loeschen laeuft ueber den bestehenden Grund-Dialog.' },
              { key: 'audit', label: 'Audit', available: true, hint: 'Detail-Drawer zeigt die Aenderungshistorie.' },
            ]}
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card className="p-4">
          <div className="text-xs font-semibold uppercase text-muted-foreground">Offene Einsaetze</div>
          <div className="mt-2 text-2xl font-bold">{activeTasks}</div>
        </Card>
        <Card className="p-4">
          <div className="text-xs font-semibold uppercase text-muted-foreground">Dringend</div>
          <div className="mt-2 text-2xl font-bold text-status-error">{urgentTasks}</div>
        </Card>
        <Card className="p-4">
          <div className="text-xs font-semibold uppercase text-muted-foreground">In Bearbeitung</div>
          <div className="mt-2 text-2xl font-bold text-blue-700">{inProgressTasks}</div>
        </Card>
        <Card className="p-4">
          <div className="text-xs font-semibold uppercase text-muted-foreground">Fortschritt im Schnitt</div>
          <div className="mt-2 text-2xl font-bold">{averageCompletion}%</div>
        </Card>
      </div>

      <Toolbar
        onSearch={setQuery}
        onCopilot={handleCopilot}
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
                  <TableCell className="font-mono">{task.taskNumber || '-'}</TableCell>
                  <TableCell>{task.title || '-'}</TableCell>
                  <TableCell>{task.taskType || '-'}</TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(task.status ?? '')}>
                      {getStatusLabel(t, task.status ?? 'UNKNOWN', task.status ?? '-')}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getPriorityColor(task.priority ?? '')}>
                      {task.priority || '-'}
                    </Badge>
                  </TableCell>
                  <TableCell>{task.assignedToName || '-'}</TableCell>
                  <TableCell>{task.completionPercentage ?? 0}%</TableCell>
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
                        onClick={() =>
                          navigate(`/agribusiness/field-service-tasks/${encodeURIComponent(task.id)}/bearbeiten${workflowQuery}`)
                        }
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

