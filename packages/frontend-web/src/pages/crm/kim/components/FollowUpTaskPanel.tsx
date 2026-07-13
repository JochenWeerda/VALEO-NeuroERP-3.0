/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { ContactLog, Customer } from '../types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ClipboardList, Calendar, CheckCircle2, AlertTriangle } from 'lucide-react';

interface FollowUpTaskPanelProps {
  logs: ContactLog[];
  customer: Customer;
  onResolveTask: (logId: string) => void;
}

export default function FollowUpTaskPanel({ logs, customer, onResolveTask }: FollowUpTaskPanelProps) {
  const activeFollowUps = logs.filter(l => l.reSubmissionDate && !l.completed);
  const today = new Date().toISOString().split('T')[0];
  const overdueTasksCount = activeFollowUps.filter(t => t.reSubmissionDate && t.reSubmissionDate < today).length;

  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden" id="follow-up-task-panel">

      <div className="bg-muted/60 px-3 py-2.5 border-b border-border flex justify-between items-center">
        <span className="text-sm font-semibold flex items-center gap-1.5 text-foreground">
          <ClipboardList size={15} className="text-primary" />
          Wiedervorlagen &amp; offene Folgekontakte ({activeFollowUps.length})
        </span>
        {overdueTasksCount > 0 && (
          <Badge variant="destructive" className="gap-1">
            <AlertTriangle size={11} />
            {overdueTasksCount} fällig
          </Badge>
        )}
      </div>

      <div className="px-3 py-2.5 bg-muted/30 border-b border-border text-xs text-muted-foreground leading-snug">
        Zur Sicherstellung der Beziehungsbindung müssen alle Anrufe, Abmachungen und offenen Fragen
        (z.B. Getreideproben, Wiegeprüfungen) termingetreu nachbereitet werden.
      </div>

      <div className="divide-y divide-border text-sm">
        {activeFollowUps.length === 0 ? (
          <div className="p-10 text-center text-muted-foreground italic">
            Keine offenen Wiedervorlagen terminiert. Alle Folgekontakte erledigt.
          </div>
        ) : (
          activeFollowUps.map(task => {
            const isOverdue = task.reSubmissionDate && task.reSubmissionDate < today;
            return (
              <div
                key={task.id}
                className={`p-3 flex items-center justify-between gap-3 transition-colors ${isOverdue ? 'bg-destructive/5 hover:bg-destructive/10' : 'hover:bg-muted/50'}`}
                id={`task-row-${task.id}`}
              >
                <div className="flex items-start gap-2.5 min-w-0">
                  <div className={`p-1.5 rounded-md border shrink-0 ${isOverdue ? 'bg-destructive/10 border-destructive/30 text-destructive' : 'bg-primary/10 border-primary/20 text-primary'}`}>
                    <Calendar size={14} />
                  </div>
                  <div className="min-w-0">
                    <strong className="text-foreground block truncate">{task.artKurzinfo}</strong>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1 flex-wrap">
                      <span className={isOverdue ? 'text-destructive font-semibold' : ''}>
                        Fällig am: {task.reSubmissionDate ? new Date(task.reSubmissionDate).toLocaleDateString("de-DE") : '—'}
                      </span>
                      <span>•</span>
                      <span>Bediener: {task.operator}</span>
                      {task.referenceType !== 'NONE' && (
                        <>
                          <span>•</span>
                          <span className="text-primary font-medium">{task.referenceType}: {task.referenceNo}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <Button size="sm" onClick={() => onResolveTask(task.id)} title="Folgekontakt abschließen" className="gap-1 shrink-0">
                  <CheckCircle2 size={13} />
                  Erledigen
                </Button>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
}
