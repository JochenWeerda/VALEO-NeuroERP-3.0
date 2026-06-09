/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { ContactLog, Customer } from '../types';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { NativeSelect } from '@/components/ui/native-select';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Paperclip, Mail, Check, Clock, Plus, X } from 'lucide-react';

interface ContactHistoryTableProps {
  logs: ContactLog[];
  customer: Customer;
  onAddLog: (vals: Partial<ContactLog>) => void | Promise<unknown>;
}

type L3HistorySubtab = 'OVERVIEW' | 'HISTORY' | 'INVOICES' | 'DUNNING' | 'CONTRACTS' | 'DROP_SHIPMENT';

export default function ContactHistoryTable({ logs, customer, onAddLog }: ContactHistoryTableProps) {
  const [activeTab, setActiveTab] = useState<L3HistorySubtab>('OVERVIEW');
  const [showAddLog, setShowAddLog] = useState(false);

  const [logDirection, setLogDirection] = useState<'INCOMING' | 'OUTGOING'>('INCOMING');
  const [logArt, setLogArt] = useState<'persoenlich' | 'telefon' | 'email' | 'whatsapp'>('telefon');
  const [logDate, setLogDate] = useState(new Date().toISOString().split('T')[0]);
  const [logDesc, setLogDesc] = useState('');        // Betreff
  const [logKommentar, setLogKommentar] = useState('');
  const [logCc, setLogCc] = useState('');            // CC: interner Empfaenger oder E-Mail
  const [logOp, setLogOp] = useState('JW');
  const [logResubmit, setLogResubmit] = useState('');
  const [logHasScan, setLogHasScan] = useState(false);
  const [logEmailSent, setLogEmailSent] = useState(false);
  const [logRefType, setLogRefType] = useState<'NONE' | 'OFFER' | 'ORDER' | 'CONTRACT' | 'INVOICE'>('NONE');
  const [logRefNo, setLogRefNo] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState('');

  const filteredLogs = logs.filter(log => {
    switch (activeTab) {
      case 'HISTORY':
        return log.referenceType === 'NONE' || !log.referenceType;
      case 'INVOICES':
        return log.referenceType === 'INVOICE' || log.artKurzinfo.toLowerCase().includes('re-') || log.artKurzinfo.toLowerCase().includes('rechnung');
      case 'DUNNING':
        return log.artKurzinfo.toLowerCase().includes('mahnung') || log.artKurzinfo.toLowerCase().includes('zahlungsverzug') || log.artKurzinfo.toLowerCase().includes('op');
      case 'CONTRACTS':
        return log.referenceType === 'CONTRACT' || log.artKurzinfo.toLowerCase().includes('kontrakt') || log.artKurzinfo.toLowerCase().includes('abnahme');
      case 'DROP_SHIPMENT':
        return log.artKurzinfo.toLowerCase().includes('strecke') || log.artKurzinfo.toLowerCase().includes('direkt');
      case 'OVERVIEW':
      default:
        return true;
    }
  });

  const handleSubmitLog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!logDesc || isSaving) return;

    setIsSaving(true);
    setSaveError('');
    try {
      await onAddLog({
        direction: logDirection,
        art: logArt,
        date: logDate,
        artKurzinfo: logDesc,
        betreff: logDesc,
        kommentar: logKommentar || undefined,
        ccIntern: logCc || undefined,
        operator: logOp,
        reSubmissionDate: logResubmit || undefined,
        hasScan: logHasScan,
        emailSent: logEmailSent,
        emailDirection: logEmailSent ? 'OUT' : undefined,
        referenceType: logRefType,
        referenceNo: logRefNo || undefined,
        completed: !logResubmit,
      });
      setLogDesc(''); setLogKommentar(''); setLogCc(''); setLogResubmit('');
      setLogHasScan(false); setLogEmailSent(false);
      setLogRefType('NONE'); setLogRefNo(''); setShowAddLog(false);
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : 'Aktivitaet konnte nicht gespeichert werden.');
    } finally {
      setIsSaving(false);
    }
  };

  const tabs: { key: L3HistorySubtab; label: string; tooltip: string }[] = [
    { key: 'OVERVIEW', label: 'Übersicht', tooltip: 'Gesamte Historie chronologisch sortiert' },
    { key: 'HISTORY', label: 'Historie', tooltip: 'Gesprächsnotizen und allgemeine Vorgänge' },
    { key: 'INVOICES', label: 'Rechnungen', tooltip: 'Berechnungs- und Fakturavorgänge' },
    { key: 'DUNNING', label: 'Mahnungen', tooltip: 'Zahlungsverzug und Mahnstufen' },
    { key: 'CONTRACTS', label: 'Kontrakte', tooltip: 'Agrar-Ernteabkommen & Silobestellungen' },
    { key: 'DROP_SHIPMENT', label: 'Strecken-Geschäfte', tooltip: 'Sonderabfuhren direkt frei Hof' },
  ];

  return (
    <div className="bg-card border-0 overflow-hidden flex flex-col h-full" id="contact-history-workspace">

      {/* Sub-tab strip */}
      <div className="bg-muted/60 border-b border-border flex flex-wrap items-end justify-between px-3 gap-2">
        <div className="flex gap-1 pt-1.5 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`whitespace-nowrap px-3 py-1.5 text-xs font-medium transition rounded-t-md border-t border-x ${
                activeTab === tab.key
                  ? 'bg-card border-border text-primary font-semibold'
                  : 'bg-transparent border-transparent text-muted-foreground hover:bg-muted hover:text-foreground'
              }`}
              title={tab.tooltip}
              id={`history-tab-btn-${tab.key}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <Button variant="outline" size="sm" onClick={() => setShowAddLog(!showAddLog)} className="gap-1 mb-1" id="btn-trigger-history-form">
          {showAddLog ? <X size={13} /> : <Plus size={13} />}
          {showAddLog ? 'Eingabe schließen' : 'Aktivität erfassen'}
        </Button>
      </div>

      {/* Scrollbarer Bereich: Formular (inkl. Speichern-Button) + Liste bleiben im kurzen Panel erreichbar */}
      <div className="flex-1 min-h-0 overflow-y-auto">
      {/* Inline entry form */}
      {showAddLog && (
        <form onSubmit={handleSubmitLog} className="p-3 bg-muted/30 border-b border-border text-sm grid grid-cols-12 gap-2" id="add-history-vorgang-form">
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Richtung</Label>
            <NativeSelect
              value={logDirection}
              onChange={e => setLogDirection(e.target.value as 'INCOMING' | 'OUTGOING')}
              options={[{ value: 'INCOMING', label: 'Anruf / Post EIN' }, { value: 'OUTGOING', label: 'Kontakt AUS' }]}
            />
          </div>

          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Vorgangsdatum</Label>
            <Input type="date" required value={logDate} onChange={e => setLogDate(e.target.value)} />
          </div>

          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label htmlFor="crm360-log-art" className="text-xs">Art</Label>
            <NativeSelect
              id="crm360-log-art"
              value={logArt}
              onChange={e => setLogArt(e.target.value as typeof logArt)}
              options={[
                { value: 'persoenlich', label: 'Persönlich' },
                { value: 'telefon', label: 'Telefon' },
                { value: 'email', label: 'E-Mail' },
                { value: 'whatsapp', label: 'WhatsApp' },
              ]}
            />
          </div>

          <div className="col-span-12 md:col-span-3 space-y-1">
            <Label htmlFor="crm360-log-subject" className="text-xs">Betreff <span className="text-destructive">*</span></Label>
            <Input id="crm360-log-subject" required value={logDesc} onChange={e => setLogDesc(e.target.value)} placeholder="Betreffzeile…" />
          </div>

          <div className="col-span-6 md:col-span-1 space-y-1">
            <Label className="text-xs">Bediener</Label>
            <Input required value={logOp} onChange={e => setLogOp(e.target.value)} className="text-center" />
          </div>

          <div className="col-span-6 md:col-span-3 space-y-1">
            <Label className="text-xs">Beleg-Referenz</Label>
            <div className="flex gap-1">
              <NativeSelect
                className="w-1/2"
                value={logRefType}
                onChange={e => setLogRefType(e.target.value as typeof logRefType)}
                options={[
                  { value: 'NONE', label: '– Ref –' },
                  { value: 'OFFER', label: 'Angebot' },
                  { value: 'ORDER', label: 'Auftrag' },
                  { value: 'CONTRACT', label: 'Silo' },
                  { value: 'INVOICE', label: 'OP-Re.' },
                ]}
              />
              <Input className="w-1/2" placeholder="Nr." value={logRefNo} onChange={e => setLogRefNo(e.target.value)} />
            </div>
          </div>

          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Wiedervorlage (WV)</Label>
            <Input type="date" value={logResubmit} onChange={e => setLogResubmit(e.target.value)} />
          </div>

          <div className="col-span-12 md:col-span-8 space-y-1">
            <Label htmlFor="crm360-log-comment" className="text-xs">Kommentar</Label>
            <Textarea id="crm360-log-comment" value={logKommentar} onChange={e => setLogKommentar(e.target.value)} className="h-16" placeholder="Freitext / Gesprächsnotiz…" />
          </div>

          <div className="col-span-12 md:col-span-4 space-y-1">
            <Label htmlFor="crm360-log-cc" className="text-xs">CC (intern Mitarbeiter/Abteilung oder externe E-Mail)</Label>
            <Input id="crm360-log-cc" value={logCc} onChange={e => setLogCc(e.target.value)} placeholder="z.B. AO  ·  oder berater@extern.de" />
          </div>

          <div className="col-span-12 border-t border-dashed border-border pt-2 flex flex-col md:flex-row justify-between items-center gap-2">
            <div className="flex flex-wrap gap-4 items-center text-muted-foreground">
              <label className="flex items-center gap-1.5 cursor-pointer select-none">
                <input type="checkbox" checked={logHasScan} onChange={e => setLogHasScan(e.target.checked)} className="accent-primary" />
                <span>Scan-Akte verknüpfen (Faxzufuhr / Wiegebrief)</span>
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer select-none">
                <input type="checkbox" checked={logEmailSent} onChange={e => setLogEmailSent(e.target.checked)} className="accent-primary" />
                <span>E-Mail-Kopie mitsenden</span>
              </label>
            </div>

            <Button type="submit" size="sm" className="gap-1.5" id="btn-save-activity-vorgang" disabled={isSaving || !logDesc.trim()}>
              <Check size={13} />
              Aktivität speichern
            </Button>
            {saveError && <p className="w-full text-right text-xs text-destructive" role="alert">{saveError}</p>}
          </div>
        </form>
      )}

      {/* Listing */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm border-collapse">
          <thead className="sticky top-0">
            <tr className="bg-muted/60 border-b border-border text-muted-foreground text-xs">
              <th className="p-2 text-center">Richtung</th>
              <th className="p-2">Datum</th>
              <th className="p-2">Art / Vorgang / Kurzinfo</th>
              <th className="p-2 text-center">Bediener</th>
              <th className="p-2 text-center">WV-Termin</th>
              <th className="p-2 text-center">Anlagen</th>
              <th className="p-2 text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-6 text-center text-muted-foreground italic">
                  Keine Vorgänge im Filter „{tabs.find(t => t.key === activeTab)?.label}".
                </td>
              </tr>
            ) : (
              filteredLogs.map(log => {
                const isOverdueWV = log.reSubmissionDate && new Date(log.reSubmissionDate) < new Date() && !log.completed;
                return (
                  <tr key={log.id} className="border-b border-border hover:bg-muted/40 transition" id={`log-row-${log.id}`}>
                    <td className="p-2 text-center">
                      <Badge variant={log.direction === 'INCOMING' ? 'success' : 'secondary'}>
                        {log.direction === 'INCOMING' ? 'EIN' : 'AUS'}
                      </Badge>
                    </td>
                    <td className="p-2 text-muted-foreground whitespace-nowrap">{new Date(log.date).toLocaleDateString("de-DE")}</td>
                    <td className="p-2 text-foreground" title={log.artKurzinfo}>
                      <div className="flex items-center gap-1.5">
                        {log.referenceType !== 'NONE' && log.referenceType && (
                          <span className="text-primary font-medium">[{log.referenceType}:{log.referenceNo || '—'}]</span>
                        )}
                        <span className="truncate max-w-[480px]">{log.artKurzinfo}</span>
                      </div>
                    </td>
                    <td className="p-2 text-center text-muted-foreground">
                      {log.operator === 'AUTO'
                        ? <Badge variant="info" title="Automatisch erfasst (Telefon/E-Mail/WhatsApp)">Auto</Badge>
                        : log.operator}
                    </td>
                    <td className={`p-2 text-center ${isOverdueWV ? 'text-destructive font-semibold' : 'text-muted-foreground'}`}>
                      {log.reSubmissionDate ? (
                        <span className="flex items-center justify-center gap-1 whitespace-nowrap text-xs">
                          <Clock size={11} className={isOverdueWV ? 'text-destructive' : 'text-muted-foreground'} />
                          {new Date(log.reSubmissionDate).toLocaleDateString("de-DE")}
                        </span>
                      ) : '—'}
                    </td>
                    <td className="p-2 text-center">
                      <div className="flex items-center justify-center gap-1.5">
                        {log.hasScan && <Badge variant="success" className="gap-0.5"><Paperclip size={10} />Scan</Badge>}
                        {log.emailSent && <Badge variant="info" className="gap-0.5"><Mail size={10} />Mail</Badge>}
                        {!log.hasScan && !log.emailSent && <span className="text-muted-foreground">—</span>}
                      </div>
                    </td>
                    <td className="p-2 text-center">
                      {log.completed ? (
                        <Badge variant="success">Erledigt</Badge>
                      ) : (
                        <Badge variant={isOverdueWV ? 'destructive' : 'info'}>{isOverdueWV ? 'Überfällig' : 'Offen'}</Badge>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
      </div>

    </div>
  );
}
