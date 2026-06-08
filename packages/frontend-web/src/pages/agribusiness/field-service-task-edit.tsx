/**
 * Field-Service-Aufgabe bearbeiten (CRM-Fall / Demo)
 */

import React, { useEffect, useMemo } from 'react';
import { useNavigate, useParams, useSearchParams } from '@/app/routing/react-router-compat';
import { useTranslation } from 'react-i18next';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

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

const TASK_TYPES = ['FIELD_SERVICE', 'INSPECTION', 'MAINTENANCE', 'EMERGENCY'] as const;
const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'URGENT'] as const;
const STATUSES = ['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'] as const;

export default function FieldServiceTaskEditPage(): JSX.Element {
  const { t } = useTranslation();
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const workflowInstanceId = searchParams.get('workflowInstanceId') || '';
  const workflowCase = searchParams.get('workflowCase') || '';

  const [title, setTitle] = React.useState('');
  const [taskType, setTaskType] = React.useState('FIELD_SERVICE');
  const [priority, setPriority] = React.useState('MEDIUM');
  const [status, setStatus] = React.useState('SCHEDULED');

  const listKey = ['field-service-tasks', workflowInstanceId] as const;

  const backHref = useMemo(() => {
    const p = new URLSearchParams();
    if (workflowInstanceId) p.set('workflowInstanceId', workflowInstanceId);
    if (workflowCase) p.set('workflowCase', workflowCase);
    const q = p.toString();
    return `/agribusiness/field-service-tasks${q ? `?${q}` : ''}`;
  }, [workflowInstanceId, workflowCase]);

  const { data: task, isLoading, isError } = useQuery({
    queryKey: ['field-service-task', taskId],
    queryFn: async () =>
      (await apiClient.get<FieldServiceTask>(`/api/v1/agribusiness/field-service-tasks/${taskId}`)).data,
    enabled: !!taskId,
  });

  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setTaskType(task.taskType || 'FIELD_SERVICE');
      setPriority(task.priority || 'MEDIUM');
      setStatus(task.status || 'SCHEDULED');
    }
  }, [task]);

  const updateMutation = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.put<FieldServiceTask>(
        `/api/v1/agribusiness/field-service-tasks/${taskId}`,
        {
          title: title.trim(),
          taskType,
          priority,
          status,
        }
      );
      return data;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: listKey });
      void queryClient.invalidateQueries({ queryKey: ['field-service-task', taskId] });
      toast({ title: t('crud.messages.saved', { defaultValue: 'Gespeichert' }) });
      navigate(backHref);
    },
    onError: (err: unknown) => {
      toast({ variant: 'destructive', title: 'Fehler', description: getAxiosErrorMessage(err) });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      toast({ variant: 'destructive', title: 'Pflichtfeld', description: 'Bitte Titel eingeben.' });
      return;
    }
    updateMutation.mutate();
  };

  if (!taskId) {
    return <p className="p-4">Ungültige Route.</p>;
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 p-8">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span>{t('crud.list.loading', { defaultValue: 'Laden…' })}</span>
      </div>
    );
  }

  if (isError || !task) {
    return (
      <div className="p-4 space-y-2">
        <p>Aufgabe nicht gefunden oder nicht ladbar.</p>
        <Button variant="outline" onClick={() => navigate(backHref)}>
          {t('crud.actions.back', { defaultValue: 'Zurück zur Liste' })}
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg space-y-4 p-4">
      <div className="flex items-center gap-2">
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate(backHref)}>
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t('crud.actions.back', { defaultValue: 'Zurück' })}
        </Button>
      </div>

      <h1 className="text-2xl font-bold">
        {t('crud.actions.edit', { defaultValue: 'Bearbeiten' })} · {task.taskNumber}
      </h1>

      <Card className="p-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fst-e-title">{t('crud.fields.name', { defaultValue: 'Name' })} *</Label>
            <Input
              id="fst-e-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              autoComplete="off"
            />
          </div>
          <div className="space-y-2">
            <Label>{t('crud.fields.type', { defaultValue: 'Typ' })}</Label>
            <Select value={taskType} onValueChange={setTaskType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TASK_TYPES.map((tt) => (
                  <SelectItem key={tt} value={tt}>
                    {tt}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>{t('crud.fields.priority', { defaultValue: 'Priorität' })}</Label>
            <Select value={priority} onValueChange={setPriority}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PRIORITIES.map((pr) => (
                  <SelectItem key={pr} value={pr}>
                    {pr}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>{t('crud.fields.status', { defaultValue: 'Status' })}</Label>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STATUSES.map((st) => (
                  <SelectItem key={st} value={st}>
                    {st}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={updateMutation.isPending}>
              {updateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {t('crud.actions.save', { defaultValue: 'Speichern' })}
            </Button>
            <Button type="button" variant="outline" onClick={() => navigate(backHref)}>
              {t('crud.actions.cancel', { defaultValue: 'Abbrechen' })}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
