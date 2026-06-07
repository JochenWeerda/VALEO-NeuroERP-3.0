/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { ContactLog, Customer } from '../types';
import { Check, ClipboardList, Calendar, Trash2, CheckCircle2, ChevronRight, AlertTriangle } from 'lucide-react';

interface FollowUpTaskPanelProps {
  logs: ContactLog[];
  customer: Customer;
  onResolveTask: (logId: string) => void;
}

export default function FollowUpTaskPanel({ logs, customer, onResolveTask }: FollowUpTaskPanelProps) {
  // Filter active followups (i.e. has reSubmissionDate and is not completed)
  const activeFollowUps = logs.filter(l => l.reSubmissionDate && !l.completed);
  
  // Outstanding tasks that have passed today's date
  const today = new Date().toISOString().split('T')[0];
  const overdueTasksCount = activeFollowUps.filter(t => t.reSubmissionDate && t.reSubmissionDate < today).length;

  return (
    <div className="bg-white border border-[#cbd5e1] rounded-sm overflow-hidden select-none font-sans" id="follow-up-task-panel">
      
      {/* Title bar */}
      <div className="bg-[#cbd5e1] p-2.5 border-b border-[#cbd5e1] flex justify-between items-center font-bold">
        <span className="font-mono text-[10px] uppercase tracking-wider flex items-center gap-1.5 text-gray-800">
          <ClipboardList size={13} className="text-[#006633]" />
          Wiedervorlagen & Offene Folgekontakte ({activeFollowUps.length})
        </span>

        {overdueTasksCount > 0 && (
          <span className="bg-red-100 text-red-800 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border border-red-200 animate-pulse flex items-center gap-1">
            <AlertTriangle size={10} className="stroke-[3]" />
            {overdueTasksCount} FÄLLIG!
          </span>
        )}
      </div>

      <div className="p-3 bg-slate-50 border-b border-gray-200 text-xs text-gray-600 leading-snug">
        <p>
          Zur Sicherstellung der Beziehungsbindung müssen alle Anrufe, Abmachungen und offenen Fragen bezüglich Getreideproben oder Wiegeprüfungen termingetreu nachbereitet werden.
        </p>
      </div>

      {/* Task list and timeline */}
      <div className="divide-y divide-gray-200 text-xs">
        {activeFollowUps.length === 0 ? (
          <div className="p-10 text-center text-gray-400 font-sans italic font-semibold">
            Keine offen Wiedervorlagen für diesen Mandanten terminiert. Alle Folgekontakte erledigt.
          </div>
        ) : (
          activeFollowUps.map(task => {
            const isOverdue = task.reSubmissionDate && task.reSubmissionDate < today;
            return (
              <div 
                key={task.id} 
                className={`p-3 flex items-center justify-between transition ${
                  isOverdue ? 'bg-red-50/40 hover:bg-red-50/75' : 'hover:bg-slate-50'
                }`}
                id={`task-row-${task.id}`}
              >
                <div className="flex items-start gap-2.5 max-w-[75%] truncate">
                  <div className={`p-1.5 rounded-sm border ${
                    isOverdue 
                      ? 'bg-red-100/50 border-red-200 text-red-700' 
                      : 'bg-indigo-50 border-indigo-100 text-indigo-700'
                  }`}>
                    <Calendar size={13} className={isOverdue ? 'animate-pulse' : ''} />
                  </div>
                  <div className="truncate leading-tight">
                    <strong className="text-gray-900 font-black truncate block text-[12.5px] font-mono">{task.artKurzinfo}</strong>
                    <div className="flex items-center gap-2 text-[10px] text-gray-400 font-mono mt-1">
                      <span className={`font-bold ${isOverdue ? 'text-red-700 font-extrabold' : 'text-slate-500'}`}>
                        Wiedervorlage fällig am: {task.reSubmissionDate ? new Date(task.reSubmissionDate).toLocaleDateString("de-DE") : '—'}
                      </span>
                      <span>•</span>
                      <span>Bediener: {task.operator}</span>
                      {task.referenceType !== 'NONE' && (
                        <>
                          <span>•</span>
                          <span className="text-[#006633] font-bold">[{task.referenceType}: {task.referenceNo}]</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => onResolveTask(task.id)}
                  className="flex items-center gap-1 bg-[#006633] hover:bg-emerald-800 text-white font-mono font-bold text-[9.5px] uppercase px-3 py-1.5 rounded-sm transition cursor-pointer select-none shadow-sm"
                  title="Folgekontakt erfolgreich abgeschlossen"
                >
                  <CheckCircle2 size={11} />
                  <span>Erledigen</span>
                </button>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
}
