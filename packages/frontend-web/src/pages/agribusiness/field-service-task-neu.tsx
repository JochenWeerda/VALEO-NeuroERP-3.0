/**
 * Neue Field-Service-Aufgabe
 * Folgepfad aus CRM-, Service- und Workflow-Vorgaengen.
 */

import React, { useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useMutation } from '@tanstack/react-query';
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

const TASK_TYPES = ['FIELD_SERVICE', 'INSPECTION', 'MAINTENANCE', 'EMERGENCY'] as const;
const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'URGENT'] as const;

export default function FieldServiceTaskNeuPage(): JSX.Element {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [searchParams] = useSearchParams();
  const workflowInstanceId = searchParams.get('workflowInstanceId') || '';
  const workflowCase = searchParams.get('workflowCase') || '';
  const serviceRequestId = searchParams.get('service_request_id') || '';

  const [title, setTitle] = React.useState('');
  const [taskType, setTaskType] = React.useState<string>('FIELD_SERVICE');
  const [priority, setPriority] = React.useState<string>('MEDIUM');

  const backHref = useMemo(() => {
    const p = new URLSearchParams();
    if (workflowInstanceId) p.set('workflowInstanceId', workflowInstanceId);
    if (workflowCase) p.set('workflowCase', workflowCase);
    const q = p.toString();
    return `/agribusiness/field-service-tasks${q ? `?${q}` : ''}`;
  }, [workflowInstanceId, workflowCase]);

  const createMutation = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post<{
        id: string;
        taskNumber: string;
        title: string;
        taskType: string;
        status: string;
        priority: string;
      }>('/api/v1/agribusiness/field-service-tasks', {
        title: title.trim(),
        taskType,
        priority,
      });
      return data;
    },
    onSuccess: (data) => {
      toast({ title: t('crud.messages.saved', { defaultValue: 'Gespeichert' }), description: data.taskNumber });
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
    createMutation.mutate();
  };

  return (
    <div className="mx-auto max-w-lg space-y-4 p-4">
      <div className="flex items-center gap-2">
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate(backHref)}>
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t('crud.actions.back', { defaultValue: 'Zurück' })}
        </Button>
      </div>

      <h1 className="text-2xl font-bold">
        {t('crud.actions.new', { defaultValue: 'Neu' })} Field-Service
      </h1>

      {(workflowInstanceId || workflowCase) && (
        <div className="rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-xs text-blue-900">
          {workflowCase ? `Workflow ${workflowCase}` : 'Workflow'}
          {workflowInstanceId ? ` · ${workflowInstanceId}` : ''}
        </div>
      )}

      {serviceRequestId && (
        <div className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-900">
          Service-Vorgang {serviceRequestId} · Einsatz wird direkt aus der Anfrage geplant.
        </div>
      )}

      <Card className="p-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fst-title">{t('crud.fields.name', { defaultValue: 'Name' })} *</Label>
            <Input
              id="fst-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="z. B. Wartung Dosieranlage"
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
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
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
